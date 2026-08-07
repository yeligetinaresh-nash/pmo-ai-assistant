def test_openapi_metadata(client) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    payload = response.json()

    assert "info" in payload
    assert "title" in payload["info"]
    assert "paths" in payload
    assert len(payload["paths"]) > 0