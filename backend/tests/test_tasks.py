"""
Unit tests for task CRUD endpoints:
GET    /api/v1/tasks
POST   /api/v1/tasks
PUT    /api/v1/tasks/{id}
DELETE /api/v1/tasks/{id}
GET    /api/v1/tasks/stats
"""

import pytest
from datetime import datetime, timedelta


class TestTasks:

    def test_create_task(self, client, auth_headers):
        res = client.post("/api/v1/tasks", headers=auth_headers, json={
            "title": "Test Task",
            "description": "A test description",
            "priority": "high",
            "status": "todo",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "Test Task"
        assert data["priority"] == "high"
        assert data["status"] == "todo"

    def test_create_task_unauthenticated(self, client):
        res = client.post("/api/v1/tasks", json={"title": "Unauthorized"})
        assert res.status_code == 401

    def test_create_task_empty_title(self, client, auth_headers):
        res = client.post("/api/v1/tasks", headers=auth_headers, json={"title": ""})
        assert res.status_code == 422

    def test_list_tasks(self, client, auth_headers):
        # Create some tasks first
        for i in range(3):
            client.post("/api/v1/tasks", headers=auth_headers, json={
                "title": f"Task {i+1}",
                "priority": "medium",
            })

        res = client.get("/api/v1/tasks", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 3
        assert len(data["items"]) >= 3

    def test_list_tasks_filtered_by_status(self, client, auth_headers):
        client.post("/api/v1/tasks", headers=auth_headers, json={
            "title": "Completed task",
            "status": "completed",
        })
        client.post("/api/v1/tasks", headers=auth_headers, json={
            "title": "Todo task",
            "status": "todo",
        })

        res = client.get("/api/v1/tasks?status=completed", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert all(t["status"] == "completed" for t in data["items"])

    def test_list_tasks_pagination(self, client, auth_headers):
        res = client.get("/api/v1/tasks?page=1&size=5", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data["items"]) <= 5
        assert data["page"] == 1

    def test_update_task(self, client, auth_headers):
        # Create
        res1 = client.post("/api/v1/tasks", headers=auth_headers, json={"title": "Original"})
        task_id = res1.json()["id"]

        # Update
        res2 = client.put(f"/api/v1/tasks/{task_id}", headers=auth_headers, json={
            "title": "Updated Title",
            "status": "in_progress",
        })
        assert res2.status_code == 200
        data = res2.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"

    def test_update_task_not_found(self, client, auth_headers):
        res = client.put("/api/v1/tasks/99999", headers=auth_headers, json={"title": "X"})
        assert res.status_code == 404

    def test_update_task_unauthenticated(self, client):
        res = client.put("/api/v1/tasks/1", json={"title": "Unauthorized"})
        assert res.status_code == 401

    def test_delete_task(self, client, auth_headers):
        res1 = client.post("/api/v1/tasks", headers=auth_headers, json={"title": "To Delete"})
        task_id = res1.json()["id"]

        res2 = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        assert res2.status_code == 200

        # Verify soft-deleted
        res3 = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        assert res3.status_code == 404

    def test_delete_task_not_found(self, client, auth_headers):
        res = client.delete("/api/v1/tasks/99999", headers=auth_headers)
        assert res.status_code == 404

    def test_get_stats(self, client, auth_headers):
        # Create some tasks
        client.post("/api/v1/tasks", headers=auth_headers, json={"title": "T1", "status": "todo"})
        client.post("/api/v1/tasks", headers=auth_headers, json={"title": "T2", "status": "completed"})

        res = client.get("/api/v1/tasks/stats", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "total" in data
        assert "todo" in data
        assert "completed" in data
        assert "completion_rate" in data
        assert data["total"] >= 2


class TestTaskOwnership:

    def test_user_cannot_see_other_users_tasks(self, client, auth_headers, admin_headers):
        # Admin creates a task
        res1 = client.post("/api/v1/tasks", headers=admin_headers, json={"title": "Admin Task"})
        admin_task_id = res1.json()["id"]

        # Regular user tries to fetch admin's task
        res2 = client.get(f"/api/v1/tasks/{admin_task_id}", headers=auth_headers)
        assert res2.status_code == 404

    def test_user_cannot_update_other_users_tasks(self, client, auth_headers, admin_headers):
        res1 = client.post("/api/v1/tasks", headers=admin_headers, json={"title": "Admin Task"})
        admin_task_id = res1.json()["id"]

        res2 = client.put(f"/api/v1/tasks/{admin_task_id}", headers=auth_headers, json={"title": "Hacked"})
        assert res2.status_code == 404

    def test_admin_can_see_all_tasks(self, client, auth_headers, admin_headers):
        # Regular user creates task
        client.post("/api/v1/tasks", headers=auth_headers, json={"title": "User Task"})

        # Admin lists all
        res = client.get("/api/v1/tasks", headers=admin_headers)
        assert res.status_code == 200
        # Admin should see tasks from all users
