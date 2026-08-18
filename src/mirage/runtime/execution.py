from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel, Field

from .urcp import CapabilityDescriptor, CapabilityRegistry, SecurityClass


class ExecutionStatus(StrEnum):
    SUCCEEDED = "succeeded"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"


class ExecutionPolicy(BaseModel):
    allow_read_only: bool = True
    allow_simulation: bool = False
    allow_external_side_effects: bool = False
    allow_physical_actuation: bool = False
    allowed_backends: set[str] = Field(default_factory=set)

    def permits(self, descriptor: CapabilityDescriptor) -> bool:
        if descriptor.security_class == SecurityClass.READ_ONLY:
            return self.allow_read_only
        if descriptor.security_class == SecurityClass.SIMULATION:
            return self.allow_simulation
        if descriptor.security_class == SecurityClass.EXTERNAL_SIDE_EFFECT:
            return self.allow_external_side_effects
        return self.allow_physical_actuation


class ExecutionRequest(BaseModel):
    capability_id: str
    version: str | None = None
    backend: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    policy: ExecutionPolicy = Field(default_factory=ExecutionPolicy)
    actor: str = "mirage"


class ExecutionResult(BaseModel):
    status: ExecutionStatus
    capability_id: str
    version: str
    backend: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    outputs: dict[str, Any] = Field(default_factory=dict)
    message: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class CapabilityBackend(Protocol):
    name: str

    async def execute(self, descriptor: CapabilityDescriptor, inputs: dict[str, Any]) -> dict[str, Any]: ...


class LocalSimulationBackend:
    name = "local"

    async def execute(self, descriptor: CapabilityDescriptor, inputs: dict[str, Any]) -> dict[str, Any]:
        return {"mode": "deterministic-local", "capability": descriptor.capability_id, "inputs": inputs}


class CoppeliaSimBackend:
    name = "coppeliasim"

    async def execute(self, descriptor: CapabilityDescriptor, inputs: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("CoppeliaSim adapter is not configured; no simulator support is claimed")


class CapabilityExecutor:
    def __init__(self, registry: CapabilityRegistry, backends: dict[str, CapabilityBackend] | None = None) -> None:
        self.registry = registry
        self.backends = backends or {"local": LocalSimulationBackend(), "coppeliasim": CoppeliaSimBackend()}

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        descriptor = self.registry.get(request.capability_id, request.version)
        if not request.policy.permits(descriptor):
            return ExecutionResult(status=ExecutionStatus.DENIED, capability_id=descriptor.capability_id, version=descriptor.version, backend=request.backend, message="execution denied by policy")
        if request.policy.allowed_backends and request.backend not in request.policy.allowed_backends:
            return ExecutionResult(status=ExecutionStatus.DENIED, capability_id=descriptor.capability_id, version=descriptor.version, backend=request.backend, message="backend denied by policy")
        if request.backend not in descriptor.compatible_backends and request.backend != "local":
            return ExecutionResult(status=ExecutionStatus.UNAVAILABLE, capability_id=descriptor.capability_id, version=descriptor.version, backend=request.backend, message="backend is not compatible with capability")
        backend = self.backends.get(request.backend)
        if backend is None:
            return ExecutionResult(status=ExecutionStatus.UNAVAILABLE, capability_id=descriptor.capability_id, version=descriptor.version, backend=request.backend, message="backend is not registered")
        try:
            outputs = await backend.execute(descriptor, request.inputs)
        except RuntimeError as exc:
            return ExecutionResult(status=ExecutionStatus.UNAVAILABLE, capability_id=descriptor.capability_id, version=descriptor.version, backend=request.backend, message=str(exc))
        return ExecutionResult(status=ExecutionStatus.SUCCEEDED, capability_id=descriptor.capability_id, version=descriptor.version, backend=request.backend, outputs=outputs, message="execution completed")
