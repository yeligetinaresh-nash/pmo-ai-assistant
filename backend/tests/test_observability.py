def test_request_id_is_added_to_response(
    client,
):
    response = client.get("/")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]


def test_existing_request_id_is_preserved(
    client,
):
    request_id = "pytest-request-123"

    response = client.get(
        "/",
        headers={
            "X-Request-ID": request_id,
        },
    )

    assert response.status_code == 200

    assert (
        response.headers["X-Request-ID"]
        == request_id
    )


def test_request_id_added_to_not_found_response(
    client,
):
    response = client.get(
        "/this-route-does-not-exist"
    )

    assert response.status_code == 404
    assert "X-Request-ID" in response.headers