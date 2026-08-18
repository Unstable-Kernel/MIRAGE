import asyncio

from mirage.runtime import CapabilityExecutor, ExecutionPolicy, ExecutionRequest, ExecutionStatus, default_registry


def run(request):
    return asyncio.run(CapabilityExecutor(default_registry()).execute(request))


def test_simulation_is_denied_by_default():
    result = run(ExecutionRequest(capability_id="run_simulation", backend="local"))
    assert result.status == ExecutionStatus.DENIED


def test_local_simulation_is_deterministic_when_explicitly_allowed():
    request = ExecutionRequest(
        capability_id="run_simulation",
        backend="local",
        inputs={"seed": 7},
        policy=ExecutionPolicy(allow_simulation=True, allowed_backends={"local"}),
    )
    first = run(request)
    second = run(request)
    assert first.status == ExecutionStatus.SUCCEEDED
    assert first.outputs == second.outputs


def test_coppeliasim_boundary_reports_unavailable():
    request = ExecutionRequest(
        capability_id="run_simulation",
        backend="coppeliasim",
        policy=ExecutionPolicy(allow_simulation=True, allowed_backends={"coppeliasim"}),
    )
    result = run(request)
    assert result.status == ExecutionStatus.UNAVAILABLE
    assert "not configured" in result.message
