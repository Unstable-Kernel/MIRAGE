# 008 : Context engine

## Goals

Define a replaceable boundary for this MIRAGE subsystem while preserving EIR, provenance, reproducibility, and human control.

## Non-goals

This document records a planned subsystem. The current repository baseline does not implement a context engine.

## Terminology

The subsystem consumes validated EIR and emits typed artifacts, requests, results, or evidence. Provider and backend details remain behind adapters.

## Requirements

Inputs, outputs, failure modes, versions, and security assumptions must be explicit. Unsupported features must fail clearly rather than being silently ignored.

## Architecture

The context engine is a planned modular service inside MIRAGE. The implemented EIR, ESG, provider, URCP, and evidence-adjacent contracts are inputs to its future design, but they do not constitute context assembly, retrieval, ranking, or retention. Implementation is scheduled by ROADMAP.md.

## Interfaces

Public interfaces use versioned schemas, typed Python protocols, serialized artifacts, and structured diagnostics.

## Data flow

Context and EIR enter the subsystem; deterministic checks run before external effects; results are recorded with provenance and configuration.

## Failure modes

Malformed input, missing dependencies, unavailable capabilities, timeouts, inconsistent state, and authorization failures are recoverable structured errors.

## Security implications

Treat external artifacts, model output, generated code, and execution results as untrusted. Apply least privilege, redaction, sandboxing, and approval gates before effects.

## Open questions

Transport, persistence, scaling, and simulator/hardware-specific policy require future RFCs.

## Validation strategy

Use unit, contract, integration, reproducibility, and end-to-end tests appropriate to the subsystem.
