# Context and Review Trace Assessment

This example binds a redacted context bundle and a provenance trace to the deterministic workflow from `examples/09-deterministic-workflow/`. Context items contain references and digests only. The trace records review artifacts, not execution events.

```bash
PYTHONPATH=src mirage workflow-context-inspect \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml \
  examples/10-context-review/context.json

PYTHONPATH=src mirage review-trace-assess \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml \
  examples/10-context-review/context.json \
  examples/09-deterministic-workflow/evidence.json \
  examples/10-context-review/review-trace.json
```

| Artifact | Validation | Boundary |
|---|---|---|
| Context bundle | Workflow identity, EIR document identity, policy provenance, redaction flag, and plan source nodes | It does not retrieve context, expose raw artifacts, or call a model |
| Review trace | Required trace events, workflow and context identity, policy provenance, context readiness, and evidence readiness | It does not approve, resume, execute, or report workflow work |
