from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from ..eir import EIRDocument, LocalEIRSource
from .deterministic_report import DeterministicReportAssessment, DeterministicReportSection, DeterministicReportStatus, DeterministicReviewReport
from .evidence_provenance import EvidenceProvenanceAssessment, EvidenceProvenanceSeal, EvidenceProvenanceStatus
from .workflow_evidence import WorkflowValidationIssue


class ProvenanceConsistencyStatus(StrEnum):
    CONSISTENT = "consistent"
    INVALID = "invalid"


class EvidenceReportProvenanceBinding(BaseModel):
    evidence_id: str = Field(min_length=1)
    source_reference: str = Field(min_length=1)
    source_digest: str = Field(min_length=8)
    report_section_id: str = Field(min_length=1)


class ProvenanceConsistencyManifest(BaseModel):
    manifest_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    eir_document_id: str = Field(min_length=1)
    eir_source_reference: str = Field(min_length=1)
    eir_source_digest: str = Field(min_length=8)
    bindings: list[EvidenceReportProvenanceBinding] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def require_unique_evidence_bindings(self) -> ProvenanceConsistencyManifest:
        evidence_ids = [binding.evidence_id for binding in self.bindings]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("provenance consistency bindings must have unique evidence identifiers")
        return self


class ProvenanceConsistencyAssessment(BaseModel):
    manifest_id: str
    workflow_id: str
    eir_document_id: str
    status: ProvenanceConsistencyStatus
    verified_evidence_ids: set[str] = Field(default_factory=set)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def _matching_reference(section: DeterministicReportSection, binding: EvidenceReportProvenanceBinding) -> bool:
    return any(
        reference.evidence_id == binding.evidence_id
        and reference.source_reference == binding.source_reference
        and reference.source_digest == binding.source_digest
        for reference in section.provenance_references
    )


def assess_provenance_consistency(
    manifest: ProvenanceConsistencyManifest,
    source: LocalEIRSource,
    document: EIRDocument,
    seals: list[EvidenceProvenanceSeal],
    evidence_provenance: EvidenceProvenanceAssessment,
    report: DeterministicReviewReport,
    report_assessment: DeterministicReportAssessment,
) -> ProvenanceConsistencyAssessment:
    """Compare declared local provenance references and digests without reading sources.

    The assessment treats the supplied source metadata, seals, report, and prior
    review assessments as local inputs. It never opens referenced paths, fetches
    references, recalculates evidence content, or grants execution permission.
    """

    issues: list[WorkflowValidationIssue] = []
    if evidence_provenance.status != EvidenceProvenanceStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="provenance_evidence_not_ready", message="evidence provenance is not ready for consistency assessment"))
    if report_assessment.status != DeterministicReportStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="provenance_report_not_ready", message="deterministic report is not ready for consistency assessment"))
    if document.id != manifest.eir_document_id:
        issues.append(WorkflowValidationIssue(code="provenance_eir_document_mismatch", message="manifest EIR document identifier does not match the ingested document"))
    if document.provenance.source_path != manifest.eir_source_reference:
        issues.append(WorkflowValidationIssue(code="provenance_eir_reference_mismatch", message="manifest EIR source reference does not match document provenance"))
    if source.sha256 != manifest.eir_source_digest:
        issues.append(WorkflowValidationIssue(code="provenance_eir_digest_mismatch", message="manifest EIR source digest does not match local ingestion metadata"))
    if report.workflow_id != manifest.workflow_id or evidence_provenance.workflow_id != manifest.workflow_id:
        issues.append(WorkflowValidationIssue(code="provenance_workflow_mismatch", message="workflow identifiers do not match the provenance manifest"))

    seals_by_evidence = {seal.evidence_id: seal for seal in seals}
    sections = {section.section_id: section for section in report.sections}
    bindings = {binding.evidence_id: binding for binding in manifest.bindings}
    verified_evidence_ids: set[str] = set()

    for binding in manifest.bindings:
        seal = seals_by_evidence.get(binding.evidence_id)
        section = sections.get(binding.report_section_id)
        binding_valid = True
        if binding.evidence_id not in evidence_provenance.sealed_evidence_ids:
            issues.append(WorkflowValidationIssue(code="provenance_evidence_not_sealed", message=f"manifest evidence is not sealed: {binding.evidence_id}"))
            binding_valid = False
        if seal is None:
            issues.append(WorkflowValidationIssue(code="provenance_seal_missing", message=f"manifest evidence seal is missing: {binding.evidence_id}"))
            binding_valid = False
        elif seal.source_reference != binding.source_reference or seal.source_digest != binding.source_digest:
            issues.append(WorkflowValidationIssue(code="provenance_seal_binding_mismatch", message=f"manifest binding differs from evidence seal: {binding.evidence_id}"))
            binding_valid = False
        if section is None:
            issues.append(WorkflowValidationIssue(code="provenance_report_section_missing", message=f"manifest report section is missing: {binding.report_section_id}"))
            binding_valid = False
        else:
            if binding.evidence_id not in section.evidence_ids:
                issues.append(WorkflowValidationIssue(code="provenance_report_evidence_missing", message=f"report section does not cite evidence: {binding.evidence_id}"))
                binding_valid = False
            if not _matching_reference(section, binding):
                issues.append(WorkflowValidationIssue(code="provenance_report_reference_missing", message=f"report section has no matching provenance reference: {binding.evidence_id}"))
                binding_valid = False
        if binding_valid:
            verified_evidence_ids.add(binding.evidence_id)

    for section in report.sections:
        for reference in section.provenance_references:
            binding = bindings.get(reference.evidence_id)
            if binding is None:
                issues.append(WorkflowValidationIssue(code="provenance_report_binding_unknown", message=f"report references evidence absent from manifest: {reference.evidence_id}"))
            elif binding.report_section_id != section.section_id:
                issues.append(WorkflowValidationIssue(code="provenance_report_section_mismatch", message=f"report provenance reference appears in an unexpected section: {reference.evidence_id}"))

    return ProvenanceConsistencyAssessment(
        manifest_id=manifest.manifest_id,
        workflow_id=manifest.workflow_id,
        eir_document_id=manifest.eir_document_id,
        status=ProvenanceConsistencyStatus.INVALID if issues else ProvenanceConsistencyStatus.CONSISTENT,
        verified_evidence_ids=verified_evidence_ids,
        issues=issues,
    )
