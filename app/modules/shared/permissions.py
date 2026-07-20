from uuid import UUID

from app.modules.shared.enums import UserRole
from app.modules.shared.exceptions.constants import ForbiddenError
from app.core.database.dependencies import current_user_dependency


def require_role(*allowed_roles: UserRole):
    """
    Dependency to require a specific user role for access.

    Args:
        allowed_roles (UserRole): One or more allowed user roles.

    Raises:
        ForbiddenError: If the current user's role is not in the allowed roles.
    """

    def dependency(current_user: current_user_dependency):
        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                f"Access denied. Required role(s): {', '.join([role.value for role in allowed_roles])}"
            )

    return dependency


def require_self_or_admin(user_id: UUID, current_user: current_user_dependency):
    """
    Dependency to require that the current user is either the user themselves or an admin.

    Args:
        user_id (UUID): The ID of the user being accessed, taken from the path.
    Raises:
        ForbiddenError: If the current user is neither the user themselves nor an admin.
    """
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise ForbiddenError(
            "Access denied. You must be the user or an admin to access this resource."
        )

    return current_user
