from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.core.jwt import InvalidToken, decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()

TOKEN_KEY_TEMPLATE = "token:{user_id}"
TOKEN_TTL_SECONDS = 60 * 60 * 24  # keep the bound token for a day


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Это бот с доступом к большой языковой модели по JWT-токену.\n"
        "Сначала отправьте токен командой: /token <JWT>\n"
        "Потом просто напишите вопрос и я с удовольствием вам отвечу!"
    )


@router.message(Command("token"))
async def cmd_token(message: Message, command: CommandObject) -> None:
    """Store a JWT for this Telegram user after validating it."""
    token = (command.args or "").strip()
    if not token:
        await message.answer("Использование: /token <JWT>")
        return

    try:
        decode_and_validate(token)
    except InvalidToken:
        await message.answer(
            "Токен недействителен или истёк. "
            "Получите новый токен в Auth Service и попробуйте снова."
        )
        return

    redis = get_redis()
    await redis.set(
        TOKEN_KEY_TEMPLATE.format(user_id=message.from_user.id),
        token,
        ex=TOKEN_TTL_SECONDS,
    )
    await message.answer("Токен сохранён. Теперь можно отправлять запросы модели.")


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message) -> None:
    """Validate the stored token, then enqueue an LLM request via Celery."""
    redis = get_redis()
    key = TOKEN_KEY_TEMPLATE.format(user_id=message.from_user.id)
    token = await redis.get(key)

    if not token:
        await message.answer(
            "Доступ запрещён. Сначала авторизуйтесь: получите JWT в Auth Service "
            "и отправьте его командой /token <JWT>."
        )
        return

    try:
        decode_and_validate(token)
    except InvalidToken:
        await redis.delete(key)
        await message.answer(
            "Ваш токен истёк или недействителен. "
            "Авторизуйтесь заново через /token <JWT>."
        )
        return

    # Publish the long-running LLM task to RabbitMQ via Celery.
    llm_request.delay(message.chat.id, message.text)
    await message.answer("Запрос принят. Ответ придёт следующим сообщением.")
