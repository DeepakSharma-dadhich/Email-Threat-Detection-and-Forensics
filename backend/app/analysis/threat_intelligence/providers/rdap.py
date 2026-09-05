from datetime import (
    datetime,
    timezone,
)

import httpx
import tldextract

from app.analysis.threat_intelligence.models import (
    ProviderResult,
)

from app.analysis.threat_intelligence.providers.base import (
    ThreatIntelligenceProvider,
)


class RDAPIntelligenceProvider(
    ThreatIntelligenceProvider
):

    BASE_URL = (
        "https://rdap.org/domain/"
    )

    def supports(
        self,
        indicator_type: str,
    ) -> bool:
        return indicator_type == "domain"

    def analyze(
        self,
        indicator: str,
        indicator_type: str,
    ) -> ProviderResult:

        lookup_domain = (
            self._get_registrable_domain(
                indicator
            )
        )

        if not lookup_domain:
            return ProviderResult(
                provider="rdap",
                indicator=indicator,
                indicator_type=indicator_type,
                success=False,
                error=(
                    "Unable to determine "
                    "registrable domain."
                ),
            )

        try:
            response = httpx.get(
                (
                    f"{self.BASE_URL}"
                    f"{lookup_domain}"
                ),
                timeout=8.0,
                follow_redirects=True,
            )

            if response.status_code == 404:
                return ProviderResult(
                    provider="rdap",
                    indicator=indicator,
                    indicator_type=indicator_type,
                    success=True,
                    risk_score=10,
                    malicious=False,
                    findings=[
                        (
                            "No RDAP registration "
                            "record was found for "
                            "the registrable domain."
                        )
                    ],
                    metadata={
                        "registered": False,
                        "original_domain":
                            indicator,
                        "lookup_domain":
                            lookup_domain,
                    },
                )

            response.raise_for_status()

            payload = response.json()

            creation_date = None
            expiration_date = None

            for event in payload.get(
                "events",
                [],
            ):

                action = event.get(
                    "eventAction"
                )

                event_date = event.get(
                    "eventDate"
                )

                if (
                    action == "registration"
                    and event_date
                ):
                    creation_date = (
                        event_date
                    )

                elif (
                    action == "expiration"
                    and event_date
                ):
                    expiration_date = (
                        event_date
                    )

            findings = []
            risk_score = 0
            age_days = None

            if creation_date:

                try:
                    created_at = (
                        datetime.fromisoformat(
                            creation_date.replace(
                                "Z",
                                "+00:00",
                            )
                        )
                    )

                    now = datetime.now(
                        timezone.utc
                    )

                    age_days = (
                        now - created_at
                    ).days

                    if age_days < 30:

                        risk_score += 30

                        findings.append(
                            (
                                "Registrable domain "
                                "was created less "
                                "than 30 days ago."
                            )
                        )

                    elif age_days < 90:

                        risk_score += 15

                        findings.append(
                            (
                                "Registrable domain "
                                "was created less "
                                "than 90 days ago."
                            )
                        )

                except ValueError:
                    pass

            metadata = {
                "registered": True,

                "original_domain":
                    indicator,

                "lookup_domain":
                    lookup_domain,

                "creation_date":
                    creation_date,

                "expiration_date":
                    expiration_date,

                "age_days":
                    age_days,

                "handle":
                    payload.get(
                        "handle"
                    ),

                "ldh_name":
                    payload.get(
                        "ldhName"
                    ),

                "status":
                    payload.get(
                        "status",
                        [],
                    ),
            }

            return ProviderResult(
                provider="rdap",
                indicator=indicator,
                indicator_type=indicator_type,
                success=True,
                risk_score=min(
                    risk_score,
                    100,
                ),
                malicious=False,
                findings=findings,
                metadata=metadata,
            )

        except Exception as exc:

            return ProviderResult(
                provider="rdap",
                indicator=indicator,
                indicator_type=indicator_type,
                success=False,
                error=str(exc),
            )

    @staticmethod
    def _get_registrable_domain(
        domain: str,
    ) -> str | None:

        domain = (
            domain
            .strip()
            .lower()
            .rstrip(".")
        )

        extracted = (
            tldextract.extract(
                domain
            )
        )

        if (
            not extracted.domain
            or not extracted.suffix
        ):
            return None

        return (
            f"{extracted.domain}."
            f"{extracted.suffix}"
        )