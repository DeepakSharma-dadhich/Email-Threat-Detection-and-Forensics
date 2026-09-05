from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.analysis_contract import (
    AnalysisResult,
)


class FinalAnalysisResponse(
    AnalysisResult
):
    analysis_id: UUID

    browser_isolation_recommended: bool = False

    analyzed_at: datetime


class AnalysisHistoryItem(BaseModel):
    analysis_id: UUID

    email_id: UUID

    aggregate_score: int | None

    verdict: str | None

    recommended_action: str | None

    browser_isolation_recommended: bool

    created_at: datetime