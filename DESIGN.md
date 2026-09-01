# Audit Field Kit — Technical Design Document

> **Status:** Draft v1  
> **Domain:** IT Audit Automation / Compliance-as-Code  
> **Architecture:** Graph-driven orchestrator + domain skills + pluggable connectors  
> **Repository:** `audits/`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Repository Structure](#3-repository-structure)
4. [Domain Taxonomy](#4-domain-taxonomy)
5. [Skill Architecture](#5-skill-architecture)
6. [Benchmark Framework](#6-benchmark-framework)
7. [Connector Layer](#7-connector-layer)
8. [Report Pipeline](#8-report-pipeline)
9. [Workflow Orchestration](#9-workflow-orchestration)
10. [Extensibility Model](#10-extensibility-model)
11. [Credentials & Security](#11-secrets-and-authentication)
12. [Output Schema](#12-output-schema)
13. [Glossary](#13-glossary)

---

## 1. Executive Summary

The Audit Field Kit is a code-driven IT audit automation system. It enables a solo practitioner or small firm to execute comprehensive infrastructure audits against industry benchmarks (CIS, NIS2, BSI IT-Grundschutz, ISO 27001) with minimal client-side setup.

**Core workflow:**

1. Client provides a service account / credentials + scope description ("audit our 20 Windows Servers 2022 against CIS Level 1 and NIS2")
2. Auditor runs a single orchestrator invocation
3. The system discovers client infrastructure, collects evidence, evaluates against selected benchmarks, generates findings with severity ratings and remediation guidance, and produces a professional audit report

**Key design properties:**

- **Extensible by domain:** Each infrastructure category (cloud, virtualization, database, identity, container, network) is a self-contained skill module
- **Benchmark decoupled from skill:** Benchmarks are structured data files — adding CIS Azure Foundations v2.0 does not require changing any skill code
- **Connector abstraction:** Data collection scripts (Python/Bash/PowerShell) are separate from evaluation logic — swap one without touching the other
- **Orchestrator-driven:** The graph engine routes work through parallel collection → evaluation → synthesis → report generation
- **AI + deterministic hybrid:** Scripts collect raw data; AI agents evaluate evidence against benchmarks; deterministic code handles formatting, deduplication, and severity aggregation

---

## 2. Architecture Overview

```

                     ┌─────────────────────────────────────┐
                     │           ORCHESTRATOR              │
                     │    (graph-engine, state router)      │
                     │    work/graph/state.json             │
                     └──────┬──────┬──────┬──────┬─────────┘
                            │      │      │      │
              ┌─────────────┘      │      │      └─────────────┐
              ▼                    ▼      ▼                    ▼
     ┌─────────────────┐   ┌──────────┐ ┌──────────┐   ┌──────────────┐
     │  DECOMPOSER     │   │ AUDIT    │ │BENCHMARK │   │  REPORT      │
     │  (task planner) │   │ PLANNER  │ │LOADER    │   │  GENERATOR   │
     └─────────────────┘   └──────────┘ └──────────┘   └──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │     PARALLEL COLLECTORS      │
                    │  (per domain / per target)    │
                    └──────┬──────┬──────┬─────────┘
                           │      │      │
                           ▼      ▼      ▼
                    ┌─────────────────────────────┐
                    │     EVALUATION ENGINE         │
                    │  (skill-based, per control)   │
                    └──────┬──────┬──────┬─────────┘
                           │      │      │
                           ▼      ▼      ▼
                    ┌─────────────────────────────┐
                    │     FINDING AGGREGATOR        │
                    │  (dedup, severity, priority)  │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │     REPORT COMPILER           │
                    │  (executive summary →        │
                    │   detailed findings →        │
                    │   remediation plan)          │
                    └─────────────────────────────┘
```

### Layers

| Layer | Responsibility | Tooling |
|-------|---------------|---------|
| **Orchestration** | Task decomposition, topology design, parallel execution, state routing | Graph-engine (orchestrator skill) |
| **Collection** | Connect to infrastructure, gather raw configuration/state data | Python scripts, Bash, PowerShell, API calls |
| **Evaluation** | Compare collected evidence against benchmark controls, produce findings | AI agents (SKILL.md-driven), structured output |
| **Aggregation** | Merge findings across domains, deduplicate, compute severity, correlate | Deterministic Python / AI synthesis |
| **Reporting** | Generate professional audit report (PDF, HTML, Markdown) | LaTeX skill, Markdown, Jinja2 templates |

---

## 3. Repository Structure

```
audits/
├── IDEA.md                          # Original concept document
├── README.md                        # Project overview, quick-start
├── DESIGN.md                        # This document
├── CHANGELOG.md                     # Version history
├── LICENSE                          # Licensing
│
├── .github/
│   └── workflows/
│       └── test.yml                 # CI: validate skill structure, schemas
│
├── .gitignore
├── .pi/
│   └── settings.json                # Pi agent settings
│
├── agents/                          # Pre-configured agent profiles
│   ├── audit-planner.md             # Architects the audit plan from client request
│   ├── evidence-collector.md        # Generic evidence collection agent
│   ├── compliance-evaluator.md      # Evaluates evidence against benchmarks
│   ├── report-writer.md             # Generates final audit report
│   └── kvalitetsledare.md           # Swedish-language report specialist
│
├── skills/                          # Audit domain skills (extensible)
│   │
│   ├── _templates/                  # Templates for new skills & connectors
│   │   ├── SKILL.skel.md            # Skeleton for a new audit skill
│   │   ├── benchmark.skel.yaml      # Skeleton for a new benchmark file
│   │   └── connector.skel.py        # Skeleton for a new data collector
│   │
│   ├── core/                        # Core skills — always loaded
│   │   ├── orchestrator/
│   │   │   ├── SKILL.md             # Graph-engine orchestrator (reuses fleet pattern)
│   │   │   ├── schema.json          # State schema
│   │   │   └── examples/            # Topology proposals
│   │   ├── decomposer/
│   │   │   └── SKILL.md             # Task decomposition & skill matching
│   │   ├── benchmark-loader/
│   │   │   ├── SKILL.md             # Loads and resolves benchmark files
│   │   │   └── benchmarks/          # Central benchmark registry
│   │   │       ├── cis/             # CIS Benchmarks
│   │   │       │   ├── cis_azure_v2.0.yaml
│   │   │       │   ├── cis_aws_v1.5.yaml
│   │   │       │   ├── cis_k8s_v1.24.yaml
│   │   │       │   ├── cis_docker_v1.6.yaml
│   │   │       │   ├── cis_win2019_v2.0.yaml
│   │   │       │   ├── cis_win2022_v1.0.yaml
│   │   │       │   ├── cis_ubuntu_v2.0.yaml
│   │   │       │   └── cis_rhel8_v2.0.yaml
│   │   │       ├── nis2/            # NIS2 directive controls
│   │   │       │   ├── nis2_technical.yaml
│   │   │       │   └── nis2_organizational.yaml
│   │   │       ├── bsi/             # BSI IT-Grundschutz
│   │   │       │   ├── bsi_compendium.yaml
│   │   │       │   └── bsi_cloud.yaml
│   │   │       ├── iso27001/        # ISO 27001:2022 Annex A
│   │   │       │   └── iso27001_2022_annex_a.yaml
│   │   │       ├── society/         # Swedish MSB / SPF / other frameworks
│   │   │       │   └── msb_framework.yaml
│   │   │       ├── best-practice/   # Industry best practice benchmarks (no formal framework)
│   │   │       │   ├── ad_best_practice.yaml
│   │   │       │   ├── vcenter_best_practice.yaml
│   │   │       │   └── oracle_dba_best_practice.yaml
│   │   │       └── custom/          # Client-specific benchmarks (generated per engagement)
│   │   │           └── README.md
│   │   ├── finding-aggregator/
│   │   │   └── SKILL.md             # Dedup, severity correlation, priority ordering
│   │   └── report-compiler/
│   │       ├── SKILL.md             # Fuses findings into audit report
│   │       └── templates/           # Report templates
│   │           ├── executive-summary.md.j2
│   │           ├── detailed-findings.md.j2
│   │           └── remediation-plan.md.j2
│   │
│   ├── cloud/                       # Cloud infrastructure audits
│   │   ├── azure/
│   │   │   ├── SKILL.md             # Azure audit skill definition
│   │   │   ├── connectors/
│   │   │   │   ├── collect_azure_subscriptions.py
│   │   │   │   ├── collect_azure_governance.py   # RBAC, policies, blueprints
│   │   │   │   ├── collect_azure_network.py      # NSGs, VNets, firewall
│   │   │   │   ├── collect_azure_storage.py
│   │   │   │   ├── collect_azure_compute.py      # VMs, scale sets
│   │   │   │   ├── collect_azure_aad.py          # Identity, conditional access
│   │   │   │   └── collect_azure_sql.py
│   │   │   └── benchmarks/          # Override / supplement global benchmarks
│   │   │       └── README.md
│   │   ├── aws/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_aws_org.py
│   │   │       ├── collect_aws_iam.py
│   │   │       ├── collect_aws_s3.py
│   │   │       ├── collect_aws_network.py
│   │   │       └── collect_aws_ec2.py
│   │   └── gcp/
│   │       ├── SKILL.md
│   │       └── connectors/
│   │           ├── collect_gcp_org.py
│   │           ├── collect_gcp_iam.py
│   │           ├── collect_gcp_gke.py
│   │           └── collect_gcp_storage.py
│   │
│   ├── virtualization/              # Virtualization platform audits
│   │   ├── vmware-vcenter/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_vcenter_clusters.py
│   │   │       ├── collect_vcenter_hosts.py
│   │   │       ├── collect_vcenter_vms.py
│   │   │       ├── collect_vcenter_networks.py
│   │   │       ├── collect_vcenter_storage.py
│   │   │       └── collect_vcenter_ha_drs.py
│   │   └── hyper-v/
│   │       ├── SKILL.md
│   │       └── connectors/
│   │           └── collect_hyperv_hosts.py
│   │
│   ├── container/                   # Container & orchestration audits
│   │   ├── kubernetes/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_k8s_policies.py   # OPA/Gatekeeper, Kyverno, PSA
│   │   │       ├── collect_k8s_network.py    # NetworkPolicies, CNI config
│   │   │       ├── collect_k8s_rbac.py
│   │   │       ├── collect_k8s_security.py   # PodSecurity, seccomp, apparmor
│   │   │       ├── collect_k8s_storage.py    # SC, PVC, CSI
│   │   │       └── collect_k8s_workloads.py  # Deployments, resources, HPAs
│   │   ├── docker/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_docker_daemon.py
│   │   │       └── collect_docker_images.py  # Image scanning, history
│   │   └── helm/
│   │       ├── SKILL.md
│   │       └── connectors/
│   │           └── collect_helm_releases.py
│   │
│   ├── identity/                    # Identity and access management audits
│   │   ├── active-directory/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_ad_domains.py
│   │   │       ├── collect_ad_gpo.py
│   │   │       ├── collect_ad_users_groups.py
│   │   │       ├── collect_ad_computers.py
│   │   │       ├── collect_ad_certificates.py  # ADCS / PKI
│   │   │       ├── collect_ad_federation.py    # ADFS
│   │   │       └── collect_ad_trusts.py
│   │   ├── entra-id/
│   │   │   ├── SKILL.md             # Microsoft Entra ID (formerly Azure AD)
│   │   │   └── connectors/
│   │   │       ├── collect_entra_tenants.py
│   │   │       ├── collect_entra_conditional_access.py
│   │   │       └── collect_entra_app_registrations.py
│   │   └── linux-sssd/
│   │       ├── SKILL.md
│   │       └── connectors/
│   │           └── collect_sssd_config.py
│   │
│   ├── database/                    # Database audits
│   │   ├── oracle/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_oracle_instances.py
│   │   │       ├── collect_oracle_security.py  # Users, roles, privileges
│   │   │       ├── collect_oracle_audit.py     # Unified auditing
│   │   │       ├── collect_oracle_network.py   # Listener, TCPS
│   │   │       └── collect_oracle_backup.py
│   │   ├── sql-server/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_mssql_instances.py
│   │   │       ├── collect_mssql_security.py
│   │   │       └── collect_mssql_audit.py
│   │   ├── postgresql/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_pg_instances.py
│   │   │       └── collect_pg_security.py
│   │   └── mongodb/
│   │       ├── SKILL.md
│   │       └── connectors/
│   │           ├── collect_mongo_instances.py
│   │           └── collect_mongo_security.py
│   │
│   ├── os/                         # Operating system audits
│   │   ├── windows-server/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_win_os_patches.py
│   │   │       ├── collect_win_security_policy.py
│   │   │       ├── collect_win_services.py
│   │   │       ├── collect_win_firewall.py
│   │   │       ├── collect_win_eventlog.py
│   │   │       └── collect_win_registry.py
│   │   ├── linux/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_linux_os_release.py
│   │   │       ├── collect_linux_kernel.py
│   │   │       ├── collect_linux_packages.py
│   │   │       ├── collect_linux_services.py
│   │   │       ├── collect_linux_firewall.py
│   │   │       ├── collect_linux_pam.py
│   │   │       ├── collect_linux_auditd.py
│   │   │       ├── collect_linux_ssh.py
│   │   │       └── collect_linux_file_permissions.py
│   │   └── esxi/
│   │       ├── SKILL.md
│   │       └── connectors/
│   │           ├── collect_esxi_config.py
│   │           └── collect_esxi_network.py
│   │
│   ├── network/                    # Network infrastructure audits
│   │   ├── firewall/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_fw_rules.py
│   │   │       └── collect_fw_nat.py
│   │   ├── load-balancer/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       └── collect_lb_config.py
│   │   └── dns/
│   │       ├── SKILL.md
│   │       └── connectors/
│   │           ├── collect_dns_zones.py
│   │           └── collect_dns_security.py
│   │
│   ├── iac/                        # Infrastructure-as-Code audits
│   │   ├── terraform/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_tf_state.py
│   │   │       ├── scan_tf_security.py   # tfsec / checkov integration
│   │   │       └── scan_tf_compliance.py # Sentinel / OPA policies
│   │   └── ansible/
│   │       ├── SKILL.md
│   │       └── connectors/
│   │           ├── collect_ansible_inventory.py
│   │           └── scan_ansible_playbooks.py
│   │
│   ├── backup/                     # Backup & DR audits
│   │   ├── veeam/
│   │   │   ├── SKILL.md
│   │   │   └── connectors/
│   │   │       ├── collect_veeam_jobs.py
│   │   │       └── collect_veeam_repositories.py
│   │   └── general-backup/
│   │       ├── SKILL.md
│   │       └── connectors/
│   │           └── collect_backup_policies.py
│   │
│   └── cross-cutting/              # Cross-cutting concern audits
│       ├── network-segmentation/
│       │   ├── SKILL.md
│       │   └── connectors/
│       │       └── collect_segmentation.py
│       ├── certificate-management/
│       │   ├── SKILL.md
│       │   └── connectors/
│       │       └── collect_certificates.py
│       ├── logging-monitoring/
│       │   ├── SKILL.md
│       │   └── connectors/
│       │       └── collect_logging_config.py
│       ├── backup-dr/
│       │   ├── SKILL.md
│       │   └── connectors/
│       │       └── collect_dr_config.py
│       └── patch-management/
│           ├── SKILL.md
│           └── connectors/
│               └── collect_patch_status.py
│
├── lib/                            # Shared library / framework code
│   ├── __init__.py
│   ├── audit_engine/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base classes: AuditSkill, Connector, Benchmark
│   │   ├── collector.py            # Collector runner (subprocess, SSH, API)
│   │   ├── evaler.py               # Evidence evaluator (AI + deterministic)
│   │   ├── findings.py             # Finding data model (Pydantic)
│   │   └── reporter.py            # Report generation utilities
│   ├── benchmark/
│   │   ├── __init__.py
│   │   ├── parser.py               # Parse benchmark YAML files
│   │   ├── resolver.py             # Resolve control dependencies, hierarchies
│   │   └── mapper.py               # Map controls to collection targets
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract connector base class
│   │   ├── ssh.py                  # SSH transport
│   │   ├── winrm.py                # WinRM transport (Windows remote)
│   │   ├── powershell.py           # PowerShell execution helper
│   │   ├── azure_cli.py            # Azure CLI wrapper
│   │   ├── aws_cli.py              # AWS CLI wrapper
│   │   ├── gcloud_cli.py           # GCloud CLI wrapper
│   │   ├── kubectl.py              # kubectl wrapper
│   │   ├── vsphere.py              # vSphere API wrapper (pyvmomi)
│   │   ├── graph.py                # Microsoft Graph API wrapper
│   │   └── ldap.py                 # LDAP query wrapper
│   ├── output/
│   │   ├── __init__.py
│   │   ├── schema.py               # Unified output schemas (Pydantic)
│   │   ├── findings.proto          # (future) Protobuf schema
│   │   └── markdown.py             # Markdown report helpers
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration loading
│   │   ├── logging.py              # Structured audit logging
│   │   ├── version.py             # Version comparison helpers
│   │   └── datetime.py            # Date/time utilities
│   └── requirements.txt            # Python dependencies
│
├── prompt-templates/               # Prompt templates for AI-driven evaluation
│   ├── evaluate-control.md.j2      # Template: evaluate one control against evidence
│   ├── generate-finding.md.j2      # Template: generate finding from control mismatch
│   ├── summarize-findings.md.j2    # Template: executive summary of findings
│   ├── compliance-gap-analysis.md.j2
│   └── remediation-advice.md.j2    # Template: generate remediation steps
│
├── clients/                        # Per-client configuration (gitignored normally)
│   └── _template/
│       ├── client-config.yaml      # Client metadata, compliance scope
│       ├── credentials.yaml        # Service account config (gitignored after fill)
│       ├── scoping.yaml            # What to audit: targets, exclusions
│       └── benchmarks.yaml         # Which benchmarks to evaluate against
│
├── scripts/                        # Utility scripts
│   ├── init-client.sh              # Bootstrap a client directory
│   ├── run-audit.sh                # Single command to run full audit
│   ├── validate-schemas.sh         # Validate all YAML schemas
│   ├── list-skills.sh              # List all available audit skills
│   └── install-deps.sh             # Install Python dependencies
│
└── work/                           # Runtime workspace (gitignored)
    ├── graph/                      # Orchestrator state
    │   ├── state.json
    │   ├── errors.log
    │   └── output/
    ├── evidence/                   # Collected evidence (raw data)
    │   └── <client-id>/
    │       ├── azure/
    │       ├── k8s/
    │       └── windows/
    ├── findings/                   # Evaluated findings (structured)
    │   └── <client-id>/
    │       ├── findings.json
    │       └── findings-summary.yaml
    └── reports/                    # Generated reports
        └── <client-id>/
            ├── audit-report.md
            ├── audit-report.pdf
            └── remediation-plan.md
```

### Directory Justifications

| Directory | Why |
|-----------|-----|
| `skills/core/` | Orchestrator, benchmark-loader, finding-aggregator, report-compiler — these run on every audit regardless of target |
| `skills/<domain>/` | Each infrastructure domain gets its own directory. Self-contained: SKILL.md describes what it audits; `connectors/` has the data collectors; `benchmarks/` has domain-specific benchmark overrides |
| `lib/` | Shared Python code — connector transport layer (SSH, WinRM, API wrappers), benchmark parser, output schemas. Avoids duplicating transport code across 20 connector scripts |
| `prompt-templates/` | Jinja2 templates for the AI evaluation prompts. Keeps prompt engineering separate from skill logic. Enables non-developers to tune prompts without touching Python code |
| `clients/` | Per-client config is its own directory with scoping, credentials, and selected benchmarks. The `_template/` is the bootstrap template. The whole `clients/` dir can be .gitignore'd or stored in a separate encrypted repo |
| `work/` | Runtime output — evidence, findings, reports. Always gitignored. Each client run creates a subdirectory under `evidence/`, `findings/`, `reports/` |
| `scripts/` | Shell scripts for common operations. Low ceremony, high discoverability for the auditor |

---

## 4. Domain Taxonomy

Infrastructure audit targets follow a two-level taxonomy:

```
Domain :: Target :: Sub-Target [optional]
```

| Domain | Targets | Example Sub-Targets |
|--------|---------|-------------------|
| `cloud` | `azure`, `aws`, `gcp` | Subscriptions, accounts, projects |
| `virtualization` | `vmware-vcenter`, `hyper-v` | Clusters, hosts, datastores |
| `container` | `kubernetes`, `docker`, `helm` | Clusters, namespaces, workloads |
| `identity` | `active-directory`, `entra-id`, `linux-sssd` | Domains, forests, tenants |
| `database` | `oracle`, `sql-server`, `postgresql`, `mongodb` | Instances, schemas, listeners |
| `os` | `windows-server`, `linux`, `esxi` | Versions, roles, patch levels |
| `network` | `firewall`, `load-balancer`, `dns` | Zones, rules, services |
| `iac` | `terraform`, `ansible` | Workspaces, states, modules |
| `backup` | `veeam`, `general-backup` | Jobs, repositories, policies |
| `cross-cutting` | `network-segmentation`, `certificate-management`, `logging-monitoring`, `backup-dr`, `patch-management` | Aggregated across all targets |

**Scoping resolution:** When the auditor specifies "audit our Azure" or "audit our 20 Windows Servers", the scoping file maps these to the taxonomy. For example:

```yaml
# clients/acme-corp/scoping.yaml
targets:
  - domain: cloud
    target: azure
    sub_targets:
      - "subscription:prod-eu-west-1"
      - "subscription:prod-us-east-1"
  - domain: os
    target: windows-server
    sub_targets:
      - "host:dc-01.corp.acme.com"
      - "host:dc-02.corp.acme.com"
      - "host:sql-01.corp.acme.com"
      - "host:app-01.corp.acme.com"       # ... 16 more host entries
  - domain: identity
    target: active-directory
    sub_targets:
      - "domain:acme.corp"
```

---

## 5. Skill Architecture

Every audit skill follows the same contract: a `SKILL.md` file with structured frontmatter and sections.

### SKILL.md Template

```markdown
---
name: azure
description: >
  Full infrastructure audit for Microsoft Azure.
  Covers governance (RBAC, Policy), networking (NSG, VNet, Firewall),
  compute (VMs, scale-sets), storage (blob, disk, SQL), and identity (Entra ID).
domain: cloud
connectors:
  - collect_azure_subscriptions.py   # Required: list all accessible subscriptions
  - collect_azure_governance.py      # Required: RBAC, Policy, Blueprints
  - collect_azure_network.py         # Optional: only if networking exists
  - collect_azure_storage.py         # Optional: only if storage exists
  - collect_azure_compute.py         # Optional: only if compute exists
  - collect_azure_aad.py             # Optional: only if Entra ID access
  - collect_azure_sql.py             # Optional: only if Azure SQL exists
benchmarks:
  - cis_azure_v2.0
  - nis2_technical
  - bsi_cloud
authentication: azure-cli  # How the connector authenticates
transport: api             # API-based (vs SSH, WinRM, GraphQL)
---

# Azure Audit Skill

## Overview

This skill audits Microsoft Azure cloud environments against CIS Azure Foundations,
NIS2 technical controls, and BSI Cloud Computing requirements. It collects
configuration data across subscriptions, evaluates governance posture, network
security, compute hardening, storage encryption, and identity management.

## Collection

Each connector script writes JSON to `work/evidence/<client-id>/azure/<script-name>.json`.
Connectors are idempotent and can run independently.

## Evaluation

After collection, each benchmark's controls are evaluated against the evidence.
Controls that fail produce a `Finding` with:
- `control_id`: e.g., CIS-1.1.1, NIS2-TECH-5.1
- `severity`: critical | high | medium | low | info
- `status`: compliant | non-compliant | not-applicable | not-tested
- `evidence`: specific data points that triggered the finding
- `remediation`: actionable steps to remediate

## Graph

Nodes:
  - name: collect-azure
    trigger: route("audit-planner")
    input: [scoping]
    role: You are an Azure infrastructure collector.
    skills: [azure/connectors]
    output: work/evidence/{client}/azure/
    route: always -> evaluate-azure

  - name: evaluate-azure
    trigger: route("collect-azure")
    input: [evidence, benchmarks]
    role: You are an Azure compliance evaluator. Compare collected evidence
          against loaded benchmarks (CIS, NIS2, BSI). Produce structured findings.
    skills: [core/benchmark-loader]
    output: work/findings/{client}/azure/
    route: always -> aggregator
```

### Connector Contract

Every connector script follows the same contract:

```python
#!/usr/bin/env python3
"""Collect Azure governance data (RBAC, Policy, Blueprints)."""

# Metadata — used by the orchestrator for capability discovery
__skill__ = "azure"
__connector__ = "collect_azure_governance"
__version__ = "1.0.0"
__args__ = [
    {"name": "subscriptions", "type": "list", "required": True,
     "description": "List of subscription IDs to audit"}
]
__output__ = {
    "type": "json",
    "path": "work/evidence/{client_id}/azure/governance.json",
    "description": "Azure RBAC role assignments, Policy assignments, Blueprint definitions"
}
__benchmarks_served__ = [
    "cis_azure_v2.0",
    "nis2_technical"
]

def collect(subscriptions: list[str], output_dir: str,
            client_id: str, credentials: dict) -> dict:
    """
    Collect governance data.

    Args:
        subscriptions: List of Azure subscription IDs
        output_dir: Base evidence directory
        client_id: Client identifier
        credentials: Authentication dict (service principal or managed identity)

    Returns:
        dict: Collection metadata (success, targets, errors)
    """
    ...
```

### Skill-to-Benchmark Mapping

Not every skill evaluates against every benchmark. The mapping is:

```yaml
# skills/azure/SKILL.md frontmatter
benchmarks:
  - cis_azure_v2.0
  - nis2_technical
  - bsi_cloud
```

When the auditor selects benchmarks in the client config, the benchmark-loader resolves which skills need to run:

```yaml
# clients/acme-corp/benchmarks.yaml
selected:
  - cis_azure_v2.0
  - nis2_technical
  - best_practice_ad

# Resolved skills needed:
# - azure        (because cis_azure_v2.0 + nis2_technical)
# - active-directory (because best_practice_ad)
```

Skills not required for any selected benchmark are skipped, saving collection time.

---

## 6. Benchmark Framework

Benchmarks are the evaluation criteria. They are structured YAML files, not code.

### Benchmark File Structure

```yaml
# skills/core/benchmark-loader/benchmarks/cis/cis_azure_v2.0.yaml
---
benchmark:
  id: cis_azure_v2.0
  name: CIS Microsoft Azure Foundations Benchmark
  version: "2.0.0"
  date: "2024-10-15"
  source: https://www.cisecurity.org/benchmark/azure
  publisher: Center for Internet Security

metadata:
  domain: cloud
  targets: [azure]
  levels:
    - level: 1
      description: Basic security (recommended for all environments)
    - level: 2
      description: Defense-in-depth (high-security environments)

controls:
  - id: CIS-1.1.1
    title: Ensure that multi-factor authentication is enabled for all privileged users
    level: 1
    category: Identity and Access Management
    description: >
      Require MFA for all users who have administrative roles in Entra ID.
    audit:
      # How to audit this control — maps to a connector + evaluation logic
      connector: collect_azure_aad.py
      evaluation_type: ai        # ai | deterministic | script
      query: >
        From the collected Entra ID directory roles data, check if MFA
        is enforced for every user with a privileged role assignment.
    severity: critical
    mapping:
      nis2: NIS2-TECH-5.1
      iso27001: A.9.4.2
    remediation: >
      1. Navigate to Entra ID > Security > Conditional Access
      2. Create a policy targeting all users with admin roles
      3. Require MFA for all cloud app access
      4. Test with a pilot group before enforcing

  - id: CIS-1.1.2
    title: Ensure that multi-factor authentication is enabled for all non-privileged users
    level: 2
    category: Identity and Access Management
    description: >
      Extend MFA requirements to all users, not just privileged ones.
    audit:
      connector: collect_azure_aad.py
      evaluation_type: ai
      query: >
        From the collected Conditional Access policies, verify there is
        a policy requiring MFA for all users, or a mechanism that covers
        non-privileged users.
    severity: high
    mapping:
      nis2: NIS2-TECH-5.2
      iso27001: A.9.4.2
    remediation: >
      1. Extend the Conditional Access policy from CIS-1.1.1 to include
         all users, or create a separate policy for non-privileged users.
```

### Evaluation Types

| Type | Description | When to Use |
|------|-------------|-------------|
| `ai` | The compliance-evaluator agent interprets evidence and benchmark query to produce a finding | Complex, contextual evaluations (e.g., "Is RBAC correctly scoped?") |
| `deterministic` | A Python script compares evidence against a set of rules | Clear yes/no checks (e.g., "Is TLS 1.2 enforced?") |
| `script` | A standalone script that does both collection and evaluation | When the evaluation logic is too complex for AI (e.g., parsing 10,000 firewall rules) |

### Cross-Benchmark Mapping

Controls in different benchmarks that cover the same requirement are mapped. This enables:

1. **Deduplication:** One finding can satisfy multiple benchmarks
2. **Gap analysis:** If CIS covers control X but NIS2 doesn't, that's a gap note

```yaml
# skills/core/benchmark-loader/benchmarks/mappings/cis-nis2.yaml
mappings:
  - cis: CIS-1.1.1
    nis2: NIS2-TECH-5.1
    iso27001: A.9.4.2
    notes: MFA for privileged users — equivalent controls
  - cis: CIS-2.1.1
    nis2: NIS2-TECH-3.2
    iso27001: A.12.6.1
    notes: >
      CIS requires specific Azure Policy rules while NIS2 is technology-agnostic.
      Evaluation may differ — CIS checks Policy assignment, NIS2 checks
      whether *any* vulnerability management process exists.
```

### Benchmark Registry

All benchmarks live under `skills/core/benchmark-loader/benchmarks/`. The directory structure is:

```
benchmarks/
├── cis/
│   ├── cis_azure_v2.0.yaml
│   ├── cis_aws_v1.5.yaml
│   ├── cis_k8s_v1.24.yaml
│   └── ... 
├── nis2/
│   ├── nis2_technical.yaml
│   └── nis2_organizational.yaml
├── bsi/
├── iso27001/
├── best-practice/
│   ├── ad_best_practice.yaml        # Community-standard AD hardening
│   ├── vcenter_best_practice.yaml   # VMware vCenter best practices
│   └── oracle_dba_best_practice.yaml
└── custom/
    └── README.md                    # Per-client benchmarks go here
```

The `best-practice/` directory contains benchmarks derived from vendor documentation, community standards, and professional experience — no formal certification body behind them, but still authoritative for specific domains.

---

## 7. Connector Layer

Connectors are the data collection interface. They abstract over transport protocols and authentication methods.

### Connector Base Class

```python
# lib/connectors/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class ConnectorResult:
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    collection_metadata: dict[str, Any] = field(default_factory=dict)

class Connector(ABC):
    """Base class for all data collection connectors."""

    @abstractmethod
    def collect(self, targets: list[str],
                credentials: dict[str, Any],
                output_dir: str,
                client_id: str) -> ConnectorResult:
        """Collect data from targets and write to output_dir."""
        ...

    @abstractmethod
    def validate_connection(self, credentials: dict[str, Any]) -> bool:
        """Test connectivity with given credentials."""
        ...
```

### Transport Protocol Abstraction

| Transport | Library | Use Case |
|-----------|---------|----------|
| `SSH` | `asyncssh` / paramiko | Linux servers, ESXi hosts |
| `WinRM` | `pywinrm` | Windows Servers |
| `API` | `httpx` / SDK | Azure (azure-identity), AWS (boto3), GCP, vCenter (pyvmomi), K8s API |
| `GraphQL` | `gql` | Some modern infrastructure tools |
| `PowerShell` | `pywinrm` + PowerShell | Windows remote management |
| `CLI subprocess` | `subprocess` | az CLI, aws CLI, kubectl, gcloud |

### Connector Discovery

Connectors are discovered by scanning `skills/*/connectors/*.py`. Each connector declares its metadata via module-level `__*__` attributes (described in Section 5). The decomposer reads these to build a capability map.

---

## 8. Report Pipeline

```
┌──────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ FINDINGS  │──▶│ AGGREGATOR   │──▶│ REPORT       │──▶│ OUTPUT       │
│ (JSON)    │   │ (dedup,      │   │ COMPILER     │   │ (MD / PDF /   │
│           │   │  severity,   │   │ (AI + Jinja2)│   │  HTML)       │
│           │   │  correlate)  │   │              │   │              │
└──────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

### Stage 1: Finding Aggregation

Input: Raw findings from each skill (one JSON file per domain)
Output: Consolidated `findings.json` with deduplicated, severity-sorted findings

```python
# skills/core/finding-aggregator/SKILL.md (conceptual)
# 1. Load all findings from work/findings/<client-id>/*.json
# 2. Group by control_id (same control from different targets)
# 3. Deduplicate: if two findings cover the same control, merge evidence
# 4. Compute aggregate severity:
#    - If ANY instance is critical → overall critical
#    - Severity per control: max across instances
# 5. Correlate: map findings to all benchmarks they affect
# 6. Sort by severity (critical → high → medium → low → info)
# 7. Write work/findings/<client-id>/findings.json
```

### Stage 2: Report Compilation

Input: Consolidated findings, client metadata, selected benchmarks
Output: Professional audit report

The report compiler uses Jinja2 templates and AI synthesis to produce:

1. **Executive Summary** — One-page summary for C-level stakeholders
2. **Scope & Methodology** — What was audited, against what benchmarks
3. **Overall Compliance Score** — Per-benchmark compliance percentage
4. **Critical & High Findings** — Everything that needs immediate attention
5. **Medium & Low Findings** — Recommendations for upcoming sprints
6. **Informational Findings** — Observations, no action required
7. **Remediation Plan** — Prioritized, actionable remediation steps
8. **Appendix A: Detailed Evidence** — Raw data collected
9. **Appendix B: Excluded Controls** — Controls deemed N/A with justification

```markdown
---
title: IT Security Audit Report — Acme Corp
date: 2025-09-01
auditor: Oliver
engagement: AUD-2025-001
---

# Executive Summary

**Acme Corp** engaged Audit Field Kit to perform an infrastructure security
audit against the following benchmarks:

- CIS Microsoft Azure Foundations Benchmark v2.0 (Level 1 + Level 2)
- NIS2 Directive — Technical Measures (Implementing Regulation)
- Active Directory Best Practice (Community Standard)

## Overall Compliance

| Benchmark | Compliant | Non-Compliant | N/A | Score |
|-----------|-----------|---------------|-----|-------|
| CIS Azure v2.0 L1 | 32 | 5 | 3 | 86% |
| CIS Azure v2.0 L2 | 18 | 3 | 1 | 86% |
| NIS2 Technical | 24 | 2 | 0 | 92% |
| AD Best Practice | 15 | 4 | 1 | 79% |

## Critical Findings (4)

| ID | Title | Target | Benchmark |
|----|-------|--------|-----------|
| CIS-1.1.1 | MFA not enforced for privileged users | Azure | CIS, NIS2 |
| AD-BP-3.1 | Domain admin group has 14 members | AD | Best Practice |
| ... | ... | ... | ... |

## Detailed Findings

### CIS-1.1.1 — MFA for Privileged Users ❌

**Severity:** Critical  
**Domain:** cloud/azure  
**Target:** subscription:prod-eu-west-1  
**Benchmarks:** CIS v2.0, NIS2-TECH-5.1, ISO 27001 A.9.4.2  

**Current State:** 4 of 12 privileged role assignments do not have MFA
enforced. Affected users: admin@acme.com, svc-terraform@acme.com, ...

**Expected State:** All users with privileged roles (Global Admin, Application
Admin, Exchange Admin, etc.) MUST have MFA enforced via Conditional Access.

**Remediation:**
1. Create a Conditional Access policy targeting "All users with admin roles"
2. Set Grant Access → "Require multifactor authentication"
3. Exclude break-glass accounts only (max 2)
4. Deploy in report-only mode for 48h, then enable
5. Verify: `az rest --method get --uri ...`
```

### Stage 3: Output Format

The report compiler supports multiple output formats:

| Format | Tooling | Use Case |
|--------|---------|----------|
| **Markdown** | Jinja2 | Default, easy to review, version-control friendly |
| **PDF** | LaTeX (weasyprint / pdflatex) | Client-ready professional delivery |
| **HTML** | Jinja2 + CSS | Interactive web view with filters |
| **CSV** | Raw data dump | Import into GRC tools |

---

## 9. Workflow Orchestration

The orchestrator follows the same graph-engine pattern as the fleet-management project. The topology for a typical audit is:

```
Decomposer → Graph-Planner → Confirm → [Parallel Collectors] → 
[Parallel Evaluators] → Aggregator → Report Compiler → Consolidator
```

### Standard Audit Topology

```

                    ┌─────────────────────────────────────┐
                    │          AUDIT PLANNER              │
                    │  (decomposer + graph-planner)        │
                    │  - Parse client request              │
                    │  - Match skills to targets           │
                    │  - Load selected benchmarks          │
                    │  - Design collection topology        │
                    └────────────┬────────────────────────┘
                                 │
                        ┌────────┴────────┐
                        │  CONFIRM GATE   │
                        │  (you approve)  │
                        └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    │    PARALLEL COLLECTORS   │
                    │                         │
                    │  ┌─────┐ ┌────┐ ┌────┐  │
                    │  │Azure│ │  AD│ │K8s │  │  (one per target domain)
                    │  └──┬──┘ └──┬─┘ └──┬─┘  │
                    │     │       │      │     │
                    └─────┼───────┼──────┼────┘
                          │       │      │
                    ┌─────┴───────┴──────┴────┐
                    │    PARALLEL EVALUATORS   │
                    │                         │
                    │  ┌─────┐ ┌────┐ ┌────┐  │
                    │  │Azure│ │  AD│ │K8s │  │  (one per domain)
                    │  └──┬──┘ └──┬─┘ └──┬─┘  │
                    │     │       │      │     │
                    └─────┼───────┼──────┼────┘
                          │       │      │
                          └───┬───┴──┬───┘
                              │      │
                              ▼      ▼
                    ┌─────────────────────────┐
                    │  FINDING AGGREGATOR      │
                    │  (dedup, severities,     │
                    │   cross-benchmark map)   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  REPORT COMPILER         │
                    │  (exec summary → detail │
                    │   → remediation plan)   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  CONSOLIDATOR            │
                    │  (present final output)  │
                    └─────────────────────────┘
```

### Topology for Single-Target Audit (e.g., "just audit my k8s cluster")

```

Decomposer → Graph-Planner → Confirm →
  collect-k8s → evaluate-k8s → aggregator → report-compiler → consolidator
```

### Topology for Quick Best-Practice Check (no formal benchmark)

```

Decomposer → Graph-Planner → Confirm →
  [collect-targets] → evaluate-best-practice → consolidator
```

(Report compiler is omitted — the evaluator produces a best-practice summary)

### Topology for Multi-Benchmark, Multi-Target Audit

```

Decomposer → Graph-Planner → Confirm →
  [collect-azure, collect-ad, collect-k8s]  (parallel)
  → [evaluate-azure-cis, evaluate-azure-nis2, evaluate-ad-bp, evaluate-k8s-cis] (parallel)
  → aggregator → report-compiler (with all benchmarks) → consolidator
```

---

## 10. Extensibility Model

The system is designed to be extended at four levels:

### Level 1: Add a new benchmark

```yaml
# skills/core/benchmark-loader/benchmarks/cis/cis_k8s_v1.25.yaml
# 1. Create YAML file following schema
# 2. Map controls to existing connectors via `audit.connector`
# 3. Done — orchestrator auto-discovers on next run
```

### Level 2: Add a new connector to an existing skill

```python
# skills/container/kubernetes/connectors/collect_k8s_network_policies.py
# 1. Create Python script following connector contract
# 2. Update SKILL.md frontmatter connectors list
# 3. Reference new connector in benchmark controls
# 4. Done — orchestrator auto-discovers
```

### Level 3: Add a new target to an existing domain

```python
# skills/database/mysql/  (new directory, following oracle/ pattern)
# 1. Create SKILL.md with frontmatter + Graph section
# 2. Create connectors/ directory with collector scripts
# 3. Optionally create domain-specific benchmarks
# 4. Create lib/connectors/mysql.py transport if new protocol needed
# 5. Done — orchestrator auto-discovers
```

### Level 4: Add an entirely new domain

```bash
mkdir -p skills/edge-computing/k3s/connectors
# 1. Create SKILL.md following template
# 2. Create connectors
# 3. Register domain in domain taxonomy (if new)
# 4. Create benchmark files
# 5. Done — orchestrator auto-discovers
```

### Extension without code changes

- **Prompt templates** in `prompt-templates/` can be modified to change evaluation behavior
- **Benchmark YAML** can be edited to add/remove/change controls
- **Client config** drives scoping without touching any skill code
- **Report templates** in `skills/core/report-compiler/templates/` can be customized per client

---

## 11. Secrets and Authentication

### Credential Storage

Credentials live in `clients/<client-id>/credentials.yaml`. This file:

1. Is gitignored by default (or stored in an encrypted subrepo/1Password/Doppler)
2. Supports multiple authentication methods per target:

```yaml
# clients/acme-corp/credentials.yaml
credentials:
  azure:
    method: service_principal
    config:
      tenant_id: "..."
      client_id: "..."
      client_secret: "..."        # Or reference: ${AZURE_CLIENT_SECRET}
      environment: public         # public | gov | china

  active-directory:
    method: service_account
    config:
      domain: "acme.corp"
      username: "svc-audit@acme.corp"
      password: "${AD_SVC_PASSWORD}"
      auth_type: kerberos

  kubernetes:
    method: kubeconfig
    config:
      path: "clients/acme-corp/kubeconfig.yaml"
      context: "prod-cluster-1"

  windows-server:
    method: winrm
    config:
      hosts:
        - "dc-01.acme.corp"
        - "sql-01.acme.corp"
      username: "svc-audit"
      password: "${WIN_SVC_PASSWORD}"
      auth: kerberos
      ssl_verify: true

  oracle:
    method: wallet
    config:
      tns_admin: "/path/to/wallet"
      username: "svc_audit"
      password: "${ORACLE_SVC_PASSWORD}"
      role: "SYSDBA"              # or standard
```

### Environment Variables vs Files

| Method | Use Case |
|--------|----------|
| `.env` file | Development, local testing |
| 1Password CLI | Production, shared secrets |
| Doppler | Team-based secret management |
| Encrypted YAML | Air-gapped client environments |

### Principle of Least Privilege

The audit service account must be scoped to read-only:

```yaml
# Recommended audit role permissions:
azure:      Reader + Security Reader + Policy Reader
aws:        ReadOnlyAccess + SecurityAudit
vcenter:    Read-Only (no administrative privileges)
ad:         Domain Readers group (non-admin)
k8s:        cluster-reader ClusterRole (view-only)
oracle:     SELECT_CATALOG_ROLE + AUDIT_VIEWER
windows:    Builtin\Remote Management Users + Event Log Readers
```

---

## 12. Output Schema

### Finding Schema

```yaml
# A single audit finding
finding:
  id: "fnd-20250901-001"                    # Generated unique ID
  control_id: "CIS-1.1.1"                   # From benchmark
  benchmark: "cis_azure_v2.0"               # Which benchmark
  benchmark_level: 1                        # CIS level 1 or 2
  title: "MFA not enforced for privileged users"
  category: "Identity and Access Management"
  domain: "cloud"
  target: "azure"
  sub_target: "subscription:prod-eu-west-1"
  severity: critical                        # critical | high | medium | low | info
  status: non-compliant                     # compliant | non-compliant | not-applicable | not-tested | error

  # The evidence that triggered the finding
  evidence:
    - source: "collect_azure_aad.py"
      data:
        privileged_roles: 12
        mfa_enforced: 8
        non_compliant_users:
          - "admin@acme.com"
          - "svc-terraform@acme.com"
          - "emergency-01@acme.com"
          - "guest-admin@partner.com"

  # Expected state per benchmark
  expected_state: >
    All users with privileged directory roles must have MFA enforced
    via Conditional Access policy.

  # Remediation steps
  remediation:
    - "Create Conditional Access policy targeting 'All users with admin roles'"
    - "Grant Access → Require multifactor authentication"
    - "Exclude break-glass accounts only (max 2)"
    - "Deploy in report-only mode for 48h, then enable"
    estimated_effort: 2h

  # Cross-benchmark mapping
  also_applies_to:
    - benchmark: nis2_technical
      control_id: NIS2-TECH-5.1
    - benchmark: iso27001_2022
      control_id: A.9.4.2
```

### Aggregated Output Schema

```yaml
# work/findings/<client-id>/findings.json
engagement:
  client_id: "acme-corp"
  date: "2025-09-01"
  auditor: "Oliver"
  targets:
    - domain: cloud
      target: azure
      sub_targets: ["prod-eu-west-1", "prod-us-east-1"]
    - domain: identity
      target: active-directory
      sub_targets: ["acme.corp"]
  benchmarks_selected:
    - cis_azure_v2.0
    - nis2_technical
    - ad_best_practice

summary:
  total_controls: 87
  compliant: 68
  non_compliant: 14
  not_applicable: 4
  not_tested: 1
  overall_compliance: 82.9%

  by_benchmark:
    cis_azure_v2.0:
      total: 42
      compliant: 35
      non_compliant: 5
      na: 2
      score: 87.5%
    nis2_technical:
      total: 28
      compliant: 24
      non_compliant: 2
      na: 2
      score: 92.3%
    ad_best_practice:
      total: 17
      compliant: 9
      non_compliant: 7
      na: 1
      score: 56.2%

  by_severity:
    critical: 4
    high: 5
    medium: 3
    low: 2
    info: 0

findings:
  - ...  # Array of finding objects, sorted by severity
```

---

## 13. Glossary

| Term | Definition |
|------|------------|
| **Skill** | A self-contained audit capability defined in a SKILL.md file. Maps to one infrastructure domain/target. |
| **Connector** | A Python/Bash script that collects data from a specific infrastructure target. Follows a standard contract. |
| **Benchmark** | A structured YAML file containing control definitions (CIS level 1/2, NIS2, etc.). |
| **Control** | A single requirement or check within a benchmark. Has an ID, title, description, severity, and audit instructions. |
| **Finding** | The result of evaluating one or more controls against collected evidence. Has status, severity, and remediation. |
| **Evidence** | Raw configuration data collected from infrastructure targets. The input to evaluation. |
| **Target** | A specific infrastructure component being audited (e.g., one Azure subscription, one K8s cluster). |
| **Domain** | A category of infrastructure (cloud, virtualization, container, identity, database, os, network, iac). |
| **Orchestrator** | The graph-engine that decomposes requests, plans topology, routes work, and consolidates results. |
| **Client Config** | Per-engagement YAML config: scope, credentials, selected benchmarks. |
| **Compliance Score** | Percentage of applicable controls that pass: (compliant / (total - na)) × 100 |

---

## Appendix A: Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Set up repo structure, `.gitignore`, `README.md`
- [ ] Implement `lib/audit_engine/base.py` — base classes
- [ ] Implement `lib/connectors/base.py` + SSH, WinRM, API transports
- [ ] Implement `lib/benchmark/parser.py` — YAML loading with validation
- [ ] Create core orchestrator skill (adapt from fleet-management)
- [ ] Create first benchmark: `cis_azure_v2.0.yaml` (5-10 representative controls)
- [ ] Create first connector: `collect_azure_subscriptions.py`
- [ ] End-to-end test: single-target Azure audit against 5 CIS controls

### Phase 2: Core Skills (Week 3-4)
- [ ] `skills/cloud/azure/` — full connector set + evaluation skill
- [ ] `skills/core/benchmark-loader/SKILL.md`
- [ ] `skills/core/finding-aggregator/SKILL.md`
- [ ] `skills/core/report-compiler/SKILL.md` + Jinja2 templates
- [ ] Prompt templates for AI evaluation
- [ ] Client config template (`clients/_template/`)

### Phase 3: Domain Expansion (Week 5-8)
- [ ] `skills/virtualization/vmware-vcenter/`
- [ ] `skills/identity/active-directory/`
- [ ] `skills/container/kubernetes/`
- [ ] `skills/database/oracle/`
- [ ] `skills/os/windows-server/`
- [ ] `skills/os/linux/`
- [ ] Full CIS benchmark files for each domain

### Phase 4: Advanced (Week 9-12)
- [ ] NIS2, BSI, ISO 27001 benchmark files
- [ ] Best-practice benchmarks for AD, vCenter, Oracle
- [ ] Multi-target, multi-benchmark topology optimization
- [ ] PDF output via LaTeX template
- [ ] `scripts/run-audit.sh` — single-command entry point
- [ ] Cross-benchmark control mapping
- [ ] Client intake wizard (interactive setup)

### Phase 5: Production Readiness (Ongoing)
- [ ] CI validation (schema, connector contract tests)
- [ ] Benchmark library expansion (community contributions)
- [ ] Performance optimization (parallel execution, caching)
- [ ] Remediation script generation (from findings → Ansible/Terraform)
- [ ] Interactive HTML report with drill-down
- [ ] Swedish language support (kvalitetsledare agent)

---

*This document is a living design artifact. Update as the architecture evolves.*