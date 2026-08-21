from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .deterministic_report import DeterministicReportSection, DeterministicReviewReport
from .evidence_provenance import EvidenceProvenanceAssessment, EvidenceProvenanceSeal, EvidenceProvenanceStatus
from .review_policy_evidence_consistency import ReviewPolicyEvidenceConsistencyAssessment, ReviewPolicyEvidenceConsistencyStatus
from .workflow_evidence import WorkflowValidationIssue


class EvidenceCaptureConsistencyStatus(StrEnum):
    CONSISTENT = "consistent"
    INVALID = "invalid"


class EvidenceCaptureDeclaration(BaseModel):
    capture_id: str = Field(min_length=1)
    evidence_id: str = Field(min_length=1)
    source_reference: str = Field(min_length=1)
    source_digest: str = Field(min_length=8)
    capture_method: str = Field(min_length=1)
    captured_at: datetime
    verifier_reference: str = Field(min_length=1)
    report_section_id: str = Field(min_length=1)


class EvidenceCaptureConsistencyManifest(BaseModel):
    manifest_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    review_policy_evidence_manifest_id: str = Field(min_length=1)
    require_review_policy_evidence_consistency: bool
    captures: list[EvidenceCaptureDeclaration] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def require_unique_capture_bindings(self) -> EvidenceCaptureConsistencyManifest:
        capture_ids = [capture.capture_id for capture in self.captures]
        evidence_ids = [capture.evidence_id for capture in self.captures]
        if len(capture_ids) != len(set(capture_ids)):
            raise ValueError("evidence capture declarations must have unique capture identifiers")
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("evidence capture declarations must have unique evidence identifiers")
        return self


class EvidenceCaptureConsistencyAssessment(BaseModel):
    manifest_id: str
    workflow_id: str
    status: EvidenceCaptureConsistencyStatus
    validated_capture_ids: set[str] = Field(default_factory=set)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_evidence_capture_consistency(
    manifest: EvidenceCaptureConsistencyManifest,
    evidence_provenance: EvidenceProvenanceAssessment,
    review_policy_evidence: ReviewPolicyEvidenceConsistencyAssessment,
    report: DeterministicReviewReport,
    seals: list[EvidenceProvenanceSeal],
) -> EvidenceCaptureConsistencyAssessment:
    """Compare supplied capture declarations with seals and report references without retrieval or execution."""

    issues: list[WorkflowValidationIssue] = []
    if evidence_provenance.status != EvidenceProvenanceStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="evidence_capture_provenance_not_ready", message="evidence provenance is not ready for capture review"))
    if manifest.require_review_policy_evidence_consistency and review_policy_evidence.status != ReviewPolicyEvidenceConsistencyStatus.CONSISTENT:
        issues.append(WorkflowValidationIssue(code="evidence_capture_review_policy_evidence_not_consistent", message="review-policy evidence assessment is not consistent"))

    _match_value(issues, manifest.workflow_id, evidence_provenance.workflow_id, "evidence_capture_provenance_workflow_mismatch", "evidence provenance workflow identifier differs from manifest")
    _match_value(issues, manifest.workflow_id, review_policy_evidence.workflow_id, "evidence_capture_review_policy_evidence_workflow_mismatch", "review-policy evidence workflow identifier differs from manifest")
    _match_value(issues, manifest.workflow_id, report.workflow_id, "evidence_capture_report_workflow_mismatch", "report workflow identifier differs from manifest")
    _match_value(issues, manifest.review_policy_evidence_manifest_id, review_policy_evidence.manifest_id, "evidence_capture_review_policy_evidence_manifest_mismatch", "review-policy evidence manifest identifier differs from capture manifest")

    seals_by_evidence = {seal.evidence_id: seal for seal in seals}
    sections = {section.section_id: section for section in report.sections}
    validated_capture_ids: set[str] = set()
    for capture in manifest.captures:
        capture_valid = True
        seal = seals_by_evidence.get(capture.evidence_id)
        section = sections.get(capture.report_section_id)
        if capture.evidence_id not in evidence_provenance.sealed_evidence_ids:
            issues.append(WorkflowValidationIssue(code="evidence_capture_not_sealed", message=f"capture evidence is not sealed: {capture.evidence_id}"))
            capture_valid = False
        if manifest.require_review_policy_evidence_consistency and capture.evidence_id not in review_policy_evidence.validated_evidence_ids:
            issues.append(WorkflowValidationIssue(code="evidence_capture_not_review_policy_validated", message=f"capture evidence is not validated by review-policy evidence assessment: {capture.evidence_id}"))
            capture_valid = False
        if seal is None:
            issues.append(WorkflowValidationIssue(code="evidence_capture_seal_missing", message=f"capture evidence seal is missing: {capture.evidence_id}"))
            capture_valid = False
        elif not _matches_seal(capture, seal):
            issues.append(WorkflowValidationIssue(code="evidence_capture_seal_mismatch", message=f"capture declaration differs from evidence seal: {capture.capture_id}"))
            capture_valid = False
        if section is None:
            issues.append(WorkflowValidationIssue(code="evidence_capture_report_section_missing", message=f"capture report section is missing: {capture.report_section_id}"))
            capture_valid = False
        else:
            if capture.evidence_id not in section.evidence_ids:
                issues.append(WorkflowValidationIssue(code="evidence_capture_report_missing", message=f"report section does not cite capture evidence: {capture.evidence_id}"))
                capture_valid = False
            if not _matches_report_reference(section, capture):
                issues.append(WorkflowValidationIssue(code="evidence_capture_report_reference_missing", message=f"report section has no matching provenance reference: {capture.evidence_id}"))
                capture_valid = False
        if capture_valid:
            validated_capture_ids.add(capture.capture_id)

    return EvidenceCaptureConsistencyAssessment(
        manifest_id=manifest.manifest_id,
        workflow_id=manifest.workflow_id,
        status=EvidenceCaptureConsistencyStatus.INVALID if issues else EvidenceCaptureConsistencyStatus.CONSISTENT,
        validated_capture_ids=validated_capture_ids,
        issues=issues,
    )


def _matches_seal(capture: EvidenceCaptureDeclaration, seal: EvidenceProvenanceSeal) -> bool:
    return (
        seal.source_reference == capture.source_reference
        and seal.source_digest == capture.source_digest
        and seal.capture_method == capture.capture_method
        and seal.captured_at == capture.captured_at
        and seal.verifier_reference == capture.verifier_reference
    )


def _matches_report_reference(section: DeterministicReportSection, capture: EvidenceCaptureDeclaration) -> bool:
    return any(
        reference.evidence_id == capture.evidence_id
        and reference.source_reference == capture.source_reference
        and reference.source_digest == capture.source_digest
        for reference in section.provenance_references
    )


def _match_value(issues: list[WorkflowValidationIssue], expected: object, actual: object, code: str, message: str) -> None:
    if expected != actual:
        issues.append(WorkflowValidationIssue(code=code, message=message))
