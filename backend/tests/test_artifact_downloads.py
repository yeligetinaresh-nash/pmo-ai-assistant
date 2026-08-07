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
def test_artifact_download(client, artifact_path) -> None:
    response = client.get(
        f"/documents/{DOCUMENT_ID}/artifacts/{artifact_path}/download"
    )

    assert response.status_code == 200

    assert len(response.content) > 0

    content_disposition = response.headers.get(
        "content-disposition",
        "",
    )

    assert "attachment" in content_disposition.lower()