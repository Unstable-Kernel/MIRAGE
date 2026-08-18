# MIRAGE Architecture

## Status

This document describes the architecture for MIRAGE Iteration 1 and the boundaries that future iterations must preserve. It is authored for Unstable Kernel by [Erebuzzz](https://github.com/Erebuzzz).

## Goals

MIRAGE must represent engineering semantics independently of any model vendor, simulator, programming language, or execution backend. Probabilistic reasoning may propose interpretations and plans, but deterministic validation, transformation, capability resolution, and safety policy must remain inspectable and testable.

## Non-goals for Iteration 1

Iteration 1 does not implement a persistent graph database, simulator control, hardware actuation, research-paper parsing, ROS/MATLAB/CAD ingestion, MCP, or autonomous optimization. It establishes EIR 0.1, provider contracts, configuration, validation, and a CLI.

## Three planes

| Plane | Responsibility | Iteration 1 status |
|---|---|---|
| Cognitive Plane | Roles, planning, synthesis, explanation, and review requests | Provider role abstraction only |
| Knowledge Plane | EIR, ESG, evidence, provenance, temporal state, and EDRs | EIR 0.1 and provenance primitives |
| Execution Plane | URCP capabilities, scheduling, adapters, and result collection | Provider adapter contract only |

## Engineering compiler

The compiler boundary is the deterministic semantic center of MIRAGE. It accepts structured engineering artifacts, validates them, normalizes them into EIR, and eventually lowers EIR into execution graphs and backend artifacts. The compiler must not depend on a particular LLM or simulator.

## EIR

EIR is a versioned, JSON/YAML-serializable representation containing stable identifiers, typed nodes, relationships, provenance, validation status, confidence, timestamps, and extension metadata. EIR 0.1 intentionally covers a small node and relationship subset. Unsupported semantics must be reported rather than silently discarded.

## Model orchestrator

The orchestrator selects a provider by role and configuration. It owns fallback order, retry policy, timeout/cancellation handling, normalized errors, and redacted observability. It depends only on the provider protocol, never on a provider SDK or vendor URL.

## Provider adapters

The initial matrix contains OpenAI, Anthropic, generic OpenAI-compatible, Ollama, vLLM, and llama.cpp. Adapters translate a normalized completion request to provider-native transport, advertise verified capabilities, and normalize responses. Shared wire protocols may share transport code, but provider identity, capabilities, configuration, documentation, and tests remain explicit.

## Knowledge plane evolution

The current slice implements ESG as a revisioned EIR-linked state object with append-only structured events. Future versions will add EKG for reusable cross-project knowledge, TESG for temporal evolution, an Evidence Graph for claim support, and EDR for important engineering decisions. These concerns remain separate so that traceability is not collapsed into opaque model context.

## Execution plane evolution

The current slice implements a declarative URCP capability descriptor and deterministic registry. URCP exposes capabilities such as `inspect_model`, `run_simulation`, `capture_sensor_data`, `evaluate_metric`, and `export_artifact`. Simulator and hardware adapters will implement URCP rather than being called directly by agents. Hardware capabilities require explicit authorization, safety classes, resource limits, network policy, emergency-stop integration, and audit logs.

## Data flow

```text
Input artifacts -> parser/frontend -> EIR -> deterministic validation
     -> cognitive request -> provider adapter -> structured proposal
     -> capability resolution -> future backend -> results -> evidence/EDR
```

Every meaningful extracted fact or decision should preserve source references, extraction method, confidence, and validation status. Every execution should record configuration, versions, seed, outputs, and failure information.

## Failure modes

The system must surface malformed input, missing provenance, unsupported provider capabilities, authentication failure, rate limiting, timeout, cancellation, invalid EIR relationships, schema mismatch, and unsafe execution requests as structured errors. It must not hide unsupported features behind best-effort behavior.

## Security implications

Provider credentials are injected at runtime and redacted in logs. External artifacts and model output are untrusted data. No model response may directly produce unrestricted physical actuation. See [SECURITY.md](SECURITY.md).

## Validation strategy

The architecture is validated through EIR unit tests, provider contract tests, mocked end-to-end tests across all six providers, CLI tests, schema-export checks, and optional live provider smoke tests. Simulator and hardware validation will be added only with deterministic fixtures and explicit safety gates.
