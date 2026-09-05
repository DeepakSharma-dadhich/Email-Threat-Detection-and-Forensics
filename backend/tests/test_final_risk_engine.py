from uuid import uuid4

from app.analysis.risk import (
    FinalRiskEngine,
)

from app.schemas.analysis_contract import (
    AnalysisJobStatus,
    AnalysisResult,
    ModuleAnalysisResult,
    ModuleStatus,
)


def module_result(
    name: str,
    score: int | None,
    evidence: dict | None = None,
):
    return ModuleAnalysisResult(
        module=name,
        status=ModuleStatus.COMPLETED,
        score=score,
        confidence=0.9,
        findings=[],
        evidence=(
            evidence
            or {}
        ),
        metadata={},
    )


def test_safe_email_decision():

    result = AnalysisResult(
        email_id=uuid4(),
        job_status=(
            AnalysisJobStatus.COMPLETED
        ),
        module_results=[
            module_result(
                "header_forensics",
                0,
            ),
            module_result(
                "nlp_analysis",
                0,
            ),
            module_result(
                "ioc_extraction",
                None,
                {
                    "iocs": {
                        "urls": [],
                    }
                },
            ),
            module_result(
                "ioc_static_intelligence",
                0,
            ),
        ],
        aggregate_score=None,
        verdict=None,
        recommended_action=None,
    )

    decision = (
        FinalRiskEngine()
        .evaluate(
            result
        )
    )

    assert (
        decision.aggregate_score
        == 0
    )

    assert (
        decision.verdict
        == "safe"
    )

    assert (
        decision.recommended_action
        == "allow"
    )

    assert (
        decision
        .browser_isolation_recommended
        is False
    )


def test_suspicious_email_recommends_dynamic_analysis():

    result = AnalysisResult(
        email_id=uuid4(),
        job_status=(
            AnalysisJobStatus.COMPLETED
        ),
        module_results=[
            module_result(
                "header_forensics",
                55,
            ),
            module_result(
                "nlp_analysis",
                70,
            ),
            module_result(
                "ioc_extraction",
                None,
                {
                    "iocs": {
                        "urls": [
                            "http://example.test/login"
                        ]
                    }
                },
            ),
            module_result(
                "ioc_static_intelligence",
                55,
            ),
        ],
        aggregate_score=None,
        verdict=None,
        recommended_action=None,
    )

    decision = (
        FinalRiskEngine()
        .evaluate(
            result
        )
    )

    assert (
        decision.aggregate_score
        >= 60
    )

    assert (
        decision.verdict
        in {
            "high_risk",
            "malicious",
        }
    )

    assert (
        decision
        .browser_isolation_recommended
        is True
    )