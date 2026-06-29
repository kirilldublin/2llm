from typing import Any

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.core.config import settings


class InvalidToken(ValueError):
    """Raised when a JWT is missing, malformed, expired, or unsigned correctly."""


def decode_and_validate(token: str) -> dict[str, Any]:
    """Validate a JWT issued by the Auth Service and return its payload.

    The Bot Service never *creates* tokens — it only verifies the
    signature, the ``exp`` claim, and the presence of ``sub``.
    """
    if not token or not isinstance(token, str):
        raise InvalidToken("Empty token")

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG]
        )
    except ExpiredSignatureError as exc:
        raise InvalidToken("Token has expired") from exc
    except JWTError as exc:
        raise InvalidToken(f"Invalid token: {exc}") from exc

    if not payload.get("sub"):
        raise InvalidToken("Token missing 'sub' claim")

    return payload
