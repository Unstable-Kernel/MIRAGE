# MIRAGE Roadmap

MIRAGE is built through small, testable vertical slices. A milestone is complete only when implementation, tests, documentation, examples, and verification exist.

| Milestone | Scope | Status |
|---|---|---|
| M0 | Organization foundation, CI, package boundaries, minimal CLI | In progress in Iteration 1 |
| M1 | EIR 0.1 schema, serialization, validation, structured JSON/YAML frontend | In progress in Iteration 1 |
| M2 | Model orchestrator and complete initial provider matrix | In progress in Iteration 1 |
| M3 | First simulator adapter and URCP execution slice | Planned |
| M4 | Goal → context → EIR → plan → simulate → evaluate → report workflow | Planned |
| M5 | Cross-simulator translation | Planned |
| M6 | Research reproduction pipeline | Planned |
| M7 | Hypothesis generation, experiment selection, diagnosis, optimization | Planned |

## Acceptance principles

Each milestone must preserve provenance, reproducibility, model independence, simulator independence, human control, and deterministic validation. Future hardware work requires explicit safety gates and must not be inferred from simulation success.

## Next highest-value slice

After Iteration 1, implement ESG persistence and a deterministic URCP capability registry, then add one simulator adapter only after the EIR-to-capability boundary has contract tests.
