# Cross-Artifact Readiness

This example checks that the local context, trace, approval, report, provenance, and policy artifacts agree before summarizing external prerequisites. It does not dispatch a capability, change workflow state, or override the missing verified transport and enforced sandbox.

```bash
PYTHONPATH=src mirage cross-artifact-assess \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml \
  examples/10-context-review/context.json \
  examples/09-deterministic-workflow/evidence.json \
  examples/10-context-review/review-trace.json \
  examples/11-guarded-approval/approval-chain.json \
  examples/13-controlled-report/context-schema.json \
  examples/13-controlled-report/context-envelope.json \
  examples/12-governance-foundations/evidence-seals.json \
  examples/13-controlled-report/report.json \
  examples/13-controlled-report/report-seal.json

PYTHONPATH=src mirage workflow-readiness-assess \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml \
  examples/10-context-review/context.json \
  examples/09-deterministic-workflow/evidence.json \
  examples/10-context-review/review-trace.json \
  examples/11-guarded-approval/approval-chain.json \
  examples/13-controlled-report/context-schema.json \
  examples/13-controlled-report/context-envelope.json \
  examples/12-governance-foundations/evidence-seals.json \
  examples/13-controlled-report/report.json \
  examples/13-controlled-report/report-seal.json \
  examples/14-cross-artifact-readiness/review-policy.json \
  examples/08-parallel-foundations/transport-manifest.json \
  examples/08-parallel-foundations/transport-evidence.json \
  examples/11-guarded-approval/sandbox-assessment.json
```

The readiness result is `ready_for_external_prerequisites`, not execution permission. Its denial reasons identify why verified live transport and actual sandbox enforcement are still required.
