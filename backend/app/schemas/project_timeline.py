from pydantic import BaseModel, Field


class TimelineActivity(BaseModel):
    activity_id: str = Field(
        description="Unique activity ID such as TL-001"
    )

    activity_name: str = Field(
        description="Project activity, task, or deliverable"
    )

    phase: str = Field(
        default="Development",
        description=(
            "Initiation, Planning, Analysis, Design, Development, "
            "Testing, Deployment, Governance, Operations, or Other"
        ),
    )

    start_week: int = Field(
        ge=1,
        description="Planned start week number"
    )

    end_week: int = Field(
        ge=1,
        description="Planned end week number"
    )

    duration_weeks: int = Field(
        ge=1,
        description="Planned activity duration in weeks"
    )

    predecessor_ids: list[str] = Field(
        default_factory=list,
        description="Activity IDs that must be completed first"
    )

    owner: str = Field(
        default="Naresh Yeligeti",
        description="Activity owner"
    )

    status: str = Field(
        default="Planned",
        description=(
            "Planned, In Progress, Complete, On Hold, "
            "Cancelled, or TBD"
        ),
    )

    progress_percent: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Activity completion percentage"
    )

    milestone: bool = Field(
        default=False,
        description="Whether the activity is a milestone"
    )

    milestone_name: str = Field(
        default="",
        description="Milestone name when milestone is true"
    )

    deliverable_or_outcome: str = Field(
        default="",
        description="Expected deliverable or outcome"
    )

    source_reference: str = Field(
        default="",
        description="Related BRD, WBS, requirement, or artifact reference"
    )

    notes: str = Field(
        default=""
    )


class ProjectTimeline(BaseModel):
    project_title: str = Field(
        description="Project name"
    )

    timeline_purpose: str = Field(
        description="Purpose of the project timeline"
    )

    planning_basis: str = Field(
        default="Relative weekly schedule",
        description="Basis used to create the timeline"
    )

    total_duration_weeks: int = Field(
        ge=1
    )

    total_activities: int = Field(
        ge=0
    )

    total_milestones: int = Field(
        ge=0
    )

    activities: list[TimelineActivity] = Field(
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