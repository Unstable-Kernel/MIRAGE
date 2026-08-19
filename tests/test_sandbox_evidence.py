import asyncio

from mirage.runtime import (
    BackendSandboxCapabilities,
    CapabilityExecutor,
    ExecutionPolicy,
    ExecutionRequest,
    ExecutionStatus,
    LocalSimulationBackend,
    SandboxAssessmentStatus,
    SandboxControl,
    SandboxEnforcementEvidence,
    SandboxEnvelope,
    SandboxEvidenceStatus,
    assess_sandbox,
    default_registry,
)


def test_verified_evidence_is_required_for_an_os_enforced_budget():
    envelope = SandboxEnvelope(max_memory_mb=128)
    capabilities = BackendSandboxCapabilities(
        backend="isolated-fixture",
        enforces_memory_limit=True,
        enforces_read_only_filesystem=True,
        enforcement_evidence=SandboxEnforcementEvidence(
            evidence_id="isolated-fixture-v1",
            backend="isolated-fixture",
            status=SandboxEvidenceStatus.VERIFIED,
            verified_controls={SandboxControl.MEMORY_LIMIT, SandboxControl.READ_ONLY_FILESYSTEM},
            verifier="contract-test",
            environment_fingerprint="sha256:isolated-fixture",
        ),
    )

    assessment = assess_sandbox(envelope, capabilities)

    assert assessment.status == SandboxAssessmentStatus.ALLOWED


def test_missing_evidence_denies_even_if_backend_declares_capabilities():
    envelope = SandboxEnvelope(max_memory_mb=128)
    capabilities = BackendSandboxCapabilities(
        backend="asserted-only",
        enforces_memory_limit=True,
        enforces_read_only_filesystem=True,
    )

    assessment = assess_sandbox(envelope, capabilities)

    assert assessment.status == SandboxAssessmentStatus.DENIED
    assert "evidence" in assessment.message


def test_executor_accepts_a_budget_only_when_backend_evidence_covers_it():
    class EvidenceBackedLocalBackend(LocalSimulationBackend):
        sandbox_capabilities = BackendSandboxCapabilities(
            backend="local",
            enforces_memory_limit=True,
            enforces_read_only_filesystem=True,
            enforcement_evidence=SandboxEnforcementEvidence(
                evidence_id="local-contract-evidence-v1",
                backend="local",
                status=SandboxEvidenceStatus.VERIFIED,
                verified_controls={SandboxControl.MEMORY_LIMIT, SandboxControl.READ_ONLY_FILESYSTEM},
                verifier="contract-test",
                environment_fingerprint="sha256:local-contract",
            ),
        )

    result = asyncio.run(
        CapabilityExecutor(
            default_registry(),
            backends={"local": EvidenceBackedLocalBackend()},
        ).execute(
            ExecutionRequest(
                capability_id="run_simulation",
                backend="local",
                policy=ExecutionPolicy(
                    allow_simulation=True,
                    allowed_backends={"local"},
                    sandbox=SandboxEnvelope(max_memory_mb=128),
                ),
            )
        )
    )

    assert result.status == ExecutionStatus.SUCCEEDED
    assert result.metadata["sandbox_assessment"]["status"] == "allowed"
