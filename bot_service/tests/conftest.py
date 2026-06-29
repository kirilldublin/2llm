import fakeredis.aioredis
import pytest


@pytest.fixture
def fake_redis():
    """In-memory async Redis used in place of the real client."""
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def patch_redis(fake_redis, monkeypatch):
    """Patch get_redis where it is *used* (app.bot.handlers.get_redis).

    Patching the import site rather than app.infra.redis ensures the
    handlers never try to reach a real redis:6379.
    """
    monkeypatch.setattr("app.bot.handlers.get_redis", lambda: fake_redis)
    return fake_redis


class FakeUser:
    def __init__(self, user_id: int):
        self.id = user_id


class FakeChat:
    def __init__(self, chat_id: int):
        self.id = chat_id


class FakeMessage:
    """Minimal stand-in for aiogram's Message with an async ``answer``."""

    def __init__(self, text: str, user_id: int = 111, chat_id: int = 222):
        self.text = text
        self.from_user = FakeUser(user_id)
        self.chat = FakeChat(chat_id)
        self.answers: list[str] = []

    async def answer(self, text: str, **kwargs) -> None:
        self.answers.append(text)


@pytest.fixture
def make_message():
    def _make(text: str, user_id: int = 111, chat_id: int = 222) -> FakeMessage:
        return FakeMessage(text, user_id=user_id, chat_id=chat_id)

    return _make
