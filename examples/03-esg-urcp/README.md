# ESG and URCP Example

This example demonstrates the deterministic knowledge and capability declarations added after Iteration 1.

Inspect the persisted Engineering State Graph:

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' esg-inspect examples/03-esg-urcp/state.json
```

List declared capabilities without executing anything:

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' capabilities
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' capabilities --backend mujoco
```

The registry is declarative. Registering `run_simulation` does not claim that a simulator is installed or that execution is safe. Future adapter runtimes must apply capability policy, resource limits, sandboxing, and approval gates.
