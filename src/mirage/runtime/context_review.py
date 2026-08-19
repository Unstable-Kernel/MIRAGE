"""Deterministic context bundles for review-only engineering workflows.

Context items contain references and digests, not raw external artifacts. The
assessment path validates provenance and planned source-node coverage without
retrieving data, calling a model, or invoking a backend.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .execution import ExecutionPolicy
from .goal_workflow import GoalToEvaluateWorkflow
from .workflow_evidence import DeterministicWorkflowPlan, WorkflowPlanStatus, WorkflowValidationIssue


class ContextItemKind(StrEnum):
    EIR_NODE = "eir_node"
    EVIDENCE_REFERENCE = "evidence_reference"
    POLICY = "policy"
    USER_CONSTRAINT = "user_constraint"


class ContextBundleStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    INVALID = "invalid"


class WorkflowContextItem(BaseModel):
    context_item_id: str = Field(min_length=1)
    kind: ContextItemKind
    reference: str = Field(min_length=1)
    content_digest: str = Field(min_length=8)
    source_node_ids: set[str] = Field(default_factory=set)
    observations: dict[str, str] = Field(default_factory=dict)


class WorkflowContextBundle(BaseModel):
    context_bundle_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    eir_document_id: str = Field(min_length=1)
    policy_provenance: dict[str, object] = Field(default_factory=dict)
    items: list[WorkflowContextItem] = Field(min_length=1, max_length=32)
    redaction_verified: bool = True

    @model_validator(mode="after")
    def require_unique_items_and_redaction(self) -> WorkflowContextBundle:
        item_ids = [item.context_item_id for item in self.items]
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("workflow context item identifiers must be unique")
        if not self.redaction_verified:
            raise ValueError("workflow context bundle requires verified redaction")
        return self


class WorkflowContextAssessment(BaseModel):
    workflow_id: str
    context_bundle_id: str
    status: ContextBundleStatus
    source_node_ids: set[str] = Field(default_factory=set)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def assess_workflow_context(
    bundle: WorkflowContextBundle,
    workflow: GoalToEvaluateWorkflow,
    plan: DeterministicWorkflowPlan,
    policy: ExecutionPolicy,
) -> WorkflowContextAssessment:
    """Validate context references against a workflow plan and active policy."""

    issues: list[WorkflowValidationIssue] = []
    if plan.status != WorkflowPlanStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="plan_not_ready", message="workflow plan is not ready for context review"))
    if bundle.workflow_id != workflow.workflow_id:
        issues.append(WorkflowValidationIssue(code="context_workflow_mismatch", message="context bundle workflow identifier does not match"))
    if bundle.eir_document_id != plan.eir_document_id:
        issues.append(WorkflowValidationIssue(code="context_eir_document_mismatch", message="context bundle EIR document identifier does not match"))
    active_provenance = policy.provenance.model_dump(mode="json")
    if bundle.policy_provenance and bundle.policy_provenance != active_provenance:
        issues.append(WorkflowValidationIssue(code="context_policy_provenance_mismatch", message="context bundle policy provenance differs from active policy"))
    source_node_ids: set[str] = set()
    for item in bundle.items:
        source_node_ids.update(item.source_node_ids)
        unknown = item.source_node_ids - plan.source_node_ids
        if unknown:
            issues.append(
                WorkflowValidationIssue(
                    code="context_source_out_of_plan",
                    message=f"context item references nodes outside the plan: {', '.join(sorted(unknown))}",
                    path=f"items[{item.context_item_id}].source_node_ids",
                )
            )
    return WorkflowContextAssessment(
        workflow_id=workflow.workflow_id,
        context_bundle_id=bundle.context_bundle_id,
        status=ContextBundleStatus.INVALID if issues else ContextBundleStatus.READY_FOR_REVIEW,
        source_node_ids=source_node_ids,
        issues=issues,
    )
