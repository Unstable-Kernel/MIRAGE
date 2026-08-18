# URCP Execution Example

This example demonstrates the policy boundary introduced in Iteration 2.

A simulation request without explicit permission is denied:

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' execute run_simulation
```

A deterministic local simulation request can be enabled explicitly:

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' execute run_simulation --backend local --allow-simulation
```

A CoppeliaSim request remains unavailable until a verified transport and runtime configuration are supplied:

```bash
PYTHONPATH=src python3 -c 'from mirage.cli import app; app()' execute run_simulation --backend coppeliasim --allow-simulation
```

The example intentionally stops before real simulator or hardware integration. The next simulator adapter must add a concrete transport, capability coverage, resource policy, reproducibility controls, and integration tests.
