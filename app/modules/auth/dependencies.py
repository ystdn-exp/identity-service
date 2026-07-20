from typing import Annotated

from fastapi import Depends

from app.modules.auth.service import AuthService, get_auth_service
from app.modules.auth.api.v1.schemas import LoginRequest

auth_service_dependency = Annotated[AuthService, Depends(get_auth_service)]
