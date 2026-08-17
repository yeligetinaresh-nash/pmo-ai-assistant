from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.connection import engine
from app.main import app
from app.models.project import Project
from app.models.user import User


client = TestClient(app)


# ============================================================
# Test Helpers
# ============================================================

def create_test_user_and_token():
    test_email = f"project_test_{uuid4().hex}@example.com"
    test_password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": test_email,
            "full_name": "Project Test User",
            "password": test_password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={
            "username": test_email,
            "password": test_password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return test_email, token


def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}",
    }


def cleanup_test_user(test_email):
    with Session(engine) as db:
        user = (
            db.query(User)
            .filter(User.email == test_email)
            .first()
        )

        if user:
            db.delete(user)
            db.commit()


def cleanup_project(project_id):
    with Session(engine) as db:
        project = (
            db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

        if project:
            db.delete(project)
            db.commit()


# ============================================================
# CREATE PROJECT
# ============================================================

def test_create_project():
    test_email, token = create_test_user_and_token()

    project_id = None

    try:
        response = client.post(
            "/projects",
            headers=auth_headers(token),
            json={
                "name": f"Test Project {uuid4().hex[:8]}",
                "description": "Automated project creation test",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert "id" in data
        assert data["name"].startswith("Test Project")
        assert (
            data["description"]
            == "Automated project creation test"
        )

        project_id = data["id"]

    finally:
        if project_id:
            cleanup_project(project_id)

        cleanup_test_user(test_email)


# ============================================================
# READ PROJECT
# ============================================================

def test_read_project():
    test_email, token = create_test_user_and_token()

    project_id = None

    try:
        create_response = client.post(
            "/projects",
            headers=auth_headers(token),
            json={
                "name": f"Read Test {uuid4().hex[:8]}",
                "description": "Project read test",
            },
        )

        assert create_response.status_code == 200

        project_id = create_response.json()["id"]

        response = client.get(
            f"/projects/{project_id}",
            headers=auth_headers(token),
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == project_id
        assert data["description"] == "Project read test"

    finally:
        if project_id:
            cleanup_project(project_id)

        cleanup_test_user(test_email)


# ============================================================
# LIST PROJECTS
# ============================================================

def test_list_projects():
    test_email, token = create_test_user_and_token()

    project_id = None

    try:
        create_response = client.post(
            "/projects",
            headers=auth_headers(token),
            json={
                "name": f"List Test {uuid4().hex[:8]}",
                "description": "Project list test",
            },
        )

        assert create_response.status_code == 200

        project_id = create_response.json()["id"]

        response = client.get(
            "/projects",
            headers=auth_headers(token),
        )

        assert response.status_code == 200

        data = response.json()

        assert isinstance(data, list)

        project_ids = [
            project["id"]
            for project in data
        ]

        assert project_id in project_ids

    finally:
        if project_id:
            cleanup_project(project_id)

        cleanup_test_user(test_email)


# ============================================================
# UPDATE PROJECT
# ============================================================

def test_update_project():
    test_email, token = create_test_user_and_token()

    project_id = None

    try:
        create_response = client.post(
            "/projects",
            headers=auth_headers(token),
            json={
                "name": f"Update Test {uuid4().hex[:8]}",
                "description": "Before update",
            },
        )

        assert create_response.status_code == 200

        project_id = create_response.json()["id"]

        response = client.put(
            f"/projects/{project_id}",
            headers=auth_headers(token),
            json={
                "name": "Updated Automated Project",
                "description": "After update",
                "status": "In Progress",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == project_id
        assert data["name"] == "Updated Automated Project"
        assert data["description"] == "After update"
        assert data["status"] == "In Progress"

    finally:
        if project_id:
            cleanup_project(project_id)

        cleanup_test_user(test_email)


# ============================================================
# DELETE PROJECT
# ============================================================

def test_delete_project():
    test_email, token = create_test_user_and_token()

    project_id = None

    try:
        create_response = client.post(
            "/projects",
            headers=auth_headers(token),
            json={
                "name": f"Delete Test {uuid4().hex[:8]}",
                "description": "Project delete test",
            },
        )

        assert create_response.status_code == 200

        project_id = create_response.json()["id"]

        delete_response = client.delete(
            f"/projects/{project_id}",
            headers=auth_headers(token),
        )

        assert delete_response.status_code == 200

        data = delete_response.json()

        assert data["message"] == (
            "Project deleted successfully"
        )

        get_response = client.get(
            f"/projects/{project_id}",
            headers=auth_headers(token),
        )

        assert get_response.status_code == 404

        project_id = None

    finally:
        if project_id:
            cleanup_project(project_id)

        cleanup_test_user(test_email)


# ============================================================
# PROJECT NOT FOUND
# ============================================================

def test_project_not_found():
    test_email, token = create_test_user_and_token()

    try:
        response = client.get(
            "/projects/999999999",
            headers=auth_headers(token),
        )

        assert response.status_code == 404

    finally:
        cleanup_test_user(test_email)


# ============================================================
# PROJECT APIs REQUIRE JWT
# ============================================================

def test_project_create_requires_authentication():
    response = client.post(
        "/projects",
        json={
            "name": "Unauthorized Project",
            "description": "Should not be created",
        },
    )

    assert response.status_code == 401