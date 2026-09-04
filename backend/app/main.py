from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth import DevLoginIn, Principal, TokenOut, issue_token, principal_from_token
from app.config import settings
from app.rag.admit import repo_root
from app.routes_discovery import router as discovery_router
from app.routes_pages import router as pages_router

load_dotenv(repo_root() / ".env")

app = FastAPI(
    title="Maple AI",
    description="Phase-gate PMLC API. Discovery run + HITL sign/reject.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(pages_router)
app.include_router(discovery_router)
app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).resolve().parent / "static")),
    name="static",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Process is up. Used by Compose and interview demos."""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    """Later: checkpointer + index. Part 1: same as health."""
    return {"status": "ready"}


@app.post("/api/auth/dev-login", response_model=TokenOut)
def dev_login(body: DevLoginIn) -> TokenOut:
    """Pick a HITL role. Replace with SSO later; keep the same role claim."""
    token = issue_token(body.name, body.role)
    return TokenOut(access_token=token, role=body.role, name=body.name)


@app.get("/api/me")
def me(principal: Principal = Depends(principal_from_token)) -> Principal:
    return principal
