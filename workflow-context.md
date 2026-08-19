# Workflow Context

## Task

Complete the parallel foundation iteration for transport verification, sandbox enforcement evidence, and the M4 goal-to-evaluate workflow review model.

## Current status

The combined implementation is verified and ready for a focused local commit on `feat/iteration-1-foundation`. The branch already has [PR #9](https://github.com/Unstable-Kernel/MIRAGE/pull/9) open against `main`. Do not push the new commit or publish any package without an explicit user request.

## Completed work

Three independent tracks were developed together. `transport_verification.py` introduces versioned read-only transport manifests, deterministic evidence, and assessment reports. The CoppeliaSim ZeroMQ reference manifest records only protocol vocabulary, permitted reads, and prohibited controls. It remains unverified and non-connecting.

`SandboxEnforcementEvidence` now supplements backend capability declarations. An OS-enforced envelope must have matching verified evidence for every requested control before assessment can return `allowed`. The default local backend remains declarative only. Test-only evidence demonstrates the acceptance contract and does not create host isolation.

`goal_workflow.py` introduces a bounded M4 review model with a goal, EIR identifier, no more than eight proposed steps, no more than eight evaluation criteria, policy-bound checkpoint creation, and non-executing checkpoint revalidation. Every review requires human approval and always reports `execution_permitted: false`.

The URCP registry exposes `review_goal_workflow@0.1` as read-only. CLI commands `transport-assess` and `goal-workflow-review` read deterministic local JSON. `examples/08-parallel-foundations/` contains the canonical manifest, evidence, workflow, and usage guide.

## Verification

| Check | Result |
|---|---|
| Full Python tests | 45 passed |
| Ruff | Passed for `src`, `tests`, and `scripts` |
| EIR schema consistency | Passed |
| Documentation verification | Every tracked Markdown file passed local-link checks |
| CLI verification | Generic capability discovery, fixture transport assessment, workflow review, and unavailable CoppeliaSim metadata inspection passed |
| Repository hygiene | Secret scan, tracked no-em-dash scan, and `git diff --check` passed |

## Known limitations

The CoppeliaSim manifest does not verify a live endpoint. Its ZeroMQ API can control simulators, so a future adapter must prove an allow-listed read-only client, auth boundary, observed version semantics, timeout cleanup, independent fixtures, and safety review before live transport verification.

The sandbox evidence model is not an OS sandbox. No cgroup, container, filesystem mount, network policy, process limit, resource quota, or cleanup supervisor exists in the local backend. A real isolated backend must provide observed enforcement evidence, not a static model.

The M4 foundation does not plan through a model, execute capabilities, resume checkpoints, collect evidence, evaluate results, or create reports. It only preserves a reviewable proposal and detects policy or capability drift. Simulator control, external side effects, physical actuation, package publication, and automatic workflow execution remain absent.

## Important files

| File | Responsibility |
|---|---|
| `src/mirage/runtime/transport_verification.py` | Read-only transport manifests, evidence, and no-connection assessment |
| `src/mirage/runtime/sandbox.py` | Envelope capability and enforcement-evidence assessment |
| `src/mirage/runtime/goal_workflow.py` | Human-review-only goal-to-evaluate workflow contracts |
| `src/mirage/runtime/simulator_adapter.py` | Fixture adapter and unavailable CoppeliaSim manifest observations |
| `src/mirage/cli.py` | Transport and workflow review inspection commands |
| `tests/test_transport_verification.py` | Transport manifest and evidence coverage |
| `tests/test_sandbox_evidence.py` | Evidence requirement and executor integration coverage |
| `tests/test_goal_workflow.py` | Review-only workflow and policy drift coverage |
| `docs/guides/parallel-foundations.md` | User-facing boundaries, examples, and official CoppeliaSim references |
| `examples/08-parallel-foundations/` | Deterministic local fixtures for the parallel slice |

## Next recommended action

Inspect the final diff and create a focused local commit. Push only on explicit user request. The next implementation priority is an authorized, independently verified real read-only simulator transport, followed by a real OS-enforced backend sandbox. The M4 workflow should add deterministic EIR-to-plan validation and evidence contracts only after those safety prerequisites are established.
