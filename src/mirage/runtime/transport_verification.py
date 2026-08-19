"""Read-only simulator transport manifests and evidence contracts.

These types verify a declared transport contract and never open a socket or
invoke a simulator API. A verified fixture contract is not evidence that a
real simulator endpoint is safe or available.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class ReadOnlyTransportOperation(StrEnum):
    PROJECT_METADATA = "project_metadata"
    STATE_SNAPSHOT = "state_snapshot"


class TransportVerificationStatus(StrEnum):
    UNVERIFIED = "unverified"
    FIXTURE_VERIFIED = "fixture_verified"
    LIVE_VERIFIED = "live_verified"


CONTROL_OPERATIONS = frozenset(
    {
        "load_scene",
        "start_simulation",
        "pause_simulation",
        "stop_simulation",
        "step_simulation",
        "reset_simulation",
        "set_object_state",
        "write_scene",
        "physical_actuation",
    }
)


class ReadOnlyTransportManifest(BaseModel):
    """Versioned operations and prohibited controls for one adapter transport."""

    manifest_id: str = Field(min_length=1)
    adapter: str = Field(min_length=1)
    protocol: str = Field(min_length=1)
    endpoint_scheme: str = Field(min_length=1)
    simulator_version: str = Field(min_length=1)
    state_semantics_revision: str = Field(min_length=1)
    allowed_operations: set[ReadOnlyTransportOperation] = Field(min_length=1)
    prohibited_operations: set[str] = Field(default_factory=lambda: set(CONTROL_OPERATIONS))
    verification_status: TransportVerificationStatus = TransportVerificationStatus.UNVERIFIED
    notes: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_complete_control_prohibition(self) -> ReadOnlyTransportManifest:
        missing = CONTROL_OPERATIONS - self.prohibited_operations
        if missing:
            raise ValueError(f"transport manifest must prohibit control operations: {', '.join(sorted(missing))}")
        return self


class TransportVerificationEvidence(BaseModel):
    """Evidence attached to a local fixture or later verified live transport."""

    evidence_id: str = Field(min_length=1)
    manifest_id: str = Field(min_length=1)
    status: TransportVerificationStatus = TransportVerificationStatus.UNVERIFIED
    verified_operations: set[ReadOnlyTransportOperation] = Field(default_factory=set)
    fixture_digest: str | None = None
    verifier: str | None = None
    observed_simulator_version: str | None = None
    observations: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_fixture_evidence(self) -> TransportVerificationEvidence:
        if self.status == TransportVerificationStatus.FIXTURE_VERIFIED and not self.fixture_digest:
            raise ValueError("fixture-verified transport evidence requires a fixture digest")
        if self.status == TransportVerificationStatus.LIVE_VERIFIED and not self.observed_simulator_version:
            raise ValueError("live-verified transport evidence requires an observed simulator version")
        return self


class TransportVerificationReport(BaseModel):
    manifest_id: str
    adapter: str
    status: TransportVerificationStatus
    valid: bool
    verified_operations: set[ReadOnlyTransportOperation] = Field(default_factory=set)
    issues: list[str] = Field(default_factory=list)


def assess_transport(manifest: ReadOnlyTransportManifest, evidence: TransportVerificationEvidence | None = None) -> TransportVerificationReport:
    """Assess evidence without connecting to a simulator or running a transport."""

    if evidence is None:
        return TransportVerificationReport(
            manifest_id=manifest.manifest_id,
            adapter=manifest.adapter,
            status=TransportVerificationStatus.UNVERIFIED,
            valid=False,
            issues=["transport evidence is not available"],
        )
    issues: list[str] = []
    if evidence.manifest_id != manifest.manifest_id:
        issues.append("transport evidence does not match the manifest")
    missing_operations = manifest.allowed_operations - evidence.verified_operations
    if missing_operations:
        issues.append(f"transport evidence is missing operations: {', '.join(sorted(item.value for item in missing_operations))}")
    if evidence.status == TransportVerificationStatus.UNVERIFIED:
        issues.append("transport evidence is unverified")
    return TransportVerificationReport(
        manifest_id=manifest.manifest_id,
        adapter=manifest.adapter,
        status=evidence.status,
        valid=not issues,
        verified_operations=evidence.verified_operations,
        issues=issues,
    )


def coppeliasim_zmq_read_only_manifest() -> ReadOnlyTransportManifest:
    """Return the non-connecting CoppeliaSim ZeroMQ reference contract.

    The ZeroMQ API supports control operations, so this manifest remains
    unverified until an adapter can prove an allow-listed read-only surface.
    """

    return ReadOnlyTransportManifest(
        manifest_id="coppeliasim-zmq-read-only-reference-v1",
        adapter="coppeliasim",
        protocol="zeromq-remote-api",
        endpoint_scheme="tcp",
        simulator_version="unverified",
        state_semantics_revision="unverified",
        allowed_operations={ReadOnlyTransportOperation.PROJECT_METADATA, ReadOnlyTransportOperation.STATE_SNAPSHOT},
        verification_status=TransportVerificationStatus.UNVERIFIED,
        notes={
            "connection": "not attempted",
            "control_surface": "prohibited by manifest",
        },
    )
