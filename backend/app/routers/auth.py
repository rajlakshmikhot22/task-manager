"""
Authentication routes: register, login.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - **email**: unique, valid email address
    - **username**: 3-50 chars, alphanumeric + underscores
    - **password**: min 8 chars, must include upper, lower, and digit
    """
    user = AuthService.register(db, payload)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and receive a JWT access token",
)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate with email and password.

    Returns a **Bearer** JWT token valid for the configured expiry period.
    Include it in subsequent requests as:
    ```
    Authorization: Bearer <token>
    ```
    """
    return AuthService.login(db, payload)
