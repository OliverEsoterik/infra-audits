# Audit Field Kit

> **Automated IT Infrastructure Auditing — Code-Driven, Benchmark-Aligned, Extensible**

An open-source toolkit for executing professional-grade IT infrastructure audits against industry benchmarks (CIS, NIS2, BSI, ISO 27001). Designed for DevOps engineers, infrastructure architects, and IT auditors who need to assess cloud, virtualization, container, identity, database, OS, and network environments — fast, consistently, and with professional reports.

## Why This Exists

Every IT audit follows the same pattern:
1. Connect to infrastructure
2. Collect configuration evidence
3. Evaluate against benchmarks (CIS, NIS2, etc.)
4. Generate findings with severity
5. Produce a professional report

The Audit Field Kit codifies this pipeline. One repo, one workflow, infinite audit targets.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/your-org/audits.git
cd audits

# Install dependencies
./scripts/install-deps.sh

# Initialize a client engagement
./scripts/init-client.sh acme-corp

# Edit client config
$EDITOR clients/acme-corp/scoping.yaml
$EDITOR clients/acme-corp/credentials.yaml
$EDITOR clients/acme-corp/benchmarks.yaml

# Run the audit
./scripts/run-audit.sh acme-corp

# Find the report
open work/reports/acme-corp/audit-report.pdf
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                          │
│   (graph-engine — decomposes, plans, routes, consolidates) │
└──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────────┘
       │      │      │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼      ▼      ▼
    ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
    │Cloud│ │  OS │ │  ID │ │  DB │ │ K8s │ │ Net │ │ IaC │  ← Skills
    └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘
       │      │      │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼      ▼      ▼
    ┌─────────────────────────────────────────────────┐
    │           CONNECTORS (SSH, WinRM, API, CLI)      │  ← Data collection
    └─────────────────────────────────────────────────┘
       │      │      │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼      ▼      ▼
    ┌─────────────────────────────────────────────────┐
    │   BENCHMARKS (CIS, NIS2, BSI, ISO, Best Practice)│  ← Evaluation
    └─────────────────────────────────────────────────┘
       │
       ▼
    ┌─────────────────────────────────────────────────┐
    │         FINDINGS → AGGREGATOR → REPORT           │  ← Output
    └─────────────────────────────────────────────────┘
```

## What You Can Audit

| Domain | Targets | Connectors | Benchmarks |
|--------|---------|-----------|------------|
| **Cloud** | Azure, AWS, GCP | Azure CLI, AWS CLI, gcloud | CIS Cloud Foundations, NIS2, BSI Cloud |
| **Virtualization** | VMware vCenter, Hyper-V | pyvmomi, WinRM | Best Practice, CIS |
| **Container** | Kubernetes, Docker, Helm | kubectl, Docker API | CIS K8s, CIS Docker |
| **Identity** | Active Directory, Entra ID, SSSD | PowerShell, MS Graph, LDAP | Best Practice, CIS |
| **Database** | Oracle, SQL Server, PostgreSQL, MongoDB | SQL*Net, TDS, psql, Mongo shell | Best Practice, CIS |
| **OS** | Windows Server, Linux, ESXi | WinRM, SSH, API | CIS OS Benchmarks |
| **Network** | Firewalls, Load Balancers, DNS | SSH, API | Best Practice |
| **IaC** | Terraform, Ansible | CLI, API | CIS IaC |
| **Backup** | Veeam, General Backup | API, SSH | Best Practice |
| **Cross-Cutting** | Network Segmentation, Certificates, Logging, Patch Management, DR | Aggregated | Best Practice |

## Repository Structure

```
audits/
├── IDEA.md                 # Original concept
├── DESIGN.md               # Full technical design document
├── README.md               # This file
│
├── skills/                 # Audit domain skills (extensible)
│   ├── core/               #   Orchestrator, benchmark-loading, aggregation
│   ├── cloud/              #   Azure, AWS, GCP
│   ├── virtualization/     #   VMware vCenter, Hyper-V
│   ├── container/          #   Kubernetes, Docker, Helm
│   ├── identity/           #   Active Directory, Entra ID
│   ├── database/           #   Oracle, SQL Server, PostgreSQL, MongoDB
│   ├── os/                 #   Windows Server, Linux, ESXi
│   ├── network/            #   Firewalls, Load Balancers, DNS
│   ├── iac/                #   Terraform, Ansible
│   ├── backup/             #   Veeam, General
│   └── cross-cutting/      #   Certificate, Segmentation, Logging
│
├── lib/                    # Shared Python libraries
│   ├── audit_engine/       #   Base classes, collector runner, evaler
│   ├── benchmark/          #   YAML parser, resolver, mapper
│   ├── connectors/         #   SSH, WinRM, API wrappers
│   ├── output/             #   Schemas, report helpers
│   └── utils/              #   Config, logging, versioning
│
├── prompt-templates/       # AI evaluation prompts (Jinja2)
├── agents/                 # Pre-configured agent profiles
├── clients/                # Per-client config (gitignored)
├── scripts/                # CLI entry points
└── work/                   # Runtime output (gitignored)
```

## Extensibility

**Add a new benchmark:** Write a YAML file → place it in `skills/core/benchmark-loader/benchmarks/<vendor>/`

**Add a new connector to a skill:** Write a Python collector → add it to `skills/<domain>/<target>/connectors/`

**Add a new audit target:** Create `skills/<domain>/<target>/SKILL.md` + connectors/ + domain-specific benchmarks

**Add an entirely new domain:** Create a new directory under `skills/`, register in the taxonomy

No orchestrator changes needed for any of these — the system auto-discovers skills, connectors, and benchmarks.

## Workflow

1. **Scoping** — Define which targets to audit and against what benchmarks
2. **Collection** — Connectors gather evidence in parallel (parallel per domain)
3. **Evaluation** — AI agents evaluate evidence against selected benchmarks
4. **Aggregation** — Findings are deduplicated, severity-ranked, cross-mapped
5. **Reporting** — Professional report with executive summary, detailed findings, remediation plan

## License

MIT — Use freely, extend, contribute.