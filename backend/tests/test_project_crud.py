def test_create_project(client) -> None:
    payload = {
        "name": "Pytest Project",
        "description": "Temporary project created by automated test",
    }

    response = client.post(
        "/projects",
        json=payload,
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["name"] == "Pytest Project"
    assert "id" in data


def test_list_projects(client) -> None:
    response = client.get("/projects")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_nonexistent_project(client) -> None:
    response = client.get("/projects/999999")

    assert response.status_code == 404


def test_update_project(client) -> None:
    create_response = client.post(
        "/projects",
        json={
            "name": "Project Before Update",
            "description": "Before update",
        },
    )

    assert create_response.status_code in (200, 201)

    project_id = create_response.json()["id"]

    update_response = client.put(
        f"/projects/{project_id}",
        json={
            "name": "Project After Update",
            "description": "After update",
            "status": "In Progress",
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["name"] == "Project After Update"
    assert data["description"] == "After update"
    assert data["status"] == "In Progress"


def test_delete_project(client) -> None:
    create_response = client.post(
        "/projects",
        json={
            "name": "Project To Delete",
            "description": "Temporary project",
        },
    )

    assert create_response.status_code in (200, 201)

    project_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/projects/{project_id}"
    )

    assert delete_response.status_code in (
        200,
        204,
    )

    get_response = client.get(
        f"/projects/{project_id}"
    )

    assert get_response.status_code == 404


def test_create_project_validation(client) -> None:
    response = client.post(
        "/projects",
        json={},
    )

    assert response.status_code == 422