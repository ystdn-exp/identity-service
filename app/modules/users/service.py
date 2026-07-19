from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.shared.enums import OTPType, UserRole
from app.modules.users.models import User
from app.core.database import db_dependency
from app.modules.shared.exceptions import NotFoundError
from app.modules.shared.utils import create_otp, generate_otp_code, otp_exists
from app.modules.users.tasks.email_verification import send_otp_email


class UserService:
    """Service class for handling user operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(self):
        """List all users."""
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_user_by_id(self, user_id: UUID):
        """Get a user by their ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found.")

        return user

    async def delete_user(self, user_id: UUID):
        """Delete a user by their ID."""
        user = await self.get_user_by_id(user_id)

        await self.db.delete(user)
        await self.db.commit()
        return True

    async def update_user(self, user_id: UUID, update_data: dict):
        """Update a user's information."""
        user = await self.get_user_by_id(user_id)

        for key, value in update_data.items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user_email(
        self, current_user: User, user_id: UUID, update_data: dict
    ):
        """Update a user's email."""
        user = await self.get_user_by_id(user_id)

        # verify email change for regular users
        if current_user.role == UserRole.USER and (
            "email" in update_data and update_data.get("email") != user.email
        ):
            user.is_verified = False
            user.last_verified_at = datetime.now(
                timezone.utc
            )  # update last_verified_at to prevent cleanup of unverified users

            otp = await otp_exists(self.db, update_data.get("email"), OTPType.EMAIL_CHANGE)  # type: ignore
            if not otp:
                code = generate_otp_code()
                await create_otp(self.db, update_data.get("email"), OTPType.EMAIL_CHANGE, code)  # type: ignore
                send_otp_email.delay(update_data.get("email"), OTPType.EMAIL_CHANGE.value, code)  # type: ignore

        user.email = update_data.get("email")  # type: ignore

        await self.db.commit()
        await self.db.refresh(user)
        return user


def get_user_service(db: db_dependency) -> UserService:
    """
    Dependency to get an instance of UserService.

    Args:
        db (AsyncSession): Database session.

    Returns:
        UserService: An instance of UserService.
    """
    return UserService(db)
