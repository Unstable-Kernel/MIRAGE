# Execution Ledger and Workflow Checkpoints

Iteration 3 adds two local persistence primitives. The **execution ledger** records every URCP attempt, including denied and unavailable requests. The record contains a generated request ID, actor, capability, version, backend, status, timestamps, policy summary, redacted inputs, redacted outputs, and a message. Records are appended as JSON Lines so they remain inspectable and easy to replay in tests.

The **workflow checkpoint** stores a validated workflow ID, revision, stage, state payload, related execution IDs, optional ESG project ID, and update time. A checkpoint is a workflow-state snapshot intended for future manual review, not an executable command. Loading it never resumes work automatically. `WorkflowCheckpoint.revalidate()` checks policy provenance, capability versions, policy permission, and backend allow-lists before a future workflow runner can consider human-approved resumption.

API keys, tokens, passwords, secrets, and credentials are redacted from persisted inputs and policy data. This redaction is a safety measure, not a substitute for avoiding sensitive data in requests.

The ledger now writes a versioned JSONL envelope around each record. Every envelope includes a canonical SHA-256 digest and the preceding envelope digest, so local inspection can detect a changed record, missing link, malformed line, or legacy unsealed record. Local reads use a shared POSIX advisory lock, while appends and retention compaction use an exclusive advisory lock. Appends refuse to proceed after an integrity failure.

`ExecutionLedger.retain(max_records)` keeps the newest bounded record set and writes a retention anchor into the first retained envelope. The anchor records the terminal digest immediately before the discarded prefix, but it does not preserve the removed records themselves. Retention is an explicit local compaction operation, not a repair or archival service.

The integrity chain detects accidental or unsophisticated local changes. It is not a signature, a remote witness, a trusted timestamp, encryption, a database transaction, a migration service, distributed coordination, or protection against an attacker who can rewrite the ledger and its digests.

CLI examples:

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' execute run_simulation --backend local --allow-simulation --ledger .artifacts/executions.jsonl
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' ledger-inspect .artifacts/executions.jsonl
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' ledger-verify .artifacts/executions.jsonl
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' checkpoint-inspect .artifacts/checkpoint.json
```
