from mirage.runtime import (
    ReadOnlyTransportManifest,
    ReadOnlyTransportOperation,
    TransportVerificationEvidence,
    TransportVerificationStatus,
    assess_transport,
    coppeliasim_zmq_read_only_manifest,
)


def test_coppeliasim_reference_manifest_is_unverified_and_prohibits_control():
    manifest = coppeliasim_zmq_read_only_manifest()

    assert manifest.verification_status == TransportVerificationStatus.UNVERIFIED
    assert manifest.protocol == "zeromq-remote-api"
    assert "start_simulation" in manifest.prohibited_operations
    assert "step_simulation" in manifest.prohibited_operations


def test_fixture_evidence_can_verify_only_declared_read_operations():
    manifest = ReadOnlyTransportManifest(
        manifest_id="fixture-v1",
        adapter="fixture",
        protocol="json",
        endpoint_scheme="file",
        simulator_version="fixture",
        state_semantics_revision="1",
        allowed_operations={ReadOnlyTransportOperation.PROJECT_METADATA, ReadOnlyTransportOperation.STATE_SNAPSHOT},
        verification_status=TransportVerificationStatus.FIXTURE_VERIFIED,
    )
    evidence = TransportVerificationEvidence(
        evidence_id="fixture-evidence-v1",
        manifest_id=manifest.manifest_id,
        status=TransportVerificationStatus.FIXTURE_VERIFIED,
        fixture_digest="sha256:fixture",
        verified_operations=set(manifest.allowed_operations),
    )

    report = assess_transport(manifest, evidence)

    assert report.valid is True
    assert report.status == TransportVerificationStatus.FIXTURE_VERIFIED


def test_transport_evidence_without_snapshot_coverage_is_rejected():
    manifest = coppeliasim_zmq_read_only_manifest()
    evidence = TransportVerificationEvidence(
        evidence_id="partial-evidence",
        manifest_id=manifest.manifest_id,
        status=TransportVerificationStatus.FIXTURE_VERIFIED,
        fixture_digest="sha256:partial",
        verified_operations={ReadOnlyTransportOperation.PROJECT_METADATA},
    )

    report = assess_transport(manifest, evidence)

    assert report.valid is False
    assert "missing operations" in report.issues[0]
