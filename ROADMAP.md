# MIRAGE Roadmap

MIRAGE is built through small, testable vertical slices. A milestone is complete only when implementation, tests, documentation, examples, and verification exist.

| Milestone | Scope | Status |
|---|---|---|
| M0 | Organization foundation, CI, package boundaries, minimal CLI | Complete |

| M1 | EIR 0.1 schema, serialization, validation, structured JSON/YAML frontend | Complete |

| M2 | Model orchestrator and complete initial provider matrix | Complete with mocked provider contracts |

| M3 | First simulator adapter and URCP execution slice | Execution contracts, deterministic local backend, audit ledger, checkpoints, timeout/cancellation budgets, and inspection-only boundary implemented; CoppeliaSim integration remains unverified |

| M4 | Goal → context → EIR → plan → simulate → evaluate → report workflow | Planned |
| M5 | Cross-simulator translation | Planned |
| M6 | Research reproduction pipeline | Planned |
| M7 | Hypothesis generation, experiment selection, diagnosis, optimization | Planned |

## Acceptance principles

Each milestone must preserve provenance, reproducibility, model independence, simulator independence, human control, and deterministic validation. Future hardware work requires explicit safety gates and must not be inferred from simulation success.

## Next highest-value slice
The URCP execution contract, policy gate, deterministic local backend, execution ledger, workflow checkpoints, and hardening controls are now implemented. The next increment is a verified simulator inspection adapter with project metadata and state extraction, then a backend sandbox envelope. Simulation control and experiment execution remain out of scope until both are verified.
