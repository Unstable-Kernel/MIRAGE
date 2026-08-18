from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .execution import ExecutionPolicy
    from .urcp import CapabilityRegistry


class CheckpointCapabilityRequirement(BaseModel):
    capability_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    backend: str | None = None


class CheckpointRevalidationIssue(BaseModel):
    code: str
    message: str


class CheckpointRevalidationResult(BaseModel):
    valid: bool
    workflow_id: str
    checkpoint_revision: int
    issues: list[CheckpointRevalidationIssue] = Field(default_factory=list)
    policy_provenance: dict[str, Any] = Field(default_factory=dict)


class WorkflowCheckpoint(BaseModel):
    workflow_id: str = Field(min_length=1)
    revision: int = Field(default=0, ge=0)
    stage: str = Field(min_length=1)
    state: dict[str, Any] = Field(default_factory=dict)
    execution_ids: list[str] = Field(default_factory=list)
    esg_project_id: str | None = None
    required_capabilities: list[CheckpointCapabilityRequirement] = Field(default_factory=list)
    policy_provenance: dict[str, Any] = Field(default_factory=dict)
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

    def revalidate(self, registry: CapabilityRegistry, policy: ExecutionPolicy) -> CheckpointRevalidationResult:
        """Validate a checkpoint for manual review only. This method never resumes work."""

        issues: list[CheckpointRevalidationIssue] = []
        current_provenance = policy.provenance.model_dump(mode="json")
        if self.policy_provenance and self.policy_provenance != current_provenance:
            issues.append(CheckpointRevalidationIssue(code="policy_provenance_mismatch", message="checkpoint policy provenance differs from the active policy"))
        for requirement in self.required_capabilities:
            try:
                descriptor = registry.get(requirement.capability_id, requirement.version)
            except KeyError:
                issues.append(CheckpointRevalidationIssue(code="capability_missing", message=f"required capability is unavailable: {requirement.capability_id}@{requirement.version}"))
                continue
            if not policy.permits(descriptor):
                issues.append(CheckpointRevalidationIssue(code="capability_denied", message=f"active policy denies required capability: {requirement.capability_id}@{requirement.version}"))
            if requirement.backend and policy.allowed_backends and requirement.backend not in policy.allowed_backends:
                issues.append(CheckpointRevalidationIssue(code="backend_denied", message=f"active policy denies required backend: {requirement.backend}"))
        return CheckpointRevalidationResult(
            valid=not issues,
            workflow_id=self.workflow_id,
            checkpoint_revision=self.revision,
            issues=issues,
            policy_provenance=current_provenance,
        )
