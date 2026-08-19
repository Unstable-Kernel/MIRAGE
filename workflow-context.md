# Workflow Context

## Task

Complete the deterministic workflow and verification-integrity iteration for MIRAGE.

## Current status

The iteration is committed locally as `3a3a819` on `feat/iteration-1-foundation`. The branch is three commits ahead of its remote and [PR #9](https://github.com/Unstable-Kernel/MIRAGE/pull/9) remains open against `main`. Do not push or publish without an explicit user request.

## Completed work

`workflow_evidence.py` introduces deterministic EIR-to-plan validation. A proposed workflow must identify the supplied EIR document and each step must cite one or more existing EIR nodes. The resulting `DeterministicWorkflowPlan` is an explicit review artifact with `execution_permitted: false`.

`assess_evaluation_evidence()` validates criterion coverage and ensures every cited evidence source appears in the deterministic plan. It reports insufficient or invalid evidence rather than inferring engineering correctness. `goal-workflow-plan` and `goal-workflow-evidence` expose these local inspection paths through the CLI.

Transport and sandbox claim integrity is stricter. A future `live_verified` transport record needs authorization, observed version, independent verifier, transcript digest, and cleanup verification. A future `verified` sandbox record needs evidence digest, environment fingerprint, verifier, and controls. No live or OS-enforced evidence record is included in the repository.

`examples/09-deterministic-workflow/` binds a review-only workflow and criterion evidence to `examples/01-validate-eir/robot_model.yaml`. The URCP registry now includes `assess_workflow_evidence@0.1` as a read-only declaration.

## Verification

| Check | Result |
|---|---|
| Full Python tests | 53 passed |
| Ruff | Passed for `src`, `tests`, and `scripts` |
| EIR schema consistency | Passed |
| Documentation verification | Every tracked Markdown file passed local-link checks |
| CLI verification | Deterministic workflow plan, evidence assessment, and generic capability discovery passed |
| Repository hygiene | Secret scan, tracked no-em-dash scan, and `git diff --check` passed |

## Known limitations

The workflow plan and evidence assessment validate references and coverage only. They do not generate a plan with a model, decide engineering correctness, obtain real measurements, execute a simulator, dispatch a capability, resume a checkpoint, approve a workflow, or create a report.

The CoppeliaSim transport remains unverified and non-connecting. The local sandbox remains declarative. Integrity fields prevent incomplete evidence claims but do not create an authorized endpoint, a network client, a cgroup, a container, a filesystem mount, or a process supervisor.

## Important files

| File | Responsibility |
|---|---|
| `src/mirage/runtime/workflow_evidence.py` | Deterministic EIR-to-plan and evaluation-evidence review artifacts |
| `src/mirage/runtime/goal_workflow.py` | Goal workflow source-node references and manual-review checkpoint contract |
| `src/mirage/runtime/transport_verification.py` | Future live transport evidence admission requirements |
| `src/mirage/runtime/sandbox.py` | Future verified sandbox evidence admission requirements |
| `src/mirage/cli.py` | `goal-workflow-plan` and `goal-workflow-evidence` local inspection commands |
| `examples/09-deterministic-workflow/` | Canonical EIR-bound workflow and evidence fixtures |
| `docs/guides/deterministic-workflow-evidence.md` | User-facing contract, limitations, and CLI guide |

## Next recommended action

Await an explicit request before pushing the three local commits to update PR #9. The next build phase should add controlled context inputs and real evidence adapters only after an authorized live read-only transport and real OS-enforced sandbox are independently verified.
