from redis.asyncio import Redis

from app.core.config import settings

_redis: Redis | None = None


def get_redis() -> Redis:
    """Return a shared async Redis client.

    A single client is reused across calls instead of creating a new
    connection each time. In tests this function is patched to return a
    fakeredis instance.
    """
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis
