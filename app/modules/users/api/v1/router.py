from uuid import UUID

from fastapi import APIRouter

from app.modules.users.dependencies import user_service_dependency
from app.modules.users.api.v1.schemas import (
    UserEmailUpdate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.modules.shared.dependencies import (
    current_user_dependency,
    require_admin_dependency,
    require_self_or_admin_dependency,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    summary="Get current user",
    description="Get the currently authenticated user",
    response_model=UserResponse,
    status_code=200,
)
async def get_me(current_user: current_user_dependency):
    return current_user


@router.get(
    "/",
    summary="Get all users",
    description="Only accessible to admins: get a list of all users",
    response_model=UserListResponse,
    status_code=200,
    dependencies=[require_admin_dependency],
)
async def get_all_users(user_service: user_service_dependency):
    users = await user_service.list_users()
    return UserListResponse(users=users, total=len(users))  # type: ignore


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    description="Only accessible to admins: get a user by their ID",
    response_model=UserResponse,
    status_code=200,
    dependencies=[require_admin_dependency],
)
async def get_user(user_id: UUID, user_service: user_service_dependency):
    return await user_service.get_user_by_id(user_id)


@router.patch(
    "/{user_id}",
    summary="Update user by ID",
    description="Update current user or admin can update any user by their ID",
    response_model=UserResponse,
    status_code=200,
)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_user: require_self_or_admin_dependency,
    user_service: user_service_dependency,
):
    updated_user = await user_service.update_user(
        user_id, data.model_dump(exclude_unset=True)
    )
    return updated_user


@router.post(
    "/{user_id}/update-email",
    summary="Update user email",
    description="Update current user email or admin can update any user email by their ID. And send an OTP to the new email for verification.",
    response_model=UserResponse,
    status_code=200,
)
async def update_user_email(
    user_id: UUID,
    data: UserEmailUpdate,
    current_user: require_self_or_admin_dependency,
    user_service: user_service_dependency,
):
    updated_user = await user_service.update_user_email(
        current_user, user_id, data.model_dump()
    )
    return updated_user


@router.delete(
    "/{user_id}",
    summary="Delete user by ID",
    description="Delete current user or admin can delete any user by their ID",
    status_code=204,
    dependencies=[require_admin_dependency],
)
async def delete_user(
    user_id: UUID,
    user_service: user_service_dependency,
):
    await user_service.delete_user(user_id)
    return None
