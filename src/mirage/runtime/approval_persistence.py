"""Integration contracts for future authenticated approval persistence.

These models describe references and verification requirements only. They do
not handle credentials, write records, connect to an identity provider, or
grant authority.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, Field

from .approval_review import ApprovalChain, ApprovalChainAssessment
from .execution import ExecutionPolicy
from .workflow_evidence import WorkflowValidationIssue


class ApprovalPersistenceStatus(StrEnum):
    READY_FOR_INTEGRATION = "ready_for_integration"
    INCOMPLETE = "incomplete"


class ApprovalIdentityEvidence(BaseModel):
    subject_id: str = Field(min_length=1)
    identity_provider: str = Field(min_length=1)
    credential_reference: str = Field(min_length=1)
    authentication_event_digest: str = Field(min_length=8)
    authenticated_at: datetime


class ApprovalPersistenceDescriptor(BaseModel):
    persistence_id: str = Field(min_length=1)
    backend_type: str = Field(min_length=1)
    audit_log_reference: str = Field(min_length=1)
    signature_scheme: str = Field(min_length=1)
    retention_days: int = Field(gt=0, le=3650)
    identity_evidence: ApprovalIdentityEvidence


class ApprovalPersistenceAssessment(BaseModel):
    persistence_id: str
    chain_id: str
    status: ApprovalPersistenceStatus
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


class ApprovalPersistenceProvider(Protocol):
    """Future persistence adapter interface, intentionally without an implementation."""

    def describe(self) -> ApprovalPersistenceDescriptor:
        """Return declarative adapter metadata without connecting or writing."""

    def assess(self, chain: ApprovalChain) -> ApprovalPersistenceAssessment:
        """Assess a chain for integration readiness without persisting it."""


def assess_approval_persistence(
    descriptor: ApprovalPersistenceDescriptor,
    chain: ApprovalChain,
    approval: ApprovalChainAssessment,
    policy: ExecutionPolicy,
) -> ApprovalPersistenceAssessment:
    """Validate future persistence prerequisites without performing a write."""

    issues: list[WorkflowValidationIssue] = []
    if approval.chain_id != chain.chain_id:
        issues.append(WorkflowValidationIssue(code="persistence_chain_mismatch", message="approval assessment does not match the chain"))
    if chain.policy_provenance and chain.policy_provenance != policy.provenance.model_dump(mode="json"):
        issues.append(WorkflowValidationIssue(code="persistence_policy_provenance_mismatch", message="approval chain policy provenance differs from active policy"))
    if descriptor.identity_evidence.subject_id not in {record.approver_id for record in chain.approvals}:
        issues.append(WorkflowValidationIssue(code="persistence_identity_not_in_chain", message="identity evidence subject is not an approval-chain approver"))
    return ApprovalPersistenceAssessment(
        persistence_id=descriptor.persistence_id,
        chain_id=chain.chain_id,
        status=ApprovalPersistenceStatus.INCOMPLETE if issues else ApprovalPersistenceStatus.READY_FOR_INTEGRATION,
        issues=issues,
    )
