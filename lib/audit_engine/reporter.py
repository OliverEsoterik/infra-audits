"""
Audit Field Kit — Report Generator

Generates professional audit reports from aggregated findings.
Supports Markdown output (with optional PDF conversion).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .base import Finding, AuditSummary


class ReportGenerator:
    """
    Generates audit reports in Markdown format.
    Optionally converts to PDF via weasyprint or pandoc.
    """

    def __init__(self, templates_dir: str = "skills/core/report-compiler/templates"):
        self.templates_dir = Path(templates_dir)

    def generate_markdown(self, findings: list[Finding], summary: AuditSummary,
                          output_path: str, client_name: str = "",
                          benchmarks: list[str] | None = None) -> str:
        """
        Generate a professional audit report in Markdown.

        Args:
            findings: Consolidated findings list
            summary: Audit engagement summary
            output_path: Path to write the report
            client_name: Client organization name
            benchmarks: List of benchmark IDs evaluated

        Returns:
            Path to generated report
        """
        lines = []
        benchmarks = benchmarks or []

        # Title page
        lines.append(f"# IT Security Audit Report — {client_name or summary.client_id}")
        lines.append(f"")
        lines.append(f"| | |")
        lines.append(f"|---|---|")
        lines.append(f"| **Engagement ID** | AUD-{datetime.utcnow().strftime('%Y%m%d-%H%M')} |")
        lines.append(f"| **Audit Date** | {summary.audit_date} |")
        lines.append(f"| **Auditor** | {summary.auditor or 'Audit Field Kit'} |")
        lines.append(f"")
        lines.append("---")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        critical_count = summary.by_severity.get("critical", 0)
        high_count = summary.by_severity.get("high", 0)

        if critical_count > 0:
            lines.append(f"> **⚠️ {critical_count} critical and {high_count} high findings identified.** ")
        else:
            lines.append(f"> **{summary.overall_compliance}% overall compliance.** ")
        lines.append("")
        lines.append(f"This report covers the audit of {len(summary.targets)} target(s) across "
                      f"{len(benchmarks)} benchmark(s).")
        lines.append("")

        # Scope
        lines.append("## Scope & Methodology")
        lines.append("")
        lines.append("### Targets")
        lines.append("")
        for t in summary.targets:
            subs = t.get("sub_targets", [])
            if subs:
                lines.append(f"- **{t['domain']}/{t['target']}**: {', '.join(subs)}")
            else:
                lines.append(f"- **{t['domain']}/{t['target']}**: Full scope")
        lines.append("")
        lines.append("### Benchmarks")
        lines.append("")
        for b in benchmarks:
            lines.append(f"- {b}")
        lines.append("")
        lines.append("### Methodology")
        lines.append("")
        lines.append("Data was collected via automated connector scripts. Evidence was "
                      "evaluated using AI-assisted analysis and deterministic checks "
                      "against the selected benchmarks.")
        lines.append("")

        # Compliance Scores
        lines.append("## Compliance Scores")
        lines.append("")
        lines.append("| Benchmark | Compliant | Non-Compliant | N/A | Score |")
        lines.append("|-----------|-----------|---------------|-----|-------|")
        for bname, bscore in summary.by_benchmark.items():
            lines.append(f"| {bname} | {bscore.get('compliant', 0)} | "
                          f"{bscore.get('non_compliant', 0)} | "
                          f"{bscore.get('na', 0)} | "
                          f"{bscore.get('score', 0)}% |")
        lines.append("")

        # Findings by severity
        severity_order = ["critical", "high", "medium", "low", "info"]
        severity_labels = {
            "critical": "⚠️ Critical Findings",
            "high": "🔴 High Findings",
            "medium": "🟡 Medium Findings",
            "low": "🟢 Low Findings",
            "info": "ℹ️ Informational Findings"
        }

        for sev in severity_order:
            sev_findings = [f for f in findings if f.severity.value == sev]
            if not sev_findings:
                continue

            lines.append(f"## {severity_labels[sev]}")
            lines.append("")

            for f in sev_findings:
                lines.append(f"### {f.control_id} — {f.title}")
                lines.append("")
                lines.append(f"| | |")
                lines.append(f"|---|---|")
                lines.append(f"| **Status** | ❌ Non-Compliant |")
                lines.append(f"| **Severity** | {f.severity.value.upper()} |")
                lines.append(f"| **Target** | {f.domain}/{f.target} |")
                if f.sub_target:
                    lines.append(f"| **Sub-Target** | {f.sub_target} |")
                lines.append(f"| **Benchmark** | {f.benchmark} |")
                lines.append("")
                if f.also_applies_to:
                    others = [f"{a.get('benchmark','')} ({a.get('control_id','')})"
                              for a in f.also_applies_to]
                    lines.append(f"*Also applies to: {', '.join(others)}*")
                    lines.append("")
                lines.append("**Current State:**")
                lines.append(f"{f.evidence_summary}")
                lines.append("")
                lines.append("**Expected State:**")
                lines.append(f"{f.expected_state}")
                lines.append("")
                lines.append("**Remediation:**")
                lines.append("")
                for i, step in enumerate(f.remediation, 1):
                    lines.append(f"{i}. {step}")
                lines.append("")
                lines.append("---")
                lines.append("")

        # Remediation Plan
        lines.append("## Remediation Plan (Priority Order)")
        lines.append("")
        lines.append("| Priority | Finding | Severity | Target |")
        lines.append("|----------|---------|----------|--------|")
        all_findings_sorted = sorted(findings, key=lambda f: [
            "critical", "high", "medium", "low", "info"
        ].index(f.severity.value))
        for i, f in enumerate(all_findings_sorted[:20], 1):  # Top 20
            lines.append(f"| {i} | {f.control_id} — {f.title[:50]} | "
                          f"{f.severity.value.upper()} | {f.target} |")
        lines.append("")

        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path_obj, "w") as f:
            f.write("\n".join(lines))

        return str(output_path_obj)