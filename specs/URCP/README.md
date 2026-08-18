# Universal Robotics Capability Protocol (URCP)

URCP is MIRAGE's execution abstraction. A capability describes an engineering operation without exposing a simulator, toolchain, or hardware API to the planner.

## Capability descriptor

Each capability has a stable ID, version, description, input and output schemas, preconditions, postconditions, resource requirements, side effects, failure modes, compatible backends, determinism, streaming, cancellation, and security classification.

## Registry behavior

The Iteration 2 registry is deterministic and declarative. It registers descriptors, rejects duplicate IDs and versions, lists capabilities, filters by backend and security class, and resolves an exact capability version. It does not execute operations. Execution belongs to a future adapter runtime with policy gates, sandboxing, resource limits, network policy, audit logging, and human approval where required.

## Initial examples

The initial descriptors cover `inspect_model`, `validate_eir`, `generate_urdf`, and `run_simulation` as declarations only. No simulator or hardware integration is claimed by registering a descriptor.
