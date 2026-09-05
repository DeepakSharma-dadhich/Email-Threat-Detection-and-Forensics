from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RiskDistribution(BaseModel):
    safe: int = 0
    low_risk: int = 0
    suspicious: int = 0
    high_risk: int = 0
    malicious: int = 0


class DashboardSummary(BaseModel):
    total_emails: int
    total_analyses: int

    average_risk_score: float

    browser_isolation_candidates: int

    risk_distribution: RiskDistribution


class RecentAnalysisItem(BaseModel):
    analysis_id: UUID
    email_id: UUID

    subject: str | None = None

    aggregate_score: int | None

    verdict: str | None

    recommended_action: str | None

    browser_isolation_recommended: bool

    analyzed_at: datetime