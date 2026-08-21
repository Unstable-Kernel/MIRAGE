# Review-Policy Evidence-Reference Consistency Example

This example compares supplied local review-policy bounds, review-policy readiness, deterministic report references, evidence-provenance readiness, evidence seals, and a manifest. It validates that each declared evidence reference remains within the supplied policy and provenance boundary without opening any source artifact.

The assessment compares supplied declarations only. It does not retrieve evidence, recompute a digest, validate a signature, authenticate a reviewer, create a trusted timestamp, contact a remote witness, mutate state, persist data, publish a report, dispatch a capability, or authorize execution.

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' review-policy-evidence-consistency-assess examples/21-review-policy-evidence-reference-consistency/review-policy.json examples/21-review-policy-evidence-reference-consistency/review-policy-assessment.json examples/21-review-policy-evidence-reference-consistency/report.json examples/21-review-policy-evidence-reference-consistency/report-assessment.json examples/21-review-policy-evidence-reference-consistency/evidence-provenance.json examples/21-review-policy-evidence-reference-consistency/evidence-seals.json examples/21-review-policy-evidence-reference-consistency/manifest.json
```

The expected output has `status` equal to `consistent`, lists `evidence-reference-1` as validated, and keeps `execution_permitted` set to `false`.
