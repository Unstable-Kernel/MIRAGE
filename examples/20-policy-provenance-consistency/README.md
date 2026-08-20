# Policy-Provenance Consistency Example

This example compares supplied local policy, context bundle, context envelope, review trace, deterministic report, review policy, review-policy assessment, and manifest declarations. It verifies shared workflow identifiers and matching policy provenance without opening referenced artifacts or executing a capability.

The assessment compares supplied declarations only. It does not retrieve content, recompute digests, validate signatures, authenticate reviewers, create timestamps, contact remote witnesses, mutate state, persist data, publish reports, dispatch capabilities, or authorize execution.

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' policy-provenance-consistency-assess examples/20-policy-provenance-consistency/policy.json examples/20-policy-provenance-consistency/context-bundle.json examples/20-policy-provenance-consistency/context-envelope.json examples/20-policy-provenance-consistency/review-trace.json examples/20-policy-provenance-consistency/report.json examples/20-policy-provenance-consistency/review-policy.json examples/20-policy-provenance-consistency/review-policy-assessment.json examples/20-policy-provenance-consistency/manifest.json
```

The expected output has `status` equal to `consistent`, populated `matched_declarations`, and `execution_permitted` set to `false`.
