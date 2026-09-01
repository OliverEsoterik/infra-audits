"""
Audit Field Kit — Connector Base & Transport Implementations

Abstract connector base class and concrete transport wrappers
(SSH, WinRM, API, CLI, PowerShell).
"""

from __future__ import annotations

import json
import os
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ConnectorResult:
    """Result of running a data collection connector."""
    success: bool = True
    data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    collection_metadata: dict[str, Any] = field(default_factory=dict)


class Connector(ABC):
    """Base class for all data collection connectors."""

    @abstractmethod
    def collect(self, targets: list[str], credentials: dict[str, Any],
                output_dir: str, client_id: str) -> ConnectorResult:
        """Collect data from targets and write to output_dir."""
        ...

    @abstractmethod
    def validate_connection(self, credentials: dict[str, Any]) -> bool:
        """Test connectivity with given credentials."""
        ...

    def write_output(self, data: dict, output_dir: str, client_id: str,
                     domain: str, filename: str):
        """Write collected data to the evidence directory."""
        path = Path(output_dir) / client_id / domain / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)


class AzureCLIConnector(Connector):
    """Connector using Azure CLI (az) for data collection."""

    def _run_az(self, args: list[str], timeout: int = 60) -> dict:
        """Run an az command and return parsed JSON output."""
        cmd = ["az"] + args
        result = subprocess.run(cmd, capture_output=True, text=True,
                                 timeout=timeout)
        if result.returncode != 0:
            raise RuntimeError(f"az command failed: {result.stderr}")
        return json.loads(result.stdout) if result.stdout else {}

    def validate_connection(self, credentials: dict[str, Any]) -> bool:
        try:
            self._run_az(["account", "show"], timeout=15)
            return True
        except Exception:
            return False

    def collect(self, targets: list[str], credentials: dict[str, Any],
                output_dir: str, client_id: str) -> ConnectorResult:
        # Implementation delegated to specific connector scripts
        raise NotImplementedError("Use domain-specific connector scripts")


class SSHConnector(Connector):
    """Connector using SSH for remote data collection."""

    def validate_connection(self, credentials: dict[str, Any]) -> bool:
        host = credentials.get("host", "")
        user = credentials.get("username", "")
        key = credentials.get("key_file", "")
        try:
            cmd = ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes"]
            if key:
                cmd.extend(["-i", key])
            cmd.extend([f"{user}@{host}", "echo", "ok"])
            subprocess.run(cmd, capture_output=True, timeout=10, check=True)
            return True
        except Exception:
            return False

    def collect(self, targets: list[str], credentials: dict[str, Any],
                output_dir: str, client_id: str) -> ConnectorResult:
        raise NotImplementedError("Use domain-specific connector scripts")


class WinRMConnector(Connector):
    """Connector using WinRM for Windows remote data collection."""

    def validate_connection(self, credentials: dict[str, Any]) -> bool:
        host = credentials.get("host", "")
        user = credentials.get("username", "")
        try:
            cmd = ["python3", "-c", f"""
import winrm
s = winrm.Session('{host}', auth=('{user}','test'))
s.run_cmd('echo ok')
            """]
            subprocess.run(cmd, capture_output=True, timeout=10)
            return True
        except Exception:
            return False

    def collect(self, targets: list[str], credentials: dict[str, Any],
                output_dir: str, client_id: str) -> ConnectorResult:
        raise NotImplementedError("Use domain-specific connector scripts")


class KubectlConnector(Connector):
    """Connector using kubectl for Kubernetes data collection."""

    def __init__(self, kubeconfig: str | None = None):
        self.kubeconfig = kubeconfig

    def validate_connection(self, credentials: dict[str, Any]) -> bool:
        try:
            env = os.environ.copy()
            if self.kubeconfig:
                env["KUBECONFIG"] = self.kubeconfig
            result = subprocess.run(
                ["kubectl", "cluster-info"],
                capture_output=True, timeout=10, env=env
            )
            return result.returncode == 0
        except Exception:
            return False

    def collect(self, targets: list[str], credentials: dict[str, Any],
                output_dir: str, client_id: str) -> ConnectorResult:
        raise NotImplementedError("Use domain-specific connector scripts")