# Guarded Approval and Dispatch Eligibility

This example shows the last review-only checkpoint before a future dispatcher. A human approval chain may be internally consistent while dispatch remains ineligible because the transport is fixture-only and the sandbox is declarative.

```bash
PYTHONPATH=src mirage approval-chain-assess \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml \
  examples/10-context-review/context.json \
  examples/09-deterministic-workflow/evidence.json \
  examples/10-context-review/review-trace.json \
  examples/11-guarded-approval/approval-chain.json

PYTHONPATH=src mirage dispatch-eligibility-assess \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml \
  examples/10-context-review/context.json \
  examples/09-deterministic-workflow/evidence.json \
  examples/10-context-review/review-trace.json \
  examples/11-guarded-approval/approval-chain.json \
  examples/08-parallel-foundations/transport-manifest.json \
  examples/08-parallel-foundations/transport-evidence.json \
  examples/11-guarded-approval/sandbox-assessment.json \
  --allow-simulation
```

The approval command returns `review_ready`. The dispatch eligibility command deliberately returns `ineligible` and exits with status 1. It does not execute anything. The fixture has neither independently verified live transport nor an enforced sandbox, so the result is a structured denial rather than an attempt to dispatch.
