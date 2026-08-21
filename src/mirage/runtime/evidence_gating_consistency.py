from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .deterministic_report import DeterministicReviewReport
from .dispatch_eligibility import DispatchEligibilityAssessment, DispatchEligibilityStatus
from .evidence_capture_lineage_consistency import (
    EvidenceCaptureLineageConsistencyAssessment,
    EvidenceCaptureLineageConsistencyManifest,
    EvidenceCaptureLineageConsistencyStatus,
)
from .workflow_evidence import WorkflowValidationIssue


class EvidenceGatingConsistencyStatus(StrEnum):
    CONSISTENT = "consistent"
    INVALID = "invalid"


class EvidenceGatingBinding(BaseModel):
    capture_id: str = Field(min_length=1)
    evidence_id: str = Field(min_length=1)
    report_section_id: str = Field(min_length=1)
    required_dispatch_reasons: set[str] = Field(min_length=1, max_length=8)


class EvidenceGatingConsistencyManifest(BaseModel):
    manifest_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    capture_lineage_manifest_id: str = Field(min_length=1)
    require_ineligible_dispatch: bool
    bindings: list[EvidenceGatingBinding] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def require_unique_capture_bindings(self) -> "EvidenceGatingConsistencyManifest":
        capture_ids = [binding.capture_id for binding in self.bindings]
        if len(capture_ids) != len(set(capture_ids)):
            raise ValueError("evidence-gating bindings must have unique capture identifiers")
        return self


class EvidenceGatingConsistencyAssessment(BaseModel):
    manifest_id: str
    workflow_id: str
    status: EvidenceGatingConsistencyStatus
    validated_capture_ids: set[str] = Field(default_factory=set)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_evidence_gating_consistency(
    manifest: EvidenceGatingConsistencyManifest,
    lineage_manifest: EvidenceCaptureLineageConsistencyManifest,
    lineage_assessment: EvidenceCaptureLineageConsistencyAssessment,
    dispatch_assessment: DispatchEligibilityAssessment,
    report: DeterministicReviewReport,
) -> EvidenceGatingConsistencyAssessment:
    """Compare supplied evidence-gating declarations without dispatching or executing work."""

    issues: list[WorkflowValidationIssue] = []
    if lineage_assessment.status != EvidenceCaptureLineageConsistencyStatus.CONSISTENT:
        issues.append(WorkflowValidationIssue(code="evidence_gating_lineage_not_consistent", message="capture-lineage assessment is not consistent"))
    if manifest.require_ineligible_dispatch and dispatch_assessment.status != DispatchEligibilityStatus.INELIGIBLE:
        issues.append(WorkflowValidationIssue(code="evidence_gating_dispatch_not_ineligible", message="dispatch assessment is not explicitly ineligible"))
    if dispatch_assessment.execution_permitted:
        issues.append(WorkflowValidationIssue(code="evidence_gating_dispatch_execution_permitted", message="dispatch assessment must not permit execution"))

    _match_value(issues, manifest.workflow_id, lineage_manifest.workflow_id, "evidence_gating_lineage_manifest_workflow_mismatch", "lineage manifest workflow identifier differs from gating manifest")
    _match_value(issues, manifest.workflow_id, lineage_assessment.workflow_id, "evidence_gating_lineage_assessment_workflow_mismatch", "lineage assessment workflow identifier differs from gating manifest")
    _match_value(issues, manifest.workflow_id, dispatch_assessment.workflow_id, "evidence_gating_dispatch_workflow_mismatch", "dispatch assessment workflow identifier differs from gating manifest")
    _match_value(issues, manifest.workflow_id, report.workflow_id, "evidence_gating_report_workflow_mismatch", "report workflow identifier differs from gating manifest")
    _match_value(issues, manifest.capture_lineage_manifest_id, lineage_manifest.manifest_id, "evidence_gating_lineage_manifest_id_mismatch", "lineage manifest identifier differs from gating manifest")
    _match_value(issues, manifest.capture_lineage_manifest_id, lineage_assessment.manifest_id, "evidence_gating_lineage_assessment_manifest_mismatch", "lineage assessment manifest identifier differs from gating manifest")

    lineage_by_capture = {declaration.capture_id: declaration for declaration in lineage_manifest.declarations}
    sections = {section.section_id: section for section in report.sections}
    validated_capture_ids: set[str] = set()
    for binding in manifest.bindings:
        binding_valid = True
        lineage = lineage_by_capture.get(binding.capture_id)
        section = sections.get(binding.report_section_id)
        if lineage is None:
            issues.append(WorkflowValidationIssue(code="evidence_gating_capture_unknown", message=f"gating binding references unknown capture: {binding.capture_id}"))
            binding_valid = False
        elif lineage.evidence_id != binding.evidence_id:
            issues.append(WorkflowValidationIssue(code="evidence_gating_evidence_mismatch", message=f"gating evidence differs from capture lineage: {binding.capture_id}"))
            binding_valid = False
        if binding.capture_id not in lineage_assessment.validated_capture_ids:
            issues.append(WorkflowValidationIssue(code="evidence_gating_capture_not_validated", message=f"capture is not validated by lineage assessment: {binding.capture_id}"))
            binding_valid = False
        if section is None:
            issues.append(WorkflowValidationIssue(code="evidence_gating_report_section_missing", message=f"gating report section is missing: {binding.report_section_id}"))
            binding_valid = False
        elif binding.evidence_id not in section.evidence_ids:
            issues.append(WorkflowValidationIssue(code="evidence_gating_report_evidence_missing", message=f"report section does not cite gated evidence: {binding.evidence_id}"))
            binding_valid = False
        missing_reasons = binding.required_dispatch_reasons - set(dispatch_assessment.reasons)
        if missing_reasons:
            issues.append(WorkflowValidationIssue(code="evidence_gating_dispatch_reason_missing", message=f"dispatch assessment lacks declared gate reasons: {', '.join(sorted(missing_reasons))}"))
            binding_valid = False
        if binding_valid:
            validated_capture_ids.add(binding.capture_id)

    return EvidenceGatingConsistencyAssessment(
        manifest_id=manifest.manifest_id,
        workflow_id=manifest.workflow_id,
        status=EvidenceGatingConsistencyStatus.INVALID if issues else EvidenceGatingConsistencyStatus.CONSISTENT,
        validated_capture_ids=validated_capture_ids,
        issues=issues,
    )


def _match_value(issues: list[WorkflowValidationIssue], expected: object, actual: object, code: str, message: str) -> None:
    if expected != actual:
        issues.append(WorkflowValidationIssue(code=code, message=message))
