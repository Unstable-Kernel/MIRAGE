# EDR-0001: Iteration 1 Scope

## Status

Accepted.

## Objective

Turn the empty MIRAGE repository into a testable foundation without attempting the full robotics platform in one pass.

## Decision

Iteration 1 delivers organization documentation, EIR 0.1, structured JSON/YAML validation, a provider-neutral model orchestrator, all six initial LLM provider adapters, a minimal CLI, mocked contract tests, optional provider smoke tests, examples, and CI. It does not implement simulators, hardware, MCP, persistent engineering graphs, or autonomous optimization.

## Alternatives considered

A broad multi-simulator prototype would provide more visible surface area but would obscure whether the EIR and capability abstractions are correct. A single-provider prototype would be narrower but would create avoidable architectural coupling. The selected scope proves the canonical semantic layer and provider independence together.

## Evidence and assumptions

The build-loop specifications identify EIR as the canonical interoperability layer, require BYO and model-agnostic providers, and require a first agent iteration with a schema, CLI, provider abstraction, CI, and an end-to-end architecture test. The implementation uses Python 3.11+, `uv`, Pydantic, HTTPX, and optional native provider SDKs.

## Risks

The EIR subset may be too narrow, provider capabilities may drift, local servers may not exist in CI, and SDK dependencies may conflict. These risks are mitigated by versioned schemas, shared contracts, capability declarations, mocked transports, optional dependency groups, and explicit documentation.

## Verification plan

Run unit tests, provider contract tests for all six adapters, CLI tests, schema-export comparison, documentation checks, secret scanning, dependency auditing, and a mocked end-to-end EIR-to-plan path. Live provider calls remain opt-in.

## Owner

Erebuzzz, Unstable Kernel, 2026-08-18.
