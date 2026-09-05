from app.analysis.threat_intelligence.analyzer import (
    ExternalThreatIntelligenceAnalyzer,
)

from app.analysis.threat_intelligence.models import (
    ProviderResult,
    ThreatIntelligenceResult,
)


class FakeThreatIntelligenceService:

    def analyze(
        self,
        indicator: str,
        indicator_type: str,
    ):

        if indicator == "evil.example":
            return ThreatIntelligenceResult(
                indicator=indicator,
                indicator_type=indicator_type,
                provider_results=[
                    ProviderResult(
                        provider="fake_provider",
                        indicator=indicator,
                        indicator_type=indicator_type,
                        success=True,
                        risk_score=100,
                        malicious=True,
                        findings=[
                            "Known malicious indicator."
                        ],
                        metadata={},
                    )
                ],
                aggregate_score=100,
            )

        return ThreatIntelligenceResult(
            indicator=indicator,
            indicator_type=indicator_type,
            provider_results=[
                ProviderResult(
                    provider="fake_provider",
                    indicator=indicator,
                    indicator_type=indicator_type,
                    success=True,
                    risk_score=0,
                    malicious=False,
                    findings=[],
                    metadata={},
                )
            ],
            aggregate_score=0,
        )


def test_external_intelligence_detects_malicious_domain():

    analyzer = (
        ExternalThreatIntelligenceAnalyzer(
            service=(
                FakeThreatIntelligenceService()
            )
        )
    )

    result = analyzer.analyze_iocs(
        {
            "urls": [],
            "domains": [
                "evil.example"
            ],
        }
    )

    assert result["score"] == 100

    assert (
        len(
            result[
                "malicious_indicators"
            ]
        )
        == 1
    )

    assert (
        result[
            "malicious_indicators"
        ][0]["indicator"]
        == "evil.example"
    )


def test_external_intelligence_clean_indicator():

    analyzer = (
        ExternalThreatIntelligenceAnalyzer(
            service=(
                FakeThreatIntelligenceService()
            )
        )
    )

    result = analyzer.analyze_iocs(
        {
            "urls": [],
            "domains": [
                "example.com"
            ],
        }
    )

    assert result["score"] == 0

    assert (
        result[
            "malicious_indicators"
        ]
        == []
    )