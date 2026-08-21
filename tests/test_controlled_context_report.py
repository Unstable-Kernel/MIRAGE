from datetime import UTC, datetime

from mirage.runtime import (
    ContextBundleStatus,
    ContextItemKind,
    ControlledContextEnvelope,
    ControlledContextField,
    ControlledContextSchema,
    DeterministicReportSection,
    DeterministicReviewReport,
    EvidenceProvenanceAssessment,
    EvidenceProvenanceStatus,
    ReportLifecycleState,
    ReportLifecycleTransition,
    ReportProvenanceSeal,
    WorkflowContextAssessment,
    WorkflowContextBundle,
    WorkflowContextItem,
    assess_controlled_context,
    assess_deterministic_report,
    assess_report_lifecycle_transition,
    assess_report_provenance,
)


def test_controlled_context_and_report_artifacts_remain_review_only():
    bundle = WorkflowContextBundle(
        context_bundle_id="context-v1",
        workflow_id="workflow-v1",
        eir_document_id="eir-v1",
        items=[
            WorkflowContextItem(
                context_item_id="robot-item",
                kind=ContextItemKind.EIR_NODE,
                reference="EIR:robot.v1",
                content_digest="sha256:robot-item-v1",
            )
        ],
    )
    context_assessment = WorkflowContextAssessment(workflow_id="workflow-v1", context_bundle_id="context-v1", status=ContextBundleStatus.READY_FOR_REVIEW)
    schema = ControlledContextSchema(
        schema_id="schema-v1",
        workflow_id="workflow-v1",
        fields=[ControlledContextField(field_id="robot", item_kind=ContextItemKind.EIR_NODE, allowed_reference_prefix="EIR:")],
    )
    envelope = ControlledContextEnvelope(
        envelope_id="envelope-v1",
        schema_id="schema-v1",
        workflow_id="workflow-v1",
        context_bundle_id="context-v1",
        claims=[{"claim_id": "claim-robot", "field_id": "robot", "context_item_id": "robot-item", "reference_digest": "sha256:robot-item-v1"}],
    )

    controlled = assess_controlled_context(schema, envelope, bundle, context_assessment)
    provenance = EvidenceProvenanceAssessment(workflow_id="workflow-v1", status=EvidenceProvenanceStatus.READY_FOR_REVIEW, sealed_evidence_ids={"evidence-v1"})
    report = DeterministicReviewReport(
        report_id="report-v1",
        workflow_id="workflow-v1",
        context_envelope_id="envelope-v1",
        sections=[DeterministicReportSection(section_id="summary", title="Review inputs", context_claim_ids={"claim-robot"}, evidence_ids={"evidence-v1"})],
    )
    report_assessment = assess_deterministic_report(report, controlled, provenance)
    provenance_assessment = assess_report_provenance(
        report,
        report_assessment,
        ReportProvenanceSeal(
            seal_id="report-seal-v1",
            report_id="report-v1",
            report_digest="sha256:report-v1",
            source_trace_id="trace-v1",
            sealer_reference="reviewer:local",
            sealed_at=datetime(2026, 8, 20, tzinfo=UTC),
        ),
    )
    lifecycle = assess_report_lifecycle_transition(
        ReportLifecycleTransition(
            transition_id="report-transition-v1",
            report_id="report-v1",
            from_state=ReportLifecycleState.READY_FOR_REVIEW,
            to_state=ReportLifecycleState.SEALED_FOR_REVIEW,
            transition_digest="sha256:report-transition-v1",
        ),
        provenance_assessment,
    )

    assert controlled.status.value == "ready_for_review"
    assert report_assessment.status.value == "ready_for_review"
    assert provenance_assessment.status.value == "ready_for_review"
    assert lifecycle.valid is True
    assert all(item.execution_permitted is False for item in (controlled, report_assessment, provenance_assessment, lifecycle))
