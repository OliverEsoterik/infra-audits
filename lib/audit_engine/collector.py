"""
Audit Field Kit — Collector Runner

Manages execution of connector scripts (Python, Bash, PowerShell) for
data collection across infrastructure targets.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional
from .base import ConnectorResult


class CollectorRunner:
    """
    Runs connector scripts and collects evidence.

    Supports Python scripts, Bash scripts, PowerShell scripts, and
    direct CLI commands. Handles transport authentication, subprocess
    execution, and output collection.
    """

    def __init__(self, work_dir: str = "work/evidence"):
        self.work_dir = Path(work_dir)

    def run_python_connector(self, script_path: str, client_id: str,
                             targets: list[str],
                             credentials: dict[str, Any] | None = None,
                             extra_args: dict[str, Any] | None = None) -> ConnectorResult:
        """Execute a Python connector script as a subprocess."""
        cmd = [sys.executable, script_path]
        cmd.extend(["--client-id", client_id])
        cmd.extend(["--output-dir", str(self.work_dir)])

        if targets:
            cmd.extend(["--targets"] + targets)

        if extra_args:
            for k, v in extra_args.items():
                cmd.extend([f"--{k}", str(v)])

        env = os.environ.copy()
        if credentials:
            for k, v in credentials.items():
                env[f"AUDIT_CRED_{k.upper()}"] = str(v)

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=600, env=env
            )
            if result.returncode == 0 and result.stdout:
                return ConnectorResult(
                    success=True,
                    data=json.loads(result.stdout),
                    errors=[]
                )
            else:
                return ConnectorResult(
                    success=False,
                    data={},
                    errors=[result.stderr.strip() or f"Exit code: {result.returncode}"]
                )
        except subprocess.TimeoutExpired:
            return ConnectorResult(
                success=False,
                data={},
                errors=["Connector timed out after 600s"]
            )
        except json.JSONDecodeError as e:
            return ConnectorResult(
                success=False,
                data={"raw_output": result.stdout if hasattr(result, 'stdout') else ""},
                errors=[f"Invalid JSON output: {str(e)}"]
            )
        except Exception as e:
            return ConnectorResult(
                success=False,
                data={},
                errors=[f"Unexpected error: {str(e)}"]
            )

    def run_bash_connector(self, script_path: str, client_id: str,
                           credentials: dict[str, Any] | None = None) -> ConnectorResult:
        """Execute a Bash connector script."""
        cmd = ["bash", script_path, "--client-id", client_id,
               "--output-dir", str(self.work_dir)]

        env = os.environ.copy()
        if credentials:
            for k, v in credentials.items():
                env[f"AUDIT_CRED_{k.upper()}"] = str(v)

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=600, env=env
            )
            return ConnectorResult(
                success=result.returncode == 0,
                data={"stdout": result.stdout, "stderr": result.stderr},
                errors=[] if result.returncode == 0 else [result.stderr.strip()]
            )
        except subprocess.TimeoutExpired:
            return ConnectorResult(success=False, errors=["Connector timed out"])
        except Exception as e:
            return ConnectorResult(success=False, errors=[str(e)])

    def find_connector(self, skill_dir: str, connector_name: str) -> str | None:
        """Find a connector script in a skill's connectors directory."""
        candidates = [
            Path(skill_dir) / "connectors" / connector_name,
            Path(skill_dir) / "connectors" / f"{connector_name}.py",
            Path(skill_dir) / "connectors" / f"{connector_name}.sh",
        ]
        for c in candidates:
            if c.exists() and os.access(c, os.X_OK):
                return str(c)
            elif c.exists():
                return str(c)
        return None