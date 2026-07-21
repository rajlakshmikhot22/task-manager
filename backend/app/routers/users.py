"""
User profile routes (self-service) and admin user management routes.
"""

from fastapi import APIRouter, Depends, File, UploadFile, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, PasswordChange, UserAdminResponse
from app.schemas.common import MessageResponse
from app.services.user_service import UserService
from app.utils.dependencies import get_current_active_user, require_admin

router = APIRouter(tags=["Users"])


# ─── Self-Service Profile ─────────────────────────────────────────────────────

@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get current user profile",
)
def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Update current user profile",
)
def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return UserService.update_profile(db, current_user, payload)


@router.put(
    "/profile/password",
    response_model=MessageResponse,
    summary="Change current user password",
)
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    UserService.change_password(db, current_user, payload)
    return MessageResponse(message="Password changed successfully")


@router.post(
    "/profile/avatar",
    response_model=UserResponse,
    summary="Upload a profile avatar image",
)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return await UserService.upload_avatar(db, current_user, file)


# ─── Admin User Management ────────────────────────────────────────────────────

@router.get(
    "/admin/users",
    summary="[Admin] List all users",
)
def admin_list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return UserService.list_users(db, page=page, size=size)


@router.delete(
    "/admin/users/{user_id}",
    response_model=MessageResponse,
    summary="[Admin] Delete a user account",
)
def admin_delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    UserService.admin_delete_user(db, user_id, admin)
    return MessageResponse(message="User deleted successfully")


@router.patch(
    "/admin/users/{user_id}/toggle-active",
    response_model=UserAdminResponse,
    summary="[Admin] Activate or deactivate a user account",
)
def admin_toggle_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return UserService.toggle_user_active(db, user_id, admin)
