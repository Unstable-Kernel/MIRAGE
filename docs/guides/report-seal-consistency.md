# Report Seal Consistency Assessment

The report seal consistency assessment compares supplied local declarations for a deterministic report, a report provenance seal, a provenance readiness assessment, a review trace, a trace readiness assessment, and a manifest. It validates that report, workflow, trace, digest, and sealer-reference fields agree and that the report explicitly declares the sealed trace reference.

## Contract

`ReportSealConsistencyManifest` contains the expected report ID, workflow ID, declared report digest, source trace ID, and sealer reference. `assess_report_seal_consistency()` compares this manifest against only the supplied models. It returns `consistent` or `invalid` with structured rejection reasons and always returns `execution_permitted: false`.

The assessment requires a ready report-provenance result and ready review-trace result. It also requires the report to carry `trace:<source_trace_id>` in at least one section's artifact references. This creates a deterministic linkage between a report declaration and its declared trace without altering either artifact.

## Explicit boundary

The report digest and sealer reference are compared as declared strings. The assessment does not canonicalize or hash report content, verify a digital signature, authenticate a sealer, establish a trusted timestamp, contact a remote witness, retrieve a trace, write durable state, change lifecycle state, publish a report, or authorize execution.

## CLI

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' report-seal-consistency-assess examples/18-report-seal-consistency/report.json examples/18-report-seal-consistency/report-seal.json examples/18-report-seal-consistency/provenance-assessment.json examples/18-report-seal-consistency/review-trace.json examples/18-report-seal-consistency/trace-assessment.json examples/18-report-seal-consistency/manifest.json
```

The command reads only the explicitly supplied local files, emits JSON, exits nonzero for an inconsistency, and does not attempt retrieval, signing, repair, persistence, dispatch, or execution.
