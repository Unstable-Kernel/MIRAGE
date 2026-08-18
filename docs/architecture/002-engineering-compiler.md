# 002 : Engineering Compiler

## Goals

Normalize heterogeneous engineering artifacts into EIR and eventually lower validated EIR into executable capability graphs.

## Non-goals

The first iteration does not parse source repositories, papers, URDF, MATLAB, or CAD.

## Terminology

A **frontend** extracts structured facts. **Normalization** maps them into EIR. **Verification** checks deterministic invariants. **Lowering** produces a backend-specific artifact or capability request.

## Requirements

Every extracted fact carries provenance and, where appropriate, confidence. Unsupported semantics are reported rather than dropped.

## Architecture

Future frontends feed an EIR builder. The builder validates identifiers, relationships, units, schema version, and provenance before a compiler stage creates an execution graph.

## Interfaces

Frontends accept artifacts and emit EIR candidates. Validators emit structured diagnostics. Backends accept only validated EIR or execution graphs.

## Data flow

Artifact → frontend → candidate EIR → validation → normalized EIR → lowering → adapter.

## Failure modes

Parser errors, ambiguous extraction, missing parameters, schema mismatch, unsupported features, and backend incompatibility must be visible.

## Security implications

Parsing must not execute untrusted code. Generated artifacts must be sandboxed and reviewed before external execution.

## Open questions

Future RFCs must define incremental indexing, compiler passes, and reproducibility metadata.

## Validation strategy

Golden EIR fixtures, schema tests, round-trip tests, and adapter contract tests are required for each frontend/backend.
