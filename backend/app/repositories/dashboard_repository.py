from sqlalchemy import (
    func,
    select,
)

from sqlalchemy.orm import Session

from app.models.analysis_record import AnalysisRecord
from app.models.email_record import EmailRecord


class DashboardRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def count_emails(
        self,
    ) -> int:

        statement = select(
            func.count(
                EmailRecord.id
            )
        )

        return int(
            self.db.scalar(
                statement
            )
            or 0
        )

    def count_analyses(
        self,
    ) -> int:

        statement = select(
            func.count(
                AnalysisRecord.analysis_id
            )
        )

        return int(
            self.db.scalar(
                statement
            )
            or 0
        )

    def average_risk_score(
        self,
    ) -> float:

        statement = select(
            func.avg(
                AnalysisRecord.aggregate_score
            )
        )

        value = self.db.scalar(
            statement
        )

        if value is None:
            return 0.0

        return round(
            float(value),
            2,
        )

    def count_browser_isolation_candidates(
        self,
    ) -> int:

        statement = (
            select(
                func.count(
                    AnalysisRecord.analysis_id
                )
            )
            .where(
                AnalysisRecord
                .browser_isolation_recommended
                .is_(True)
            )
        )

        return int(
            self.db.scalar(
                statement
            )
            or 0
        )

    def verdict_counts(
        self,
    ) -> dict[str, int]:

        statement = (
            select(
                AnalysisRecord.verdict,
                func.count(
                    AnalysisRecord.analysis_id
                ),
            )
            .group_by(
                AnalysisRecord.verdict
            )
        )

        rows = self.db.execute(
            statement
        ).all()

        return {
            verdict: int(count)
            for verdict, count in rows
            if verdict is not None
        }

    def recent_analyses(
        self,
        limit: int = 10,
    ):
        statement = (
            select(
                AnalysisRecord,
                EmailRecord.subject,
            )
            .join(
                EmailRecord,
                EmailRecord.id
                == AnalysisRecord.email_id,
            )
            .order_by(
                AnalysisRecord.created_at.desc()
            )
            .limit(
                limit
            )
        )

        return self.db.execute(
            statement
        ).all()