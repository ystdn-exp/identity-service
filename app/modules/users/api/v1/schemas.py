from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.shared.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=255,
    )


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)


class UserEmailUpdate(BaseModel):
    email: EmailStr


class UserResponse(UserBase):
    id: UUID
    role: UserRole
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
