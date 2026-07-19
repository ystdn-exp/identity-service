from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.shared.enums import OTPType
from app.modules.shared.exceptions import (
    BusinessValidationError,
    NotFoundError,
    UnauthorizedError,
)
from app.modules.users.models import TokenBlacklist, User
from app.core.database.connection import db_dependency
from app.modules.shared.utils import (
    create_otp,
    otp_exists,
    generate_otp_code,
    verify_otp,
)
from app.modules.shared.security import hash_password, verify_password
from app.modules.auth.api.v1.schemas import OTPVerifyRequest, PasswordResetVerifyRequest
from app.modules.shared.security import (
    decode_jwt_token,
    encode_jwt_token,
    encode_refresh_token,
)
from app.modules.users.tasks.email_verification import send_otp_email


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def signup(self, user_data: dict):
        # check if user already exists
        existing_user = await self.db.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        if existing_user.scalar_one_or_none():
            raise BusinessValidationError("User already exists.")

        otp = await otp_exists(self.db, user_data.get("email"), OTPType.REGISTRATION)  # type: ignore
        if not otp:
            code = generate_otp_code()
            await create_otp(self.db, user_data.get("email"), OTPType.REGISTRATION, code)  # type: ignore
            send_otp_email.delay(  # type: ignore
                user_data.get("email"), OTPType.REGISTRATION.value, code
            )

        password = user_data.pop("password", None)
        hashed_password = hash_password(password)

        # Simplification: signup always creates a regular USER (the model
        # default) - there's no self-service way to create the first admin.
        # In production this would be a one-off bootstrap (e.g. a seed
        # script or CLI command run against a trusted environment, or an
        # admin-only "promote user" endpoint gated behind an existing admin),
        # not something exposed on the public signup endpoint.
        user = User(
            **user_data,
            password=hashed_password,
            is_verified=False,
            last_verified_at=datetime.now(timezone.utc),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def login(self, credentials: dict):
        """Authenticate a user by email and password and issue a token pair."""
        # Simplification: no rate-limiting on login attempts or OTP requests
        # (signup, password-reset). In production this would sit in front of
        # these endpoints as a per-IP/per-email limiter (e.g. Redis-backed,
        # since Redis is already in the stack) to stop credential-stuffing
        # and OTP-spam abuse.
        result = await self.db.execute(
            select(User).where(User.email == credentials.get("email"))
        )
        user = result.scalar_one_or_none()
        if not user or not verify_password(credentials.get("password"), user.password):  # type: ignore
            raise BusinessValidationError("Invalid email or password.")

        return {
            "access_token": encode_jwt_token(user),
            "refresh_token": encode_refresh_token(user),
        }

    async def refresh_token(self, refresh_token: str):
        """Verify a refresh token and issue a new token pair, rotating the old one."""
        payload = decode_jwt_token(refresh_token, expected_type="refresh")

        blacklisted = await self.db.execute(
            select(TokenBlacklist).where(TokenBlacklist.refresh_token == refresh_token)
        )
        if blacklisted.scalar_one_or_none():
            raise UnauthorizedError("Token has been blacklisted.")

        result = await self.db.execute(
            select(User).where(User.id == payload.get("user_id"))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise UnauthorizedError("User not found.")

        # blacklist the consumed refresh token so it cannot be reused
        self.db.add(TokenBlacklist(access_token="", refresh_token=refresh_token))
        await self.db.commit()

        return {
            "access_token": encode_jwt_token(user),
            "refresh_token": encode_refresh_token(user),
        }

    async def verify_email(
        self, current_user: User, otp_data: OTPVerifyRequest, otp_type: OTPType
    ):
        """Verify a user's email using the provided OTP data."""
        is_valid = await verify_otp(self.db, otp_data, otp_type)
        if not is_valid:
            raise BusinessValidationError("Invalid or expired OTP.")

        current_user.is_verified = True
        current_user.last_verified_at = datetime.now(timezone.utc)
        current_user.email = otp_data.email
        await self.db.commit()
        await self.db.refresh(current_user)
        return current_user

    async def logout(self, access_token: str, refresh_token: str):
        """Blacklist the given access and refresh tokens, ending the session."""
        self.db.add(
            TokenBlacklist(access_token=access_token, refresh_token=refresh_token)
        )
        await self.db.commit()

    async def request_password_reset(self, email: str):
        """Create and send a password reset OTP for the given email."""
        existing_user = await self.db.execute(select(User).where(User.email == email))
        if not existing_user.scalar_one_or_none():
            raise NotFoundError("User not found.")

        otp = await otp_exists(self.db, email, OTPType.PASSWORD_RESET)
        if not otp:
            code = generate_otp_code()
            await create_otp(self.db, email, OTPType.PASSWORD_RESET, code)
            send_otp_email.delay(email, OTPType.PASSWORD_RESET.value, code)  # type: ignore

    async def reset_password(self, otp_data: PasswordResetVerifyRequest):
        """Verify a password reset OTP and set the user's new password."""
        is_valid = await verify_otp(self.db, otp_data, OTPType.PASSWORD_RESET)
        if not is_valid:
            raise BusinessValidationError("Invalid or expired OTP.")

        result = await self.db.execute(select(User).where(User.email == otp_data.email))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found.")

        user.password = hash_password(otp_data.new_password)
        await self.db.commit()
        await self.db.refresh(user)
        return user


def get_auth_service(db: db_dependency) -> AuthService:
    return AuthService(db)
