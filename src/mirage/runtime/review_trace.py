"""Policy-bound provenance traces for non-executing workflow review artifacts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .context_review import ContextBundleStatus, WorkflowContextAssessment
from .execution import ExecutionPolicy
from .goal_workflow import GoalToEvaluateWorkflow
from .workflow_evidence import (
    WorkflowEvidenceAssessment,
    WorkflowEvidenceStatus,
    WorkflowValidationIssue,
)


class ReviewTraceEventType(StrEnum):
    CONTEXT_BOUND = "context_bound"
    PLAN_VALIDATED = "plan_validated"
    EVIDENCE_ASSESSED = "evidence_assessed"
    HUMAN_REVIEW_REQUESTED = "human_review_requested"


class ReviewTraceEvent(BaseModel):
    event_id: str = Field(min_length=1)
    event_type: ReviewTraceEventType
    artifact_reference: str = Field(min_length=1)
    artifact_digest: str = Field(min_length=8)
    observations: dict[str, str] = Field(default_factory=dict)


class WorkflowReviewTrace(BaseModel):
    trace_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    context_bundle_id: str = Field(min_length=1)
    policy_provenance: dict[str, object] = Field(default_factory=dict)
    events: list[ReviewTraceEvent] = Field(min_length=4, max_length=16)

    @model_validator(mode="after")
    def require_unique_complete_trace(self) -> WorkflowReviewTrace:
        event_ids = [event.event_id for event in self.events]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("review trace event identifiers must be unique")
        event_types = {event.event_type for event in self.events}
        required = set(ReviewTraceEventType)
        missing = required - event_types
        if missing:
            raise ValueError(f"review trace is missing events: {', '.join(sorted(item.value for item in missing))}")
        return self


class ReviewTraceAssessment(BaseModel):
    trace_id: str
    workflow_id: str
    status: ContextBundleStatus
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    human_review_required: bool = True
    execution_permitted: bool = False


def assess_review_trace(
    trace: WorkflowReviewTrace,
    workflow: GoalToEvaluateWorkflow,
    context: WorkflowContextAssessment,
    evidence: WorkflowEvidenceAssessment,
    policy: ExecutionPolicy,
) -> ReviewTraceAssessment:
    """Check provenance and review trace completeness without changing workflow state."""

    issues: list[WorkflowValidationIssue] = []
    if trace.workflow_id != workflow.workflow_id:
        issues.append(WorkflowValidationIssue(code="trace_workflow_mismatch", message="review trace workflow identifier does not match"))
    if trace.context_bundle_id != context.context_bundle_id:
        issues.append(WorkflowValidationIssue(code="trace_context_mismatch", message="review trace context bundle identifier does not match"))
    active_provenance = policy.provenance.model_dump(mode="json")
    if trace.policy_provenance and trace.policy_provenance != active_provenance:
        issues.append(WorkflowValidationIssue(code="trace_policy_provenance_mismatch", message="review trace policy provenance differs from active policy"))
    if context.status != ContextBundleStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="context_not_ready", message="workflow context is not ready for review"))
    if evidence.status != WorkflowEvidenceStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="evidence_not_ready", message="workflow evidence is not ready for review"))
    return ReviewTraceAssessment(
        trace_id=trace.trace_id,
        workflow_id=workflow.workflow_id,
        status=ContextBundleStatus.INVALID if issues else ContextBundleStatus.READY_FOR_REVIEW,
        issues=issues,
    )
