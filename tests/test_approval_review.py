from datetime import UTC, datetime

from mirage.runtime import (
    ApprovalChain,
    ApprovalChainStatus,
    ApprovalDecision,
    ContextBundleStatus,
    ExecutionPolicy,
    HumanApprovalRecord,
    ReviewTraceAssessment,
    assess_approval_chain,
)


def trace() -> ReviewTraceAssessment:
    return ReviewTraceAssessment(trace_id="trace-v1", workflow_id="workflow-v1", status=ContextBundleStatus.READY_FOR_REVIEW)


def record(policy: ExecutionPolicy, decision: ApprovalDecision = ApprovalDecision.APPROVED) -> HumanApprovalRecord:
    return HumanApprovalRecord(
        approval_id="approval-v1",
        workflow_id="workflow-v1",
        trace_id="trace-v1",
        approver_id="reviewer@example.invalid",
        decision=decision,
        policy_provenance=policy.provenance.model_dump(mode="json"),
        approval_digest="sha256:approval-v1",
        recorded_at=datetime(2026, 8, 19, tzinfo=UTC),
    )


def test_approved_chain_is_review_ready_but_never_execution_permitted():
    policy = ExecutionPolicy()
    chain = ApprovalChain(
        chain_id="chain-v1",
        workflow_id="workflow-v1",
        trace_id="trace-v1",
        policy_provenance=policy.provenance.model_dump(mode="json"),
        approvals=[record(policy)],
    )

    assessment = assess_approval_chain(chain, trace(), policy)

    assert assessment.status == ApprovalChainStatus.REVIEW_READY
    assert assessment.execution_permitted is False


def test_rejected_chain_stays_rejected_without_authority_side_effect():
    policy = ExecutionPolicy()
    chain = ApprovalChain(
        chain_id="chain-rejected",
        workflow_id="workflow-v1",
        trace_id="trace-v1",
        approvals=[record(policy, ApprovalDecision.REJECTED)],
    )

    assessment = assess_approval_chain(chain, trace(), policy)

    assert assessment.status == ApprovalChainStatus.REJECTED
    assert assessment.execution_permitted is False
