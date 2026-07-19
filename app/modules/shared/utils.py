from random import randint
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.shared.enums import OTPType
from app.modules.users.models import OTP


def generate_otp_code() -> str:
    """
    Generate a random 8-digit OTP code.

    Returns:
        str: A 8-digit OTP code as a string.
    """

    return f"{randint(10000000, 99999999)}"


async def create_otp(db: AsyncSession, email: str, otp_type: OTPType, code: str) -> OTP:
    """
    Create a new OTP entry in the database for the given email.
    """

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    otp = OTP(
        email=email,
        code=code,
        expires_at=expires_at,
        type=otp_type,
    )
    db.add(otp)
    await db.commit()
    await db.refresh(otp)
    return otp


async def otp_exists(db: AsyncSession, email: str, otp_type: OTPType) -> bool:
    """
    Check if an OTP exists for the given email and type.

    Args:
        email (str): The email address to check.
        otp_type (OTPType): The type of OTP to check.

    Returns:
        bool: True if an OTP exists, False otherwise.
    """
    result = await db.execute(
        select(OTP).where(
            OTP.email == email, OTP.type == otp_type, OTP.is_used == False
        )
    )
    return result.scalar_one_or_none() is not None


async def verify_otp(db: AsyncSession, otp_data: ..., otp_type: OTPType) -> bool:
    """
    Verify the provided OTP code for the given email.

    Args:
        email (str): The email address associated with the OTP.
        code (str): The OTP code to verify.

    Returns:
        bool: True if the OTP is valid and not expired, False otherwise.
    """
    result = await db.execute(
        select(OTP).where(
            OTP.email == otp_data.email,
            OTP.code == otp_data.code,
            OTP.type == otp_type,
            OTP.is_used == False,
            OTP.expires_at > datetime.now(timezone.utc),
        )
    )
    otp = result.scalar_one_or_none()
    if not otp:
        return False

    # mark the OTP as used to prevent reuse
    otp.is_used = True
    await db.commit()

    return True
