import httpx

from app.core.config import settings


class OpenRouterError(Exception):
    """Raised when OpenRouter returns an error or is unreachable."""


def call_openrouter(prompt: str, model: str | None = None) -> str:
    """Send a chat completion request to OpenRouter and return the text.

    Synchronous on purpose: it is called from the Celery worker. Network
    errors and non-200 responses are turned into :class:`OpenRouterError`
    so the worker fails with a clear message instead of an opaque traceback.
    """
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
    }
    payload = {
        "model": model or settings.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        raise OpenRouterError(f"Network error calling OpenRouter: {exc}") from exc

    if response.status_code != 200:
        raise OpenRouterError(
            f"OpenRouter returned {response.status_code}: {response.text}"
        )

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise OpenRouterError(f"Unexpected OpenRouter response: {data}") from exc
