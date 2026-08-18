# @unstable-kernel/mirage

This package is a thin Node.js launcher for the canonical MIRAGE Python CLI. It deliberately does not reimplement MIRAGE in JavaScript.

## Current release boundary

The launcher is marked `private` during release preparation and must not be published until the repository owner completes the release checklist. When the Python distribution is published as `mirage-engineering`, a global install can expose the same `mirage` command for Node.js-centric environments.

```bash
npx @unstable-kernel/mirage doctor
```

The launcher resolves the `mirage` binary from `PATH`. For testing or managed environments, set `MIRAGE_COMMAND` to the executable to invoke.

## Safety and ownership

The npm package is scoped to `@unstable-kernel` to avoid the occupied unscoped `mirage` name. Registry publication requires explicit maintainer authorization, an availability recheck, a signed release tag, artifact verification, and a changelog entry.
