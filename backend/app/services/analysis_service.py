from uuid import UUID

from sqlalchemy.orm import Session

from app.analysis.orchestrator import AnalysisOrchestrator
from app.analysis.risk.engine import FinalRiskEngine
from app.models.analysis_record import AnalysisRecord
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.final_analysis import (
    AnalysisHistoryItem,
    FinalAnalysisResponse,
)
from app.services.email_lifecycle_service import EmailLifecycleService
from app.services.email_query_service import EmailQueryService


class AnalysisService:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db
        self.email_query_service = EmailQueryService(db)
        self.analysis_repository = AnalysisRepository(db)
        self.orchestrator = AnalysisOrchestrator()
        self.risk_engine = FinalRiskEngine()
        self.lifecycle_service = EmailLifecycleService(db)

    def analyze_email(
        self,
        email_id: UUID,
        user_id: UUID,
    ) -> FinalAnalysisResponse:

        email = self.email_query_service.get_for_user(
            email_id=email_id,
            user_id=user_id,
        )

        module_analysis = self.orchestrator.analyze(
            email
        )

        decision = self.risk_engine.evaluate(
            module_analysis
        )

        job_status_value = (
            module_analysis.job_status.value
            if hasattr(
                module_analysis.job_status,
                "value",
            )
            else str(
                module_analysis.job_status
            )
        )

        module_results_json = [
            result.model_dump(
                mode="json"
            )
            for result in module_analysis.module_results
        ]

        result_data = {
            "email_id": str(
                email_id
            ),
            "job_status": (
                job_status_value
            ),
            "module_results": (
                module_results_json
            ),
            "aggregate_score": (
                decision.aggregate_score
            ),
            "verdict": (
                decision.verdict
            ),
            "recommended_action": (
                decision.recommended_action
            ),
            "browser_isolation_recommended": (
                decision.browser_isolation_recommended
            ),
        }

        record = AnalysisRecord(
            email_id=email_id,
            job_status=(
                job_status_value
            ),
            aggregate_score=(
                decision.aggregate_score
            ),
            verdict=(
                decision.verdict
            ),
            recommended_action=(
                decision.recommended_action
            ),
            browser_isolation_recommended=(
                decision.browser_isolation_recommended
            ),
            module_results=(
                module_results_json
            ),
            result_data=(
                result_data
            ),
        )

        record = self.analysis_repository.create(
            record
        )

        self.lifecycle_service.apply_system_decision(
            email_id=email_id,
            analysis_id=record.analysis_id,
            recommended_action=(
                decision.recommended_action
            ),
        )

        return FinalAnalysisResponse(
            analysis_id=(
                record.analysis_id
            ),
            email_id=email_id,
            job_status=(
                module_analysis.job_status
            ),
            module_results=(
                module_analysis.module_results
            ),
            aggregate_score=(
                decision.aggregate_score
            ),
            verdict=(
                decision.verdict
            ),
            recommended_action=(
                decision.recommended_action
            ),
            browser_isolation_recommended=(
                decision.browser_isolation_recommended
            ),
            analyzed_at=(
                record.created_at
            ),
        )

    def get_history(
        self,
        email_id: UUID,
        user_id: UUID,
    ) -> list[
        AnalysisHistoryItem
    ]:

        self.email_query_service.get_for_user(
            email_id=email_id,
            user_id=user_id,
        )

        records = (
            self.analysis_repository
            .list_for_email(
                email_id
            )
        )

        return [
            AnalysisHistoryItem(
                analysis_id=(
                    record.analysis_id
                ),
                email_id=(
                    record.email_id
                ),
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
                created_at=(
                    record.created_at
                ),
            )
            for record in records
        ]