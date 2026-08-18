# 004 : Knowledge plane

## Goals

Define a replaceable boundary for this MIRAGE subsystem while preserving EIR, provenance, reproducibility, and human control.

## Non-goals

This document describes the implemented ESG foundation and the knowledge-plane components that remain planned.

## Terminology

The subsystem consumes validated EIR and preserves typed engineering state, events, and future evidence. Provider and backend details remain behind adapters.

## Requirements

Inputs, outputs, failure modes, versions, and security assumptions must be explicit. Unsupported features must fail clearly rather than being silently ignored.

## Architecture

The current knowledge-plane implementation is `EngineeringStateGraph`: a revisioned project-level wrapper around a validated EIR document with append-only unique events. It persists as validated JSON and provides deterministic state inspection. EKG, TESG, evidence graphs, EDRs, concurrency control, and durable storage are planned separately.

## Interfaces

Public interfaces include the versioned EIR schema, `EngineeringStateGraph`, typed event records, validated JSON snapshots, and structured diagnostics.

## Data flow

Validated EIR enters the graph; typed events advance its revision; persisted snapshots preserve the current EIR, event history, and optional event details for inspection.

## Failure modes

Malformed input, missing dependencies, unavailable capabilities, timeouts, inconsistent state, and authorization failures are recoverable structured errors.

## Security implications

Treat external artifacts, model output, generated code, and execution results as untrusted. Apply least privilege, redaction, sandboxing, and approval gates before effects.

## Open questions

Concurrency, transactional persistence, event replay, retention, EKG/TESG relationships, evidence graphs, and scaling require future RFCs.

## Validation strategy

Use unit, contract, integration, reproducibility, and end-to-end tests appropriate to the subsystem.
