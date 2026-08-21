# Evidence-capture declaration consistency

The evidence-capture declaration consistency assessment compares supplied declarations only. It is a deterministic review surface that confirms whether a declared capture agrees with its provenance seal, prior review-policy evidence assessment, and report provenance reference. It does not treat a matching declaration as proof that evidence was collected, source bytes exist, a digest is correct, or a verifier is trusted.

## Inputs and checks

| Input | Required local comparison | Not performed |
|---|---|---|
| Capture manifest | Unique capture and evidence identifiers, workflow identity, prior assessment identity, expected capture metadata, and report section binding | Source retrieval or capture execution |
| Evidence-provenance assessment | Review readiness, workflow identity, and sealed evidence declaration | Evidence content inspection or digest recomputation |
| Review-policy evidence assessment | Required consistency state, workflow identity, manifest identity, and validated evidence declaration | Policy re-evaluation, signature validation, or authority decisions |
| Deterministic report | Workflow identity, cited evidence identifier, section placement, source reference, and digest declaration | Report rendering, generated claims, or publication |
| Evidence seals | Source reference, digest, capture method, capture timestamp, and verifier reference equality | Timestamp trust, remote witness contact, or seal signing |

Run the local inspection with the ordered files shown below.

```bash
mirage evidence-capture-consistency-assess \
  examples/22-evidence-capture-consistency/evidence-provenance.json \
  examples/22-evidence-capture-consistency/review-policy-evidence-assessment.json \
  examples/22-evidence-capture-consistency/report.json \
  examples/22-evidence-capture-consistency/evidence-seals.json \
  examples/22-evidence-capture-consistency/manifest.json
```

The result returns `consistent` only when every supplied declaration agrees. It returns `invalid` with structured issue codes when a workflow, manifest, seal, report section, evidence citation, or provenance reference differs. `execution_permitted` is always `false`.

## Explicit non-goals

This assessment has no retrieval, remote transport, simulator, OS-sandbox, credential, storage, signature, trusted-timestamp, remote-witness, lifecycle-mutation, dispatch, or execution path. A future evidence-capture implementation requires an authorized environment and independently verifiable collection, isolation, retention, and review controls.
