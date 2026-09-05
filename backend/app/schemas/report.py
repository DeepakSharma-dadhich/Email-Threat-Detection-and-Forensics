from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.analysis_contract import (
    ModuleAnalysisResult,
)


class ReportEmailSummary(BaseModel):
    email_id: UUID

    subject: str | None = None

    source_type: str

    received_at: datetime | None = None


class ReportDecision(BaseModel):
    risk_score: int | None

    verdict: str | None

    recommended_action: str | None

    browser_isolation_recommended: bool


class ReportDataResponse(BaseModel):
    analysis_id: UUID

    email: ReportEmailSummary

    decision: ReportDecision

    modules: list[
        ModuleAnalysisResult
    ]

    analyzed_at: datetime