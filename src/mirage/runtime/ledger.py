from __future__ import annotations

import json
import re
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .execution import ExecutionRequest, ExecutionResult

_SECRET_KEY = re.compile(r"(key|token|secret|password|credential)", re.IGNORECASE)


def redact(value: Any, key: str = "") -> Any:
    if _SECRET_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {name: redact(item, name) for name, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


class ExecutionAuditRecord(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    actor: str
    capability_id: str
    version: str | None = None
    backend: str
    status: str
    started_at: datetime
    completed_at: datetime
    policy: dict[str, Any] = Field(default_factory=dict)
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    message: str = ""
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_execution(cls, request: ExecutionRequest, result: ExecutionResult) -> ExecutionAuditRecord:
        return cls(
            actor=request.actor,
            capability_id=request.capability_id,
            version=result.version,
            backend=request.backend,
            status=result.status.value,
            started_at=result.started_at,
            completed_at=result.completed_at,
            policy=redact(request.policy.model_dump()),
            inputs=redact(request.inputs),
            outputs=redact(result.outputs),
            message=result.message,
        )


class ExecutionLedger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, record: ExecutionAuditRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(record.model_dump_json() + "\n")

    def records(self) -> Iterable[ExecutionAuditRecord]:
        if not self.path.exists():
            return []
        return [ExecutionAuditRecord.model_validate(json.loads(line)) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def get(self, request_id: str) -> ExecutionAuditRecord:
        for record in self.records():
            if record.request_id == request_id:
                return record
        raise KeyError(f"execution record not found: {request_id}")
