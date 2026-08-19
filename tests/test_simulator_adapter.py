import asyncio
import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app
from mirage.runtime import (
    CancellationToken,
    CoppeliaSimReadOnlyAdapter,
    ExecutionPolicy,
    FixtureSimulatorAdapter,
    ReadOnlySimulatorStatus,
    SandboxAssessmentStatus,
)

FIXTURE = Path(__file__).parents[1] / "examples/07-simulator-adapter/fixture-simulation.json"


def adapter() -> FixtureSimulatorAdapter:
    return FixtureSimulatorAdapter.from_file(FIXTURE)


def run(awaitable):
    return asyncio.run(awaitable)


def test_fixture_adapter_reads_deterministic_metadata_and_snapshot_without_control():
    active_adapter = adapter()

    metadata = run(active_adapter.read_project_metadata())
    snapshot = run(active_adapter.read_state_snapshot())

    assert metadata.status == ReadOnlySimulatorStatus.AVAILABLE
    assert metadata.metadata is not None
    assert metadata.metadata.project_id == "fixture.pick-and-place"
    assert metadata.control_available is False
    assert metadata.transport_verified is True
    assert metadata.sandbox_assessment.status == SandboxAssessmentStatus.DECLARATIVE_ONLY
    assert snapshot.status == ReadOnlySimulatorStatus.AVAILABLE
    assert snapshot.snapshot is not None
    assert snapshot.snapshot.snapshot_id == "fixture.pick-and-place.t0"
    assert len(snapshot.snapshot.objects) == 3
    assert snapshot.control_available is False


def test_adapter_respects_read_only_policy_backend_and_sandbox_denials():
    active_adapter = adapter()

    denied_policy = run(active_adapter.read_project_metadata(policy=ExecutionPolicy(allow_read_only=False)))
    denied_backend = run(active_adapter.read_project_metadata(policy=ExecutionPolicy(allowed_backends={"coppeliasim"})))
    denied_sandbox = run(
        active_adapter.read_project_metadata(
            policy=ExecutionPolicy(sandbox={"max_memory_mb": 128})
        )
    )

    assert denied_policy.status == ReadOnlySimulatorStatus.DENIED
    assert denied_backend.status == ReadOnlySimulatorStatus.DENIED
    assert denied_sandbox.status == ReadOnlySimulatorStatus.DENIED
    assert denied_sandbox.sandbox_assessment.status == SandboxAssessmentStatus.DENIED


def test_adapter_enforces_timeout_with_cancellation_token():
    class DelayedFixtureAdapter(FixtureSimulatorAdapter):
        async def _metadata_source(self):
            await asyncio.sleep(0.05)
            return await super()._metadata_source()

    active_adapter = DelayedFixtureAdapter(adapter().metadata, adapter().snapshot)
    token = CancellationToken()

    result = run(active_adapter.read_project_metadata(timeout_seconds=0.001, cancellation=token))

    assert result.status == ReadOnlySimulatorStatus.TIMED_OUT
    assert token.cancelled is True
    assert result.control_available is False


def test_coppeliasim_adapter_reports_unavailable_without_transport_connection():
    result = run(CoppeliaSimReadOnlyAdapter(endpoint="tcp://127.0.0.1:23000").read_state_snapshot())

    assert result.status == ReadOnlySimulatorStatus.UNAVAILABLE
    assert result.transport_verified is False
    assert result.control_available is False
    assert result.observations["endpoint_configured"] == "true"
    assert result.observations["transport"] == "unverified"
    assert result.observations["transport_manifest_id"] == "coppeliasim-zmq-read-only-reference-v1"
    assert result.observations["transport_protocol"] == "zeromq-remote-api"
    assert "no connection or control operation" in result.message


def test_simulator_metadata_cli_reads_fixture_and_optional_snapshot():
    outcome = CliRunner().invoke(app, ["simulator-metadata", str(FIXTURE), "--include-state"])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["metadata"]["status"] == "available"
    assert payload["snapshot"]["status"] == "available"
    assert payload["metadata"]["control_available"] is False
