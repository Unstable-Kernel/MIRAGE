# Ledger Integrity and Retention Example

This example demonstrates the local JSONL ledger integrity contract. The ledger stores a versioned envelope for each audit record, links each envelope to the preceding digest, and can retain only the newest bounded record set while preserving an explicit retention anchor.

The example is local-only. It does not contact a remote witness, create a signature, perform distributed coordination, repair a malformed file, execute a URCP capability, or publish data.

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' ledger-verify examples/15-ledger-integrity/executions.jsonl
```

Expected output is a JSON object with `status` set to `valid`, `valid` set to `true`, and `record_count` set to `2`. The first retained envelope contains a `retention_anchor` that identifies the terminal digest before the discarded prefix.
