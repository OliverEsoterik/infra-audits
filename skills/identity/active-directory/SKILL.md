---
name: active-directory
description: >
  Full security audit for Active Directory Domain Services. Covers domain
  health, group membership (privileged groups), GPO analysis, certificate
  services, trusts, federation, and AD audit configuration.
domain: identity
connectors:
  - collect_ad_domains.py
  - collect_ad_gpo.py
  - collect_ad_users_groups.py
  - collect_ad_computers.py
  - collect_ad_certificates.py
  - collect_ad_federation.py
  - collect_ad_trusts.py
benchmarks:
  - ad_best_practice
authentication: service-account
transport: powershell-winrm
---

# Active Directory Audit Skill

## Overview

Audits Active Directory Domain Services against industry best practice
baselines. Covers privileged access management, GPO security configuration,
domain controller health, ADCS (PKI), ADFS, trust relationships, and
audit logging.

## Collection

| Connector | What It Collects | Transport |
|-----------|------------------|-----------|
| `collect_ad_domains.py` | Domain info, forest functional levels, FSMO roles | WinRM + PowerShell |
| `collect_ad_gpo.py` | All GPOs with settings (password, lockout, audit, security options) | WinRM + PowerShell |
| `collect_ad_users_groups.py` | Users, groups, membership (privileged groups) | WinRM + PowerShell |
| `collect_ad_computers.py` | Computer objects, DC health, OS versions | WinRM + PowerShell |
| `collect_ad_certificates.py` | CA hierarchy, certificate templates, CRL, key protection | WinRM + PowerShell |
| `collect_ad_federation.py` | ADFS config, relying parties, claim rules | WinRM + PowerShell |
| `collect_ad_trusts.py` | Domain/forest trusts, SID filtering, trust direction | WinRM + PowerShell |

## Evaluation

Evaluates against:
- **AD Best Practice Baseline** — 15+ controls covering privileged access, GPO security, DC health, PKI

## Graph

Nodes:
  - name: collect-ad
    trigger: route("audit-planner")
    input: [scoping, credentials]
    role: You collect Active Directory data via PowerShell.
    skills: [identity/active-directory/connectors]
    output: work/evidence/{client}/active-directory/
    route: always -> evaluate-ad

  - name: evaluate-ad
    trigger: route("collect-ad")
    input: [evidence, benchmarks]
    role: You evaluate AD evidence against best practice benchmarks.
    skills: [core/benchmark-loader]
    output: work/findings/{client}/active-directory/
    route: always -> aggregator