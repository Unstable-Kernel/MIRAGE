# MIRAGE

> **Multiversal Intelligence for Robotics, Autonomous Systems, and Generative Engineering**

MIRAGE is an AI-native engineering compiler and runtime for robotics and autonomous systems. It is designed to transform heterogeneous engineering knowledge into a versioned **Engineering Intermediate Representation (EIR)**, reason over that representation, and execute validated workflows through replaceable capabilities and adapters.

The first implementation iteration establishes a real foundation rather than claiming the full long-term platform. It delivers EIR 0.1 validation, a provider-neutral model orchestrator, six model-provider adapters, and a small CLI. Simulator execution, graph persistence, autonomous experiment loops, and physical-hardware integration remain roadmap work.

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
uv run pytest
```

The validation and inspection commands are deterministic and do not require an API key. Provider configuration is optional for the first CLI workflow. To configure a model provider, copy `examples/02-model-providers/provider-config.example.yaml`, replace environment-variable references with your own environment, and set `MIRAGE_PROVIDER_CONFIG` to the file path.

## Current status

| Capability | Status |
|---|---|
| EIR 0.1 schema, JSON/YAML serialization, validation | Implemented |
| `mirage validate`, `mirage inspect`, `mirage doctor` | Implemented |
| Provider-neutral typed completion contract | Implemented |
| OpenAI, Anthropic, generic OpenAI-compatible, Ollama, vLLM, llama.cpp adapters | Implemented with mocked contract tests |
| Optional live provider smoke tests | Implemented; opt-in only |
| Engineering State Graph persistence and event history | Implemented |
| Declarative URCP capability registry | Implemented; execution is not included |
| Simulator adapters and URCP execution | Planned |
| Research-paper and robotics-format ingestion | Planned |
| Autonomous experiments and optimization | Planned |
| Physical hardware execution | Planned; requires additional safety gates |

## Documentation

Read [ARCHITECTURE.md](ARCHITECTURE.md) for the system boundaries, [specs/EIR/eir-0.1.md](specs/EIR/eir-0.1.md) for the canonical semantic contract, [specs/ESG/README.md](specs/ESG/README.md) for state history, [specs/URCP/README.md](specs/URCP/README.md) for capability declarations, and [docs/guides/model-providers.md](docs/guides/model-providers.md) for all six provider integrations. Development rules are in [CONTRIBUTING.md](CONTRIBUTING.md), the security model is in [SECURITY.md](SECURITY.md), and the delivery path is in [ROADMAP.md](ROADMAP.md).

## Authorship and contact

MIRAGE is authored and maintained by [Erebuzzz](https://github.com/Erebuzzz) for Unstable Kernel. Contact: `kshitiz23kumar@gmail.com`. LinkedIn: [linkedin.com/in/kksinha23](https://linkedin.com/in/kksinha23).

## License

The core source tree is distributed under the Mozilla Public License 2.0. Specifications and adapters follow the repository licensing policy documented in [docs/legal/third-party.md](docs/legal/third-party.md). See [LICENSE](LICENSE) and [LICENSES/](LICENSES/) for the applicable texts.

## Roadmap

MIRAGE follows a vertical-slice build loop: discover, read, model, plan, implement, test, verify, document, commit, review, and update the roadmap. See [ROADMAP.md](ROADMAP.md) for milestones and acceptance criteria.

## Contributing

Contributions are welcome after reading [CONTRIBUTING.md](CONTRIBUTING.md). Changes to EIR, provider protocols, security, licensing, or public APIs require an RFC or engineering decision record when appropriate.
