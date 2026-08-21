# Provenance Consistency Example

This example compares declared local provenance metadata across an ingested EIR source, evidence seals, and a deterministic report. It checks only the supplied reference strings, SHA-256 digest declarations, evidence identifiers, report sections, and prior review statuses.

The EIR source is parsed through the local EIR ingestion adapter. The assessment does not open any reference named by an evidence seal, retrieve a URI, recalculate evidence content, generate a report, change a review state, call a provider, connect to a simulator, or dispatch a capability.

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' provenance-consistency-assess examples/16-eir-ingestion/robot_model.json examples/17-provenance-consistency/manifest.json examples/17-provenance-consistency/evidence-seals.json examples/17-provenance-consistency/report.json examples/17-provenance-consistency/evidence-provenance.json examples/17-provenance-consistency/report-assessment.json
```

The expected assessment has `status` equal to `consistent`, both evidence identifiers in `verified_evidence_ids`, and `execution_permitted` set to `false`.
