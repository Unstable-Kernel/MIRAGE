from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .deterministic_report import DeterministicReportAssessment, DeterministicReportSection, DeterministicReportStatus, DeterministicReviewReport
from .evidence_provenance import EvidenceProvenanceAssessment, EvidenceProvenanceSeal, EvidenceProvenanceStatus
from .review_policy import DeterministicReviewPolicy, ReviewPolicyAssessment, ReviewPolicyStatus
from .workflow_evidence import WorkflowValidationIssue


class ReviewPolicyEvidenceConsistencyStatus(StrEnum):
    CONSISTENT = "consistent"
    INVALID = "invalid"


class ReviewPolicyEvidenceReferenceBinding(BaseModel):
    evidence_id: str = Field(min_length=1)
    source_reference: str = Field(min_length=1)
    source_digest: str = Field(min_length=8)
    report_section_id: str = Field(min_length=1)


class ReviewPolicyEvidenceConsistencyManifest(BaseModel):
    manifest_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    review_policy_id: str = Field(min_length=1)
    max_report_sections: int = Field(ge=1, le=16)
    require_cross_artifact_consistency: bool
    require_reference_only_report: bool
    evidence_provenance_workflow_id: str = Field(min_length=1)
    bindings: list[ReviewPolicyEvidenceReferenceBinding] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def require_unique_evidence_bindings(self) -> ReviewPolicyEvidenceConsistencyManifest:
        evidence_ids = [binding.evidence_id for binding in self.bindings]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("review policy evidence bindings must have unique evidence identifiers")
        return self


class ReviewPolicyEvidenceConsistencyAssessment(BaseModel):
    manifest_id: str
    workflow_id: str
    status: ReviewPolicyEvidenceConsistencyStatus
    validated_evidence_ids: set[str] = Field(default_factory=set)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_review_policy_evidence_consistency(
    manifest: ReviewPolicyEvidenceConsistencyManifest,
    review_policy: DeterministicReviewPolicy,
    review_policy_assessment: ReviewPolicyAssessment,
    report: DeterministicReviewReport,
    report_assessment: DeterministicReportAssessment,
    evidence_provenance: EvidenceProvenanceAssessment,
    seals: list[EvidenceProvenanceSeal],
) -> ReviewPolicyEvidenceConsistencyAssessment:
    """Compare supplied review-policy bounds and evidence declarations without retrieval or execution."""

    issues: list[WorkflowValidationIssue] = []
    if review_policy_assessment.status != ReviewPolicyStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="review_policy_evidence_policy_not_ready", message="review policy assessment is not ready"))
    if report_assessment.status != DeterministicReportStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="review_policy_evidence_report_not_ready", message="deterministic report assessment is not ready"))
    if evidence_provenance.status != EvidenceProvenanceStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="review_policy_evidence_provenance_not_ready", message="evidence provenance assessment is not ready"))

    _match_value(issues, manifest.review_policy_id, review_policy.policy_id, "review_policy_evidence_policy_id_mismatch", "review policy identifier differs from manifest")
    _match_value(issues, manifest.review_policy_id, review_policy_assessment.policy_id, "review_policy_evidence_assessment_policy_id_mismatch", "review policy assessment identifier differs from manifest")
    _match_value(issues, manifest.max_report_sections, review_policy.max_report_sections, "review_policy_evidence_section_limit_mismatch", "review policy section limit differs from manifest")
    _match_value(issues, manifest.require_cross_artifact_consistency, review_policy.require_cross_artifact_consistency, "review_policy_evidence_cross_artifact_rule_mismatch", "cross-artifact rule differs from manifest")
    _match_value(issues, manifest.require_reference_only_report, review_policy.require_reference_only_report, "review_policy_evidence_reference_only_rule_mismatch", "reference-only rule differs from manifest")
    _match_value(issues, manifest.workflow_id, report.workflow_id, "review_policy_evidence_report_workflow_mismatch", "report workflow identifier differs from manifest")
    _match_value(issues, manifest.workflow_id, review_policy_assessment.workflow_id, "review_policy_evidence_assessment_workflow_mismatch", "review policy assessment workflow identifier differs from manifest")
    _match_value(issues, manifest.evidence_provenance_workflow_id, evidence_provenance.workflow_id, "review_policy_evidence_provenance_workflow_mismatch", "evidence provenance workflow identifier differs from manifest")
    if len(report.sections) > review_policy.max_report_sections:
        issues.append(WorkflowValidationIssue(code="review_policy_evidence_section_limit_exceeded", message="report section count exceeds supplied policy bound"))

    seals_by_evidence = {seal.evidence_id: seal for seal in seals}
    sections = {section.section_id: section for section in report.sections}
    bindings = {binding.evidence_id: binding for binding in manifest.bindings}
    validated_evidence_ids: set[str] = set()
    for binding in manifest.bindings:
        seal = seals_by_evidence.get(binding.evidence_id)
        section = sections.get(binding.report_section_id)
        binding_valid = True
        if binding.evidence_id not in evidence_provenance.sealed_evidence_ids:
            issues.append(WorkflowValidationIssue(code="review_policy_evidence_not_sealed", message=f"manifest evidence is not sealed: {binding.evidence_id}"))
            binding_valid = False
        if seal is None:
            issues.append(WorkflowValidationIssue(code="review_policy_evidence_seal_missing", message=f"manifest evidence seal is missing: {binding.evidence_id}"))
            binding_valid = False
        elif seal.source_reference != binding.source_reference or seal.source_digest != binding.source_digest:
            issues.append(WorkflowValidationIssue(code="review_policy_evidence_seal_mismatch", message=f"manifest binding differs from evidence seal: {binding.evidence_id}"))
            binding_valid = False
        if section is None:
            issues.append(WorkflowValidationIssue(code="review_policy_evidence_section_missing", message=f"manifest report section is missing: {binding.report_section_id}"))
            binding_valid = False
        else:
            if binding.evidence_id not in section.evidence_ids:
                issues.append(WorkflowValidationIssue(code="review_policy_evidence_report_missing", message=f"report section does not cite evidence: {binding.evidence_id}"))
                binding_valid = False
            if not _matching_reference(section, binding):
                issues.append(WorkflowValidationIssue(code="review_policy_evidence_reference_missing", message=f"report section has no matching provenance reference: {binding.evidence_id}"))
                binding_valid = False
        if binding_valid:
            validated_evidence_ids.add(binding.evidence_id)

    if review_policy.require_reference_only_report:
        for section in report.sections:
            if not section.context_claim_ids and not section.evidence_ids and not section.artifact_references and not section.provenance_references:
                issues.append(WorkflowValidationIssue(code="review_policy_evidence_unreferenced_section", message=f"report section has no declared references: {section.section_id}"))
    for section in report.sections:
        for reference in section.provenance_references:
            binding = bindings.get(reference.evidence_id)
            if binding is None:
                issues.append(WorkflowValidationIssue(code="review_policy_evidence_binding_unknown", message=f"report references evidence absent from manifest: {reference.evidence_id}"))
            elif binding.report_section_id != section.section_id:
                issues.append(WorkflowValidationIssue(code="review_policy_evidence_section_mismatch", message=f"report provenance reference appears in an unexpected section: {reference.evidence_id}"))

    return ReviewPolicyEvidenceConsistencyAssessment(
        manifest_id=manifest.manifest_id,
        workflow_id=manifest.workflow_id,
        status=ReviewPolicyEvidenceConsistencyStatus.INVALID if issues else ReviewPolicyEvidenceConsistencyStatus.CONSISTENT,
        validated_evidence_ids=validated_evidence_ids,
        issues=issues,
    )


def _matching_reference(section: DeterministicReportSection, binding: ReviewPolicyEvidenceReferenceBinding) -> bool:
    return any(
        reference.evidence_id == binding.evidence_id
        and reference.source_reference == binding.source_reference
        and reference.source_digest == binding.source_digest
        for reference in section.provenance_references
    )


def _match_value(issues: list[WorkflowValidationIssue], expected: object, actual: object, code: str, message: str) -> None:
    if expected != actual:
        issues.append(WorkflowValidationIssue(code=code, message=message))
