# Third-Party and Licensing Policy

The MIRAGE core source tree is MPL-2.0. Specifications, adapters, SDK-facing interfaces, examples, and documentation may use the explicit licenses stated below. Each subtree must carry a clear notice when its license differs from the root.

| Area | Default license | Notes |
|---|---|---|
| Core implementation | MPL-2.0 | Root `LICENSE` governs the core source tree |
| Specifications and protocol schemas | Apache-2.0 | Permissive reuse for interoperability contracts |
| Provider and simulator adapters | Apache-2.0 | Third-party SDK terms still apply |
| Examples | MIT | Examples may be reused independently |
| Original documentation | CC BY 4.0 | Attribution required where applicable |

MIRAGE must not relicense third-party code or engineering artifacts. Imported papers, datasets, CAD, simulator assets, and provider SDKs retain their original terms. Maintainers should update `dependency-licenses.md`, `attribution.md`, and `NOTICE` when dependencies introduce attribution or notice obligations.
