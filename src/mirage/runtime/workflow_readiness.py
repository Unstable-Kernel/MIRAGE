"""Unified readiness view that intentionally never dispatches a workflow."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .cross_artifact_review import CrossArtifactAssessment, CrossArtifactStatus
from .dispatch_eligibility import DispatchEligibilityAssessment
from .review_policy import ReviewPolicyAssessment, ReviewPolicyStatus


class WorkflowReadinessStatus(StrEnum):
    READY_FOR_EXTERNAL_PREREQUISITES = "ready_for_external_prerequisites"
    BLOCKED = "blocked"


class WorkflowReadinessAssessment(BaseModel):
    workflow_id: str
    status: WorkflowReadinessStatus
    denial_reasons: list[str] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_workflow_readiness(
    cross_artifact: CrossArtifactAssessment,
    policy: ReviewPolicyAssessment,
    dispatch: DispatchEligibilityAssessment,
) -> WorkflowReadinessAssessment:
    """Combine review readiness with future dispatch prerequisites without invoking a backend."""

    reasons: list[str] = []
    if cross_artifact.status != CrossArtifactStatus.CONSISTENT:
        reasons.extend(issue.message for issue in cross_artifact.issues)
    if policy.status != ReviewPolicyStatus.READY_FOR_REVIEW:
        reasons.extend(issue.message for issue in policy.issues)
    reasons.extend(dispatch.reasons)
    status = WorkflowReadinessStatus.READY_FOR_EXTERNAL_PREREQUISITES
    if cross_artifact.status != CrossArtifactStatus.CONSISTENT or policy.status != ReviewPolicyStatus.READY_FOR_REVIEW:
        status = WorkflowReadinessStatus.BLOCKED
    return WorkflowReadinessAssessment(
        workflow_id=cross_artifact.workflow_id,
        status=status,
        denial_reasons=list(dict.fromkeys(reasons)),
    )
