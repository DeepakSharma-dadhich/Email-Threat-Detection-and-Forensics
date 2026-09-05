from fastapi import (
    APIRouter,
    Query,
)

from app.analysis.threat_intelligence.service import (
    ThreatIntelligenceService,
)

from app.schemas.threat_intelligence import (
    ThreatIntelligenceResponse,
    ThreatProviderResponse,
)


router = APIRouter()


@router.get(
    "/lookup",
    response_model=ThreatIntelligenceResponse,
)
def lookup_indicator(
    indicator: str = Query(
        min_length=1
    ),
    indicator_type: str = Query(
        pattern="^(domain)$"
    ),
):
    result = (
        ThreatIntelligenceService()
        .analyze(
            indicator=indicator,
            indicator_type=indicator_type,
        )
    )

    return ThreatIntelligenceResponse(
        indicator=result.indicator,
        indicator_type=(
            result.indicator_type
        ),
        aggregate_score=(
            result.aggregate_score
        ),
        providers=[
            ThreatProviderResponse(
                provider=item.provider,
                success=item.success,
                risk_score=item.risk_score,
                malicious=item.malicious,
                findings=item.findings,
                metadata=item.metadata,
                error=item.error,
            )
            for item
            in result.provider_results
        ],
    )