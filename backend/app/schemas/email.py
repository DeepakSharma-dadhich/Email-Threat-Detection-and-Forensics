from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HeaderItem(BaseModel):
    name: str
    value: str


class Mailbox(BaseModel):
    name: str | None = None
    address: str


class AttachmentInfo(BaseModel):
    attachment_id: UUID
    filename: str | None = None
    content_type: str
    content_disposition: str | None = None
    content_id: str | None = None
    size_bytes: int
    sha256: str
    storage_key: str


class SourceInfo(BaseModel):
    type: str
    source_message_id: str | None = None
    original_filename: str | None = None


class RawArtifactInfo(BaseModel):
    sha256: str
    size_bytes: int
    storage_key: str


class CommonEmailObject(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email_id: UUID
    source: SourceInfo
    message_id: str | None = None
    subject: str | None = None
    from_address: Mailbox | None = None
    reply_to: Mailbox | None = None
    return_path: str | None = None
    to: list[Mailbox] = Field(default_factory=list)
    cc: list[Mailbox] = Field(default_factory=list)
    bcc: list[Mailbox] = Field(default_factory=list)
    received_at: datetime | None = None
    headers: list[HeaderItem] = Field(default_factory=list)
    body_text: str | None = None
    body_html: str | None = None
    attachments: list[AttachmentInfo] = Field(default_factory=list)
    raw_artifact: RawArtifactInfo
    parse_warnings: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class EmailListItem(BaseModel):
    email_id: UUID
    subject: str | None = None
    from_address: str | None = None
    received_at: datetime | None = None
    source_type: str
    attachment_count: int
    created_at: datetime


class EmailListResponse(BaseModel):
    items: list[EmailListItem]
    total: int
    limit: int
    offset: int
