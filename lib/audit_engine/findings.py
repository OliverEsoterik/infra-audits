"""
Audit Field Kit — Findings Data Model

Pydantic models for audit findings, aggregation, and report data.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SeverityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class StatusEnum(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non-compliant"
    NOT_APPLICABLE = "not-applicable"
    NOT_TESTED = "not-tested"
    ERROR = "error"


class ControlMapping(BaseModel):
    """Cross-benchmark mapping for a single control."""
    nis2: str = ""
    iso27001: str = ""
    cis: str = ""
    ad: str = ""
    notes: str = ""


class EvidenceRef(BaseModel):
    """Reference to collected evidence."""
    source: str
    connector: str
    timestamp: str = ""
    data_summary: str = ""


class FindingModel(BaseModel):
    """A single audit finding."""
    id: str = Field(default_factory=lambda: f"fnd-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}")
    control_id: str
    benchmark: str
    benchmark_level: int = 1
    title: str
    category: str = ""
    domain: str
    target: str
    sub_target: str = ""
    severity: SeverityEnum
    status: StatusEnum
    evidence_summary: str = ""
    expected_state: str = ""
    remediation: list[str] = Field(default_factory=list)
    estimated_effort: str = ""
    also_applies_to: list[dict] = Field(default_factory=list)
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)


class BenchmarkScore(BaseModel):
    """Compliance score for one benchmark."""
    name: str
    total: int = 0
    compliant: int = 0
    non_compliant: int = 0
    na: int = 0
    not_tested: int = 0

    @property
    def score(self) -> float:
        applicable = self.total - self.na - self.not_tested
        if applicable <= 0:
            return 0.0
        return round((self.compliant / applicable) * 100, 1)


class EngagementSummary(BaseModel):
    """Summary of an audit engagement."""
    client_id: str
    audit_date: str
    auditor: str = ""
    targets: list[dict] = Field(default_factory=list)
    benchmarks_selected: list[str] = Field(default_factory=list)
    total_controls: int = 0
    compliant: int = 0
    non_compliant: int = 0
    not_applicable: int = 0
    not_tested: int = 0
    by_benchmark: dict[str, BenchmarkScore] = Field(default_factory=dict)
    by_severity: dict[str, int] = Field(default_factory=lambda: {
        "critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0
    })

    @property
    def overall_compliance(self) -> float:
        applicable = self.total_controls - self.not_applicable - self.not_tested
        if applicable <= 0:
            return 0.0
        return round((self.compliant / applicable) * 100, 1)


class AggregatedOutput(BaseModel):
    """Complete aggregated output from an audit engagement."""
    engagement: EngagementSummary
    summary: dict
    findings: list[FindingModel]
    excluded_controls: list[dict] = Field(default_factory=list)
    evidence_index: list[dict] = Field(default_factory=list)