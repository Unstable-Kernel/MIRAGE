# Deterministic Workflow and Evidence Review

This example binds a review-only workflow to a validated EIR document. Every proposed workflow step cites an existing EIR node. Every evaluation criterion receives an explicit evidence reference. The commands inspect local JSON and YAML only.

```bash
PYTHONPATH=src mirage goal-workflow-plan \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml

PYTHONPATH=src mirage goal-workflow-evidence \
  examples/09-deterministic-workflow/workflow.json \
  examples/01-validate-eir/robot_model.yaml \
  examples/09-deterministic-workflow/evidence.json
```

| Output | Meaning | Boundary |
|---|---|---|
| Workflow plan | Every proposed step references a known node in a valid EIR document | It does not create a plan with a model or call a capability backend |
| Evidence assessment | Every required criterion has cited evidence from a planned source node | It does not decide engineering correctness, execute work, or create a report |

The resulting artifacts remain suitable only for manual review. They do not start a simulator, connect to a service, resume a checkpoint, create a subprocess, alter project state, or actuate hardware.
