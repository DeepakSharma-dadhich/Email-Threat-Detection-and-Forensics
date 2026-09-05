from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.analysis_contract import (
    AnalysisJobStatus,
)


class GmailConnectionResponse(BaseModel):
    connected: bool
    email_address: str | None = None


class GmailMessageSummary(BaseModel):
    gmail_message_id: str
    gmail_thread_id: str | None
    label_ids: list[str]


class GmailMessageListResponse(BaseModel):
    count: int
    messages: list[GmailMessageSummary]


class GmailImportResponse(BaseModel):
    gmail_message_id: str
    email_id: UUID
    status: str


class GmailProcessResponse(BaseModel):
    gmail_message_id: str

    email_id: UUID
    analysis_id: UUID

    job_status: AnalysisJobStatus

    aggregate_score: int | float
    verdict: str
    recommended_action: str

    browser_isolation_recommended: bool

    analyzed_at: datetime

    status: str