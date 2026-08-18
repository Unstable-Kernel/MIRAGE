# Dependency License Register

Every dependency added to MIRAGE should be recorded with its name, version range, source, license, optional/required status, compatibility notes, and security status. The authoritative package metadata and lockfile remain the source of exact resolved versions.

| Dependency family | Purpose | License review |
|---|---|---|
| Pydantic | EIR models and validation | Record resolved version and license in release review |
| PyYAML | YAML serialization | Record resolved version and license in release review |
| Typer | CLI | Record resolved version and license in release review |
| HTTPX | Provider transport and test mocks | Record resolved version and license in release review |
| Provider SDKs | Optional native provider adapters | Review each SDK independently |

Do not introduce a dependency-license conflict without maintainer review. Dependency updates require tests, security review, and changelog coverage when behavior changes.
