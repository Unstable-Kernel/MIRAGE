import asyncio

import httpx
import pytest

from mirage.core import ProviderName, make_adapter
from mirage.eir import load_data, validate_document


def test_valid_fixture():
    result = validate_document(load_data("examples/01-validate-eir/robot_model.yaml"))
    assert result.ok


def test_missing_relationship_endpoint_is_rejected():
    data = load_data("examples/01-validate-eir/robot_model.yaml")
    data["relationships"][0]["target_id"] = "missing"
    result = validate_document(data)
    assert not result.ok
    assert any(error.code == "RELATIONSHIP_ENDPOINT_MISSING" for error in result.errors)


@pytest.mark.parametrize("provider", list(ProviderName))
def test_all_provider_adapters_register(provider):
    adapter = make_adapter(provider.value, "test-model", "http://test.local/v1", "secret")
    assert adapter.name == provider
    assert adapter.capabilities().provider == provider.value


def test_openai_compatible_normalization():
    async def run():
        async def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "id": "x",
                    "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
                },
            )

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        adapter = make_adapter("openai", "test", "http://test.local/v1", "secret", client)
        from mirage.core import CompletionRequest

        response = await adapter.complete(
            CompletionRequest("test", [{"role": "user", "content": "hi"}])
        )
        await client.aclose()
        return response

    assert asyncio.run(run()).text == "ok"
