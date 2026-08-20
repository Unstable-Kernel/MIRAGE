# Review-Trace Event Consistency Example

This example compares a supplied review trace, trace readiness assessment, and event-consistency manifest. It checks the declared trace, workflow, context bundle, policy provenance, and all four review-event references and digest declarations.

The assessment compares supplied declarations only. It does not retrieve an artifact, recalculate a digest, verify a signature, authenticate a reviewer, create a timestamp, contact a remote witness, change workflow state, persist data, publish a report, dispatch a capability, or authorize execution.

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' review-trace-event-consistency-assess examples/19-review-trace-event-consistency/review-trace.json examples/19-review-trace-event-consistency/trace-assessment.json examples/19-review-trace-event-consistency/manifest.json
```

The expected output has `status` equal to `consistent`, all four event types in `matched_event_types`, and `execution_permitted` set to `false`.
