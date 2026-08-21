# Report Seal Consistency Example

This example compares a supplied deterministic report, report provenance seal, provenance readiness assessment, review trace, trace readiness assessment, and local consistency manifest. It checks report identity, workflow identity, trace identity, declared report digest, sealer reference, and the report's trace artifact reference.

The assessment compares supplied declarations only. It does not calculate a report digest, inspect report content beyond its supplied identifiers and artifact references, retrieve a trace, verify a signature, contact a remote witness, authenticate the sealer, store a seal, mutate report state, publish a report, or authorize execution.

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' report-seal-consistency-assess examples/18-report-seal-consistency/report.json examples/18-report-seal-consistency/report-seal.json examples/18-report-seal-consistency/provenance-assessment.json examples/18-report-seal-consistency/review-trace.json examples/18-report-seal-consistency/trace-assessment.json examples/18-report-seal-consistency/manifest.json
```

The expected result has `status` equal to `consistent`, all declared fields in `matched_fields`, and `execution_permitted` set to `false`.
