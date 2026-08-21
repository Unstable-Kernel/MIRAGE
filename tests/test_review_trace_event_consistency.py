import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app
from mirage.runtime import (
    ReviewTraceAssessment,
    ReviewTraceEventConsistencyManifest,
    ReviewTraceEventConsistencyStatus,
    WorkflowReviewTrace,
    assess_review_trace_event_consistency,
)

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples/19-review-trace-event-consistency"


def _artifacts():
    trace = WorkflowReviewTrace.model_validate_json((EXAMPLE / "review-trace.json").read_text(encoding="utf-8"))
    trace_assessment = ReviewTraceAssessment.model_validate_json((EXAMPLE / "trace-assessment.json").read_text(encoding="utf-8"))
    manifest = ReviewTraceEventConsistencyManifest.model_validate_json((EXAMPLE / "manifest.json").read_text(encoding="utf-8"))
    return manifest, trace, trace_assessment


def test_review_trace_event_consistency_accepts_aligned_declarations():
    manifest, trace, trace_assessment = _artifacts()

    assessment = assess_review_trace_event_consistency(manifest, trace, trace_assessment)

    assert assessment.status == ReviewTraceEventConsistencyStatus.CONSISTENT
    assert len(assessment.matched_event_types) == 4
    assert assessment.execution_permitted is False


def test_review_trace_event_consistency_rejects_declared_digest_mismatch():
    manifest, trace, trace_assessment = _artifacts()
    trace = trace.model_copy(deep=True)
    trace.events[2].artifact_digest = "sha256:tampered-evidence"

    assessment = assess_review_trace_event_consistency(manifest, trace, trace_assessment)

    assert assessment.status == ReviewTraceEventConsistencyStatus.INVALID
    assert any(issue.code == "trace_event_digest_mismatch" for issue in assessment.issues)


def test_review_trace_event_consistency_rejects_policy_provenance_mismatch():
    manifest, trace, trace_assessment = _artifacts()
    trace = trace.model_copy(deep=True)
    trace.policy_provenance["revision"] = "unexpected"

    assessment = assess_review_trace_event_consistency(manifest, trace, trace_assessment)

    assert assessment.status == ReviewTraceEventConsistencyStatus.INVALID
    assert any(issue.code == "trace_event_policy_provenance_mismatch" for issue in assessment.issues)


def test_review_trace_event_consistency_cli_reports_reference_only_assessment():
    files = ["review-trace.json", "trace-assessment.json", "manifest.json"]
    outcome = CliRunner().invoke(app, ["review-trace-event-consistency-assess", *(str(EXAMPLE / file) for file in files)])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "consistent"
    assert payload["execution_permitted"] is False
