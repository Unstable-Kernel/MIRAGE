# Governance Foundation Assessment

This example validates four future-facing governance contracts entirely from local JSON. It does not authenticate a user, resolve a credential, save a record, revoke an approval, retrieve evidence, or mutate workflow state.

```bash
PYTHONPATH=src mirage approval-persistence-assess \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml \
  examples/10-context-review/context.json \
  examples/09-deterministic-workflow/evidence.json \
  examples/10-context-review/review-trace.json \
  examples/11-guarded-approval/approval-chain.json \
  examples/12-governance-foundations/persistence.json

PYTHONPATH=src mirage approval-revocation-assess \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml \
  examples/10-context-review/context.json \
  examples/09-deterministic-workflow/evidence.json \
  examples/10-context-review/review-trace.json \
  examples/11-guarded-approval/approval-chain.json \
  examples/12-governance-foundations/revocation.json

PYTHONPATH=src mirage evidence-provenance-assess \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml \
  examples/09-deterministic-workflow/evidence.json \
  examples/12-governance-foundations/evidence-seals.json
```

| Assessment | Success means | It does not mean |
|---|---|---|
| Persistence | A future adapter has enough declared identifiers and integrity references to begin integration review | A credential was used, a record was written, or a signature was verified |
| Revocation | A declared record names a known approval and is structurally policy-consistent | The approval chain was changed or an external system was notified |
| Provenance | Each local evidence reference has a matching declared seal | Evidence contents were retrieved, evaluated, or physically verified |
| Lifecycle | A requested state transition follows the declared review order | Workflow state changed or execution became allowed |
