"""
Audit Field Kit — Benchmark Parser

Loads, validates, and resolves benchmark YAML files.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

import yaml


class BenchmarkParser:
    """
    Parses benchmark YAML files from the benchmark registry.
    Supports validation, dependency resolution, and cross-benchmark mapping.
    """

    def __init__(self, benchmarks_dir: str = "skills/core/benchmark-loader/benchmarks"):
        self.benchmarks_dir = Path(benchmarks_dir)

    def load_benchmark(self, benchmark_id: str) -> dict | None:
        """
        Load a specific benchmark by ID.

        Searches all subdirectories for a YAML file whose `benchmark.id`
        matches the requested ID.

        Args:
            benchmark_id: Benchmark ID (e.g., "cis_azure_v2.0")

        Returns:
            Parsed benchmark dict, or None if not found
        """
        for yaml_path in self.benchmarks_dir.rglob("*.yaml"):
            try:
                with open(yaml_path) as f:
                    data = yaml.safe_load(f)
                if data and data.get("benchmark", {}).get("id") == benchmark_id:
                    return data
            except (yaml.YAMLError, IOError):
                continue

        # Also check .yml files
        for yml_path in self.benchmarks_dir.rglob("*.yml"):
            try:
                with open(yml_path) as f:
                    data = yaml.safe_load(f)
                if data and data.get("benchmark", {}).get("id") == benchmark_id:
                    return data
            except (yaml.YAMLError, IOError):
                continue

        return None

    def load_all_benchmarks(self) -> dict[str, dict]:
        """
        Load all benchmarks from the registry.

        Returns:
            Dict mapping benchmark ID -> benchmark data
        """
        benchmarks = {}
        for yaml_path in sorted(self.benchmarks_dir.rglob("*.yaml")):
            try:
                with open(yaml_path) as f:
                    data = yaml.safe_load(f)
                if data and "benchmark" in data:
                    bid = data["benchmark"].get("id")
                    if bid:
                        benchmarks[bid] = data
            except (yaml.YAMLError, IOError):
                continue
        return benchmarks

    def load_mappings(self) -> list[dict]:
        """Load cross-benchmark control mappings."""
        mappings_path = self.benchmarks_dir / "mappings"
        mappings = []
        for f in mappings_path.rglob("*.yaml"):
            try:
                with open(f) as fp:
                    data = yaml.safe_load(fp)
                if data and "mappings" in data:
                    mappings.extend(data["mappings"])
            except (yaml.YAMLError, IOError):
                continue
        return mappings

    def get_controls_for_benchmark(self, benchmark_id: str) -> list[dict]:
        """Get all controls for a specific benchmark."""
        benchmark = self.load_benchmark(benchmark_id)
        if not benchmark:
            return []
        return benchmark.get("controls", [])

    def resolve_skill_benchmarks(self, skill_dir: str) -> list[str]:
        """
        Resolve which benchmarks a skill claims to support.

        Reads the skill's SKILL.md frontmatter for the `benchmarks` field.
        """
        skill_path = Path(skill_dir) / "SKILL.md"
        if not skill_path.exists():
            return []

        with open(skill_path) as f:
            content = f.read()

        # Parse YAML frontmatter (between --- delimiters)
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    if frontmatter:
                        return frontmatter.get("benchmarks", [])
                except yaml.YAMLError:
                    pass

        return []