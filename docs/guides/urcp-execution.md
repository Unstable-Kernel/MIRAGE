# URCP Execution Guide

Iteration 2 adds a policy-gated execution runtime. The runtime resolves a capability from the URCP registry, checks its security class and requested backend against an explicit `ExecutionPolicy`, then delegates to a registered backend and returns a structured `ExecutionResult`.

Simulation is denied by default. Read-only capability execution is permitted by default, simulation requires `allow_simulation: true`, and external side effects or physical actuation remain denied unless a future policy explicitly enables them. An allow-list of backends can further restrict the request.

The local backend is deterministic and exists for contract tests and development. It does not represent a physics simulator. The CoppeliaSim backend is a declared boundary that currently reports unavailable because no verified CoppeliaSim transport has been configured. MIRAGE does not claim CoppeliaSim support from this adapter boundary alone.

Example commands:

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' execute run_simulation
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' execute run_simulation --backend local --allow-simulation
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' execute run_simulation --backend coppeliasim --allow-simulation
```

The first command is expected to return a policy denial. The second uses the deterministic local backend. The third reports that the CoppeliaSim backend is unavailable. No command accepts arbitrary host commands, shell strings, or unrestricted physical actuation inputs.
