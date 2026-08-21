from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .evidence_capture_consistency import EvidenceCaptureConsistencyAssessment, EvidenceCaptureConsistencyManifest, EvidenceCaptureConsistencyStatus
from .workflow_evidence import WorkflowValidationIssue


class EvidenceCaptureLineageConsistencyStatus(StrEnum):
    CONSISTENT = "consistent"
    INVALID = "invalid"


class EvidenceCaptureLineageDeclaration(BaseModel):
    capture_id: str = Field(min_length=1)
    evidence_id: str = Field(min_length=1)
    predecessor_capture_ids: set[str] = Field(default_factory=set, max_length=16)


class EvidenceCaptureLineageConsistencyManifest(BaseModel):
    manifest_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    evidence_capture_manifest_id: str = Field(min_length=1)
    require_evidence_capture_consistency: bool
    declarations: list[EvidenceCaptureLineageDeclaration] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def require_unique_capture_declarations(self) -> EvidenceCaptureLineageConsistencyManifest:
        capture_ids = [declaration.capture_id for declaration in self.declarations]
        if len(capture_ids) != len(set(capture_ids)):
            raise ValueError("capture-lineage declarations must have unique capture identifiers")
        return self


class EvidenceCaptureLineageConsistencyAssessment(BaseModel):
    manifest_id: str
    workflow_id: str
    status: EvidenceCaptureLineageConsistencyStatus
    validated_capture_ids: set[str] = Field(default_factory=set)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_evidence_capture_lineage_consistency(
    manifest: EvidenceCaptureLineageConsistencyManifest,
    capture_manifest: EvidenceCaptureConsistencyManifest,
    capture_assessment: EvidenceCaptureConsistencyAssessment,
) -> EvidenceCaptureLineageConsistencyAssessment:
    """Compare supplied capture-lineage declarations without retrieving, ordering, or executing captures."""

    issues: list[WorkflowValidationIssue] = []
    if manifest.require_evidence_capture_consistency and capture_assessment.status != EvidenceCaptureConsistencyStatus.CONSISTENT:
        issues.append(WorkflowValidationIssue(code="capture_lineage_capture_assessment_not_consistent", message="evidence-capture assessment is not consistent"))

    _match_value(issues, manifest.workflow_id, capture_manifest.workflow_id, "capture_lineage_capture_manifest_workflow_mismatch", "capture manifest workflow identifier differs from lineage manifest")
    _match_value(issues, manifest.workflow_id, capture_assessment.workflow_id, "capture_lineage_capture_assessment_workflow_mismatch", "capture assessment workflow identifier differs from lineage manifest")
    _match_value(issues, manifest.evidence_capture_manifest_id, capture_manifest.manifest_id, "capture_lineage_capture_manifest_id_mismatch", "capture manifest identifier differs from lineage manifest")
    _match_value(issues, manifest.evidence_capture_manifest_id, capture_assessment.manifest_id, "capture_lineage_capture_assessment_manifest_mismatch", "capture assessment manifest identifier differs from lineage manifest")

    captures_by_id = {capture.capture_id: capture for capture in capture_manifest.captures}
    declarations_by_id = {declaration.capture_id: declaration for declaration in manifest.declarations}
    for capture_id in sorted(set(captures_by_id) - set(declarations_by_id)):
        issues.append(WorkflowValidationIssue(code="capture_lineage_declaration_missing", message=f"capture has no lineage declaration: {capture_id}"))
    for capture_id in sorted(set(declarations_by_id) - set(captures_by_id)):
        issues.append(WorkflowValidationIssue(code="capture_lineage_capture_unknown", message=f"lineage declaration references unknown capture: {capture_id}"))

    valid_capture_ids: set[str] = set()
    for capture_id, declaration in declarations_by_id.items():
        source_capture = captures_by_id.get(capture_id)
        if source_capture is None:
            continue
        declaration_valid = True
        if declaration.evidence_id != source_capture.evidence_id:
            issues.append(WorkflowValidationIssue(code="capture_lineage_evidence_mismatch", message=f"lineage evidence differs from capture declaration: {capture_id}"))
            declaration_valid = False
        if manifest.require_evidence_capture_consistency and capture_id not in capture_assessment.validated_capture_ids:
            issues.append(WorkflowValidationIssue(code="capture_lineage_capture_not_validated", message=f"capture is not validated by evidence-capture assessment: {capture_id}"))
            declaration_valid = False
        if capture_id in declaration.predecessor_capture_ids:
            issues.append(WorkflowValidationIssue(code="capture_lineage_self_reference", message=f"capture declares itself as a predecessor: {capture_id}"))
            declaration_valid = False
        for predecessor_id in sorted(declaration.predecessor_capture_ids - set(captures_by_id)):
            issues.append(WorkflowValidationIssue(code="capture_lineage_predecessor_unknown", message=f"capture predecessor is unknown: {predecessor_id}"))
            declaration_valid = False
        if declaration_valid:
            valid_capture_ids.add(capture_id)

    cyclic_capture_ids = _cyclic_capture_ids(declarations_by_id)
    for capture_id in sorted(cyclic_capture_ids):
        issues.append(WorkflowValidationIssue(code="capture_lineage_cycle", message=f"capture lineage contains a cycle at: {capture_id}"))
    valid_capture_ids -= cyclic_capture_ids

    return EvidenceCaptureLineageConsistencyAssessment(
        manifest_id=manifest.manifest_id,
        workflow_id=manifest.workflow_id,
        status=EvidenceCaptureLineageConsistencyStatus.INVALID if issues else EvidenceCaptureLineageConsistencyStatus.CONSISTENT,
        validated_capture_ids=valid_capture_ids,
        issues=issues,
    )


def _cyclic_capture_ids(declarations: dict[str, EvidenceCaptureLineageDeclaration]) -> set[str]:
    visited: set[str] = set()
    active: set[str] = set()
    stack: list[str] = []
    cyclic: set[str] = set()

    def visit(capture_id: str) -> None:
        if capture_id in active:
            cyclic.update(stack[stack.index(capture_id) :])
            return
        if capture_id in visited or capture_id not in declarations:
            return
        active.add(capture_id)
        stack.append(capture_id)
        for predecessor_id in declarations[capture_id].predecessor_capture_ids:
            visit(predecessor_id)
        stack.pop()
        active.remove(capture_id)
        visited.add(capture_id)

    for capture_id in declarations:
        visit(capture_id)
    return cyclic


def _match_value(issues: list[WorkflowValidationIssue], expected: object, actual: object, code: str, message: str) -> None:
    if expected != actual:
        issues.append(WorkflowValidationIssue(code=code, message=message))
