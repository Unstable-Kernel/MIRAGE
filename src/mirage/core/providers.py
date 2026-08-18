from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import httpx


class ProviderName(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENAI_COMPATIBLE = "openai_compatible"
    OLLAMA = "ollama"
    VLLM = "vllm"
    LLAMA_CPP = "llama_cpp"


class ModelRole(StrEnum):
    PLANNING_REASONING = "planning_reasoning"
    CODE_GENERATION = "code_generation"
    VISION_ANALYSIS = "vision_analysis"
    LONG_CONTEXT_SYNTHESIS = "long_context_synthesis"
    MATHEMATICAL_REASONING = "mathematical_reasoning"
    FAILURE_ANALYSIS = "failure_analysis"
    TECHNICAL_WRITING = "technical_writing"
    REVIEW_CRITICAL = "review_critical"


@dataclass(frozen=True)
class CompletionRequest:
    model: str
    messages: list[dict[str, Any]]
    system: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    response_format: dict[str, Any] | None = None
    timeout: float = 60.0


@dataclass(frozen=True)
class CompletionResponse:
    text: str
    provider: str
    model: str
    finish_reason: str | None = None
    usage: dict[str, Any] = field(default_factory=dict)
    raw_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderCapabilities:
    provider: str
    streaming: bool = True
    structured_output: bool = False
    vision: bool = False
    cancellation: bool = True


class ProviderError(RuntimeError):
    def __init__(self, code: str, message: str, provider: str, retryable: bool = False) -> None:
        super().__init__(message)
        self.code, self.provider, self.retryable = code, provider, retryable


class ProviderAdapter:
    name: ProviderName

    def __init__(
        self,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.model, self.base_url, self.api_key = model, base_url, api_key
        self.client = client or httpx.AsyncClient(timeout=60.0)

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(self.name.value)

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        raise NotImplementedError

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    async def _post(
        self, url: str, payload: dict[str, Any], headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        try:
            response = await self.client.post(url, json=payload, headers=headers or {})
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ProviderError(
                    "INVALID_RESPONSE", "provider returned a non-object response", self.name.value
                )
            return data
        except ProviderError:
            raise
        except httpx.TimeoutException as exc:
            raise ProviderError(
                "TIMEOUT", "provider request timed out", self.name.value, True
            ) from exc
        except httpx.HTTPStatusError as exc:
            retryable = exc.response.status_code in {408, 429, 500, 502, 503, 504}
            code = "RATE_LIMIT" if exc.response.status_code == 429 else "PROVIDER_HTTP_ERROR"
            raise ProviderError(
                code,
                f"provider returned HTTP {exc.response.status_code}",
                self.name.value,
                retryable,
            ) from exc
        except (httpx.HTTPError, json.JSONDecodeError) as exc:
            raise ProviderError(
                "TRANSPORT_ERROR", "provider transport failed", self.name.value, True
            ) from exc

    def _openai_payload(self, request: CompletionRequest) -> dict[str, Any]:
        messages = (
            [{"role": "system", "content": request.system}] if request.system else []
        ) + request.messages
        payload: dict[str, Any] = {"model": request.model, "messages": messages}
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.response_format:
            payload["response_format"] = request.response_format
        return payload


class OpenAICompatibleAdapter(ProviderAdapter):
    def __init__(
        self,
        name: ProviderName,
        model: str,
        base_url: str,
        api_key: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(model, base_url.rstrip("/"), api_key, client)
        self.name = name

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            self.name.value, structured_output=self.name in {ProviderName.OPENAI, ProviderName.VLLM}
        )

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        data = await self._post(
            f"{self.base_url}/chat/completions", self._openai_payload(request), self._headers()
        )
        try:
            choice = data["choices"][0]
            message = choice.get("message", {})
            return CompletionResponse(
                str(message.get("content", "")),
                self.name.value,
                request.model,
                choice.get("finish_reason"),
                data.get("usage", {}),
                data.get("id"),
            )
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError(
                "INVALID_RESPONSE", "missing chat completion fields", self.name.value
            ) from exc


class AnthropicAdapter(ProviderAdapter):
    name = ProviderName.ANTHROPIC

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(self.name.value, structured_output=False, vision=True)

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": request.messages,
            "max_tokens": request.max_tokens or 1024,
        }
        if request.system:
            payload["system"] = request.system
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        headers = {
            "x-api-key": self.api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        data = await self._post(f"{self.base_url.rstrip('/')}/v1/messages", payload, headers)
        try:
            text = "".join(
                str(block.get("text", ""))
                for block in data.get("content", [])
                if block.get("type") == "text"
            )
            return CompletionResponse(
                text,
                self.name.value,
                request.model,
                data.get("stop_reason"),
                data.get("usage", {}),
                data.get("id"),
            )
        except (AttributeError, TypeError) as exc:
            raise ProviderError(
                "INVALID_RESPONSE", "invalid Anthropic response", self.name.value
            ) from exc


def make_adapter(
    provider: str,
    model: str,
    base_url: str,
    api_key: str | None = None,
    client: httpx.AsyncClient | None = None,
) -> ProviderAdapter:
    name = ProviderName(provider)
    if name == ProviderName.ANTHROPIC:
        return AnthropicAdapter(model, base_url, api_key, client)
    return OpenAICompatibleAdapter(name, model, base_url, api_key, client)
