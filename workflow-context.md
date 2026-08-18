# Workflow Context

## Task

Complete the MIRAGE declarative backend sandbox and checkpoint revalidation safety iteration.

## Current status

The sandbox and checkpoint revalidation implementation is verified and ready for a focused local commit on `feat/iteration-1-foundation`. Do not push or publish without an explicit user request.

## Completed work

The execution runtime includes policy provenance, requested timeout limits, cooperative cancellation tokens, input/output byte budgets, structured `cancelled` and `timed_out` outcomes, and a non-connecting CoppeliaSim inspection boundary. The new sandbox envelope assesses requested operating-system-level restrictions against explicit backend capability declarations. Unsupported requests are denied before backend invocation. The local backend is identified as declarative only, never as an isolated runtime.

`WorkflowCheckpoint.revalidate()` now checks stored policy provenance, exact required capability versions, active capability permission, and explicit backend allow-lists. It returns a typed result for manual review and never resumes, mutates, or executes a workflow.

Safe CLI surfaces include `mirage sandbox-assess` and `mirage checkpoint-revalidate`. The example in `examples/06-sandbox-checkpoint/` demonstrates a denied default simulation policy followed by an explicitly permitted local review. No command starts a simulator or changes host resource controls.

## Verification

| Check | Result |
|---|---|
| Python tests | 30 passed |
| Ruff | Passed for `src`, `tests`, and `scripts` |
| EIR schema consistency | Passed |
| Sandbox CLI | Declarative local assessment and unsupported memory budget denial passed |
| Checkpoint CLI | Denied default policy and explicit local simulation policy revalidation passed |
| Repository hygiene | Secret scan, tracked no-em-dash scan, and `git diff --check` passed |

## Known limitations

The sandbox is a declarative assessment only. It does not provide cgroups, containers, filesystem mounts, CPU/RAM/disk/network/process enforcement, command interception, or cleanup. Cooperative cancellation and serialized byte budgets are not OS isolation. CoppeliaSim remains unavailable and unverified, and no side-effecting or physical execution path exists.

The exact `mirage` registry name remains occupied by unrelated packages. `mirage-engineering` and `@unstable-kernel/mirage` must be rechecked immediately before any explicitly approved release. Distribution artifacts remain build-ready but unpublished.

## Important files

| File | Responsibility |
|---|---|
| `src/mirage/runtime/sandbox.py` | Sandbox envelope and backend capability assessment |
| `src/mirage/runtime/checkpoint.py` | Typed checkpoint revalidation without resume behavior |
| `src/mirage/runtime/execution.py` | Sandbox assessment before backend dispatch |
| `tests/test_sandbox_checkpoint.py` | Safety and revalidation contract coverage |
| `docs/guides/sandbox-checkpoint-revalidation.md` | Sandbox and checkpoint safety guide |
| `docs/guides/core-features.md` | Prioritized next MIRAGE core features |
| `code_review.md` | Final review and risk record for the completed iteration |

## Next recommended action

Inspect the final diff, run the complete verification suite, and create a focused local commit. Push only on explicit user request. The next implementation slice should be a verified read-only simulator project metadata and state-extraction adapter with documented transport, test fixtures, timeout handling, and no control capability.
