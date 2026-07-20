import bcrypt
import jwt

from datetime import datetime, timedelta, timezone
from jwt.exceptions import PyJWTError

from app.core.settings import (
    JWT_ACCESS_EXPIRE_MINUTES,
    JWT_REFRESH_EXPIRE_DAYS,
    JWT_ALGORITHM,
    settings,
)
from app.modules.shared.exceptions.constants import UnauthorizedError
from app.modules.users.models import User


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def decode_jwt_token(token: str, expected_type: str = "access") -> dict:
    """
    Decode a JWT token and return the payload.

    Args:
        token (str): The JWT token to decode.
        expected_type (str): The expected token type ("access" or "refresh").
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])

        user_id = payload.get("user_id")
        if not user_id or payload.get("type") != expected_type:
            raise UnauthorizedError(message="Invalid token.")

        return payload
    except PyJWTError:
        raise UnauthorizedError(message="Invalid token.")


def _create_token(user: User, expires_delta: timedelta, token_type: str) -> str:
    """
    Encode a JWT of the given type and lifetime for the given user.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": str(user.id),
        "role": user.role.value,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def encode_jwt_token(user: User) -> str:
    """
    Encode a short-lived access token for the given user.

    Args:
        user (User): The user for whom to create the token.

    Returns:
        str: The encoded JWT access token.
    """
    return _create_token(user, timedelta(minutes=JWT_ACCESS_EXPIRE_MINUTES), "access")


def encode_refresh_token(user: User) -> str:
    """
    Encode a long-lived refresh token for the given user.

    Args:
        user (User): The user for whom to create the token.

    Returns:
        str: The encoded JWT refresh token.
    """
    return _create_token(user, timedelta(days=JWT_REFRESH_EXPIRE_DAYS), "refresh")
