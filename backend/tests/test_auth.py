from fastapi.testclient import TestClient
from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.connection import engine
from app.models.user import User
from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "PMO AI Assistant API is running successfully!"
    )

def test_projects_requires_authentication():
    response = client.get("/projects")

    assert response.status_code == 401

def test_login_with_invalid_credentials():
    response = client.post(
        "/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401

def test_register_and_login_successfully():
    test_email = f"test_{uuid4().hex}@example.com"
    test_password = "TestPassword123!"

    try:
        register_response = client.post(
            "/auth/register",
            json={
                "email": test_email,
                "full_name": "Test User",
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

        data = login_response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"

    finally:
        with Session(engine) as db:
            test_user = (
                db.query(User)
                .filter(User.email == test_email)
                .first()
            )

            if test_user:
                db.delete(test_user)
                db.commit()

def test_authenticated_user_can_access_projects():
    test_email = f"test_{uuid4().hex}@example.com"
    test_password = "TestPassword123!"

    try:
        register_response = client.post(
            "/auth/register",
            json={
                "email": test_email,
                "full_name": "Test User",
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

        projects_response = client.get(
            "/projects",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert projects_response.status_code == 200

    finally:
        with Session(engine) as db:
            test_user = (
                db.query(User)
                .filter(User.email == test_email)
                .first()
            )

            if test_user:
                db.delete(test_user)
                db.commit()