import httpx

from app.core.config import settings
from app.infra.celery_app import celery_app
from app.services.openrouter_client import OpenRouterError, call_openrouter


def _send_telegram_message(chat_id: int, text: str) -> None:
    """Send a message to a Telegram chat using the Bot API (sync).

    Telegram messages have a 4096 character limit, so long answers are
    truncated to stay within it.
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    with httpx.Client(timeout=30.0) as client:
        client.post(url, json={"chat_id": chat_id, "text": text[:4096]})


@celery_app.task(name="app.tasks.llm_tasks.llm_request", bind=True, max_retries=2)
def llm_request(self, tg_chat_id: int, prompt: str) -> str:
    """Celery task: call the LLM and deliver the answer to the user.

    The returned value is stored in the Celery result backend (Redis).
    The answer is also pushed to the user via the Telegram Bot API.
    """
    try:
        answer = call_openrouter(prompt)
    except OpenRouterError as exc:
        answer = f"⚠️ Ошибка при обращении к LLM: {exc}"

    _send_telegram_message(tg_chat_id, answer)
    return answer
