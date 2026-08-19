import pytest
from pydantic import ValidationError

from mirage.runtime import (
    ReadOnlyTransportOperation,
    SandboxControl,
    SandboxEnforcementEvidence,
    SandboxEvidenceStatus,
    TransportVerificationEvidence,
    TransportVerificationStatus,
)


def test_live_transport_evidence_requires_authorization_cleanup_and_transcript_integrity():
    with pytest.raises(ValidationError, match="authorization reference"):
        TransportVerificationEvidence(
            evidence_id="live-incomplete",
            manifest_id="coppeliasim-zmq-read-only-reference-v1",
            status=TransportVerificationStatus.LIVE_VERIFIED,
            verified_operations={ReadOnlyTransportOperation.PROJECT_METADATA, ReadOnlyTransportOperation.STATE_SNAPSHOT},
            observed_simulator_version="4.x",
            verifier="reviewer",
        )


def test_verified_sandbox_evidence_requires_integrity_fields():
    with pytest.raises(ValidationError, match="evidence digest"):
        SandboxEnforcementEvidence(
            evidence_id="sandbox-incomplete",
            backend="isolated",
            status=SandboxEvidenceStatus.VERIFIED,
            verified_controls={SandboxControl.MEMORY_LIMIT},
            verifier="reviewer",
            environment_fingerprint="sha256:environment",
        )
