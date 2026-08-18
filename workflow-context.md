# Workflow Context

## Task

Complete the MIRAGE distribution-readiness phase after the execution ledger and workflow checkpoint slice.

## Current status

Python and npm distribution artifacts are build-ready and locally verified. The distribution phase is committed locally as `122b8a8` (`feat: prepare MIRAGE distribution artifacts`) on `feat/iteration-1-foundation`. The user has approved pushing the branch and opening a pull request. Do not publish package artifacts without a separate explicit user approval.

## Completed work

The runtime includes append-only JSONL `ExecutionLedger` with stable request IDs, execution status, actor, capability, version, backend, timestamps, policy summary, redacted inputs and outputs, and lookup by request ID. The URCP executor records denied, unavailable, and successful execution attempts when a ledger is provided.

The runtime includes validated `WorkflowCheckpoint` snapshots with workflow ID, revision, stage, arbitrary state, related execution IDs, optional ESG project ID, and update time. Checkpoints can advance and round-trip through JSON. Loading a checkpoint never executes or resumes work.

The registry-safe Python distribution is named `mirage-engineering`, with PEP 440 alpha version `0.1.0a0` sourced from `mirage.__version__`. The `mirage` console command remains the canonical user-facing CLI. The scoped `@unstable-kernel/mirage` npm launcher is private and delegates to that Python command instead of reimplementing MIRAGE in JavaScript. CI validates Python and npm artifacts but contains no publishing automation.

## Verification

| Check | Result |
|---|---|
| Python tests | 21 passed |
| Ruff | Passed for `src`, `tests`, and `scripts` |
| EIR schema consistency | Passed |
| Python build | Source archive and wheel passed `twine check` |
| Installed Python artifact | Metadata and `mirage doctor` passed |
| npm launcher | Forwarding tests, syntax check, and dry-run package check passed |
| Secret and punctuation checks | Passed during the Iteration 3 verification |

## Known limitations

The ledger is local JSONL storage without file locking, encryption, retention policies, database transactions, or distributed coordination. Checkpoints are validated snapshots and do not resume work automatically. CoppeliaSim remains unavailable and unverified. No external side effects or physical actuation are exposed.

The exact `mirage` registry name is occupied by unrelated packages on PyPI and npm. `mirage-engineering` and `@unstable-kernel/mirage` returned no registry record during this build, but availability must be checked again immediately before release. Publishing remains a manual, explicitly authorized maintainer action that needs a signed tag, clean verification, artifact review, release note, and configured trusted publishing.

## Important files

| File | Responsibility |
|---|---|
| `pyproject.toml` | Python distribution identity, dynamic version source, console entry point, and wheel configuration |
| `packages/npm-launcher/` | Private scoped npm launcher package and tests |
| `docs/guides/distribution.md` | Release naming, artifact verification, and publishing boundary |
| `.github/workflows/ci.yml` | Test, Python artifact, and npm package checks without release automation |
| `code_review.md` | Final collaborator review covering runtime and distribution risks |

## Next recommended action

Push the current branch, create or update the pull request against `main`, and keep package publishing disabled. The next build slice should add request-level timeout, cancellation, resource limits, and a verified simulator inspection adapter before any simulator control path.
