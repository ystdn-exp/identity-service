from pydantic import BaseModel, EmailStr, Field

from app.modules.users.api.v1.schemas import UserCreate


class SignupRequest(UserCreate):
    """Request schema for user signup."""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=8, max_length=8)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetVerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=8, max_length=8)
    new_password: str = Field(..., min_length=8, max_length=255)


class MessageResponse(BaseModel):
    message: str
