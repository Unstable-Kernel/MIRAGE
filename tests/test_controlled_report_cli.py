import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app

ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / "examples/09-deterministic-workflow/workflow.json"
EIR = ROOT / "examples/01-validate-eir/robot_model.yaml"
CONTEXT = ROOT / "examples/10-context-review/context.json"
EVIDENCE = ROOT / "examples/09-deterministic-workflow/evidence.json"
SCHEMA = ROOT / "examples/13-controlled-report/context-schema.json"
ENVELOPE = ROOT / "examples/13-controlled-report/context-envelope.json"
SEALS = ROOT / "examples/12-governance-foundations/evidence-seals.json"
REPORT = ROOT / "examples/13-controlled-report/report.json"
REPORT_SEAL = ROOT / "examples/13-controlled-report/report-seal.json"
TRANSITION = ROOT / "examples/13-controlled-report/report-transition.json"


def test_controlled_report_cli_remains_reference_only_and_non_executing():
    runner = CliRunner()
    context = runner.invoke(app, ["controlled-context-assess", str(WORKFLOW), str(EIR), str(CONTEXT), str(SCHEMA), str(ENVELOPE)])
    report = runner.invoke(app, ["deterministic-report-assess", str(WORKFLOW), str(EIR), str(CONTEXT), str(EVIDENCE), str(SCHEMA), str(ENVELOPE), str(SEALS), str(REPORT)])
    provenance = runner.invoke(app, ["report-provenance-assess", str(WORKFLOW), str(EIR), str(CONTEXT), str(EVIDENCE), str(SCHEMA), str(ENVELOPE), str(SEALS), str(REPORT), str(REPORT_SEAL)])
    lifecycle = runner.invoke(app, ["report-lifecycle-assess", str(WORKFLOW), str(EIR), str(CONTEXT), str(EVIDENCE), str(SCHEMA), str(ENVELOPE), str(SEALS), str(REPORT), str(REPORT_SEAL), str(TRANSITION)])

    for outcome in (context, report, provenance, lifecycle):
        assert outcome.exit_code == 0, outcome.output
        assert json.loads(outcome.output)["execution_permitted"] is False
