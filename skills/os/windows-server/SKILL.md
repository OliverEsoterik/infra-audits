---
name: windows-server
description: >
  Full security audit for Windows Server installations. Covers OS patch
  status, security policy, services configuration, firewall rules, event
  log configuration, and registry settings.
domain: os
connectors:
  - collect_win_os_patches.py
  - collect_win_security_policy.py
  - collect_win_services.py
  - collect_win_firewall.py
  - collect_win_eventlog.py
  - collect_win_registry.py
benchmarks:
  - cis_win2022_v1.0
  - nis2_technical
authentication: service-account
transport: winrm
---

# Windows Server Audit Skill

## Overview

Audits Windows Server against CIS Windows Server benchmarks and NIS2 technical
measures. Collects OS-level configuration via WinRM + PowerShell and evaluates
security posture.

## Collection

| Connector | What It Collects | Transport |
|-----------|------------------|-----------|
| `collect_win_os_patches.py` | Installed patches, hotfixes, KBs | WinRM |
| `collect_win_security_policy.py` | Local & domain security policy (password, lockout, audit) | WinRM |
| `collect_win_services.py` | Running services, startup types, non-Microsoft services | WinRM |
| `collect_win_firewall.py` | Windows Firewall rules, profiles (domain/private/public) | WinRM |
| `collect_win_eventlog.py` | Event log configuration (sizes, retention, enabled logs) | WinRM |
| `collect_win_registry.py` | Security-relevant registry keys (LSA, UAC, Cipher suites) | WinRM |

## Evaluation

Evaluates against:
- **CIS Windows Server 2022 v1.0** — 200+ controls across account policies, security options, audit policy, registry
- **NIS2 Technical** — logging, authentication, encryption controls

## Graph

Nodes:
  - name: collect-windows
    trigger: route("audit-planner")
    input: [scoping, credentials]
    role: You collect Windows Server data via WinRM + PowerShell.
    skills: [os/windows-server/connectors]
    output: work/evidence/{client}/windows-server/
    route: always -> evaluate-windows

  - name: evaluate-windows
    trigger: route("collect-windows")
    input: [evidence, benchmarks]
    role: You evaluate Windows Server evidence against CIS and NIS2 benchmarks.
    skills: [core/benchmark-loader]
    output: work/findings/{client}/windows-server/
    route: always -> aggregator