"""Audited, non-mutating human approval records for workflow review artifacts."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .execution import ExecutionPolicy
from .review_trace import ReviewTraceAssessment
from .workflow_evidence import WorkflowValidationIssue


class ApprovalDecision(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalChainStatus(StrEnum):
    REVIEW_READY = "review_ready"
    REJECTED = "rejected"
    INVALID = "invalid"


class HumanApprovalRecord(BaseModel):
    """An immutable-looking approval declaration supplied by a human workflow."""

    approval_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    trace_id: str = Field(min_length=1)
    approver_id: str = Field(min_length=1)
    decision: ApprovalDecision
    policy_provenance: dict[str, object] = Field(default_factory=dict)
    approval_digest: str = Field(min_length=8)
    previous_approval_digest: str | None = None
    recorded_at: datetime
    observations: dict[str, str] = Field(default_factory=dict)


class ApprovalChain(BaseModel):
    chain_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    trace_id: str = Field(min_length=1)
    policy_provenance: dict[str, object] = Field(default_factory=dict)
    approvals: list[HumanApprovalRecord] = Field(min_length=1, max_length=16)

    @model_validator(mode="after")
    def require_unique_linked_approvals(self) -> ApprovalChain:
        approval_ids = [approval.approval_id for approval in self.approvals]
        if len(approval_ids) != len(set(approval_ids)):
            raise ValueError("approval identifiers must be unique")
        previous_digest: str | None = None
        for approval in self.approvals:
            if approval.workflow_id != self.workflow_id or approval.trace_id != self.trace_id:
                raise ValueError("approval record does not match the approval chain workflow and trace")
            if approval.previous_approval_digest != previous_digest:
                raise ValueError("approval chain digest linkage is invalid")
            previous_digest = approval.approval_digest
        return self


class ApprovalChainAssessment(BaseModel):
    chain_id: str
    workflow_id: str
    trace_id: str
    status: ApprovalChainStatus
    latest_approval_id: str | None = None
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_approval_chain(
    chain: ApprovalChain,
    trace: ReviewTraceAssessment,
    policy: ExecutionPolicy,
) -> ApprovalChainAssessment:
    """Assess a declared approval chain without granting authority or executing work."""

    issues: list[WorkflowValidationIssue] = []
    if chain.workflow_id != trace.workflow_id:
        issues.append(WorkflowValidationIssue(code="approval_workflow_mismatch", message="approval chain workflow identifier does not match trace"))
    if chain.trace_id != trace.trace_id:
        issues.append(WorkflowValidationIssue(code="approval_trace_mismatch", message="approval chain trace identifier does not match"))
    active_provenance = policy.provenance.model_dump(mode="json")
    if chain.policy_provenance and chain.policy_provenance != active_provenance:
        issues.append(WorkflowValidationIssue(code="approval_policy_provenance_mismatch", message="approval chain policy provenance differs from active policy"))
    if trace.status.value != "ready_for_review":
        issues.append(WorkflowValidationIssue(code="trace_not_ready", message="review trace is not ready for approval assessment"))
    latest = chain.approvals[-1]
    if latest.decision == ApprovalDecision.REJECTED:
        return ApprovalChainAssessment(
            chain_id=chain.chain_id,
            workflow_id=chain.workflow_id,
            trace_id=chain.trace_id,
            status=ApprovalChainStatus.REJECTED,
            latest_approval_id=latest.approval_id,
            issues=issues,
        )
    return ApprovalChainAssessment(
        chain_id=chain.chain_id,
        workflow_id=chain.workflow_id,
        trace_id=chain.trace_id,
        status=ApprovalChainStatus.INVALID if issues else ApprovalChainStatus.REVIEW_READY,
        latest_approval_id=latest.approval_id,
        issues=issues,
    )
