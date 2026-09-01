"""
Audit Field Kit — Base Classes

Defines the abstract interfaces for audit skills, connectors, and benchmarks.
All audit skills inherit from these base classes.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non-compliant"
    NOT_APPLICABLE = "not-applicable"
    NOT_TESTED = "not-tested"
    ERROR = "error"


class EvaluationType(str, Enum):
    AI = "ai"
    DETERMINISTIC = "deterministic"
    SCRIPT = "script"


class TransportType(str, Enum):
    SSH = "ssh"
    WINRM = "winrm"
    API = "api"
    CLI = "cli"
    SQL = "sql"
    LDAP = "ldap"


@dataclass
class Finding:
    """A single audit finding — result of evaluating one control."""
    id: str
    control_id: str
    benchmark: str
    benchmark_level: int = 1
    title: str = ""
    category: str = ""
    domain: str = ""
    target: str = ""
    sub_target: str = ""
    severity: Severity = Severity.MEDIUM
    status: FindingStatus = FindingStatus.NON_COMPLIANT
    evidence_summary: str = ""
    expected_state: str = ""
    remediation: list[str] = field(default_factory=list)
    estimated_effort: str = ""
    also_applies_to: list[dict] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "control_id": self.control_id,
            "benchmark": self.benchmark,
            "benchmark_level": self.benchmark_level,
            "title": self.title,
            "category": self.category,
            "domain": self.domain,
            "target": self.target,
            "sub_target": self.sub_target,
            "severity": self.severity.value,
            "status": self.status.value,
            "evidence_summary": self.evidence_summary,
            "expected_state": self.expected_state,
            "remediation": self.remediation,
            "estimated_effort": self.estimated_effort,
            "also_applies_to": self.also_applies_to,
            "evidence_refs": self.evidence_refs,
        }


@dataclass
class AuditSummary:
    """Summary of an entire audit engagement."""
    client_id: str
    audit_date: str
    auditor: str = ""
    targets: list[dict] = field(default_factory=list)
    benchmarks_selected: list[str] = field(default_factory=list)
    total_controls: int = 0
    compliant: int = 0
    non_compliant: int = 0
    not_applicable: int = 0
    not_tested: int = 0
    by_benchmark: dict[str, dict] = field(default_factory=dict)
    by_severity: dict[str, int] = field(default_factory=lambda: {
        "critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0
    })

    @property
    def overall_compliance(self) -> float:
        applicable = self.total_controls - self.not_applicable
        if applicable <= 0:
            return 0.0
        return round((self.compliant / applicable) * 100, 1)


@dataclass
class ConnectorResult:
    """Result of running a data collection connector."""
    success: bool = True
    data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    collection_metadata: dict[str, Any] = field(default_factory=dict)


class AuditConnector(ABC):
    """Base class for data collection connectors."""

    @abstractmethod
    def collect(self, targets: list[str], credentials: dict[str, Any],
                output_dir: str, client_id: str) -> ConnectorResult:
        """Collect data from targets and write output."""
        ...

    @abstractmethod
    def validate_connection(self, credentials: dict[str, Any]) -> bool:
        """Test connectivity with given credentials."""
        ...


class AuditSkill(ABC):
    """Base class for an audit skill (one infrastructure domain)."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def domain(self) -> str: ...

    @property
    @abstractmethod
    def connectors(self) -> list[str]: ...

    @property
    @abstractmethod
    def benchmarks(self) -> list[str]: ...

    @abstractmethod
    def collect(self, client_id: str, targets: list[str],
                credentials: dict[str, Any]) -> ConnectorResult:
        """Run all connectors for this skill."""
        ...

    @abstractmethod
    def evaluate(self, client_id: str, benchmark_ids: list[str],
                 evidence_dir: str) -> list[Finding]:
        """Evaluate evidence against specified benchmarks."""
        ...


class AuditReporter(ABC):
    """Base class for audit report generation."""

    @abstractmethod
    def generate(self, findings: list[Finding], summary: AuditSummary,
                 output_dir: str, client_id: str) -> Path:
        """Generate audit report and return path to the report file."""
        ...


def generate_finding_id(prefix: str = "fnd") -> str:
    """Generate a unique finding ID."""
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    import random
    suffix = random.randint(1000, 9999)
    return f"{prefix}-{ts}-{suffix}"