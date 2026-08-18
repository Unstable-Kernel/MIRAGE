# Execution Ledger and Workflow Checkpoints

Iteration 3 adds two local persistence primitives. The **execution ledger** records every URCP attempt, including denied and unavailable requests. The record contains a generated request ID, actor, capability, version, backend, status, timestamps, policy summary, redacted inputs, redacted outputs, and a message. Records are appended as JSON Lines so they remain inspectable and easy to replay in tests.

The **workflow checkpoint** stores a validated workflow ID, revision, stage, state payload, related execution IDs, optional ESG project ID, and update time. A checkpoint is a resumable data snapshot, not an executable command. Loading it never resumes work automatically. A future workflow runner may use a checkpoint after applying policy, validating current capabilities, and requesting human approval where required.

API keys, tokens, passwords, secrets, and credentials are redacted from persisted inputs and policy data. This redaction is a safety measure, not a substitute for avoiding sensitive data in requests. The ledger currently has no file locking, retention policy, encryption, database transactions, or distributed coordination.

CLI examples:

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' execute run_simulation --backend local --allow-simulation --ledger .artifacts/executions.jsonl
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' ledger-inspect .artifacts/executions.jsonl
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' checkpoint-inspect .artifacts/checkpoint.json
```
