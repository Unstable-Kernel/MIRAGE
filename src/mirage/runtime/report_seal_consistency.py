from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .context_review import ContextBundleStatus
from .deterministic_report import DeterministicReviewReport
from .report_provenance import ReportProvenanceAssessment, ReportProvenanceSeal, ReportProvenanceStatus
from .review_trace import ReviewTraceAssessment, WorkflowReviewTrace
from .workflow_evidence import WorkflowValidationIssue


class ReportSealConsistencyStatus(StrEnum):
    CONSISTENT = "consistent"
    INVALID = "invalid"


class ReportSealConsistencyManifest(BaseModel):
    manifest_id: str = Field(min_length=1)
    report_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    report_digest: str = Field(min_length=8)
    source_trace_id: str = Field(min_length=1)
    sealer_reference: str = Field(min_length=1)


class ReportSealConsistencyAssessment(BaseModel):
    manifest_id: str
    report_id: str
    status: ReportSealConsistencyStatus
    matched_fields: set[str] = Field(default_factory=set)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_report_seal_consistency(
    manifest: ReportSealConsistencyManifest,
    report: DeterministicReviewReport,
    seal: ReportProvenanceSeal,
    provenance: ReportProvenanceAssessment,
    trace: WorkflowReviewTrace,
    trace_assessment: ReviewTraceAssessment,
) -> ReportSealConsistencyAssessment:
    """Compare supplied report-seal declarations without signing, fetching, or mutating artifacts."""

    issues: list[WorkflowValidationIssue] = []
    matched_fields: set[str] = set()
    if provenance.status != ReportProvenanceStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="report_seal_provenance_not_ready", message="report provenance is not ready for seal consistency review"))
    if trace_assessment.status != ContextBundleStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="report_seal_trace_not_ready", message="review trace is not ready for seal consistency review"))
    if report.report_id != manifest.report_id or provenance.report_id != manifest.report_id:
        issues.append(WorkflowValidationIssue(code="report_seal_report_id_mismatch", message="report identifier differs from the consistency manifest"))
    else:
        matched_fields.add("report_id")
    if report.workflow_id != manifest.workflow_id or trace.workflow_id != manifest.workflow_id or trace_assessment.workflow_id != manifest.workflow_id:
        issues.append(WorkflowValidationIssue(code="report_seal_workflow_mismatch", message="workflow identifier differs across report, trace, or manifest"))
    else:
        matched_fields.add("workflow_id")
    if trace.trace_id != manifest.source_trace_id or trace_assessment.trace_id != manifest.source_trace_id:
        issues.append(WorkflowValidationIssue(code="report_seal_trace_id_mismatch", message="review trace identifier differs from the consistency manifest"))
    else:
        matched_fields.add("source_trace_id")

    expected = {
        "report_id": manifest.report_id,
        "report_digest": manifest.report_digest,
        "source_trace_id": manifest.source_trace_id,
        "sealer_reference": manifest.sealer_reference,
    }
    for field_name, expected_value in expected.items():
        if getattr(seal, field_name) != expected_value:
            issues.append(WorkflowValidationIssue(code=f"report_seal_{field_name}_mismatch", message=f"report seal {field_name} differs from the consistency manifest"))
        else:
            matched_fields.add(field_name)

    trace_reference = f"trace:{manifest.source_trace_id}"
    if not any(trace_reference in section.artifact_references for section in report.sections):
        issues.append(WorkflowValidationIssue(code="report_seal_trace_reference_missing", message="report does not declare the sealed review trace reference"))
    else:
        matched_fields.add("report_trace_reference")

    return ReportSealConsistencyAssessment(
        manifest_id=manifest.manifest_id,
        report_id=report.report_id,
        status=ReportSealConsistencyStatus.INVALID if issues else ReportSealConsistencyStatus.CONSISTENT,
        matched_fields=matched_fields,
        issues=issues,
    )
