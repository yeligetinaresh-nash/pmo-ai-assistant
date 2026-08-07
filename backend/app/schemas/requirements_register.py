from pydantic import BaseModel, Field


class RequirementRegisterItem(BaseModel):
    requirement_id: str = Field(
        description="Requirement identifier such as BR-01 or NFR-01"
    )

    requirement_type: str = Field(
        default="Business",
        description=(
            "Business, Functional, Non-Functional, Security, "
            "Data, Integration, Reporting, or Other"
        ),
    )

    description: str = Field(
        description="Clear requirement description"
    )

    priority: str = Field(
        default="P2",
        description="Priority such as P1, P2, or P3"
    )

    status: str = Field(
        default="Planned",
        description=(
            "Complete, Partially Complete, Planned, "
            "In Progress, On Hold, or Cancelled"
        ),
    )

    source_reference: str = Field(
        default="",
        description="Source section, BRD reference, or analysis reference"
    )

    owner: str = Field(
        default="",
        description="Person or role responsible for delivery"
    )

    test_reference: str = Field(
        default="",
        description="Related test scenario such as TS-01"
    )

    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description="Conditions required to accept the requirement"
    )

    dependencies: list[str] = Field(
        default_factory=list,
        description="Related requirements or external dependencies"
    )

    notes: str = Field(
        default=""
    )


class RequirementsRegister(BaseModel):
    project_title: str = Field(
        description="Project name"
    )

    register_purpose: str = Field(
        description="Purpose of the Requirements Register"
    )

    total_requirements: int = Field(
        ge=0
    )

    complete_count: int = Field(
        ge=0
    )

    planned_count: int = Field(
        ge=0
    )

    partially_complete_count: int = Field(
        default=0,
        ge=0
    )

    items: list[RequirementRegisterItem] = Field(
        description="Complete list of project requirements"
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

    