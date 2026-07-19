from typing import Annotated

from fastapi import Depends

from app.modules.users.service import UserService, get_user_service

user_service_dependency = Annotated[UserService, Depends(get_user_service)]
