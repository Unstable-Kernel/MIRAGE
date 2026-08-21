"""Deterministic policy checks for non-executing review artifacts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .cross_artifact_review import CrossArtifactAssessment, CrossArtifactStatus
from .deterministic_report import DeterministicReviewReport
from .workflow_evidence import WorkflowValidationIssue


class ReviewPolicyStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    BLOCKED = "blocked"


class DeterministicReviewPolicy(BaseModel):
    policy_id: str = Field(min_length=1)
    max_report_sections: int = Field(default=8, ge=1, le=16)
    require_cross_artifact_consistency: bool = True
    require_reference_only_report: bool = True


class ReviewPolicyAssessment(BaseModel):
    policy_id: str
    workflow_id: str
    status: ReviewPolicyStatus
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_review_policy(
    policy: DeterministicReviewPolicy,
    report: DeterministicReviewReport,
    cross_artifact: CrossArtifactAssessment,
) -> ReviewPolicyAssessment:
    """Apply bounded review policy rules without a dispatcher or generated content."""

    issues: list[WorkflowValidationIssue] = []
    if policy.require_cross_artifact_consistency and cross_artifact.status != CrossArtifactStatus.CONSISTENT:
        issues.append(WorkflowValidationIssue(code="review_policy_cross_artifact_invalid", message="cross-artifact review is not consistent"))
    if len(report.sections) > policy.max_report_sections:
        issues.append(WorkflowValidationIssue(code="review_policy_section_limit_exceeded", message="report section count exceeds deterministic policy"))
    if policy.require_reference_only_report:
        for section in report.sections:
            if not section.context_claim_ids and not section.evidence_ids and not section.artifact_references:
                issues.append(WorkflowValidationIssue(code="review_policy_unreferenced_section", message=f"report section has no declared references: {section.section_id}"))
    return ReviewPolicyAssessment(
        policy_id=policy.policy_id,
        workflow_id=cross_artifact.workflow_id,
        status=ReviewPolicyStatus.BLOCKED if issues else ReviewPolicyStatus.READY_FOR_REVIEW,
        issues=issues,
    )
