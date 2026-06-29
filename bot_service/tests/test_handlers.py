"""Mock tests for the Telegram handlers (fakeredis + mocked Celery)."""

import time

import pytest
from jose import jwt

from app.bot import handlers
from app.core.config import settings


def _make_token(sub: str = "1", exp_offset: int = 3600) -> str:
    now = int(time.time())
    payload = {"sub": sub, "role": "user", "iat": now, "exp": now + exp_offset}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


class FakeCommand:
    def __init__(self, args: str | None):
        self.args = args


@pytest.mark.asyncio
async def test_token_command_saves_to_redis(patch_redis, make_message):
    token = _make_token()
    message = make_message("/token " + token, user_id=555)

    await handlers.cmd_token(message, FakeCommand(token))

    stored = await patch_redis.get("token:555")
    assert stored == token
    assert any("сохран" in a.lower() for a in message.answers)


@pytest.mark.asyncio
async def test_text_without_token_does_not_call_celery(
    patch_redis, make_message, mocker
):
    delay = mocker.patch("app.bot.handlers.llm_request.delay")
    message = make_message("Привет, как дела?", user_id=777)

    await handlers.handle_text(message)

    delay.assert_not_called()
    assert any("запрещ" in a.lower() or "автор" in a.lower() for a in message.answers)


@pytest.mark.asyncio
async def test_text_with_token_calls_celery(patch_redis, make_message, mocker):
    delay = mocker.patch("app.bot.handlers.llm_request.delay")
    token = _make_token()
    await patch_redis.set("token:888", token)

    message = make_message("Напиши годы жизни Л. Н. Толстого", user_id=888, chat_id=999)
    await handlers.handle_text(message)

    delay.assert_called_once_with(999, "Напиши годы жизни Л. Н. Толстого")
    assert any("принят" in a.lower() for a in message.answers)
