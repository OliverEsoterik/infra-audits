---
name: oracle
description: >
  Security audit for Oracle Database instances. Covers authentication,
  authorization, auditing, encryption (TDE, network), listener security,
  patch level, and configuration hardening.
domain: database
connectors:
  - collect_oracle_instances.py
  - collect_oracle_security.py
  - collect_oracle_audit.py
  - collect_oracle_network.py
  - collect_oracle_backup.py
benchmarks:
  - oracle_dba_best_practice
  - nis2_technical
authentication: service-account
transport: sqlplus
---

# Oracle Database Audit Skill

## Overview

Audits Oracle Database instances against DBA best practice baselines and
NIS2 technical measures. Covers database security configuration, user
privileges, audit policies, network encryption, and backup validation.

## Collection

| Connector | What It Collects | Transport |
|-----------|------------------|-----------|
| `collect_oracle_instances.py` | Instance info, version, patches, DBID | SQL*Plus / SQL*Net |
| `collect_oracle_security.py` | Users, roles, system/object privileges, profiles | SQL*Plus |
| `collect_oracle_audit.py` | Unified audit configuration, audit trail, audit policies | SQL*Plus |
| `collect_oracle_network.py` | Listener config (protocols, SSL/TLS), wallet | Listener control / SQL*Net |
| `collect_oracle_backup.py` | RMAN config, backup schedule, restore validation | SQL*Plus / RMAN |

## Graph

Nodes:
  - name: collect-oracle
    trigger: route("audit-planner")
    input: [scoping, credentials]
    role: You collect Oracle Database data via SQL*Plus.
    skills: [database/oracle/connectors]
    output: work/evidence/{client}/oracle/
    route: always -> evaluate-oracle

  - name: evaluate-oracle
    trigger: route("collect-oracle")
    input: [evidence, benchmarks]
    role: You evaluate Oracle evidence against best practice benchmarks.
    skills: [core/benchmark-loader]
    output: work/findings/{client}/oracle/
    route: always -> aggregator