import base64

import httpx

from app.analysis.threat_intelligence.models import (
    ProviderResult,
)

from app.analysis.threat_intelligence.providers.base import (
    ThreatIntelligenceProvider,
)

from app.core.config import settings


class VirusTotalProvider(
    ThreatIntelligenceProvider
):

    BASE_URL = (
        "https://www.virustotal.com/api/v3"
    )

    def supports(
        self,
        indicator_type: str,
    ) -> bool:
        return indicator_type in {
            "domain",
            "url",
        }

    def analyze(
        self,
        indicator: str,
        indicator_type: str,
    ) -> ProviderResult:

        api_key = getattr(
            settings,
            "VIRUSTOTAL_API_KEY",
            None,
        )

        if not api_key:
            return ProviderResult(
                provider="virustotal",
                indicator=indicator,
                indicator_type=indicator_type,
                success=False,
                risk_score=None,
                malicious=None,
                findings=[],
                metadata={},
                error=(
                    "VirusTotal API key "
                    "is not configured."
                ),
            )

        try:
            endpoint = self._build_endpoint(
                indicator,
                indicator_type,
            )

            response = httpx.get(
                endpoint,
                headers={
                    "x-apikey": api_key,
                },
                timeout=10.0,
                follow_redirects=True,
            )

            if response.status_code == 404:
                return ProviderResult(
                    provider="virustotal",
                    indicator=indicator,
                    indicator_type=indicator_type,
                    success=True,
                    risk_score=None,
                    malicious=None,
                    findings=[
                        (
                            "VirusTotal has no "
                            "existing report for "
                            "this indicator."
                        )
                    ],
                    metadata={
                        "report_found": False,
                    },
                    error=None,
                )

            response.raise_for_status()

            payload = response.json()

            attributes = (
                payload
                .get("data", {})
                .get("attributes", {})
            )

            stats = attributes.get(
                "last_analysis_stats",
                {},
            )

            malicious_count = stats.get(
                "malicious",
                0,
            )

            suspicious_count = stats.get(
                "suspicious",
                0,
            )

            harmless_count = stats.get(
                "harmless",
                0,
            )

            undetected_count = stats.get(
                "undetected",
                0,
            )

            risk_score = self._calculate_score(
                malicious_count,
                suspicious_count,
            )

            findings = []

            if malicious_count > 0:
                findings.append(
                    (
                        f"{malicious_count} "
                        "VirusTotal engines "
                        "classified the indicator "
                        "as malicious."
                    )
                )

            if suspicious_count > 0:
                findings.append(
                    (
                        f"{suspicious_count} "
                        "VirusTotal engines "
                        "classified the indicator "
                        "as suspicious."
                    )
                )

            return ProviderResult(
                provider="virustotal",
                indicator=indicator,
                indicator_type=indicator_type,
                success=True,
                risk_score=risk_score,
                malicious=(
                    malicious_count > 0
                ),
                findings=findings,
                metadata={
                    "report_found": True,
                    "malicious":
                        malicious_count,
                    "suspicious":
                        suspicious_count,
                    "harmless":
                        harmless_count,
                    "undetected":
                        undetected_count,
                    "reputation":
                        attributes.get(
                            "reputation"
                        ),
                    "last_analysis_date":
                        attributes.get(
                            "last_analysis_date"
                        ),
                },
                error=None,
            )

        except httpx.HTTPStatusError as exc:
            return ProviderResult(
                provider="virustotal",
                indicator=indicator,
                indicator_type=indicator_type,
                success=False,
                risk_score=None,
                malicious=None,
                findings=[],
                metadata={},
                error=(
                    "VirusTotal HTTP error: "
                    f"{exc.response.status_code}"
                ),
            )

        except Exception as exc:
            return ProviderResult(
                provider="virustotal",
                indicator=indicator,
                indicator_type=indicator_type,
                success=False,
                risk_score=None,
                malicious=None,
                findings=[],
                metadata={},
                error=str(exc),
            )

    def _build_endpoint(
        self,
        indicator: str,
        indicator_type: str,
    ) -> str:

        if indicator_type == "domain":
            return (
                f"{self.BASE_URL}/domains/"
                f"{indicator}"
            )

        encoded_url = (
            base64.urlsafe_b64encode(
                indicator.encode(
                    "utf-8"
                )
            )
            .decode("utf-8")
            .rstrip("=")
        )

        return (
            f"{self.BASE_URL}/urls/"
            f"{encoded_url}"
        )

    @staticmethod
    def _calculate_score(
        malicious: int,
        suspicious: int,
    ) -> int:

        if malicious >= 5:
            return 100

        if malicious >= 3:
            return 90

        if malicious >= 1:
            return 75

        if suspicious >= 3:
            return 60

        if suspicious >= 1:
            return 40

        return 0