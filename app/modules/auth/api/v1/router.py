from uuid import UUID
from fastapi import APIRouter

from app.modules.auth.dependencies import auth_service_dependency
from app.modules.auth.api.v1.schemas import (
    LoginRequest,
    MessageResponse,
    OTPVerifyRequest,
    PasswordResetRequest,
    PasswordResetVerifyRequest,
    RefreshTokenRequest,
    SignupRequest,
    TokenResponse,
)
from app.modules.users.api.v1.schemas import UserResponse
from app.modules.shared.dependencies import (
    current_user_dependency,
    oauth2_scheme_dependency,
)
from app.modules.shared.enums import OTPType

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup",
    summary="Sign up a new user",
    description="Create a new user account",
    response_model=UserResponse,
    status_code=201,
)
async def signup(user: SignupRequest, auth_service: auth_service_dependency):
    return await auth_service.signup(user.model_dump())


@router.post(
    "/login",
    summary="Log in a user",
    description="Authenticate a user and return a token",
    response_model=TokenResponse,
    status_code=200,
)
async def login(credentials: LoginRequest, auth_service: auth_service_dependency):
    return await auth_service.login(credentials.model_dump())


@router.post(
    "/refresh",
    summary="Refresh an access token",
    description="Refresh an access token using a refresh token",
    response_model=TokenResponse,
    status_code=200,
)
async def refresh_token(
    payload: RefreshTokenRequest, auth_service: auth_service_dependency
):
    return await auth_service.refresh_token(payload.refresh_token)


@router.post(
    "/verify",
    summary="Verify a user's email",
    description="Send a verification email to a user",
    response_model=UserResponse,
    status_code=200,
)
async def verify_email(
    otp_data: OTPVerifyRequest,
    current_user: current_user_dependency,
    auth_service: auth_service_dependency,
):
    return await auth_service.verify_email(current_user, otp_data, OTPType.REGISTRATION)


@router.post(
    "/verify-email-change/{user_id}",
    summary="Verify a user's email change",
    description="Verify a user's email change using an OTP code",
    response_model=UserResponse,
    status_code=200,
)
async def verify_email_change(
    user_id: UUID,
    otp_data: OTPVerifyRequest,
    current_user: current_user_dependency,
    auth_service: auth_service_dependency,
):
    return await auth_service.verify_email(current_user, otp_data, OTPType.EMAIL_CHANGE)


@router.post(
    "/password-reset",
    summary="Request a password reset",
    description="Send an OTP to the user's email to reset their password.",
    response_model=MessageResponse,
    status_code=200,
)
async def password_reset(
    data: PasswordResetRequest, auth_service: auth_service_dependency
):
    await auth_service.request_password_reset(data.email)
    return MessageResponse(message="Password reset OTP sent to your email.")


@router.post(
    "/verify-password-reset",
    summary="Verify a password reset",
    description="Verify a password reset OTP and set a new password.",
    response_model=MessageResponse,
    status_code=200,
)
async def verify_password_reset(
    data: PasswordResetVerifyRequest, auth_service: auth_service_dependency
):
    await auth_service.reset_password(data)
    return MessageResponse(message="Password has been reset successfully.")


@router.post(
    "/logout",
    summary="Log out a user",
    description="Invalidate the user's access and refresh tokens",
    response_model=MessageResponse,
    status_code=200,
)
async def logout(
    current_user: current_user_dependency,
    access_token: oauth2_scheme_dependency,
    data: RefreshTokenRequest,
    auth_service: auth_service_dependency,
):
    await auth_service.logout(access_token, data.refresh_token)
    return MessageResponse(message="Successfully logged out.")
