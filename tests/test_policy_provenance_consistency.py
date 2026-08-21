import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app
from mirage.runtime import (
    ControlledContextEnvelope,
    DeterministicReviewPolicy,
    DeterministicReviewReport,
    ExecutionPolicy,
    PolicyProvenanceConsistencyManifest,
    PolicyProvenanceConsistencyStatus,
    ReviewPolicyAssessment,
    WorkflowContextBundle,
    WorkflowReviewTrace,
    assess_policy_provenance_consistency,
)

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples/20-policy-provenance-consistency"


def _load(name: str, model):
    return model.model_validate_json((EXAMPLE / name).read_text(encoding="utf-8"))


def _artifacts():
    return (
        _load("manifest.json", PolicyProvenanceConsistencyManifest),
        _load("policy.json", ExecutionPolicy),
        _load("context-bundle.json", WorkflowContextBundle),
        _load("context-envelope.json", ControlledContextEnvelope),
        _load("review-trace.json", WorkflowReviewTrace),
        _load("report.json", DeterministicReviewReport),
        _load("review-policy.json", DeterministicReviewPolicy),
        _load("review-policy-assessment.json", ReviewPolicyAssessment),
    )


def test_policy_provenance_consistency_accepts_aligned_declarations():
    assessment = assess_policy_provenance_consistency(*_artifacts())

    assert assessment.status == PolicyProvenanceConsistencyStatus.CONSISTENT
    assert "trace_policy_provenance" in assessment.matched_declarations
    assert assessment.execution_permitted is False


def test_policy_provenance_consistency_rejects_trace_provenance_drift():
    artifacts = list(_artifacts())
    artifacts[4] = artifacts[4].model_copy(deep=True)
    artifacts[4].policy_provenance["revision"] = "unexpected"

    assessment = assess_policy_provenance_consistency(*artifacts)

    assert assessment.status == PolicyProvenanceConsistencyStatus.INVALID
    assert any(issue.code == "policy_provenance_trace_mismatch" for issue in assessment.issues)


def test_policy_provenance_consistency_rejects_report_workflow_drift():
    artifacts = list(_artifacts())
    artifacts[5] = artifacts[5].model_copy(update={"workflow_id": "unexpected-workflow"})

    assessment = assess_policy_provenance_consistency(*artifacts)

    assert assessment.status == PolicyProvenanceConsistencyStatus.INVALID
    assert any(issue.code == "policy_provenance_workflow_mismatch" for issue in assessment.issues)


def test_policy_provenance_consistency_cli_reports_reference_only_assessment():
    files = [
        "policy.json",
        "context-bundle.json",
        "context-envelope.json",
        "review-trace.json",
        "report.json",
        "review-policy.json",
        "review-policy-assessment.json",
        "manifest.json",
    ]
    outcome = CliRunner().invoke(app, ["policy-provenance-consistency-assess", *(str(EXAMPLE / file) for file in files)])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "consistent"
    assert payload["execution_permitted"] is False
