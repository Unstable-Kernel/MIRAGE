import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app

ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / "examples/09-deterministic-workflow/workflow.json"
EIR = ROOT / "examples/01-validate-eir/robot_model.yaml"
EVIDENCE = ROOT / "examples/09-deterministic-workflow/evidence.json"
CONTEXT = ROOT / "examples/10-context-review/context.json"
TRACE = ROOT / "examples/10-context-review/review-trace.json"


def test_context_inspection_cli_returns_a_review_only_assessment():
    outcome = CliRunner().invoke(app, ["workflow-context-inspect", str(WORKFLOW), str(EIR), str(CONTEXT)])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "ready_for_review"
    assert payload["execution_permitted"] is False


def test_review_trace_cli_returns_complete_review_trace_assessment():
    outcome = CliRunner().invoke(app, ["review-trace-assess", str(WORKFLOW), str(EIR), str(CONTEXT), str(EVIDENCE), str(TRACE)])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "ready_for_review"
    assert payload["execution_permitted"] is False
