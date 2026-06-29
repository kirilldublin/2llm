"""Unit tests for JWT validation in the Bot Service."""

import time

import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import InvalidToken, decode_and_validate


def _make_token(sub: str = "1", role: str = "user", exp_offset: int = 3600) -> str:
    now = int(time.time())
    payload = {"sub": sub, "role": role, "iat": now, "exp": now + exp_offset}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def test_decode_valid_token_returns_sub():
    token = _make_token(sub="42", role="admin")
    payload = decode_and_validate(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"


def test_garbage_string_raises():
    with pytest.raises(InvalidToken):
        decode_and_validate("this-is-not-a-jwt")


def test_expired_token_raises():
    token = _make_token(exp_offset=-10)
    with pytest.raises(InvalidToken):
        decode_and_validate(token)


def test_token_without_sub_raises():
    now = int(time.time())
    token = jwt.encode(
        {"role": "user", "iat": now, "exp": now + 3600},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )
    with pytest.raises(InvalidToken):
        decode_and_validate(token)
