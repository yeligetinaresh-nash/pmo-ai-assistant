from app.main import (
    _prepare_project_timeline_for_response,
    _prepare_raci_matrix_for_response,
    _prepare_stakeholder_register_for_response,
)


def test_stakeholder_normalization() -> None:
    raw_content = {
        "stakeholders": [
            {
                "stakeholder_id": "STK-004",
                "status": "Active",
                "communication_channel": "UI notifications",
            }
        ]
    }

    result = _prepare_stakeholder_register_for_response(
        raw_content
    )

    assert result["total_stakeholders"] == 1
    assert result["stakeholders"][0]["status"] == "Planned"
    assert (
        result["stakeholders"][0]["communication_channel"]
        == "Documentation / Email; UI notifications planned"
    )
    assert result["artifact_status"] == "Draft"


def test_raci_normalization() -> None:
    raw_content = {
        "activities": [
            {
                "activity_id": "RAC-012",
                "phase": "Design",
                "status": "Planned",
                "responsible": ["Naresh Yeligeti"],
                "accountable": ["Naresh Yeligeti"],
                "consulted": [],
                "informed": [],
            }
        ]
    }

    result = _prepare_raci_matrix_for_response(
        raw_content
    )

    activity = result["activities"][0]

    assert result["total_activities"] == 1
    assert activity["phase"] == "Development"
    assert activity["status"] == "In Progress"
    assert result["artifact_status"] == "Draft"


def test_timeline_normalization() -> None:
    raw_content = {
        "activities": [
            {
                "activity_id": "TL-007",
                "start_week": 11,
                "end_week": 15,
                "duration_weeks": 5,
                "status": "In Progress",
                "progress_percent": 60,
                "milestone": False,
                "milestone_name": "",
            },
            {
                "activity_id": "TL-013",
                "start_week": 1,
                "end_week": 32,
                "duration_weeks": 32,
                "status": "In Progress",
                "progress_percent": 45,
                "milestone": False,
                "milestone_name": "",
            },
        ]
    }

    result = _prepare_project_timeline_for_response(
        raw_content
    )

    activity_by_id = {
        activity["activity_id"]: activity
        for activity in result["activities"]
    }

    assert activity_by_id["TL-007"]["status"] == "Complete"
    assert activity_by_id["TL-007"]["progress_percent"] == 100
    assert activity_by_id["TL-007"]["milestone"] is True
    assert activity_by_id["TL-013"]["end_week"] == 36
    assert result["total_duration_weeks"] == 36
    assert result["total_activities"] == 2
    assert result["artifact_status"] == "Draft"