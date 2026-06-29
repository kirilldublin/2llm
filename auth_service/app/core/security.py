from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the given plain password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plain password against a stored bcrypt hash."""
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(
    sub: str,
    role: str = "user",
    expires_minutes: int | None = None,
) -> str:
    """Create a signed JWT access token.

    The token always carries ``sub`` (user id), ``role``, ``iat`` and
    ``exp`` claims as required by the project specification.
    """
    now = datetime.now(timezone.utc)
    expire_minutes = (
        expires_minutes
        if expires_minutes is not None
        else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    expire = now + timedelta(minutes=expire_minutes)

    payload: dict[str, Any] = {
        "sub": str(sub),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


class TokenError(Exception):
    """Raised when a token cannot be decoded."""


class TokenExpired(TokenError):
    """Raised when a token signature is valid but the token has expired."""


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT, returning its payload.

    Raises :class:`TokenExpired` if the token is expired and
    :class:`TokenError` for any other validation failure.
    """
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except ExpiredSignatureError as exc:
        raise TokenExpired(str(exc)) from exc
    except JWTError as exc:
        raise TokenError(str(exc)) from exc
