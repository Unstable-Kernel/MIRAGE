# MIRAGE Roadmap

MIRAGE is built through small, testable vertical slices. A milestone is complete only when implementation, tests, documentation, examples, and verification exist.

| Milestone | Scope | Status |
|---|---|---|
| M0 | Organization foundation, CI, package boundaries, minimal CLI | Complete |

| M1 | EIR 0.1 schema, serialization, validation, structured local JSON/YAML frontend | Complete |

| M2 | Model orchestrator and complete initial provider matrix | Complete with mocked provider contracts |

| M3 | First simulator adapter and URCP execution slice | Execution contracts, deterministic local backend, audit ledger, checkpoints, timeout/cancellation budgets, sandbox assessment, checkpoint revalidation, fixture-backed read-only metadata/state extraction, transport evidence, and sandbox enforcement-evidence contracts implemented; CoppeliaSim transport, real OS isolation, and simulator control remain unverified |

| M4 | Goal → context → EIR → plan → simulate → evaluate → report workflow | Review-only goal, EIR-bound steps, criteria, policy-bound checkpoint, deterministic plan, evidence assessment, redacted context, provenance review trace, review-trace event consistency, policy-provenance consistency, approval chain, advisory eligibility, persistence interface, revocation review, provenance seal, lifecycle validation, controlled context, deterministic report artifact, cross-artifact consistency, reference-only provenance consistency, report-seal consistency, and readiness foundation implemented; controlled real context, planning model, execution, policy-bound evaluation, authenticated approval persistence, and report pipeline remain planned |
| M5 | Cross-simulator translation | Planned |
| M6 | Research reproduction pipeline | Planned |
| M7 | Hypothesis generation, experiment selection, diagnosis, optimization | Planned |

## Acceptance principles

Each milestone must preserve provenance, reproducibility, model independence, simulator independence, human control, and deterministic validation. Future hardware work requires explicit safety gates and must not be inferred from simulation success.

## Next highest-value slice
The URCP execution contract, policy gate, deterministic local backend, execution ledger, workflow checkpoints, hardening controls, sandbox assessment, checkpoint revalidation, fixture-backed simulator metadata/state extraction, transport evidence, sandbox enforcement-evidence contracts, review-only M4 workflow foundation, local ledger integrity and retention contracts, local EIR candidate ingestion, reference-only EIR, evidence, and report provenance consistency, report-seal consistency, review-trace event consistency, and policy-provenance consistency are now implemented. The next blocked increment is a documented and independently verified real read-only simulator transport, followed by an OS-enforced backend sandbox and deterministic M4 evidence flow. Simulator control and experiment execution remain out of scope until these prerequisites are verified.

## Delivery accounting

The roadmap currently has eight milestone rows. M0 through M2 are complete. M3 and M4 have active partial foundations: M3 contains the bounded execution and deterministic transport-evidence contracts, while M4 contains review-only workflow contracts. Real verified transport, enforced isolation, deterministic planning, evidence evaluation, and reporting remain. M5 through M7 are planned. This means three completed milestones, two active partial milestones, and three planned major milestones. Scope and risk are uneven, so MIRAGE does not claim a completion percentage.

See [docs/guides/delivery-status.md](docs/guides/delivery-status.md) for the six primary remaining delivery streams, their dependencies, and the evidence required before they can be marked complete.
