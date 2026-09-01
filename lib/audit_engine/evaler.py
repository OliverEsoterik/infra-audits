"""
Audit Field Kit — Evidence Evaluator

Evaluates collected evidence against benchmark controls.
Supports AI-based evaluation (via prompt templates) and
deterministic evaluation (via Python logic).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from .base import Finding, FindingStatus, Severity, EvaluationType, generate_finding_id


class EvidenceEvaluator:
    """
    Evaluates collected evidence against benchmark controls.

    Supports two evaluation modes:
    - AI: Uses prompt templates + LLM to evaluate complex controls
    - Deterministic: Uses Python logic for clear yes/no checks
    """

    def __init__(self, prompt_templates_dir: str = "prompt-templates"):
        self.templates_dir = Path(prompt_templates_dir)

    def evaluate_control(self, control: dict, evidence: dict,
                         evaluation_type: str) -> Finding | None:
        """
        Evaluate a single control against available evidence.

        Args:
            control: Control definition from benchmark YAML
            evidence: Collected evidence data
            evaluation_type: "ai", "deterministic", or "script"

        Returns:
            Finding object if non-compliant, None if compliant
        """
        if evaluation_type == "deterministic":
            return self._evaluate_deterministic(control, evidence)
        elif evaluation_type == "ai":
            # AI evaluation returns the finding from the LLM evaluation
            return None  # Handled by compliance-evaluator agent
        elif evaluation_type == "script":
            # Handled by dedicated evaluation script
            return None
        return None

    def _evaluate_deterministic(self, control: dict, evidence: dict) -> Finding | None:
        """Evaluate a control using deterministic logic."""
        audit_query = control.get("audit", {}).get("query", "")
        severity = Severity(control.get("severity", "medium"))

        # Extract what we need to check from the query
        # This is simplified - real connectors produce structured evidence
        is_compliant = self._check_deterministic(audit_query, evidence)

        if is_compliant:
            return None

        return Finding(
            id=generate_finding_id(),
            control_id=control.get("id", ""),
            benchmark="",
            title=control.get("title", ""),
            category=control.get("category", ""),
            severity=severity,
            status=FindingStatus.NON_COMPLIANT,
            expected_state=control.get("description", ""),
            remediation=control.get("remediation", "").split("\n"),
        )

    def _check_deterministic(self, query: str, evidence: dict) -> bool:
        """
        Simple deterministic check against structured evidence.

        Override this method in domain-specific evaluators for
        complex logic. This base implementation matches common patterns.
        """
        # Pattern: "check that X == Y" or "ensure X is True"
        equality_match = re.search(r'(\w+)\s*(?:==|is|equals?|be)\s*["\']?(True|true|\w+)["\']?', query)
        if equality_match:
            key, expected = equality_match.group(1), equality_match.group(2)
            actual = evidence.get(key)
            if actual is not None:
                return str(actual).lower() == expected.lower()

        # Pattern: "check if X contains Y"
        contains_match = re.search(r'(\w+)\s+(?:contains?|has|includes?)\s+["\'](.+?)["\']', query)
        if contains_match:
            key, expected = contains_match.group(1), contains_match.group(2)
            actual = evidence.get(key)
            if actual is not None:
                return expected.lower() in str(actual).lower()

        # Default: assume non-compliant if evidence is empty or missing
        if not evidence:
            return False

        return True

    def load_evidence(self, evidence_dir: str, connector_name: str) -> dict:
        """Load evidence from a specific connector's output file."""
        evidence_path = Path(evidence_dir) / f"{connector_name.replace('.py', '')}.json"
        if not evidence_path.exists():
            # Try without extension
            for ext in [".json", ".yaml", ".yml"]:
                alt = evidence_path.with_suffix(ext)
                if alt.exists():
                    evidence_path = alt
                    break
            else:
                return {}

        try:
            with open(evidence_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}