# 005 : Execution plane

## Goals

Define a replaceable boundary for this MIRAGE subsystem while preserving EIR, provenance, reproducibility, and human control.

## Non-goals

This document does not claim that the subsystem is implemented in Iteration 1 unless the status is stated in the repository README.

## Terminology

The subsystem consumes validated EIR and emits typed artifacts, requests, results, or evidence. Provider and backend details remain behind adapters.

## Requirements

Inputs, outputs, failure modes, versions, and security assumptions must be explicit. Unsupported features must fail clearly rather than being silently ignored.

## Architecture

The execution plane now contains URCP descriptors, a deterministic registry, an execution policy, structured execution requests/results, and replaceable backend adapters. Read-only operations are allowed by default, simulation requires explicit permission, and external or physical side effects are denied by default. Request timeout, cooperative cancellation, input/output budget checks, policy provenance, a declarative sandbox assessment, and checkpoint revalidation produce structured results. The fixture-backed read-only simulator adapter returns typed project metadata and bounded state snapshots with sandbox assessment evidence, policy checks, and no control surface. The CoppeliaSim read-only boundary reports unavailable without connecting or controlling a simulator until a transport and its semantic contract are independently verified.

## Interfaces

Public interfaces use versioned schemas, typed Python protocols, serialized artifacts, and structured diagnostics. `CapabilityExecutor` resolves a descriptor, evaluates policy, resource budget, sandbox enforceability, cancellation, and backend compatibility, invokes a backend, and returns an `ExecutionResult` with policy provenance. `ReadOnlySimulatorAdapter` exposes only `read_project_metadata()` and `read_state_snapshot()`, each returning a `ReadOnlySimulatorResult` with a sandbox assessment. `WorkflowCheckpoint.revalidate()` checks active policy and capability availability without resuming work. MIRAGE never accepts arbitrary host commands.

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
