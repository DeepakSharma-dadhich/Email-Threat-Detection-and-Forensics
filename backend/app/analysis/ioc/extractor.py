import ipaddress
import re
import html
from html.parser import HTMLParser

from urllib.parse import urlsplit

from app.analysis.common import (
    new_finding,
)

from app.schemas.analysis_contract import (
    FindingSeverity,
    ModuleAnalysisResult,
    ModuleStatus,
)

from app.schemas.email import (
    CommonEmailObject,
)


URL_RE = re.compile(
    r"\bhttps?://[^\s<>'\"\])}]+",
    re.I,
)


EMAIL_RE = re.compile(
    r"\b[A-Z0-9._%+-]+@"
    r"[A-Z0-9.-]+\."
    r"[A-Z]{2,63}\b",
    re.I,
)


IP_RE = re.compile(
    r"(?<![\w:])"
    r"(?:\d{1,3}\.){3}"
    r"\d{1,3}"
    r"(?![\w:])"
)


class _LinkParser(HTMLParser):

    def __init__(self):

        super().__init__()

        self.urls: list[str] = []

    def handle_starttag(
        self,
        tag,
        attrs,
    ):

        attr_map = dict(attrs)

        for key in (
            "href",
            "src",
            "action",
        ):

            value = attr_map.get(
                key
            )

            if (
                isinstance(
                    value,
                    str,
                )
                and value.lower().startswith(
                    (
                        "http://",
                        "https://",
                    )
                )
            ):

                self.urls.append(
                    value
                )


class IOCExtractor:

    module_name = "ioc_extraction"

    def analyze(
        self,
        email: CommonEmailObject,
    ) -> ModuleAnalysisResult:

        # -----------------------------------------
        # Build IOC search surface
        # -----------------------------------------

        text = "\n".join(
            [
                email.subject or "",
                email.body_text or "",
                email.body_html or "",
                *[
                    header.value
                    for header
                    in email.headers
                ],
            ]
        )

                # -----------------------------------------
        # URLs
        # -----------------------------------------

        raw_urls = set(
            URL_RE.findall(
                text
            )
        )

        # Normalize HTML entities such as:
        #
        # &amp;  -> &
        #
        # This prevents the same URL from being
        # treated as two different indicators.

        urls = {
            html.unescape(
                url
            ).strip()
            for url in raw_urls
        }

        # Extract HTML href/src/action URLs

        if email.body_html:

            parser = _LinkParser()

            try:
                parser.feed(
                    email.body_html
                )

                for url in parser.urls:

                    normalized_url = (
                        html.unescape(
                            url
                        )
                        .strip()
                    )

                    urls.add(
                        normalized_url
                    )

            except Exception:
                pass

        # Extract HTML href/src/action URLs

        if email.body_html:

            parser = _LinkParser()

            try:

                parser.feed(
                    email.body_html
                )

                urls.update(
                    parser.urls
                )

            except Exception:

                pass

        # -----------------------------------------
        # Email addresses
        # -----------------------------------------

        email_addresses = {
            match.lower()
            for match
            in EMAIL_RE.findall(
                text
            )
        }

        mailboxes = [

            email.from_address,

            email.reply_to,

            *email.to,

            *email.cc,

            *email.bcc,
        ]

        for mailbox in mailboxes:

            if mailbox:

                email_addresses.add(
                    mailbox.address.lower()
                )

        # -----------------------------------------
        # IP addresses
        # -----------------------------------------

        ips = set()

        for candidate in (
            IP_RE.findall(text)
        ):

            try:

                ips.add(
                    str(
                        ipaddress.ip_address(
                            candidate
                        )
                    )
                )

            except ValueError:

                continue

        # -----------------------------------------
        # Domains
        # -----------------------------------------

        domains = set()

        for url in urls:

            try:

                host = (
                    urlsplit(url)
                    .hostname
                    or ""
                ).lower()

                if host:

                    domains.add(
                        host
                    )

            except Exception:

                continue

        for address in (
            email_addresses
        ):

            if "@" in address:

                domains.add(
                    address
                    .rsplit(
                        "@",
                        1,
                    )[1]
                    .lower()
                )

        # -----------------------------------------
        # Attachments + hashes
        # -----------------------------------------

        attachments = [

            {
                "attachment_id":
                    str(
                        attachment
                        .attachment_id
                    ),

                "filename":
                    attachment.filename,

                "content_type":
                    attachment.content_type,

                "size_bytes":
                    attachment.size_bytes,

                "sha256":
                    attachment.sha256,

                "storage_key":
                    attachment.storage_key,
            }

            for attachment
            in email.attachments
        ]

        # -----------------------------------------

        iocs = {

            "urls":
                sorted(urls),

            "domains":
                sorted(domains),

            "ips":
                sorted(ips),

            "email_addresses":
                sorted(
                    email_addresses
                ),

            "attachments":
                attachments,

            "hashes":
                sorted(
                    {
                        attachment.sha256
                        for attachment
                        in email.attachments
                    }
                ),
        }

        findings = []

        if any(
            iocs[key]
            for key in (
                "urls",
                "domains",
                "ips",
                "attachments",
            )
        ):

            findings.append(
                new_finding(
                    title=(
                        "Indicators extracted"
                    ),
                    category=(
                        "ioc_inventory"
                    ),
                    severity=(
                        FindingSeverity.INFO
                    ),
                    description=(
                        "Indicators were extracted "
                        "for downstream intelligence "
                        "analysis."
                    ),
                    evidence={
                        "url_count":
                            len(
                                iocs["urls"]
                            ),
                        "domain_count":
                            len(
                                iocs["domains"]
                            ),
                        "ip_count":
                            len(
                                iocs["ips"]
                            ),
                        "attachment_count":
                            len(
                                iocs[
                                    "attachments"
                                ]
                            ),
                    },
                )
            )

        return ModuleAnalysisResult(

            module=self.module_name,

            status=(
                ModuleStatus.COMPLETED
            ),

            # Extractor does NOT predict risk
            score=None,

            confidence=1.0,

            findings=findings,

            evidence={
                "iocs": iocs
            },

            metadata={

                "url_count":
                    len(iocs["urls"]),

                "domain_count":
                    len(
                        iocs["domains"]
                    ),

                "ip_count":
                    len(iocs["ips"]),

                "email_count":
                    len(
                        iocs[
                            "email_addresses"
                        ]
                    ),

                "attachment_count":
                    len(
                        iocs[
                            "attachments"
                        ]
                    ),
            },
        )