"""
Authentication business logic: registration, login, token issuance.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, Token
from app.utils.security import hash_password, verify_password, create_access_token
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class AuthService:

    @staticmethod
    def register(db: Session, payload: UserCreate) -> User:
        """
        Register a new user account.

        Raises:
            HTTPException 409 if email or username already exists.
        """
        # Check email uniqueness
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )

        # Check username uniqueness
        if db.query(User).filter(User.username == payload.username).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already taken",
            )

        user = User(
            email=payload.email,
            username=payload.username,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            role=UserRole.USER,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info("New user registered: %s (%s)", user.username, user.email)
        return user

    @staticmethod
    def login(db: Session, payload: UserLogin) -> Token:
        """
        Authenticate user credentials and issue a JWT.

        Raises:
            HTTPException 401 for invalid credentials.
            HTTPException 403 for deactivated account.
        """
        user = db.query(User).filter(User.email == payload.email).first()

        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated. Please contact support.",
            )

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        }
        access_token = create_access_token(data=token_data)

        # Update last login timestamp
        user.last_login = datetime.utcnow()
        db.commit()

        expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        logger.info("User logged in: %s", user.email)

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=expire_seconds,
        )
