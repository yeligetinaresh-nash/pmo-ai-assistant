from pydantic import BaseModel, Field


class RACIActivity(BaseModel):
    activity_id: str = Field(
        description="Unique activity identifier such as RAC-001"
    )

    activity_name: str = Field(
        description="Project activity, task, decision, or deliverable"
    )

    phase: str = Field(
        default="Delivery",
        description=(
            "Initiation, Planning, Analysis, Design, Development, "
            "Testing, Deployment, Governance, Operations, or Other"
        ),
    )

    deliverable_or_outcome: str = Field(
        default="",
        description="Expected deliverable or outcome"
    )

    responsible: list[str] = Field(
        default_factory=list,
        description=(
            "Stakeholders who perform or execute the activity"
        ),
    )

    accountable: list[str] = Field(
        default_factory=list,
        description=(
            "Stakeholder with final ownership and approval authority"
        ),
    )

    consulted: list[str] = Field(
        default_factory=list,
        description=(
            "Stakeholders consulted before or during the activity"
        ),
    )

    informed: list[str] = Field(
        default_factory=list,
        description=(
            "Stakeholders informed about progress or outcomes"
        ),
    )

    source_reference: str = Field(
        default="",
        description=(
            "BRD, WBS, requirement, risk, stakeholder, or "
            "governance reference"
        ),
    )

    status: str = Field(
        default="Planned",
        description=(
            "Planned, In Progress, Complete, On Hold, "
            "Cancelled, or TBD"
        ),
    )

    notes: str = Field(
        default=""
    )


class RACIMatrix(BaseModel):
    project_title: str = Field(
        description="Project name"
    )

    matrix_purpose: str = Field(
        description="Purpose of the RACI Matrix"
    )

    total_activities: int = Field(
        ge=0
    )

    stakeholders: list[str] = Field(
        default_factory=list,
        description=(
            "Unique stakeholder names or stakeholder groups "
            "used across the matrix"
        ),
    )

    activities: list[RACIActivity] = Field(
        default_factory=list
    )

    assumptions: list[str] = Field(
        default_factory=list
    )

    notes: list[str] = Field(
        default_factory=list
    )

    artifact_status: str = Field(
        default="Draft"
    )