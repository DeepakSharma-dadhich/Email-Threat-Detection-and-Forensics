from abc import ABC, abstractmethod

from app.analysis.threat_intelligence.models import (
    ProviderResult,
)


class ThreatIntelligenceProvider(ABC):

    @abstractmethod
    def supports(
        self,
        indicator_type: str,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def analyze(
        self,
        indicator: str,
        indicator_type: str,
    ) -> ProviderResult:
        raise NotImplementedError