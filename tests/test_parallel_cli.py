import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app

EXAMPLE = Path(__file__).parents[1] / "examples/08-parallel-foundations"


def test_transport_assess_cli_reads_fixture_evidence_without_connection():
    outcome = CliRunner().invoke(
        app,
        ["transport-assess", str(EXAMPLE / "transport-manifest.json"), str(EXAMPLE / "transport-evidence.json")],
    )

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["valid"] is True
    assert payload["status"] == "fixture_verified"


def test_goal_workflow_review_cli_returns_a_review_only_checkpoint():
    outcome = CliRunner().invoke(app, ["goal-workflow-review", str(EXAMPLE / "goal-workflow.json"), "--backend", "fixture"])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "ready_for_review"
    assert payload["execution_permitted"] is False
    assert payload["checkpoint"]["stage"] == "awaiting-human-review"
