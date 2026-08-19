from mirage.runtime import (
    CheckpointCapabilityRequirement,
    ExecutionPolicy,
    GoalEvaluationCriterion,
    GoalToEvaluateWorkflow,
    GoalWorkflowStatus,
    GoalWorkflowStep,
    PolicyProvenance,
    default_registry,
)


def make_workflow() -> GoalToEvaluateWorkflow:
    return GoalToEvaluateWorkflow(
        workflow_id="goal-review-1",
        goal="Inspect the deterministic simulator state without control.",
        eir_document_id="robot-arm-v1",
        steps=[
            GoalWorkflowStep(
                step_id="inspect-state",
                summary="Inspect a bounded simulator snapshot.",
                capability=CheckpointCapabilityRequirement(
                    capability_id="inspect_simulator_state",
                    version="0.1",
                    backend="fixture",
                ),
                expected_evidence=["state snapshot"],
            )
        ],
        evaluation_criteria=[
            GoalEvaluationCriterion(
                criterion_id="snapshot-present",
                description="A bounded state snapshot is available for review.",
            )
        ],
    )


def test_goal_workflow_creates_non_executing_review_checkpoint():
    policy = ExecutionPolicy(
        allow_read_only=True,
        allowed_backends={"fixture"},
        provenance=PolicyProvenance(policy_id="review-policy", revision="1"),
    )

    review = make_workflow().review(default_registry(), policy)

    assert review.status == GoalWorkflowStatus.READY_FOR_REVIEW
    assert review.human_approval_required is True
    assert review.execution_permitted is False
    assert review.checkpoint.stage == "awaiting-human-review"
    assert review.revalidation.valid is True


def test_goal_workflow_keeps_denied_capabilities_out_of_execution():
    policy = ExecutionPolicy(allow_read_only=False, allowed_backends={"fixture"})

    review = make_workflow().review(default_registry(), policy)

    assert review.status == GoalWorkflowStatus.REVALIDATION_FAILED
    assert review.execution_permitted is False
    assert {issue.code for issue in review.revalidation.issues} == {"capability_denied"}
