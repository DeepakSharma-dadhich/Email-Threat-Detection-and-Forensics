import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EmailRecord(Base):
    __tablename__ = "email_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    source_message_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_filename: Mapped[str | None] = mapped_column(Text, nullable=True)

    message_id: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    from_address: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reply_to: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    return_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    to_addresses: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    cc_addresses: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    bcc_addresses: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    headers: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachments: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    raw_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    raw_storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    raw_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    parse_warnings: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )
