"""Integration tests for the Auth Service HTTP endpoints."""

import pytest


@pytest.mark.asyncio
async def test_register_login_me_flow(client):
    # Register
    resp = await client.post(
        "/auth/register",
        json={"email": "ivanov@email.com", "password": "secret123"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "ivanov@email.com"
    assert body["role"] == "user"
    assert "password_hash" not in body

    # Login (OAuth2 form-data)
    resp = await client.post(
        "/auth/login",
        data={"username": "ivanov@email.com", "password": "secret123"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

    # /me with bearer token
    resp = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    me = resp.json()
    assert me["email"] == "ivanov@email.com"


@pytest.mark.asyncio
async def test_duplicate_registration_returns_409(client):
    payload = {"email": "dup@email.com", "password": "secret123"}
    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/auth/register", json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client):
    await client.post(
        "/auth/register",
        json={"email": "petrov@email.com", "password": "secret123"},
    )
    resp = await client.post(
        "/auth/login",
        data={"username": "petrov@email.com", "password": "wrong-pass"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_without_token_returns_401(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_token_returns_401(client):
    resp = await client.get(
        "/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert resp.status_code == 401
