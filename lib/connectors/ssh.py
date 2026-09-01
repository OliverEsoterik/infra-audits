"""
Audit Field Kit — SSH Transport

SSH-based data collection for Linux, ESXi, and network device audits.
Uses asyncssh for asynchronous, parallel SSH connections.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Optional

from .base import Connector, ConnectorResult


class SSHCollector(Connector):
    """
    SSH-based data collector.

    Connects to remote hosts via SSH, executes commands, and collects
    output as structured evidence.
    """

    def __init__(self, key_file: str | None = None,
                 timeout: int = 30, port: int = 22):
        self.key_file = key_file
        self.timeout = timeout
        self.port = port

    def validate_connection(self, credentials: dict[str, Any]) -> bool:
        host = credentials.get("host", "")
        user = credentials.get("username", "")
        key = credentials.get("key_file") or self.key_file
        try:
            # Try a simple SSH connection
            cmd = ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
                   "-o", "StrictHostKeyChecking=accept-new"]
            if key:
                cmd.extend(["-i", key])
            if self.port != 22:
                cmd.extend(["-p", str(self.port)])
            cmd.extend([f"{user}@{host}", "echo", "ok"])
            import subprocess
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False

    def collect(self, targets: list[str], credentials: dict[str, Any],
                output_dir: str, client_id: str) -> ConnectorResult:
        """Collect data from multiple hosts via SSH."""
        results = {"hosts": {}, "errors": []}
        user = credentials.get("username", "root")
        key = credentials.get("key_file") or self.key_file
        commands = credentials.get("commands", ["uname -a"])

        import subprocess
        for host in targets:
            host_data = {"host": host, "commands": {}}
            try:
                for cmd_str in commands:
                    cmd = ["ssh", "-o", "BatchMode=yes",
                           "-o", "StrictHostKeyChecking=accept-new",
                           "-o", f"ConnectTimeout={self.timeout}"]
                    if key:
                        cmd.extend(["-i", key])
                    if self.port != 22:
                        cmd.extend(["-p", str(self.port)])
                    cmd.extend([f"{user}@{host}", cmd_str])

                    result = subprocess.run(cmd, capture_output=True,
                                              text=True, timeout=self.timeout)
                    host_data["commands"][cmd_str[:50]] = {
                        "exit_code": result.returncode,
                        "stdout": result.stdout.strip(),
                        "stderr": result.stderr.strip()
                    }
                results["hosts"][host] = host_data
            except subprocess.TimeoutExpired:
                results["errors"].append(f"{host}: Command timed out")
            except Exception as e:
                results["errors"].append(f"{host}: {str(e)}")

        self.write_output(results, output_dir, client_id, "ssh", "ssh_collection.json")
        return ConnectorResult(
            success=len(results["errors"]) == 0,
            data=results,
            errors=results["errors"]
        )