# MIRAGE Governance

MIRAGE is maintained by Unstable Kernel. The initial maintainer and project author is [Erebuzzz](https://github.com/Erebuzzz), `kshitiz23kumar@gmail.com`.

## Maintainer responsibilities

Maintainers protect the architecture, review security-sensitive changes, steward specifications, manage releases, and ensure that documentation and tests accompany implementation. Maintainers may delegate review but retain responsibility for release and security decisions.

## Specification governance

EIR, URCP, agent-protocol, and other public specifications are changed through an RFC. An RFC records the problem, motivation, alternatives, proposed design, compatibility, security impact, migration path, and open questions. Accepted RFCs become the authoritative design record for implementation.

## Breaking changes

Breaking changes require a versioned specification update, migration guidance, updated fixtures, and an explicit changelog entry. Runtime and adapter APIs should follow semantic versioning independently of EIR versions.

## Releases

Releases are cut from reviewed commits on `main` after CI passes. Release notes must identify schema changes, provider compatibility changes, security fixes, limitations, and reproducibility information.

## Decision records

Significant architectural or engineering decisions are recorded in `docs/decisions/` as EDRs. Decisions include alternatives, evidence, assumptions, risks, verification, author, and status.

## Security escalation

Security reports are handled privately through `SECURITY.md`. Maintainers may delay a release or disable a capability when a safety or credential issue is unresolved.
