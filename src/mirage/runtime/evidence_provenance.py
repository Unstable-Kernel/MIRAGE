"""Reference-only provenance seals for deterministic workflow evidence."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from .workflow_evidence import EvaluationEvidence, WorkflowEvidenceAssessment, WorkflowEvidenceStatus, WorkflowValidationIssue


class EvidenceProvenanceStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    INVALID = "invalid"


class EvidenceProvenanceSeal(BaseModel):
    seal_id: str = Field(min_length=1)
    evidence_id: str = Field(min_length=1)
    source_reference: str = Field(min_length=1)
    source_digest: str = Field(min_length=8)
    capture_method: str = Field(min_length=1)
    captured_at: datetime
    verifier_reference: str = Field(min_length=1)


class EvidenceProvenanceAssessment(BaseModel):
    workflow_id: str
    status: EvidenceProvenanceStatus
    sealed_evidence_ids: set[str] = Field(default_factory=set)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_evidence_provenance(
    assessment: WorkflowEvidenceAssessment,
    evidence: list[EvaluationEvidence],
    seals: list[EvidenceProvenanceSeal],
) -> EvidenceProvenanceAssessment:
    """Check one-to-one reference seals without retrieving or evaluating evidence contents."""

    issues: list[WorkflowValidationIssue] = []
    if assessment.status != WorkflowEvidenceStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="evidence_not_ready", message="workflow evidence is not ready for provenance review"))
    evidence_by_id = {item.evidence_id: item for item in evidence}
    sealed_ids: set[str] = set()
    for seal in seals:
        item = evidence_by_id.get(seal.evidence_id)
        if item is None:
            issues.append(WorkflowValidationIssue(code="seal_evidence_missing", message=f"seal references unknown evidence: {seal.evidence_id}"))
            continue
        if seal.source_reference != item.source_reference:
            issues.append(WorkflowValidationIssue(code="seal_source_reference_mismatch", message=f"seal source differs for evidence: {seal.evidence_id}"))
            continue
        sealed_ids.add(seal.evidence_id)
    missing = set(evidence_by_id) - sealed_ids
    for evidence_id in sorted(missing):
        issues.append(WorkflowValidationIssue(code="seal_missing", message=f"evidence has no provenance seal: {evidence_id}"))
    return EvidenceProvenanceAssessment(
        workflow_id=assessment.workflow_id,
        status=EvidenceProvenanceStatus.INVALID if issues else EvidenceProvenanceStatus.READY_FOR_REVIEW,
        sealed_evidence_ids=sealed_ids,
        issues=issues,
    )
