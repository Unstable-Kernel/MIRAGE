# Workflow Context

## Task

Complete the MIRAGE read-only simulator project metadata and state-extraction adapter iteration.

## Current status

The fixture-backed read-only adapter implementation, contract tests, CLI, examples, documentation, roadmap, code review, and continuation context are ready for final verification and a focused local commit on `feat/iteration-1-foundation`. Do not push or publish without an explicit user request.

## Completed work

`src/mirage/runtime/simulator_adapter.py` defines `SimulatorProjectMetadata`, `SimulatorObjectState`, `SimulatorStateSnapshot`, `ReadOnlySimulatorAdapter`, and `ReadOnlySimulatorResult`. The public protocol includes only metadata and state-snapshot reads. Every result includes a sandbox assessment and reports `control_available: false`.

`FixtureSimulatorAdapter` loads a validated local JSON fixture and deep-copies deterministic metadata and snapshots. It supports policy allow/deny checks, backend allow-lists, unsupported sandbox-envelope denial, output-size limits, request timeouts, and cooperative `CancellationToken` handling. `CoppeliaSimReadOnlyAdapter` stays unavailable and non-connecting until a real transport and state semantics are independently verified.

The URCP registry now exposes `inspect_simulator_state@0.1` as a read-only descriptor. The `mirage simulator-metadata` command reads the fixture path and can include the matching snapshot. The deterministic fixture lives in `examples/07-simulator-adapter/`.

## Verification

| Check | Result |
|---|---|
| Focused adapter tests | 5 passed |
| Focused Ruff check | Passed |
| Fixture CLI | Returned typed metadata and state snapshot results with declarative sandbox assessment |

## Known limitations

The fixture adapter is not a real simulator transport. Its `transport_verified` result only means fixture parsing and result semantics are deterministic and covered by tests. No network connection, simulator state read, simulator control, scene change, host command, external side effect, or physical actuation exists.

The CoppeliaSim adapter is intentionally unavailable. Endpoint configuration is recorded without a connection attempt. Sandbox controls remain declarative on the local backend and do not provide cgroups, containers, filesystem mounts, CPU/RAM/disk quotas, network enforcement, or subprocess isolation.

## Important files

| File | Responsibility |
|---|---|
| `src/mirage/runtime/simulator_adapter.py` | Read-only models, protocol, deterministic fixture adapter, unavailable CoppeliaSim boundary |
| `src/mirage/runtime/sandbox.py` | Conservative sandbox assessment recorded by every adapter result |
| `src/mirage/runtime/execution.py` | Policy and cancellation model shared by adapter requests |
| `src/mirage/cli.py` | `simulator-metadata` inspection command |
| `tests/test_simulator_adapter.py` | Read-only adapter contract suite |
| `docs/guides/read-only-simulator-adapter.md` | Adapter contract, limitations, and verification guide |
| `examples/07-simulator-adapter/` | Canonical deterministic fixture and CLI example |

## Next recommended action

Run the complete repository verification suite, inspect the final diff, and create a focused local commit. Push only on explicit user request. The next technical slice should be an independently verified real read-only simulator transport, or a separately enforced OS-level backend sandbox. Neither slice should introduce simulator control without a distinct safety design and approval path.
