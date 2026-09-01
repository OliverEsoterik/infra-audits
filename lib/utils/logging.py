"""
Audit Field Kit — Structured Audit Logging

Provides structured logging for audit operations with severity levels
and JSON output for machine parsing.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class AuditLogger:
    """
    Structured logger for audit operations.

    Writes JSON-formatted log entries with timestamps, severity,
    component, and message. Supports both console output and
    file output.
    """

    def __init__(self, name: str = "audit-toolkit",
                 log_file: str | None = None,
                 console: bool = True):
        self.name = name
        self.log_file = Path(log_file) if log_file else None
        self.console = console

        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _log(self, level: str, component: str, message: str,
             extra: dict | None = None):
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "component": component,
            "message": message,
        }
        if extra:
            entry["extra"] = extra

        line = json.dumps(entry)

        if self.console:
            print(line, file=sys.stderr)

        if self.log_file:
            with open(self.log_file, "a") as f:
                f.write(line + "\n")

    def info(self, component: str, message: str, extra: dict | None = None):
        self._log("INFO", component, message, extra)

    def warn(self, component: str, message: str, extra: dict | None = None):
        self._log("WARN", component, message, extra)

    def error(self, component: str, message: str, extra: dict | None = None):
        self._log("ERROR", component, message, extra)

    def debug(self, component: str, message: str, extra: dict | None = None):
        self._log("DEBUG", component, message, extra)

    def collector_start(self, connector: str, targets: list[str]):
        self.info("collector", f"Starting {connector}", {
            "connector": connector,
            "targets": targets,
            "action": "start"
        })

    def collector_end(self, connector: str, success: bool, targets_count: int,
                      errors: list[str] | None = None):
        self.info("collector", f"{'Completed' if success else 'Failed'} {connector}", {
            "connector": connector,
            "success": success,
            "targets_count": targets_count,
            "errors": errors or [],
            "action": "end"
        })

    def finding_generated(self, control_id: str, severity: str,
                          benchmark: str, target: str):
        self.info("evaluator", f"Finding: {control_id} ({severity})", {
            "control_id": control_id,
            "severity": severity,
            "benchmark": benchmark,
            "target": target,
            "action": "finding"
        })