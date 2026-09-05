from app.adapters.base import EmailSourceAdapter
from app.core.exceptions import AppError
from app.domain.raw_email import RawEmailEnvelope


class EmlFileAdapter(EmailSourceAdapter):
    def __init__(self, raw_bytes: bytes, filename: str | None):
        self._raw_bytes = raw_bytes
        self._filename = filename

    def load(self) -> RawEmailEnvelope:
        if not self._raw_bytes:
            raise AppError("Uploaded .eml file is empty.", 400, "EMPTY_EMAIL")

        if self._filename and not self._filename.lower().endswith(".eml"):
            raise AppError("Only .eml files are accepted in the Batch 1 Test Lab.", 415, "UNSUPPORTED_FILE")

        return RawEmailEnvelope(
            raw_bytes=self._raw_bytes,
            source_type="eml",
            original_filename=self._filename,
        )
