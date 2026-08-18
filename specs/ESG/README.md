# Engineering State Graph (ESG)

The Engineering State Graph is the current project-level view of engineering knowledge. It links EIR nodes and relationships to a revision history and records state transitions as structured events.

## Invariants

An ESG has a stable project identifier, a monotonically increasing revision, a current EIR document, and an append-only event list. Event IDs are unique. Each event records its type, timestamp, actor, affected EIR references, and optional details. The ESG does not replace EIR; it tracks the evolving state around EIR.
