"""Policy-gated URCP execution with deterministic hardening controls."""

from __future__ import annotations

import asyncio
import json
from contextlib import suppress
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
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class ResourceLimits(BaseModel):
    """Per-policy limits evaluated before and after a capability invocation."""

    max_timeout_seconds: float | None = Field(default=None, gt=0)
    max_input_bytes: int | None = Field(default=None, gt=0)
    max_output_bytes: int | None = Field(default=None, gt=0)


class PolicyProvenance(BaseModel):
    """Identifies the policy that authorized or denied an execution request."""

    policy_id: str = Field(default="local-default", min_length=1)
    revision: str = Field(default="1", min_length=1)
    source: str = Field(default="local", min_length=1)
    approved_by: str | None = None


class ExecutionPolicy(BaseModel):
    allow_read_only: bool = True
    allow_simulation: bool = False
    allow_external_side_effects: bool = False
    allow_physical_actuation: bool = False
    allowed_backends: set[str] = Field(default_factory=set)
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits)
    provenance: PolicyProvenance = Field(default_factory=PolicyProvenance)

    def permits(self, descriptor: CapabilityDescriptor) -> bool:
        if descriptor.security_class == SecurityClass.READ_ONLY:
            return self.allow_read_only
        if descriptor.security_class == SecurityClass.SIMULATION:
            return self.allow_simulation
        if descriptor.security_class == SecurityClass.EXTERNAL_SIDE_EFFECT:
            return self.allow_external_side_effects
        return self.allow_physical_actuation


class CancellationToken:
    """Cooperative cancellation state controlled outside the serializable request."""

    def __init__(self) -> None:
        self._event = asyncio.Event()
        self.reason = "cancelled by caller"

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def cancel(self, reason: str = "cancelled by caller") -> None:
        self.reason = reason
        self._event.set()

    async def wait(self) -> None:
        await self._event.wait()


class ExecutionRequest(BaseModel):
    capability_id: str
    version: str | None = None
    backend: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    policy: ExecutionPolicy = Field(default_factory=ExecutionPolicy)
    actor: str = "mirage"
    timeout_seconds: float | None = Field(default=None, gt=0)


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

    async def execute(
        self,
        descriptor: CapabilityDescriptor,
        inputs: dict[str, Any],
        cancellation: CancellationToken | None = None,
    ) -> dict[str, Any]: ...


class LocalSimulationBackend:
    name = "local"

    async def execute(
        self,
        descriptor: CapabilityDescriptor,
        inputs: dict[str, Any],
        cancellation: CancellationToken | None = None,
    ) -> dict[str, Any]:
        if cancellation and cancellation.cancelled:
            raise asyncio.CancelledError(cancellation.reason)
        return {"mode": "deterministic-local", "capability": descriptor.capability_id, "inputs": inputs}


class CoppeliaSimBackend:
    """Explicit unavailable execution boundary, never a simulator control adapter."""

    name = "coppeliasim"

    async def execute(
        self,
        descriptor: CapabilityDescriptor,
        inputs: dict[str, Any],
        cancellation: CancellationToken | None = None,
    ) -> dict[str, Any]:
        raise RuntimeError("CoppeliaSim adapter is not configured; no simulator support is claimed")


def _payload_size(payload: dict[str, Any]) -> int:
    return len(json.dumps(payload, default=str, sort_keys=True, separators=(",", ":")).encode("utf-8"))


class CapabilityExecutor:
    def __init__(self, registry: CapabilityRegistry, backends: dict[str, CapabilityBackend] | None = None, ledger: Any = None) -> None:
        self.registry = registry
        self.backends = backends or {"local": LocalSimulationBackend(), "coppeliasim": CoppeliaSimBackend()}
        self.ledger = ledger

    def _metadata(self, request: ExecutionRequest, **extra: Any) -> dict[str, Any]:
        return {"policy_provenance": request.policy.provenance.model_dump(mode="json"), "resource_limits": request.policy.resource_limits.model_dump(mode="json"), **extra}

    def _result(
        self,
        request: ExecutionRequest,
        descriptor: CapabilityDescriptor,
        status: ExecutionStatus,
        message: str,
        outputs: dict[str, Any] | None = None,
        **extra: Any,
    ) -> ExecutionResult:
        return ExecutionResult(
            status=status,
            capability_id=descriptor.capability_id,
            version=descriptor.version,
            backend=request.backend,
            message=message,
            outputs=outputs or {},
            metadata=self._metadata(request, **extra),
        )

    def _record(self, request: ExecutionRequest, result: ExecutionResult) -> ExecutionResult:
        if self.ledger is not None:
            from .ledger import ExecutionAuditRecord

            self.ledger.append(ExecutionAuditRecord.from_execution(request, result))
        return result

    def _preflight(self, request: ExecutionRequest, descriptor: CapabilityDescriptor, cancellation: CancellationToken) -> ExecutionResult | None:
        if cancellation.cancelled:
            return self._result(request, descriptor, ExecutionStatus.CANCELLED, cancellation.reason)
        if not request.policy.permits(descriptor):
            return self._result(request, descriptor, ExecutionStatus.DENIED, "execution denied by policy")
        if request.policy.allowed_backends and request.backend not in request.policy.allowed_backends:
            return self._result(request, descriptor, ExecutionStatus.DENIED, "backend denied by policy")
        if request.backend not in descriptor.compatible_backends and request.backend != "local":
            return self._result(request, descriptor, ExecutionStatus.UNAVAILABLE, "backend is not compatible with capability")
        limits = request.policy.resource_limits
        if limits.max_input_bytes is not None and _payload_size(request.inputs) > limits.max_input_bytes:
            return self._result(request, descriptor, ExecutionStatus.DENIED, "input exceeds policy resource limit")
        if limits.max_timeout_seconds is not None and request.timeout_seconds is not None and request.timeout_seconds > limits.max_timeout_seconds:
            return self._result(request, descriptor, ExecutionStatus.DENIED, "requested timeout exceeds policy resource limit")
        return None

    async def execute(self, request: ExecutionRequest, cancellation: CancellationToken | None = None) -> ExecutionResult:
        descriptor = self.registry.get(request.capability_id, request.version)
        cancellation = cancellation or CancellationToken()
        denied = self._preflight(request, descriptor, cancellation)
        if denied is not None:
            return self._record(request, denied)
        backend = self.backends.get(request.backend)
        if backend is None:
            return self._record(request, self._result(request, descriptor, ExecutionStatus.UNAVAILABLE, "backend is not registered"))

        execution_task = asyncio.create_task(backend.execute(descriptor, request.inputs, cancellation))
        cancellation_task = asyncio.create_task(cancellation.wait())
        limits = request.policy.resource_limits
        timeout = request.timeout_seconds or limits.max_timeout_seconds
        done, _ = await asyncio.wait({execution_task, cancellation_task}, timeout=timeout, return_when=asyncio.FIRST_COMPLETED)

        if execution_task in done:
            cancellation_task.cancel()
            with suppress(asyncio.CancelledError):
                await cancellation_task
            try:
                outputs = execution_task.result()
            except asyncio.CancelledError:
                return self._record(request, self._result(request, descriptor, ExecutionStatus.CANCELLED, cancellation.reason))
            except RuntimeError as exc:
                return self._record(request, self._result(request, descriptor, ExecutionStatus.UNAVAILABLE, str(exc)))
            except Exception as exc:
                return self._record(request, self._result(request, descriptor, ExecutionStatus.FAILED, str(exc)))
            if limits.max_output_bytes is not None and _payload_size(outputs) > limits.max_output_bytes:
                return self._record(request, self._result(request, descriptor, ExecutionStatus.FAILED, "output exceeds policy resource limit"))
            return self._record(request, self._result(request, descriptor, ExecutionStatus.SUCCEEDED, "execution completed", outputs=outputs))

        if cancellation_task in done:
            execution_task.cancel()
            with suppress(asyncio.CancelledError):
                await execution_task
            return self._record(request, self._result(request, descriptor, ExecutionStatus.CANCELLED, cancellation.reason))

        cancellation.cancel("execution timed out")
        execution_task.cancel()
        cancellation_task.cancel()
        with suppress(asyncio.CancelledError):
            await execution_task
        with suppress(asyncio.CancelledError):
            await cancellation_task
        return self._record(request, self._result(request, descriptor, ExecutionStatus.TIMED_OUT, "execution timed out", timeout_seconds=timeout))
