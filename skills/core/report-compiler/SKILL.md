---
name: report-compiler
description: >
  Generates the final professional audit report from aggregated findings.
  Supports Markdown and PDF output formats. Uses Jinja2 templates for
  structure and AI for executive summary generation.
---

# Report Compiler

## Trigger

After aggregator produces consolidated findings.

## Input

- `work/findings/<client-id>/findings.json` — aggregated findings
- `clients/<client-id>/client-config.yaml` — client metadata
- `skills/core/report-compiler/templates/` — Jinja2 templates

## Behavior

1. Load consolidated findings
2. Load client metadata (company name, engagement details)
3. Compute compliance scores per benchmark
4. Render Jinja2 templates for each report section
5. Generate AI executive summary (from critical + high findings)
6. Assemble final report document

## Output

- `work/reports/<client-id>/audit-report.md` — Markdown report
- `work/reports/<client-id>/audit-report.pdf` — PDF report (optional)
- `work/reports/<client-id>/remediation-plan.md` — standalone remediation plan

## Report Structure

1. **Title Page** — Client name, auditor, date, engagement ID
2. **Executive Summary** — 1-page AI-generated summary for C-level stakeholders
3. **Scope & Methodology** — What was audited, how, against which benchmarks
4. **Overall Compliance** — Per-benchmark scores with visual indicators
5. **Critical Findings** — Everything requiring immediate action
6. **High Findings** — Serious issues requiring prompt attention
7. **Medium Findings** — Recommendations for upcoming sprints
8. **Low Findings** — Informational, no immediate action
9. **Remediation Plan** — Priority-ordered action items with effort estimates
10. **Appendices**
    - A: Evidence Index
    - B: Controls Excluded (with justification)
    - C: Collector Log (success/failure per target)