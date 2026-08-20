from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .context_review import WorkflowContextBundle
from .controlled_context import ControlledContextEnvelope
from .deterministic_report import DeterministicReviewReport
from .execution import ExecutionPolicy
from .review_policy import DeterministicReviewPolicy, ReviewPolicyAssessment, ReviewPolicyStatus
from .review_trace import WorkflowReviewTrace
from .workflow_evidence import WorkflowValidationIssue


class PolicyProvenanceConsistencyStatus(StrEnum):
    CONSISTENT = "consistent"
    INVALID = "invalid"


class PolicyProvenanceConsistencyManifest(BaseModel):
    manifest_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    context_bundle_id: str = Field(min_length=1)
    context_envelope_id: str = Field(min_length=1)
    trace_id: str = Field(min_length=1)
    report_id: str = Field(min_length=1)
    review_policy_id: str = Field(min_length=1)
    policy_provenance: dict[str, object]


class PolicyProvenanceConsistencyAssessment(BaseModel):
    manifest_id: str
    workflow_id: str
    status: PolicyProvenanceConsistencyStatus
    matched_declarations: set[str] = Field(default_factory=set)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_policy_provenance_consistency(
    manifest: PolicyProvenanceConsistencyManifest,
    policy: ExecutionPolicy,
    context_bundle: WorkflowContextBundle,
    context_envelope: ControlledContextEnvelope,
    trace: WorkflowReviewTrace,
    report: DeterministicReviewReport,
    review_policy: DeterministicReviewPolicy,
    review_policy_assessment: ReviewPolicyAssessment,
) -> PolicyProvenanceConsistencyAssessment:
    """Compare supplied policy provenance declarations without retrieval, mutation, or execution."""

    issues: list[WorkflowValidationIssue] = []
    matched_declarations: set[str] = set()
    active_provenance = policy.provenance.model_dump(mode="json")

    _match_value(issues, matched_declarations, "policy_provenance", manifest.policy_provenance, active_provenance, "policy_provenance_active_mismatch")
    _match_value(issues, matched_declarations, "context_policy_provenance", manifest.policy_provenance, context_bundle.policy_provenance, "policy_provenance_context_mismatch")
    _match_value(issues, matched_declarations, "trace_policy_provenance", manifest.policy_provenance, trace.policy_provenance, "policy_provenance_trace_mismatch")
    _match_value(issues, matched_declarations, "workflow_id", manifest.workflow_id, context_bundle.workflow_id, "policy_provenance_context_workflow_mismatch")
    _match_value(issues, matched_declarations, "context_bundle_id", manifest.context_bundle_id, context_bundle.context_bundle_id, "policy_provenance_context_bundle_mismatch")
    _match_value(issues, matched_declarations, "context_envelope_id", manifest.context_envelope_id, context_envelope.envelope_id, "policy_provenance_context_envelope_mismatch")
    _match_value(issues, matched_declarations, "trace_id", manifest.trace_id, trace.trace_id, "policy_provenance_trace_id_mismatch")
    _match_value(issues, matched_declarations, "report_id", manifest.report_id, report.report_id, "policy_provenance_report_id_mismatch")
    _match_value(issues, matched_declarations, "review_policy_id", manifest.review_policy_id, review_policy.policy_id, "policy_provenance_review_policy_id_mismatch")
    _match_value(issues, matched_declarations, "review_policy_assessment_policy_id", manifest.review_policy_id, review_policy_assessment.policy_id, "policy_provenance_review_policy_assessment_mismatch")

    for declaration_name, workflow_id in {
        "context_envelope_workflow_id": context_envelope.workflow_id,
        "trace_workflow_id": trace.workflow_id,
        "report_workflow_id": report.workflow_id,
        "review_policy_assessment_workflow_id": review_policy_assessment.workflow_id,
    }.items():
        _match_value(issues, matched_declarations, declaration_name, manifest.workflow_id, workflow_id, "policy_provenance_workflow_mismatch")
    if review_policy_assessment.status != ReviewPolicyStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="policy_provenance_review_policy_not_ready", message="review policy assessment is not ready for consistency review"))

    return PolicyProvenanceConsistencyAssessment(
        manifest_id=manifest.manifest_id,
        workflow_id=manifest.workflow_id,
        status=PolicyProvenanceConsistencyStatus.INVALID if issues else PolicyProvenanceConsistencyStatus.CONSISTENT,
        matched_declarations=matched_declarations,
        issues=issues,
    )


def _match_value(
    issues: list[WorkflowValidationIssue],
    matched_declarations: set[str],
    declaration_name: str,
    expected: object,
    actual: object,
    issue_code: str,
) -> None:
    if expected != actual:
        issues.append(WorkflowValidationIssue(code=issue_code, message=f"{declaration_name} differs from the consistency manifest"))
        return
    matched_declarations.add(declaration_name)
