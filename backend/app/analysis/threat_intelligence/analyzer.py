from app.analysis.common import (
    new_finding,
)

from app.analysis.threat_intelligence.service import (
    ThreatIntelligenceService,
)

from app.schemas.analysis_contract import (
    FindingSeverity,
    ModuleAnalysisResult,
)


class ExternalThreatIntelligenceAnalyzer:

    REPUTATION_PROVIDERS = {
        "virustotal",
        "google_safe_browsing",
    }

    CONTEXT_PROVIDERS = {
        "dns",
        "rdap",
    }

    def __init__(
        self,
        service: ThreatIntelligenceService | None = None,
        max_urls: int = 10,
        max_domains: int = 10,
    ):
        self.service = (
            service
            or ThreatIntelligenceService()
        )

        self.max_urls = max_urls
        self.max_domains = max_domains

    def analyze_iocs(
        self,
        iocs: dict,
    ) -> dict:

        urls = (
            iocs.get("urls", [])
            [:self.max_urls]
        )

        domains = (
            iocs.get("domains", [])
            [:self.max_domains]
        )

        results = []

        for url in urls:
            result = self.service.analyze(
                indicator=url,
                indicator_type="url",
            )

            results.append(result)

        for domain in domains:
            result = self.service.analyze(
                indicator=domain,
                indicator_type="domain",
            )

            results.append(result)

        reputation_scores = []
        context_scores = []

        malicious_indicators = []
        provider_failures = []

        successful_reputation_providers = 0
        successful_context_providers = 0

        for result in results:

            for provider_result in (
                result.provider_results
            ):

                provider_name = (
                    provider_result.provider
                )

                if not provider_result.success:
                    provider_failures.append(
                        {
                            "indicator":
                                result.indicator,

                            "indicator_type":
                                result.indicator_type,

                            "provider":
                                provider_name,

                            "error":
                                provider_result.error,
                        }
                    )

                    continue

                if (
                    provider_name
                    in self.REPUTATION_PROVIDERS
                ):
                    successful_reputation_providers += 1

                    if (
                        provider_result.risk_score
                        is not None
                    ):
                        reputation_scores.append(
                            provider_result.risk_score
                        )

                elif (
                    provider_name
                    in self.CONTEXT_PROVIDERS
                ):
                    successful_context_providers += 1

                    if (
                        provider_result.risk_score
                        is not None
                    ):
                        context_scores.append(
                            provider_result.risk_score
                        )

                if (
                    provider_result.malicious
                    is True
                ):
                    if (
                        provider_result.risk_score
                        is not None
                        and provider_result.risk_score
                        not in reputation_scores
                    ):
                        reputation_scores.append(
                            provider_result.risk_score
                        )

                    malicious_indicators.append(
                        {
                            "indicator":
                                result.indicator,

                            "indicator_type":
                                result.indicator_type,

                            "provider":
                                provider_name,

                            "risk_score":
                                provider_result.risk_score,

                            "findings":
                                provider_result.findings,
                        }
                    )

        reputation_score = (
            max(reputation_scores)
            if reputation_scores
            else 0
        )

        context_score = (
            max(context_scores)
            if context_scores
            else 0
        )

        return {
            "score": min(
                reputation_score,
                100,
            ),

            "context_score": min(
                context_score,
                100,
            ),

            "results": [
                self._serialize_result(
                    result
                )
                for result in results
            ],

            "malicious_indicators":
                malicious_indicators,

            "provider_failures":
                provider_failures,

            "metadata": {
                "url_count_analyzed":
                    len(urls),

                "domain_count_analyzed":
                    len(domains),

                "indicator_count_analyzed":
                    len(results),

                "provider_failure_count":
                    len(provider_failures),

                "malicious_indicator_count":
                    len(malicious_indicators),

                "successful_reputation_providers":
                    successful_reputation_providers,

                "successful_context_providers":
                    successful_context_providers,

                "reputation_score":
                    min(
                        reputation_score,
                        100,
                    ),

                "context_score":
                    min(
                        context_score,
                        100,
                    ),

                "max_urls":
                    self.max_urls,

                "max_domains":
                    self.max_domains,
            },
        }

    @staticmethod
    def enrich_static_result(
        static_result: ModuleAnalysisResult,
        external_result: dict,
    ) -> ModuleAnalysisResult:

        static_score = (
            static_result.score
            if static_result.score is not None
            else 0
        )

        external_score = (
            external_result.get(
                "score",
                0,
            )
        )

        context_score = (
            external_result.get(
                "context_score",
                0,
            )
        )

        if external_score >= 90:
            enriched_score = max(
                static_score,
                90,
            )

        elif external_score >= 70:
            enriched_score = max(
                static_score,
                75,
            )

        elif external_score >= 40:
            enriched_score = max(
                static_score,
                50,
            )

        elif external_score >= 20:
            enriched_score = max(
                static_score,
                25,
            )

        else:
            enriched_score = static_score

        enriched_score = min(
            enriched_score,
            100,
        )

        findings = list(
            static_result.findings
        )

        malicious_indicators = (
            external_result.get(
                "malicious_indicators",
                [],
            )
        )

        if malicious_indicators:
            findings.append(
                new_finding(
                    title=(
                        "External threat intelligence "
                        "match"
                    ),
                    category=(
                        "external_threat_intelligence"
                    ),
                    severity=(
                        FindingSeverity.HIGH
                    ),
                    description=(
                        "One or more extracted "
                        "indicators were identified "
                        "as malicious by an external "
                        "threat intelligence provider."
                    ),
                    evidence={
                        "matches":
                            malicious_indicators,
                    },
                )
            )

        evidence = dict(
            static_result.evidence
        )

        evidence[
            "external_threat_intelligence"
        ] = {
            "score":
                external_score,

            "context_score":
                context_score,

            "results":
                external_result.get(
                    "results",
                    [],
                ),

            "malicious_indicators":
                malicious_indicators,

            "provider_failures":
                external_result.get(
                    "provider_failures",
                    [],
                ),

            "metadata":
                external_result.get(
                    "metadata",
                    {},
                ),
        }

        metadata = dict(
            static_result.metadata
        )

        metadata.update(
            {
                "static_score":
                    static_score,

                "external_intelligence_score":
                    external_score,

                "external_context_score":
                    context_score,

                "enriched_score":
                    enriched_score,

                "external_intelligence_used":
                    bool(
                        external_result.get(
                            "results",
                            [],
                        )
                    ),

                "external_reputation_available":
                    (
                        external_result
                        .get(
                            "metadata",
                            {},
                        )
                        .get(
                            "successful_reputation_providers",
                            0,
                        )
                        > 0
                    ),

                "external_provider_failures":
                    len(
                        external_result.get(
                            "provider_failures",
                            [],
                        )
                    ),

                "external_malicious_matches":
                    len(
                        malicious_indicators
                    ),
            }
        )

        return ModuleAnalysisResult(
            module=static_result.module,
            status=static_result.status,
            score=enriched_score,
            confidence=static_result.confidence,
            findings=findings,
            evidence=evidence,
            metadata=metadata,
        )

    @staticmethod
    def _serialize_result(
        result,
    ) -> dict:

        return {
            "indicator":
                result.indicator,

            "indicator_type":
                result.indicator_type,

            "aggregate_score":
                result.aggregate_score,

            "providers": [
                {
                    "provider":
                        provider.provider,

                    "success":
                        provider.success,

                    "risk_score":
                        provider.risk_score,

                    "malicious":
                        provider.malicious,

                    "findings":
                        provider.findings,

                    "metadata":
                        provider.metadata,

                    "error":
                        provider.error,
                }
                for provider
                in result.provider_results
            ],
        }