import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
    UUID,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "email_records.email_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    job_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    aggregate_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    verdict: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    recommended_action: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    browser_isolation_recommended: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    module_results: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    result_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc
        ),
    )