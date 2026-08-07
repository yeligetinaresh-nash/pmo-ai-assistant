def test_get_nonexistent_document_method_not_allowed(client) -> None:
    response = client.get("/documents/999999")

    assert response.status_code == 405


def test_delete_nonexistent_document(client) -> None:
    response = client.delete("/documents/999999")

    assert response.status_code == 404