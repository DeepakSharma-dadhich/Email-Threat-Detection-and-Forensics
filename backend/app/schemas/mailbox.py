from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class MailboxLatestAnalysis(BaseModel):
    analysis_id: UUID | None = None
    risk_score: int | None = None
    verdict: str | None = None
    recommended_action: str | None = None
    analyzed_at: datetime | None = None


class MailboxEmailItem(BaseModel):
    email_id: UUID
    subject: str | None = None
    from_address: dict[str, Any] | None = None
    received_at: datetime | None = None
    source_type: str

    status: str

    has_attachments: bool
    attachment_count: int = 0
    url_count: int = 0

    latest_analysis: MailboxLatestAnalysis | None = None


class MailboxListResponse(BaseModel):
    status: str
    total: int
    limit: int
    offset: int
    items: list[MailboxEmailItem] = Field(
        default_factory=list
    )


class InvestigationDecision(BaseModel):
    analysis_id: UUID | None = None
    risk_score: int | None = None
    verdict: str | None = None
    recommended_action: str | None = None
    browser_isolation_recommended: bool = False
    analyzed_at: datetime | None = None


class InvestigationLifecycle(BaseModel):
    status: str
    latest_analysis_id: UUID | None = None
    updated_by: str | None = None
    updated_at: datetime | None = None


class InvestigationActionHistoryItem(BaseModel):
    action_id: UUID
    analysis_id: UUID | None = None
    action: str
    previous_status: str | None = None
    new_status: str
    actor_type: str
    reason: str | None = None
    created_at: datetime


class InvestigationAnalysisHistoryItem(BaseModel):
    analysis_id: UUID
    risk_score: int
    verdict: str
    recommended_action: str
    browser_isolation_recommended: bool
    created_at: datetime


class EmailInvestigationResponse(BaseModel):
    email_id: UUID
    source_type: str
    source_message_id: str | None = None

    message_id: str | None = None
    subject: str | None = None

    from_address: dict[str, Any] | None = None
    reply_to: dict[str, Any] | None = None
    return_path: str | None = None

    to_addresses: list[dict[str, Any]] = Field(
        default_factory=list
    )

    cc_addresses: list[dict[str, Any]] = Field(
        default_factory=list
    )

    bcc_addresses: list[dict[str, Any]] = Field(
        default_factory=list
    )

    received_at: datetime | None = None

    body_text: str | None = None
    body_html: str | None = None

    attachments: list[dict[str, Any]] = Field(
        default_factory=list
    )

    parse_warnings: list[Any] = Field(
        default_factory=list
    )

    lifecycle: InvestigationLifecycle

    decision: InvestigationDecision | None = None

    modules: list[dict[str, Any]] = Field(
        default_factory=list
    )

    analysis_history: list[
        InvestigationAnalysisHistoryItem
    ] = Field(
        default_factory=list
    )

    action_history: list[
        InvestigationActionHistoryItem
    ] = Field(
        default_factory=list
    )