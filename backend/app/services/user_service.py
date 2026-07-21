"""
User profile management and admin user service.
"""

import os
import shutil
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status

from app.models.user import User
from app.schemas.user import UserUpdate, PasswordChange
from app.utils.security import hash_password, verify_password
from app.config import settings
import logging

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_AVATAR_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


class UserService:

    @staticmethod
    def get_profile(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    @staticmethod
    def update_profile(db: Session, user: User, payload: UserUpdate) -> User:
        update_data = payload.model_dump(exclude_unset=True)

        # Check username uniqueness if being changed
        if "username" in update_data and update_data["username"] != user.username:
            if db.query(User).filter(User.username == update_data["username"]).first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username is already taken",
                )

        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        logger.info("Profile updated for user id=%s", user.id)
        return user

    @staticmethod
    def change_password(db: Session, user: User, payload: PasswordChange) -> None:
        if not verify_password(payload.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )
        if payload.current_password == payload.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must differ from the current password",
            )
        user.hashed_password = hash_password(payload.new_password)
        db.commit()
        logger.info("Password changed for user id=%s", user.id)

    @staticmethod
    async def upload_avatar(db: Session, user: User, file: UploadFile) -> User:
        # Validate content type
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '{file.content_type}'. Allowed: JPEG, PNG, GIF, WEBP",
            )

        # Read and size-check
        content = await file.read()
        if len(content) > MAX_AVATAR_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB} MB limit",
            )

        # Generate unique filename and save
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
        filename = f"avatar_{user.id}_{uuid.uuid4().hex}.{ext}"
        dest_path = os.path.join(settings.UPLOAD_DIR, filename)

        with open(dest_path, "wb") as fp:
            fp.write(content)

        # Remove old avatar file if it exists
        if user.avatar:
            old_path = os.path.join(settings.UPLOAD_DIR, os.path.basename(user.avatar))
            if os.path.exists(old_path):
                os.remove(old_path)

        user.avatar = f"/uploads/{filename}"
        db.commit()
        db.refresh(user)
        return user

    # ─── Admin ────────────────────────────────────────────────────────────────

    @staticmethod
    def list_users(db: Session, page: int = 1, size: int = 20) -> dict:
        import math
        total = db.query(User).count()
        users = (
            db.query(User)
            .order_by(User.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return {
            "items": users,
            "total": total,
            "page": page,
            "size": size,
            "pages": math.ceil(total / size) if total else 0,
        }

    @staticmethod
    def admin_delete_user(db: Session, user_id: int, requesting_user: User) -> None:
        if user_id == requesting_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot delete your own account via the admin panel",
            )
        target = db.query(User).filter(User.id == user_id).first()
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        db.delete(target)
        db.commit()
        logger.warning("Admin %s deleted user id=%s", requesting_user.id, user_id)

    @staticmethod
    def toggle_user_active(db: Session, user_id: int, requesting_user: User) -> User:
        target = db.query(User).filter(User.id == user_id).first()
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if target.id == requesting_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own active status",
            )
        target.is_active = not target.is_active
        db.commit()
        db.refresh(target)
        return target
