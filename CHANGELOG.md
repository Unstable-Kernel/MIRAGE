# Changelog

All notable MIRAGE changes are recorded here. The project is pre-1.0 and follows independent versioning for EIR, runtime, and adapters.

## [Unreleased] : Iteration 1

### Added

- Organization-level architecture, governance, security, contribution, support, and roadmap documents.
- EIR 0.1 schema, provenance primitives, deterministic validation, JSON/YAML serialization, and JSON Schema export.
- Provider-neutral model protocol and role-based orchestrator.
- OpenAI, Anthropic, generic OpenAI-compatible, Ollama, vLLM, and llama.cpp adapters.
- `mirage validate`, `mirage inspect`, `mirage doctor`, `mirage esg-inspect`, and `mirage capabilities` CLI commands.
- Mocked provider contract tests and optional live smoke-test harness.
- EIR-backed Engineering State Graph snapshots with revisioned event history.
- Declarative URCP capability descriptors and deterministic registry filtering.
- Policy-gated URCP execution requests and structured execution results.
- Deterministic local simulation backend for tests and development.
- Explicit CoppeliaSim adapter boundary that reports unavailable until verified and configured.
- Append-only JSONL execution ledger with request IDs and secret redaction.
- Validated workflow checkpoints with revisioning and explicit non-executing resume semantics.
- `mirage ledger-inspect` and `mirage checkpoint-inspect` commands.
- Build-ready `mirage-engineering` Python distribution metadata with dynamic in-package versioning.
- Private `@unstable-kernel/mirage` npm launcher with local forwarding and package artifact checks.
- Local Python wheel and source distribution verification, plus CI package safeguards that do not publish.

### Not yet included

- Simulator or hardware execution.
- Persistent ESG/EKG/TESG knowledge stores.
- MCP, research-paper ingestion, autonomous experiments, optimization, or physical actuation.
