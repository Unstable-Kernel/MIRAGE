from pathlib import Path

from mirage.eir import load_data, validate_document
from mirage.runtime import (
    EvaluationEvidence,
    EvaluationEvidenceClass,
    GoalToEvaluateWorkflow,
    WorkflowEvidenceStatus,
    WorkflowPlanStatus,
    assess_evaluation_evidence,
    build_deterministic_plan,
)

EXAMPLE = Path(__file__).parents[1] / "examples/09-deterministic-workflow"


def workflow() -> GoalToEvaluateWorkflow:
    return GoalToEvaluateWorkflow.model_validate_json((EXAMPLE / "workflow.json").read_text(encoding="utf-8"))


def document():
    result = validate_document(load_data(Path(__file__).parents[1] / "examples/01-validate-eir/robot_model.yaml"))
    assert result.ok
    assert result.document is not None
    return result.document


def test_deterministic_plan_binds_every_workflow_step_to_known_eir_nodes():
    plan = build_deterministic_plan(workflow(), document())

    assert plan.status == WorkflowPlanStatus.READY_FOR_REVIEW
    assert plan.source_node_ids == {"robot.quadrotor", "objective.inspect"}
    assert plan.execution_permitted is False


def test_deterministic_plan_rejects_document_mismatch_and_unknown_node():
    invalid_workflow = workflow().model_copy(deep=True)
    invalid_workflow.eir_document_id = "wrong-document"
    invalid_workflow.steps[0].source_node_ids = {"missing-node"}

    plan = build_deterministic_plan(invalid_workflow, document())

    assert plan.status == WorkflowPlanStatus.INVALID
    assert {issue.code for issue in plan.issues} == {"eir_document_mismatch", "workflow_source_node_missing"}


def test_evidence_assessment_requires_all_criteria_and_known_plan_sources():
    active_workflow = workflow()
    plan = build_deterministic_plan(active_workflow, document())
    evidence = [
        EvaluationEvidence(
            evidence_id="evidence-robot",
            criterion_id="robot-identified",
            evidence_class=EvaluationEvidenceClass.DETERMINISTIC_VALIDATION,
            source_node_ids={"robot.quadrotor"},
            source_reference="EIR:robot.quadrotor",
        ),
        EvaluationEvidence(
            evidence_id="evidence-objective",
            criterion_id="objective-identified",
            evidence_class=EvaluationEvidenceClass.DETERMINISTIC_VALIDATION,
            source_node_ids={"objective.inspect"},
            source_reference="EIR:objective.inspect",
        ),
    ]

    assessment = assess_evaluation_evidence(active_workflow, plan, evidence)

    assert assessment.status == WorkflowEvidenceStatus.READY_FOR_REVIEW
    assert assessment.execution_permitted is False


def test_evidence_assessment_rejects_unknown_plan_sources():
    active_workflow = workflow()
    plan = build_deterministic_plan(active_workflow, document())
    evidence = [
        EvaluationEvidence(
            evidence_id="evidence-invalid",
            criterion_id="robot-identified",
            evidence_class=EvaluationEvidenceClass.READ_ONLY_SNAPSHOT,
            source_node_ids={"outside-plan"},
            source_reference="fixture:outside-plan",
        )
    ]

    assessment = assess_evaluation_evidence(active_workflow, plan, evidence)

    assert assessment.status == WorkflowEvidenceStatus.INVALID
    assert assessment.issues[0].code == "evidence_source_out_of_plan"
