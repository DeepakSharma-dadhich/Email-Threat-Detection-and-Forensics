from uuid import UUID

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.email_record import (
    EmailRecord,
)

from app.repositories.analysis_repository import (
    AnalysisRepository,
)

from app.schemas.analysis_contract import (
    ModuleAnalysisResult,
)

from app.schemas.report import (
    ReportDataResponse,
    ReportDecision,
    ReportEmailSummary,
)


class ReportService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

        self.analysis_repository = (
            AnalysisRepository(
                db
            )
        )

    def get_report_data(
        self,
        analysis_id: UUID,
    ) -> ReportDataResponse:

        analysis = (
            self.analysis_repository
            .get_by_id(
                analysis_id
            )
        )

        if analysis is None:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found.",
            )

        email = self.db.get(
            EmailRecord,
            analysis.email_id,
        )

        if email is None:
            raise HTTPException(
                status_code=404,
                detail="Email not found.",
            )

        modules = [
            ModuleAnalysisResult
            .model_validate(
                module
            )
            for module
            in analysis.module_results
        ]

        return ReportDataResponse(
            analysis_id=(
                analysis.analysis_id
            ),

            email=ReportEmailSummary(
                email_id=email.id,
                subject=email.subject,
                source_type=(
                    email.source_type
                ),
                received_at=(
                    email.received_at
                ),
            ),

            decision=ReportDecision(
                risk_score=(
                    analysis.aggregate_score
                ),
                verdict=(
                    analysis.verdict
                ),
                recommended_action=(
                    analysis
                    .recommended_action
                ),
                browser_isolation_recommended=(
                    analysis
                    .browser_isolation_recommended
                ),
            ),

            modules=modules,

            analyzed_at=(
                analysis.created_at
            ),
        )