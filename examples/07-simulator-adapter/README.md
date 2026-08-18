# Read-Only Simulator Adapter Example

This example contains deterministic project metadata and a state snapshot. It is a contract fixture, not a simulator project and not a replayable simulation.

```bash
PYTHONPATH=src mirage simulator-metadata examples/07-simulator-adapter/fixture-simulation.json --include-state
```

The command reads the fixture and prints separate policy-assessed metadata and snapshot results. Both results identify the fixture backend, include a sandbox assessment, set `control_available` to `false`, and do not start, stop, step, connect to, or modify any simulator.

## Fixture contract

| Section | Purpose |
|---|---|
| `metadata` | Static simulator project identification and scene summary |
| `snapshot` | Bounded object pose and velocity observation in the declared world frame |

The CoppeliaSim boundary remains unavailable until its read-only transport and semantics are verified. Passing an endpoint to MIRAGE only records that configuration exists. It never opens a connection.
