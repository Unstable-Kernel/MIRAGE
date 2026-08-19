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
APPROVAL = ROOT / "examples/11-guarded-approval/approval-chain.json"
MANIFEST = ROOT / "examples/08-parallel-foundations/transport-manifest.json"
TRANSPORT_EVIDENCE = ROOT / "examples/08-parallel-foundations/transport-evidence.json"
SANDBOX = ROOT / "examples/11-guarded-approval/sandbox-assessment.json"


def test_approval_chain_cli_returns_review_ready_without_execution_permission():
    outcome = CliRunner().invoke(app, ["approval-chain-assess", str(WORKFLOW), str(EIR), str(CONTEXT), str(EVIDENCE), str(TRACE), str(APPROVAL)])

    assert outcome.exit_code == 0, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "review_ready"
    assert payload["execution_permitted"] is False


def test_dispatch_eligibility_cli_reports_ineligible_even_after_local_approval():
    outcome = CliRunner().invoke(
        app,
        [
            "dispatch-eligibility-assess",
            str(WORKFLOW),
            str(EIR),
            str(CONTEXT),
            str(EVIDENCE),
            str(TRACE),
            str(APPROVAL),
            str(MANIFEST),
            str(TRANSPORT_EVIDENCE),
            str(SANDBOX),
            "--allow-simulation",
        ],
    )

    assert outcome.exit_code == 1, outcome.output
    payload = json.loads(outcome.output)
    assert payload["status"] == "ineligible"
    assert payload["execution_permitted"] is False
