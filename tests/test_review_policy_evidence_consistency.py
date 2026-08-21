import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app
from mirage.runtime import (
    DeterministicReportAssessment,
    DeterministicReviewPolicy,
    DeterministicReviewReport,
    EvidenceProvenanceAssessment,
    EvidenceProvenanceSeal,
    ReviewPolicyAssessment,
    ReviewPolicyEvidenceConsistencyManifest,
    ReviewPolicyEvidenceConsistencyStatus,
    assess_review_policy_evidence_consistency,
)

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples/21-review-policy-evidence-reference-consistency"


def _load(name: str, model):
    return model.model_validate_json((EXAMPLE / name).read_text(encoding="utf-8"))


def _artifacts():
    return (
        _load("manifest.json", ReviewPolicyEvidenceConsistencyManifest),
        _load("review-policy.json", DeterministicReviewPolicy),
        _load("review-policy-assessment.json", ReviewPolicyAssessment),
        _load("report.json", DeterministicReviewReport),
        _load("report-assessment.json", DeterministicReportAssessment),
        _load("evidence-provenance.json", EvidenceProvenanceAssessment),
        [EvidenceProvenanceSeal.model_validate(item) for item in json.loads((EXAMPLE / "evidence-seals.json").read_text(encoding="utf-8"))],
    )


def test_review_policy_evidence_consistency_accepts_aligned_declarations():
    assessment = assess_review_policy_evidence_consistency(*_artifacts())

    assert assessment.status == ReviewPolicyEvidenceConsistencyStatus.CONSISTENT
    assert assessment.validated_evidence_ids == {"evidence-reference-1"}
    assert assessment.execution_permitted is False


def test_review_policy_evidence_consistency_rejects_policy_bound_drift():
    artifacts = list(_artifacts())
    artifacts[1] = artifacts[1].model_copy(update={"max_report_sections": 3})

    assessment = assess_review_policy_evidence_consistency(*artifacts)

    assert assessment.status == ReviewPolicyEvidenceConsistencyStatus.INVALID
    assert any(issue.code == "review_policy_evidence_section_limit_mismatch" for issue in assessment.issues)


def test_review_policy_evidence_consistency_rejects_missing_report_reference():
    artifacts = list(_artifacts())
    report = artifacts[3].model_copy(deep=True)
    report.sections[0].provenance_references = []
    artifacts[3] = report

    assessment = assess_review_policy_evidence_consistency(*artifacts)

    assert assessment.status == ReviewPolicyEvidenceConsistencyStatus.INVALID
    assert any(issue.code == "review_policy_evidence_reference_missing" for issue in assessment.issues)


def test_review_policy_evidence_consistency_cli_reports_reference_only_assessment():
    files = [
        "review-policy.json",
        "review-policy-assessment.json",
        "report.json",
        "report-assessment.json",
        "evidence-provenance.json",
        "evidence-seals.json",
        "manifest.json",
    ]
    outcome = CliRunner().invoke(app, ["review-policy-evidence-consistency-assess", *(str(EXAMPLE / file) for file in files)])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "consistent"
    assert payload["execution_permitted"] is False
