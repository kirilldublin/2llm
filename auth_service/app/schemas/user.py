from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserPublic(BaseModel):
    """Public representation of a user. Never exposes the password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: str
    created_at: datetime
