from sqlalchemy.orm import Session

from app.schemas.gmail import (
    GmailProcessResponse,
)

from app.services.analysis_service import (
    AnalysisService,
)

from app.services.gmail_import_service import (
    GmailImportService,
)


class GmailProcessingService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

        self.gmail_import_service = (
            GmailImportService(db)
        )

        self.analysis_service = (
            AnalysisService(db)
        )

    def process_message(
        self,
        gmail_message_id: str,
    ) -> GmailProcessResponse:

        email_record = (
            self.gmail_import_service
            .import_message(
                gmail_message_id
            )
        )

        analysis = (
            self.analysis_service
            .analyze_email(
                email_record.id
            )
        )

        return GmailProcessResponse(
            gmail_message_id=(
                gmail_message_id
            ),
            email_id=email_record.id,
            analysis_id=(
                analysis.analysis_id
            ),
            job_status=(
                analysis.job_status
            ),
            aggregate_score=(
                analysis.aggregate_score
            ),
            verdict=analysis.verdict,
            recommended_action=(
                analysis.recommended_action
            ),
            browser_isolation_recommended=(
                analysis
                .browser_isolation_recommended
            ),
            analyzed_at=(
                analysis.analyzed_at
            ),
            status="processed",
        )