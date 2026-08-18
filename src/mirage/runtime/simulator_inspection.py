"""Inspection-only simulator adapter contracts with no control surface."""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, Field


class InspectionStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class SimulatorInspection(BaseModel):
    backend: str
    status: InspectionStatus
    endpoint_configured: bool
    control_available: bool = False
    observations: dict[str, str] = Field(default_factory=dict)
    message: str


class SimulatorInspectionBackend(Protocol):
    name: str

    async def inspect(self) -> SimulatorInspection: ...


class CoppeliaSimInspectionBackend:
    """Safe non-connecting boundary for future CoppeliaSim state inspection."""

    name = "coppeliasim"

    def __init__(self, endpoint: str | None = None) -> None:
        self.endpoint = endpoint

    async def inspect(self) -> SimulatorInspection:
        return SimulatorInspection(
            backend=self.name,
            status=InspectionStatus.UNAVAILABLE,
            endpoint_configured=bool(self.endpoint),
            observations={"mode": "inspection-only", "transport": "unverified"},
            message="CoppeliaSim inspection transport is unverified; no connection or control operation was attempted",
        )


def default_inspection_backends(endpoint: str | None = None) -> dict[str, SimulatorInspectionBackend]:
    return {"coppeliasim": CoppeliaSimInspectionBackend(endpoint=endpoint)}
