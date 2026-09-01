---
name: "{{SKILL_NAME}}"
description: >
  {{SKILL_DESCRIPTION}}
domain: "{{DOMAIN}}"
connectors:
  - "{{CONNECTOR_1}}"
benchmarks:
  - "{{BENCHMARK_1}}"
authentication: "{{AUTH_METHOD}}"
transport: "{{TRANSPORT}}"
---

# {{SKILL_NAME}} — Audit Skill

## Overview

TODO: Describe what this skill audits, what it covers, and what it produces.

## Collection

Connector scripts in `connectors/` collect data from targets.
Output: `work/evidence/<client-id>/{{DOMAIN}}/<connector-name>.json`

## Connectors

| Connector | Description | Required | Transport |
|-----------|-------------|----------|-----------|
| `connector_a.py` | ... | Yes | ... |
| `connector_b.py` | ... | Optional | ... |

## Evaluation

Benchmarks evaluated by this skill:

| Benchmark | Controls | Evaluation Type |
|-----------|----------|-----------------|
| `benchmark_a` | N | ai / deterministic |
| `benchmark_b` | N | ai / deterministic |

## Graph

Nodes:
  - name: collect-{{SKILL_NAME}}
    trigger: route("audit-planner")
    input: [scoping]
    role: You collect {{TARGET}} infrastructure data.
    skills: [{{DOMAIN}}/{{SKILL_NAME}}/connectors]
    output: work/evidence/{client}/{{DOMAIN}}/
    route: always -> evaluate-{{SKILL_NAME}}

  - name: evaluate-{{SKILL_NAME}}
    trigger: route("collect-{{SKILL_NAME}}")
    input: [evidence, benchmarks]
    role: You evaluate {{TARGET}} evidence against benchmarks.
    skills: [core/benchmark-loader]
    output: work/findings/{client}/{{DOMAIN}}/
    route: always -> aggregator