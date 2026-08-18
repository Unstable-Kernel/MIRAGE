# Universal Robotics Capability Protocol (URCP)

URCP is MIRAGE's execution abstraction. A capability describes an engineering operation without exposing a simulator, toolchain, or hardware API to the planner.

## Capability descriptor

Each capability has a stable ID, version, description, input and output schemas, preconditions, postconditions, resource requirements, side effects, failure modes, compatible backends, determinism, streaming, cancellation, and security classification.

## Registry behavior

The current registry is deterministic and declarative. It registers descriptors, rejects duplicate IDs and versions, lists capabilities, filters by backend and security class, and resolves an exact capability version. The execution runtime consumes these descriptors through policy gates. Read-only operations are allowed by default, simulation requires explicit permission, and external side effects and physical actuation remain denied by default. Execution returns a structured result and never accepts arbitrary host commands.

Execution belongs to a backend adapter runtime with policy gates, declared sandbox assessment, request-level resource budgets, audit logging, and human approval where required. The local execution backend is deterministic test infrastructure. Every execution attempt can be recorded in an append-only local ledger with redacted inputs and outputs. Workflow checkpoints are validated snapshots and never resume execution automatically. The CoppeliaSim boundaries are not verified simulator integrations and report unavailable without opening a connection. The local sandbox assessment is declarative only and does not claim operating-system isolation.

## Initial examples

The current descriptors cover `inspect_model`, `validate_eir`, `generate_urdf`, `run_simulation`, and `inspect_simulator_state`. `inspect_simulator_state@0.1` is a read-only fixture-backed metadata and bounded state-extraction contract. `run_simulation@0.1` remains only a declaration and requires explicit policy permission. No real simulator or hardware integration is claimed by registering a descriptor.
