from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ProjectArtifact(Base):
    __tablename__ = "project_artifacts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    document_analysis_id: Mapped[int] = mapped_column(
        ForeignKey(
            "document_analyses.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    artifact_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="completed",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    project = relationship(
        "Project",
        back_populates="artifacts",
    )

    document_analysis = relationship(
        "DocumentAnalysis",
        back_populates="artifacts",
    )