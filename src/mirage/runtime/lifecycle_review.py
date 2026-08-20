"""Non-mutating lifecycle transition validation for review artifacts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .approval_review import ApprovalChainAssessment, ApprovalChainStatus
from .evidence_provenance import EvidenceProvenanceAssessment, EvidenceProvenanceStatus
from .workflow_evidence import WorkflowValidationIssue


class WorkflowLifecycleState(StrEnum):
    DRAFT = "draft"
    REVIEW_READY = "review_ready"
    APPROVAL_REVIEWED = "approval_reviewed"
    ELIGIBILITY_ASSESSED = "eligibility_assessed"


class LifecycleTransitionStatus(StrEnum):
    VALID = "valid"
    INVALID = "invalid"


class WorkflowLifecycleTransition(BaseModel):
    transition_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    from_state: WorkflowLifecycleState
    to_state: WorkflowLifecycleState
    trace_id: str = Field(min_length=1)
    transition_digest: str = Field(min_length=8)


class LifecycleTransitionAssessment(BaseModel):
    transition_id: str
    workflow_id: str
    status: LifecycleTransitionStatus
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_lifecycle_transition(
    transition: WorkflowLifecycleTransition,
    approval: ApprovalChainAssessment,
    provenance: EvidenceProvenanceAssessment,
) -> LifecycleTransitionAssessment:
    """Validate a requested lifecycle step without mutating a workflow or granting execution."""

    issues: list[WorkflowValidationIssue] = []
    allowed = {
        WorkflowLifecycleState.DRAFT: WorkflowLifecycleState.REVIEW_READY,
        WorkflowLifecycleState.REVIEW_READY: WorkflowLifecycleState.APPROVAL_REVIEWED,
        WorkflowLifecycleState.APPROVAL_REVIEWED: WorkflowLifecycleState.ELIGIBILITY_ASSESSED,
    }
    if allowed.get(transition.from_state) != transition.to_state:
        issues.append(WorkflowValidationIssue(code="lifecycle_transition_invalid", message="requested lifecycle transition is not permitted"))
    if transition.workflow_id != approval.workflow_id or transition.workflow_id != provenance.workflow_id:
        issues.append(WorkflowValidationIssue(code="lifecycle_workflow_mismatch", message="lifecycle transition workflow identifier does not match review artifacts"))
    if transition.to_state == WorkflowLifecycleState.APPROVAL_REVIEWED and approval.status != ApprovalChainStatus.REVIEW_READY:
        issues.append(WorkflowValidationIssue(code="lifecycle_approval_not_ready", message="approval chain is not ready"))
    if transition.to_state == WorkflowLifecycleState.REVIEW_READY and provenance.status != EvidenceProvenanceStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="lifecycle_provenance_not_ready", message="evidence provenance is not ready"))
    return LifecycleTransitionAssessment(
        transition_id=transition.transition_id,
        workflow_id=transition.workflow_id,
        status=LifecycleTransitionStatus.INVALID if issues else LifecycleTransitionStatus.VALID,
        issues=issues,
    )
