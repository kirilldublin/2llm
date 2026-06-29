"""Unit tests for the security helpers (pure functions, no DB / FastAPI)."""

from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_is_not_plaintext():
    password = "s3cret-password"
    hashed = hash_password(password)
    assert hashed != password
    assert hashed.startswith("$2")  # bcrypt prefix


def test_verify_password_accepts_correct_and_rejects_wrong():
    password = "s3cret-password"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_create_and_decode_token_roundtrip():
    token = create_access_token(sub="42", role="admin")
    payload = decode_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "admin"
    assert "iat" in payload
    assert "exp" in payload
