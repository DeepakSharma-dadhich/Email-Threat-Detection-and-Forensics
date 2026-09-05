from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import (
    DashboardRepository,
)

from app.schemas.dashboard import (
    DashboardSummary,
    RecentAnalysisItem,
    RiskDistribution,
)


class DashboardService:

    def __init__(
        self,
        db: Session,
    ):
        self.repository = (
            DashboardRepository(
                db
            )
        )

    def get_summary(
        self,
    ) -> DashboardSummary:

        verdict_counts = (
            self.repository
            .verdict_counts()
        )

        distribution = RiskDistribution(
            safe=verdict_counts.get(
                "safe",
                0,
            ),
            low_risk=verdict_counts.get(
                "low_risk",
                0,
            ),
            suspicious=verdict_counts.get(
                "suspicious",
                0,
            ),
            high_risk=verdict_counts.get(
                "high_risk",
                0,
            ),
            malicious=verdict_counts.get(
                "malicious",
                0,
            ),
        )

        return DashboardSummary(
            total_emails=(
                self.repository
                .count_emails()
            ),
            total_analyses=(
                self.repository
                .count_analyses()
            ),
            average_risk_score=(
                self.repository
                .average_risk_score()
            ),
            browser_isolation_candidates=(
                self.repository
                .count_browser_isolation_candidates()
            ),
            risk_distribution=distribution,
        )

    def get_recent(
        self,
        limit: int = 10,
    ) -> list[RecentAnalysisItem]:

        rows = (
            self.repository
            .recent_analyses(
                limit=limit
            )
        )

        return [
            RecentAnalysisItem(
                analysis_id=(
                    record.analysis_id
                ),
                email_id=(
                    record.email_id
                ),
                subject=subject,
                aggregate_score=(
                    record.aggregate_score
                ),
                verdict=(
                    record.verdict
                ),
                recommended_action=(
                    record.recommended_action
                ),
                browser_isolation_recommended=(
                    record
                    .browser_isolation_recommended
                ),
                analyzed_at=(
                    record.created_at
                ),
            )
            for record, subject in rows
        ]