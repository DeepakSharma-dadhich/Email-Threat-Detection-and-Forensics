import dns.resolver

from app.analysis.threat_intelligence.models import (
    ProviderResult,
)

from app.analysis.threat_intelligence.providers.base import (
    ThreatIntelligenceProvider,
)


class DNSIntelligenceProvider(
    ThreatIntelligenceProvider
):

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

        findings = []
        metadata = {
            "a_records": [],
            "aaaa_records": [],
            "mx_records": [],
        }

        resolved = False

        try:
            try:
                answers = dns.resolver.resolve(
                    indicator,
                    "A",
                )

                metadata["a_records"] = [
                    str(answer)
                    for answer in answers
                ]

                if metadata["a_records"]:
                    resolved = True

            except Exception:
                pass

            try:
                answers = dns.resolver.resolve(
                    indicator,
                    "AAAA",
                )

                metadata["aaaa_records"] = [
                    str(answer)
                    for answer in answers
                ]

                if metadata["aaaa_records"]:
                    resolved = True

            except Exception:
                pass

            try:
                answers = dns.resolver.resolve(
                    indicator,
                    "MX",
                )

                metadata["mx_records"] = [
                    str(answer.exchange).rstrip(
                        "."
                    )
                    for answer in answers
                ]

            except Exception:
                pass

            risk_score = 0

            if not resolved:
                risk_score = 20

                findings.append(
                    "Domain did not resolve to an "
                    "A or AAAA record."
                )

            return ProviderResult(
                provider="dns",
                indicator=indicator,
                indicator_type=indicator_type,
                success=True,
                risk_score=risk_score,
                malicious=False,
                findings=findings,
                metadata=metadata,
            )

        except Exception as exc:
            return ProviderResult(
                provider="dns",
                indicator=indicator,
                indicator_type=indicator_type,
                success=False,
                error=str(exc),
            )