# Evidence-capture declaration consistency example

This fixture demonstrates a local-only comparison between one supplied evidence-capture declaration, its provenance seal, a prior review-policy evidence assessment, and a report provenance reference. The command reads only these files. It does not open the declared source, recompute a digest, verify a signature, contact a witness, mutate an artifact, or permit execution.

```bash
mirage evidence-capture-consistency-assess \
  evidence-provenance.json \
  review-policy-evidence-assessment.json \
  report.json \
  evidence-seals.json \
  manifest.json
```

The expected result has `status: consistent`, one validated capture identifier, and `execution_permitted: false`.
