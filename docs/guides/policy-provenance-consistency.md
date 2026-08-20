# Policy-Provenance Consistency Assessment

The policy-provenance consistency assessment compares supplied local policy, context bundle, context envelope, review trace, deterministic report, review policy, review-policy assessment, and manifest declarations. It verifies that workflow identifiers and policy-provenance declarations agree across the submitted review artifacts.

## Contract

`PolicyProvenanceConsistencyManifest` declares the expected workflow, context-bundle, context-envelope, trace, report, review-policy identifiers, and policy provenance. `assess_policy_provenance_consistency()` compares those declarations to explicitly supplied local artifacts. It returns `consistent` or `invalid` with structured rejection reasons and always returns `execution_permitted: false`.

The supplied review-policy assessment must be `ready_for_review`. The active execution-policy provenance, context-bundle provenance, and trace provenance must equal the manifest provenance. Context envelope, trace, report, and review-policy assessment workflow identifiers must equal the manifest workflow identifier.

## Explicit boundary

This assessment compares supplied strings and structured declarations only. It does not retrieve content, open an artifact reference, recompute a digest, validate a signature, authenticate a reviewer, create a trusted timestamp, contact a remote witness, mutate a lifecycle state, persist data, publish a report, invoke a backend, dispatch a capability, or authorize execution.

## CLI

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' policy-provenance-consistency-assess examples/20-policy-provenance-consistency/policy.json examples/20-policy-provenance-consistency/context-bundle.json examples/20-policy-provenance-consistency/context-envelope.json examples/20-policy-provenance-consistency/review-trace.json examples/20-policy-provenance-consistency/report.json examples/20-policy-provenance-consistency/review-policy.json examples/20-policy-provenance-consistency/review-policy-assessment.json examples/20-policy-provenance-consistency/manifest.json
```

The command reads only the explicitly supplied local files, emits JSON, exits nonzero for an inconsistency, and does not attempt retrieval, signing, repair, persistence, dispatch, or execution.
