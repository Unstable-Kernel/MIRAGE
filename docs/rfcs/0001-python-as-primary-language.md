# RFC 0001: Python as the Primary Implementation Language

## Status

Accepted for Iteration 1.

## Problem

MIRAGE needs a practical implementation language for EIR modeling, deterministic validation, provider adapters, and a CLI while remaining close to the robotics and scientific-computing ecosystem.

## Decision

Use Python 3.11 or newer as the primary language for the initial monorepo. Use `uv` and `pyproject.toml` for environments, package metadata, and lockfile management. Keep EIR serializations language-independent so future implementations can interoperate without adopting Python.

## Alternatives

TypeScript offers strong tooling and broad API support but is less aligned with the initial robotics and numerical ecosystem. Rust offers strong safety and performance but would increase early development cost and integration friction. A polyglot foundation would be premature before the semantic contracts stabilize.

## Compatibility and migration

The decision does not constrain future adapters or performance-critical components. EIR is serialized as JSON/YAML and validated by a versioned schema. A future Rust, C++, or TypeScript implementation can consume the same contract.

## Security

Python dependencies are pinned and audited in CI. Provider credentials remain runtime configuration. Untrusted engineering artifacts must not be executed directly during parsing.

## Validation

The decision is validated by the first EIR, orchestrator, adapter, CLI, and CI implementation. Revisit it if profiling or deployment requirements show a concrete bottleneck.

## Owner

Erebuzzz, Unstable Kernel, 2026-08-18.
