# MIRAGE Code Review

## Review scope

This review covers the ESG and URCP vertical slice, policy-gated execution, the append-only execution ledger, workflow checkpoints, backend boundaries, CLI commands, specifications, examples, and tests added through Iteration 3.

## Architecture summary

```mermaid
flowchart TD
    EIR[EIR 0.1 document] --> ESG[Engineering State Graph]
    ESG --> EVENTS[Revisioned event history]
    URCP[URCP capability descriptors] --> REG[Deterministic registry]
    REG --> CLI[CLI discovery commands]
    ESG --> CLI
    REG --> EXEC[Policy-gated executor]
    EXEC --> LOCAL[Deterministic local backend]
    EXEC -. explicit boundary .-> SIM[CoppeliaSim, unavailable until verified]
    EXEC --> LEDGER[Append-only audit ledger]
    LEDGER --> CHECKPOINT[Validated workflow checkpoint]
    CHECKPOINT -. future resume after revalidation .-> EXEC
```

The implementation keeps the correct separation between semantic state, execution declarations, audit history, and resumable workflow state. ESG stores current project state around an EIR document, URCP describes capabilities, the executor applies policy, the ledger records attempts, and checkpoints preserve validated state without automatically resuming work.

## Important files

| File | Responsibility |
|---|---|
| `src/mirage/knowledge/esg.py` | ESG event model, revision tracking, duplicate-event protection, JSON persistence |
| `src/mirage/runtime/urcp.py` | Capability descriptor, security classification, registry, default declarations |
| `src/mirage/runtime/execution.py` | Execution policy, request/result types, executor, local backend, CoppeliaSim boundary |
| `src/mirage/runtime/ledger.py` | Append-only JSONL audit records, request IDs, redaction, persistence, and lookup |
| `src/mirage/runtime/checkpoint.py` | Validated workflow checkpoint snapshots and revisioning |
| `src/mirage/runtime/` | Public runtime exports for execution, ledger, checkpoint, and URCP APIs |
| `src/mirage/cli.py` | EIR, ESG, URCP, execution, ledger, checkpoint, and doctor commands |
| `tests/test_ledger_checkpoint.py` | Ledger persistence, redaction, execution recording, and checkpoint coverage |
| `docs/guides/execution-ledger.md` | Ledger and checkpoint semantics |
| `examples/05-ledger-checkpoint/` | Audit and checkpoint workflow example |
| `specs/URCP/README.md` | URCP execution, policy, and adapter contract |

## Strengths

The ESG model preserves the EIR document as the canonical semantic payload. Revision numbers and append-only events make state changes inspectable without requiring a database. Duplicate event IDs are rejected, and persisted snapshots round-trip through Pydantic validation.

The URCP registry is deterministic and declarative. It rejects duplicate capability/version pairs, requires an exact version when multiple versions exist, supports backend and security-class filtering, and returns stable ordering. The descriptor records execution metadata including side effects, failure modes, determinism, cancellation, resource requirements, and security classification.

The execution policy has safe defaults. Read-only operations are allowed by default, simulation requires explicit permission, and external side effects and physical actuation remain denied. The local backend is deterministic test infrastructure. The CoppeliaSim boundary explicitly reports unavailable instead of claiming unverified support.

The ledger records denied, unavailable, and successful attempts when enabled. Secret-looking keys are redacted before persistence. Checkpoints are validated snapshots and do not execute instructions on load.

## Risks and follow-up work

The ESG is currently an in-process snapshot model. A future persistence layer must define concurrency, transactional updates, event replay, corruption recovery, and migration. Event references should eventually be validated against the active EIR document.

The local ledger has no file locking, encryption, retention policy, database transactions, distributed coordination, adapter lifecycle management, capability negotiation, resource isolation, timeout cancellation, or external policy service. These are required before the ledger becomes a production control-plane component.

Checkpoint resume must revalidate the current capability registry and execution policy before any future action. Loading a checkpoint must remain non-executable by default.

The default registry includes simulator names for planning and filtering only. The CoppeliaSim boundary must not be treated as simulator support. A verified adapter should add a concrete transport, environment detection, capability coverage, deterministic fixtures where possible, resource and timeout policy, and explicit limitations.

## Tests and verification

The current verification suite passes with 19 tests. Ruff passes for source, tests, and scripts. The EIR schema consistency check passes. ESG CLI snapshot inspection, URCP backend filtering, policy denial, deterministic local execution, unavailable CoppeliaSim behavior, audit persistence, secret redaction, checkpoint round trips, ledger inspection, checkpoint inspection, secret-pattern scanning, tracked no-em-dash scanning, and repository diff checks pass.

## Collaborator guidance

Keep EIR, ESG, and URCP versioned independently. Do not add simulator-specific fields to EIR or core orchestration merely to support one backend. Add a new capability descriptor before adding an executor, and add a contract test before claiming backend support. Preserve secret redaction, provenance, deterministic validation, and explicit safety boundaries.

## Recommended next slice

Add file locking or a transactional storage backend, request-level timeout and cancellation semantics, resource limits, ledger retention and integrity policy, and stronger policy provenance. Then verify one simulator adapter, starting with project inspection and state extraction before simulation control or experiment execution.

## Distribution readiness review

The release-readiness slice keeps the Python runtime authoritative and makes the npm surface intentionally thin. The `mirage-engineering` Python distribution is configured through Hatchling with the in-package `mirage.__version__` as its version source. The current alpha version is `0.1.0a0`, which is both PEP 440 compliant and accurately signals pre-release status.

```mermaid
flowchart LR
    PYPI[mirage-engineering wheel and source archive] --> PYCLI[mirage Python CLI]
    NPM[@unstable-kernel/mirage private launcher] --> PYCLI
    PYCLI --> CORE[MIRAGE runtime]
    CORE --> EIR[EIR and validation]
    CORE --> SAFE[URCP policy-gated execution]
```

| File | Distribution responsibility |
|---|---|
| `pyproject.toml` | Registry-safe Python project identity, classifiers, URLs, dynamic version source, console script, and Hatchling wheel configuration |
| `src/mirage/__init__.py` | Installed package version and maintainer identity |
| `tests/test_distribution.py` | Validates in-package and installed distribution metadata agreement |
| `packages/npm-launcher/` | Private scoped launcher that forwards to the installed Python CLI |
| `docs/guides/distribution.md` | Package naming, artifact checks, release ownership, and non-publication boundary |
| `.github/workflows/ci.yml` | Python artifact and npm launcher checks with no publishing workflow |

The npm launcher forwards CLI arguments to the `mirage` binary or to `MIRAGE_COMMAND` for controlled environments. It correctly fails with an actionable message when the runtime is absent. It does not install Python automatically, download binaries, send telemetry, or duplicate the engineering runtime in JavaScript.

## Release-specific risks

The names `mirage-engineering` and `@unstable-kernel/mirage` were available during this build but registry availability is time-sensitive. A maintainer must check both names again immediately before publishing. No publish token, registry credential, or release automation belongs in this repository or CI until explicit release ownership and trusted-publishing configuration are approved.

The Python CI artifact job must install the built wheel in an environment that is not shadowed by the checkout when this becomes a release gate. The local verification confirms the wheel metadata and command entry point, but a future isolated environment test will provide stronger assurance. The npm launcher is deliberately marked `private: true`; changing that flag is a release decision, not a routine code change.

## Updated verification

The full suite now passes with 21 tests. Ruff, EIR schema consistency, Python source and wheel builds, `twine check`, installed-wheel metadata verification, `mirage doctor`, npm launcher forwarding tests, Node syntax checks, and `npm pack --dry-run` all passed. The build phase did not publish, reserve, or upload an artifact to any registry.

## Commit and review handoff

The distribution-readiness implementation is committed as `122b8a8` with the message `feat: prepare MIRAGE distribution artifacts`. The commit contains no co-author trailer or AI attribution. Its pull request should be reviewed as a release-preparation change only: it adds build metadata, package checks, documentation, and a private launcher, but it does not authorize or perform a PyPI or npm release.

## Execution hardening iteration review

The execution runtime now applies an explicit policy-provenance record and resource budget to every returned result. The runtime checks backend allow-lists, input size, and requested timeout before a backend receives work. It then uses a cooperative cancellation token, timeout wait, and output-size check to make policy outcomes observable rather than implicit.

```mermaid
flowchart LR
    REQUEST[Execution request] --> PRECHECK[Policy, backend, and input checks]
    PRECHECK -->|deny| RESULT[Structured result and ledger]
    PRECHECK -->|allow| BACKEND[Cooperative backend task]
    BACKEND --> HARDEN[Cancellation, timeout, and output checks]
    HARDEN --> RESULT
    INSPECT[Inspection-only simulator boundary] -->|unavailable| RESULT
```

| File | Hardening responsibility |
|---|---|
| `src/mirage/runtime/execution.py` | Timeout, cancellation token, input/output byte limits, policy provenance, and structured status results |
| `src/mirage/runtime/simulator_inspection.py` | Non-connecting, inspection-only CoppeliaSim boundary with no control surface |
| `src/mirage/cli.py` | `--timeout-seconds` execution option and `simulator-inspect` command |
| `tests/test_execution_hardening.py` | Preflight denial, timeout, cancellation, provenance, and inspection-boundary coverage |
| `docs/guides/execution-hardening.md` | User-facing enforcement sequence and safety limitations |
| `docs/guides/core-features.md` | Prioritized upcoming MIRAGE core-feature roadmap |

The inspection boundary is correctly conservative. It records endpoint configuration only and explicitly reports that no connection or control action occurred. It does not implement simulator state extraction, transport negotiation, project loading, scene traversal, simulation control, or actuator access.

## Hardening risks and follow-up work

Cancellation is cooperative within the current Python task model. A backend that blocks in non-cooperative native code, a subprocess, or a remote server still needs an external sandbox, process management, resource cgroup, deadline propagation, and cleanup contract. Current byte budgets are deterministic serialized-payload checks, not CPU, RAM, disk, GPU, network, or process limits.

The next verified adapter slice should implement read-only simulator project metadata and state extraction using a documented transport with test fixtures. Only after transport, authorization, state semantics, timeout behavior, and cleanup have verification evidence should MIRAGE consider any simulator control capability.

## Updated verification

The suite now passes with 26 tests. Ruff, EIR schema consistency, safe CLI inspection, explicit local execution with a timeout budget, secret-pattern scanning, tracked no-em-dash scanning, and `git diff --check` passed. No simulator connection, control operation, external side effect, physical actuation, package publication, or release upload occurred.

## Sandbox and checkpoint revalidation iteration review

The sandbox envelope implementation is deliberately declarative. A `SandboxEnvelope` describes CPU, memory, disk, process, network, filesystem, and subprocess restrictions. `BackendSandboxCapabilities` makes a backend's claimed enforcement explicit. MIRAGE compares the two before dispatch and denies work that requests operating-system-level restrictions the backend cannot enforce.

```mermaid
flowchart LR
    POLICY[Execution policy] --> ENVELOPE[Sandbox envelope]
    ENVELOPE --> CAPS[Backend sandbox capabilities]
    CAPS --> ASSESS[Assessment]
    ASSESS -->|denied| RESULT[Structured execution result]
    ASSESS -->|declarative only| LOCAL[Deterministic local backend]
    CHECKPOINT[Workflow checkpoint] --> REVALIDATE[Policy and capability revalidation]
    REVALIDATE --> REVIEW[Manual review only]
```

| File | Safety responsibility |
|---|---|
| `src/mirage/runtime/sandbox.py` | Declared envelope, backend enforcement claims, and conservative assessment |
| `src/mirage/runtime/execution.py` | Sandbox preflight denial and execution-result assessment metadata |
| `src/mirage/runtime/checkpoint.py` | Non-executing policy and capability revalidation for manual resume review |
| `tests/test_sandbox_checkpoint.py` | Declarative local outcome, unsupported resource denial, and checkpoint drift coverage |
| `docs/guides/sandbox-checkpoint-revalidation.md` | User-facing boundary and safe CLI behavior |

Checkpoint revalidation is correctly non-executing. It compares stored policy provenance, exact capability versions, policy permission, and explicit backend allow-lists before a checkpoint can enter a future human review flow. It never changes the checkpoint or invokes a backend.

## Sandbox-specific risks and next step

The implementation does not create an OS sandbox. The local backend has no cgroup, process supervisor, filesystem mount, network firewall, container runtime, CPU quota, memory limit, disk quota, GPU partition, subprocess interceptor, or forced cleanup. These restrictions are denied when requested instead of being represented as successful enforcement.

The next safe implementation should add one verified read-only simulator metadata and state-extraction adapter with test fixtures and a documented transport. An enforced backend sandbox should follow only after the project has a suitable isolated runtime and an auditable OS-level policy enforcement design.

## Updated verification

The suite now passes with 30 tests. Ruff, EIR schema consistency, sandbox assessment CLI, denied sandbox budget CLI, checkpoint revalidation CLI for both denied and explicitly allowed cases, secret-pattern scanning, tracked no-em-dash scanning, and diff integrity checks passed. No checkpoint was resumed, no process isolation was claimed, and no simulator connection or control operation occurred.
