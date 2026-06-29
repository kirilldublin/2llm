"""Integration test for the OpenRouter client using respx (no real network)."""

import httpx
import respx

from app.core.config import settings
from app.services.openrouter_client import call_openrouter


@respx.mock
def test_call_openrouter_returns_text():
    route = respx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"role": "assistant", "content": "Лев Толстой: 1828–1910"}}
                ]
            },
        )
    )

    result = call_openrouter("Годы жизни Толстого?")

    assert result == "Лев Толстой: 1828–1910"
    assert route.called


@respx.mock
def test_call_openrouter_raises_on_error_status():
    respx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(500, text="server error")
    )

    import pytest

    from app.services.openrouter_client import OpenRouterError

    with pytest.raises(OpenRouterError):
        call_openrouter("any prompt")
