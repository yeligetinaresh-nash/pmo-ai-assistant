from pydantic import BaseModel, Field


class StakeholderItem(BaseModel):
    stakeholder_id: str = Field(
        description="Unique stakeholder identifier such as STK-001"
    )

    name: str = Field(
        description="Stakeholder name or stakeholder group"
    )

    role: str = Field(
        description="Project or business role"
    )

    organization: str = Field(
        default="",
        description="Organization, department, or team"
    )

    stakeholder_type: str = Field(
        default="Internal",
        description="Internal, External, Vendor, Customer, or Other"
    )

    interest_level: str = Field(
        default="Medium",
        description="High, Medium, or Low"
    )

    influence_level: str = Field(
        default="Medium",
        description="High, Medium, or Low"
    )

    power_interest_quadrant: str = Field(
        default="Keep Informed",
        description=(
            "Manage Closely, Keep Satisfied, Keep Informed, "
            "or Monitor"
        ),
    )

    current_engagement: str = Field(
        default="Neutral",
        description=(
            "Unaware, Resistant, Neutral, Supportive, or Leading"
        ),
    )

    desired_engagement: str = Field(
        default="Supportive",
        description=(
            "Unaware, Resistant, Neutral, Supportive, or Leading"
        ),
    )

    expectations: list[str] = Field(
        default_factory=list,
        description="Key expectations from the project"
    )

    responsibilities: list[str] = Field(
        default_factory=list,
        description="Primary stakeholder responsibilities"
    )

    communication_needs: list[str] = Field(
        default_factory=list,
        description="Information and communication needs"
    )

    communication_frequency: str = Field(
        default="As Needed",
        description=(
            "Daily, Weekly, Fortnightly, Monthly, "
            "At Milestones, As Needed, or Other"
        ),
    )

    communication_channel: str = Field(
        default="Email / Meeting",
        description="Preferred communication channel"
    )

    owner: str = Field(
        default="Naresh Yeligeti",
        description="Relationship owner or engagement owner"
    )

    source_reference: str = Field(
        default="",
        description="Related BRD, analysis, requirement, or governance reference"
    )

    status: str = Field(
        default="Active",
        description="Active, Planned, Monitoring, Inactive, or Closed"
    )

    notes: str = Field(
        default=""
    )


class StakeholderRegister(BaseModel):
    project_title: str = Field(
        description="Project name"
    )

    register_purpose: str = Field(
        description="Purpose of the Stakeholder Register"
    )

    total_stakeholders: int = Field(
        ge=0
    )

    high_influence_count: int = Field(
        ge=0
    )

    manage_closely_count: int = Field(
        ge=0
    )

    stakeholders: list[StakeholderItem] = Field(
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