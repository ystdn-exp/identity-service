from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select

from app.modules.users.models import User, TokenBlacklist
from app.core.database.connection import db_dependency
from app.modules.shared.security import decode_jwt_token
from app.modules.shared.exceptions import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
oauth2_scheme_dependency = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(
    token: oauth2_scheme_dependency,
    db: db_dependency,
):
    """
    Dependency to get the current user from the JWT token.

    Args:
        token (str): JWT token from the request header.
        db (AsyncSession): Database session.
    """

    if token is None:
        raise UnauthorizedError("Not authenticated.")

    payload = decode_jwt_token(token)

    # verify if the token is blacklisted
    blacklisted_token = await db.execute(
        select(TokenBlacklist).where(TokenBlacklist.access_token == token)
    )
    if blacklisted_token.scalar_one_or_none():
        raise UnauthorizedError("Token has been blacklisted.")

    user_id = payload.get("user_id")
    user_role = payload.get("role")
    result = await db.execute(
        select(User).where(User.id == user_id, User.role == user_role)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedError("User not found or invalid token.")

    return user
