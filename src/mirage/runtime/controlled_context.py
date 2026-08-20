"""Schema-bound context references for deterministic review artifacts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .context_review import ContextBundleStatus, ContextItemKind, WorkflowContextAssessment, WorkflowContextBundle
from .workflow_evidence import WorkflowValidationIssue


class ControlledContextStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    INVALID = "invalid"


class ControlledContextField(BaseModel):
    field_id: str = Field(min_length=1)
    item_kind: ContextItemKind
    required: bool = True
    allowed_reference_prefix: str = Field(min_length=1)


class ControlledContextSchema(BaseModel):
    schema_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    version: str = Field(default="0.1", min_length=1)
    fields: list[ControlledContextField] = Field(min_length=1, max_length=16)

    @model_validator(mode="after")
    def require_unique_fields(self) -> ControlledContextSchema:
        field_ids = [field.field_id for field in self.fields]
        if len(field_ids) != len(set(field_ids)):
            raise ValueError("controlled context field identifiers must be unique")
        return self


class ControlledContextClaim(BaseModel):
    claim_id: str = Field(min_length=1)
    field_id: str = Field(min_length=1)
    context_item_id: str = Field(min_length=1)
    reference_digest: str = Field(min_length=8)


class ControlledContextEnvelope(BaseModel):
    envelope_id: str = Field(min_length=1)
    schema_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    context_bundle_id: str = Field(min_length=1)
    claims: list[ControlledContextClaim] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def require_unique_claims_and_fields(self) -> ControlledContextEnvelope:
        claim_ids = [claim.claim_id for claim in self.claims]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("controlled context claim identifiers must be unique")
        field_ids = [claim.field_id for claim in self.claims]
        if len(field_ids) != len(set(field_ids)):
            raise ValueError("controlled context fields may have only one claim")
        return self


class ControlledContextAssessment(BaseModel):
    envelope_id: str
    workflow_id: str
    status: ControlledContextStatus
    claim_ids: set[str] = Field(default_factory=set)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_controlled_context(
    schema: ControlledContextSchema,
    envelope: ControlledContextEnvelope,
    bundle: WorkflowContextBundle,
    assessment: WorkflowContextAssessment,
) -> ControlledContextAssessment:
    """Validate bounded context claims without retrieving source content."""

    issues: list[WorkflowValidationIssue] = []
    if assessment.status != ContextBundleStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="context_not_ready", message="workflow context is not ready for controlled assessment"))
    if schema.workflow_id != envelope.workflow_id or bundle.workflow_id != envelope.workflow_id:
        issues.append(WorkflowValidationIssue(code="controlled_context_workflow_mismatch", message="controlled context workflow identifier does not match"))
    if schema.schema_id != envelope.schema_id:
        issues.append(WorkflowValidationIssue(code="controlled_context_schema_mismatch", message="controlled context schema identifier does not match"))
    if bundle.context_bundle_id != envelope.context_bundle_id:
        issues.append(WorkflowValidationIssue(code="controlled_context_bundle_mismatch", message="controlled context bundle identifier does not match"))
    fields = {field.field_id: field for field in schema.fields}
    items = {item.context_item_id: item for item in bundle.items}
    claims_by_field = {claim.field_id: claim for claim in envelope.claims}
    for field in schema.fields:
        if field.required and field.field_id not in claims_by_field:
            issues.append(WorkflowValidationIssue(code="controlled_context_claim_missing", message=f"required context claim is missing: {field.field_id}"))
    for claim in envelope.claims:
        field = fields.get(claim.field_id)
        if field is None:
            issues.append(WorkflowValidationIssue(code="controlled_context_field_unknown", message=f"claim references unknown field: {claim.field_id}"))
            continue
        item = items.get(claim.context_item_id)
        if item is None:
            issues.append(WorkflowValidationIssue(code="controlled_context_item_unknown", message=f"claim references unknown item: {claim.context_item_id}"))
            continue
        if item.kind != field.item_kind:
            issues.append(WorkflowValidationIssue(code="controlled_context_kind_mismatch", message=f"claim item kind differs for field: {claim.field_id}"))
        if not item.reference.startswith(field.allowed_reference_prefix):
            issues.append(WorkflowValidationIssue(code="controlled_context_reference_prefix_invalid", message=f"claim reference prefix differs for field: {claim.field_id}"))
        if claim.reference_digest != item.content_digest:
            issues.append(WorkflowValidationIssue(code="controlled_context_digest_mismatch", message=f"claim digest differs for item: {claim.context_item_id}"))
    return ControlledContextAssessment(
        envelope_id=envelope.envelope_id,
        workflow_id=envelope.workflow_id,
        status=ControlledContextStatus.INVALID if issues else ControlledContextStatus.READY_FOR_REVIEW,
        claim_ids={claim.claim_id for claim in envelope.claims},
        issues=issues,
    )
