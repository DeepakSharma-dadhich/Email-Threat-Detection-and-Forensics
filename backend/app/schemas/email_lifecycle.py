from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class EmailOperationalStatus(str, Enum):
    INBOX = "inbox"
    QUARANTINE = "quarantine"
    BLOCKED = "blocked"
    REVIEW = "review"


class LifecycleAction(str, Enum):
    SYSTEM_ALLOW = "system_allow"
    SYSTEM_MONITOR = "system_monitor"
    SYSTEM_REVIEW = "system_review"
    SYSTEM_QUARANTINE = "system_quarantine"
    SYSTEM_BLOCK = "system_block"

    MANUAL_ALLOW = "manual_allow"
    MANUAL_QUARANTINE = "manual_quarantine"
    MANUAL_BLOCK = "manual_block"
    MANUAL_REVIEW = "manual_review"

    RELEASE = "release"
    RESTORE = "restore"


class ManualActionRequest(BaseModel):
    reason: str | None = Field(
        default=None,
        max_length=1000,
    )


class EmailLifecycleResponse(BaseModel):
    email_id: UUID
    status: EmailOperationalStatus

    latest_analysis_id: UUID | None = None

    updated_by: str

    updated_at: datetime


class EmailActionHistoryItem(BaseModel):
    action_id: UUID

    email_id: UUID

    analysis_id: UUID | None

    action: LifecycleAction

    previous_status: EmailOperationalStatus | None

    new_status: EmailOperationalStatus

    actor_type: str

    reason: str | None

    created_at: datetime


class LifecycleSummary(BaseModel):
    inbox: int = 0
    quarantine: int = 0
    blocked: int = 0
    review: int = 0

    total: int = 0