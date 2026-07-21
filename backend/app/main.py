"""
FastAPI application factory and entry point.

Start with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.database import engine, Base
from app.models import user, task  # ensure models are imported before create_all
from app.routers import auth, tasks, users
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.utils.logger import setup_logging
from app.utils.security import hash_password

# ─── Logging ──────────────────────────────────────────────────────────────────
setup_logging()
logger = logging.getLogger(__name__)

# ─── Rate Limiter ─────────────────────────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)


# ─── Startup / Shutdown ───────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs setup before startup and teardown on shutdown.
    """
    logger.info("Starting %s v%s [%s]", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)

    # Create all database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created / verified")

    # Seed first admin account if none exists
    _seed_admin()

    yield  # application is running

    logger.info("Shutting down %s", settings.APP_NAME)


def _seed_admin() -> None:
    """Create the initial admin user if no admin exists yet."""
    # Skip seeding when running in test mode
    if os.getenv("TESTING") == "true":
        return

    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models.user import User, UserRole

    db: Session = SessionLocal()
    try:
        exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not exists:
            admin = User(
                email=settings.FIRST_ADMIN_EMAIL,
                username="admin",
                full_name="System Administrator",
                hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            logger.info(
                "Admin account seeded: %s  (change the password immediately!)",
                settings.FIRST_ADMIN_EMAIL,
            )
    finally:
        db.close()


# ─── App Factory ──────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "A production-ready Task Management REST API built with FastAPI. "
            "Supports JWT authentication, role-based access control, and full CRUD."
        ),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── Rate limiting ─────────────────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Security headers ──────────────────────────────────────────────────────
    app.add_middleware(SecurityHeadersMiddleware)

    # ── Request logging ───────────────────────────────────────────────────────
    app.add_middleware(LoggingMiddleware)

    # ── Static files (avatar uploads) ─────────────────────────────────────────
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

    # ── Routers ───────────────────────────────────────────────────────────────
    api_prefix = "/api/v1"
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(tasks.router, prefix=api_prefix)
    app.include_router(users.router, prefix=api_prefix)

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Application health check")
    def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    # ── Global exception handler ──────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred. Please try again later."},
        )

    return app


app = create_app()
