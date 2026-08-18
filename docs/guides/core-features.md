# MIRAGE Core Features Roadmap

## Current core surface

MIRAGE has a versioned EIR 0.1 semantic layer, ESG project state, role-based model orchestration, declarative URCP capabilities, a policy-gated execution runtime, local audit records, validated checkpoints, release-ready Python artifacts, and a private npm launcher. The implementation emphasizes verified contracts over unverified integrations.

## Upcoming core features

| Priority | Feature | Intended outcome | Explicit boundary |
|---|---|---|---|
| Next | Verified simulator inspection adapter | Read simulator project metadata and state through a tested transport | No simulation control, experiment execution, or actuator path |
| Next | Backend sandbox envelope | Enforce CPU, memory, disk, process, and network limits around non-cooperative work | No host command execution by default |
| Next | Ledger integrity and retention | Add locking, retention, tamper-evident records, and storage migration | No claim of distributed coordination yet |
| Near-term | Checkpoint revalidation | Revalidate policy, capability versions, and backend availability before manual resume | Never automatically execute on load |
| Near-term | EIR ingestion adapters | Translate controlled source formats into EIR with provenance | Do not weaken the canonical EIR contract for one source format |
| Later | Goal to evaluate workflow | Connect goals, context, EIR, planning, simulation, evaluation, and report evidence | Keep model reasoning separate from deterministic validation |
| Later | Cross-simulator translation | Map validated semantics across verified simulator adapters | No compatibility claim without adapter-specific tests |
| Later | Research reproduction pipeline | Capture papers, artifacts, environments, and evidence for reproducible studies | No autonomous paper execution without sandboxing and review |

## Delivery principles

Each feature moves through the same loop: define a versioned contract, implement the smallest deterministic slice, add contract tests, verify the boundary, document limitations, update the continuation context, and then commit. A feature remains planned until the repository contains implementation, tests, documentation, and verification evidence.
