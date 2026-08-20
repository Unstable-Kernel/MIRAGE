# Universal Robotics Capability Protocol (URCP)

URCP is MIRAGE's execution abstraction. A capability describes an engineering operation without exposing a simulator, toolchain, or hardware API to the planner.

## Capability descriptor

Each capability has a stable ID, version, description, input and output schemas, preconditions, postconditions, resource requirements, side effects, failure modes, compatible backends, determinism, streaming, cancellation, and security classification.

## Registry behavior

The current registry is deterministic and declarative. It registers descriptors, rejects duplicate IDs and versions, lists capabilities, filters by backend and security class, and resolves an exact capability version. The execution runtime consumes these descriptors through policy gates. Read-only operations are allowed by default, simulation requires explicit permission, and external side effects and physical actuation remain denied by default. Execution returns a structured result and never accepts arbitrary host commands.

Execution belongs to a backend adapter runtime with policy gates, declared sandbox assessment, request-level resource budgets, audit logging, and human approval where required. OS-enforced envelope claims now require matching backend capabilities and verified enforcement evidence. The local execution backend is deterministic test infrastructure and remains declarative only. Every execution attempt can be recorded in an append-only local ledger with redacted inputs and outputs. Workflow checkpoints are validated snapshots and never resume execution automatically. The CoppeliaSim boundaries are not verified simulator integrations and report unavailable without opening a connection.

## Initial examples

The current descriptors cover `inspect_model`, `validate_eir`, `generate_urdf`, `run_simulation`, `inspect_simulator_state`, `review_goal_workflow`, `assess_workflow_evidence`, `inspect_workflow_context`, `assess_review_trace`, `assess_human_approval`, `assess_dispatch_eligibility`, `assess_approval_persistence`, `assess_approval_revocation`, `assess_evidence_provenance`, and `assess_workflow_lifecycle`. `inspect_simulator_state@0.1` is a read-only fixture-backed metadata and bounded state-extraction contract. `review_goal_workflow@0.1` revalidates a bounded goal-to-evaluate workflow for manual review and never executes or resumes it. `assess_workflow_evidence@0.1` validates declared evidence references for human review without evaluating engineering correctness or dispatching a backend. `inspect_workflow_context@0.1` validates redacted context references without retrieval, while `assess_review_trace@0.1` validates required provenance stages without changing state. `assess_human_approval@0.1` validates an approval chain without granting authority, and `assess_dispatch_eligibility@0.1` reports future prerequisites without invoking a backend. The governance descriptors validate persistence readiness, declared revocation, provenance seals, and lifecycle order without credentials, writes, retrieval, or state mutation. `run_simulation@0.1` remains only a declaration and requires explicit policy permission. No real simulator or hardware integration is claimed by registering a descriptor.
