import re

from app.analysis.common import (
    new_finding,
    strip_html,
)

from app.analysis.nlp.rules import (
    CATEGORY_PATTERNS,
)

from app.schemas.analysis_contract import (
    FindingSeverity,
    ModuleAnalysisResult,
    ModuleStatus,
)

from app.schemas.email import CommonEmailObject


_CATEGORY_WEIGHTS = {

    "urgency": 10,

    "credential_request": 24,

    "financial_request": 20,

    "threat_pressure": 14,

    "secrecy": 12,

    "impersonation_bec": 22,

    "link_action": 8,
}


_CATEGORY_SEVERITY = {

    "urgency":
        FindingSeverity.MEDIUM,

    "credential_request":
        FindingSeverity.HIGH,

    "financial_request":
        FindingSeverity.HIGH,

    "threat_pressure":
        FindingSeverity.MEDIUM,

    "secrecy":
        FindingSeverity.MEDIUM,

    "impersonation_bec":
        FindingSeverity.HIGH,

    "link_action":
        FindingSeverity.LOW,
}


class NLPAnalyzer:

    module_name = "nlp_analysis"

    def analyze(
        self,
        email: CommonEmailObject,
    ) -> ModuleAnalysisResult:

        text = self._combined_text(
            email
        )

        normalized = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        findings = []

        evidence: dict[
            str,
            list[str],
        ] = {}

        score = 0.0

        # ---------------------------------------------
        # Detect NLP categories
        # ---------------------------------------------

        for (
            category,
            patterns,
        ) in CATEGORY_PATTERNS.items():

            matches = []

            for pattern in patterns:

                for match in re.finditer(
                    pattern,
                    normalized,
                    flags=re.I,
                ):

                    snippet = match.group(0)

                    existing = {
                        item.lower()
                        for item in matches
                    }

                    if (
                        snippet.lower()
                        not in existing
                    ):
                        matches.append(
                            snippet
                        )

            if matches:

                evidence[
                    category
                ] = matches[:8]

                weight = (
                    _CATEGORY_WEIGHTS[
                        category
                    ]
                )

                score += weight

                findings.append(
                    new_finding(
                        title=(
                            category
                            .replace(
                                "_",
                                " ",
                            )
                            .title()
                        ),
                        category=(
                            "social_engineering"
                        ),
                        severity=(
                            _CATEGORY_SEVERITY[
                                category
                            ]
                        ),
                        description=(
                            "Language associated "
                            f"with "
                            f"{category.replace('_', ' ')} "
                            "was detected."
                        ),
                        evidence={
                            "matches":
                                matches[:8]
                        },
                    )
                )

        # ---------------------------------------------
        # Combination amplification
        # ---------------------------------------------

        category_count = len(
            evidence
        )

        if category_count >= 3:

            score += min(
                18,
                (category_count - 2) * 6,
            )

        confidence = (
            self._confidence(
                normalized,
                category_count,
            )
        )

        return ModuleAnalysisResult(
            module=self.module_name,
            status=ModuleStatus.COMPLETED,
            score=min(
                round(score, 2),
                100.0,
            ),
            confidence=confidence,
            findings=findings,
            evidence={
                "matched_categories":
                    evidence,
                "text_length":
                    len(normalized),
            },
            metadata={
                "engine":
                    "deterministic_nlp_rules_v1",
                "category_count":
                    category_count,
            },
        )

    # ---------------------------------------------

    @staticmethod
    def _combined_text(
        email: CommonEmailObject,
    ) -> str:

        parts = [
            email.subject or "",
            email.body_text or "",
            strip_html(
                email.body_html
            ),
        ]

        return "\n".join(
            part
            for part in parts
            if part
        )

    # ---------------------------------------------

    @staticmethod
    def _confidence(
        text: str,
        category_count: int,
    ) -> float:

        if not text:
            return 0.2

        length_factor = min(
            len(text) / 1500,
            1.0,
        )

        match_factor = min(
            category_count / 4,
            1.0,
        )

        confidence = min(
            0.45
            + 0.25 * length_factor
            + 0.2 * match_factor,
            0.90,
        )

        return round(
            confidence,
            2,
        )