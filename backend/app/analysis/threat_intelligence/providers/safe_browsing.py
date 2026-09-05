import httpx

from app.analysis.threat_intelligence.models import (
    ProviderResult,
)

from app.analysis.threat_intelligence.providers.base import (
    ThreatIntelligenceProvider,
)

from app.core.config import settings


class GoogleSafeBrowsingProvider(
    ThreatIntelligenceProvider
):

    BASE_URL = (
        "https://safebrowsing.googleapis.com/"
        "v4/threatMatches:find"
    )

    def supports(
        self,
        indicator_type: str,
    ) -> bool:
        return indicator_type == "url"

    def analyze(
        self,
        indicator: str,
        indicator_type: str,
    ) -> ProviderResult:

        api_key = getattr(
            settings,
            "GOOGLE_SAFE_BROWSING_API_KEY",
            None,
        )

        if not api_key:
            return ProviderResult(
                provider=(
                    "google_safe_browsing"
                ),
                indicator=indicator,
                indicator_type=indicator_type,
                success=False,
                risk_score=None,
                malicious=None,
                findings=[],
                metadata={},
                error=(
                    "Google Safe Browsing "
                    "API key is not configured."
                ),
            )

        payload = {
            "client": {
                "clientId": (
                    "email-threat-detection-platform"
                ),
                "clientVersion": "1.0.0",
            },
            "threatInfo": {
                "threatTypes": [
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                    "UNWANTED_SOFTWARE",
                    (
                        "POTENTIALLY_HARMFUL_"
                        "APPLICATION"
                    ),
                ],
                "platformTypes": [
                    "ANY_PLATFORM",
                ],
                "threatEntryTypes": [
                    "URL",
                ],
                "threatEntries": [
                    {
                        "url": indicator,
                    }
                ],
            },
        }

        try:
            response = httpx.post(
                self.BASE_URL,
                params={
                    "key": api_key,
                },
                json=payload,
                timeout=10.0,
            )

            response.raise_for_status()

            data = response.json()

            matches = data.get(
                "matches",
                [],
            )

            if not matches:
                return ProviderResult(
                    provider=(
                        "google_safe_browsing"
                    ),
                    indicator=indicator,
                    indicator_type=indicator_type,
                    success=True,
                    risk_score=0,
                    malicious=False,
                    findings=[],
                    metadata={
                        "match_count": 0,
                        "threat_types": [],
                    },
                    error=None,
                )

            threat_types = sorted(
                {
                    match.get(
                        "threatType",
                        "UNKNOWN",
                    )
                    for match in matches
                }
            )

            return ProviderResult(
                provider=(
                    "google_safe_browsing"
                ),
                indicator=indicator,
                indicator_type=indicator_type,
                success=True,
                risk_score=100,
                malicious=True,
                findings=[
                    (
                        "Google Safe Browsing "
                        "matched the URL against "
                        "an unsafe resource list."
                    )
                ],
                metadata={
                    "match_count":
                        len(matches),

                    "threat_types":
                        threat_types,
                },
                error=None,
            )

        except httpx.HTTPStatusError as exc:
            return ProviderResult(
                provider=(
                    "google_safe_browsing"
                ),
                indicator=indicator,
                indicator_type=indicator_type,
                success=False,
                risk_score=None,
                malicious=None,
                findings=[],
                metadata={},
                error=(
                    "Google Safe Browsing "
                    "HTTP error: "
                    f"{exc.response.status_code}"
                ),
            )

        except Exception as exc:
            return ProviderResult(
                provider=(
                    "google_safe_browsing"
                ),
                indicator=indicator,
                indicator_type=indicator_type,
                success=False,
                risk_score=None,
                malicious=None,
                findings=[],
                metadata={},
                error=str(exc),
            )