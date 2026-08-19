from mirage.runtime import (
    ContextBundleStatus,
    ExecutionPolicy,
    GoalToEvaluateWorkflow,
    ReviewTraceEvent,
    ReviewTraceEventType,
    WorkflowContextAssessment,
    WorkflowEvidenceAssessment,
    WorkflowEvidenceStatus,
    WorkflowReviewTrace,
    assess_review_trace,
)
from mirage.runtime.workflow_evidence import WorkflowPlanStatus


def workflow() -> GoalToEvaluateWorkflow:
    return GoalToEvaluateWorkflow.model_validate(
        {
            "workflow_id": "trace-workflow-1",
            "goal": "Review trace completeness.",
            "eir_document_id": "trace-eir",
            "steps": [
                {
                    "step_id": "inspect",
                    "summary": "Inspect a node.",
                    "capability": {"capability_id": "inspect_model", "version": "0.1", "backend": "generic"},
                    "source_node_ids": ["robot.trace"],
                    "expected_evidence": ["node reference"],
                }
            ],
            "evaluation_criteria": [{"criterion_id": "present", "description": "Node is present."}],
        }
    )


def trace(policy: ExecutionPolicy) -> WorkflowReviewTrace:
    return WorkflowReviewTrace(
        trace_id="trace-v1",
        workflow_id="trace-workflow-1",
        context_bundle_id="context-v1",
        policy_provenance=policy.provenance.model_dump(mode="json"),
        events=[
            ReviewTraceEvent(event_id="context", event_type=ReviewTraceEventType.CONTEXT_BOUND, artifact_reference="context:v1", artifact_digest="sha256:context-v1"),
            ReviewTraceEvent(event_id="plan", event_type=ReviewTraceEventType.PLAN_VALIDATED, artifact_reference="plan:v1", artifact_digest="sha256:plan-v1"),
            ReviewTraceEvent(event_id="evidence", event_type=ReviewTraceEventType.EVIDENCE_ASSESSED, artifact_reference="evidence:v1", artifact_digest="sha256:evidence-v1"),
            ReviewTraceEvent(event_id="review", event_type=ReviewTraceEventType.HUMAN_REVIEW_REQUESTED, artifact_reference="review:v1", artifact_digest="sha256:review-v1"),
        ],
    )


def test_complete_review_trace_is_ready_without_execution():
    policy = ExecutionPolicy()
    context = WorkflowContextAssessment(workflow_id="trace-workflow-1", context_bundle_id="context-v1", status=ContextBundleStatus.READY_FOR_REVIEW)
    evidence = WorkflowEvidenceAssessment(workflow_id="trace-workflow-1", plan_status=WorkflowPlanStatus.READY_FOR_REVIEW, status=WorkflowEvidenceStatus.READY_FOR_REVIEW)

    assessment = assess_review_trace(trace(policy), workflow(), context, evidence, policy)

    assert assessment.status == ContextBundleStatus.READY_FOR_REVIEW
    assert assessment.execution_permitted is False
    assert assessment.human_review_required is True


def test_review_trace_rejects_policy_provenance_drift():
    policy = ExecutionPolicy()
    invalid_trace = trace(policy).model_copy(deep=True)
    invalid_trace.policy_provenance["revision"] = "unexpected"
    context = WorkflowContextAssessment(workflow_id="trace-workflow-1", context_bundle_id="context-v1", status=ContextBundleStatus.READY_FOR_REVIEW)
    evidence = WorkflowEvidenceAssessment(workflow_id="trace-workflow-1", plan_status=WorkflowPlanStatus.READY_FOR_REVIEW, status=WorkflowEvidenceStatus.READY_FOR_REVIEW)

    assessment = assess_review_trace(invalid_trace, workflow(), context, evidence, policy)

    assert assessment.status == ContextBundleStatus.INVALID
    assert assessment.issues[0].code == "trace_policy_provenance_mismatch"
