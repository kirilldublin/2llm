from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.core.security import TokenError, TokenExpired, decode_token
from app.db.session import AsyncSessionLocal
from app.repositories.users import UsersRepository
from app.usecases.auth import AuthUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session, closing it when the request ends."""
    async with AsyncSessionLocal() as session:
        yield session


def get_users_repo(db: AsyncSession = Depends(get_db)) -> UsersRepository:
    return UsersRepository(db)


def get_auth_uc(
    repo: UsersRepository = Depends(get_users_repo),
) -> AuthUseCase:
    return AuthUseCase(repo)


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Decode the bearer token and return the user id from ``sub``.

    Raises the appropriate domain exception when the token is expired
    or otherwise invalid.
    """
    try:
        payload = decode_token(token)
    except TokenExpired as exc:
        raise TokenExpiredError() from exc
    except TokenError as exc:
        raise InvalidTokenError() from exc

    sub = payload.get("sub")
    if sub is None:
        raise InvalidTokenError()
    try:
        return int(sub)
    except (TypeError, ValueError) as exc:
        raise InvalidTokenError() from exc
