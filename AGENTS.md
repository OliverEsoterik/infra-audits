# Audit Field Kit — Project-Level Agent Configuration

This file contains agent definitions specific to this project.
Agents define reusable agent profiles with specific skills, models, and tools.

## orchestration

The root level orchestrator. At the start of the session / audit the user asks for an audit of a client. The orchestrator analyzes the user request, scopes the audit, builds the topology of skills needed and fire them. After gathering all findings the orchestrator generates the audit report.

## audit-planner

Decomposes the client's audit request into skills and targets.
Takes the client scoping + benchmarks → produces audit topology.

## evidence-collector

Runs collector scripts for a specific domain/target.
Writes raw JSON evidence to work/evidence/<client-id>/<domain>/.

## compliance-evaluator

Reads collected evidence + loaded benchmarks.
Evaluates each control, produces structured findings.
Uses AI (prompt templates) + deterministic checks.

## report-writer

Reads aggregated findings.
Generates professional audit report (Markdown → PDF).
Uses Jinja2 templates + AI executive summary generation.