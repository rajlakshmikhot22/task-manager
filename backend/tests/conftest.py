"""
pytest fixtures shared across all test modules.
Uses an in-memory SQLite database so tests are isolated and fast.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.utils.security import hash_password

# ─── In-memory test database ──────────────────────────────────────────────────
TEST_DB_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once for the test session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():
    """Provide a clean DB session per test; rollback changes after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """
    Provide a TestClient with the DB session overridden.
    TESTING=true env var tells the app lifespan to skip admin seeding.
    """
    import os
    os.environ["TESTING"] = "true"
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    os.environ.pop("TESTING", None)


# ─── Pre-seeded users ─────────────────────────────────────────────────────────

@pytest.fixture
def regular_user(db) -> User:
    user = User(
        email="user@test.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hash_password("Test@1234"),
        role=UserRole.USER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db) -> User:
    user = User(
        email="admin@test.com",
        username="testadmin",
        full_name="Test Admin",
        hashed_password=hash_password("Admin@1234"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def user_token(client, regular_user) -> str:
    """Login as regular user and return access token."""
    res = client.post("/api/v1/auth/login", json={"email": "user@test.com", "password": "Test@1234"})
    return res.json()["access_token"]


@pytest.fixture
def admin_token(client, admin_user) -> str:
    """Login as admin and return access token."""
    res = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "Admin@1234"})
    return res.json()["access_token"]


@pytest.fixture
def auth_headers(user_token) -> dict:
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}
