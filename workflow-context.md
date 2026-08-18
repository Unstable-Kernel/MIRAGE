# Workflow Context

## Task

Complete the MIRAGE execution-hardening iteration after the distribution-readiness phase.

## Current status

The execution-hardening implementation and verification are complete. The working tree is ready for a focused local commit on `feat/iteration-1-foundation`. Do not push or publish without an explicit user request.

## Completed work

The runtime includes append-only JSONL `ExecutionLedger` with stable request IDs, execution status, actor, capability, version, backend, timestamps, policy summary, redacted inputs and outputs, and lookup by request ID. The URCP executor records denied, unavailable, and successful execution attempts when a ledger is provided.

The runtime includes validated `WorkflowCheckpoint` snapshots with workflow ID, revision, stage, arbitrary state, related execution IDs, optional ESG project ID, and update time. Checkpoints can advance and round-trip through JSON. Loading a checkpoint never executes or resumes work.

The registry-safe Python distribution is named `mirage-engineering`, with PEP 440 alpha version `0.1.0a0` sourced from `mirage.__version__`. The `mirage` console command remains the canonical user-facing CLI. The scoped `@unstable-kernel/mirage` npm launcher is private and delegates to that Python command instead of reimplementing MIRAGE in JavaScript. CI validates Python and npm artifacts but contains no publishing automation.

The execution runtime now supports policy provenance, requested timeout limits, cooperative cancellation tokens, input/output byte budgets, and structured `cancelled` and `timed_out` outcomes. The `simulator-inspect` CLI command reaches only a non-connecting CoppeliaSim inspection boundary and never controls a simulator. The current source documents the next core features in `docs/guides/core-features.md`.

## Verification

| Check | Result |
|---|---|
| Python tests | 26 passed |
| Ruff | Passed for `src`, `tests`, and `scripts` |
| EIR schema consistency | Passed |
| Python build | Source archive and wheel passed `twine check` during the distribution phase |
| Installed Python artifact | Metadata and `mirage doctor` passed during the distribution phase |
| npm launcher | Forwarding tests, syntax check, and dry-run package check passed during the distribution phase |
| Execution hardening | Timeout, cancellation, resource-limit, policy-provenance, and inspection-boundary tests passed |
| Repository hygiene | Secret scan, tracked no-em-dash scan, and `git diff --check` passed |

## Known limitations

The ledger is local JSONL storage without file locking, encryption, retention policies, database transactions, or distributed coordination. Checkpoints are validated snapshots and do not resume work automatically. CoppeliaSim remains unavailable and unverified. No external side effects or physical actuation are exposed. Cancellation is cooperative and byte budgets are not operating-system resource isolation.

The exact `mirage` registry name is occupied by unrelated packages on PyPI and npm. `mirage-engineering` and `@unstable-kernel/mirage` returned no registry record during the distribution build, but availability must be checked again immediately before release. Publishing remains a manual, explicitly authorized maintainer action that needs a signed tag, clean verification, artifact review, release note, and configured trusted publishing.

## Important files

| File | Responsibility |
|---|---|
| `src/mirage/runtime/execution.py` | Execution policy, provenance, timeout, cancellation, budgets, and result statuses |
| `src/mirage/runtime/simulator_inspection.py` | Non-connecting inspection-only simulator boundary |
| `tests/test_execution_hardening.py` | Execution-hardening contract coverage |
| `docs/guides/execution-hardening.md` | Hardening semantics and safety limitations |
| `docs/guides/core-features.md` | Prioritized outline of upcoming MIRAGE core features |
| `code_review.md` | Final collaborator review covering runtime, distribution, and execution-hardening risks |

## Next recommended action

Inspect the final diff, run final hardening checks, and create a focused local commit. Push only on explicit user request. Do not publish to PyPI or npm unless the user explicitly approves that sensitive release operation. The next build slice should implement verified read-only simulator project metadata and state extraction before any simulator control path.
