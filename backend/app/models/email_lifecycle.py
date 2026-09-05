import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EmailLifecycleState(Base):
    __tablename__ = "email_lifecycle_states"

    __table_args__ = (
        UniqueConstraint(
            "email_id",
            name="uq_email_lifecycle_states_email_id",
        ),
    )

    state_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "email_records.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    latest_analysis_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "analysis_records.analysis_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    updated_by: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="system",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class EmailActionHistory(Base):
    __tablename__ = "email_action_history"

    action_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "email_records.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    analysis_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "analysis_records.analysis_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    previous_status: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    new_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    actor_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )