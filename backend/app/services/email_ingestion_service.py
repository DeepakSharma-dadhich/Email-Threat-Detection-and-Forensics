import uuid

from sqlalchemy.orm import Session

from app.adapters.base import EmailSourceAdapter
from app.core.config import settings
from app.core.exceptions import AppError
from app.models.email_record import EmailRecord
from app.parser.email_parser import EmailParser
from app.repositories.email_repository import EmailRepository
from app.services.storage_service import StorageService


class EmailIngestionService:
    def __init__(
        self,
        db: Session,
        parser: EmailParser | None = None,
        storage: StorageService | None = None,
    ):
        self.repository = EmailRepository(db)
        self.parser = parser or EmailParser()
        self.storage = storage or StorageService()

    def ingest(self, adapter: EmailSourceAdapter) -> EmailRecord:
        envelope = adapter.load()
        raw_bytes = envelope.raw_bytes

        if len(raw_bytes) > settings.max_email_size_bytes:
            raise AppError(
                f"Email exceeds the configured {settings.max_email_size_mb} MB limit.",
                413,
                "EMAIL_TOO_LARGE",
            )

        raw_sha256 = self.storage.sha256(raw_bytes)

        parsed = self.parser.parse(raw_bytes)
        email_id = uuid.uuid4()

        raw_path = self.storage.save_raw_email(email_id, raw_bytes)
        attachment_infos: list[dict] = []

        for attachment in parsed.attachments:
            attachment_id = uuid.uuid4()
            sha256 = self.storage.sha256(attachment.payload)
            storage_key = self.storage.save_attachment(
                email_id=email_id,
                attachment_id=attachment_id,
                filename=attachment.filename,
                payload=attachment.payload,
            )
            attachment_infos.append(
                {
                    "attachment_id": str(attachment_id),
                    "filename": attachment.filename,
                    "content_type": attachment.content_type,
                    "content_disposition": attachment.content_disposition,
                    "content_id": attachment.content_id,
                    "size_bytes": len(attachment.payload),
                    "sha256": sha256,
                    "storage_key": storage_key,
                }
            )

        record = EmailRecord(
            id=email_id,
            source_type=envelope.source_type,
            source_message_id=envelope.source_message_id,
            original_filename=envelope.original_filename,
            message_id=parsed.message_id,
            subject=parsed.subject,
            from_address=self._mailbox_to_json(parsed.from_address),
            reply_to=self._mailbox_to_json(parsed.reply_to),
            return_path=parsed.return_path,
            to_addresses=[self._mailbox_to_json(m) for m in parsed.to],
            cc_addresses=[self._mailbox_to_json(m) for m in parsed.cc],
            bcc_addresses=[self._mailbox_to_json(m) for m in parsed.bcc],
            received_at=parsed.received_at,
            headers=parsed.headers,
            body_text=parsed.body_text,
            body_html=parsed.body_html,
            attachments=attachment_infos,
            raw_sha256=raw_sha256,
            raw_storage_key=raw_path,
            raw_size_bytes=len(raw_bytes),
            parse_warnings=parsed.warnings,
        )
        return self.repository.create(record)

    @staticmethod
    def _mailbox_to_json(mailbox):
        if mailbox is None:
            return None
        return {"name": mailbox.name, "address": mailbox.address}
