# Review-Trace Event Consistency Assessment

The review-trace event consistency assessment compares a supplied review trace, trace readiness assessment, and manifest. It checks trace, workflow, context-bundle, and policy-provenance identifiers, then checks the declared artifact reference and digest for each required review event.

## Contract

`ReviewTraceEventConsistencyManifest` declares one expected event for each of `context_bound`, `plan_validated`, `evidence_assessed`, and `human_review_requested`. `assess_review_trace_event_consistency()` compares those declarations to the supplied local trace and readiness result. It returns `consistent` or `invalid` with structured rejection reasons and always returns `execution_permitted: false`.

The trace readiness result must be `ready_for_review`. The trace and manifest must agree on trace ID, workflow ID, context bundle ID, and policy provenance. Each matching event must then agree on its artifact reference and declared digest.

## Explicit boundary

This assessment compares supplied strings and structured declarations only. It does not retrieve an artifact, recalculate an artifact digest, validate a signature, authenticate a reviewer, create a trusted timestamp, contact a remote witness, mutate a workflow, persist data, publish a report, invoke a backend, dispatch a capability, or authorize execution.

## CLI

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' review-trace-event-consistency-assess examples/19-review-trace-event-consistency/review-trace.json examples/19-review-trace-event-consistency/trace-assessment.json examples/19-review-trace-event-consistency/manifest.json
```

The command reads only the explicitly supplied local files, emits JSON, exits nonzero for an inconsistency, and does not attempt retrieval, signing, repair, persistence, dispatch, or execution.
