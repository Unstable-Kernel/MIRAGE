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
- Policy provenance, request timeout, cooperative cancellation, and input/output resource-budget checks for URCP execution.
- Inspection-only CoppeliaSim adapter contract that never connects or controls a simulator.
- Declarative backend sandbox envelope assessment that denies unsupported OS-level resource restrictions.
- Checkpoint revalidation for policy provenance, capability versions, and backend allow-lists without resume behavior.
- Fixture-backed read-only simulator project metadata and state extraction with sandbox assessment, policy checks, timeout handling, and cancellation-token cooperation.
- `mirage simulator-metadata` for deterministic fixture inspection, with an explicitly unavailable non-connecting CoppeliaSim read-only boundary.
- Read-only transport manifests and evidence assessment, including the unverified, non-connecting CoppeliaSim ZeroMQ reference manifest.
- Sandbox enforcement-evidence contracts that reject OS-enforced envelope claims without matching declared controls and verified evidence.
- Bounded goal-to-evaluate workflow review contracts, `review_goal_workflow@0.1`, and a human-review checkpoint that never executes or resumes work.
- `mirage transport-assess` and `mirage goal-workflow-review` for deterministic local contract inspection.
- Deterministic EIR-to-plan validation and evaluation-evidence assessment contracts that remain review-only and never invoke a model or backend.
- `assess_workflow_evidence@0.1`, `mirage goal-workflow-plan`, and `mirage goal-workflow-evidence` for local workflow inspection.
- Stronger integrity requirements for live transport and verified sandbox evidence claims.
- Deterministic redacted context bundles and policy-bound provenance review traces for the M4 human-review foundation.
- `inspect_workflow_context@0.1`, `assess_review_trace@0.1`, `mirage workflow-context-inspect`, and `mirage review-trace-assess` for local review-only inspection.

### Changed

- Reconciled README, architecture records, runtime guides, URCP specification, security boundaries, examples, roadmap, collaborator review, and workflow continuation context with the current execution and read-only adapter baseline.
- Added a delivery-status guide that distinguishes completed milestones, the partial M3 foundation, planned milestones, remaining delivery streams, and cross-cutting hardening work.

### Not yet included

- Simulator control, real simulator transport integration, or hardware execution.
- Persistent ESG/EKG/TESG knowledge stores.
- MCP, research-paper ingestion, autonomous experiments, optimization, or physical actuation.
