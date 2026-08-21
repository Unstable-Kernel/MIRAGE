import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app
from mirage.runtime import (
    DeterministicReviewReport,
    DispatchEligibilityAssessment,
    EvidenceCaptureLineageConsistencyAssessment,
    EvidenceCaptureLineageConsistencyManifest,
    EvidenceGatingConsistencyManifest,
    EvidenceGatingConsistencyStatus,
    assess_evidence_gating_consistency,
)

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples/24-evidence-gating-consistency"


def _load(name: str, model):
    return model.model_validate_json((EXAMPLE / name).read_text(encoding="utf-8"))


def _artifacts():
    return (
        _load("manifest.json", EvidenceGatingConsistencyManifest),
        _load("lineage-manifest.json", EvidenceCaptureLineageConsistencyManifest),
        _load("lineage-assessment.json", EvidenceCaptureLineageConsistencyAssessment),
        _load("dispatch-assessment.json", DispatchEligibilityAssessment),
        _load("report.json", DeterministicReviewReport),
    )


def test_evidence_gating_consistency_accepts_aligned_ineligible_declarations():
    assessment = assess_evidence_gating_consistency(*_artifacts())

    assert assessment.status == EvidenceGatingConsistencyStatus.CONSISTENT
    assert assessment.validated_capture_ids == {"capture-gate-1"}
    assert assessment.execution_permitted is False


def test_evidence_gating_consistency_rejects_missing_declared_dispatch_reason():
    artifacts = list(_artifacts())
    dispatch = artifacts[3].model_copy(update={"reasons": ["live read-only transport is not independently verified"]})
    artifacts[3] = dispatch

    assessment = assess_evidence_gating_consistency(*artifacts)

    assert assessment.status == EvidenceGatingConsistencyStatus.INVALID
    assert any(issue.code == "evidence_gating_dispatch_reason_missing" for issue in assessment.issues)


def test_evidence_gating_consistency_cli_reports_local_assessment():
    files = ["lineage-manifest.json", "lineage-assessment.json", "dispatch-assessment.json", "report.json", "manifest.json"]
    outcome = CliRunner().invoke(app, ["evidence-gating-consistency-assess", *(str(EXAMPLE / file) for file in files)])

    assert outcome.exit_code == 0, outcome.output
    assert json.loads(outcome.output)["execution_permitted"] is False
