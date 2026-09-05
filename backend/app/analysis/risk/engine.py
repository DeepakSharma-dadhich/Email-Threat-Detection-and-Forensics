from dataclasses import dataclass

from app.schemas.analysis_contract import (
    AnalysisResult,
    ModuleStatus,
)


@dataclass(frozen=True)
class RiskDecision:
    aggregate_score: int
    verdict: str
    recommended_action: str
    browser_isolation_recommended: bool


class FinalRiskEngine:
    """
    Combines module-level risk scores into the final email risk decision.

    Important:
    IOC Extraction is intentionally not included because it only
    extracts indicators and does not assess their risk.
    """

    MODULE_WEIGHTS = {
        "header_forensics": 0.30,
        "nlp_analysis": 0.30,
        "ioc_static_intelligence": 0.40,
    }

    def evaluate(
        self,
        analysis_result: AnalysisResult,
    ) -> RiskDecision:

        weighted_score = 0.0
        available_weight = 0.0

        module_map = {
            result.module: result
            for result in analysis_result.module_results
        }

        for module_name, weight in self.MODULE_WEIGHTS.items():
            module = module_map.get(module_name)

            if module is None:
                continue

            if module.status != ModuleStatus.COMPLETED:
                continue

            if module.score is None:
                continue

            score = max(
                0,
                min(100, float(module.score)),
            )

            weighted_score += score * weight
            available_weight += weight

        if available_weight == 0:
            aggregate_score = 0
        else:
            aggregate_score = round(
                weighted_score / available_weight
            )

        aggregate_score = self._apply_cross_module_rules(
            aggregate_score=aggregate_score,
            module_map=module_map,
        )

        aggregate_score = max(
            0,
            min(100, aggregate_score),
        )

        verdict, action = self._decision_from_score(
            aggregate_score
        )

        browser_isolation_recommended = (
            self._should_use_browser_isolation(
                aggregate_score=aggregate_score,
                module_map=module_map,
            )
        )

        return RiskDecision(
            aggregate_score=aggregate_score,
            verdict=verdict,
            recommended_action=action,
            browser_isolation_recommended=(
                browser_isolation_recommended
            ),
        )

    def _apply_cross_module_rules(
        self,
        aggregate_score: int,
        module_map: dict,
    ) -> int:

        score = aggregate_score

        header_score = self._module_score(
            module_map,
            "header_forensics",
        )

        nlp_score = self._module_score(
            module_map,
            "nlp_analysis",
        )

        ioc_score = self._module_score(
            module_map,
            "ioc_static_intelligence",
        )

        # Multiple independent modules agreeing on risk
        # increases confidence in the final decision.
        high_modules = sum(
            value >= 50
            for value in (
                header_score,
                nlp_score,
                ioc_score,
            )
        )

        if high_modules >= 2:
            score += 10

        # Strong social engineering + suspicious infrastructure.
        if (
            nlp_score >= 60
            and ioc_score >= 40
        ):
            score += 8

        # Authentication/alignment problems together with
        # suspicious language.
        if (
            header_score >= 50
            and nlp_score >= 50
        ):
            score += 7

        return score

    @staticmethod
    def _module_score(
        module_map: dict,
        module_name: str,
    ) -> int:

        module = module_map.get(module_name)

        if (
            module is None
            or module.score is None
        ):
            return 0

        return int(module.score)

    @staticmethod
    def _decision_from_score(
        score: int,
    ) -> tuple[str, str]:

        if score < 20:
            return (
                "safe",
                "allow",
            )

        if score < 40:
            return (
                "low_risk",
                "allow_with_monitoring",
            )

        if score < 60:
            return (
                "suspicious",
                "review",
            )

        if score < 80:
            return (
                "high_risk",
                "quarantine",
            )

        return (
            "malicious",
            "block",
        )

    def _should_use_browser_isolation(
        self,
        aggregate_score: int,
        module_map: dict,
    ) -> bool:
        """
        Browser isolation is a separate project.

        This function only decides whether dynamic URL analysis
        would be useful.

        Later an external API adapter can use this flag.
        """

        ioc_module = module_map.get(
            "ioc_static_intelligence"
        )

        extraction_module = module_map.get(
            "ioc_extraction"
        )

        if extraction_module is None:
            return False

        iocs = (
            extraction_module.evidence
            .get("iocs", {})
        )

        urls = iocs.get(
            "urls",
            [],
        )

        if not urls:
            return False

        ioc_score = 0

        if (
            ioc_module is not None
            and ioc_module.score is not None
        ):
            ioc_score = int(
                ioc_module.score
            )

        # Clearly safe message.
        if (
            aggregate_score < 20
            and ioc_score == 0
        ):
            return False

        # Suspicious email containing one or more URLs.
        if aggregate_score >= 40:
            return True

        # URL itself has meaningful static suspicion.
        if ioc_score >= 30:
            return True

        return False