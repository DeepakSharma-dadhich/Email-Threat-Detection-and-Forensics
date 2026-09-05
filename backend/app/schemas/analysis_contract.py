from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AnalysisJobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ModuleStatus(str, Enum):
    NOT_RUN = "not_run"
    COMPLETED = "completed"
    FAILED = "failed"


class FindingSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Finding(BaseModel):
    finding_id: str
    title: str
    category: str
    severity: FindingSeverity
    description: str
    evidence: dict[str, Any] = Field(default_factory=dict)


class ModuleAnalysisResult(BaseModel):
    module: str
    status: ModuleStatus
    score: float | None = Field(default=None, ge=0, le=100)
    confidence: float | None = Field(default=None, ge=0, le=1)
    findings: list[Finding] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalysisResult(BaseModel):
    email_id: UUID
    job_status: AnalysisJobStatus
    module_results: list[ModuleAnalysisResult] = Field(default_factory=list)
    aggregate_score: float | None = Field(default=None, ge=0, le=100)
    verdict: str | None = None
    recommended_action: str | None = None
