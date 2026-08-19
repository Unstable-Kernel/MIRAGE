"""Deterministic EIR-to-plan validation and workflow evidence assessment.

The functions in this module validate a proposed workflow against an EIR
document and assess declared evidence. They never invoke a model, simulator,
capability backend, checkpoint resume path, or external service.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from ..eir import EIRDocument, validate_document
from .goal_workflow import GoalToEvaluateWorkflow


class WorkflowPlanStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    INVALID = "invalid"


class WorkflowEvidenceStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    INSUFFICIENT = "insufficient"
    INVALID = "invalid"


class WorkflowValidationIssue(BaseModel):
    code: str
    message: str
    path: str = ""


class DeterministicWorkflowPlan(BaseModel):
    workflow_id: str
    eir_document_id: str
    eir_version: str
    status: WorkflowPlanStatus
    source_node_ids: set[str] = Field(default_factory=set)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


class EvaluationEvidenceClass(StrEnum):
    DETERMINISTIC_VALIDATION = "deterministic_validation"
    READ_ONLY_SNAPSHOT = "read_only_snapshot"
    HUMAN_REVIEW = "human_review"
    MODEL_GENERATED = "model_generated"


class EvaluationEvidence(BaseModel):
    evidence_id: str = Field(min_length=1)
    criterion_id: str = Field(min_length=1)
    evidence_class: EvaluationEvidenceClass
    source_node_ids: set[str] = Field(min_length=1)
    source_reference: str = Field(min_length=1)
    observations: dict[str, str] = Field(default_factory=dict)


class WorkflowEvidenceAssessment(BaseModel):
    workflow_id: str
    plan_status: WorkflowPlanStatus
    status: WorkflowEvidenceStatus
    criterion_evidence: dict[str, list[str]] = Field(default_factory=dict)
    issues: list[WorkflowValidationIssue] = Field(default_factory=list)
    execution_permitted: bool = False


def build_deterministic_plan(workflow: GoalToEvaluateWorkflow, document: EIRDocument) -> DeterministicWorkflowPlan:
    """Validate proposed workflow references against a fully validated EIR document."""

    issues: list[WorkflowValidationIssue] = []
    validation = validate_document(document.model_dump(mode="json"))
    if not validation.ok:
        issues.extend(
            WorkflowValidationIssue(code=f"eir_{error.code.lower()}", message=error.message, path=error.path)
            for error in validation.errors
        )
    if workflow.eir_document_id != document.id:
        issues.append(
            WorkflowValidationIssue(
                code="eir_document_mismatch",
                message="workflow EIR document identifier does not match the provided EIR document",
                path="eir_document_id",
            )
        )
    known_node_ids = {node.id for node in document.nodes}
    source_node_ids: set[str] = set()
    for step in workflow.steps:
        source_node_ids.update(step.source_node_ids)
        unknown = step.source_node_ids - known_node_ids
        if unknown:
            issues.append(
                WorkflowValidationIssue(
                    code="workflow_source_node_missing",
                    message=f"workflow step references unknown EIR nodes: {', '.join(sorted(unknown))}",
                    path=f"steps[{step.step_id}].source_node_ids",
                )
            )
    return DeterministicWorkflowPlan(
        workflow_id=workflow.workflow_id,
        eir_document_id=document.id,
        eir_version=document.eir_version,
        status=WorkflowPlanStatus.INVALID if issues else WorkflowPlanStatus.READY_FOR_REVIEW,
        source_node_ids=source_node_ids,
        issues=issues,
    )


def assess_evaluation_evidence(
    workflow: GoalToEvaluateWorkflow,
    plan: DeterministicWorkflowPlan,
    evidence: list[EvaluationEvidence],
) -> WorkflowEvidenceAssessment:
    """Assess cited evidence for review, without evaluating or executing a workflow."""

    issues: list[WorkflowValidationIssue] = []
    criterion_ids = {criterion.criterion_id for criterion in workflow.evaluation_criteria}
    evidence_by_criterion: dict[str, list[str]] = {criterion_id: [] for criterion_id in criterion_ids}
    if plan.status != WorkflowPlanStatus.READY_FOR_REVIEW:
        issues.append(WorkflowValidationIssue(code="plan_not_ready", message="deterministic workflow plan is not ready for review"))
    for item in evidence:
        if item.criterion_id not in criterion_ids:
            issues.append(
                WorkflowValidationIssue(
                    code="evidence_criterion_unknown",
                    message=f"evidence references an unknown criterion: {item.criterion_id}",
                    path=f"evidence[{item.evidence_id}].criterion_id",
                )
            )
            continue
        unknown_nodes = item.source_node_ids - plan.source_node_ids
        if unknown_nodes:
            issues.append(
                WorkflowValidationIssue(
                    code="evidence_source_out_of_plan",
                    message=f"evidence references nodes outside the deterministic workflow plan: {', '.join(sorted(unknown_nodes))}",
                    path=f"evidence[{item.evidence_id}].source_node_ids",
                )
            )
            continue
        evidence_by_criterion[item.criterion_id].append(item.evidence_id)
    for criterion in workflow.evaluation_criteria:
        if criterion.evidence_required and not evidence_by_criterion[criterion.criterion_id]:
            issues.append(
                WorkflowValidationIssue(
                    code="criterion_evidence_missing",
                    message=f"required evidence is missing for criterion: {criterion.criterion_id}",
                    path=f"evaluation_criteria[{criterion.criterion_id}]",
                )
            )
    status = WorkflowEvidenceStatus.READY_FOR_REVIEW
    if issues:
        status = WorkflowEvidenceStatus.INVALID if any(issue.code.startswith("evidence_") or issue.code == "plan_not_ready" for issue in issues) else WorkflowEvidenceStatus.INSUFFICIENT
    return WorkflowEvidenceAssessment(
        workflow_id=workflow.workflow_id,
        plan_status=plan.status,
        status=status,
        criterion_evidence=evidence_by_criterion,
        issues=issues,
    )
