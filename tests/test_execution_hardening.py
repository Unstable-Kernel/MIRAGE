import asyncio

from mirage.runtime import (
    CancellationToken,
    CapabilityExecutor,
    ExecutionPolicy,
    ExecutionRequest,
    ExecutionStatus,
    ResourceLimits,
    default_inspection_backends,
    default_registry,
)


def run(request: ExecutionRequest, cancellation: CancellationToken | None = None, backends=None):
    return asyncio.run(CapabilityExecutor(default_registry(), backends=backends).execute(request, cancellation))


def simulation_request(**kwargs):
    policy = kwargs.pop("policy", ExecutionPolicy(allow_simulation=True, allowed_backends={"local"}))
    return ExecutionRequest(
        capability_id="run_simulation",
        backend="local",
        policy=policy,
        **kwargs,
    )


def test_resource_limit_rejects_oversized_inputs_before_execution():
    request = simulation_request(inputs={"artifact": "x" * 30}, policy=ExecutionPolicy(allow_simulation=True, allowed_backends={"local"}, resource_limits=ResourceLimits(max_input_bytes=10)))
    result = run(request)
    assert result.status == ExecutionStatus.DENIED
    assert "input exceeds" in result.message
    assert result.metadata["policy_provenance"]["policy_id"] == "local-default"


def test_requested_timeout_cannot_exceed_policy_limit():
    request = simulation_request(timeout_seconds=3, policy=ExecutionPolicy(allow_simulation=True, allowed_backends={"local"}, resource_limits=ResourceLimits(max_timeout_seconds=1)))
    result = run(request)
    assert result.status == ExecutionStatus.DENIED
    assert "timeout exceeds" in result.message


def test_pre_cancelled_request_is_recorded_without_backend_execution():
    token = CancellationToken()
    token.cancel("cancelled by test")
    result = run(simulation_request(), token)
    assert result.status == ExecutionStatus.CANCELLED
    assert result.message == "cancelled by test"


class SlowBackend:
    name = "local"

    async def execute(self, descriptor, inputs, cancellation=None):
        await asyncio.sleep(0.03)
        return {"slow": True}


def test_timeout_cancels_a_slow_backend():
    result = run(simulation_request(timeout_seconds=0.001), backends={"local": SlowBackend()})
    assert result.status == ExecutionStatus.TIMED_OUT
    assert result.metadata["timeout_seconds"] == 0.001


def test_inspection_boundary_never_claims_control_or_connectivity():
    result = asyncio.run(default_inspection_backends("tcp://127.0.0.1:23000")["coppeliasim"].inspect())
    assert result.status.value == "unavailable"
    assert result.endpoint_configured is True
    assert result.control_available is False
    assert "no connection" in result.message
