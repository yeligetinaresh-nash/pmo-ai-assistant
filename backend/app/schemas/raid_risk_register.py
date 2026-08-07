from pydantic import BaseModel, Field


class RAIDItem(BaseModel):
    item_id: str = Field(
        description="Unique RAID identifier such as R-001, A-001, I-001, or D-001"
    )

    category: str = Field(
        description="Risk, Assumption, Issue, or Dependency"
    )

    title: str = Field(
        description="Short title of the RAID item"
    )

    description: str = Field(
        description="Detailed description of the item"
    )

    status: str = Field(
        default="Open",
        description=(
            "Open, In Progress, Monitoring, Resolved, "
            "Accepted, Closed, or Planned"
        ),
    )

    priority: str = Field(
        default="Medium",
        description="Critical, High, Medium, or Low"
    )

    owner: str = Field(
        default="",
        description="Person or role responsible for the item"
    )

    source_reference: str = Field(
        default="",
        description="Related BRD, analysis, requirement, or WBS reference"
    )

    response_or_action: str = Field(
        default="",
        description="Mitigation, action, validation, or dependency management plan"
    )

    due_date: str = Field(
        default="",
        description="Target date in YYYY-MM-DD format when supported"
    )

    dependencies: list[str] = Field(
        default_factory=list,
        description="Related requirement, risk, issue, assumption, or dependency IDs"
    )

    notes: str = Field(
        default=""
    )


class RiskRegisterItem(BaseModel):
    risk_id: str = Field(
        description="Unique risk identifier such as R-001"
    )

    risk_title: str = Field(
        description="Short risk title"
    )

    risk_description: str = Field(
        description="Detailed risk statement"
    )

    category: str = Field(
        default="Project",
        description=(
            "Project, Technical, Security, Data, Delivery, "
            "Operational, Financial, Vendor, Compliance, or Other"
        ),
    )

    probability: str = Field(
        default="Medium",
        description="High, Medium, or Low"
    )

    impact: str = Field(
        default="Medium",
        description="Critical, High, Medium, or Low"
    )

    risk_score: int = Field(
        default=1,
        ge=1,
        le=25,
        description="Calculated or assessed risk score from 1 to 25"
    )

    priority: str = Field(
        default="Medium",
        description="Critical, High, Medium, or Low"
    )

    status: str = Field(
        default="Open",
        description=(
            "Open, In Progress, Monitoring, Accepted, "
            "Mitigated, Closed, or Realized"
        ),
    )

    owner: str = Field(
        default="",
        description="Risk owner"
    )

    mitigation_plan: str = Field(
        default="",
        description="Preventive mitigation actions"
    )

    contingency_plan: str = Field(
        default="",
        description="Fallback plan if the risk occurs"
    )

    trigger: str = Field(
        default="",
        description="Early warning condition or event"
    )

    source_reference: str = Field(
        default="",
        description="Related BRD, requirement, assumption, dependency, or WBS reference"
    )

    target_date: str = Field(
        default="",
        description="Target mitigation date in YYYY-MM-DD format when supported"
    )

    notes: str = Field(
        default=""
    )


class RAIDAndRiskRegister(BaseModel):
    project_title: str = Field(
        description="Project name"
    )

    register_purpose: str = Field(
        description="Purpose of the RAID Log and Risk Register"
    )

    total_raid_items: int = Field(
        ge=0
    )

    total_risks: int = Field(
        ge=0
    )

    open_risk_count: int = Field(
        ge=0
    )

    high_priority_risk_count: int = Field(
        ge=0
    )

    raid_items: list[RAIDItem] = Field(
        default_factory=list
    )

    risk_register: list[RiskRegisterItem] = Field(
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