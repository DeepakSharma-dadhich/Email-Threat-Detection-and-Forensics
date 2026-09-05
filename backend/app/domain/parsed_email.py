from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ParsedMailbox:
    name: str | None
    address: str


@dataclass(slots=True)
class ParsedAttachment:
    filename: str | None
    content_type: str
    content_disposition: str | None
    content_id: str | None
    payload: bytes


@dataclass(slots=True)
class ParsedEmail:
    message_id: str | None
    subject: str | None
    from_address: ParsedMailbox | None
    reply_to: ParsedMailbox | None
    return_path: str | None
    to: list[ParsedMailbox] = field(default_factory=list)
    cc: list[ParsedMailbox] = field(default_factory=list)
    bcc: list[ParsedMailbox] = field(default_factory=list)
    received_at: datetime | None = None
    headers: list[dict[str, str]] = field(default_factory=list)
    body_text: str | None = None
    body_html: str | None = None
    attachments: list[ParsedAttachment] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
