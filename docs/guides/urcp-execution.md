# URCP Execution Guide

The current runtime resolves a capability from the URCP registry, checks its security class and requested backend against an explicit `ExecutionPolicy`, assesses the declared sandbox envelope, then delegates to a registered backend and returns a structured `ExecutionResult`.

Simulation is denied by default. Read-only capability execution is permitted by default, simulation requires `allow_simulation: true`, and external side effects or physical actuation remain denied unless a future policy explicitly enables them. An allow-list of backends can further restrict the request.

The local execution backend is deterministic and exists for contract tests and development. It does not represent a physics simulator. The separate fixture-backed read-only simulator adapter can inspect deterministic project metadata and bounded state snapshots, but it cannot control a simulator. The CoppeliaSim execution and read-only boundaries report unavailable because no verified CoppeliaSim transport has been configured. MIRAGE does not claim CoppeliaSim support from either boundary alone.

Example commands:

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' execute run_simulation
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' execute run_simulation --backend local --allow-simulation
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' execute run_simulation --backend coppeliasim --allow-simulation
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' simulator-metadata examples/07-simulator-adapter/fixture-simulation.json --include-state
```

The first command is expected to return a policy denial. The second uses the deterministic local backend. The third reports that the CoppeliaSim execution backend is unavailable. The final command reads a local contract fixture and emits metadata and state results with sandbox assessment evidence. No command accepts arbitrary host commands, shell strings, simulator control, or unrestricted physical actuation inputs. See [read-only-simulator-adapter.md](read-only-simulator-adapter.md) and [sandbox-checkpoint-revalidation.md](sandbox-checkpoint-revalidation.md) for the complete safety boundaries.
