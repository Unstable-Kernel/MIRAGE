import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from mirage.cli import app
from mirage.runtime import ExecutionAuditRecord, ExecutionLedger, LedgerIntegrityError


def _record(request_id: str) -> ExecutionAuditRecord:
    timestamp = datetime(2026, 8, 20, tzinfo=UTC)
    return ExecutionAuditRecord(
        request_id=request_id,
        actor="ledger-test",
        capability_id="inspect_model",
        version="0.1",
        backend="local",
        status="succeeded",
        started_at=timestamp,
        completed_at=timestamp,
        inputs={"model": request_id},
        outputs={"observed": True},
    )


def test_ledger_envelopes_form_a_verifiable_digest_chain(tmp_path):
    ledger = ExecutionLedger(tmp_path / "executions.jsonl")
    ledger.append(_record("request-1"))
    ledger.append(_record("request-2"))

    assessment = ledger.verify_integrity()

    assert assessment.status == "valid"
    assert assessment.valid is True
    assert assessment.record_count == 2
    assert assessment.first_digest is not None
    assert assessment.last_digest is not None
    assert assessment.first_digest != assessment.last_digest
    assert ledger.lock_path.exists()


def test_ledger_integrity_detects_tampered_record_and_refuses_append(tmp_path):
    ledger = ExecutionLedger(tmp_path / "executions.jsonl")
    ledger.append(_record("request-1"))
    payload = json.loads(ledger.path.read_text(encoding="utf-8"))
    payload["record"]["message"] = "tampered"
    ledger.path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    assessment = ledger.verify_integrity()

    assert assessment.status == "invalid"
    assert assessment.issues[0].line_number == 1
    assert "digest" in assessment.issues[0].message
    with pytest.raises(LedgerIntegrityError):
        ledger.append(_record("request-2"))


def test_ledger_retention_compacts_to_tail_with_a_chain_anchor(tmp_path):
    ledger = ExecutionLedger(tmp_path / "executions.jsonl")
    for index in range(1, 5):
        ledger.append(_record(f"request-{index}"))

    result = ledger.retain(max_records=2)
    assessment = ledger.verify_integrity()

    assert result.status == "compacted"
    assert result.discarded_records == 2
    assert result.retained_records == 2
    assert result.retention_anchor is not None
    assert assessment.status == "valid"
    assert assessment.retention_anchor == result.retention_anchor
    assert [record.request_id for record in ledger.records()] == ["request-3", "request-4"]


def test_malformed_ledger_is_reported_without_silent_recovery(tmp_path):
    ledger = ExecutionLedger(tmp_path / "executions.jsonl")
    ledger.path.write_text("{not-json}\n", encoding="utf-8")

    assessment = ledger.verify_integrity()

    assert assessment.status == "invalid"
    assert assessment.valid is False
    assert assessment.issues[0].line_number == 1
    assert assessment.issues[0].message == "invalid JSON"


def test_ledger_verify_cli_reports_the_non_executing_integrity_assessment(tmp_path):
    ledger = ExecutionLedger(tmp_path / "executions.jsonl")
    ledger.append(_record("request-1"))

    outcome = CliRunner().invoke(app, ["ledger-verify", str(ledger.path)])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "valid"
    assert payload["valid"] is True


def test_ledger_integrity_example_is_a_valid_retained_fixture():
    fixture = Path(__file__).parents[1] / "examples/15-ledger-integrity/executions.jsonl"

    assessment = ExecutionLedger(fixture).verify_integrity()

    assert assessment.status == "valid"
    assert assessment.record_count == 2
    assert assessment.retention_anchor is not None
    assert assessment.retention_anchor.discarded_records == 1
