"""Non-mutating report lifecycle transition validation."""

from enum import StrEnum

from pydantic import BaseModel, Field

from .report_provenance import ReportProvenanceAssessment, ReportProvenanceStatus
from .workflow_evidence import WorkflowValidationIssue


class ReportLifecycleState(StrEnum):
    DRAFT = "draft"
    READY_FOR_REVIEW = "ready_for_review"
    SEALED_FOR_REVIEW = "sealed_for_review"


class ReportLifecycleTransition(BaseModel):
    transition_id: str = Field(min_length=1)
    report_id: str = Field(min_length=1)
    from_state: ReportLifecycleState
    to_state: ReportLifecycleState
    transition_digest: str = Field(min_length=8)


class ReportLifecycleAssessment(BaseModel):
    transition_id: str
    report_id: str
    valid: bool
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_report_lifecycle_transition(
    transition: ReportLifecycleTransition,
    provenance: ReportProvenanceAssessment,
) -> ReportLifecycleAssessment:
    """Check report lifecycle order without saving a transition or authorizing a report."""

    issues: list[WorkflowValidationIssue] = []
    allowed = {
        ReportLifecycleState.DRAFT: ReportLifecycleState.READY_FOR_REVIEW,
        ReportLifecycleState.READY_FOR_REVIEW: ReportLifecycleState.SEALED_FOR_REVIEW,
    }
    if allowed.get(transition.from_state) != transition.to_state:
        issues.append(WorkflowValidationIssue(code="report_lifecycle_transition_invalid", message="requested report lifecycle transition is not permitted"))
    if transition.report_id != provenance.report_id:
        issues.append(WorkflowValidationIssue(code="report_lifecycle_report_mismatch", message="report lifecycle transition does not match provenance"))
    if transition.to_state == ReportLifecycleState.SEALED_FOR_REVIEW and provenance.status != ReportProvenanceStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="report_lifecycle_provenance_not_ready", message="report provenance is not ready"))
    return ReportLifecycleAssessment(
        transition_id=transition.transition_id,
        report_id=transition.report_id,
        valid=not issues,
        issues=issues,
    )
