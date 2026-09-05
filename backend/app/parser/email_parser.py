from email import policy
from email.header import decode_header, make_header
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime

from app.core.exceptions import AppError
from app.domain.parsed_email import ParsedAttachment, ParsedEmail, ParsedMailbox


class EmailParser:
    def parse(self, raw_bytes: bytes) -> ParsedEmail:
        try:
            message = BytesParser(policy=policy.default).parsebytes(raw_bytes)
        except Exception as exc:
            raise AppError("The uploaded file could not be parsed as an email.", 422, "EMAIL_PARSE_FAILED") from exc

        warnings: list[str] = []
        headers = [{"name": str(name), "value": str(value)} for name, value in message.raw_items()]

        body_text_parts: list[str] = []
        body_html_parts: list[str] = []
        attachments: list[ParsedAttachment] = []

        for part in message.walk():
            if part.is_multipart():
                continue

            disposition = part.get_content_disposition()
            filename = self._decode_header_value(part.get_filename())
            content_type = part.get_content_type()
            payload = part.get_payload(decode=True) or b""

            is_attachment = disposition == "attachment" or filename is not None
            if is_attachment:
                attachments.append(
                    ParsedAttachment(
                        filename=filename,
                        content_type=content_type,
                        content_disposition=disposition,
                        content_id=part.get("Content-ID"),
                        payload=payload,
                    )
                )
                continue

            if content_type not in {"text/plain", "text/html"}:
                continue

            text = self._decode_text_part(part, payload, warnings)
            if not text:
                continue

            if content_type == "text/plain":
                body_text_parts.append(text)
            else:
                body_html_parts.append(text)


        return ParsedEmail(
            message_id=self._clean(message.get("Message-ID")),
            subject=self._decode_header_value(message.get("Subject")),
            from_address=self._first_mailbox(message.get_all("From", [])),
            reply_to=self._first_mailbox(message.get_all("Reply-To", [])),
            return_path=self._clean(message.get("Return-Path")),
            to=self._mailboxes(message.get_all("To", [])),
            cc=self._mailboxes(message.get_all("Cc", [])),
            bcc=self._mailboxes(message.get_all("Bcc", [])),
            received_at=self._parse_date(message.get("Date"), warnings),
            headers=headers,
            body_text="\n\n".join(body_text_parts).strip() or None,
            body_html="\n\n".join(body_html_parts).strip() or None,
            attachments=attachments,
            warnings=warnings,
        )

    @staticmethod
    def _clean(value) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _decode_header_value(value) -> str | None:
        if value is None:
            return None
        try:
            return str(make_header(decode_header(str(value)))).strip() or None
        except Exception:
            return str(value).strip() or None

    def _mailboxes(self, values: list[str]) -> list[ParsedMailbox]:
        result: list[ParsedMailbox] = []
        for display_name, address in getaddresses([str(v) for v in values]):
            address = address.strip()
            if not address:
                continue
            result.append(
                ParsedMailbox(
                    name=self._decode_header_value(display_name),
                    address=address,
                )
            )
        return result

    def _first_mailbox(self, values: list[str]) -> ParsedMailbox | None:
        parsed = self._mailboxes(values)
        return parsed[0] if parsed else None

    @staticmethod
    def _parse_date(value, warnings: list[str]):
        if not value:
            return None
        try:
            return parsedate_to_datetime(str(value))
        except Exception:
            warnings.append("Date header could not be parsed.")
            return None

    @staticmethod
    def _decode_text_part(part, payload: bytes, warnings: list[str]) -> str:
        charset = part.get_content_charset() or "utf-8"
        try:
            return payload.decode(charset, errors="replace")
        except LookupError:
            warnings.append(f"Unknown charset '{charset}'; UTF-8 fallback used.")
            return payload.decode("utf-8", errors="replace")
