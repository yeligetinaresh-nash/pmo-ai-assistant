from pydantic import BaseModel, Field


class Stakeholder(BaseModel):
    name: str = ""
    role: str = ""
    department: str = ""


class Requirement(BaseModel):
    requirement_id: str = ""
    description: str
    priority: str = ""


class Risk(BaseModel):
    description: str
    likelihood: str = ""
    impact: str = ""
    mitigation: str = ""


class BRDAnalysis(BaseModel):
    project_summary: str = Field(
        description="A concise summary of the project and business need."
    )

    objectives: list[str] = Field(default_factory=list)

    scope_in: list[str] = Field(default_factory=list)

    scope_out: list[str] = Field(default_factory=list)

    stakeholders: list[Stakeholder] = Field(default_factory=list)

    requirements: list[Requirement] = Field(default_factory=list)

    risks: list[Risk] = Field(default_factory=list)

    assumptions: list[str] = Field(default_factory=list)

    dependencies: list[str] = Field(default_factory=list)

    constraints: list[str] = Field(default_factory=list)

    acceptance_criteria: list[str] = Field(default_factory=list)