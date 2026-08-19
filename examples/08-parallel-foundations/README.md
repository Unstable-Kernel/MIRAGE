# Parallel Foundation Contracts

This example demonstrates three deterministic, non-executing foundations that can be developed independently and integrated through shared safety evidence.

| File | Purpose | Boundary |
|---|---|---|
| `transport-manifest.json` | Declares the fixture read-only transport surface | All simulator control operations are prohibited |
| `transport-evidence.json` | Attests that both declared fixture reads are covered | It does not attest a real simulator connection |
| `goal-workflow.json` | Proposes one goal-to-evaluate review step and a criterion | It produces a review checkpoint only, never execution |

Run the deterministic inspections:

```bash
PYTHONPATH=src mirage transport-assess \
  examples/08-parallel-foundations/transport-manifest.json \
  examples/08-parallel-foundations/transport-evidence.json

PYTHONPATH=src mirage goal-workflow-review \
  examples/08-parallel-foundations/goal-workflow.json \
  --backend fixture
```

Both commands parse local JSON and return structured evidence. They do not create a socket, call a model, start or step a simulation, resume a checkpoint, launch a subprocess, write a scene, or actuate hardware.
