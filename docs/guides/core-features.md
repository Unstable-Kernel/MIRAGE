# MIRAGE Core Features Roadmap

## Current core surface

MIRAGE has a versioned EIR 0.1 semantic layer, ESG project state, role-based model orchestration, declarative URCP capabilities, a policy-gated execution runtime, local audit records, validated checkpoints, read-only transport manifests, sandbox enforcement-evidence contracts, EIR-bound M4 workflow and evidence review primitives, release-ready Python artifacts, and a private npm launcher. The implementation emphasizes verified contracts over unverified integrations.

## Upcoming core features

| Priority | Feature | Intended outcome | Explicit boundary |
|---|---|---|---|
| Current | Fixture-backed read-only simulator adapter | Read deterministic project metadata and bounded state snapshots with policy, timeout, cancellation, and sandbox assessment evidence | No simulator connection, control, experiment execution, or actuator path |
| Current | Read-only transport manifest and fixture evidence | Declare permitted read operations and prove deterministic fixture coverage | No real transport connection, live verification, or simulator control |
| Next | Verified real simulator read-only transport | Read project metadata and state through an adapter-specific verified transport | No simulation control, experiment execution, or actuator path |
| Current | Declarative sandbox envelope and enforcement evidence | Deny OS-level envelopes without matching backend claims and verified evidence | No claim of process isolation, cgroups, or container enforcement in the local backend |
| Next | Ledger integrity and retention | Add locking, retention, tamper-evident records, and storage migration | No claim of distributed coordination yet |
| Current | Checkpoint revalidation | Revalidate policy provenance, capability versions, and backend availability before manual resume review | Never automatically execute on load |
| Next | Enforced backend sandbox | Add verified process, CPU, memory, disk, network, filesystem, and cleanup controls around non-cooperative work | No host command execution by default |
| Near-term | EIR ingestion adapters | Translate controlled source formats into EIR with provenance | Do not weaken the canonical EIR contract for one source format |
| Current | Goal-to-evaluate workflow review foundation | Preserve a bounded goal, proposed steps, criteria, policy-bound checkpoint, and manual revalidation result | No provider planning, automatic resume, execution, evaluation, or report generation |
| Current | Deterministic EIR-to-plan and evidence assessment | Validate planned source nodes and criterion evidence against EIR without a model or backend | No engineering correctness judgment, metric execution, or automatic approval |
| Later | Goal-to-evaluate workflow | Connect goals, context, EIR, planning, simulation, evaluation, and report evidence | Keep model reasoning separate from deterministic validation |
| Later | Cross-simulator translation | Map validated semantics across verified simulator adapters | No compatibility claim without adapter-specific tests |
| Later | Research reproduction pipeline | Capture papers, artifacts, environments, and evidence for reproducible studies | No autonomous paper execution without sandboxing and review |

## Delivery principles

Each feature moves through the same loop: define a versioned contract, implement the smallest deterministic slice, add contract tests, verify the boundary, document limitations, update the continuation context, and then commit. A feature remains planned until the repository contains implementation, tests, documentation, and verification evidence.
