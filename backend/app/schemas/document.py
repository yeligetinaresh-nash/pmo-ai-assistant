from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    file_name: str
    original_name: str
    file_type: str
    file_size: int
    storage_path: str
    uploaded_at: datetime