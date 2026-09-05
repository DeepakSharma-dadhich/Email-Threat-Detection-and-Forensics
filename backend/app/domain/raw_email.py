from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RawEmailEnvelope:
    raw_bytes: bytes
    source_type: str
    source_message_id: str | None = None
    original_filename: str | None = None
