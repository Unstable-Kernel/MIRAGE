import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app

EXAMPLE = Path(__file__).parents[1] / "examples/09-deterministic-workflow"
EIR = Path(__file__).parents[1] / "examples/01-validate-eir/robot_model.yaml"


def test_goal_workflow_plan_cli_returns_eir_bound_review_plan():
    outcome = CliRunner().invoke(app, ["goal-workflow-plan", str(EXAMPLE / "workflow.json"), str(EIR)])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "ready_for_review"
    assert payload["execution_permitted"] is False


def test_goal_workflow_evidence_cli_returns_review_only_evidence_assessment():
    outcome = CliRunner().invoke(
        app,
        ["goal-workflow-evidence", str(EXAMPLE / "workflow.json"), str(EIR), str(EXAMPLE / "evidence.json")],
    )

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "ready_for_review"
    assert payload["execution_permitted"] is False
