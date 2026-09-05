from sqlalchemy.orm import Session

from app.adapters.gmail import GmailSourceAdapter
from app.integrations.gmail_auth import GmailAuthClient
from app.models.email_record import EmailRecord
from app.services.email_ingestion_service import (
    EmailIngestionService,
)


class GmailImportService:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

        auth_client = GmailAuthClient()

        self.gmail_api = (
            auth_client.build_service()
        )

        self.ingestion_service = (
            EmailIngestionService(db)
        )

    def import_message(
        self,
        gmail_message_id: str,
    ) -> EmailRecord:
        adapter = GmailSourceAdapter(
            gmail_service=self.gmail_api,
            gmail_message_id=gmail_message_id,
        )

        return self.ingestion_service.ingest(
            adapter
        )