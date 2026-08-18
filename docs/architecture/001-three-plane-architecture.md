# 001 : Three-Plane Architecture

## Goals

Keep cognition, semantic knowledge, and execution independently testable.

## Non-goals

No implementation of a graph database, scheduler, or hardware controller is included in Iteration 1.

## Terminology

Cognitive Plane proposes; Knowledge Plane represents and remembers; Execution Plane resolves and performs capabilities.

## Requirements

No plane may bypass EIR or call an implementation-specific backend without a declared adapter contract.

## Architecture

The Cognitive Plane consumes goals and evidence. The Knowledge Plane stores EIR and implemented revisioned ESG snapshots with append-only events; EKG, TESG, evidence graphs, and EDRs remain future artifacts. The Execution Plane exposes implemented URCP descriptors, policy-gated execution, and bounded adapters.

## Interfaces

The boundaries are typed requests, EIR documents, capability descriptors, result artifacts, and evidence records.

## Data flow

Goal → cognitive request → EIR/context → capability request → adapter → result → evidence/state.

## Failure modes

Invalid representation, unavailable capability, permission denial, timeout, and inconsistent evidence are surfaced as structured failures.

## Security implications

The Cognitive Plane cannot directly issue arbitrary host or hardware commands. Execution requires policy checks.

## Open questions

Future work must decide whether inter-plane communication is in-process, RPC, event-driven, or a combination.

## Validation strategy

Mock each boundary independently and verify that provider or backend substitutions preserve contract behavior.
