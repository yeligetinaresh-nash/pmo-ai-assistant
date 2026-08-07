from pydantic import BaseModel, Field


class WBSItem(BaseModel):
    wbs_id: str = Field(
        description="Hierarchical WBS identifier, for example 1.1 or 2.3.1"
    )

    name: str = Field(
        description="Name of the phase, deliverable, work package, or task"
    )

    description: str = Field(
        default="",
        description="Clear description of the work item"
    )

    level: int = Field(
        ge=1,
        description="Hierarchy level where 1 is phase, 2 is deliverable, and 3 is work package"
    )

    parent_wbs_id: str = Field(
        default="",
        description="Parent WBS identifier. Blank for top-level items"
    )

    item_type: str = Field(
        default="Work Package",
        description="Phase, Deliverable, Work Package, or Task"
    )

    status: str = Field(
        default="Planned",
        description="Planned, In Progress, Complete, or On Hold"
    )

    owner: str = Field(
        default="",
        description="Person or role responsible for the work item"
    )

    estimated_effort_hours: float | None = Field(
        default=None,
        ge=0,
        description="Estimated effort in hours, when available"
    )

    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description="Conditions required to consider this work item complete"
    )

    dependencies: list[str] = Field(
        default_factory=list,
        description="Other WBS items or external dependencies"
    )


class WorkBreakdownStructure(BaseModel):
    project_title: str = Field(
        description="Project name"
    )

    wbs_purpose: str = Field(
        description="Purpose of the Work Breakdown Structure"
    )

    decomposition_approach: str = Field(
        default="Deliverable-based",
        description="Approach used to decompose the project"
    )

    total_estimated_effort_hours: float | None = Field(
        default=None,
        ge=0,
        description="Total estimated effort across all WBS items"
    )

    items: list[WBSItem] = Field(
        description="Hierarchical list of WBS items"
    )

    assumptions: list[str] = Field(
        default_factory=list
    )

    constraints: list[str] = Field(
        default_factory=list
    )

    notes: list[str] = Field(
        default_factory=list
    )

    artifact_status: str = Field(
        default="Draft"
    )