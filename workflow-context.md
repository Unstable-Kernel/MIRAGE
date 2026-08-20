# Workflow Context

## Task

Continue MIRAGE within the active session through locally verifiable M4 workflow and governance foundations.

## Current status

The cross-artifact readiness iteration is committed locally as `d14b7dc` on `feat/iteration-1-foundation`. [PR #10](https://github.com/Unstable-Kernel/MIRAGE/pull/10) remains open against `main`. The branch is five commits ahead of its remote. The active-session local-review backlog is now complete.

## Completed work

`cross_artifact_review.py` confirms that controlled context, review trace, approval chain, deterministic report, and report provenance use one workflow and are ready for review. `review_policy.py` applies bounded, deterministic report citation rules. `workflow_readiness.py` combines these local results with the existing advisory dispatch check.

The readiness result intentionally returns `ready_for_external_prerequisites` rather than execution permission. It preserves denial reasons for missing verified live transport, actual OS-enforced sandbox evidence, and any simulation policy denial. New generic URCP declarations, local CLI commands, tests, and `examples/14-cross-artifact-readiness/` expose the integration path.

## Verification

| Check | Result |
|---|---|
| Full Python tests | 72 passed |
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
| `examples/14-cross-artifact-readiness/` | Canonical readiness policy and command example |
| `docs/guides/cross-artifact-readiness.md` | User-facing readiness contract and remaining prerequisite boundaries |

## Next recommended action

Stop autonomous execution work and request an authorized live simulator integration environment plus an OS-enforced sandbox design before starting any transport or dispatcher implementation. Push the accumulated local commits to update PR #10 only on explicit user request.
