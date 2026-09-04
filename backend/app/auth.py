"""Dev login: pick a role, get a JWT. SSO can replace this later; roles stay."""

from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.config import settings

Role = Literal["product", "finance", "engineering", "exec", "growth", "legal"]

ROLES: tuple[Role, ...] = (
    "product",
    "finance",
    "engineering",
    "exec",
    "growth",
    "legal",
)

bearer = HTTPBearer(auto_error=False)


class DevLoginIn(BaseModel):
    name: str = "Siddharth"
    role: Role


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role
    name: str


class Principal(BaseModel):
    name: str
    role: Role
    email: str = ""


def issue_token(name: str, role: Role, email: str = "") -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": name,
        "role": role,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=12)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> Principal:
    data = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    role = data.get("role")
    if role not in ROLES:
        raise jwt.InvalidTokenError("unknown role")
    return Principal(
        name=str(data.get("sub", "unknown")),
        role=role,
        email=str(data.get("email") or ""),
    )


def principal_from_cookie(request) -> Principal | None:
    raw = request.cookies.get("maple_token")
    if not raw:
        return None
    try:
        return decode_token(raw)
    except jwt.PyJWTError:
        return None


def principal_from_token(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Principal:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    try:
        return decode_token(creds.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from exc
