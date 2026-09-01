"""
Audit Field Kit — Benchmark Resolver

Resolves benchmark dependencies, control hierarchies, and
determines which controls apply to which targets.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .parser import BenchmarkParser


class BenchmarkResolver:
    """
    Resolves benchmark controls for a given set of targets and benchmarks.
    Determines applicability, resolves dependencies, and handles
    benchmark level selection (CIS Level 1 vs Level 2).
    """

    def __init__(self, parser: BenchmarkParser | None = None):
        self.parser = parser or BenchmarkParser()

    def resolve_controls(self, benchmark_ids: list[str],
                         target_domain: str, target_name: str,
                         levels: list[int] | None = None) -> list[dict]:
        """
        Resolve applicable controls for a target.

        Args:
            benchmark_ids: List of benchmark IDs to check
            target_domain: Domain of target (e.g., "cloud")
            target_name: Name of target (e.g., "azure")
            levels: Specific benchmark levels (e.g., [1] for CIS Level 1 only)

        Returns:
            List of control dicts applicable to this target
        """
        applicable = []

        for bid in benchmark_ids:
            benchmark = self.parser.load_benchmark(bid)
            if not benchmark:
                continue

            meta = benchmark.get("metadata", {})
            b_domain = meta.get("domain", "")
            b_targets = meta.get("targets", [])

            # Check domain and target match
            if b_domain and b_domain != target_domain:
                continue
            if b_targets and target_name not in b_targets:
                continue

            # Filter controls by level if specified
            for control in benchmark.get("controls", []):
                if levels and control.get("level") not in levels:
                    continue
                applicable.append(control)

        return applicable

    def get_connectors_needed(self, controls: list[dict]) -> set[str]:
        """Get the set of connectors needed to evaluate these controls."""
        connectors = set()
        for c in controls:
            connector = c.get("audit", {}).get("connector", "")
            if connector:
                connectors.add(connector)
        return connectors

    def resolve_levels_from_config(self, benchmark_id: str,
                                    config_levels: list[str] | None = None) -> list[int]:
        """
        Resolve benchmark levels from config.

        Args:
            benchmark_id: Benchmark identifier
            config_levels: Levels from config (e.g., ["1"], ["1", "2"])

        Returns:
            List of level integers to evaluate
        """
        if not config_levels:
            return [1]  # Default: Level 1 only

        levels = []
        for l in config_levels:
            try:
                levels.append(int(l))
            except (ValueError, TypeError):
                continue
        return levels or [1]