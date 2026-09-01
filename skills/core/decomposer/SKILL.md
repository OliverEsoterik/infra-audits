---
name: decomposer
description: >
  Decomposes a client audit request into tasks by parsing client config files
  and matching targets against available skills and benchmarks.
---

# Decomposer — Audit Task Planner

## Trigger

`state.status == "SCOPING"` OR `state.routing.next_node == "decomposer"`

## Input

- `state.user_request` — the audit request
- `state.client_id` — client identifier
- `clients/<client-id>/scoping.yaml` — target definitions
- `clients/<client-id>/benchmarks.yaml` — selected benchmarks

## Behavior

1. Read client config files (scoping, benchmarks, client-config)
2. Scan `skills/*/SKILL.md` — build skill index (name, domain, description,
   connectors, benchmarks)
3. Scan `skills/core/benchmark-loader/benchmarks/` — build benchmark index
4. Match scoping targets → skills:
   - For each target in scoping, find the skill covering that domain/target
   - For each selected benchmark, find skills that have it in their `benchmarks` list
5. Build task list:
   - One task per domain-target combination
   - Each task has: target, domain, skills needed, benchmarks to evaluate
6. Write to state: `decomposition.tasks`, `skill_index`, `benchmark_index`

## Output

Writes to `work/graph/state.json`:
- `decomposition.tasks` — list of audit tasks
- `skill_index` — matched skills
- `benchmark_index` — loaded benchmarks
- `client_config` — parsed client config
- `routing.next_node = "graph-planner"`