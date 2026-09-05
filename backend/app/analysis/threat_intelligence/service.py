from app.analysis.threat_intelligence.models import (
    ThreatIntelligenceResult,
)

from app.analysis.threat_intelligence.providers.dns import (
    DNSIntelligenceProvider,
)

from app.analysis.threat_intelligence.providers.rdap import (
    RDAPIntelligenceProvider,
)

from app.analysis.threat_intelligence.providers.virustotal import (
    VirusTotalProvider,
)

from app.analysis.threat_intelligence.providers.safe_browsing import (
    GoogleSafeBrowsingProvider,
)


class ThreatIntelligenceService:

    def __init__(self):
        self.providers = [
            DNSIntelligenceProvider(),
            RDAPIntelligenceProvider(),
            VirusTotalProvider(),
            GoogleSafeBrowsingProvider(),
        ]

    def analyze(
        self,
        indicator: str,
        indicator_type: str,
    ) -> ThreatIntelligenceResult:

        results = []

        for provider in self.providers:

            if not provider.supports(
                indicator_type
            ):
                continue

            try:
                result = provider.analyze(
                    indicator=indicator,
                    indicator_type=indicator_type,
                )

                results.append(result)

            except Exception as exc:
                # A provider must never break
                # the complete email analysis.
                continue

        successful_scores = [
            result.risk_score
            for result in results
            if (
                result.success
                and result.risk_score is not None
            )
        ]

        if successful_scores:
            aggregate_score = round(
                sum(successful_scores)
                / len(successful_scores)
            )
        else:
            aggregate_score = 0

        return ThreatIntelligenceResult(
            indicator=indicator,
            indicator_type=indicator_type,
            provider_results=results,
            aggregate_score=min(
                aggregate_score,
                100,
            ),
        )