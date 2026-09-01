---
name: finding-aggregator
description: >
  Merges findings from multiple domains and benchmarks into a consolidated
  finding set. Deduplicates cross-benchmark findings, computes aggregate
  severity, and produces compliance scores.
---

# Finding Aggregator

## Trigger

After all evaluators complete for a domain, or after all domains complete.

## Input

- `work/findings/<client-id>/<domain>/<benchmark>.json` — individual findings files
- Cross-benchmark mappings from benchmark-loader

## Behavior

1. **Load all findings** — scan `work/findings/<client-id>/*/*.json`
2. **Group by control mapping** — use cross-benchmark mapping to identify
   controls that are equivalent across benchmarks. If CIS-1.1.1 and NIS2-TECH-5.1
   are mapped, they produce one consolidated finding.
3. **Deduplicate** — if two findings map to the same underlying control,
   merge evidence and keep the highest severity
4. **Compute aggregate severity**:
   - If ANY domain has a critical finding → overall critical
   - Severity per control: max across all instances
5. **Compute compliance scores** per benchmark:
   ```
   score = (compliant_controls / (total_controls - not_applicable)) * 100
   ```
6. **Sort findings** by severity (critical → high → medium → low → info)

## Output

- `work/findings/<client-id>/findings.json` — consolidated findings with:
  - `summary`: overall and per-benchmark compliance scores
  - `findings`: sorted array of all findings
  - `by_severity`: count per severity level