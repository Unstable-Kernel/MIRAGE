from mirage.eir import EIRDocument, EIRNode, NodeType, Provenance
from mirage.runtime import (
    ContextBundleStatus,
    ContextItemKind,
    ExecutionPolicy,
    GoalToEvaluateWorkflow,
    WorkflowContextBundle,
    WorkflowContextItem,
    assess_workflow_context,
    build_deterministic_plan,
)


def workflow() -> GoalToEvaluateWorkflow:
    return GoalToEvaluateWorkflow.model_validate(
        {
            "workflow_id": "context-review-1",
            "goal": "Review a valid EIR node.",
            "eir_document_id": "context-eir",
            "steps": [
                {
                    "step_id": "inspect",
                    "summary": "Inspect a node.",
                    "capability": {"capability_id": "inspect_model", "version": "0.1", "backend": "generic"},
                    "source_node_ids": ["robot.context"],
                    "expected_evidence": ["node reference"],
                }
            ],
            "evaluation_criteria": [{"criterion_id": "node-present", "description": "Node is present."}],
        }
    )


def document() -> EIRDocument:
    return EIRDocument(
        id="context-eir",
        provenance=Provenance(source_type="test"),
        nodes=[EIRNode(id="robot.context", type=NodeType.ROBOT, provenance=Provenance(source_type="test"))],
    )


def test_context_bundle_is_ready_when_policy_and_plan_sources_match():
    active_workflow = workflow()
    policy = ExecutionPolicy()
    plan = build_deterministic_plan(active_workflow, document())
    bundle = WorkflowContextBundle(
        context_bundle_id="context-v1",
        workflow_id=active_workflow.workflow_id,
        eir_document_id="context-eir",
        policy_provenance=policy.provenance.model_dump(mode="json"),
        items=[
            WorkflowContextItem(
                context_item_id="node-context",
                kind=ContextItemKind.EIR_NODE,
                reference="EIR:robot.context",
                content_digest="sha256:robot-context",
                source_node_ids={"robot.context"},
            )
        ],
    )

    assessment = assess_workflow_context(bundle, active_workflow, plan, policy)

    assert assessment.status == ContextBundleStatus.READY_FOR_REVIEW
    assert assessment.execution_permitted is False


def test_context_bundle_rejects_sources_outside_the_plan():
    active_workflow = workflow()
    policy = ExecutionPolicy()
    plan = build_deterministic_plan(active_workflow, document())
    bundle = WorkflowContextBundle(
        context_bundle_id="context-invalid",
        workflow_id=active_workflow.workflow_id,
        eir_document_id="context-eir",
        items=[
            WorkflowContextItem(
                context_item_id="outside-context",
                kind=ContextItemKind.EIR_NODE,
                reference="EIR:outside",
                content_digest="sha256:outside-context",
                source_node_ids={"outside"},
            )
        ],
    )

    assessment = assess_workflow_context(bundle, active_workflow, plan, policy)

    assert assessment.status == ContextBundleStatus.INVALID
    assert assessment.issues[0].code == "context_source_out_of_plan"
