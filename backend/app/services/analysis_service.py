from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.analysis.orchestrator import AnalysisOrchestrator
from app.analysis.risk.engine import FinalRiskEngine

from app.models.analysis_record import AnalysisRecord

from app.repositories.analysis_repository import AnalysisRepository

from app.schemas.analysis_contract import (
    AnalysisResult,
)

from app.schemas.final_analysis import (
    AnalysisHistoryItem,
    FinalAnalysisResponse,
)

from app.services.email_lifecycle_service import (
    EmailLifecycleService,
)

from app.services.email_query_service import (
    EmailQueryService,
)


class AnalysisService:

    def __init__(
        self,
        db: Session,
        orchestrator: AnalysisOrchestrator | None = None,
        risk_engine: FinalRiskEngine | None = None,
    ):
        self.db = db

        self.email_query_service = EmailQueryService(
            db
        )

        self.analysis_repository = AnalysisRepository(
            db
        )

        self.lifecycle_service = EmailLifecycleService(
            db
        )

        self.orchestrator = (
            orchestrator
            or AnalysisOrchestrator()
        )

        self.risk_engine = (
            risk_engine
            or FinalRiskEngine()
        )

    def analyze_email(
        self,
        email_id: UUID,
    ) -> FinalAnalysisResponse:

        email = self.email_query_service.get(
            email_id
        )

        module_analysis = self.orchestrator.analyze(
            email
        )

        decision = self.risk_engine.evaluate(
            module_analysis
        )

        final_result = AnalysisResult(
            email_id=email_id,
            job_status=module_analysis.job_status,
            module_results=module_analysis.module_results,
            aggregate_score=decision.aggregate_score,
            verdict=decision.verdict,
            recommended_action=decision.recommended_action,
        )

        analyzed_at = datetime.now(
            timezone.utc
        )

        record = AnalysisRecord(
            email_id=email_id,
            job_status=final_result.job_status.value,
            aggregate_score=final_result.aggregate_score,
            verdict=final_result.verdict,
            recommended_action=(
                final_result.recommended_action
            ),
            browser_isolation_recommended=(
                decision.browser_isolation_recommended
            ),
            module_results=[
                module.model_dump(
                    mode="json"
                )
                for module in final_result.module_results
            ],
            result_data=final_result.model_dump(
                mode="json"
            ),
            created_at=analyzed_at,
        )

        record = self.analysis_repository.create(
            record
        )

        self.lifecycle_service.apply_system_decision(
            email_id=email_id,
            analysis_id=record.analysis_id,
            recommended_action=(
                final_result.recommended_action
            ),
        )

        return FinalAnalysisResponse(
            **final_result.model_dump(),
            analysis_id=record.analysis_id,
            browser_isolation_recommended=(
                decision.browser_isolation_recommended
            ),
            analyzed_at=record.created_at,
        )

    def get_history(
        self,
        email_id: UUID,
    ) -> list[AnalysisHistoryItem]:

        self.email_query_service.get(
            email_id
        )

        records = (
            self.analysis_repository.list_for_email(
                email_id
            )
        )

        return [
            AnalysisHistoryItem(
                analysis_id=record.analysis_id,
                email_id=record.email_id,
                aggregate_score=record.aggregate_score,
                verdict=record.verdict,
                recommended_action=(
                    record.recommended_action
                ),
                browser_isolation_recommended=(
                    record.browser_isolation_recommended
                ),
                created_at=record.created_at,
            )
            for record in records
        ]