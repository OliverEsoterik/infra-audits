---
name: azure
description: >
  Full infrastructure audit for Microsoft Azure. Covers governance (RBAC,
  Policy, Blueprint), networking (NSG, VNet, Firewall), compute (VMs,
  scale-sets), storage (blob, disk), databases (SQL), and identity (Entra ID).
domain: cloud
connectors:
  - collect_azure_subscriptions.py
  - collect_azure_governance.py
  - collect_azure_network.py
  - collect_azure_storage.py
  - collect_azure_compute.py
  - collect_azure_aad.py
  - collect_azure_sql.py
benchmarks:
  - cis_azure_v2.0
  - nis2_technical
authentication: azure-cli
transport: api
---

# Azure Audit Skill

## Overview

Audits Microsoft Azure cloud environments against CIS Azure Foundations
Benchmark v2.0 and NIS2 technical controls. Collects configuration data
across subscriptions and evaluates governance, networking, compute,
storage, and identity posture.

## Collection

Connector scripts are idempotent and run independently. Each writes JSON
evidence to `work/evidence/<client-id>/azure/<connector-name>.json`.

| Connector | What It Collects | Requires |
|-----------|------------------|----------|
| `collect_azure_subscriptions.py` | List accessible subscriptions, management groups | Reader |
| `collect_azure_governance.py` | RBAC, Policy assignments, Blueprints | Reader + Policy Reader |
| `collect_azure_network.py` | VNets, NSGs, Firewall, VPN, ExpressRoute | Reader |
| `collect_azure_storage.py` | Storage accounts, blob containers, disk encryption | Reader |
| `collect_azure_compute.py` | VMs, scale-sets, disk config, extensions | Reader |
| `collect_azure_aad.py` | Entra ID roles, Conditional Access, PIM, MFA status | Reader + Security Reader |
| `collect_azure_sql.py` | SQL servers, databases, auditing, TDE, firewall rules | Reader |

## Evaluation

Evaluates collected evidence against:
- **CIS Azure Foundations v2.0** — 40+ controls across identity, governance, networking, storage, compute, databases
- **NIS2 Technical** — 10+ controls with cross-mapping to CIS equivalents

## Graph

Nodes:
  - name: collect-azure
    trigger: route("audit-planner")
    input: [scoping, credentials]
    role: You are an Azure infrastructure collector.
    skills: [cloud/azure/connectors]
    output: work/evidence/{client}/azure/
    route: always -> evaluate-azure

  - name: evaluate-azure
    trigger: route("collect-azure")
    input: [evidence, benchmarks]
    role: You are an Azure compliance evaluator. Compare collected evidence
          against loaded benchmarks (CIS, NIS2). Produce structured findings.
    skills: [core/benchmark-loader]
    output: work/findings/{client}/azure/
    route: always -> aggregator