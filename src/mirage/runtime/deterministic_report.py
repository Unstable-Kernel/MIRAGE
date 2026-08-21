"""Reference-only deterministic review report artifacts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .controlled_context import ControlledContextAssessment, ControlledContextStatus
from .evidence_provenance import EvidenceProvenanceAssessment, EvidenceProvenanceStatus
from .workflow_evidence import WorkflowValidationIssue


class DeterministicReportStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    INVALID = "invalid"


class ReportProvenanceReference(BaseModel):
    evidence_id: str = Field(min_length=1)
    source_reference: str = Field(min_length=1)
    source_digest: str = Field(min_length=8)


class DeterministicReportSection(BaseModel):
    section_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    context_claim_ids: set[str] = Field(default_factory=set)
    evidence_ids: set[str] = Field(default_factory=set)
    artifact_references: list[str] = Field(default_factory=list, max_length=16)
    provenance_references: list[ReportProvenanceReference] = Field(default_factory=list, max_length=16)


class DeterministicReviewReport(BaseModel):
    report_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    context_envelope_id: str = Field(min_length=1)
    report_version: str = Field(default="0.1", min_length=1)
    sections: list[DeterministicReportSection] = Field(min_length=1, max_length=16)

    @model_validator(mode="after")
    def require_unique_sections(self) -> DeterministicReviewReport:
        section_ids = [section.section_id for section in self.sections]
        if len(section_ids) != len(set(section_ids)):
            raise ValueError("deterministic report section identifiers must be unique")
        return self


class DeterministicReportAssessment(BaseModel):
    report_id: str
    workflow_id: str
    status: DeterministicReportStatus
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_deterministic_report(
    report: DeterministicReviewReport,
    context: ControlledContextAssessment,
    provenance: EvidenceProvenanceAssessment,
) -> DeterministicReportAssessment:
    """Validate report references without generating engineering claims or text."""

    issues: list[WorkflowValidationIssue] = []
    if context.status != ControlledContextStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="report_context_not_ready", message="controlled context is not ready for report review"))
    if provenance.status != EvidenceProvenanceStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="report_provenance_not_ready", message="evidence provenance is not ready for report review"))
    if report.workflow_id != context.workflow_id or report.workflow_id != provenance.workflow_id:
        issues.append(WorkflowValidationIssue(code="report_workflow_mismatch", message="report workflow identifier does not match review artifacts"))
    if report.context_envelope_id != context.envelope_id:
        issues.append(WorkflowValidationIssue(code="report_context_envelope_mismatch", message="report context envelope identifier does not match"))
    sealed_ids = provenance.sealed_evidence_ids
    for section in report.sections:
        unknown_claims = section.context_claim_ids - context.claim_ids
        if unknown_claims:
            issues.append(WorkflowValidationIssue(code="report_context_claim_unknown", message=f"report section references unknown claims: {', '.join(sorted(unknown_claims))}"))
        unknown_evidence = section.evidence_ids - sealed_ids
        if unknown_evidence:
            issues.append(WorkflowValidationIssue(code="report_evidence_unknown", message=f"report section references unsealed evidence: {', '.join(sorted(unknown_evidence))}"))
    return DeterministicReportAssessment(
        report_id=report.report_id,
        workflow_id=report.workflow_id,
        status=DeterministicReportStatus.INVALID if issues else DeterministicReportStatus.READY_FOR_REVIEW,
        issues=issues,
    )
