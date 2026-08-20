from datetime import UTC, datetime

from mirage.runtime import (
    ApprovalChain,
    ApprovalChainAssessment,
    ApprovalChainStatus,
    ApprovalDecision,
    ApprovalIdentityEvidence,
    ApprovalPersistenceDescriptor,
    ApprovalRevocationRecord,
    EvaluationEvidence,
    EvaluationEvidenceClass,
    EvidenceProvenanceSeal,
    EvidenceProvenanceStatus,
    ExecutionPolicy,
    HumanApprovalRecord,
    WorkflowEvidenceAssessment,
    WorkflowEvidenceStatus,
    WorkflowLifecycleState,
    WorkflowLifecycleTransition,
    WorkflowPlanStatus,
    assess_approval_persistence,
    assess_approval_revocation,
    assess_evidence_provenance,
    assess_lifecycle_transition,
)


def policy() -> ExecutionPolicy:
    return ExecutionPolicy()


def chain(active_policy: ExecutionPolicy) -> ApprovalChain:
    return ApprovalChain(
        chain_id="chain-v1",
        workflow_id="workflow-v1",
        trace_id="trace-v1",
        policy_provenance=active_policy.provenance.model_dump(mode="json"),
        approvals=[
            HumanApprovalRecord(
                approval_id="approval-v1",
                workflow_id="workflow-v1",
                trace_id="trace-v1",
                approver_id="reviewer@example.invalid",
                decision=ApprovalDecision.APPROVED,
                approval_digest="sha256:approval-v1",
                recorded_at=datetime(2026, 8, 20, tzinfo=UTC),
            )
        ],
    )


def approval_assessment() -> ApprovalChainAssessment:
    return ApprovalChainAssessment(chain_id="chain-v1", workflow_id="workflow-v1", trace_id="trace-v1", status=ApprovalChainStatus.REVIEW_READY)


def test_persistence_descriptor_is_ready_for_integration_without_writing():
    active_policy = policy()
    descriptor = ApprovalPersistenceDescriptor(
        persistence_id="persistence-v1",
        backend_type="external-audit-interface",
        audit_log_reference="audit://approvals",
        signature_scheme="detached-signature",
        retention_days=365,
        identity_evidence=ApprovalIdentityEvidence(
            subject_id="reviewer@example.invalid",
            identity_provider="example-identity",
            credential_reference="credential://opaque-reference",
            authentication_event_digest="sha256:authentication-event-v1",
            authenticated_at=datetime(2026, 8, 20, tzinfo=UTC),
        ),
    )

    assessment = assess_approval_persistence(descriptor, chain(active_policy), approval_assessment(), active_policy)

    assert assessment.status.value == "ready_for_integration"
    assert assessment.execution_permitted is False


def test_declared_revocation_is_valid_and_does_not_mutate_the_chain():
    active_policy = policy()
    record = ApprovalRevocationRecord(
        revocation_id="revocation-v1",
        chain_id="chain-v1",
        approval_id="approval-v1",
        revoker_id="reviewer@example.invalid",
        reason="Evidence superseded.",
        revocation_digest="sha256:revocation-v1",
        recorded_at=datetime(2026, 8, 20, tzinfo=UTC),
    )

    assessment = assess_approval_revocation(record, chain(active_policy), active_policy)

    assert assessment.status.value == "declared"
    assert assessment.execution_permitted is False


def test_provenance_and_lifecycle_transition_remain_non_mutating():
    evidence = [
        EvaluationEvidence(
            evidence_id="evidence-v1",
            criterion_id="criterion-v1",
            evidence_class=EvaluationEvidenceClass.DETERMINISTIC_VALIDATION,
            source_node_ids={"node-v1"},
            source_reference="EIR:node-v1",
        )
    ]
    evidence_assessment = WorkflowEvidenceAssessment(
        workflow_id="workflow-v1",
        plan_status=WorkflowPlanStatus.READY_FOR_REVIEW,
        status=WorkflowEvidenceStatus.READY_FOR_REVIEW,
    )
    provenance = assess_evidence_provenance(
        evidence_assessment,
        evidence,
        [
            EvidenceProvenanceSeal(
                seal_id="seal-v1",
                evidence_id="evidence-v1",
                source_reference="EIR:node-v1",
                source_digest="sha256:evidence-v1",
                capture_method="deterministic-validation",
                captured_at=datetime(2026, 8, 20, tzinfo=UTC),
                verifier_reference="reviewer:local",
            )
        ],
    )
    transition = WorkflowLifecycleTransition(
        transition_id="transition-v1",
        workflow_id="workflow-v1",
        from_state=WorkflowLifecycleState.REVIEW_READY,
        to_state=WorkflowLifecycleState.APPROVAL_REVIEWED,
        trace_id="trace-v1",
        transition_digest="sha256:transition-v1",
    )

    lifecycle = assess_lifecycle_transition(transition, approval_assessment(), provenance)

    assert provenance.status == EvidenceProvenanceStatus.READY_FOR_REVIEW
    assert lifecycle.status.value == "valid"
    assert lifecycle.execution_permitted is False
