import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app
from mirage.runtime import (
    DeterministicReviewReport,
    ReportProvenanceAssessment,
    ReportProvenanceSeal,
    ReportSealConsistencyManifest,
    ReportSealConsistencyStatus,
    ReviewTraceAssessment,
    WorkflowReviewTrace,
    assess_report_seal_consistency,
)

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples/18-report-seal-consistency"


def _artifacts():
    report = DeterministicReviewReport.model_validate_json((EXAMPLE / "report.json").read_text(encoding="utf-8"))
    seal = ReportProvenanceSeal.model_validate_json((EXAMPLE / "report-seal.json").read_text(encoding="utf-8"))
    provenance = ReportProvenanceAssessment.model_validate_json((EXAMPLE / "provenance-assessment.json").read_text(encoding="utf-8"))
    trace = WorkflowReviewTrace.model_validate_json((EXAMPLE / "review-trace.json").read_text(encoding="utf-8"))
    trace_assessment = ReviewTraceAssessment.model_validate_json((EXAMPLE / "trace-assessment.json").read_text(encoding="utf-8"))
    manifest = ReportSealConsistencyManifest.model_validate_json((EXAMPLE / "manifest.json").read_text(encoding="utf-8"))
    return manifest, report, seal, provenance, trace, trace_assessment


def test_report_seal_consistency_accepts_aligned_supplied_declarations():
    manifest, report, seal, provenance, trace, trace_assessment = _artifacts()

    assessment = assess_report_seal_consistency(manifest, report, seal, provenance, trace, trace_assessment)

    assert assessment.status == ReportSealConsistencyStatus.CONSISTENT
    assert assessment.execution_permitted is False
    assert {"report_id", "report_digest", "source_trace_id", "sealer_reference", "report_trace_reference"} <= assessment.matched_fields


def test_report_seal_consistency_rejects_mismatched_declared_digest():
    manifest, report, seal, provenance, trace, trace_assessment = _artifacts()
    seal = seal.model_copy(update={"report_digest": "sha256:tampered-report"})

    assessment = assess_report_seal_consistency(manifest, report, seal, provenance, trace, trace_assessment)

    assert assessment.status == ReportSealConsistencyStatus.INVALID
    assert any(issue.code == "report_seal_report_digest_mismatch" for issue in assessment.issues)


def test_report_seal_consistency_requires_report_trace_reference():
    manifest, report, seal, provenance, trace, trace_assessment = _artifacts()
    section = report.sections[0].model_copy(update={"artifact_references": []})
    report = report.model_copy(update={"sections": [section]})

    assessment = assess_report_seal_consistency(manifest, report, seal, provenance, trace, trace_assessment)

    assert assessment.status == ReportSealConsistencyStatus.INVALID
    assert any(issue.code == "report_seal_trace_reference_missing" for issue in assessment.issues)


def test_report_seal_consistency_cli_reports_a_reference_only_assessment():
    files = [
        "report.json",
        "report-seal.json",
        "provenance-assessment.json",
        "review-trace.json",
        "trace-assessment.json",
        "manifest.json",
    ]
    outcome = CliRunner().invoke(app, ["report-seal-consistency-assess", *(str(EXAMPLE / file) for file in files)])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "consistent"
    assert payload["execution_permitted"] is False
