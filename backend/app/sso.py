"""Google SSO. Same JWT + role as dev login. Company domain is optional."""

import json
import secrets
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.auth import ROLES, Role
from app.config import settings

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
GOOGLE_USER = "https://www.googleapis.com/oauth2/v2/userinfo"


def sso_ready() -> bool:
    return bool(settings.google_client_id and settings.google_client_secret)


def new_state() -> str:
    return secrets.token_urlsafe(24)


def authorize_url(state: str) -> str:
    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "prompt": "select_account",
        }
    )
    return f"{GOOGLE_AUTH}?{query}"


def role_for_email(email: str) -> Role:
    """Map one email to a Maple role. Default is product."""
    wanted = email.strip().lower()
    for pair in settings.sso_role_map.split(","):
        if "=" not in pair:
            continue
        addr, role = pair.split("=", 1)
        role = role.strip()
        if addr.strip().lower() == wanted and role in ROLES:
            return role  # type: ignore[return-value]
    fallback = settings.sso_default_role
    if fallback not in ROLES:
        fallback = "product"
    return fallback  # type: ignore[return-value]


def domain_ok(email: str) -> bool:
    allowed = settings.sso_allowed_domain.strip().lower()
    if not allowed:
        return True
    return email.strip().lower().endswith("@" + allowed)


def exchange_code(code: str) -> dict:
    body = urlencode(
        {
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode()
    req = Request(GOOGLE_TOKEN, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urlopen(req, timeout=20) as resp:
        token = json.loads(resp.read().decode())
    access = token.get("access_token")
    if not access:
        raise RuntimeError("google did not return access_token")
    info_req = Request(GOOGLE_USER, method="GET")
    info_req.add_header("Authorization", f"Bearer {access}")
    with urlopen(info_req, timeout=20) as resp:
        return json.loads(resp.read().decode())
