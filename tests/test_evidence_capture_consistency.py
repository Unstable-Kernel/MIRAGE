import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app
from mirage.runtime import (
    DeterministicReviewReport,
    EvidenceCaptureConsistencyManifest,
    EvidenceCaptureConsistencyStatus,
    EvidenceProvenanceAssessment,
    EvidenceProvenanceSeal,
    ReviewPolicyEvidenceConsistencyAssessment,
    assess_evidence_capture_consistency,
)

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples/22-evidence-capture-consistency"


def _load(name: str, model):
    return model.model_validate_json((EXAMPLE / name).read_text(encoding="utf-8"))


def _artifacts():
    return (
        _load("manifest.json", EvidenceCaptureConsistencyManifest),
        _load("evidence-provenance.json", EvidenceProvenanceAssessment),
        _load("review-policy-evidence-assessment.json", ReviewPolicyEvidenceConsistencyAssessment),
        _load("report.json", DeterministicReviewReport),
        [EvidenceProvenanceSeal.model_validate(item) for item in json.loads((EXAMPLE / "evidence-seals.json").read_text(encoding="utf-8"))],
    )


def test_evidence_capture_consistency_accepts_aligned_declarations():
    assessment = assess_evidence_capture_consistency(*_artifacts())

    assert assessment.status == EvidenceCaptureConsistencyStatus.CONSISTENT
    assert assessment.validated_capture_ids == {"capture-declaration-1"}
    assert assessment.execution_permitted is False


def test_evidence_capture_consistency_rejects_capture_seal_drift():
    artifacts = list(_artifacts())
    seals = artifacts[4]
    artifacts[4] = [seals[0].model_copy(update={"capture_method": "different-fixture"})]

    assessment = assess_evidence_capture_consistency(*artifacts)

    assert assessment.status == EvidenceCaptureConsistencyStatus.INVALID
    assert any(issue.code == "evidence_capture_seal_mismatch" for issue in assessment.issues)


def test_evidence_capture_consistency_rejects_missing_report_reference():
    artifacts = list(_artifacts())
    report = artifacts[3].model_copy(deep=True)
    report.sections[0].provenance_references = []
    artifacts[3] = report

    assessment = assess_evidence_capture_consistency(*artifacts)

    assert assessment.status == EvidenceCaptureConsistencyStatus.INVALID
    assert any(issue.code == "evidence_capture_report_reference_missing" for issue in assessment.issues)


def test_evidence_capture_consistency_cli_reports_local_assessment():
    files = [
        "evidence-provenance.json",
        "review-policy-evidence-assessment.json",
        "report.json",
        "evidence-seals.json",
        "manifest.json",
    ]
    outcome = CliRunner().invoke(app, ["evidence-capture-consistency-assess", *(str(EXAMPLE / file) for file in files)])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "consistent"
    assert payload["execution_permitted"] is False
