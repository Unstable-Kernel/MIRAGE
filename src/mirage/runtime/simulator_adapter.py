"""Verified read-only simulator metadata and state extraction contracts.

This module intentionally has no simulator control operations. It exposes only
project metadata and state snapshot reads, with policy and sandbox assessment
recorded in every result.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field

from .execution import CancellationToken, ExecutionPolicy
from .sandbox import BackendSandboxCapabilities, SandboxAssessment, assess_sandbox


class ReadOnlySimulatorStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DENIED = "denied"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"
    FAILED = "failed"


class SimulatorProjectMetadata(BaseModel):
    """Static project attributes that can be returned without changing a simulator."""

    project_id: str = Field(min_length=1)
    project_name: str = Field(min_length=1)
    simulator: str = Field(min_length=1)
    simulator_version: str = Field(min_length=1)
    scene_name: str = Field(min_length=1)
    scene_path: str | None = None
    model_count: int = Field(ge=0)
    object_count: int = Field(ge=0)
    observations: dict[str, str] = Field(default_factory=dict)


class SimulatorObjectState(BaseModel):
    """One observed object's pose and velocity in a declared world frame."""

    object_id: str = Field(min_length=1)
    object_name: str = Field(min_length=1)
    object_type: str = Field(min_length=1)
    position_m: tuple[float, float, float]
    orientation_rpy_rad: tuple[float, float, float]
    linear_velocity_mps: tuple[float, float, float] = (0.0, 0.0, 0.0)


class SimulatorStateSnapshot(BaseModel):
    """A bounded read-only state observation with no stepping or mutation semantics."""

    snapshot_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    simulation_time_seconds: float = Field(ge=0)
    world_frame: str = Field(default="world", min_length=1)
    objects: list[SimulatorObjectState] = Field(default_factory=list)
    observations: dict[str, str] = Field(default_factory=dict)


class ReadOnlySimulatorResult(BaseModel):
    """A policy-assessed read result that never exposes simulator control."""

    backend: str
    operation: str
    status: ReadOnlySimulatorStatus
    message: str
    sandbox_assessment: SandboxAssessment
    metadata: SimulatorProjectMetadata | None = None
    snapshot: SimulatorStateSnapshot | None = None
    transport_verified: bool = False
    control_available: bool = False
    observations: dict[str, str] = Field(default_factory=dict)


class ReadOnlySimulatorAdapter(Protocol):
    """Narrow adapter protocol with no start, stop, step, or write operation."""

    name: str
    sandbox_capabilities: BackendSandboxCapabilities

    async def read_project_metadata(
        self,
        policy: ExecutionPolicy | None = None,
        timeout_seconds: float | None = None,
        cancellation: CancellationToken | None = None,
    ) -> ReadOnlySimulatorResult: ...

    async def read_state_snapshot(
        self,
        policy: ExecutionPolicy | None = None,
        timeout_seconds: float | None = None,
        cancellation: CancellationToken | None = None,
    ) -> ReadOnlySimulatorResult: ...


class SimulatorTransportUnavailable(RuntimeError):
    """Raised internally when a read-only transport has not been verified."""


def _payload_size(payload: BaseModel) -> int:
    return len(json.dumps(payload.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode("utf-8"))


class _ReadOnlyAdapterBase:
    name = "read-only"
    transport_verified = False
    sandbox_capabilities = BackendSandboxCapabilities(backend=name)

    def _assessment(self, policy: ExecutionPolicy) -> SandboxAssessment:
        return assess_sandbox(policy.sandbox, self.sandbox_capabilities)

    def _result(
        self,
        operation: str,
        status: ReadOnlySimulatorStatus,
        message: str,
        assessment: SandboxAssessment,
        *,
        metadata: SimulatorProjectMetadata | None = None,
        snapshot: SimulatorStateSnapshot | None = None,
        observations: dict[str, str] | None = None,
    ) -> ReadOnlySimulatorResult:
        return ReadOnlySimulatorResult(
            backend=self.name,
            operation=operation,
            status=status,
            message=message,
            sandbox_assessment=assessment,
            metadata=metadata,
            snapshot=snapshot,
            transport_verified=self.transport_verified,
            observations=observations or {},
        )

    def _preflight(
        self,
        operation: str,
        policy: ExecutionPolicy,
        timeout_seconds: float | None,
        cancellation: CancellationToken,
    ) -> tuple[SandboxAssessment, ReadOnlySimulatorResult | None, float | None]:
        assessment = self._assessment(policy)
        if cancellation.cancelled:
            return assessment, self._result(operation, ReadOnlySimulatorStatus.CANCELLED, cancellation.reason, assessment), None
        if not policy.allow_read_only:
            return assessment, self._result(operation, ReadOnlySimulatorStatus.DENIED, "read-only simulator access denied by policy", assessment), None
        if policy.allowed_backends and self.name not in policy.allowed_backends:
            return assessment, self._result(operation, ReadOnlySimulatorStatus.DENIED, "backend denied by policy", assessment), None
        if assessment.status.value == "denied":
            return assessment, self._result(operation, ReadOnlySimulatorStatus.DENIED, assessment.message, assessment), None
        limit = policy.resource_limits.max_timeout_seconds
        if limit is not None and timeout_seconds is not None and timeout_seconds > limit:
            return assessment, self._result(operation, ReadOnlySimulatorStatus.DENIED, "requested timeout exceeds policy resource limit", assessment), None
        return assessment, None, timeout_seconds or limit

    async def _read(
        self,
        operation: str,
        reader: Callable[[], Awaitable[SimulatorProjectMetadata | SimulatorStateSnapshot]],
        policy: ExecutionPolicy | None,
        timeout_seconds: float | None,
        cancellation: CancellationToken | None,
    ) -> ReadOnlySimulatorResult:
        active_policy = policy or ExecutionPolicy()
        token = cancellation or CancellationToken()
        assessment, preflight, timeout = self._preflight(operation, active_policy, timeout_seconds, token)
        if preflight is not None:
            return preflight

        read_task = asyncio.create_task(reader())
        cancellation_task = asyncio.create_task(token.wait())
        done, _ = await asyncio.wait({read_task, cancellation_task}, timeout=timeout, return_when=asyncio.FIRST_COMPLETED)

        if read_task in done:
            cancellation_task.cancel()
            try:
                await cancellation_task
            except asyncio.CancelledError:
                pass
            try:
                value = read_task.result()
            except SimulatorTransportUnavailable as exc:
                return self._result(operation, ReadOnlySimulatorStatus.UNAVAILABLE, str(exc), assessment)
            except asyncio.CancelledError:
                return self._result(operation, ReadOnlySimulatorStatus.CANCELLED, token.reason, assessment)
            except Exception as exc:
                return self._result(operation, ReadOnlySimulatorStatus.FAILED, str(exc), assessment)

            max_output_bytes = active_policy.resource_limits.max_output_bytes
            if max_output_bytes is not None and _payload_size(value) > max_output_bytes:
                return self._result(operation, ReadOnlySimulatorStatus.DENIED, "output exceeds policy resource limit", assessment)
            if isinstance(value, SimulatorProjectMetadata):
                return self._result(operation, ReadOnlySimulatorStatus.AVAILABLE, "read-only project metadata extracted", assessment, metadata=value)
            return self._result(operation, ReadOnlySimulatorStatus.AVAILABLE, "read-only simulator state extracted", assessment, snapshot=value)

        read_task.cancel()
        cancellation_task.cancel()
        for task in (read_task, cancellation_task):
            try:
                await task
            except asyncio.CancelledError:
                pass
        if token.cancelled:
            return self._result(operation, ReadOnlySimulatorStatus.CANCELLED, token.reason, assessment)
        token.cancel("read-only simulator extraction timed out")
        return self._result(operation, ReadOnlySimulatorStatus.TIMED_OUT, token.reason, assessment)


class FixtureSimulatorAdapter(_ReadOnlyAdapterBase):
    """Deterministic fixture adapter that performs no network or simulator operation."""

    name = "fixture"
    transport_verified = True
    sandbox_capabilities = BackendSandboxCapabilities(backend=name)

    def __init__(self, metadata: SimulatorProjectMetadata, snapshot: SimulatorStateSnapshot) -> None:
        if metadata.project_id != snapshot.project_id:
            raise ValueError("fixture metadata and snapshot project identifiers must match")
        self.metadata = metadata
        self.snapshot = snapshot

    @classmethod
    def from_file(cls, path: Path) -> FixtureSimulatorAdapter:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            metadata=SimulatorProjectMetadata.model_validate(raw["metadata"]),
            snapshot=SimulatorStateSnapshot.model_validate(raw["snapshot"]),
        )

    async def _metadata_source(self) -> SimulatorProjectMetadata:
        return self.metadata.model_copy(deep=True)

    async def _snapshot_source(self) -> SimulatorStateSnapshot:
        return self.snapshot.model_copy(deep=True)

    async def read_project_metadata(
        self,
        policy: ExecutionPolicy | None = None,
        timeout_seconds: float | None = None,
        cancellation: CancellationToken | None = None,
    ) -> ReadOnlySimulatorResult:
        return await self._read("project_metadata", self._metadata_source, policy, timeout_seconds, cancellation)

    async def read_state_snapshot(
        self,
        policy: ExecutionPolicy | None = None,
        timeout_seconds: float | None = None,
        cancellation: CancellationToken | None = None,
    ) -> ReadOnlySimulatorResult:
        return await self._read("state_snapshot", self._snapshot_source, policy, timeout_seconds, cancellation)


class CoppeliaSimReadOnlyAdapter(_ReadOnlyAdapterBase):
    """Unavailable non-connecting CoppeliaSim boundary until a transport is verified."""

    name = "coppeliasim"
    sandbox_capabilities = BackendSandboxCapabilities(backend=name)

    def __init__(self, endpoint: str | None = None) -> None:
        self.endpoint = endpoint

    async def _unverified_transport(self) -> SimulatorProjectMetadata:
        raise SimulatorTransportUnavailable(
            "CoppeliaSim read-only transport is unverified; no connection or control operation was attempted"
        )

    async def _unverified_snapshot_transport(self) -> SimulatorStateSnapshot:
        raise SimulatorTransportUnavailable(
            "CoppeliaSim read-only transport is unverified; no connection or control operation was attempted"
        )

    async def read_project_metadata(
        self,
        policy: ExecutionPolicy | None = None,
        timeout_seconds: float | None = None,
        cancellation: CancellationToken | None = None,
    ) -> ReadOnlySimulatorResult:
        result = await self._read("project_metadata", self._unverified_transport, policy, timeout_seconds, cancellation)
        result.observations["endpoint_configured"] = str(bool(self.endpoint)).lower()
        result.observations["transport"] = "unverified"
        return result

    async def read_state_snapshot(
        self,
        policy: ExecutionPolicy | None = None,
        timeout_seconds: float | None = None,
        cancellation: CancellationToken | None = None,
    ) -> ReadOnlySimulatorResult:
        result = await self._read("state_snapshot", self._unverified_snapshot_transport, policy, timeout_seconds, cancellation)
        result.observations["endpoint_configured"] = str(bool(self.endpoint)).lower()
        result.observations["transport"] = "unverified"
        return result
