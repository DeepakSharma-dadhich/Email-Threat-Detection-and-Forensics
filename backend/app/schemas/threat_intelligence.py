from typing import Any

from pydantic import BaseModel


class ThreatProviderResponse(BaseModel):
    provider: str
    success: bool

    risk_score: int | None = None
    malicious: bool | None = None

    findings: list[str]
    metadata: dict[str, Any]

    error: str | None = None


class ThreatIntelligenceResponse(BaseModel):
    indicator: str
    indicator_type: str

    aggregate_score: int

    providers: list[
        ThreatProviderResponse
    ]