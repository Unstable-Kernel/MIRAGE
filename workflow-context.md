# Workflow Context

## Task

Complete the guarded approval and advisory dispatch eligibility iteration for MIRAGE.

## Current status

The iteration is verified and ready for a focused local commit on `feat/iteration-1-foundation`. The branch already has six unpushed commits from the preceding safety and workflow iterations, and [PR #9](https://github.com/Unstable-Kernel/MIRAGE/pull/9) remains open against `main`. Do not push or publish without an explicit user request.

## Completed work

`approval_review.py` introduces `HumanApprovalRecord` and `ApprovalChain`. Each record binds an approver identifier, decision, workflow, review trace, policy provenance, digest linkage, and timestamp. Assessment checks trace, workflow, policy provenance, and latest decision. It returns a review result only and never sets execution permission.

`dispatch_eligibility.py` introduces an advisory preflight that combines approval readiness, simulation policy, transport report, and sandbox assessment. Its eligibility result is always non-executing. The fixture demonstrates why an approved local review still cannot dispatch when transport is only fixture-verified and the sandbox is declarative.

The URCP registry exposes `assess_human_approval@0.1` and `assess_dispatch_eligibility@0.1` as generic read-only declarations. The `approval-chain-assess` and `dispatch-eligibility-assess` CLI commands consume local JSON only. `examples/11-guarded-approval/` provides the canonical approval and blocked eligibility fixtures.

## Verification

| Check | Result |
|---|---|
| Full Python tests | 64 passed |
| Ruff | Passed for `src`, `tests`, and `scripts` |
| EIR schema consistency | Passed |
| Documentation verification | Every tracked Markdown file passed local-link checks |
| CLI verification | Approval chain returns review-ready; dispatch eligibility returns expected ineligible result; generic capability discovery passed |
| Repository hygiene | Secret scan, tracked no-em-dash scan, and `git diff --check` passed |

## Known limitations

Approval records are local data contracts, not authenticated human identity or signatures. They are not stored durably, revocable, notified, or independently audited. Dispatch eligibility is advisory and does not dispatch a backend even if all supplied conditions appear ready.

The live transport and OS-enforced sandbox prerequisites remain unavailable. The M4 workflow still lacks real controlled context, external evidence adapters, policy-bound evaluation, authenticated approval persistence, report artifacts, and an execution integration. Simulator control, external side effects, physical actuation, automatic checkpoint resume, package publication, and autonomous experimentation remain absent.

## Important files

| File | Responsibility |
|---|---|
| `src/mirage/runtime/approval_review.py` | Approval chain models, digest linkage, and review-only assessment |
| `src/mirage/runtime/dispatch_eligibility.py` | Advisory technical prerequisite assessment with structured denial reasons |
| `src/mirage/cli.py` | Approval and eligibility local inspection commands |
| `examples/11-guarded-approval/` | Canonical approved-yet-ineligible fixture set |
| `docs/guides/guarded-approval-eligibility.md` | User-facing contract, refusal behavior, and safety limits |

## Next recommended action

Inspect the final diff, create a focused local commit, and wait for an explicit push request. The next locally safe M4 slice is an authenticated approval-persistence interface definition with no credential handling or execution path. It must remain advisory until verified live transport and an enforced sandbox exist.
