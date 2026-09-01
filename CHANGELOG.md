# Changelog

All notable changes to the Audit Field Kit will be documented in this file.

## [0.1.0] — 2025-09-01

### Added

- **Repository structure**: Complete skill-based repo with 10 domains, 20+ skills, and 40+ connector slots
- **Design document**: `DESIGN.md` — full architecture document covering taxonomy, skill architecture, benchmark framework, connector layer, report pipeline, workflow orchestration, and extensibility model
- **Core orchestrator**: Graph-engine pattern adapted from fleet-management orchestrator, specialized for audit workflows
- **Benchmark framework**: YAML-based benchmark definitions with CIS Azure v2.0 (10 controls), NIS2 Technical (5 controls), and AD Best Practice (6 controls)
- **Cross-benchmark mapping**: Control equivalence mapping between CIS, NIS2, ISO 27001, and AD Best Practice
- **Connector architecture**: Abstract connector base classes with SSH, WinRM, API, CLI transport adapters
- **Library code**: Python base classes, collector runner, evidence evaluator, report generator (Pydantic models)
- **Prompt templates**: Jinja2 templates for AI-driven control evaluation and remediation advice
- **Client config system**: Template-based per-client configuration with scoping, benchmarks, and credentials
- **Shell scripts**: run-audit.sh, init-client.sh, list-skills.sh, validate-schemas.sh, install-deps.sh
- **Gitignore**: Work directories, client data, credentials, and build artifacts excluded
- **README**: Full project documentation with quick-start, architecture overview, and extensibility guide