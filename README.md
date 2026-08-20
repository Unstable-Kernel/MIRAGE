# MIRAGE

> **Multiversal Intelligence for Robotics, Autonomous Systems, and Generative Engineering**

MIRAGE is an AI-native engineering compiler and runtime for robotics and autonomous systems. It is designed to transform heterogeneous engineering knowledge into a versioned **Engineering Intermediate Representation (EIR)**, reason over that representation, and execute validated workflows through replaceable capabilities and adapters.

The current implementation establishes a real foundation rather than claiming the full long-term platform. It delivers EIR 0.1 validation, a provider-neutral model orchestrator, six model-provider adapters, revisioned ESG snapshots, a policy-gated URCP runtime, an audit ledger, checkpoint revalidation, sandbox assessment, deterministic fixture-backed read-only simulator inspection, transport verification manifests, sandbox enforcement-evidence contracts, and non-executing goal-to-evaluate workflow review with deterministic EIR-to-plan, evidence assessment, context bundles, review traces, approval chains, advisory dispatch eligibility, persistence interface definitions, revocation review, provenance seals, lifecycle validation, controlled context schemas, and deterministic report artifacts. Real simulator transport, host-level sandbox enforcement, simulator control, autonomous experiment loops, and physical-hardware integration remain roadmap work.

## Core thesis

MIRAGE separates probabilistic reasoning from deterministic engineering semantics and execution:

```text
Goal / artifacts
      |
      v
Cognitive Plane: roles, planning, explanation
      |
      v
Engineering Compiler: ingestion, EIR, validation, lowering
      |
      v
Knowledge Plane: ESG, evidence, decisions, provenance
      |
      v
Execution Plane: URCP capabilities and adapters
      |
      +--> model providers: OpenAI, Anthropic, compatible, Ollama, vLLM, llama.cpp
      +--> future simulators, toolchains, and hardware
```

The model provider is replaceable. The simulator is replaceable. **EIR and capability contracts are the architecture.**

## Iteration 1 quickstart

Install Python 3.11 or newer and `uv`, then run:

```bash
uv sync
uv run mirage doctor
uv run mirage validate examples/01-validate-eir/robot_model.yaml
uv run mirage inspect examples/01-validate-eir/robot_model.yaml
uv run mirage simulator-metadata examples/07-simulator-adapter/fixture-simulation.json --include-state
uv run mirage transport-assess examples/08-parallel-foundations/transport-manifest.json examples/08-parallel-foundations/transport-evidence.json
uv run mirage goal-workflow-review examples/08-parallel-foundations/goal-workflow.json --backend fixture
uv run mirage goal-workflow-plan examples/09-deterministic-workflow/workflow.json examples/01-validate-eir/robot_model.yaml
uv run mirage goal-workflow-evidence examples/09-deterministic-workflow/workflow.json examples/01-validate-eir/robot_model.yaml examples/09-deterministic-workflow/evidence.json
uv run mirage workflow-context-inspect examples/09-deterministic-workflow/workflow.json examples/01-validate-eir/robot_model.yaml examples/10-context-review/context.json
uv run mirage review-trace-assess examples/09-deterministic-workflow/workflow.json examples/01-validate-eir/robot_model.yaml examples/10-context-review/context.json examples/09-deterministic-workflow/evidence.json examples/10-context-review/review-trace.json
uv run mirage approval-chain-assess examples/09-deterministic-workflow/workflow.json examples/01-validate-eir/robot_model.yaml examples/10-context-review/context.json examples/09-deterministic-workflow/evidence.json examples/10-context-review/review-trace.json examples/11-guarded-approval/approval-chain.json
uv run mirage evidence-provenance-assess examples/09-deterministic-workflow/workflow.json examples/01-validate-eir/robot_model.yaml examples/09-deterministic-workflow/evidence.json examples/12-governance-foundations/evidence-seals.json
uv run mirage deterministic-report-assess examples/09-deterministic-workflow/workflow.json examples/01-validate-eir/robot_model.yaml examples/10-context-review/context.json examples/09-deterministic-workflow/evidence.json examples/13-controlled-report/context-schema.json examples/13-controlled-report/context-envelope.json examples/12-governance-foundations/evidence-seals.json examples/13-controlled-report/report.json
uv run pytest
```

The validation, inspection, transport assessment, workflow review, EIR-bound workflow planning, evidence assessment, context inspection, review-trace assessment, approval-chain assessment, persistence readiness, revocation review, provenance seal, lifecycle assessment, controlled-context, deterministic-report, and fixture-backed simulator metadata commands are deterministic and do not require an API key. The transport and simulator commands read only local JSON fixtures and cannot connect to, control, or step a simulator. The workflow commands create human-review artifacts and cannot resume or execute a workflow. Provider configuration is optional for the first CLI workflow. To configure a model provider, copy `examples/02-model-providers/provider-config.example.yaml`, replace environment-variable references with your own environment, and set `MIRAGE_PROVIDER_CONFIG` to the file path.

## Distribution status

MIRAGE is build-ready but not published to PyPI or npm. The intended Python distribution is `mirage-engineering`, while `@unstable-kernel/mirage` is a private npm launcher that delegates to the canonical Python CLI. The exact `mirage` name is occupied on both registries by unrelated packages. See [docs/guides/distribution.md](docs/guides/distribution.md) for package identity, local artifact verification, and the explicit publishing boundary.

## Current status

| Capability | Status |
|---|---|
| EIR 0.1 schema, JSON/YAML serialization, validation | Implemented |
| `mirage validate`, `mirage inspect`, `mirage doctor` | Implemented |
| Provider-neutral typed completion contract | Implemented |
| OpenAI, Anthropic, generic OpenAI-compatible, Ollama, vLLM, llama.cpp adapters | Implemented with mocked contract tests |
| Optional live provider smoke tests | Implemented; opt-in only |
| Engineering State Graph persistence and event history | Implemented |
| Declarative URCP capability registry | Implemented |
| Policy-gated URCP execution and deterministic local backend | Implemented |
| Persistent execution ledger and workflow checkpoints | Implemented as local JSONL and validated snapshots |
| Execution timeout, cancellation, input/output budget checks, and policy provenance | Implemented for the policy-gated runtime |
| Declarative backend sandbox assessment and checkpoint revalidation | Implemented; no OS isolation or automatic resume is claimed |
| Sandbox enforcement-evidence contracts | Implemented; only matching backend capabilities and verified evidence can satisfy an OS-enforced envelope claim |
| Inspection-only CoppeliaSim adapter boundary | Implemented as unavailable and non-connecting; no simulator control is exposed |
| Fixture-backed read-only simulator metadata and state extraction | Implemented with deterministic contract fixtures, policy checks, timeout handling, and sandbox assessment evidence |
| Transport verification manifest and fixture evidence | Implemented; CoppeliaSim ZeroMQ reference remains unverified, non-connecting, and control-prohibited |
| Goal-to-evaluate workflow review foundation | Implemented as a bounded review checkpoint; no planning model, execution, resume, or report pipeline is claimed |
| Deterministic EIR-to-plan and evidence assessment | Implemented as local validation and review artifacts; no engineering judgment or execution is claimed |
| Context bundles and review traces | Implemented as redacted references and provenance checks; no retrieval, approval, or execution is claimed |
| Approval chains and dispatch eligibility | Implemented as local advisory checks; no authority, dispatch, or execution is claimed |
| Governance foundations | Implemented as local persistence, revocation, provenance, and lifecycle contracts; no credentials, writes, or execution are claimed |
| Controlled context and deterministic report | Implemented as schema-bound references and review artifacts; no retrieval, generated claims, signing, publication, or execution is claimed |
| CoppeliaSim read-only transport | Unavailable until transport and semantics are verified; no connection or control is attempted |
| Simulator control and verified URCP execution | Planned; explicit safety review and verified adapter behavior are required |
| Research-paper and robotics-format ingestion | Planned |
| Autonomous experiments and optimization | Planned |
| Physical hardware execution | Planned; requires additional safety gates |

## Documentation

Read [ARCHITECTURE.md](ARCHITECTURE.md) for the system boundaries, [specs/EIR/eir-0.1.md](specs/EIR/eir-0.1.md) for the canonical semantic contract, [specs/ESG/README.md](specs/ESG/README.md) for state history, [specs/URCP/README.md](specs/URCP/README.md) for capability declarations, [docs/guides/urcp-execution.md](docs/guides/urcp-execution.md) for execution policy, [docs/guides/execution-hardening.md](docs/guides/execution-hardening.md) for timeout and cancellation behavior, [docs/guides/read-only-simulator-adapter.md](docs/guides/read-only-simulator-adapter.md) for metadata and state extraction boundaries, [docs/guides/parallel-foundations.md](docs/guides/parallel-foundations.md) for the transport, sandbox, and M4 foundation contracts, [docs/guides/deterministic-workflow-evidence.md](docs/guides/deterministic-workflow-evidence.md) for EIR-bound planning and evidence review, [docs/guides/context-review-trace.md](docs/guides/context-review-trace.md) for context and provenance review, [docs/guides/guarded-approval-eligibility.md](docs/guides/guarded-approval-eligibility.md) for approval and advisory dispatch checks, [docs/guides/governance-foundations.md](docs/guides/governance-foundations.md) for persistence, revocation, provenance, and lifecycle contracts, [docs/guides/controlled-context-report.md](docs/guides/controlled-context-report.md) for schema-bound context and deterministic reports, [docs/guides/sandbox-checkpoint-revalidation.md](docs/guides/sandbox-checkpoint-revalidation.md) for sandbox and checkpoint safety, [docs/guides/execution-ledger.md](docs/guides/execution-ledger.md) for audit and checkpoint behavior, [docs/guides/model-providers.md](docs/guides/model-providers.md) for all six provider integrations, [docs/guides/distribution.md](docs/guides/distribution.md) for release readiness, [docs/guides/delivery-status.md](docs/guides/delivery-status.md) for the quantified baseline and remaining delivery streams, and [docs/guides/core-features.md](docs/guides/core-features.md) for the upcoming core roadmap. Development rules are in [CONTRIBUTING.md](CONTRIBUTING.md), the security model is in [SECURITY.md](SECURITY.md), and the delivery path is in [ROADMAP.md](ROADMAP.md).

## Authorship and contact

MIRAGE is authored and maintained by [Erebuzzz](https://github.com/Erebuzzz) for Unstable Kernel. Contact: `kshitiz23kumar@gmail.com`. LinkedIn: [linkedin.com/in/kksinha23](https://linkedin.com/in/kksinha23).

## License

The core source tree is distributed under the Mozilla Public License 2.0. Specifications and adapters follow the repository licensing policy documented in [docs/legal/third-party.md](docs/legal/third-party.md). See [LICENSE](LICENSE) and [LICENSES/](LICENSES/) for the applicable texts.

## Roadmap

MIRAGE follows a vertical-slice build loop: discover, read, model, plan, implement, test, verify, document, commit, review, and update the roadmap. See [ROADMAP.md](ROADMAP.md) for milestones and acceptance criteria.

## Contributing

Contributions are welcome after reading [CONTRIBUTING.md](CONTRIBUTING.md). Changes to EIR, provider protocols, security, licensing, or public APIs require an RFC or engineering decision record when appropriate.
