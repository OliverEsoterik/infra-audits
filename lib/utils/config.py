"""
Audit Field Kit — Configuration Loader

Loads client configurations from the clients/ directory.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

import yaml


class ConfigLoader:
    """
    Loads client configuration files (scoping, benchmarks, credentials).

    Config files live in clients/<client-id>/ directory.
    """

    def __init__(self, clients_dir: str = "clients"):
        self.clients_dir = Path(clients_dir)

    def load_client_config(self, client_id: str) -> dict[str, Any]:
        """
        Load all config files for a client.
        Returns combined config with scoping, benchmarks, and client metadata.
        """
        client_dir = self.clients_dir / client_id
        config = {
            "client_id": client_id,
            "scoping": {},
            "benchmarks": {},
            "client_config": {},
        }

        # Load client-config.yaml
        config_paths = {
            "client_config": "client-config.yaml",
            "scoping": "scoping.yaml",
            "benchmarks": "benchmarks.yaml",
        }

        for key, filename in config_paths.items():
            path = client_dir / filename
            if path.exists():
                try:
                    with open(path) as f:
                        config[key] = yaml.safe_load(f) or {}
                except yaml.YAMLError as e:
                    config[key] = {"error": str(e)}

        return config

    def load_credentials(self, client_id: str) -> dict[str, Any]:
        """
        Load credentials for a client.

        Credentials may come from:
        1. clients/<client-id>/credentials.yaml
        2. Environment variables (AUDIT_CRED_*)
        3. 1Password CLI (op)
        4. Doppler CLI
        """
        credentials = {}

        # Try file-based credentials
        cred_path = self.clients_dir / client_id / "credentials.yaml"
        if cred_path.exists():
            try:
                with open(cred_path) as f:
                    content = f.read()
                    # Substitute env vars
                    import re
                    content = re.sub(
                        r'\$\{(\w+)\}',
                        lambda m: os.environ.get(m.group(1), m.group(0)),
                        content
                    )
                    credentials = yaml.safe_load(content) or {}
            except (yaml.YAMLError, IOError):
                pass

        # Try environment variable credentials
        # AUDIT_CRED_AZURE_TENANT_ID, AUDIT_CRED_AZURE_CLIENT_ID, etc.
        for key, val in os.environ.items():
            if key.startswith("AUDIT_CRED_"):
                parts = key.replace("AUDIT_CRED_", "").lower().split("_", 1)
                if len(parts) == 2:
                    provider, field = parts
                    if provider not in credentials:
                        credentials[provider] = {}
                    if isinstance(credentials[provider], dict):
                        credentials[provider][field] = val

        return credentials

    def list_clients(self) -> list[str]:
        """List all client directories (excluding _template)."""
        clients = []
        for d in self.clients_dir.iterdir():
            if d.is_dir() and d.name != "_template" and not d.name.startswith("."):
                clients.append(d.name)
        return sorted(clients)