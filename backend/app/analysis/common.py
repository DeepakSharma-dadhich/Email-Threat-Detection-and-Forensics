import re
import uuid
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit

from app.schemas.analysis_contract import Finding, FindingSeverity
from app.schemas.email import CommonEmailObject


class _TextHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


def strip_html(html: str | None) -> str:
    if not html:
        return ""

    parser = _TextHTMLParser()

    try:
        parser.feed(html)
        return unescape(" ".join(parser.parts))

    except Exception:
        return re.sub(r"<[^>]+>", " ", html)


def header_values(
    email: CommonEmailObject,
    name: str,
) -> list[str]:

    target = name.lower()

    return [
        header.value
        for header in email.headers
        if header.name.lower() == target
    ]


def header_value(
    email: CommonEmailObject,
    name: str,
) -> str | None:

    values = header_values(email, name)

    return values[0] if values else None


def email_domain(address: str | None) -> str | None:

    if not address or "@" not in address:
        return None

    return (
        address
        .rsplit("@", 1)[1]
        .strip()
        .strip(">")
        .lower()
        or None
    )


def host_from_url(value: str) -> str | None:

    try:
        return (
            urlsplit(value).hostname or ""
        ).lower() or None

    except Exception:
        return None


def new_finding(
    title: str,
    category: str,
    severity: FindingSeverity,
    description: str,
    evidence: dict | None = None,
) -> Finding:

    return Finding(
        finding_id=str(uuid.uuid4()),
        title=title,
        category=category,
        severity=severity,
        description=description,
        evidence=evidence or {},
    )