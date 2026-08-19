"""Bounded, non-executing M4 goal-to-evaluate workflow contracts.

These models turn an engineering goal into a reviewable capability plan. They
never invoke a provider, simulator, backend, or checkpoint resume path.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .checkpoint import CheckpointCapabilityRequirement, CheckpointRevalidationResult, WorkflowCheckpoint
from .execution import ExecutionPolicy
from .urcp import CapabilityRegistry


class GoalWorkflowStatus(StrEnum):
    DRAFT = "draft"
    READY_FOR_REVIEW = "ready_for_review"
    REVALIDATION_FAILED = "revalidation_failed"


class GoalWorkflowStep(BaseModel):
    """A proposed, review-only engineering workflow step."""

    step_id: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    capability: CheckpointCapabilityRequirement
    expected_evidence: list[str] = Field(min_length=1)
    requires_human_approval: bool = True


class GoalEvaluationCriterion(BaseModel):
    criterion_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    evidence_required: bool = True


class GoalWorkflowReview(BaseModel):
    workflow_id: str
    status: GoalWorkflowStatus
    checkpoint: WorkflowCheckpoint
    revalidation: CheckpointRevalidationResult
    human_approval_required: bool = True
    execution_permitted: bool = False


class GoalToEvaluateWorkflow(BaseModel):
    """Versioned goal, proposed steps, and evaluation criteria for human review."""

    workflow_id: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    eir_document_id: str = Field(min_length=1)
    esg_project_id: str | None = None
    version: str = Field(default="0.1", min_length=1)
    steps: list[GoalWorkflowStep] = Field(min_length=1, max_length=8)
    evaluation_criteria: list[GoalEvaluationCriterion] = Field(min_length=1, max_length=8)
    policy_provenance: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_unique_identifiers(self) -> GoalToEvaluateWorkflow:
        step_ids = [step.step_id for step in self.steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("goal workflow step identifiers must be unique")
        criterion_ids = [criterion.criterion_id for criterion in self.evaluation_criteria]
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("goal workflow criterion identifiers must be unique")
        return self

    def to_checkpoint(self, policy: ExecutionPolicy) -> WorkflowCheckpoint:
        """Create a review checkpoint without authorizing or invoking a step."""

        return WorkflowCheckpoint(
            workflow_id=self.workflow_id,
            stage="awaiting-human-review",
            state={
                "workflow_version": self.version,
                "goal": self.goal,
                "eir_document_id": self.eir_document_id,
                "steps": [step.model_dump(mode="json") for step in self.steps],
                "evaluation_criteria": [criterion.model_dump(mode="json") for criterion in self.evaluation_criteria],
            },
            esg_project_id=self.esg_project_id,
            required_capabilities=[step.capability for step in self.steps],
            policy_provenance=policy.provenance.model_dump(mode="json"),
        )

    def review(self, registry: CapabilityRegistry, policy: ExecutionPolicy) -> GoalWorkflowReview:
        """Revalidate proposed capabilities for manual review without execution."""

        checkpoint = self.to_checkpoint(policy)
        revalidation = checkpoint.revalidate(registry, policy)
        status = GoalWorkflowStatus.READY_FOR_REVIEW if revalidation.valid else GoalWorkflowStatus.REVALIDATION_FAILED
        return GoalWorkflowReview(
            workflow_id=self.workflow_id,
            status=status,
            checkpoint=checkpoint,
            revalidation=revalidation,
        )
