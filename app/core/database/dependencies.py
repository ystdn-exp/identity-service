from fastapi.params import Depends
from typing_extensions import Annotated

from app.core.database.auth import get_current_user
from app.modules.users.models import User

current_user_dependency = Annotated[User, Depends(get_current_user)]
