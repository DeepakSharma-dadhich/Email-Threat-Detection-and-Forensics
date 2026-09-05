from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProviderResult:
    provider: str
    indicator: str
    indicator_type: str

    success: bool

    risk_score: int | None = None
    malicious: bool | None = None

    findings: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    error: str | None = None


@dataclass(slots=True)
class ThreatIntelligenceResult:
    indicator: str
    indicator_type: str

    provider_results: list[
        ProviderResult
    ] = field(
        default_factory=list
    )

    aggregate_score: int = 0