from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

EIR_VERSION = "0.1"


class NodeType(StrEnum):
    ROBOT = "Robot"
    LINK = "Link"
    JOINT = "Joint"
    SENSOR = "Sensor"
    ACTUATOR = "Actuator"
    CONTROLLER = "Controller"
    OBJECTIVE = "Objective"
    CONSTRAINT = "Constraint"
    METRIC = "Metric"
    EXPERIMENT = "Experiment"
    ASSUMPTION = "Assumption"
    REQUIREMENT = "Requirement"


class RelationshipType(StrEnum):
    CONTROLS = "controls"
    SENSES = "senses"
    DERIVES_FROM = "derives_from"
    DEPENDS_ON = "depends_on"
    VALIDATES = "validates"
    CONTRADICTS = "contradicts"
    IMPLEMENTS = "implements"
    GENERATED_BY = "generated_by"


class ValidationStatus(StrEnum):
    UNKNOWN = "unknown"
    VALID = "valid"
    INVALID = "invalid"
    PARTIAL = "partial"


class SourceRef(BaseModel):
    model_config = ConfigDict(extra="allow")
    ref_type: str
    uri: str | None = None
    title: str | None = None
    section: str | None = None
    page: int | None = Field(default=None, ge=1)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class Provenance(BaseModel):
    model_config = ConfigDict(extra="allow")
    source_type: str
    source_path: str | None = None
    source_location: str | None = None
    extraction_method: str = "manual"
    extractor_version: str = "mirage-0.1"
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EIRNode(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(min_length=1)
    type: NodeType
    schema_version: str = EIR_VERSION
    provenance: Provenance
    source_refs: list[SourceRef] = Field(default_factory=list)
    validation_status: ValidationStatus = ValidationStatus.UNKNOWN
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EIRRelationship(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(min_length=1)
    type: RelationshipType
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    provenance: Provenance
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    properties: dict[str, Any] = Field(default_factory=dict)


class EIRDocument(BaseModel):
    model_config = ConfigDict(extra="allow")
    eir_version: str = EIR_VERSION
    id: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provenance: Provenance
    nodes: list[EIRNode] = Field(default_factory=list)
    relationships: list[EIRRelationship] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("eir_version")
    @classmethod
    def supported_version(cls, value: str) -> str:
        if value != EIR_VERSION:
            raise ValueError(f"unsupported EIR version: {value}")
        return value
