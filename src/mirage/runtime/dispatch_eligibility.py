"""Guarded dispatch eligibility assessment that never dispatches a capability."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .approval_review import ApprovalChainAssessment, ApprovalChainStatus
from .execution import ExecutionPolicy
from .sandbox import SandboxAssessment, SandboxAssessmentStatus
from .transport_verification import TransportVerificationReport, TransportVerificationStatus


class DispatchEligibilityStatus(StrEnum):
    INELIGIBLE = "ineligible"
    ELIGIBLE_FOR_VERIFIED_DISPATCH = "eligible_for_verified_dispatch"


class DispatchEligibilityAssessment(BaseModel):
    workflow_id: str
    status: DispatchEligibilityStatus
    reasons: list[str] = Field(default_factory=list)
    approval_chain_id: str | None = None
    transport_manifest_id: str | None = None
    sandbox_envelope_id: str | None = None
    execution_permitted: bool = False


def assess_dispatch_eligibility(
    approval: ApprovalChainAssessment,
    transport: TransportVerificationReport,
    sandbox: SandboxAssessment,
    policy: ExecutionPolicy,
) -> DispatchEligibilityAssessment:
    """Assess prerequisites for a future dispatcher without invoking any backend."""

    reasons: list[str] = []
    if approval.status != ApprovalChainStatus.REVIEW_READY:
        reasons.append("human approval chain is not ready for review")
    if not policy.allow_simulation:
        reasons.append("active policy does not allow simulation")
    if not transport.valid or transport.status != TransportVerificationStatus.LIVE_VERIFIED:
        reasons.append("live read-only transport is not independently verified")
    if sandbox.status != SandboxAssessmentStatus.ALLOWED:
        reasons.append("sandbox assessment is not backed by an enforced verified environment")
    return DispatchEligibilityAssessment(
        workflow_id=approval.workflow_id,
        status=DispatchEligibilityStatus.INELIGIBLE if reasons else DispatchEligibilityStatus.ELIGIBLE_FOR_VERIFIED_DISPATCH,
        reasons=reasons,
        approval_chain_id=approval.chain_id,
        transport_manifest_id=transport.manifest_id,
        sandbox_envelope_id=sandbox.envelope_id,
    )
