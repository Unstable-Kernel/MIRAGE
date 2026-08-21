# Workflow Context

## Task

Continue MIRAGE within the active session through locally verifiable M4 workflow and governance foundations.

## Current status

The cross-artifact readiness iteration is committed locally as `d14b7dc` on `feat/iteration-1-foundation`. [PR #10](https://github.com/Unstable-Kernel/MIRAGE/pull/10) is merged into `main`. The local ledger integrity and retention iteration is committed as `c6cc0ff`, and its handoff commit remains unpushed with it. The local EIR ingestion iteration is committed as `a4ea637` and remains unpushed. The coordinated provenance-consistency iteration is committed as `9dcdb8a` and remains unpushed. The coordinated report-seal consistency iteration is committed as `05813dc` and remains unpushed. The review-trace event consistency iteration is committed locally as `42e6db7` and remains unpushed. The policy-provenance consistency iteration is committed locally as `94e308d` and remains unpushed. The review-policy evidence-reference consistency iteration is committed locally as `89ddba6` and remains unpushed. A three-hour autonomous build review is active.

## Completed work

`cross_artifact_review.py` confirms that controlled context, review trace, approval chain, deterministic report, and report provenance use one workflow and are ready for review. `review_policy.py` applies bounded, deterministic report citation rules. `workflow_readiness.py` combines these local results with the existing advisory dispatch check. `ledger.py` now writes versioned audit envelopes with canonical chained digests, local advisory locking, integrity assessment, append refusal after verification failure, and bounded retention compaction with an explicit anchor. `ingestion.py` adds controlled local JSON and YAML EIR candidate ingestion with source byte counts, SHA-256 digests, deterministic diagnostics, optional allowed-root checks, and canonical validation without provenance mutation or retrieval. `provenance_consistency.py` compares supplied EIR source metadata, evidence-seal reference and digest declarations, and report provenance bindings without opening referenced evidence, fetching a source, or granting execution permission. `report_seal_consistency.py` compares supplied report, seal, report-provenance assessment, review trace, trace assessment, and manifest declarations without hashing report content, verifying signatures, contacting a witness, mutating lifecycle state, or granting execution permission. `review_trace_consistency.py` compares supplied trace, trace readiness, event reference and digest declarations, context bundle identity, and policy provenance without retrieving artifacts, recomputing digests, verifying signatures, or granting execution permission. `policy_provenance_consistency.py` compares supplied active policy, context bundle, context envelope, trace, report, review policy, review-policy assessment, and manifest declarations without retrieving artifacts, recomputing digests, verifying signatures, contacting a witness, mutating state, or granting execution permission. `review_policy_evidence_consistency.py` compares supplied review-policy bounds, readiness, report evidence and provenance declarations, evidence-provenance readiness, seals, and manifest bindings without retrieving artifacts, recomputing digests, verifying signatures, contacting a witness, mutating state, or granting execution permission.

The readiness result intentionally returns `ready_for_external_prerequisites` rather than execution permission. It preserves denial reasons for missing verified live transport, actual OS-enforced sandbox evidence, and any simulation policy denial. New generic URCP declarations, local CLI commands, tests, and `examples/14-cross-artifact-readiness/` expose the integration path.

## Verification

| Check | Result |
|---|---|
| Full Python tests | 105 passed |
| Ruff | Passed for `src`, `tests`, and `scripts` |
| EIR schema consistency | Passed |
| Documentation verification | Every tracked Markdown file passed local-link checks |
| CLI verification | Cross-artifact, review-policy, review-policy evidence-reference, readiness, and generic capability inspection passed |
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
| `src/mirage/eir/ingestion.py` | Controlled local EIR candidate ingestion with source digests and canonical validation |
| `src/mirage/runtime/provenance_consistency.py` | Reference-only EIR, evidence-seal, and report provenance consistency assessment |
| `src/mirage/runtime/report_seal_consistency.py` | Reference-only report, seal, readiness, and trace declaration consistency assessment |
| `src/mirage/runtime/review_trace_consistency.py` | Reference-only trace event, context bundle, and policy provenance consistency assessment |
| `src/mirage/runtime/policy_provenance_consistency.py` | Reference-only active policy, context, trace, report, and review-policy provenance consistency assessment |
| `src/mirage/runtime/review_policy_evidence_consistency.py` | Reference-only review-policy bounds, evidence-provenance, seal, and report-reference consistency assessment |
| `examples/14-cross-artifact-readiness/` | Canonical readiness policy and command example |
| `examples/15-ledger-integrity/` | Canonical retained local ledger fixture and integrity inspection command |
| `examples/16-eir-ingestion/` | Canonical local JSON EIR candidate and ingestion command |
| `examples/17-provenance-consistency/` | Canonical local EIR, evidence-seal, and report consistency fixture set |
| `examples/18-report-seal-consistency/` | Canonical local report, seal, trace, and consistency manifest fixture set |
| `examples/19-review-trace-event-consistency/` | Canonical local review-trace event and policy consistency fixture set |
| `examples/20-policy-provenance-consistency/` | Canonical local policy, context, trace, report, and review-policy consistency fixture set |
| `examples/21-review-policy-evidence-reference-consistency/` | Canonical local review-policy, evidence-provenance, seal, and report-reference fixture set |
| `docs/guides/cross-artifact-readiness.md` | User-facing readiness contract and remaining prerequisite boundaries |

## Next recommended action

The schedule `Every 3 hours MIRAGE build review` is active every 10,800 seconds, equivalent to every three hours, in `Asia/Calcutta`. On each run, inspect `/home/ubuntu/MIRAGE` on `feat/iteration-1-foundation`, `workflow-context.md`, `todo.md`, `code_review.md`, `ROADMAP.md`, and the PR state, then select only the next coherent locally verifiable slice. Permitted work is deterministic review, validation, provenance, documentation, and contract work that does not require external credentials or infrastructure. The schedule must keep simulator control, physical actuation, external side effects, live transport, OS-level sandbox claims, retrieval, credential handling, durable authority mutation, package publication, and branch push disabled. Every completed slice must include tests, examples, documentation, code review, workflow context, todo updates, full verification, and focused local commits without co-author attribution. If the next slice requires an authorized live simulator environment or a real OS-enforced sandbox, stop and report the precise prerequisite. The policy was reverified once more against the active schedule, current local branch, roadmap, and merged PR #10 state; no push or publication authorization exists. The next safe candidate after review-policy evidence-reference consistency is a bounded local evidence-capture declaration consistency assessment, provided it compares only supplied capture metadata, seal declarations, and evidence-reference records without retrieval, signature verification, remote witnessing, lifecycle mutation, or execution. Do not push or publish without explicit user approval.
