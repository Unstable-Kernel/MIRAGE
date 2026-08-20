# Workflow Context

## Task

Continue MIRAGE within the active session through locally verifiable M4 workflow and governance foundations.

## Current status

The cross-artifact readiness iteration is committed locally as `d14b7dc` on `feat/iteration-1-foundation`. [PR #10](https://github.com/Unstable-Kernel/MIRAGE/pull/10) is merged into `main`. The current active-loop iteration adds local ledger integrity and retention work and remains unpushed pending the focused local commit. A three-hour autonomous build review is active.

## Completed work

`cross_artifact_review.py` confirms that controlled context, review trace, approval chain, deterministic report, and report provenance use one workflow and are ready for review. `review_policy.py` applies bounded, deterministic report citation rules. `workflow_readiness.py` combines these local results with the existing advisory dispatch check. `ledger.py` now writes versioned audit envelopes with canonical chained digests, local advisory locking, integrity assessment, append refusal after verification failure, and bounded retention compaction with an explicit anchor.

The readiness result intentionally returns `ready_for_external_prerequisites` rather than execution permission. It preserves denial reasons for missing verified live transport, actual OS-enforced sandbox evidence, and any simulation policy denial. New generic URCP declarations, local CLI commands, tests, and `examples/14-cross-artifact-readiness/` expose the integration path.

## Verification

| Check | Result |
|---|---|
| Full Python tests | 78 passed |
| Ruff | Passed for `src`, `tests`, and `scripts` |
| EIR schema consistency | Passed |
| Documentation verification | Every tracked Markdown file passed local-link checks |
| CLI verification | Cross-artifact, review-policy, readiness, and generic capability inspection passed |
| Repository hygiene | Secret scan, tracked no-em-dash scan, and `git diff --check` passed |

## Blocking external prerequisites

The local review foundation is complete. Continuing toward any execution phase now requires an independently verified, authorized live read-only simulator transport and a real OS-enforced sandbox backend. The repository does not have endpoint credentials, transport access, observed simulator semantics, process isolation, cgroups, filesystem mounts, network policy, resource-quota enforcement, or cleanup supervision.

No further safe execution, control, experiment, optimization, external side-effect, or physical-actuation slice should be implemented until those prerequisites are supplied and independently verified. A future task may instead proceed with an approved integration environment, credentials handled through the appropriate secure flow, and a concrete enforced runtime design.

## Important files

| File | Responsibility |
|---|---|
| `src/mirage/runtime/cross_artifact_review.py` | Workflow-wide consistency validation for review artifacts |
| `src/mirage/runtime/review_policy.py` | Deterministic local review-policy constraints |
| `src/mirage/runtime/workflow_readiness.py` | Non-executing readiness and external denial aggregation |
| `src/mirage/runtime/ledger.py` | Local advisory-locked digest envelope, integrity assessment, and bounded retention compaction |
| `examples/14-cross-artifact-readiness/` | Canonical readiness policy and command example |
| `examples/15-ledger-integrity/` | Canonical retained local ledger fixture and integrity inspection command |
| `docs/guides/cross-artifact-readiness.md` | User-facing readiness contract and remaining prerequisite boundaries |

## Next recommended action

The schedule `Every 3 hours MIRAGE build review` is active every 10,800 seconds, equivalent to every three hours, in `Asia/Calcutta`. On each run, inspect `/home/ubuntu/MIRAGE` on `feat/iteration-1-foundation`, `workflow-context.md`, `todo.md`, `code_review.md`, `ROADMAP.md`, and the PR state, then select only the next coherent locally verifiable slice. Permitted work is deterministic review, validation, provenance, documentation, and contract work that does not require external credentials or infrastructure. The schedule must keep simulator control, physical actuation, external side effects, live transport, OS-level sandbox claims, retrieval, credential handling, durable authority mutation, package publication, and branch push disabled. Every completed slice must include tests, examples, documentation, code review, workflow context, todo updates, full verification, and focused local commits without co-author attribution. If the next slice requires an authorized live simulator environment or a real OS-enforced sandbox, stop and report the precise prerequisite. The next safe candidate after the ledger integrity slice is a local EIR ingestion-adapter contract, provided it only parses controlled local inputs with provenance and does not introduce retrieval. Do not push or publish without explicit user approval.
