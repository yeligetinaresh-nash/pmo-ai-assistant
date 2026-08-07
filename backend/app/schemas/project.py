from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str
    description: str | None = None
    status: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    status: str

    model_config = ConfigDict(from_attributes=True)