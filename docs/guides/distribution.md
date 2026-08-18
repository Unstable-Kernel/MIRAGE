# MIRAGE Distribution Guide

## Purpose

This guide defines the release-ready package boundaries for MIRAGE. It prepares local, testable artifacts only. It does not authorize publication, reserve a registry name, or publish an artifact.

## Package identity

MIRAGE remains the product, repository, and command name. The exact unscoped `mirage` name cannot be used for either registry because unrelated packages already occupy it.

| Surface | Identifier | Status | Responsibility |
|---|---|---|---|
| Product and command | `MIRAGE`, `mirage` | Current | Core Python CLI |
| Python distribution | `mirage-engineering` | Build-ready, unpublished | Canonical runtime and CLI |
| npm distribution | `@unstable-kernel/mirage` | Private, build-ready, unpublished | Thin launcher only |

The PyPI `mirage` record belongs to a JWST simulator, and the npm `mirage` record belongs to a Primus plugin. The candidates above returned no current registry records during this build, but they must be checked again immediately before release. [1] [2]

## Architecture

```mermaid
flowchart LR
    USER[Developer] --> PYPI[mirage-engineering]
    USER --> NPM[@unstable-kernel/mirage]
    PYPI --> CLI[mirage command]
    NPM --> CLI
    CLI --> RUNTIME[MIRAGE Python runtime]
    RUNTIME --> EIR[EIR validation]
    RUNTIME --> URCP[URCP execution policy]
    RUNTIME --> ESG[ESG and audit state]
```

The Python distribution is authoritative. The npm package only delegates to an installed `mirage` binary and must not reproduce the engineering runtime in JavaScript. This preserves one semantic and execution core.

## Local verification

Build and validate the Python artifacts locally:

```bash
python -m build
twine check dist/*
python -m pip install --force-reinstall dist/*.whl
mirage doctor
```

Validate the scoped npm launcher without publishing:

```bash
cd packages/npm-launcher
npm test
npm run check
npm pack --dry-run
```

## Publishing boundary

> Publishing requires an explicit maintainer decision. No repository workflow may publish to PyPI or npm automatically.

Before a human maintainer publishes either artifact, the release must have a final registry availability check, a clean build, passing test and lint suite, artifact validation, a versioned changelog entry, a signed Git tag, an approved security review, and a release note. The npm package must be changed from `private: true` only as part of that explicit release decision.

## Versioning

The current build metadata is `0.1.0a0`, a PEP 440 alpha version. EIR, runtime, and adapters may evolve independently, but the published runtime package must expose a single installed version through `mirage.__version__` and its distribution metadata.

## Website release status

The MIRAGE website queries GitHub's public Releases API. When no release exists, the site intentionally reports a source release in progress rather than inventing a package version or changelog entry. Publishing a GitHub release after artifact verification will allow the website to display it automatically.

## References

[1] [PyPI: mirage](https://pypi.org/project/mirage/)

[2] [npm: mirage](https://www.npmjs.com/package/mirage)
