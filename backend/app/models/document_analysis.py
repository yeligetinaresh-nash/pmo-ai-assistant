from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class DocumentAnalysis(Base):
    __tablename__ = "document_analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey(
            "uploaded_documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    analysis_type: Mapped[str] = mapped_column(
        String(50),
        default="brd_analysis",
        nullable=False,
    )

    result_json: Mapped[dict[str, Any]] = mapped_column(
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

    document = relationship(
        "UploadedDocument",
        back_populates="analyses",
    )
    artifacts = relationship(
    "ProjectArtifact",
    back_populates="document_analysis",
    cascade="all, delete-orphan",
)