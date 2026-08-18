from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class WorkflowCheckpoint(BaseModel):
    workflow_id: str = Field(min_length=1)
    revision: int = Field(default=0, ge=0)
    stage: str = Field(min_length=1)
    state: dict[str, Any] = Field(default_factory=dict)
    execution_ids: list[str] = Field(default_factory=list)
    esg_project_id: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.model_dump_json(indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> WorkflowCheckpoint:
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))

    def advance(self, stage: str, state: dict[str, Any] | None = None, execution_id: str | None = None) -> WorkflowCheckpoint:
        self.revision += 1
        self.stage = stage
        if state is not None:
            self.state = state
        if execution_id is not None:
            self.execution_ids.append(execution_id)
        self.updated_at = datetime.now(UTC)
        return self
