# Local EIR Ingestion Example

This example demonstrates deterministic ingestion of one local JSON EIR candidate. The adapter reads only the supplied local path, identifies the supported source format, records byte length and SHA-256 digest, and passes the candidate unchanged to the canonical EIR validator.

The returned source record is separate from document provenance. It does not rewrite document, node, or relationship provenance. The adapter does not retrieve a URI, parse source repositories, papers, URDF, MATLAB, or CAD, execute code, invoke a model, write to a database, or dispatch a capability.

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' eir-ingest examples/16-eir-ingestion/robot_model.json
```

The expected result has `status` equal to `accepted`, a `json` source format, the content SHA-256 digest, and a validated `quadrotor-inspection` EIR document.
