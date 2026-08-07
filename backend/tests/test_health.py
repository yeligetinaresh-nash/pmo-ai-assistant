def test_health_endpoint(client) -> None:
    response = client.get("/")

    assert response.status_code == 200