import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app
from mirage.eir import ingest_eir_file
from mirage.runtime import (
    DeterministicReportAssessment,
    DeterministicReviewReport,
    EvidenceProvenanceAssessment,
    EvidenceProvenanceSeal,
    ProvenanceConsistencyManifest,
    ProvenanceConsistencyStatus,
    assess_provenance_consistency,
)

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples/17-provenance-consistency"
EIR = ROOT / "examples/16-eir-ingestion/robot_model.json"


def _artifacts():
    ingestion = ingest_eir_file(EIR)
    assert ingestion.accepted
    assert ingestion.source is not None
    assert ingestion.document is not None
    manifest = ProvenanceConsistencyManifest.model_validate_json((EXAMPLE / "manifest.json").read_text(encoding="utf-8"))
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in json.loads((EXAMPLE / "evidence-seals.json").read_text(encoding="utf-8"))]
    evidence = EvidenceProvenanceAssessment.model_validate_json((EXAMPLE / "evidence-provenance.json").read_text(encoding="utf-8"))
    report = DeterministicReviewReport.model_validate_json((EXAMPLE / "report.json").read_text(encoding="utf-8"))
    report_assessment = DeterministicReportAssessment.model_validate_json((EXAMPLE / "report-assessment.json").read_text(encoding="utf-8"))
    return ingestion, manifest, seals, evidence, report, report_assessment


def test_provenance_consistency_accepts_aligned_local_references_and_digests():
    ingestion, manifest, seals, evidence, report, report_assessment = _artifacts()

    assessment = assess_provenance_consistency(manifest, ingestion.source, ingestion.document, seals, evidence, report, report_assessment)

    assert assessment.status == ProvenanceConsistencyStatus.CONSISTENT
    assert assessment.execution_permitted is False
    assert assessment.verified_evidence_ids == {"eir-robot-validation", "eir-objective-validation"}


def test_provenance_consistency_rejects_an_eir_source_digest_mismatch():
    ingestion, manifest, seals, evidence, report, report_assessment = _artifacts()
    manifest = manifest.model_copy(update={"eir_source_digest": "sha256:incorrect-eir-source"})

    assessment = assess_provenance_consistency(manifest, ingestion.source, ingestion.document, seals, evidence, report, report_assessment)

    assert assessment.status == ProvenanceConsistencyStatus.INVALID
    assert any(issue.code == "provenance_eir_digest_mismatch" for issue in assessment.issues)


def test_provenance_consistency_rejects_a_missing_report_digest_binding():
    ingestion, manifest, seals, evidence, report, report_assessment = _artifacts()
    section = report.sections[0].model_copy(update={"provenance_references": []})
    report = report.model_copy(update={"sections": [section]})

    assessment = assess_provenance_consistency(manifest, ingestion.source, ingestion.document, seals, evidence, report, report_assessment)

    assert assessment.status == ProvenanceConsistencyStatus.INVALID
    assert any(issue.code == "provenance_report_reference_missing" for issue in assessment.issues)


def test_provenance_consistency_cli_reports_a_reference_only_assessment():
    outcome = CliRunner().invoke(
        app,
        [
            "provenance-consistency-assess",
            str(EIR),
            str(EXAMPLE / "manifest.json"),
            str(EXAMPLE / "evidence-seals.json"),
            str(EXAMPLE / "report.json"),
            str(EXAMPLE / "evidence-provenance.json"),
            str(EXAMPLE / "report-assessment.json"),
        ],
    )

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["assessment"]["status"] == "consistent"
    assert payload["assessment"]["execution_permitted"] is False
