"""
Unit tests for profile endpoints:
GET  /api/v1/profile
PUT  /api/v1/profile
PUT  /api/v1/profile/password
"""

import pytest


class TestProfile:

    def test_get_profile(self, client, auth_headers, regular_user):
        res = client.get("/api/v1/profile", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == regular_user.email
        assert data["username"] == regular_user.username
        assert "hashed_password" not in data

    def test_get_profile_unauthenticated(self, client):
        res = client.get("/api/v1/profile")
        assert res.status_code == 401

    def test_update_profile(self, client, auth_headers):
        res = client.put("/api/v1/profile", headers=auth_headers, json={
            "full_name": "Updated Name",
            "bio": "Hello world",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["full_name"] == "Updated Name"
        assert data["bio"] == "Hello world"

    def test_change_password_success(self, client, auth_headers):
        res = client.put("/api/v1/profile/password", headers=auth_headers, json={
            "current_password": "Test@1234",
            "new_password": "NewPass@5678",
        })
        assert res.status_code == 200
        assert res.json()["success"] is True

    def test_change_password_wrong_current(self, client, auth_headers):
        res = client.put("/api/v1/profile/password", headers=auth_headers, json={
            "current_password": "WrongPass@1",
            "new_password": "NewPass@5678",
        })
        assert res.status_code == 400

    def test_change_password_same_as_current(self, client, auth_headers):
        res = client.put("/api/v1/profile/password", headers=auth_headers, json={
            "current_password": "Test@1234",
            "new_password": "Test@1234",
        })
        assert res.status_code == 400

    def test_change_password_weak_new(self, client, auth_headers):
        res = client.put("/api/v1/profile/password", headers=auth_headers, json={
            "current_password": "Test@1234",
            "new_password": "weak",
        })
        assert res.status_code == 422


class TestAdminPanel:

    def test_admin_can_list_users(self, client, admin_headers, regular_user, admin_user):
        res = client.get("/api/v1/admin/users", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert data["total"] >= 2

    def test_non_admin_cannot_list_users(self, client, auth_headers):
        res = client.get("/api/v1/admin/users", headers=auth_headers)
        assert res.status_code == 403

    def test_admin_can_toggle_user(self, client, admin_headers, regular_user):
        res = client.patch(
            f"/api/v1/admin/users/{regular_user.id}/toggle-active",
            headers=admin_headers,
        )
        assert res.status_code == 200
        assert res.json()["is_active"] is False

    def test_admin_cannot_delete_self(self, client, admin_headers, admin_user):
        res = client.delete(f"/api/v1/admin/users/{admin_user.id}", headers=admin_headers)
        assert res.status_code == 400
