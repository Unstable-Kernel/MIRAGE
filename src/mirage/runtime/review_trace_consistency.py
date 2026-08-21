from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .context_review import ContextBundleStatus
from .review_trace import ReviewTraceAssessment, ReviewTraceEventType, WorkflowReviewTrace
from .workflow_evidence import WorkflowValidationIssue


class ReviewTraceEventConsistencyStatus(StrEnum):
    CONSISTENT = "consistent"
    INVALID = "invalid"


class ReviewTraceEventExpectation(BaseModel):
    event_type: ReviewTraceEventType
    artifact_reference: str = Field(min_length=1)
    artifact_digest: str = Field(min_length=8)


class ReviewTraceEventConsistencyManifest(BaseModel):
    manifest_id: str = Field(min_length=1)
    trace_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    context_bundle_id: str = Field(min_length=1)
    policy_provenance: dict[str, object]
    expected_events: list[ReviewTraceEventExpectation] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def require_exact_event_coverage(self) -> ReviewTraceEventConsistencyManifest:
        event_types = [expectation.event_type for expectation in self.expected_events]
        if len(event_types) != len(set(event_types)):
            raise ValueError("review trace event expectations must use unique event types")
        if set(event_types) != set(ReviewTraceEventType):
            raise ValueError("review trace event expectations must cover every event type")
        return self


class ReviewTraceEventConsistencyAssessment(BaseModel):
    manifest_id: str
    trace_id: str
    workflow_id: str
    status: ReviewTraceEventConsistencyStatus
    matched_event_types: set[ReviewTraceEventType] = Field(default_factory=set)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_review_trace_event_consistency(
    manifest: ReviewTraceEventConsistencyManifest,
    trace: WorkflowReviewTrace,
    trace_assessment: ReviewTraceAssessment,
) -> ReviewTraceEventConsistencyAssessment:
    """Compare supplied review-trace event declarations without retrieval, signing, or state mutation."""

    issues: list[WorkflowValidationIssue] = []
    matched_event_types: set[ReviewTraceEventType] = set()
    if trace_assessment.status != ContextBundleStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="trace_event_assessment_not_ready", message="review trace is not ready for event consistency review"))
    if trace.trace_id != manifest.trace_id or trace_assessment.trace_id != manifest.trace_id:
        issues.append(WorkflowValidationIssue(code="trace_event_trace_id_mismatch", message="review trace identifier differs from the consistency manifest"))
    if trace.workflow_id != manifest.workflow_id or trace_assessment.workflow_id != manifest.workflow_id:
        issues.append(WorkflowValidationIssue(code="trace_event_workflow_id_mismatch", message="workflow identifier differs from the consistency manifest"))
    if trace.context_bundle_id != manifest.context_bundle_id:
        issues.append(WorkflowValidationIssue(code="trace_event_context_bundle_mismatch", message="context bundle identifier differs from the consistency manifest"))
    if trace.policy_provenance != manifest.policy_provenance:
        issues.append(WorkflowValidationIssue(code="trace_event_policy_provenance_mismatch", message="review trace policy provenance differs from the consistency manifest"))

    actual_by_type = {event.event_type: event for event in trace.events}
    for expected in manifest.expected_events:
        actual = actual_by_type.get(expected.event_type)
        if actual is None:
            issues.append(WorkflowValidationIssue(code="trace_event_missing", message=f"review trace is missing {expected.event_type.value} event"))
            continue
        if actual.artifact_reference != expected.artifact_reference:
            issues.append(WorkflowValidationIssue(code="trace_event_reference_mismatch", message=f"{expected.event_type.value} artifact reference differs from the consistency manifest"))
            continue
        if actual.artifact_digest != expected.artifact_digest:
            issues.append(WorkflowValidationIssue(code="trace_event_digest_mismatch", message=f"{expected.event_type.value} artifact digest differs from the consistency manifest"))
            continue
        matched_event_types.add(expected.event_type)

    return ReviewTraceEventConsistencyAssessment(
        manifest_id=manifest.manifest_id,
        trace_id=trace.trace_id,
        workflow_id=trace.workflow_id,
        status=ReviewTraceEventConsistencyStatus.INVALID if issues else ReviewTraceEventConsistencyStatus.CONSISTENT,
        matched_event_types=matched_event_types,
        issues=issues,
    )
