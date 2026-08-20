"""Reference-only provenance seals for deterministic review report artifacts."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from .deterministic_report import DeterministicReportAssessment, DeterministicReportStatus, DeterministicReviewReport
from .workflow_evidence import WorkflowValidationIssue


class ReportProvenanceStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    INVALID = "invalid"


class ReportProvenanceSeal(BaseModel):
    seal_id: str = Field(min_length=1)
    report_id: str = Field(min_length=1)
    report_digest: str = Field(min_length=8)
    source_trace_id: str = Field(min_length=1)
    sealer_reference: str = Field(min_length=1)
    sealed_at: datetime


class ReportProvenanceAssessment(BaseModel):
    report_id: str
    status: ReportProvenanceStatus
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_report_provenance(
    report: DeterministicReviewReport,
    report_assessment: DeterministicReportAssessment,
    seal: ReportProvenanceSeal,
) -> ReportProvenanceAssessment:
    """Validate report provenance identifiers and review readiness without signing or storing data."""

    issues: list[WorkflowValidationIssue] = []
    if report_assessment.status != DeterministicReportStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="report_not_ready", message="report is not ready for provenance review"))
    if seal.report_id != report.report_id or seal.report_id != report_assessment.report_id:
        issues.append(WorkflowValidationIssue(code="report_provenance_report_mismatch", message="report provenance seal identifier does not match"))
    return ReportProvenanceAssessment(
        report_id=report.report_id,
        status=ReportProvenanceStatus.INVALID if issues else ReportProvenanceStatus.READY_FOR_REVIEW,
        issues=issues,
    )
