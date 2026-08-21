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
PERSISTENCE = ROOT / "examples/12-governance-foundations/persistence.json"
REVOCATION = ROOT / "examples/12-governance-foundations/revocation.json"
SEALS = ROOT / "examples/12-governance-foundations/evidence-seals.json"
TRANSITION = ROOT / "examples/12-governance-foundations/lifecycle-transition.json"


def test_governance_cli_reports_readiness_without_execution_permission():
    runner = CliRunner()
    persistence = runner.invoke(app, ["approval-persistence-assess", str(WORKFLOW), str(EIR), str(CONTEXT), str(EVIDENCE), str(TRACE), str(APPROVAL), str(PERSISTENCE)])
    revocation = runner.invoke(app, ["approval-revocation-assess", str(WORKFLOW), str(EIR), str(CONTEXT), str(EVIDENCE), str(TRACE), str(APPROVAL), str(REVOCATION)])
    provenance = runner.invoke(app, ["evidence-provenance-assess", str(WORKFLOW), str(EIR), str(EVIDENCE), str(SEALS)])
    lifecycle = runner.invoke(app, ["lifecycle-transition-assess", str(WORKFLOW), str(EIR), str(CONTEXT), str(EVIDENCE), str(TRACE), str(APPROVAL), str(SEALS), str(TRANSITION)])

    for outcome, status in ((persistence, "ready_for_integration"), (revocation, "declared"), (provenance, "ready_for_review"), (lifecycle, "valid")):
        assert outcome.exit_code == 0, outcome.output
        payload = json.loads(outcome.output)
        assert payload["status"] == status
        assert payload["execution_permitted"] is False
