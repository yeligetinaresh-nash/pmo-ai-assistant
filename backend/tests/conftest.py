from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.connection import engine
from app.main import app
from app.models.user import User


@pytest.fixture(scope="session")
def client():
    test_email = f"pytest_{uuid4().hex}@example.com"
    test_password = "TestPassword123!"

    with TestClient(app) as test_client:
        # ----------------------------------------------------
        # Create temporary test user
        # ----------------------------------------------------
        register_response = test_client.post(
            "/auth/register",
            json={
                "email": test_email,
                "full_name": "Pytest User",
                "password": test_password,
            },
        )

        assert register_response.status_code == 201

        # ----------------------------------------------------
        # Login and obtain JWT
        # ----------------------------------------------------
        login_response = test_client.post(
            "/auth/login",
            data={
                "username": test_email,
                "password": test_password,
            },
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        # ----------------------------------------------------
        # Automatically authenticate future test requests
        # ----------------------------------------------------
        test_client.headers.update(
            {
                "Authorization": f"Bearer {token}",
            }
        )

        yield test_client

    # --------------------------------------------------------
    # Cleanup temporary test user
    # --------------------------------------------------------
    with Session(engine) as db:
        test_user = (
            db.query(User)
            .filter(User.email == test_email)
            .first()
        )

        if test_user:
            db.delete(test_user)
            db.commit()