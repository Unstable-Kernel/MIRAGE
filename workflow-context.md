# Workflow Context

## Task

Continue MIRAGE within the active session through locally verifiable governance foundations.

## Current status

The governance foundation iteration is verified and ready for a focused local commit on `feat/iteration-1-foundation`. [PR #10](https://github.com/Unstable-Kernel/MIRAGE/pull/10) is open against `main`; the working iteration has not yet been pushed. Continue autonomously through safe local slices, but stop for an external prerequisite, a safety decision, or an explicit user choice.

## Completed work

`approval_persistence.py` defines an integration-only persistence descriptor, identity evidence reference, and provider protocol. It has no credential value, write method, connection behavior, or identity-provider implementation. Assessment confirms only that local references are structurally consistent with the approval chain and active policy.

`revocation_review.py` validates declared revocation records without applying them. `evidence_provenance.py` seals each locally declared evidence reference with a digest and verifier reference. `lifecycle_review.py` checks a limited review-state order from draft through eligibility assessment without mutating any workflow.

The dispatch eligibility model now recognizes a declared revocation as a blocking reason. The runtime registry adds four generic read-only declarations: approval persistence, approval revocation, evidence provenance, and workflow lifecycle assessment. Four corresponding local CLI commands and `examples/12-governance-foundations/` demonstrate the contracts.

## Verification

| Check | Result |
|---|---|
| Full Python tests | 68 passed |
| Ruff | Passed for `src`, `tests`, and `scripts` |
| EIR schema consistency | Passed |
| Documentation verification | Every tracked Markdown file passed local-link checks |
| CLI verification | Persistence, revocation, provenance, lifecycle, and generic capability inspection passed |
| Repository hygiene | Secret scan, tracked no-em-dash scan, and `git diff --check` passed |

## Known limitations

The governance foundation is interface and assessment work only. It does not authenticate users, store or revoke approvals, verify signatures, connect to an audit log, retrieve evidence, assess physical correctness, alter state, or execute a capability.

Live simulator transport and host-level sandbox enforcement remain unavailable. The M4 workflow still lacks controlled external context, real evidence adapters, authenticated durable approval, report artifacts, and execution integration. Simulator control, external side effects, physical actuation, automatic checkpoint resume, package publication, and autonomous experimentation remain absent.

## Important files

| File | Responsibility |
|---|---|
| `src/mirage/runtime/approval_persistence.py` | Future authenticated persistence descriptor and no-write protocol |
| `src/mirage/runtime/revocation_review.py` | Declared revocation review without state mutation |
| `src/mirage/runtime/evidence_provenance.py` | Local evidence reference sealing and coverage assessment |
| `src/mirage/runtime/lifecycle_review.py` | Non-mutating review lifecycle transition assessment |
| `src/mirage/cli.py` | Four local governance inspection commands |
| `examples/12-governance-foundations/` | Canonical local governance fixtures |
| `docs/guides/governance-foundations.md` | User-facing contract and safety documentation |

## Next recommended action

Commit this iteration locally, then continue to a controlled-context schema and deterministic report-artifact contract. Do not add a live client, credentials, durable storage, dispatch path, or sandbox claim without independently verified external prerequisites.
