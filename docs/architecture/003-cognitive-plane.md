# 003 — Cognitive Plane

## Goals

Transform engineering goals and evidence into structured proposals, plans, questions, and explanations.

## Non-goals

The Cognitive Plane does not parse files directly, validate physical semantics, or call simulator APIs.

## Terminology

A role is a typed reasoning responsibility. A proposal is probabilistic output that must pass deterministic checks before execution.

## Requirements

Provider selection is role-based and replaceable. Prompts and responses must preserve safe provenance and redacted traces.

## Architecture

The plane contains future planning, reasoning, debate, reflection, and explanation components. Iteration 1 supplies only the provider-neutral orchestrator.

## Interfaces

Inputs are goals, EIR, evidence, and constraints. Outputs are structured plans, capability requests, explanations, and confidence-bearing proposals.

## Data flow

Goal/context → role request → model adapter → normalized response → deterministic parser/validator.

## Failure modes

Low confidence, malformed structured output, provider error, unsupported modality, timeout, and conflicting proposals are explicit outcomes.

## Security implications

Model output is untrusted. API keys are never placed in prompts. No cognitive output can directly actuate hardware.

## Open questions

Future work must define debate protocol, uncertainty aggregation, and human approval UX.

## Validation strategy

Mock each provider and assert identical normalized behavior for equivalent requests.
