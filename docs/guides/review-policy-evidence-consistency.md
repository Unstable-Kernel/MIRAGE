# Review-Policy Evidence-Reference Consistency Assessment

The review-policy evidence-reference consistency assessment compares supplied local review-policy bounds, review-policy readiness, deterministic report evidence and provenance declarations, evidence-provenance readiness, evidence seals, and a manifest. It verifies that declared report evidence references remain aligned with the supplied policy and provenance declarations.

## Contract

`ReviewPolicyEvidenceConsistencyManifest` declares the expected workflow, review-policy identifier, bounded section count, review-policy booleans, evidence-provenance workflow identifier, and one evidence-to-report binding per evidence identifier. `assess_review_policy_evidence_consistency()` compares those declarations to explicitly supplied local artifacts. It returns `consistent` or `invalid` with structured rejection reasons and always returns `execution_permitted: false`.

The supplied review-policy, report, and evidence-provenance assessments must be ready for review. Every binding must have a declared evidence seal, a matching sealed identifier, a report section containing the evidence identifier, and a matching report provenance reference. Any provenance declaration in the report must appear in the manifest and in its expected section.

## Explicit boundary

This assessment compares supplied strings and structured declarations only. It does not retrieve evidence, open a source reference, recompute a digest, validate a signature, authenticate a reviewer, create a trusted timestamp, contact a remote witness, mutate a lifecycle state, persist data, publish a report, invoke a backend, dispatch a capability, or authorize execution.

## CLI

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' review-policy-evidence-consistency-assess examples/21-review-policy-evidence-reference-consistency/review-policy.json examples/21-review-policy-evidence-reference-consistency/review-policy-assessment.json examples/21-review-policy-evidence-reference-consistency/report.json examples/21-review-policy-evidence-reference-consistency/report-assessment.json examples/21-review-policy-evidence-reference-consistency/evidence-provenance.json examples/21-review-policy-evidence-reference-consistency/evidence-seals.json examples/21-review-policy-evidence-reference-consistency/manifest.json
```

The command reads only the explicitly supplied local files, emits JSON, exits nonzero for an inconsistency, and does not attempt retrieval, signing, repair, persistence, dispatch, or execution.
