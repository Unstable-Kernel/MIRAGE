import asyncio
import json

from mirage.runtime import (
    CapabilityExecutor,
    ExecutionLedger,
    ExecutionPolicy,
    ExecutionRequest,
    ExecutionStatus,
    WorkflowCheckpoint,
    default_registry,
)


def test_executor_records_redacted_audit_for_denied_request(tmp_path):
    ledger = ExecutionLedger(tmp_path / "executions.jsonl")
    executor = CapabilityExecutor(default_registry(), ledger=ledger)
    request = ExecutionRequest(
        capability_id="run_simulation",
        backend="local",
        inputs={"api_key": "do-not-persist", "seed": 7},
    )
    result = asyncio.run(executor.execute(request))
    assert result.status == ExecutionStatus.DENIED
    records = list(ledger.records())
    assert len(records) == 1
    assert records[0].inputs["api_key"] == "[REDACTED]"
    assert records[0].inputs["seed"] == 7


def test_successful_execution_records_request_and_result(tmp_path):
    ledger = ExecutionLedger(tmp_path / "executions.jsonl")
    executor = CapabilityExecutor(default_registry(), ledger=ledger)
    request = ExecutionRequest(
        capability_id="run_simulation",
        backend="local",
        policy=ExecutionPolicy(allow_simulation=True, allowed_backends={"local"}),
        inputs={"seed": 4},
    )
    result = asyncio.run(executor.execute(request))
    assert result.status == ExecutionStatus.SUCCEEDED
    record = next(iter(ledger.records()))
    assert record.status == "succeeded"
    assert record.outputs["mode"] == "deterministic-local"
    assert ledger.get(record.request_id).request_id == record.request_id


def test_checkpoint_advances_and_round_trips(tmp_path):
    path = tmp_path / "checkpoint.json"
    checkpoint = WorkflowCheckpoint(workflow_id="workflow.demo", stage="goal", state={"goal": "inspect"})
    checkpoint.advance("plan", {"steps": ["validate"]}, "request-1")
    checkpoint.save(path)
    restored = WorkflowCheckpoint.load(path)
    assert restored.revision == 1
    assert restored.stage == "plan"
    assert restored.execution_ids == ["request-1"]
    assert json.loads(path.read_text())['workflow_id'] == "workflow.demo"
