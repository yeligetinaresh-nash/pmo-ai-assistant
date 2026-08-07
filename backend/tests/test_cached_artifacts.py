import pytest


DOCUMENT_ID = 5


@pytest.mark.parametrize(
    "artifact_path",
    [
        "project-charter",
        "wbs",
        "requirements-register",
        "raid-risk-register",
        "stakeholder-register",
        "raci-matrix",
        "project-timeline",
    ],
)
def test_get_cached_artifact(client, artifact_path) -> None:
    response = client.get(
        f"/documents/{DOCUMENT_ID}/artifacts/{artifact_path}"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0