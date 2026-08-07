from pydantic import BaseModel, Field, field_validator


class Milestone(BaseModel):
    name: str
    description: str = ""
    target_timeline: str = ""


class CharterStakeholder(BaseModel):
    name: str = ""
    role: str = ""
    responsibility: str = ""


class ProjectCharter(BaseModel):
    project_title: str

    project_purpose: str = Field(
        description="The business reason and purpose for undertaking the project."
    )

    project_summary: str = Field(
        description="A concise overview of what the project will deliver."
    )

    business_objectives: list[str] = Field(default_factory=list)

    in_scope: list[str] = Field(default_factory=list)

    out_of_scope: list[str] = Field(default_factory=list)

    key_deliverables: list[str] = Field(default_factory=list)

    stakeholders: list[CharterStakeholder] = Field(default_factory=list)

    milestones: list[Milestone] = Field(default_factory=list)

    assumptions: list[str] = Field(default_factory=list)

    constraints: list[str] = Field(default_factory=list)

    dependencies: list[str] = Field(default_factory=list)

    high_level_risks: list[str] = Field(default_factory=list)

    success_criteria: list[str] = Field(default_factory=list)

    project_manager: str = ""

    sponsor: str = ""

    approval_status: str = "Draft"

    @field_validator("approval_status", mode="before")
    @classmethod
    def set_default_approval_status(cls, value):
        if value is None:
            return "Draft"

        cleaned_value = str(value).strip()

        if not cleaned_value:
            return "Draft"

        return cleaned_value