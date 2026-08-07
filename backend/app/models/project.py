from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)

    description = Column(String(1000))

    status = Column(String(50), default="Draft")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    documents = relationship(
        "UploadedDocument",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    artifacts = relationship(
    "ProjectArtifact",
    back_populates="project",
    cascade="all, delete-orphan",
)