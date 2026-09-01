"""
Audit Field Kit — Benchmark Mapper

Maps controls between different benchmarks for deduplication
and compliance correlation.
"""

from __future__ import annotations

from .parser import BenchmarkParser


class BenchmarkMapper:
    """
    Maps controls between different benchmarks.

    When the same underlying control is covered by multiple benchmarks
    (e.g., CIS-1.1.1 and NIS2-TECH-5.1 both require MFA for privileged
    users), the mapper identifies equivalence and prevents double-counting.
    """

    def __init__(self, parser: BenchmarkParser | None = None):
        self.parser = parser or BenchmarkParser()
        self._mappings: list[dict] | None = None

    @property
    def mappings(self) -> list[dict]:
        if self._mappings is None:
            self._mappings = self.parser.load_mappings()
        return self._mappings

    def find_equivalent_controls(self, control_id: str,
                                  source_benchmark: str) -> list[dict]:
        """
        Find equivalent controls in other benchmarks.

        Args:
            control_id: Control identifier (e.g., "CIS-1.1.1")
            source_benchmark: Source benchmark ID (e.g., "cis_azure_v2.0")

        Returns:
            List of equivalent control references:
            [{"benchmark": "nis2_technical", "control_id": "NIS2-TECH-5.1"}, ...]
        """
        equivalents = []

        # Search in field matching the source benchmark
        source_key = None
        for key in ["cis", "nis2", "iso27001", "ad", "bsi"]:
            for m in self.mappings:
                if m.get(key) == control_id:
                    source_key = key
                    break
            if source_key:
                break

        if not source_key:
            return equivalents

        # Find all mappings containing this control_id
        for m in self.mappings:
            if m.get(source_key) == control_id:
                for key, val in m.items():
                    if key != "notes" and key != source_key and val:
                        equivalents.append({
                            "benchmark": key,
                            "control_id": val
                        })

        return equivalents

    def deduplicate_findings(self, findings: list[dict]) -> list[dict]:
        """
        Deduplicate findings by merging equivalent controls.

        Args:
            findings: Raw findings list (may have duplicates)

        Returns:
            Deduplicated findings with merged evidence
        """
        deduped = {}
        for f in findings:
            cid = f.get("control_id", "")
            bench = f.get("benchmark", "")

            # Find equivalent control groups
            equivalents = self.find_equivalent_controls(cid, bench)
            group_key = cid  # Default: group by own control_id

            for eq in equivalents:
                # Use the "primary" control_id if there's a mapping
                for m in self.mappings:
                    if m.get("cis") == cid or m.get("ad") == cid:
                        group_key = m.get("cis") or m.get("ad") or cid
                        break

            if group_key in deduped:
                # Merge evidence
                existing = deduped[group_key]
                existing["also_applies_to"] = existing.get("also_applies_to", [])
                existing["also_applies_to"].append({
                    "benchmark": bench,
                    "control_id": cid
                })
                # Keep highest severity
                severity_order = ["info", "low", "medium", "high", "critical"]
                if severity_order.index(f.get("severity", "medium")) > \
                   severity_order.index(existing.get("severity", "medium")):
                    existing["severity"] = f["severity"]
            else:
                f["also_applies_to"] = []
                deduped[group_key] = f

        return list(deduped.values())