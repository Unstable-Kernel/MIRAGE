# Execution Ledger and Checkpoint Example

This example demonstrates that URCP execution can be audited and that workflow state can be persisted without automatically resuming work.

Create an execution record:

```bash
mkdir -p .artifacts
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' execute run_simulation --backend local --allow-simulation --ledger .artifacts/executions.jsonl
```

Inspect the audit record:

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' ledger-inspect .artifacts/executions.jsonl
```

Create and inspect a checkpoint:

```bash
PYTHONPATH=src python3 -c 'from mirage.runtime import WorkflowCheckpoint; WorkflowCheckpoint(workflow_id="workflow.demo", stage="plan", state={"steps": ["validate"]}).save(".artifacts/checkpoint.json")'
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' checkpoint-inspect .artifacts/checkpoint.json
```

The ledger is an audit record, not an authorization system. The checkpoint is a validated state snapshot, not an executable plan. Future resume behavior must revalidate capabilities and policies before doing work.
