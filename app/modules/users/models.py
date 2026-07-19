from datetime import datetime

from app.modules.shared.models import Base, UUIDMixin, CreatedAtMixin, TimeStampMixin
from sqlalchemy import String, Boolean, Enum, func
from sqlalchemy.orm import Mapped, mapped_column
from app.modules.shared.enums import OTPType, UserRole


class User(UUIDMixin, CreatedAtMixin, Base):
    """User model representing a user in the system."""

    __tablename__ = "users_users"

    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=lambda x: [e.value for e in x]),
        default=UserRole.USER,
    )
    last_verified_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=True
    )


class OTP(Base):
    """OTP model representing a one-time password for user verification."""

    __tablename__ = "users_otp"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    type: Mapped[OTPType] = mapped_column(
        Enum(OTPType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(8), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)


class TokenBlacklist(TimeStampMixin, Base):
    """TokenBlacklist model representing blacklisted JWT tokens."""

    __tablename__ = "users_token_blacklist"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    access_token: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=False)
