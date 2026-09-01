#!/usr/bin/env python3
"""List accessible Azure subscriptions and management groups for audit scoping."""

import json
import os
import subprocess
import sys
from pathlib import Path

__skill__ = "azure"
__connector__ = "collect_azure_subscriptions"
__version__ = "1.0.0"
__args__ = [
    {"name": "output_dir", "type": "string", "required": True,
     "description": "Base evidence output directory"}
]
__output__ = {
    "type": "json",
    "path": "work/evidence/{client_id}/azure/subscriptions.json",
    "description": "Azure subscriptions with metadata, management group hierarchy"
}
__benchmarks_served__ = [
    "cis_azure_v2.0",
    "nis2_technical"
]


def collect(output_dir: str, client_id: str, credentials: dict | None = None) -> dict:
    """
    Collect Azure subscription information.

    Uses Azure CLI (az) for authentication and data collection.
    Requires: az login --service-principal or az login interactive first.

    Args:
        output_dir: Base evidence directory
        client_id: Client identifier
        credentials: Optional credentials dict (tenant_id, client_id, client_secret)

    Returns:
        dict: Collection metadata
    """
    results = {
        "connector": __connector__,
        "version": __version__,
        "client_id": client_id,
        "success": True,
        "errors": [],
        "subscriptions": [],
        "management_groups": []
    }

    output_path = Path(output_dir) / client_id / "azure" / "subscriptions.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Authenticate with service principal if credentials provided
        if credentials and "client_id" in credentials:
            tenant_id = credentials.get("tenant_id", "")
            sp_id = credentials.get("client_id", "")
            sp_secret = credentials.get("client_secret", "")
            env = credentials.get("environment", "public")

            # Set Azure environment
            if env != "public":
                os.environ["AZURE_ENVIRONMENT"] = env

            cmd = [
                "az", "login", "--service-principal",
                "--username", sp_id,
                "--password", sp_secret,
                "--tenant", tenant_id,
                "--allow-no-subscriptions"
            ]
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)

        # List subscriptions
        cmd = ["az", "account", "list", "--query", "[].{id:id, name:name, state:state, tenantId:tenantId}"]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)
        subscriptions = json.loads(result.stdout)
        results["subscriptions"] = subscriptions

        # List management groups
        try:
            cmd = ["az", "account", "management-group", "list"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                results["management_groups"] = json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            results["errors"].append(f"Management group list failed: {str(e)}")

    except subprocess.CalledProcessError as e:
        results["success"] = False
        results["errors"].append(f"Azure CLI error: {e.stderr.decode() if hasattr(e.stderr, 'decode') else str(e)}")
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Unexpected error: {str(e)}")

    # Write output
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Collect Azure subscriptions")
    parser.add_argument("--output-dir", default="work/evidence")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--tenant-id", help="Azure tenant ID")
    parser.add_argument("--sp-id", help="Service principal client ID")
    parser.add_argument("--sp-secret", help="Service principal client secret")
    args = parser.parse_args()

    creds = {}
    if args.tenant_id and args.sp_id and args.sp_secret:
        creds = {"tenant_id": args.tenant_id, "client_id": args.sp_id, "client_secret": args.sp_secret}

    result = collect(args.output_dir, args.client_id, creds)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)