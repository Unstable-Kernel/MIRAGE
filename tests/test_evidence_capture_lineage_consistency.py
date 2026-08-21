from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app
from mirage.runtime import (
    EvidenceCaptureConsistencyAssessment,
    EvidenceCaptureConsistencyManifest,
    EvidenceCaptureLineageConsistencyManifest,
    EvidenceCaptureLineageConsistencyStatus,
    assess_evidence_capture_lineage_consistency,
)

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples/23-evidence-capture-lineage-consistency"


def _load(name: str, model):
    return model.model_validate_json((EXAMPLE / name).read_text(encoding="utf-8"))


def _artifacts():
    return (
        _load("lineage-manifest.json", EvidenceCaptureLineageConsistencyManifest),
        _load("capture-manifest.json", EvidenceCaptureConsistencyManifest),
        _load("capture-assessment.json", EvidenceCaptureConsistencyAssessment),
    )


def test_capture_lineage_consistency_accepts_aligned_declarations():
    assessment = assess_evidence_capture_lineage_consistency(*_artifacts())

    assert assessment.status == EvidenceCaptureLineageConsistencyStatus.CONSISTENT
    assert assessment.validated_capture_ids == {"capture-lineage-1"}
    assert assessment.execution_permitted is False


def test_capture_lineage_consistency_rejects_evidence_drift():
    lineage_manifest, capture_manifest, capture_assessment = _artifacts()
    lineage_manifest = lineage_manifest.model_copy(deep=True)
    lineage_manifest.declarations[0].evidence_id = "unexpected-evidence"

    assessment = assess_evidence_capture_lineage_consistency(lineage_manifest, capture_manifest, capture_assessment)

    assert assessment.status == EvidenceCaptureLineageConsistencyStatus.INVALID
    assert any(issue.code == "capture_lineage_evidence_mismatch" for issue in assessment.issues)


def test_capture_lineage_consistency_rejects_self_references():
    lineage_manifest, capture_manifest, capture_assessment = _artifacts()
    lineage_manifest = lineage_manifest.model_copy(deep=True)
    lineage_manifest.declarations[0].predecessor_capture_ids.add("capture-lineage-1")

    assessment = assess_evidence_capture_lineage_consistency(lineage_manifest, capture_manifest, capture_assessment)

    assert assessment.status == EvidenceCaptureLineageConsistencyStatus.INVALID
    assert any(issue.code == "capture_lineage_self_reference" for issue in assessment.issues)


def test_capture_lineage_consistency_cli_reports_local_assessment():
    files = ["capture-manifest.json", "capture-assessment.json", "lineage-manifest.json"]
    outcome = CliRunner().invoke(app, ["evidence-capture-lineage-consistency-assess", *(str(EXAMPLE / file) for file in files)])

    assert outcome.exit_code == 0, outcome.output
    assert '"status":"consistent"' in outcome.output
    assert '"execution_permitted":false' in outcome.output
