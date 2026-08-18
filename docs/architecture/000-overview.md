# 000 : Architecture Overview

## Goals

Define the stable boundaries that allow MIRAGE to evolve from EIR validation into autonomous engineering workflows.

## Non-goals

This overview does not define simulator-specific behavior, a database schema, or a particular model vendor.

## Terminology

**EIR** is the canonical engineering representation. **ESG** is current project engineering state. **EKG** is reusable cross-project knowledge. **TESG** is temporal state evolution. **EDR** records important decisions. **URCP** exposes execution capabilities.

## Requirements

The system must preserve provenance, model independence, simulator independence, reproducibility, human control, and deterministic validation.

## Architecture

MIRAGE consists of Cognitive, Knowledge, and Execution planes joined by an Engineering Compiler. Provider and future simulator adapters implement replaceable contracts.

## Interfaces

Public interfaces are EIR schemas, provider protocol types, future URCP capability definitions, CLI commands, and serialized evidence/decision artifacts.

## Data flow

Artifacts become EIR; cognitive roles request model completions; deterministic validation and capability resolution precede execution; results update evidence and state.

## Failure modes

Unsupported semantics, invalid schemas, provider failure, missing credentials, unavailable backends, and unsafe actions must be explicit and recoverable.

## Security implications

External artifacts and model output are untrusted. Credentials are runtime-only. Physical execution requires stronger gates than simulation.

## Open questions

ESG persistence, URCP transport, long-running scheduling, and simulator capability coverage remain future design work.

## Validation strategy

Architecture tests must demonstrate that provider changes do not alter EIR semantics or core orchestration behavior.

See the numbered documents in this directory for plane-specific details.
