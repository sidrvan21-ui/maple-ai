from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.agents.catalog import GATE_BRIEF, SPECS
from app.audit import for_product, log
from app.auth import ROLES, decode_token, issue_token, principal_from_cookie
from app.config import settings
from app.graph import _run_error_message, run_current_room
from app.hitl import reject_pack, sign_pack
from app.sso import (
    authorize_url,
    domain_ok,
    exchange_code,
    new_state,
    role_for_email,
    sso_ready,
)
from app.schemas.development import DevelopmentArtifacts
from app.schemas.discovery import DiscoveryArtifacts
from app.schemas.growth import GrowthArtifacts
from app.schemas.launch import LaunchArtifacts
from app.schemas.maturity import MaturityArtifacts
from app.schemas.qualify import QualifyArtifacts
from app.schemas.scoping import ScopingArtifacts
from app.schemas.strategy import StrategyArtifacts
from app.schemas.sunset import SunsetArtifacts
from app.start import cookie_secure, start_page
from app.session import get_state, visible_pack

_BRIEFING_KIND = {
    DiscoveryArtifacts: "discovery",
    StrategyArtifacts: "strategy",
    ScopingArtifacts: "scoping",
    DevelopmentArtifacts: "development",
    QualifyArtifacts: "qualify",
    LaunchArtifacts: "launch",
    GrowthArtifacts: "growth",
    MaturityArtifacts: "maturity",
    SunsetArtifacts: "sunset",
}

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
router = APIRouter()


def _need_login() -> RedirectResponse:
    return RedirectResponse("/", status_code=303)


def _to_workbench(product_id: str, error: str | None = None) -> RedirectResponse:
    url = f"/p/{product_id}"
    if error:
        url = f"{url}?error={quote(error)}"
    return RedirectResponse(url, status_code=303)


@router.get("/", response_class=HTMLResponse)
def home(request: Request, error: str | None = None):
    return start_page(request, error=error)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: str | None = None):
    return start_page(request, error=error)


@router.post("/login")
def login_submit(request: Request, name: str = Form(...), role: str = Form(...)):
    if not settings.allow_dev_login:
        return RedirectResponse("/?error=dev+login+off", status_code=303)
    if role not in ROLES:
        return RedirectResponse("/?error=bad+role", status_code=303)
    token = issue_token(name, role)
    log(decode_token(token), "login", detail="dev")
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie(
        "maple_token",
        token,
        httponly=True,
        samesite="lax",
        secure=cookie_secure(request),
    )
    return resp


@router.get("/auth/google")
def google_start(request: Request):
    if not sso_ready():
        return RedirectResponse("/?error=sso+not+configured", status_code=303)
    state = new_state()
    resp = RedirectResponse(authorize_url(state), status_code=303)
    resp.set_cookie(
        "maple_sso",
        state,
        httponly=True,
        samesite="lax",
        max_age=600,
        secure=cookie_secure(request),
    )
    return resp


@router.get("/auth/google/callback")
def google_callback(request: Request, code: str | None = None, state: str | None = None):
    expected = request.cookies.get("maple_sso")
    if not code or not state or not expected or state != expected:
        return RedirectResponse("/?error=sso+state", status_code=303)
    try:
        info = exchange_code(code)
    except Exception:
        return RedirectResponse("/?error=sso+exchange", status_code=303)
    email = str(info.get("email") or "").lower()
    name = str(info.get("name") or email.split("@")[0] or "sso")
    if not email or not domain_ok(email):
        log(None, "sso_denied", detail=email or "no-email")
        return RedirectResponse("/?error=sso+domain", status_code=303)
    role = role_for_email(email)
    token = issue_token(name, role, email=email)
    log(decode_token(token), "sso_login", detail=email)
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie(
        "maple_token",
        token,
        httponly=True,
        samesite="lax",
        secure=cookie_secure(request),
    )
    resp.delete_cookie("maple_sso")
    return resp


@router.get("/logout")
def logout(request: Request):
    log(principal_from_cookie(request), "logout")
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie("maple_token")
    return resp


@router.get("/p/{product_id}", response_class=HTMLResponse)
def workbench(
    request: Request,
    product_id: str,
    error: str | None = None,
    view: int | None = None,
):
    principal = principal_from_cookie(request)
    if principal is None:
        return _need_login()
    state = get_state(product_id)
    pack = visible_pack(state, view)
    artifacts = pack.artifacts if pack is not None else None
    briefing_kind = _BRIEFING_KIND.get(type(artifacts), "raw") if artifacts else ""
    artifacts_text = artifacts.model_dump_json(indent=2) if artifacts is not None else ""
    can_gate = principal.role in state.get("required_approver_roles", [])
    current_spec = SPECS[state["current_stage"]]
    lesson_stage = pack.stage if pack is not None else state["current_stage"]
    rooms = [
        {
            "n": n,
            "name": spec.name,
            "admitted": n in state["admitted_stages"],
            "here": n == state["current_stage"],
            "has_pack": n in state["gate_packs"],
        }
        for n, spec in SPECS.items()
    ]
    return templates.TemplateResponse(
        request,
        "workbench.html",
        {
            "principal": principal,
            "product_id": product_id,
            "state": state,
            "pack": pack,
            "artifacts": artifacts,
            "briefing_kind": briefing_kind,
            "artifacts_text": artifacts_text,
            "error": error,
            "can_gate": can_gate,
            "in_review": state["hitl"] == "in_review",
            "run_label": f"Run {current_spec.name}",
            "lesson_name": SPECS[lesson_stage].name,
            "brief": GATE_BRIEF[lesson_stage],
            "rooms": rooms,
            "audit": for_product(product_id),
        },
    )


@router.post("/p/{product_id}/run")
def page_run(request: Request, product_id: str):
    principal = principal_from_cookie(request)
    if principal is None:
        return _need_login()
    try:
        run_current_room(product_id)
    except HTTPException as exc:
        return _to_workbench(product_id, str(exc.detail))
    except Exception as exc:
        return _to_workbench(product_id, _run_error_message(exc))
    log(principal, "run", product_id)
    return _to_workbench(product_id)


@router.post("/p/{product_id}/sign")
def page_sign(request: Request, product_id: str):
    principal = principal_from_cookie(request)
    if principal is None:
        return _need_login()
    try:
        sign_pack(get_state(product_id), principal.role)
    except HTTPException as exc:
        return _to_workbench(product_id, str(exc.detail))
    log(principal, "sign", product_id)
    return _to_workbench(product_id)


@router.post("/p/{product_id}/reject")
def page_reject(request: Request, product_id: str):
    principal = principal_from_cookie(request)
    if principal is None:
        return _need_login()
    try:
        reject_pack(get_state(product_id), principal.role)
    except HTTPException as exc:
        return _to_workbench(product_id, str(exc.detail))
    log(principal, "reject", product_id)
    return _to_workbench(product_id)
