from typing import Annotated
from fastapi.params import Depends

from app.modules.shared.enums import UserRole
from app.modules.users.models import User

from app.modules.shared.permissions import require_self_or_admin, require_role

require_self_or_admin_dependency = Annotated[User, Depends(require_self_or_admin)]

# Define role-based dependencies
require_admin_dependency = Depends(require_role(UserRole.ADMIN))
require_user_dependency = Depends(require_role(UserRole.USER, UserRole.ADMIN))
