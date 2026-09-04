from urllib.parse import quote

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse, Response

from app.audit import log
from app.auth import principal_from_cookie
from app.ingest import ingest, resolve_product
from app.onboard import parse_room, template_zip_bytes
from app.rag.vector_store import drop_store as drop_index
from app.start import onboard_page as render_onboard

router = APIRouter()


def _need_login() -> RedirectResponse:
    return RedirectResponse("/", status_code=303)


@router.get("/onboard")
def onboard_get(request: Request, error: str | None = None):
    if principal_from_cookie(request) is None:
        return _need_login()
    return render_onboard(request, error=error)


@router.get("/onboard/kit.zip")
def onboard_kit():
    return Response(
        content=template_zip_bytes(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=maple-nine-rooms.zip"},
    )


@router.post("/onboard")
async def onboard_submit(
    request: Request,
    product: str = Form(""),
    existing: str = Form(""),
    company: str = Form(""),
    room: str = Form("unsure"),
    files: list[UploadFile] = File(default=[]),
):
    if principal_from_cookie(request) is None:
        return _need_login()
    uploads: list[tuple[str, bytes]] = []
    for item in files:
        name = item.filename or ""
        if not name:
            continue
        uploads.append((name, await item.read()))
    try:
        name = resolve_product(product, existing)
        if not name:
            raise ValueError("pick an existing product or type a new name")
        report = ingest(name, company, parse_room(room), uploads)
    except ValueError as exc:
        return RedirectResponse(f"/onboard?error={quote(str(exc))}", status_code=303)
    drop_index(report["slug"])
    log(principal_from_cookie(request), "onboard", report["slug"], f"{report['files']} files")
    return render_onboard(request, report=report)
