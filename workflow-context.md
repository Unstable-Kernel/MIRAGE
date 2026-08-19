# Workflow Context

## Task

Complete the parallel context and review-trace iteration for MIRAGE.

## Current status

The iteration is committed locally as `f9f0ab0` on `feat/iteration-1-foundation`. The branch is five commits ahead of its remote and [PR #9](https://github.com/Unstable-Kernel/MIRAGE/pull/9) remains open against `main`. Do not push or publish without an explicit user request.

## Completed work

`context_review.py` introduces `WorkflowContextBundle` and redacted `WorkflowContextItem` contracts. Each item stores references and digests rather than raw artifacts. The bundle binds to a workflow ID, EIR document ID, policy provenance, and deterministic plan source nodes. Assessment rejects identifier, provenance, redaction, and source-node drift.

`review_trace.py` introduces typed review events and `WorkflowReviewTrace`. A complete trace requires context binding, plan validation, evidence assessment, and human-review request records. Trace assessment checks workflow ID, context ID, policy provenance, context readiness, and evidence readiness. Every result is review-only and has `execution_permitted: false`.

The runtime registry includes `inspect_workflow_context@0.1` and `assess_review_trace@0.1` as generic read-only declarations. The `workflow-context-inspect` and `review-trace-assess` commands parse local files only. `examples/10-context-review/` is the canonical deterministic fixture set.

## Verification

| Check | Result |
|---|---|
| Full Python tests | 59 passed |
| Ruff | Passed for `src`, `tests`, and `scripts` |
| EIR schema consistency | Passed |
| Documentation verification | Every tracked Markdown file passed local-link checks |
| CLI verification | Context inspection, review-trace assessment, and generic capability discovery passed |
| Repository hygiene | Secret scan, tracked no-em-dash scan, and `git diff --check` passed |

## Known limitations

Context bundles are redacted reference containers, not a retrieval system. They do not read local or remote artifacts, resolve URLs, reveal raw source content, construct provider prompts, or manage credentials. Review traces validate declared stage completeness but do not represent human approval, authorization, execution, or report issuance.

Live simulator transport and host-level sandbox enforcement remain unavailable. The M4 workflow still lacks controlled real context inputs, evidence adapters, policy-bound evaluation, audited approval transitions, report artifacts, and all execution paths. Simulator control, external side effects, physical actuation, automatic checkpoint resume, package publication, and autonomous experimentation remain absent.

## Important files

| File | Responsibility |
|---|---|
| `src/mirage/runtime/context_review.py` | Redacted context bundle contracts and plan-bound assessment |
| `src/mirage/runtime/review_trace.py` | Policy-bound review-event trace and completeness assessment |
| `src/mirage/runtime/workflow_evidence.py` | EIR-bound deterministic plan and evaluation-evidence review |
| `src/mirage/cli.py` | Context and trace local inspection commands |
| `examples/10-context-review/` | Canonical context and trace fixtures |
| `docs/guides/context-review-trace.md` | User-facing contracts and safety boundaries |

## Next recommended action

Await an explicit request before pushing the five local commits to update PR #9. The next locally safe build slice is an audited human approval transition contract. It must remain non-executing until verified live transport and an enforced sandbox exist.
