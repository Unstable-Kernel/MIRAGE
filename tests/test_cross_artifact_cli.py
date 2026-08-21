import json
from pathlib import Path

from typer.testing import CliRunner

from mirage.cli import app

ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / "examples/09-deterministic-workflow/workflow.json"
EIR = ROOT / "examples/01-validate-eir/robot_model.yaml"
CONTEXT = ROOT / "examples/10-context-review/context.json"
EVIDENCE = ROOT / "examples/09-deterministic-workflow/evidence.json"
TRACE = ROOT / "examples/10-context-review/review-trace.json"
APPROVAL = ROOT / "examples/11-guarded-approval/approval-chain.json"
SCHEMA = ROOT / "examples/13-controlled-report/context-schema.json"
ENVELOPE = ROOT / "examples/13-controlled-report/context-envelope.json"
SEALS = ROOT / "examples/12-governance-foundations/evidence-seals.json"
REPORT = ROOT / "examples/13-controlled-report/report.json"
REPORT_SEAL = ROOT / "examples/13-controlled-report/report-seal.json"
POLICY = ROOT / "examples/14-cross-artifact-readiness/review-policy.json"
TRANSPORT_MANIFEST = ROOT / "examples/08-parallel-foundations/transport-manifest.json"
TRANSPORT_EVIDENCE = ROOT / "examples/08-parallel-foundations/transport-evidence.json"
SANDBOX = ROOT / "examples/11-guarded-approval/sandbox-assessment.json"


def test_cross_artifact_cli_reports_consistency_and_external_prerequisite_readiness():
    runner = CliRunner()
    shared = [str(WORKFLOW), str(EIR), str(CONTEXT), str(EVIDENCE), str(TRACE), str(APPROVAL), str(SCHEMA), str(ENVELOPE), str(SEALS), str(REPORT), str(REPORT_SEAL)]
    cross = runner.invoke(app, ["cross-artifact-assess", *shared])
    review_policy = runner.invoke(app, ["review-policy-assess", *shared, str(POLICY)])
    readiness = runner.invoke(app, ["workflow-readiness-assess", *shared, str(POLICY), str(TRANSPORT_MANIFEST), str(TRANSPORT_EVIDENCE), str(SANDBOX)])

    assert cross.exit_code == 0, cross.output
    assert review_policy.exit_code == 0, review_policy.output
    assert readiness.exit_code == 0, readiness.output
    assert json.loads(cross.output)["status"] == "consistent"
    assert json.loads(review_policy.output)["status"] == "ready_for_review"
    readiness_payload = json.loads(readiness.output)
    assert readiness_payload["status"] == "ready_for_external_prerequisites"
    assert readiness_payload["execution_permitted"] is False
