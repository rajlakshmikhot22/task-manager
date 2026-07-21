"""
Unit tests for authentication endpoints:
POST /api/v1/auth/register
POST /api/v1/auth/login
"""

import pytest


class TestRegister:

    def test_register_success(self, client):
        res = client.post("/api/v1/auth/register", json={
            "email": "newuser@test.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "Secure@123",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == "newuser@test.com"
        assert data["username"] == "newuser"
        assert data["role"] == "user"
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, regular_user):
        res = client.post("/api/v1/auth/register", json={
            "email": "user@test.com",  # already exists
            "username": "another",
            "password": "Secure@123",
        })
        assert res.status_code == 409
        assert "email" in res.json()["detail"].lower()

    def test_register_duplicate_username(self, client, regular_user):
        res = client.post("/api/v1/auth/register", json={
            "email": "unique@test.com",
            "username": "testuser",   # already exists
            "password": "Secure@123",
        })
        assert res.status_code == 409

    def test_register_weak_password(self, client):
        res = client.post("/api/v1/auth/register", json={
            "email": "weak@test.com",
            "username": "weakpw",
            "password": "short",
        })
        assert res.status_code == 422

    def test_register_invalid_email(self, client):
        res = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "username": "someuser",
            "password": "Secure@123",
        })
        assert res.status_code == 422

    def test_register_invalid_username(self, client):
        res = client.post("/api/v1/auth/register", json={
            "email": "valid@test.com",
            "username": "ab",  # too short
            "password": "Secure@123",
        })
        assert res.status_code == 422

    def test_register_missing_fields(self, client):
        res = client.post("/api/v1/auth/register", json={"email": "a@b.com"})
        assert res.status_code == 422


class TestLogin:

    def test_login_success(self, client, regular_user):
        res = client.post("/api/v1/auth/login", json={
            "email": "user@test.com",
            "password": "Test@1234",
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    def test_login_wrong_password(self, client, regular_user):
        res = client.post("/api/v1/auth/login", json={
            "email": "user@test.com",
            "password": "WrongPass@1",
        })
        assert res.status_code == 401

    def test_login_nonexistent_email(self, client):
        res = client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com",
            "password": "Test@1234",
        })
        assert res.status_code == 401

    def test_login_missing_fields(self, client):
        res = client.post("/api/v1/auth/login", json={"email": "user@test.com"})
        assert res.status_code == 422

    def test_login_inactive_user(self, client, db, regular_user):
        regular_user.is_active = False
        db.commit()
        res = client.post("/api/v1/auth/login", json={
            "email": "user@test.com",
            "password": "Test@1234",
        })
        assert res.status_code == 403
