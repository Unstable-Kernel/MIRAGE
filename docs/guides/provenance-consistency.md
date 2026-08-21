# Provenance Consistency Assessment

The provenance consistency assessment compares declared local metadata from three existing review surfaces: an ingested EIR candidate, evidence provenance seals, and a deterministic report. It is a reference-only integrity check. It compares identifiers, source references, declared digest strings, workflow identity, report section placement, and readiness states without opening or retrieving the referenced evidence.

## Contract

`ProvenanceConsistencyManifest` binds one ingested EIR document to its declared source reference and source digest. It also contains one binding per evidence identifier. Each binding names the sealed source reference and digest plus the report section that must cite the evidence and contain the matching provenance reference.

`assess_provenance_consistency()` accepts the manifest, the local EIR source metadata returned by `ingest_eir_file()`, the validated EIR document, evidence seals, a prior evidence-provenance assessment, the report, and a prior report assessment. It returns `consistent` only when every declared link agrees. It always returns `execution_permitted: false`.

## Rejection semantics

The assessment rejects mismatched EIR document identity, EIR source reference or digest, workflow IDs, missing or unsealed evidence, seal and manifest disagreement, missing report sections, uncited evidence, missing report provenance references, unknown report bindings, and incorrect report-section placement. It does not repair any artifact or overwrite a declared digest.

## Explicit boundary

The EIR source digest is verified against local ingestion metadata because that file is explicitly supplied to the command. Evidence and report digest declarations are compared as strings only. The assessment does not fetch source references, open evidence paths, recompute evidence digests, verify signatures, create a trusted timestamp, provide remote witnessing, authenticate a reviewer, mutate a report, publish an artifact, invoke a backend, or authorize execution.

## CLI

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' provenance-consistency-assess examples/16-eir-ingestion/robot_model.json examples/17-provenance-consistency/manifest.json examples/17-provenance-consistency/evidence-seals.json examples/17-provenance-consistency/report.json examples/17-provenance-consistency/evidence-provenance.json examples/17-provenance-consistency/report-assessment.json
```

The command emits the local EIR source metadata and the assessment as JSON. It exits nonzero when the provenance graph is inconsistent, and it does not attempt retrieval, repair, persistence, dispatch, or execution.
