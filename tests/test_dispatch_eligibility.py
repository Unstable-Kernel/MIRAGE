from mirage.runtime import (
    ApprovalChainAssessment,
    ApprovalChainStatus,
    BackendSandboxCapabilities,
    DispatchEligibilityStatus,
    ExecutionPolicy,
    SandboxAssessment,
    SandboxAssessmentStatus,
    TransportVerificationReport,
    TransportVerificationStatus,
    assess_dispatch_eligibility,
)


def test_dispatch_is_ineligible_without_live_transport_or_enforced_sandbox():
    approval = ApprovalChainAssessment(
        chain_id="chain-v1",
        workflow_id="workflow-v1",
        trace_id="trace-v1",
        status=ApprovalChainStatus.REVIEW_READY,
    )
    transport = TransportVerificationReport(
        manifest_id="fixture-v1",
        adapter="fixture",
        status=TransportVerificationStatus.FIXTURE_VERIFIED,
        valid=True,
    )
    sandbox = SandboxAssessment(
        status=SandboxAssessmentStatus.DECLARATIVE_ONLY,
        backend="local",
        envelope_id="local-default",
        envelope_revision="1",
        message="declarative only",
        capabilities=BackendSandboxCapabilities(backend="local"),
    )

    assessment = assess_dispatch_eligibility(approval, transport, sandbox, ExecutionPolicy(allow_simulation=True))

    assert assessment.status == DispatchEligibilityStatus.INELIGIBLE
    assert assessment.execution_permitted is False
    assert assessment.reasons == [
        "live read-only transport is not independently verified",
        "sandbox assessment is not backed by an enforced verified environment",
    ]
