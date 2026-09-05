from concurrent.futures import (
    ThreadPoolExecutor,
)

from app.analysis.header_forensics.analyzer import (
    HeaderForensicsAnalyzer,
)

from app.analysis.ioc.extractor import (
    IOCExtractor,
)

from app.analysis.ioc.intelligence import (
    IOCIntelligenceAnalyzer,
)

from app.analysis.nlp.analyzer import (
    NLPAnalyzer,
)

from app.analysis.threat_intelligence.analyzer import (
    ExternalThreatIntelligenceAnalyzer,
)

from app.schemas.analysis_contract import (
    AnalysisJobStatus,
    AnalysisResult,
)

from app.schemas.email import (
    CommonEmailObject,
)


class AnalysisOrchestrator:

    def __init__(
        self,
        header_analyzer:
            HeaderForensicsAnalyzer
            | None = None,

        nlp_analyzer:
            NLPAnalyzer
            | None = None,

        ioc_extractor:
            IOCExtractor
            | None = None,

        ioc_intelligence:
            IOCIntelligenceAnalyzer
            | None = None,

        external_intelligence:
            ExternalThreatIntelligenceAnalyzer
            | None = None,
    ):

        self.header_analyzer = (
            header_analyzer
            or HeaderForensicsAnalyzer()
        )

        self.nlp_analyzer = (
            nlp_analyzer
            or NLPAnalyzer()
        )

        self.ioc_extractor = (
            ioc_extractor
            or IOCExtractor()
        )

        self.ioc_intelligence = (
            ioc_intelligence
            or IOCIntelligenceAnalyzer()
        )

        self.external_intelligence = (
            external_intelligence
            or ExternalThreatIntelligenceAnalyzer()
        )

    def analyze(
        self,
        email: CommonEmailObject,
    ) -> AnalysisResult:

        # -------------------------------------------------
        # Independent email modules execute in parallel
        # -------------------------------------------------

        with ThreadPoolExecutor(
            max_workers=3
        ) as pool:

            header_future = (
                pool.submit(
                    self.header_analyzer.analyze,
                    email,
                )
            )

            nlp_future = (
                pool.submit(
                    self.nlp_analyzer.analyze,
                    email,
                )
            )

            ioc_future = (
                pool.submit(
                    self.ioc_extractor.analyze,
                    email,
                )
            )

            header_result = (
                header_future.result()
            )

            nlp_result = (
                nlp_future.result()
            )

            ioc_result = (
                ioc_future.result()
            )

        # -------------------------------------------------
        # IOC intelligence depends on IOC extraction
        # -------------------------------------------------

        iocs = (
            ioc_result
            .evidence
            .get(
                "iocs",
                {},
            )
        )

        # -------------------------------------------------
        # Static + external IOC intelligence can execute
        # in parallel because both depend only on IOCs.
        # -------------------------------------------------

        with ThreadPoolExecutor(
            max_workers=2
        ) as pool:

            static_future = (
                pool.submit(
                    self.ioc_intelligence
                    .analyze_iocs,
                    iocs,
                )
            )

            external_future = (
                pool.submit(
                    self.external_intelligence
                    .analyze_iocs,
                    iocs,
                )
            )

            static_result = (
                static_future.result()
            )

            external_result = (
                external_future.result()
            )

        # -------------------------------------------------
        # Merge external reputation into the existing
        # IOC intelligence module contract.
        #
        # FinalRiskEngine still sees:
        # "ioc_static_intelligence"
        #
        # Therefore Batch 3 risk weights remain unchanged.
        # -------------------------------------------------

        intelligence_result = (
            self.external_intelligence
            .enrich_static_result(
                static_result,
                external_result,
            )
        )

        # -------------------------------------------------
        # Final Risk Engine intentionally remains outside
        # the orchestrator.
        # -------------------------------------------------

        return AnalysisResult(

            email_id=email.email_id,

            job_status=(
                AnalysisJobStatus.COMPLETED
            ),

            module_results=[
                header_result,
                nlp_result,
                ioc_result,
                intelligence_result,
            ],

            aggregate_score=None,

            verdict=None,

            recommended_action=None,
        )