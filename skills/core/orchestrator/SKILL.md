---
name: orchestrator
description: >
  Graph-engine orchestrator for the audit field kit. Routes audit work
  through a data-driven state machine. Skills register their own graph
  nodes dynamically based on scoping and benchmark selection.
---

# Orchestrator — Audit Graph Engine

## Overview

The orchestrator is a **state router**: it reads shared state, selects the
next node to execute based on routing rules, launches sub-agents for execution
nodes (collectors, evaluators), and writes results back.

**Key difference from generic orchestrator:** This orchestrator specializes in
audit workflows — it understands the audit lifecycle (scope → collect → evaluate
→ aggregate → report) and optimizes topology for multi-target, multi-benchmark
scenarios.

### Flow

```
User request → decomposer (parse scoping) → graph-planner (design topology)
  → confirm (you approve) → [parallel collectors] → [parallel evaluators]
  → aggregator → report-compiler → consolidator
```

### Architecture

```
                    ┌─────────────────────────────┐
                    │       SHARED STATE          │
                    │  work/graph/state.json      │
                    │  status, topology, nodes{}  │
                    └─────────────┬───────────────┘
                                  │
                      ┌───────────┴───────────┐
                      │        ROUTER         │
                      │  f(state) -> ready[]  │
                      └───────────┬───────────┘
                                  │
          ┌────────┬──────────────┼──────────────┬───────────┐
          ▼        ▼              ▼              ▼           ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
   │collectors│ │evaluators│ │aggregator│ │report-   │ │consolida-│
   │(parallel)│ │(parallel)│ │          │ │compiler  │ │tor       │
   └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

## Status values

| Status | Meaning |
|--------|---------|
| `SCOPING` | Reading client config, identifying targets |
| `PLANNING` | Designing collector + evaluator topology |
| `CONFIRM` | Waiting for user approval on audit plan |
| `COLLECTING` | One or more collectors running (parallel) |
| `EVALUATING` | Evaluating evidence against benchmarks (parallel) |
| `AGGREGATING` | Merging findings from all domains |
| `REPORTING` | Generating audit report |
| `COMPLETE` | Audit finished |

## Graph Nodes

### Built-in nodes

| Node | Purpose |
|------|---------|
| `decomposer` | Parse client request, match skills, build task list |
| `graph-planner` | Design collector → evaluator topology |
| `confirm` | Get user approval on audit topology |
| `aggregator` | Merge findings across domains, deduplicate, rank |
| `report-compiler` | Generate professional audit report |
| `consolidator` | Present final output to user |

### Graph skill nodes (registered from skill SKILL.md `## Graph` sections)

Each audit skill registers two nodes:
- `collect-<target>` — runs connector scripts
- `evaluate-<target>` — evaluates evidence against benchmarks

## Router Logic

The router follows the same `f(state) -> ready_nodes[]` pattern as the
fleet-management orchestrator. See `skills/core/orchestrator/examples/` for
topology proposals.