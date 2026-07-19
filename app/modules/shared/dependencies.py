from typing import Annotated
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select

from app.modules.shared.enums import UserRole
from app.modules.shared.exceptions import UnauthorizedError
from app.core.database import db_dependency
from app.modules.shared.security import decode_jwt_token
from app.modules.users.models import User, TokenBlacklist

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
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


current_user_dependency = Annotated[User, Depends(get_current_user)]

from app.modules.shared.permissions import (
    require_self_or_admin,
    require_role,
)  # noqa: E402

require_self_or_admin_dependency = Annotated[User, Depends(require_self_or_admin)]

# Define role-based dependencies
require_admin_dependency = Depends(require_role(UserRole.ADMIN))
require_user_dependency = Depends(require_role(UserRole.USER, UserRole.ADMIN))
