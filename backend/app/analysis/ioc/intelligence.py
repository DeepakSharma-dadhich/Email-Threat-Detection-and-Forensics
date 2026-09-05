import ipaddress
import re

from urllib.parse import (
    unquote,
    urlsplit,
)

from app.analysis.common import (
    new_finding,
)

from app.schemas.analysis_contract import (
    FindingSeverity,
    ModuleAnalysisResult,
    ModuleStatus,
)


_SUSPICIOUS_URL_TOKENS = {

    "login",
    "verify",
    "verification",
    "secure",
    "account",
    "update",
    "password",
    "signin",
    "wallet",
    "billing",
    "invoice",
    "payment",
}


_SHORTENER_HOSTS = {

    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "cutt.ly",
}


_EXECUTABLE_EXTENSIONS = {

    ".exe",
    ".scr",
    ".msi",
    ".bat",
    ".cmd",
    ".ps1",
    ".js",
    ".vbs",
    ".jar",
}


class IOCIntelligenceAnalyzer:

    module_name = (
        "ioc_static_intelligence"
    )

    def analyze_iocs(
        self,
        iocs: dict,
    ) -> ModuleAnalysisResult:

        findings = []

        score = 0.0

        url_evidence = []

        # -----------------------------------------
        # URL Static Intelligence
        # -----------------------------------------

        for url in iocs.get(
            "urls",
            [],
        ):

            result = (
                self._analyze_url(
                    url
                )
            )

            url_evidence.append(
                result
            )

            score += result[
                "risk_points"
            ]

            risk_points = (
                result["risk_points"]
            )

            if risk_points >= 16:

                severity = (
                    FindingSeverity.HIGH
                )

            elif risk_points >= 8:

                severity = (
                    FindingSeverity.MEDIUM
                )

            elif risk_points > 0:

                severity = (
                    FindingSeverity.LOW
                )

            else:

                severity = None

            if severity:

                findings.append(
                    new_finding(
                        title=(
                            "Suspicious URL "
                            "characteristics"
                        ),
                        category=(
                            "url_static_analysis"
                        ),
                        severity=severity,
                        description=(
                            "The URL contains one "
                            "or more static "
                            "characteristics associated "
                            "with risky links."
                        ),
                        evidence=result,
                    )
                )

        # -----------------------------------------
        # IP information
        # -----------------------------------------

        ip_evidence = []

        for value in iocs.get(
            "ips",
            [],
        ):

            try:

                ip = ipaddress.ip_address(
                    value
                )

                item = {

                    "ip":
                        value,

                    "private":
                        ip.is_private,

                    "loopback":
                        ip.is_loopback,

                    "reserved":
                        ip.is_reserved,

                    "global":
                        ip.is_global,
                }

                ip_evidence.append(
                    item
                )

            except ValueError:

                continue

        # -----------------------------------------

        return ModuleAnalysisResult(

            module=self.module_name,

            status=(
                ModuleStatus.COMPLETED
            ),

            score=min(
                round(score, 2),
                100.0,
            ),

            confidence=(
                self._confidence(
                    iocs
                )
            ),

            findings=findings,

            evidence={

                "url_analysis":
                    url_evidence,

                "ip_analysis":
                    ip_evidence,
            },

            metadata={

                "engine":
                    "offline_static_ioc_v1",

                "external_reputation_used":
                    False,
            },
        )

    # -------------------------------------------------

    @staticmethod
    def _analyze_url(
        url: str,
    ) -> dict:

        points = 0

        reasons = []

        decoded = unquote(
            url
        )

        parsed = urlsplit(
            decoded
        )

        host = (
            parsed.hostname
            or ""
        ).lower()

        path_query = (
            f"{parsed.path}"
            f"?{parsed.query}"
        ).lower()

        # -----------------------------------------
        # HTTP
        # -----------------------------------------

        if (
            parsed.scheme.lower()
            != "https"
        ):

            points += 4

            reasons.append(
                "non_https"
            )

        # -----------------------------------------
        # URL Shortener
        # -----------------------------------------

        if host in _SHORTENER_HOSTS:

            points += 10

            reasons.append(
                "url_shortener"
            )

        # -----------------------------------------
        # IP literal
        # -----------------------------------------

        try:

            ipaddress.ip_address(
                host
            )

            points += 14

            reasons.append(
                "ip_literal_host"
            )

        except ValueError:

            pass

        # -----------------------------------------
        # Punycode
        # -----------------------------------------

        if "xn--" in host:

            points += 12

            reasons.append(
                "punycode_host"
            )

        # -----------------------------------------
        # Excessive subdomains
        # -----------------------------------------

        if host.count(".") >= 4:

            points += 5

            reasons.append(
                "many_subdomains"
            )

        # -----------------------------------------
        # user@host URL trick
        # -----------------------------------------

        if "@" in parsed.netloc:

            points += 12

            reasons.append(
                "userinfo_in_url"
            )

        # -----------------------------------------
        # Suspicious action keywords
        # -----------------------------------------

        token_hits = sorted(

            token

            for token
            in _SUSPICIOUS_URL_TOKENS

            if token in path_query
        )

        if token_hits:

            points += min(
                12,
                len(token_hits) * 3,
            )

            reasons.append(
                "sensitive_action_tokens"
            )

        # -----------------------------------------
        # Executable downloads
        # -----------------------------------------

        lowered_path = (
            parsed.path.lower()
        )

        if any(
            lowered_path.endswith(
                extension
            )
            for extension
            in _EXECUTABLE_EXTENSIONS
        ):

            points += 20

            reasons.append(
                "executable_download_extension"
            )

        # -----------------------------------------
        # Excessive URL length
        # -----------------------------------------

        if len(url) > 180:

            points += 5

            reasons.append(
                "very_long_url"
            )

        # -----------------------------------------
        # Encoding
        # -----------------------------------------

        if re.search(
            r"%[0-9a-fA-F]{2}",
            url,
        ):

            points += 3

            reasons.append(
                "percent_encoding"
            )

        return {

            "url":
                url,

            "host":
                host,

            "risk_points":
                min(
                    points,
                    100,
                ),

            "reasons":
                reasons,

            "token_hits":
                token_hits,
        }

    # -------------------------------------------------

    @staticmethod
    def _confidence(
        iocs: dict,
    ) -> float:

        url_count = len(
            iocs.get(
                "urls",
                [],
            )
        )

        if url_count == 0:

            return 0.70

        confidence = min(
            0.72
            + min(
                url_count,
                6,
            )
            * 0.03,
            0.90,
        )

        return round(
            confidence,
            2,
        )