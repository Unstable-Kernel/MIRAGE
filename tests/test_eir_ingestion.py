import hashlib
import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app
from mirage.eir import (
    EIRIngestionStatus,
    EIRSourceFormat,
    ingest_eir_file,
)

ROOT = Path(__file__).parents[1]
YAML_FIXTURE = ROOT / "examples/01-validate-eir/robot_model.yaml"
JSON_FIXTURE = ROOT / "examples/16-eir-ingestion/robot_model.json"


def test_json_ingestion_returns_a_validated_document_and_local_source_digest():
    result = ingest_eir_file(JSON_FIXTURE)

    assert result.status == EIRIngestionStatus.ACCEPTED
    assert result.document is not None
    assert result.document.id == "quadrotor-inspection"
    assert result.document.provenance.source_path == "examples/16-eir-ingestion/robot_model.json"
    assert result.source is not None
    assert result.source.format == EIRSourceFormat.JSON
    assert result.source.sha256 == hashlib.sha256(JSON_FIXTURE.read_bytes()).hexdigest()


def test_yaml_ingestion_preserves_candidate_provenance_without_overwriting_it():
    result = ingest_eir_file(YAML_FIXTURE)

    assert result.accepted
    assert result.document is not None
    assert result.document.provenance.source_type == "manual"
    assert result.document.provenance.source_path == "examples/01-validate-eir/robot_model.yaml"
    assert result.source is not None
    assert result.source.format == EIRSourceFormat.YAML


def test_ingestion_rejects_unsupported_formats_before_reading_source(tmp_path):
    source = tmp_path / "candidate.txt"
    source.write_text("not an EIR source", encoding="utf-8")

    result = ingest_eir_file(source)

    assert result.status == EIRIngestionStatus.REJECTED
    assert result.diagnostics[0].code == "UNSUPPORTED_SOURCE_FORMAT"


def test_ingestion_rejects_invalid_json_and_non_mapping_roots(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{", encoding="utf-8")
    scalar = tmp_path / "scalar.yaml"
    scalar.write_text("- one\n- two\n", encoding="utf-8")

    assert ingest_eir_file(invalid).diagnostics[0].code == "SOURCE_PARSE_FAILED"
    assert ingest_eir_file(scalar).diagnostics[0].code == "SOURCE_NOT_MAPPING"


def test_ingestion_reuses_canonical_validation_diagnostics(tmp_path):
    payload = json.loads(JSON_FIXTURE.read_text(encoding="utf-8"))
    payload["relationships"][0]["target_id"] = "missing"
    invalid = tmp_path / "invalid-eir.json"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    result = ingest_eir_file(invalid)

    assert result.status == EIRIngestionStatus.REJECTED
    assert result.diagnostics[0].code == "RELATIONSHIP_ENDPOINT_MISSING"


def test_ingestion_can_require_a_local_allowed_root(tmp_path):
    source = tmp_path / "candidate.json"
    source.write_bytes(JSON_FIXTURE.read_bytes())
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()

    result = ingest_eir_file(source, allowed_root=allowed_root)

    assert result.status == EIRIngestionStatus.REJECTED
    assert result.diagnostics[0].code == "SOURCE_OUTSIDE_ALLOWED_ROOT"


def test_eir_ingest_cli_reports_a_non_executing_local_assessment():
    outcome = CliRunner().invoke(app, ["eir-ingest", str(JSON_FIXTURE)])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "accepted"
    assert payload["source"]["format"] == "json"
    assert payload["document"]["id"] == "quadrotor-inspection"
