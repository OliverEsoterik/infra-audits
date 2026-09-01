#!/usr/bin/env python3
"""
{{CONNECTOR_DESCRIPTION}}

Collects {{TARGET}} data for audit evaluation.
"""

import json
import os
import sys
from pathlib import Path

# Metadata — used by the orchestrator for capability discovery
__skill__ = "{{SKILL_NAME}}"
__connector__ = "{{CONNECTOR_NAME}}"
__version__ = "1.0.0"
__args__ = [
    {
        "name": "targets",
        "type": "list",
        "required": True,
        "description": "List of targets to collect data from"
    }
]
__output__ = {
    "type": "json",
    "path": "work/evidence/{client_id}/{{DOMAIN}}/{{OUTPUT_FILE}}",
    "description": "{{OUTPUT_DESCRIPTION}}"
}
__benchmarks_served__ = [
    "{{BENCHMARK_1}}"
]


def collect(targets: list[str], output_dir: str,
            client_id: str, credentials: dict) -> dict:
    """
    Collect {{TARGET}} data.

    Args:
        targets: List of target identifiers (hosts, subscriptions, etc.)
        output_dir: Base evidence directory
        client_id: Client identifier
        credentials: Authentication dict

    Returns:
        dict: Collection metadata with success, targets, errors
    """
    results = {
        "connector": __connector__,
        "version": __version__,
        "client_id": client_id,
        "targets_attempted": len(targets),
        "targets_succeeded": 0,
        "targets_failed": 0,
        "data": {},
        "errors": []
    }

    output_path = Path(output_dir) / client_id / "{{DOMAIN}}" / "{{OUTPUT_FILE}}"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    for target in targets:
        try:
            # TODO: Implement data collection logic
            target_data = {
                "target": target,
                "status": "collected",
                "items": []
            }
            results["data"][target] = target_data
            results["targets_succeeded"] += 1
        except Exception as e:
            results["errors"].append(f"{target}: {str(e)}")
            results["targets_failed"] += 1

    # Write output
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    return results


if __name__ == "__main__":
    # CLI entry point for standalone usage
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", nargs="+", required=True)
    parser.add_argument("--output-dir", default="work/evidence")
    parser.add_argument("--client-id", required=True)
    args = parser.parse_args()

    creds = {}  # In standalone mode, creds come from env vars or config
    result = collect(args.targets, args.output_dir, args.client_id, creds)
    print(json.dumps(result, indent=2))

    if result["targets_failed"] > 0:
        sys.exit(1)