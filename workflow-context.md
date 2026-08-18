# Workflow Context

## Task

Continue MIRAGE after Iteration 1 by implementing EIR-backed Engineering State Graph primitives and a deterministic Universal Robotics Capability Protocol registry.

## Current status

Implementation is complete and verified locally. The change is ready to commit on `feat/iteration-1-foundation`.

## Completed work

- Added ESG models with project ID, revision, EIR payload, structured event history, duplicate-event protection, JSON persistence, and snapshot loading.
- Added URCP capability descriptors with version, schemas, preconditions, postconditions, resources, side effects, failure modes, backend compatibility, determinism, streaming, cancellation, and security class.
- Added deterministic capability registration, exact lookup, duplicate detection, backend filtering, security filtering, stable ordering, and a default declarative capability set.
- Added CLI commands `esg-inspect` and `capabilities`.
- Added ESG and URCP specifications, examples, tests, README updates, roadmap updates, changelog updates, and `code_review.md` at the end of the build as requested.

## Changed files

- `src/mirage/knowledge/esg.py`
- `src/mirage/knowledge/__init__.py`
- `src/mirage/runtime/urcp.py`
- `src/mirage/runtime/__init__.py`
- `src/mirage/cli.py`
- `tests/test_esg_urcp.py`
- `specs/ESG/README.md`
- `specs/URCP/README.md`
- `examples/03-esg-urcp/state.json`
- `examples/03-esg-urcp/README.md`
- `ARCHITECTURE.md`
- `README.md`
- `ROADMAP.md`
- `CHANGELOG.md`
- `code_review.md`

## Verification

- `13 passed` with pytest.
- Ruff passed for `src`, `tests`, and `scripts`.
- EIR schema consistency check passed.
- ESG CLI inspection passed.
- URCP backend filtering passed.
- `git diff --check` passed.
- Repository-wide em dash scan was performed.

## Known limitations

ESG is currently an in-process JSON snapshot model. URCP is declarative and has no execution engine, policy enforcement, adapter lifecycle, or simulator support. The default registry's simulator names are declarations for future filtering only.

## Commit state

The working tree contains the next iteration changes and is not yet committed. The next action is to inspect the diff, create a focused commit, and report the commit and verification results. Push only if the user explicitly requests synchronization.
