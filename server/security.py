"""Password hashing, signed session cookies and simple login throttling."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from collections import defaultdict

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import AdminUser

COOKIE_NAME = "slovenec_admin"
SESSION_MAX_AGE = settings.session_days * 24 * 3600

_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_LEN = 32


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_SCRYPT_LEN,
        maxmem=64 * 1024 * 1024,
    )
    return (
        "scrypt$"
        + base64.b64encode(salt).decode()
        + "$"
        + base64.b64encode(digest).decode()
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_b64, digest_b64 = stored.split("$", 2)
        if scheme != "scrypt":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=_SCRYPT_N,
            r=_SCRYPT_R,
            p=_SCRYPT_P,
            dklen=_SCRYPT_LEN,
            maxmem=64 * 1024 * 1024,
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _sign(payload: str) -> str:
    return hmac.new(
        settings.secret_key.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()


def create_session_token(user_id: int) -> str:
    payload = json.dumps({"uid": user_id, "exp": int(time.time()) + SESSION_MAX_AGE})
    encoded = base64.urlsafe_b64encode(payload.encode()).decode()
    return encoded + "." + _sign(encoded)


def read_session_token(token: str) -> int | None:
    try:
        encoded, signature = token.split(".", 1)
        if not hmac.compare_digest(signature, _sign(encoded)):
            return None
        payload = json.loads(base64.urlsafe_b64decode(encoded.encode()))
        if int(payload["exp"]) < time.time():
            return None
        return int(payload["uid"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def current_admin(request: Request, db: Session = Depends(get_db)) -> AdminUser | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    user_id = read_session_token(token)
    if user_id is None:
        return None
    return db.get(AdminUser, user_id)


def require_admin(admin: AdminUser | None = Depends(current_admin)) -> AdminUser:
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Prijava je potrebna."
        )
    return admin


_failed: dict[str, list[float]] = defaultdict(list)
_WINDOW = 15 * 60
_MAX_ATTEMPTS = 8


def client_ip(request: Request) -> str:
    if settings.trust_proxy:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def login_allowed(ip: str) -> bool:
    now = time.time()
    attempts = [t for t in _failed[ip] if now - t < _WINDOW]
    _failed[ip] = attempts
    return len(attempts) < _MAX_ATTEMPTS


def register_failed_login(ip: str) -> None:
    _failed[ip].append(time.time())


def clear_login_attempts(ip: str) -> None:
    _failed.pop(ip, None)
