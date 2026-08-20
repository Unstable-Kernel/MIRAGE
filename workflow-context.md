# Workflow Context

## Task

Continue MIRAGE within the active session through locally verifiable M4 workflow and governance foundations.

## Current status

The controlled context and deterministic report iteration is committed locally as `e16d575` on `feat/iteration-1-foundation`. [PR #10](https://github.com/Unstable-Kernel/MIRAGE/pull/10) remains open against `main`. The branch is three commits ahead of its remote. Continue autonomously through safe local slices, but stop for an external prerequisite, safety decision, or explicit user choice.

## Completed work

`controlled_context.py` defines schemas, envelopes, and claim records that bind a workflow to expected redacted context item kinds, reference prefixes, and content digests. The assessment detects missing required claims, unknown fields and items, mismatched kinds, invalid prefixes, and digest drift without reading source content.

`deterministic_report.py` adds a reference-only report artifact. Each section can cite controlled claim identifiers, sealed evidence identifiers, and stable artifact references. The report assessment refuses unknown claims or unsealed evidence without generating findings or prose.

`report_provenance.py` and `report_lifecycle.py` add local report seal and review-state assessment contracts. They validate declared identifiers and ordering only. No signature, persistence, publication, or state mutation occurs. The registry adds four generic read-only capabilities, local CLI commands expose the checks, and `examples/13-controlled-report/` contains canonical fixtures.

## Verification

| Check | Result |
|---|---|
| Full Python tests | 70 passed |
| Ruff | Passed for `src`, `tests`, and `scripts` |
| EIR schema consistency | Passed |
| Documentation verification | Every tracked Markdown file passed local-link checks |
| CLI verification | Controlled context, deterministic report, report provenance, report lifecycle, and generic capability inspection passed |
| Repository hygiene | Secret scan, tracked no-em-dash scan, and `git diff --check` passed |

## Known limitations

Controlled context is a local schema for already redacted references. It is not an ingestion, retrieval, classification, authorization, or prompt-construction service. The deterministic report is a citation graph, not generated engineering prose or a rendered deliverable. Report provenance is a declared reference, not a cryptographic signature, and report lifecycle validation does not persist or publish state.

Live simulator transport and host-level sandbox enforcement remain unavailable. The M4 workflow still lacks controlled external inputs, real evidence adapters, authenticated approval persistence, durable audit controls, rendered reports, and execution integration. Simulator control, external side effects, physical actuation, automatic checkpoint resume, package publication, and autonomous experimentation remain absent.

## Important files

| File | Responsibility |
|---|---|
| `src/mirage/runtime/controlled_context.py` | Schema-bound redacted context envelope and assessment |
| `src/mirage/runtime/deterministic_report.py` | Reference-only deterministic report artifact and citation validation |
| `src/mirage/runtime/report_provenance.py` | Local report seal validation without signing or storage |
| `src/mirage/runtime/report_lifecycle.py` | Non-mutating report review lifecycle assessment |
| `src/mirage/cli.py` | Four local controlled-context and report inspection commands |
| `examples/13-controlled-report/` | Canonical controlled report fixtures |
| `docs/guides/controlled-context-report.md` | User-facing contract and safety guide |

## Next recommended action

Continue to deterministic policy-evaluation criteria and cross-artifact consistency checks. Do not add retrieval, a model, live transport, credentials, durable storage, dispatch, or a sandbox claim without independently verified external prerequisites.
