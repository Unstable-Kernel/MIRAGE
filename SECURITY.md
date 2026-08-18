# MIRAGE Security Policy

## Scope

MIRAGE processes engineering artifacts and may eventually produce actions for simulators, toolchains, and physical systems. This policy applies to source code, provider adapters, EIR, generated artifacts, logs, and future execution backends.

## Credential handling

API keys and provider credentials must be supplied through environment variables or a user-owned configuration file outside version control. They must never be committed, placed in prompts, serialized into EIR, emitted in logs, included in exceptions, or stored in test snapshots. Configuration objects expose redacted representations. CI performs secret scanning.

## Data routing

The selected provider determines where model input is sent. Users must be able to choose cloud, compatible, or local providers explicitly. Documentation must identify provider endpoints, retention assumptions that are known to the adapter, and local-only options. MIRAGE must not silently route data to a fallback provider without recording and exposing that decision.

## Threat model

Treat research papers, repositories, CAD files, configuration files, datasets, logs, and model responses as untrusted data. Threats include prompt injection, poisoned artifacts, malicious parsers, arbitrary code execution, credential exfiltration, unsafe generated control logic, simulator-to-real transfer error, and disclosure of proprietary engineering data.

## Execution boundaries

MIRAGE does not execute real simulators or hardware. The fixture-backed read-only adapter only parses deterministic local data and cannot connect to, control, or step a simulator. Future real execution must use capability allow-lists, least privilege, isolated workspaces, verifiable network and resource enforcement, timeouts, cancellation, approval gates, audit logs, and emergency-stop integration. An LLM must never directly emit unrestricted physical actuation commands.

## Verification

Deterministic validation must run before expensive simulation or external execution. Important claims must identify their evidence class: model-generated, symbolically derived, deterministically validated, simulation-supported, experimentally supported, or published. Simulation success is not proof of physical correctness.

## Vulnerability reporting

Please report security issues privately to `kshitiz23kumar@gmail.com` with the subject `MIRAGE Security Report`. Include impact, reproduction steps, affected revision, and a safe disclosure contact. Do not publish credentials or sensitive engineering artifacts in an issue.

## Disclosure

Maintainers will acknowledge reports, reproduce issues in an isolated environment, coordinate remediation, and publish a disclosure summary when appropriate. Please do not test physical hardware or third-party systems without explicit authorization.
