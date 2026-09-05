import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.repositories.email_repository import (
    EmailRepository,
)
from app.schemas.email import (
    AttachmentInfo,
    CommonEmailObject,
    EmailListItem,
    EmailListResponse,
    HeaderItem,
    Mailbox,
    RawArtifactInfo,
    SourceInfo,
)


class EmailQueryService:
    def __init__(
        self,
        db: Session,
    ):
        self.repository = EmailRepository(
            db
        )

    def get(
        self,
        email_id: uuid.UUID,
    ) -> CommonEmailObject:
        record = self.repository.get(
            email_id
        )

        if record is None:
            raise AppError(
                "Email not found.",
                404,
                "EMAIL_NOT_FOUND",
            )

        return self._to_common_email(
            record
        )

    def get_for_user(
        self,
        email_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> CommonEmailObject:
        record = (
            self.repository.get_for_user(
                email_id=email_id,
                user_id=user_id,
            )
        )

        if record is None:
            raise AppError(
                "Email not found.",
                404,
                "EMAIL_NOT_FOUND",
            )

        return self._to_common_email(
            record
        )

    def list(
        self,
        limit: int,
        offset: int,
    ) -> EmailListResponse:
        records, total = (
            self.repository.list(
                limit,
                offset,
            )
        )

        return self._to_list_response(
            records=records,
            total=total,
            limit=limit,
            offset=offset,
        )

    def list_for_user(
        self,
        user_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> EmailListResponse:
        records, total = (
            self.repository.list_for_user(
                user_id=user_id,
                limit=limit,
                offset=offset,
            )
        )

        return self._to_list_response(
            records=records,
            total=total,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def _to_list_response(
        records,
        total: int,
        limit: int,
        offset: int,
    ) -> EmailListResponse:
        items = [
            EmailListItem(
                email_id=r.id,
                subject=r.subject,
                from_address=(
                    r.from_address
                    or {}
                ).get(
                    "address"
                ),
                received_at=r.received_at,
                source_type=r.source_type,
                attachment_count=len(
                    r.attachments
                    or []
                ),
                created_at=r.created_at,
            )
            for r in records
        ]

        return EmailListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def _mailbox(
        value: dict | None,
    ) -> Mailbox | None:
        return (
            Mailbox(**value)
            if value
            else None
        )

    def _to_common_email(
        self,
        record,
    ) -> CommonEmailObject:
        return CommonEmailObject(
            email_id=record.id,
            source=SourceInfo(
                type=record.source_type,
                source_message_id=(
                    record.source_message_id
                ),
                original_filename=(
                    record.original_filename
                ),
            ),
            message_id=record.message_id,
            subject=record.subject,
            from_address=self._mailbox(
                record.from_address
            ),
            reply_to=self._mailbox(
                record.reply_to
            ),
            return_path=record.return_path,
            to=[
                Mailbox(**item)
                for item
                in record.to_addresses
            ],
            cc=[
                Mailbox(**item)
                for item
                in record.cc_addresses
            ],
            bcc=[
                Mailbox(**item)
                for item
                in record.bcc_addresses
            ],
            received_at=record.received_at,
            headers=[
                HeaderItem(**item)
                for item
                in record.headers
            ],
            body_text=record.body_text,
            body_html=record.body_html,
            attachments=[
                AttachmentInfo(**item)
                for item
                in record.attachments
            ],
            raw_artifact=RawArtifactInfo(
                sha256=record.raw_sha256,
                size_bytes=(
                    record.raw_size_bytes
                ),
                storage_key=(
                    record.raw_storage_key
                ),
            ),
            parse_warnings=(
                record.parse_warnings
            ),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )