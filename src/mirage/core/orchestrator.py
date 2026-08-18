from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .providers import (
    CompletionRequest,
    CompletionResponse,
    ModelRole,
    ProviderAdapter,
    ProviderError,
    make_adapter,
)

_ENV = re.compile(r"\$\{([A-Z0-9_]+)(?::-(.*?))?\}")


@dataclass(frozen=True)
class ProviderConfig:
    providers: dict[str, dict[str, Any]]
    roles: dict[str, list[str]]

    @classmethod
    def from_file(cls, path: str | Path) -> ProviderConfig:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        return cls(_expand(data.get("providers", {})), data.get("roles", {}))

    def redacted(self) -> dict[str, Any]:
        result: dict[str, Any] = {"providers": {}, "roles": self.roles}
        for name, config in self.providers.items():
            result["providers"][name] = {
                key: ("***" if "key" in key.lower() or "token" in key.lower() else value)
                for key, value in config.items()
            }
        return result


def _expand(value: Any) -> Any:
    if isinstance(value, str):
        return _ENV.sub(lambda match: os.getenv(match.group(1), match.group(2) or ""), value)
    if isinstance(value, dict):
        return {key: _expand(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand(item) for item in value]
    return value


class ModelOrchestrator:
    def __init__(
        self, config: ProviderConfig, adapters: dict[str, ProviderAdapter] | None = None
    ) -> None:
        self.config = config
        self.adapters = adapters or {}
        for name, provider in config.providers.items():
            if name not in self.adapters:
                self.adapters[name] = make_adapter(
                    provider["type"],
                    provider.get("model", "default"),
                    provider.get("base_url", "http://localhost:11434"),
                    provider.get("api_key") or None,
                )

    async def complete(
        self, role: ModelRole, messages: list[dict[str, Any]], **kwargs: Any
    ) -> CompletionResponse:
        candidates = self.config.roles.get(role.value, [])
        if not candidates:
            raise ProviderError(
                "ROLE_UNCONFIGURED", f"no provider configured for role {role.value}", "mirage"
            )
        last_error: ProviderError | None = None
        for name in candidates:
            adapter = self.adapters.get(name)
            if adapter is None:
                last_error = ProviderError(
                    "PROVIDER_UNAVAILABLE", f"provider {name} is not registered", name
                )
                continue
            provider = self.config.providers[name]
            request = CompletionRequest(
                model=provider.get("model", adapter.model), messages=messages, **kwargs
            )
            try:
                return await adapter.complete(request)
            except ProviderError as exc:
                last_error = exc
                if not exc.retryable:
                    continue
        raise last_error or ProviderError(
            "NO_PROVIDER", "no provider could complete request", "mirage"
        )
