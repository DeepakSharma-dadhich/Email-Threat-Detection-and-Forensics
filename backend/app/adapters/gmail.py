import base64

from app.adapters.base import EmailSourceAdapter
from app.domain.raw_email import RawEmailEnvelope


class GmailSourceAdapter(EmailSourceAdapter):
    def __init__(
        self,
        gmail_service,
        gmail_message_id: str,
    ):
        self.service = gmail_service
        self.gmail_message_id = gmail_message_id

    def load(self) -> RawEmailEnvelope:
        response = (
            self.service
            .users()
            .messages()
            .get(
                userId="me",
                id=self.gmail_message_id,
                format="raw",
            )
            .execute()
        )

        encoded_raw = response.get("raw")

        if not encoded_raw:
            raise ValueError(
                "Gmail API returned no raw message content."
            )

        raw_bytes = base64.urlsafe_b64decode(
            encoded_raw.encode("utf-8")
        )

        return RawEmailEnvelope(
            source_type="gmail",
            source_message_id=response["id"],
            original_filename=None,
            raw_bytes=raw_bytes,
        )