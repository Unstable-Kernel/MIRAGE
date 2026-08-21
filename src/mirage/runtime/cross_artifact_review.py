"""Cross-artifact consistency checks for review-only workflow evidence."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .approval_review import ApprovalChainAssessment, ApprovalChainStatus
from .controlled_context import ControlledContextAssessment, ControlledContextStatus
from .deterministic_report import DeterministicReportAssessment, DeterministicReportStatus
from .report_provenance import ReportProvenanceAssessment, ReportProvenanceStatus
from .review_trace import ReviewTraceAssessment
from .workflow_evidence import WorkflowValidationIssue


class CrossArtifactStatus(StrEnum):
    CONSISTENT = "consistent"
    INVALID = "invalid"


class CrossArtifactAssessment(BaseModel):
    workflow_id: str
    status: CrossArtifactStatus
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_cross_artifacts(
    context: ControlledContextAssessment,
    trace: ReviewTraceAssessment,
    approval: ApprovalChainAssessment,
    report: DeterministicReportAssessment,
    provenance: ReportProvenanceAssessment,
) -> CrossArtifactAssessment:
    """Validate identifiers and review readiness across local artifacts without state changes."""

    issues: list[WorkflowValidationIssue] = []
    workflow_ids = {context.workflow_id, trace.workflow_id, approval.workflow_id, report.workflow_id}
    workflow_id = context.workflow_id
    if len(workflow_ids) != 1:
        issues.append(WorkflowValidationIssue(code="cross_artifact_workflow_mismatch", message="review artifacts do not share one workflow identifier"))
    if context.status != ControlledContextStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="cross_artifact_context_not_ready", message="controlled context is not ready"))
    if trace.status.value != "ready_for_review":
        issues.append(WorkflowValidationIssue(code="cross_artifact_trace_not_ready", message="review trace is not ready"))
    if approval.status != ApprovalChainStatus.REVIEW_READY:
        issues.append(WorkflowValidationIssue(code="cross_artifact_approval_not_ready", message="approval chain is not ready"))
    if report.status != DeterministicReportStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="cross_artifact_report_not_ready", message="deterministic report is not ready"))
    if provenance.status != ReportProvenanceStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="cross_artifact_report_provenance_not_ready", message="report provenance is not ready"))
    return CrossArtifactAssessment(
        workflow_id=workflow_id,
        status=CrossArtifactStatus.INVALID if issues else CrossArtifactStatus.CONSISTENT,
        issues=issues,
    )
