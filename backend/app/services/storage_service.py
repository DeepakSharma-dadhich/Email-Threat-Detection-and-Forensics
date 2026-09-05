import hashlib
import re
import uuid
from pathlib import Path

from app.core.config import settings


_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


class StorageService:
    def __init__(self, root: Path | None = None):
        self.root = (root or settings.storage_root).resolve()

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def safe_filename(filename: str | None, fallback: str) -> str:
        if not filename:
            return fallback
        name = Path(filename).name
        sanitized = _SAFE_FILENAME_RE.sub("_", name).strip("._")
        return sanitized[:180] or fallback

    def save_raw_email(self, email_id: uuid.UUID, raw_bytes: bytes) -> str:
        key = Path("emails") / str(email_id) / "raw.eml"
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw_bytes)
        return key.as_posix()

    def save_attachment(
        self,
        email_id: uuid.UUID,
        attachment_id: uuid.UUID,
        filename: str | None,
        payload: bytes,
    ) -> str:
        safe_name = self.safe_filename(filename, "attachment.bin")
        key = Path("emails") / str(email_id) / "attachments" / f"{attachment_id}_{safe_name}"
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return key.as_posix()

    def resolve_key(self, storage_key: str) -> Path:
        candidate = (self.root / storage_key).resolve()
        candidate.relative_to(self.root)
        return candidate
