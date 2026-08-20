"""Non-mutating review contract for declared approval revocations."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from .approval_review import ApprovalChain
from .execution import ExecutionPolicy
from .workflow_evidence import WorkflowValidationIssue


class ApprovalRevocationStatus(StrEnum):
    DECLARED = "declared"
    INVALID = "invalid"


class ApprovalRevocationRecord(BaseModel):
    revocation_id: str = Field(min_length=1)
    chain_id: str = Field(min_length=1)
    approval_id: str = Field(min_length=1)
    revoker_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    policy_provenance: dict[str, object] = Field(default_factory=dict)
    revocation_digest: str = Field(min_length=8)
    recorded_at: datetime


class ApprovalRevocationAssessment(BaseModel):
    revocation_id: str
    chain_id: str
    status: ApprovalRevocationStatus
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_approval_revocation(
    record: ApprovalRevocationRecord,
    chain: ApprovalChain,
    policy: ExecutionPolicy,
) -> ApprovalRevocationAssessment:
    """Validate a declared revocation without changing any stored approval state."""

    issues: list[WorkflowValidationIssue] = []
    if record.chain_id != chain.chain_id:
        issues.append(WorkflowValidationIssue(code="revocation_chain_mismatch", message="revocation chain identifier does not match"))
    if record.approval_id not in {approval.approval_id for approval in chain.approvals}:
        issues.append(WorkflowValidationIssue(code="revocation_approval_missing", message="revocation targets an unknown approval"))
    active_provenance = policy.provenance.model_dump(mode="json")
    if record.policy_provenance and record.policy_provenance != active_provenance:
        issues.append(WorkflowValidationIssue(code="revocation_policy_provenance_mismatch", message="revocation policy provenance differs from active policy"))
    return ApprovalRevocationAssessment(
        revocation_id=record.revocation_id,
        chain_id=record.chain_id,
        status=ApprovalRevocationStatus.INVALID if issues else ApprovalRevocationStatus.DECLARED,
        issues=issues,
    )
