def test_core_artifact_routes_are_registered(
    client,
) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    expected_paths = [
        "/documents/{document_id}/artifacts/project-charter",
        "/documents/{document_id}/artifacts/wbs",
        "/documents/{document_id}/artifacts/requirements-register",
        "/documents/{document_id}/artifacts/raid-risk-register",
        "/documents/{document_id}/artifacts/stakeholder-register",
        "/documents/{document_id}/artifacts/raci-matrix",
        "/documents/{document_id}/artifacts/project-timeline",
    ]

    for path in expected_paths:
        assert path in paths