from abc import ABC, abstractmethod

from app.domain.raw_email import RawEmailEnvelope


class EmailSourceAdapter(ABC):
    @abstractmethod
    def load(self) -> RawEmailEnvelope:
        """Return source-specific data as one canonical raw-email envelope."""
        raise NotImplementedError
