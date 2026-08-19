from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SecurityClass(StrEnum):
    READ_ONLY = "read_only"
    SIMULATION = "simulation"
    EXTERNAL_SIDE_EFFECT = "external_side_effect"
    PHYSICAL_ACTUATION = "physical_actuation"


class CapabilityDescriptor(BaseModel):
    model_config = ConfigDict(extra="allow")
    capability_id: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_.-]*$")
    version: str = Field(min_length=1)
    description: str = Field(min_length=1)
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    preconditions: list[str] = Field(default_factory=list)
    postconditions: list[str] = Field(default_factory=list)
    resource_requirements: dict[str, Any] = Field(default_factory=dict)
    side_effects: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    compatible_backends: list[str] = Field(default_factory=list)
    deterministic: bool = True
    streaming: bool = False
    cancellable: bool = True
    security_class: SecurityClass = SecurityClass.READ_ONLY


class CapabilityRegistry:
    def __init__(self, descriptors: list[CapabilityDescriptor] | None = None) -> None:
        self._descriptors: dict[tuple[str, str], CapabilityDescriptor] = {}
        for descriptor in descriptors or []:
            self.register(descriptor)

    def register(self, descriptor: CapabilityDescriptor) -> None:
        key = (descriptor.capability_id, descriptor.version)
        if key in self._descriptors:
            raise ValueError(f"duplicate capability: {descriptor.capability_id}@{descriptor.version}")
        self._descriptors[key] = descriptor

    def get(self, capability_id: str, version: str | None = None) -> CapabilityDescriptor:
        matches = [descriptor for (name, _), descriptor in self._descriptors.items() if name == capability_id]
        if version is not None:
            try:
                return self._descriptors[(capability_id, version)]
            except KeyError as exc:
                raise KeyError(f"capability not found: {capability_id}@{version}") from exc
        if not matches:
            raise KeyError(f"capability not found: {capability_id}")
        if len(matches) > 1:
            raise KeyError(f"capability version is required: {capability_id}")
        return matches[0]

    def list(self, backend: str | None = None, security_class: SecurityClass | None = None) -> list[CapabilityDescriptor]:
        values = list(self._descriptors.values())
        if backend is not None:
            values = [item for item in values if backend in item.compatible_backends]
        if security_class is not None:
            values = [item for item in values if item.security_class == security_class]
        return sorted(values, key=lambda item: (item.capability_id, item.version))

    def as_dict(self) -> dict[str, Any]:
        return {f"{item.capability_id}@{item.version}": item.model_dump(mode="json") for item in self.list()}


def default_registry() -> CapabilityRegistry:
    return CapabilityRegistry([
        CapabilityDescriptor(
            capability_id="inspect_model",
            version="0.1",
            description="Inspect a validated engineering model.",
            compatible_backends=["generic"],
            security_class=SecurityClass.READ_ONLY,
        ),
        CapabilityDescriptor(
            capability_id="validate_eir",
            version="0.1",
            description="Validate an EIR document before downstream work.",
            compatible_backends=["generic"],
            security_class=SecurityClass.READ_ONLY,
        ),
        CapabilityDescriptor(
            capability_id="generate_urdf",
            version="0.1",
            description="Generate a URDF artifact from validated robot semantics.",
            compatible_backends=["generic"],
            security_class=SecurityClass.READ_ONLY,
        ),
        CapabilityDescriptor(
            capability_id="run_simulation",
            version="0.1",
            description="Run a simulation through a verified simulator adapter.",
            compatible_backends=["mujoco", "gazebo", "coppeliasim", "webots", "pybullet"],
            security_class=SecurityClass.SIMULATION,
            deterministic=False,
            resource_requirements={"requires": "simulator_adapter"},
        ),
        CapabilityDescriptor(
            capability_id="inspect_simulator_state",
            version="0.1",
            description="Read simulator project metadata and a bounded state snapshot without control.",
            compatible_backends=["fixture", "coppeliasim"],
            security_class=SecurityClass.READ_ONLY,
            deterministic=False,
            resource_requirements={"requires": "verified_read_only_simulator_transport"},
            postconditions=["no simulator control operation is attempted"],
        ),
        CapabilityDescriptor(
            capability_id="review_goal_workflow",
            version="0.1",
            description="Revalidate a bounded goal-to-evaluate workflow for human review without execution.",
            compatible_backends=["generic"],
            security_class=SecurityClass.READ_ONLY,
            postconditions=["workflow remains non-executing", "human approval remains required"],
        ),
        CapabilityDescriptor(
            capability_id="assess_workflow_evidence",
            version="0.1",
            description="Assess declared workflow evidence for human review without evaluating or executing engineering work.",
            compatible_backends=["generic"],
            security_class=SecurityClass.READ_ONLY,
            postconditions=["evidence remains review-only", "human approval remains required"],
        ),
    ])
