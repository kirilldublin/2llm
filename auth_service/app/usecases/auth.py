from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.models import User
from app.repositories.users import UsersRepository


class AuthUseCase:
    """Business logic for the Auth Service.

    Orchestrates the repository and security helpers. Contains no SQL
    and raises domain exceptions from ``app.core.exceptions`` on error.
    """

    def __init__(self, users: UsersRepository) -> None:
        self.users = users

    async def register(self, email: str, password: str, role: str = "user") -> User:
        existing = await self.users.get_by_email(email)
        if existing is not None:
            raise UserAlreadyExistsError()
        password_hash = hash_password(password)
        return await self.users.create(
            email=email, password_hash=password_hash, role=role
        )

    async def login(self, email: str, password: str) -> str:
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return create_access_token(sub=str(user.id), role=user.role)

    async def me(self, user_id: int) -> User:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        return user
