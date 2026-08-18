# Model Providers

MIRAGE uses a typed provider-neutral contract. The initial matrix is implemented in `src/mirage/core/providers.py`; provider-specific transport remains behind `ProviderAdapter`.

| Provider | Endpoint style | Credentials | Default capability notes |
|---|---|---|---|
| OpenAI | OpenAI `/v1/chat/completions` | `OPENAI_API_KEY` | Structured output advertised |
| Anthropic | Anthropic `/v1/messages` | `ANTHROPIC_API_KEY` | Native system/content-block translation |
| Generic OpenAI-compatible | Injected `/v1/chat/completions` | User-defined | Capability declaration depends on endpoint |
| Ollama | Local OpenAI-compatible server | Usually none | Local execution; model must be installed |
| vLLM | OpenAI-compatible `/v1` server | Optional | Server model and feature flags are user-defined |
| llama.cpp | OpenAI-compatible local server | Optional | Local server capability subset |

Use `examples/02-model-providers/provider-config.example.yaml` as the starting point. Environment variables are expanded at runtime. Never commit literal keys or provider responses containing sensitive engineering data.

Default tests use mocked HTTP transports and do not require credentials or local servers. Optional live smoke tests must be explicitly enabled with `MIRAGE_RUN_PROVIDER_SMOKE=1`; unavailable credentials or local services are reported as skips, not silently treated as successful support.
