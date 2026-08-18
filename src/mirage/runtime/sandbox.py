"""Declarative backend sandbox envelopes and deterministic capability assessment."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class SandboxAssessmentStatus(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
    DECLARATIVE_ONLY = "declarative_only"


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
