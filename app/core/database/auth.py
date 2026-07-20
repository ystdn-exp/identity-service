from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer
from sqlalchemy import select

from app.modules.users.models import User, TokenBlacklist
from app.core.database.connection import db_dependency
from app.modules.shared.security import decode_jwt_token
from app.modules.shared.exceptions.constants import UnauthorizedError

http_bearer = HTTPBearer(auto_error=False)
bearer_scheme_dependency = Annotated[str, Depends(http_bearer)]


async def get_current_user(
    token: bearer_scheme_dependency,
    db: db_dependency,
):
    """
    Dependency to get the current user from the JWT token.

    Args:
        token (str): JWT token from the request header.
        db (AsyncSession): Database session.
    """

    token = getattr(token, "credentials", None)  # type: ignore
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
