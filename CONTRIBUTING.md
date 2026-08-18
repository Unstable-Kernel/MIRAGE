# Contributing to MIRAGE

MIRAGE is developed by Unstable Kernel as an open engineering platform. The project prioritizes correctness, architectural integrity, reproducibility, maintainability, and then feature count.

## Development setup

Use Python 3.11 or newer and `uv`:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy packages
```

Do not commit virtual environments, generated caches, provider credentials, downloaded models, simulator binaries, or private engineering artifacts.

## Branches and commits

Use a focused branch such as `feat/eir-validation` or `fix/provider-redaction`. Commit messages follow Conventional Commits. Keep commits coherent, explain public behavior in documentation, and avoid mixing unrelated refactors with feature work.

## Required quality gate

A feature is incomplete until its tests, documentation, examples where useful, and failure modes are included. Run focused tests first, then the full suite. Changes to EIR, URCP, public APIs, security, licensing, or architecture require an RFC or engineering decision record.

## Provider adapters

Every provider adapter must implement the shared typed protocol, declare capabilities accurately, normalize errors, redact credentials, and include mocked contract tests. Live provider calls are never required in default CI. Adapter-specific behavior must remain behind the adapter boundary.

## Specifications

EIR and future URCP changes are specification changes. Document motivation, alternatives, compatibility, security impact, migration, open questions, and validation strategy. Never silently introduce a breaking schema change.

## Pull requests

Pull requests should state what changed, why it changed, tests run, tests not run, security and licensing implications, documentation updates, and known limitations. Reviewers should verify that probabilistic reasoning remains separated from deterministic validation and execution policy.

## Code of conduct and security

All contributors must follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Do not report vulnerabilities in public issues; follow [SECURITY.md](SECURITY.md).
