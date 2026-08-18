from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from mirage.eir import EIRDocument


class ESGEventType(StrEnum):
    CREATED = "created"
    CONTEXT_INDEXED = "context_indexed"
    NODE_ADDED = "node_added"
    NODE_UPDATED = "node_updated"
    RELATIONSHIP_ADDED = "relationship_added"
    VALIDATED = "validated"
    DECISION_RECORDED = "decision_recorded"


class ESGEvent(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(min_length=1)
    type: ESGEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor: str = Field(min_length=1)
    eir_refs: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class EngineeringStateGraph(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_id: str = Field(min_length=1)
    revision: int = Field(default=0, ge=0)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    eir: EIRDocument
    events: list[ESGEvent] = Field(default_factory=list)

    def append_event(self, event: ESGEvent) -> EngineeringStateGraph:
        if any(existing.id == event.id for existing in self.events):
            raise ValueError(f"duplicate ESG event ID: {event.id}")
        self.events.append(event)
        self.revision += 1
        self.updated_at = event.timestamp
        return self

    def snapshot(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.model_dump_json(indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> EngineeringStateGraph:
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))
