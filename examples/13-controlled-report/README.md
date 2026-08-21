# Controlled Context and Deterministic Report

This example constrains a redacted context bundle with a local schema, validates a report that contains references only, checks a declared provenance seal, and assesses lifecycle order. It does not retrieve content, generate prose, sign a report, write a file outside this fixture set, publish, or execute a workflow.

```bash
PYTHONPATH=src mirage controlled-context-assess \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml \
  examples/10-context-review/context.json \
  examples/13-controlled-report/context-schema.json \
  examples/13-controlled-report/context-envelope.json

PYTHONPATH=src mirage deterministic-report-assess \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml \
  examples/10-context-review/context.json \
  examples/09-deterministic-workflow/evidence.json \
  examples/13-controlled-report/context-schema.json \
  examples/13-controlled-report/context-envelope.json \
  examples/12-governance-foundations/evidence-seals.json \
  examples/13-controlled-report/report.json
```

| Output | Meaning | It does not mean |
|---|---|---|
| Controlled context ready | The declared claims match redacted bundle items and schema constraints | Any source content was retrieved or made safe for a model prompt |
| Report ready | The reference-only report cites known claims and sealed evidence | Engineering prose was generated or correctness was evaluated |
| Report seal ready | The declared seal identifies the ready report and source trace | A cryptographic signature or publication occurred |
| Lifecycle valid | The requested review-state order is structurally permitted | Report state changed or execution became allowed |
