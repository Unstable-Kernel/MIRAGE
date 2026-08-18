# 006 : Model orchestrator

## Goals

Define a replaceable boundary for this MIRAGE subsystem while preserving EIR, provenance, reproducibility, and human control.

## Non-goals

This document describes the implemented provider-neutral orchestration foundation and its planned extensions.

## Terminology

The subsystem accepts typed completion requests and emits normalized completion responses. Provider transport details remain behind adapters.

## Requirements

Inputs, outputs, failure modes, versions, and security assumptions must be explicit. Unsupported features must fail clearly rather than being silently ignored.

## Architecture

The current implementation provides a provider-neutral completion contract, role-based provider selection, configuration validation, normalized errors, and explicit adapters for OpenAI, Anthropic, generic OpenAI-compatible endpoints, Ollama, vLLM, and llama.cpp. Planning, debate, uncertainty aggregation, and autonomous multi-agent runtime behavior remain planned.

## Interfaces

Public interfaces use typed completion requests and responses, provider adapter protocols, provider configuration models, role mappings, and structured diagnostics.

## Data flow

Role and request input select a configured provider adapter; the adapter normalizes the transport result; callers receive a provider-neutral response or structured failure.

## Failure modes

Malformed input, missing dependencies, unavailable capabilities, timeouts, inconsistent state, and authorization failures are recoverable structured errors.

## Security implications

Treat external artifacts, model output, generated code, and execution results as untrusted. Apply least privilege, redaction, sandboxing, and approval gates before effects.

## Open questions

Provider fallback policy, cache policy, streaming semantics, rate-limit coordination, budget enforcement, and long-running multi-agent orchestration require future RFCs.

## Validation strategy

Use unit, contract, integration, reproducibility, and end-to-end tests appropriate to the subsystem.
