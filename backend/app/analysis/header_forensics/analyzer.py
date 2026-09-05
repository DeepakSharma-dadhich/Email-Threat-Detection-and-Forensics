import re
from ipaddress import ip_address

from app.analysis.common import (
    email_domain,
    header_value,
    header_values,
    new_finding,
)

from app.schemas.analysis_contract import (
    FindingSeverity,
    ModuleAnalysisResult,
    ModuleStatus,
)

from app.schemas.email import CommonEmailObject


_AUTH_RE = re.compile(
    r"\b(spf|dkim|dmarc)\s*=\s*([a-zA-Z0-9_-]+)",
    re.I,
)

_RECEIVED_IP_RE = re.compile(
    r"\[([0-9a-fA-F:.]+)\]"
)


class HeaderForensicsAnalyzer:

    module_name = "header_forensics"

    def analyze(
        self,
        email: CommonEmailObject,
    ) -> ModuleAnalysisResult:

        findings = []

        score = 0.0

        evidence: dict = {}

        # -------------------------------------------------
        # Authentication analysis
        # -------------------------------------------------

        auth = self._authentication_results(email)

        evidence["authentication"] = auth

        for mechanism in (
            "spf",
            "dkim",
            "dmarc",
        ):

            status = auth.get(mechanism)

            if status in {
                "fail",
                "softfail",
                "permerror",
                "temperror",
            }:

                severity = (
                    FindingSeverity.HIGH
                    if mechanism == "dmarc"
                    else FindingSeverity.MEDIUM
                )

                weight = (
                    24
                    if mechanism == "dmarc"
                    else 16
                )

                score += weight

                findings.append(
                    new_finding(
                        title=(
                            f"{mechanism.upper()} "
                            f"authentication problem"
                        ),
                        category="email_authentication",
                        severity=severity,
                        description=(
                            f"{mechanism.upper()} "
                            f"result is '{status}'."
                        ),
                        evidence={
                            "mechanism": mechanism,
                            "result": status,
                        },
                    )
                )

        # -------------------------------------------------
        # Identity alignment
        # -------------------------------------------------

        from_domain = email_domain(
            email.from_address.address
            if email.from_address
            else None
        )

        reply_domain = email_domain(
            email.reply_to.address
            if email.reply_to
            else None
        )

        return_path_domain = email_domain(
            email.return_path
        )

        message_id_domain = (
            self._message_id_domain(
                email.message_id
            )
        )

        alignment = {
            "from_domain": from_domain,
            "reply_to_domain": reply_domain,
            "return_path_domain": return_path_domain,
            "message_id_domain": message_id_domain,
        }

        evidence["alignment"] = alignment

        # -------------------------------------------------
        # From vs Reply-To
        # -------------------------------------------------

        if (
            from_domain
            and reply_domain
            and from_domain != reply_domain
        ):

            score += 18

            findings.append(
                new_finding(
                    title=(
                        "From and Reply-To "
                        "domain mismatch"
                    ),
                    category="identity_alignment",
                    severity=FindingSeverity.HIGH,
                    description=(
                        "Replies would be sent to "
                        "a domain different from "
                        "the visible sender domain."
                    ),
                    evidence=alignment,
                )
            )

        # -------------------------------------------------
        # From vs Return-Path
        # -------------------------------------------------

        if (
            from_domain
            and return_path_domain
            and from_domain
            != return_path_domain
        ):

            score += 10

            findings.append(
                new_finding(
                    title=(
                        "From and Return-Path "
                        "domain mismatch"
                    ),
                    category="identity_alignment",
                    severity=FindingSeverity.MEDIUM,
                    description=(
                        "Envelope return path uses "
                        "a different domain from "
                        "the visible sender."
                    ),
                    evidence=alignment,
                )
            )

        # -------------------------------------------------
        # Message-ID alignment
        # -------------------------------------------------

        if (
            from_domain
            and message_id_domain
            and from_domain
            != message_id_domain
        ):

            score += 6

            findings.append(
                new_finding(
                    title=(
                        "Message-ID domain "
                        "differs from sender"
                    ),
                    category="identity_alignment",
                    severity=FindingSeverity.LOW,
                    description=(
                        "The Message-ID domain "
                        "does not match the visible "
                        "sender domain."
                    ),
                    evidence=alignment,
                )
            )

        # -------------------------------------------------
        # Missing headers
        # -------------------------------------------------

        missing = []

        if not email.from_address:
            missing.append("From")

        if not email.message_id:
            missing.append("Message-ID")

        if not header_value(email, "Date"):
            missing.append("Date")

        if missing:

            score += min(
                12,
                len(missing) * 4,
            )

            findings.append(
                new_finding(
                    title=(
                        "Expected headers "
                        "are missing"
                    ),
                    category="header_integrity",
                    severity=FindingSeverity.LOW,
                    description=(
                        "One or more commonly "
                        "expected email headers "
                        "are absent."
                    ),
                    evidence={
                        "missing": missing
                    },
                )
            )

        # -------------------------------------------------
        # Received chain
        # -------------------------------------------------

        received = header_values(
            email,
            "Received",
        )

        received_summary = (
            self._received_summary(
                received
            )
        )

        evidence["received_chain"] = (
            received_summary
        )

        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------

        confidence = self._confidence(
            email,
            auth,
            received,
        )

        return ModuleAnalysisResult(
            module=self.module_name,
            status=ModuleStatus.COMPLETED,
            score=min(
                round(score, 2),
                100.0,
            ),
            confidence=confidence,
            findings=findings,
            evidence=evidence,
            metadata={
                "received_hops": len(received),
                "authentication_header_present": bool(
                    header_value(
                        email,
                        "Authentication-Results",
                    )
                    or header_value(
                        email,
                        "Received-SPF",
                    )
                ),
            },
        )

    # -----------------------------------------------------
    # Authentication parser
    # -----------------------------------------------------

    def _authentication_results(
        self,
        email: CommonEmailObject,
    ) -> dict[str, str | None]:

        combined = " ".join(
            header_values(
                email,
                "Authentication-Results",
            )
        )

        received_spf = " ".join(
            header_values(
                email,
                "Received-SPF",
            )
        )

        result: dict[str, str | None] = {
            "spf": None,
            "dkim": None,
            "dmarc": None,
        }

        for mechanism, status in (
            _AUTH_RE.findall(combined)
        ):

            result[
                mechanism.lower()
            ] = status.lower()

        if (
            result["spf"] is None
            and received_spf
        ):

            token = (
                received_spf
                .strip()
                .split(None, 1)[0]
                .lower()
                .rstrip(";")
            )

            if token:
                result["spf"] = token

        return result

    # -----------------------------------------------------

    @staticmethod
    def _message_id_domain(
        message_id: str | None,
    ) -> str | None:

        if (
            not message_id
            or "@" not in message_id
        ):
            return None

        return (
            message_id
            .strip("<>")
            .rsplit("@", 1)[1]
            .lower()
        )

    # -----------------------------------------------------

    @staticmethod
    def _received_summary(
        received_headers: list[str],
    ) -> dict:

        public_ips = []

        private_ips = []

        invalid_ips = []

        for value in received_headers:

            candidates = (
                _RECEIVED_IP_RE.findall(value)
            )

            for candidate in candidates:

                try:
                    ip = ip_address(candidate)

                    target = (
                        private_ips
                        if (
                            ip.is_private
                            or ip.is_loopback
                        )
                        else public_ips
                    )

                    if str(ip) not in target:
                        target.append(str(ip))

                except ValueError:

                    if (
                        candidate
                        not in invalid_ips
                    ):
                        invalid_ips.append(
                            candidate
                        )

        return {
            "hop_count": len(
                received_headers
            ),
            "public_ips": public_ips,
            "private_or_local_ips": (
                private_ips
            ),
            "unparsed_ip_literals": (
                invalid_ips
            ),
        }

    # -----------------------------------------------------

    @staticmethod
    def _confidence(
        email: CommonEmailObject,
        auth: dict,
        received: list[str],
    ) -> float:

        signals = 0

        if email.from_address:
            signals += 1

        if email.return_path:
            signals += 1

        if any(auth.values()):
            signals += 2

        if received:
            signals += 2

        if email.message_id:
            signals += 1

        confidence = min(
            0.45 + (signals * 0.07),
            0.94,
        )

        return round(
            confidence,
            2,
        )