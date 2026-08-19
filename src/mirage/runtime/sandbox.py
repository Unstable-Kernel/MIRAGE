"""Declarative backend sandbox envelopes and deterministic capability assessment."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class SandboxAssessmentStatus(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
    DECLARATIVE_ONLY = "declarative_only"


class SandboxEvidenceStatus(StrEnum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"


class SandboxControl(StrEnum):
    CPU_LIMIT = "cpu_limit"
    MEMORY_LIMIT = "memory_limit"
    DISK_LIMIT = "disk_limit"
    PROCESS_LIMIT = "process_limit"
    NETWORK_LIMIT = "network_limit"
    NETWORK_ALLOWLIST = "network_allowlist"
    READ_ONLY_FILESYSTEM = "read_only_filesystem"
    SUBPROCESS_POLICY = "subprocess_policy"


class SandboxEnvelope(BaseModel):
    """Requested backend restrictions that must be verifiably enforceable to be claimed."""

    envelope_id: str = Field(default="local-default", min_length=1)
    revision: str = Field(default="1", min_length=1)
    max_cpu_seconds: float | None = Field(default=None, gt=0)
    max_memory_mb: int | None = Field(default=None, gt=0)
    max_disk_mb: int | None = Field(default=None, gt=0)
    max_processes: int | None = Field(default=None, gt=0)
    max_network_bytes: int | None = Field(default=None, gt=0)
    allowed_network_hosts: set[str] = Field(default_factory=set)
    read_only_filesystem: bool = True
    allow_subprocesses: bool = False

    def requires_os_enforcement(self) -> bool:
        return any(
            value is not None
            for value in (self.max_cpu_seconds, self.max_memory_mb, self.max_disk_mb, self.max_processes, self.max_network_bytes)
        ) or bool(self.allowed_network_hosts) or self.allow_subprocesses or not self.read_only_filesystem


class SandboxEnforcementEvidence(BaseModel):
    """Auditable evidence required before an OS-enforced sandbox is accepted."""

    evidence_id: str = Field(min_length=1)
    backend: str = Field(min_length=1)
    status: SandboxEvidenceStatus = SandboxEvidenceStatus.UNVERIFIED
    verified_controls: set[SandboxControl] = Field(default_factory=set)
    verifier: str | None = None
    environment_fingerprint: str | None = None
    evidence_digest: str | None = None
    observations: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_integrity_for_verified_evidence(self) -> SandboxEnforcementEvidence:
        if self.status == SandboxEvidenceStatus.VERIFIED:
            required = {
                "evidence digest": self.evidence_digest,
                "environment fingerprint": self.environment_fingerprint,
                "verifier": self.verifier,
                "verified controls": self.verified_controls,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise ValueError(f"verified sandbox evidence requires: {', '.join(missing)}")
        return self

    def covers(self, envelope: SandboxEnvelope) -> bool:
        required: set[SandboxControl] = set()
        if envelope.max_cpu_seconds is not None:
            required.add(SandboxControl.CPU_LIMIT)
        if envelope.max_memory_mb is not None:
            required.add(SandboxControl.MEMORY_LIMIT)
        if envelope.max_disk_mb is not None:
            required.add(SandboxControl.DISK_LIMIT)
        if envelope.max_processes is not None:
            required.add(SandboxControl.PROCESS_LIMIT)
        if envelope.max_network_bytes is not None:
            required.add(SandboxControl.NETWORK_LIMIT)
        if envelope.allowed_network_hosts:
            required.add(SandboxControl.NETWORK_ALLOWLIST)
        if envelope.read_only_filesystem:
            required.add(SandboxControl.READ_ONLY_FILESYSTEM)
        if envelope.allow_subprocesses:
            required.add(SandboxControl.SUBPROCESS_POLICY)
        return self.status == SandboxEvidenceStatus.VERIFIED and required <= self.verified_controls


class BackendSandboxCapabilities(BaseModel):
    backend: str
    enforces_cpu_limit: bool = False
    enforces_memory_limit: bool = False
    enforces_disk_limit: bool = False
    enforces_process_limit: bool = False
    enforces_network_limit: bool = False
    enforces_network_allowlist: bool = False
    enforces_read_only_filesystem: bool = False
    enforces_subprocess_policy: bool = False
    enforcement_evidence: SandboxEnforcementEvidence | None = None

    def supports(self, envelope: SandboxEnvelope) -> bool:
        return (
            (envelope.max_cpu_seconds is None or self.enforces_cpu_limit)
            and (envelope.max_memory_mb is None or self.enforces_memory_limit)
            and (envelope.max_disk_mb is None or self.enforces_disk_limit)
            and (envelope.max_processes is None or self.enforces_process_limit)
            and (envelope.max_network_bytes is None or self.enforces_network_limit)
            and (not envelope.allowed_network_hosts or self.enforces_network_allowlist)
            and (not envelope.read_only_filesystem or self.enforces_read_only_filesystem)
            and (not envelope.allow_subprocesses or self.enforces_subprocess_policy)
        )


class SandboxAssessment(BaseModel):
    status: SandboxAssessmentStatus
    backend: str
    envelope_id: str
    envelope_revision: str
    message: str
    capabilities: BackendSandboxCapabilities


def assess_sandbox(envelope: SandboxEnvelope, capabilities: BackendSandboxCapabilities) -> SandboxAssessment:
    """Return a conservative assessment without attempting host-level isolation."""

    if envelope.requires_os_enforcement() and not capabilities.supports(envelope):
        return SandboxAssessment(
            status=SandboxAssessmentStatus.DENIED,
            backend=capabilities.backend,
            envelope_id=envelope.envelope_id,
            envelope_revision=envelope.revision,
            message="backend cannot enforce the requested sandbox envelope",
            capabilities=capabilities,
        )
    if envelope.requires_os_enforcement():
        evidence = capabilities.enforcement_evidence
        if evidence is None or evidence.backend != capabilities.backend:
            return SandboxAssessment(
                status=SandboxAssessmentStatus.DENIED,
                backend=capabilities.backend,
                envelope_id=envelope.envelope_id,
                envelope_revision=envelope.revision,
                message="backend lacks matching verified sandbox enforcement evidence",
                capabilities=capabilities,
            )
        if not evidence.covers(envelope):
            return SandboxAssessment(
                status=SandboxAssessmentStatus.DENIED,
                backend=capabilities.backend,
                envelope_id=envelope.envelope_id,
                envelope_revision=envelope.revision,
                message="sandbox enforcement evidence does not cover the requested envelope",
                capabilities=capabilities,
            )
        return SandboxAssessment(
            status=SandboxAssessmentStatus.ALLOWED,
            backend=capabilities.backend,
            envelope_id=envelope.envelope_id,
            envelope_revision=envelope.revision,
            message="backend has matching verified sandbox enforcement evidence",
            capabilities=capabilities,
        )
    if not envelope.requires_os_enforcement() and not capabilities.supports(envelope):
        return SandboxAssessment(
            status=SandboxAssessmentStatus.DECLARATIVE_ONLY,
            backend=capabilities.backend,
            envelope_id=envelope.envelope_id,
            envelope_revision=envelope.revision,
            message="sandbox envelope is declarative only; no operating-system isolation is claimed",
            capabilities=capabilities,
        )
    return SandboxAssessment(
        status=SandboxAssessmentStatus.ALLOWED,
        backend=capabilities.backend,
        envelope_id=envelope.envelope_id,
        envelope_revision=envelope.revision,
        message="backend reports support for the requested sandbox envelope",
        capabilities=capabilities,
    )
