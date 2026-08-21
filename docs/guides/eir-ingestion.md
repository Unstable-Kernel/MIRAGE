# Local EIR Ingestion

`ingest_eir_file()` is MIRAGE's deterministic local frontend boundary for an existing EIR candidate stored as JSON or YAML. It accepts a file path, reads local UTF-8 bytes, identifies the format from a supported extension, calculates a SHA-256 source digest, and passes the parsed mapping to the canonical `validate_document()` contract.

The result is accepted only when canonical validation accepts the candidate. Rejections preserve structured diagnostics for unsupported formats, read failures, invalid UTF-8, parsing failures, non-mapping roots, allowed-root violations, and EIR validation errors. The ingestion layer does not duplicate the EIR invariant logic.

## Provenance boundary

The local source record contains the resolved local path, source format, byte count, and content digest. It is separate from the document's own provenance. MIRAGE deliberately preserves supplied document, node, and relationship provenance rather than rewriting it during ingestion.

An optional `allowed_root` can require that the resolved source path sits beneath a caller-provided local directory. This is a path-boundary check only. It does not provide a filesystem sandbox, path authorization service, or symlink attack defense against a concurrent hostile local writer.

## Explicit non-goals

This adapter does not retrieve URLs, access external services, parse repositories, papers, URDF, MATLAB, CAD, or arbitrary data formats, execute source content, invoke providers, lower EIR into a backend artifact, modify a workflow, or dispatch a capability. Unsupported inputs are rejected with a diagnostic instead of being partially interpreted.

## CLI

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' eir-ingest examples/16-eir-ingestion/robot_model.json
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' eir-ingest examples/16-eir-ingestion/robot_model.json --allowed-root examples/16-eir-ingestion
```

The command reports a JSON ingestion result and exits nonzero for a rejected candidate. It performs no retrieval, execution, repair, persistence, or dispatch.
