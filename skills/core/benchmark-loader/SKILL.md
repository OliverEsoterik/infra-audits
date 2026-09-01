---
name: benchmark-loader
description: >
  Loads, validates, and resolves benchmark YAML files. Provides the evaluation
  engine with structured control definitions, audit queries, and cross-benchmark
  mappings.
---

# Benchmark Loader

## Overview

The benchmark loader discovers, loads, validates, and resolves benchmark YAML
files from the benchmark registry. It also loads cross-benchmark mappings for
finding deduplication.

## Trigger

`state.routing.next_node == "benchmark-loader"` (called as sub-skill during
evaluation steps)

## Discovery

Benchmarks live in `skills/core/benchmark-loader/benchmarks/`. The loader
scans all subdirectories for `*.yaml` files:

```
benchmarks/
├── cis/
│   ├── cis_azure_v2.0.yaml
│   ├── cis_k8s_v1.24.yaml
│   └── ...
├── nis2/
├── best-practice/
└── custom/   # Per-client benchmarks added here
```

## Resolution

Given a list of benchmark IDs (from client config), the loader:

1. Finds the matching YAML files
2. Validates schema (all required fields present)
3. Resolves control dependencies (if control A references control B)
4. Loads cross-benchmark mappings (e.g., CIS-1.1.1 ↔ NIS2-TECH-5.1)
5. Returns resolved benchmark objects

## Benchmark YAML Schema

```yaml
benchmark:
  id: string              # Unique identifier
  name: string            # Human-readable name
  version: semver         # Version string
  date: ISO-date          # Publication date
  source: URL             # Source URL
  publisher: string       # Organization

metadata:
  domain: string          # Infrastructure domain
  targets: [string]       # Applicable target types
  levels:
    - level: 1|2          # CIS levels
      description: string

controls:
  - id: string            # Control ID (e.g., CIS-1.1.1)
    title: string         # Short title
    level: 1|2            # Benchmark level
    category: string      # Control category
    description: string   # Long description
    audit:
      connector: string   # Collector script that provides evidence
      evaluation_type: ai | deterministic | script
      query: string       # AI prompt or deterministic logic
    severity: critical | high | medium | low | info
    mapping:              # Cross-benchmark mapping
      nis2: string        # NIS2 control ID
      iso27001: string    # ISO 27001 control ID
    remediation: string   # Remediation steps
```