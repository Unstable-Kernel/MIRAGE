import asyncio

from mirage.runtime import (
    CapabilityExecutor,
    CheckpointCapabilityRequirement,
    ExecutionPolicy,
    ExecutionRequest,
    ExecutionStatus,
    PolicyProvenance,
    SandboxEnvelope,
    WorkflowCheckpoint,
    default_registry,
)


def run(request: ExecutionRequest):
    return asyncio.run(CapabilityExecutor(default_registry()).execute(request))


def test_local_backend_reports_default_sandbox_as_declarative_only():
    result = run(
        ExecutionRequest(
            capability_id="run_simulation",
            backend="local",
            policy=ExecutionPolicy(allow_simulation=True, allowed_backends={"local"}),
        )
    )
    assert result.status == ExecutionStatus.SUCCEEDED
    assert result.metadata["sandbox_assessment"]["status"] == "declarative_only"


def test_requested_os_resource_limit_is_denied_without_enforcer():
    result = run(
        ExecutionRequest(
            capability_id="run_simulation",
            backend="local",
            policy=ExecutionPolicy(
                allow_simulation=True,
                allowed_backends={"local"},
                sandbox=SandboxEnvelope(max_memory_mb=256),
            ),
        )
    )
    assert result.status == ExecutionStatus.DENIED
    assert result.metadata["sandbox_assessment"]["status"] == "denied"


def test_checkpoint_revalidation_detects_policy_and_capability_drift():
    checkpoint = WorkflowCheckpoint(
        workflow_id="workflow-1",
        stage="awaiting-review",
        policy_provenance=PolicyProvenance(policy_id="approved", revision="1").model_dump(mode="json"),
        required_capabilities=[
            CheckpointCapabilityRequirement(capability_id="run_simulation", version="0.1", backend="local"),
            CheckpointCapabilityRequirement(capability_id="missing", version="1"),
        ],
    )
    result = checkpoint.revalidate(default_registry(), ExecutionPolicy())
    codes = {issue.code for issue in result.issues}
    assert result.valid is False
    assert {"policy_provenance_mismatch", "capability_denied", "capability_missing"} <= codes


def test_checkpoint_revalidation_succeeds_when_active_policy_and_capabilities_match():
    policy = ExecutionPolicy(
        allow_simulation=True,
        allowed_backends={"local"},
        provenance=PolicyProvenance(policy_id="approved", revision="1"),
    )
    checkpoint = WorkflowCheckpoint(
        workflow_id="workflow-2",
        stage="awaiting-review",
        policy_provenance=policy.provenance.model_dump(mode="json"),
        required_capabilities=[CheckpointCapabilityRequirement(capability_id="run_simulation", version="0.1", backend="local")],
    )
    result = checkpoint.revalidate(default_registry(), policy)
    assert result.valid is True
    assert result.issues == []
