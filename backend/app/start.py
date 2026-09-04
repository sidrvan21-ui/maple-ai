from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.auth import ROLES, principal_from_cookie
from app.config import settings
from app.onboard import rooms_for_page
from app.ingest import list_products
from app.sso import sso_ready

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


def start_page(request: Request, error: str | None = None) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "principal": principal_from_cookie(request),
            "roles": ROLES,
            "error": error,
            "sso_ready": sso_ready(),
            "allow_dev_login": settings.allow_dev_login,
        },
    )


def onboard_page(
    request: Request,
    error: str | None = None,
    report: dict | None = None,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "onboard.html",
        {
            "principal": principal_from_cookie(request),
            "rooms": rooms_for_page(),
            "products": list_products(),
            "error": error,
            "report": report,
        },
    )


def cookie_secure(request: Request) -> bool:
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    return proto == "https"
