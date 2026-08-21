from __future__ import annotations

import asyncio
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

import typer

from .eir import ingest_eir_file, load_data, validate_document
from .knowledge import EngineeringStateGraph
from .runtime import (
    ApprovalChain,
    ApprovalPersistenceDescriptor,
    ApprovalRevocationRecord,
    BackendSandboxCapabilities,
    CapabilityExecutor,
    ControlledContextEnvelope,
    ControlledContextSchema,
    CoppeliaSimReadOnlyAdapter,
    DeterministicReportAssessment,
    DeterministicReviewPolicy,
    DeterministicReviewReport,
    EvaluationEvidence,
    EvidenceCaptureConsistencyManifest,
    EvidenceProvenanceAssessment,
    EvidenceProvenanceSeal,
    ExecutionLedger,
    ExecutionPolicy,
    ExecutionRequest,
    FixtureSimulatorAdapter,
    GoalToEvaluateWorkflow,
    PolicyProvenanceConsistencyManifest,
    ProvenanceConsistencyManifest,
    ReadOnlyTransportManifest,
    ReportLifecycleTransition,
    ReportProvenanceAssessment,
    ReportProvenanceSeal,
    ReportSealConsistencyManifest,
    ReviewPolicyAssessment,
    ReviewPolicyEvidenceConsistencyAssessment,
    ReviewPolicyEvidenceConsistencyManifest,
    ReviewTraceAssessment,
    ReviewTraceEventConsistencyManifest,
    SandboxAssessment,
    SandboxEnvelope,
    TransportVerificationEvidence,
    WorkflowCheckpoint,
    WorkflowContextBundle,
    WorkflowLifecycleTransition,
    WorkflowReviewTrace,
    assess_approval_chain,
    assess_approval_persistence,
    assess_approval_revocation,
    assess_controlled_context,
    assess_cross_artifacts,
    assess_deterministic_report,
    assess_dispatch_eligibility,
    assess_evaluation_evidence,
    assess_evidence_capture_consistency,
    assess_evidence_provenance,
    assess_lifecycle_transition,
    assess_policy_provenance_consistency,
    assess_provenance_consistency,
    assess_report_lifecycle_transition,
    assess_report_provenance,
    assess_report_seal_consistency,
    assess_review_policy,
    assess_review_policy_evidence_consistency,
    assess_review_trace,
    assess_review_trace_event_consistency,
    assess_sandbox,
    assess_transport,
    assess_workflow_context,
    assess_workflow_readiness,
    build_deterministic_plan,
    default_inspection_backends,
    default_registry,
)

app = typer.Typer(help="MIRAGE engineering compiler and runtime CLI")
FIXTURE_ARGUMENT = typer.Argument(default=None, help="Deterministic read-only fixture JSON path.")
EVIDENCE_ARGUMENT = typer.Argument(default=None, help="Optional deterministic transport evidence JSON path.")


def _result(path: Path) -> Any:
    return validate_document(load_data(path))


@app.command()
def validate(file: Path) -> None:
    """Validate a JSON or YAML EIR document."""
    result = _result(file)
    if result.ok:
        typer.echo(
            f"valid: {file} ({len(result.document.nodes)} nodes, {len(result.document.relationships)} relationships)"
        )
        raise typer.Exit(0)
    typer.echo(json.dumps(result.as_dict(), indent=2))
    raise typer.Exit(1)


@app.command()
def inspect(file: Path) -> None:
    """Inspect an EIR document after validation."""
    result = _result(file)
    if not result.ok:
        typer.echo(json.dumps(result.as_dict(), indent=2))
        raise typer.Exit(1)
    assert result.document is not None
    counts = Counter(node.type.value for node in result.document.nodes)
    typer.echo(f"document: {result.document.id}")
    typer.echo(f"eir_version: {result.document.eir_version}")
    typer.echo(f"nodes: {len(result.document.nodes)}")
    for kind, count in sorted(counts.items()):
        typer.echo(f"  {kind}: {count}")
    typer.echo(f"relationships: {len(result.document.relationships)}")


@app.command("eir-ingest")
def eir_ingest(file: Path, allowed_root: Path | None = None) -> None:
    """Ingest one local JSON or YAML EIR candidate without retrieval, execution, or provenance mutation."""
    result = ingest_eir_file(file, allowed_root=allowed_root)
    typer.echo(result.model_dump_json())
    if not result.accepted:
        raise typer.Exit(1)


@app.command("esg-inspect")
def esg_inspect(file: Path) -> None:
    """Inspect a persisted Engineering State Graph snapshot."""
    graph = EngineeringStateGraph.load(file)
    typer.echo(f"project_id: {graph.project_id}")
    typer.echo(f"revision: {graph.revision}")
    typer.echo(f"eir: {graph.eir.id}")
    typer.echo(f"events: {len(graph.events)}")
    for event in graph.events:
        typer.echo(f"  {event.type.value}: {event.id} ({event.actor})")


@app.command("capabilities")
def capabilities(backend: str | None = None) -> None:
    """List declared URCP capabilities without executing them."""
    for descriptor in default_registry().list(backend=backend):
        backends = ",".join(descriptor.compatible_backends) or "none"
        typer.echo(f"{descriptor.capability_id}@{descriptor.version} [{descriptor.security_class.value}] backends={backends}")


@app.command("execute")
def execute(
    capability_id: str,
    backend: str = "local",
    allow_simulation: bool = False,
    ledger: Path | None = None,
    timeout_seconds: float | None = None,
) -> None:
    """Execute only through the policy-gated local runtime; no host commands are accepted."""
    request = ExecutionRequest(
        capability_id=capability_id,
        backend=backend,
        policy=ExecutionPolicy(allow_simulation=allow_simulation, allowed_backends={backend}),
        timeout_seconds=timeout_seconds,
    )
    audit_ledger = ExecutionLedger(ledger) if ledger else None
    result = asyncio.run(CapabilityExecutor(default_registry(), ledger=audit_ledger).execute(request))
    typer.echo(result.model_dump_json())
    if result.status.value != "succeeded":
        raise typer.Exit(1)


@app.command("simulator-inspect")
def simulator_inspect(backend: str = "coppeliasim", endpoint: str | None = None) -> None:
    """Inspect a simulator boundary without connecting, controlling, or actuating it."""
    inspector = default_inspection_backends(endpoint).get(backend)
    if inspector is None:
        typer.echo(json.dumps({"backend": backend, "status": "unavailable", "message": "inspection backend is not registered"}))
        raise typer.Exit(1)
    typer.echo(asyncio.run(inspector.inspect()).model_dump_json())


@app.command("simulator-metadata")
def simulator_metadata(
    fixture: Path | None = FIXTURE_ARGUMENT,
    backend: str = "fixture",
    endpoint: str | None = None,
    include_state: bool = False,
    timeout_seconds: float | None = None,
) -> None:
    """Read project metadata and an optional state snapshot without simulator control."""
    if fixture is not None:
        adapter = FixtureSimulatorAdapter.from_file(fixture)
    elif backend == "coppeliasim":
        adapter = CoppeliaSimReadOnlyAdapter(endpoint=endpoint)
    else:
        typer.echo(json.dumps({"backend": backend, "status": "unavailable", "message": "fixture path is required"}))
        raise typer.Exit(1)
    policy = ExecutionPolicy(allow_read_only=True, allowed_backends={adapter.name})
    metadata = asyncio.run(adapter.read_project_metadata(policy=policy, timeout_seconds=timeout_seconds))
    payload: dict[str, Any] = {"metadata": metadata.model_dump(mode="json")}
    statuses = [metadata.status.value]
    if include_state:
        snapshot = asyncio.run(adapter.read_state_snapshot(policy=policy, timeout_seconds=timeout_seconds))
        payload["snapshot"] = snapshot.model_dump(mode="json")
        statuses.append(snapshot.status.value)
    typer.echo(json.dumps(payload, sort_keys=True))
    if any(status != "available" for status in statuses):
        raise typer.Exit(1)


@app.command("transport-assess")
def transport_assess(manifest_file: Path, evidence_file: Path | None = EVIDENCE_ARGUMENT) -> None:
    """Assess read-only transport evidence without opening a simulator connection."""
    manifest = ReadOnlyTransportManifest.model_validate_json(manifest_file.read_text(encoding="utf-8"))
    evidence = None
    if evidence_file is not None:
        evidence = TransportVerificationEvidence.model_validate_json(evidence_file.read_text(encoding="utf-8"))
    report = assess_transport(manifest, evidence)
    typer.echo(report.model_dump_json())
    if not report.valid:
        raise typer.Exit(1)


@app.command("goal-workflow-review")
def goal_workflow_review(file: Path, backend: str | None = None, allow_simulation: bool = False) -> None:
    """Revalidate a goal-to-evaluate workflow for manual review without executing a step."""
    workflow = GoalToEvaluateWorkflow.model_validate_json(file.read_text(encoding="utf-8"))
    policy = ExecutionPolicy(
        allow_read_only=True,
        allow_simulation=allow_simulation,
        allowed_backends={backend} if backend else set(),
    )
    review = workflow.review(default_registry(), policy)
    typer.echo(review.model_dump_json())
    if review.status.value != "ready_for_review":
        raise typer.Exit(1)


def _workflow_document(eir_file: Path):
    validation = validate_document(load_data(eir_file))
    if not validation.ok:
        typer.echo(json.dumps(validation.as_dict(), sort_keys=True))
        raise typer.Exit(1)
    assert validation.document is not None
    return validation.document


@app.command("goal-workflow-plan")
def goal_workflow_plan(workflow_file: Path, eir_file: Path) -> None:
    """Validate an EIR-bound goal workflow plan without model or backend invocation."""
    workflow = GoalToEvaluateWorkflow.model_validate_json(workflow_file.read_text(encoding="utf-8"))
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    typer.echo(plan.model_dump_json())
    if plan.status.value != "ready_for_review":
        raise typer.Exit(1)


@app.command("goal-workflow-evidence")
def goal_workflow_evidence(workflow_file: Path, eir_file: Path, evidence_file: Path) -> None:
    """Assess cited workflow evidence without evaluating or executing engineering work."""
    workflow = GoalToEvaluateWorkflow.model_validate_json(workflow_file.read_text(encoding="utf-8"))
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    evidence = [EvaluationEvidence.model_validate(item) for item in json.loads(evidence_file.read_text(encoding="utf-8"))]
    assessment = assess_evaluation_evidence(workflow, plan, evidence)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "ready_for_review":
        raise typer.Exit(1)


@app.command("workflow-context-inspect")
def workflow_context_inspect(workflow_file: Path, eir_file: Path, context_file: Path) -> None:
    """Validate a local redacted context bundle against a deterministic workflow plan."""
    workflow = GoalToEvaluateWorkflow.model_validate_json(workflow_file.read_text(encoding="utf-8"))
    policy = ExecutionPolicy()
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    context = WorkflowContextBundle.model_validate_json(context_file.read_text(encoding="utf-8"))
    assessment = assess_workflow_context(context, workflow, plan, policy)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "ready_for_review":
        raise typer.Exit(1)


@app.command("review-trace-assess")
def review_trace_assess(workflow_file: Path, eir_file: Path, context_file: Path, evidence_file: Path, trace_file: Path) -> None:
    """Assess a complete local provenance trace without changing workflow state."""
    workflow = GoalToEvaluateWorkflow.model_validate_json(workflow_file.read_text(encoding="utf-8"))
    policy = ExecutionPolicy()
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    context = WorkflowContextBundle.model_validate_json(context_file.read_text(encoding="utf-8"))
    context_assessment = assess_workflow_context(context, workflow, plan, policy)
    evidence = [EvaluationEvidence.model_validate(item) for item in json.loads(evidence_file.read_text(encoding="utf-8"))]
    evidence_assessment = assess_evaluation_evidence(workflow, plan, evidence)
    trace = WorkflowReviewTrace.model_validate_json(trace_file.read_text(encoding="utf-8"))
    assessment = assess_review_trace(trace, workflow, context_assessment, evidence_assessment, policy)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "ready_for_review":
        raise typer.Exit(1)


def _review_artifacts(workflow_file: Path, eir_file: Path, context_file: Path, evidence_file: Path, trace_file: Path):
    workflow = GoalToEvaluateWorkflow.model_validate_json(workflow_file.read_text(encoding="utf-8"))
    policy = ExecutionPolicy()
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    context = WorkflowContextBundle.model_validate_json(context_file.read_text(encoding="utf-8"))
    context_assessment = assess_workflow_context(context, workflow, plan, policy)
    evidence = [EvaluationEvidence.model_validate(item) for item in json.loads(evidence_file.read_text(encoding="utf-8"))]
    evidence_assessment = assess_evaluation_evidence(workflow, plan, evidence)
    trace = WorkflowReviewTrace.model_validate_json(trace_file.read_text(encoding="utf-8"))
    trace_assessment = assess_review_trace(trace, workflow, context_assessment, evidence_assessment, policy)
    return workflow, policy, trace_assessment


def _approval_artifacts(workflow_file: Path, eir_file: Path, context_file: Path, evidence_file: Path, trace_file: Path, approval_file: Path):
    workflow, policy, trace_assessment = _review_artifacts(workflow_file, eir_file, context_file, evidence_file, trace_file)
    chain = ApprovalChain.model_validate_json(approval_file.read_text(encoding="utf-8"))
    return workflow, policy, chain, assess_approval_chain(chain, trace_assessment, policy)


def _evidence_artifacts(workflow_file: Path, eir_file: Path, evidence_file: Path):
    workflow = GoalToEvaluateWorkflow.model_validate_json(workflow_file.read_text(encoding="utf-8"))
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    evidence = [EvaluationEvidence.model_validate(item) for item in json.loads(evidence_file.read_text(encoding="utf-8"))]
    return workflow, evidence, assess_evaluation_evidence(workflow, plan, evidence)


def _controlled_context_artifacts(workflow_file: Path, eir_file: Path, context_file: Path, schema_file: Path, envelope_file: Path):
    workflow = GoalToEvaluateWorkflow.model_validate_json(workflow_file.read_text(encoding="utf-8"))
    policy = ExecutionPolicy()
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    bundle = WorkflowContextBundle.model_validate_json(context_file.read_text(encoding="utf-8"))
    context_assessment = assess_workflow_context(bundle, workflow, plan, policy)
    schema = ControlledContextSchema.model_validate_json(schema_file.read_text(encoding="utf-8"))
    envelope = ControlledContextEnvelope.model_validate_json(envelope_file.read_text(encoding="utf-8"))
    controlled = assess_controlled_context(schema, envelope, bundle, context_assessment)
    return workflow, envelope, controlled


def _report_artifacts(
    workflow_file: Path,
    eir_file: Path,
    context_file: Path,
    evidence_file: Path,
    schema_file: Path,
    envelope_file: Path,
    seals_file: Path,
    report_file: Path,
):
    _, envelope, controlled = _controlled_context_artifacts(workflow_file, eir_file, context_file, schema_file, envelope_file)
    _, evidence, evidence_assessment = _evidence_artifacts(workflow_file, eir_file, evidence_file)
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in json.loads(seals_file.read_text(encoding="utf-8"))]
    provenance = assess_evidence_provenance(evidence_assessment, evidence, seals)
    report = DeterministicReviewReport.model_validate_json(report_file.read_text(encoding="utf-8"))
    return envelope, report, assess_deterministic_report(report, controlled, provenance)


def _cross_artifact_assessment(
    workflow_file: Path,
    eir_file: Path,
    context_file: Path,
    evidence_file: Path,
    trace_file: Path,
    approval_file: Path,
    schema_file: Path,
    envelope_file: Path,
    seals_file: Path,
    report_file: Path,
    report_seal_file: Path,
):
    _, policy, _, approval = _approval_artifacts(workflow_file, eir_file, context_file, evidence_file, trace_file, approval_file)
    _, _, controlled = _controlled_context_artifacts(workflow_file, eir_file, context_file, schema_file, envelope_file)
    _, report, report_assessment = _report_artifacts(workflow_file, eir_file, context_file, evidence_file, schema_file, envelope_file, seals_file, report_file)
    report_seal = ReportProvenanceSeal.model_validate_json(report_seal_file.read_text(encoding="utf-8"))
    report_provenance = assess_report_provenance(report, report_assessment, report_seal)
    _, _, trace = _review_artifacts(workflow_file, eir_file, context_file, evidence_file, trace_file)
    return policy, approval, report, assess_cross_artifacts(controlled, trace, approval, report_assessment, report_provenance)


@app.command("approval-chain-assess")
def approval_chain_assess(workflow_file: Path, eir_file: Path, context_file: Path, evidence_file: Path, trace_file: Path, approval_file: Path) -> None:
    """Assess a local human approval chain without granting authority or changing workflow state."""
    _, policy, trace_assessment = _review_artifacts(workflow_file, eir_file, context_file, evidence_file, trace_file)
    chain = ApprovalChain.model_validate_json(approval_file.read_text(encoding="utf-8"))
    assessment = assess_approval_chain(chain, trace_assessment, policy)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "review_ready":
        raise typer.Exit(1)


@app.command("approval-persistence-assess")
def approval_persistence_assess(
    workflow_file: Path,
    eir_file: Path,
    context_file: Path,
    evidence_file: Path,
    trace_file: Path,
    approval_file: Path,
    persistence_file: Path,
) -> None:
    """Assess an authenticated approval persistence interface without credentials or writes."""
    _, policy, chain, approval = _approval_artifacts(workflow_file, eir_file, context_file, evidence_file, trace_file, approval_file)
    descriptor = ApprovalPersistenceDescriptor.model_validate_json(persistence_file.read_text(encoding="utf-8"))
    assessment = assess_approval_persistence(descriptor, chain, approval, policy)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "ready_for_integration":
        raise typer.Exit(1)


@app.command("approval-revocation-assess")
def approval_revocation_assess(
    workflow_file: Path,
    eir_file: Path,
    context_file: Path,
    evidence_file: Path,
    trace_file: Path,
    approval_file: Path,
    revocation_file: Path,
) -> None:
    """Validate a declared approval revocation without changing approval state."""
    _, policy, chain, _ = _approval_artifacts(workflow_file, eir_file, context_file, evidence_file, trace_file, approval_file)
    record = ApprovalRevocationRecord.model_validate_json(revocation_file.read_text(encoding="utf-8"))
    assessment = assess_approval_revocation(record, chain, policy)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "declared":
        raise typer.Exit(1)


@app.command("evidence-provenance-assess")
def evidence_provenance_assess(workflow_file: Path, eir_file: Path, evidence_file: Path, seals_file: Path) -> None:
    """Assess local evidence reference seals without retrieving any evidence content."""
    _, evidence, assessment = _evidence_artifacts(workflow_file, eir_file, evidence_file)
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in json.loads(seals_file.read_text(encoding="utf-8"))]
    provenance = assess_evidence_provenance(assessment, evidence, seals)
    typer.echo(provenance.model_dump_json())
    if provenance.status.value != "ready_for_review":
        raise typer.Exit(1)


@app.command("lifecycle-transition-assess")
def lifecycle_transition_assess(
    workflow_file: Path,
    eir_file: Path,
    context_file: Path,
    evidence_file: Path,
    trace_file: Path,
    approval_file: Path,
    seals_file: Path,
    transition_file: Path,
) -> None:
    """Validate a requested local lifecycle transition without mutating workflow state."""
    _, policy, _, approval = _approval_artifacts(workflow_file, eir_file, context_file, evidence_file, trace_file, approval_file)
    _, evidence, evidence_assessment = _evidence_artifacts(workflow_file, eir_file, evidence_file)
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in json.loads(seals_file.read_text(encoding="utf-8"))]
    provenance = assess_evidence_provenance(evidence_assessment, evidence, seals)
    transition = WorkflowLifecycleTransition.model_validate_json(transition_file.read_text(encoding="utf-8"))
    assessment = assess_lifecycle_transition(transition, approval, provenance)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "valid":
        raise typer.Exit(1)


@app.command("controlled-context-assess")
def controlled_context_assess(workflow_file: Path, eir_file: Path, context_file: Path, schema_file: Path, envelope_file: Path) -> None:
    """Validate schema-bound local context claims without retrieving source content."""
    _, _, assessment = _controlled_context_artifacts(workflow_file, eir_file, context_file, schema_file, envelope_file)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "ready_for_review":
        raise typer.Exit(1)


@app.command("deterministic-report-assess")
def deterministic_report_assess(
    workflow_file: Path,
    eir_file: Path,
    context_file: Path,
    evidence_file: Path,
    schema_file: Path,
    envelope_file: Path,
    seals_file: Path,
    report_file: Path,
) -> None:
    """Validate a reference-only report artifact without generating a report or engineering claim."""
    _, _, assessment = _report_artifacts(workflow_file, eir_file, context_file, evidence_file, schema_file, envelope_file, seals_file, report_file)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "ready_for_review":
        raise typer.Exit(1)


@app.command("report-provenance-assess")
def report_provenance_assess(
    workflow_file: Path,
    eir_file: Path,
    context_file: Path,
    evidence_file: Path,
    schema_file: Path,
    envelope_file: Path,
    seals_file: Path,
    report_file: Path,
    report_seal_file: Path,
) -> None:
    """Validate a report provenance seal without signing, storing, or publishing a report."""
    _, report, assessment = _report_artifacts(workflow_file, eir_file, context_file, evidence_file, schema_file, envelope_file, seals_file, report_file)
    seal = ReportProvenanceSeal.model_validate_json(report_seal_file.read_text(encoding="utf-8"))
    provenance = assess_report_provenance(report, assessment, seal)
    typer.echo(provenance.model_dump_json())
    if provenance.status.value != "ready_for_review":
        raise typer.Exit(1)


@app.command("report-seal-consistency-assess")
def report_seal_consistency_assess(
    report_file: Path,
    seal_file: Path,
    provenance_assessment_file: Path,
    trace_file: Path,
    trace_assessment_file: Path,
    manifest_file: Path,
) -> None:
    """Compare supplied report seal and review-trace declarations without retrieval, signing, or mutation."""
    report = DeterministicReviewReport.model_validate_json(report_file.read_text(encoding="utf-8"))
    seal = ReportProvenanceSeal.model_validate_json(seal_file.read_text(encoding="utf-8"))
    provenance = ReportProvenanceAssessment.model_validate_json(provenance_assessment_file.read_text(encoding="utf-8"))
    trace = WorkflowReviewTrace.model_validate_json(trace_file.read_text(encoding="utf-8"))
    trace_assessment = ReviewTraceAssessment.model_validate_json(trace_assessment_file.read_text(encoding="utf-8"))
    manifest = ReportSealConsistencyManifest.model_validate_json(manifest_file.read_text(encoding="utf-8"))
    assessment = assess_report_seal_consistency(manifest, report, seal, provenance, trace, trace_assessment)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "consistent":
        raise typer.Exit(1)


@app.command("review-trace-event-consistency-assess")
def review_trace_event_consistency_assess(trace_file: Path, trace_assessment_file: Path, manifest_file: Path) -> None:
    """Compare supplied review-trace event declarations without retrieval, signing, mutation, or execution."""
    trace = WorkflowReviewTrace.model_validate_json(trace_file.read_text(encoding="utf-8"))
    trace_assessment = ReviewTraceAssessment.model_validate_json(trace_assessment_file.read_text(encoding="utf-8"))
    manifest = ReviewTraceEventConsistencyManifest.model_validate_json(manifest_file.read_text(encoding="utf-8"))
    assessment = assess_review_trace_event_consistency(manifest, trace, trace_assessment)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "consistent":
        raise typer.Exit(1)


@app.command("policy-provenance-consistency-assess")
def policy_provenance_consistency_assess(
    policy_file: Path,
    context_bundle_file: Path,
    context_envelope_file: Path,
    trace_file: Path,
    report_file: Path,
    review_policy_file: Path,
    review_policy_assessment_file: Path,
    manifest_file: Path,
) -> None:
    """Compare supplied policy provenance declarations without retrieval, mutation, or execution."""
    policy = ExecutionPolicy.model_validate_json(policy_file.read_text(encoding="utf-8"))
    context_bundle = WorkflowContextBundle.model_validate_json(context_bundle_file.read_text(encoding="utf-8"))
    context_envelope = ControlledContextEnvelope.model_validate_json(context_envelope_file.read_text(encoding="utf-8"))
    trace = WorkflowReviewTrace.model_validate_json(trace_file.read_text(encoding="utf-8"))
    report = DeterministicReviewReport.model_validate_json(report_file.read_text(encoding="utf-8"))
    review_policy = DeterministicReviewPolicy.model_validate_json(review_policy_file.read_text(encoding="utf-8"))
    review_policy_assessment = ReviewPolicyAssessment.model_validate_json(review_policy_assessment_file.read_text(encoding="utf-8"))
    manifest = PolicyProvenanceConsistencyManifest.model_validate_json(manifest_file.read_text(encoding="utf-8"))
    assessment = assess_policy_provenance_consistency(
        manifest,
        policy,
        context_bundle,
        context_envelope,
        trace,
        report,
        review_policy,
        review_policy_assessment,
    )
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "consistent":
        raise typer.Exit(1)


@app.command("review-policy-evidence-consistency-assess")
def review_policy_evidence_consistency_assess(
    review_policy_file: Path,
    review_policy_assessment_file: Path,
    report_file: Path,
    report_assessment_file: Path,
    evidence_provenance_file: Path,
    seals_file: Path,
    manifest_file: Path,
) -> None:
    """Compare supplied review-policy evidence declarations without retrieval, mutation, or execution."""
    review_policy = DeterministicReviewPolicy.model_validate_json(review_policy_file.read_text(encoding="utf-8"))
    review_policy_assessment = ReviewPolicyAssessment.model_validate_json(review_policy_assessment_file.read_text(encoding="utf-8"))
    report = DeterministicReviewReport.model_validate_json(report_file.read_text(encoding="utf-8"))
    report_assessment = DeterministicReportAssessment.model_validate_json(report_assessment_file.read_text(encoding="utf-8"))
    evidence_provenance = EvidenceProvenanceAssessment.model_validate_json(evidence_provenance_file.read_text(encoding="utf-8"))
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in json.loads(seals_file.read_text(encoding="utf-8"))]
    manifest = ReviewPolicyEvidenceConsistencyManifest.model_validate_json(manifest_file.read_text(encoding="utf-8"))
    assessment = assess_review_policy_evidence_consistency(
        manifest,
        review_policy,
        review_policy_assessment,
        report,
        report_assessment,
        evidence_provenance,
        seals,
    )
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "consistent":
        raise typer.Exit(1)


@app.command("evidence-capture-consistency-assess")
def evidence_capture_consistency_assess(
    evidence_provenance_file: Path,
    review_policy_evidence_assessment_file: Path,
    report_file: Path,
    seals_file: Path,
    manifest_file: Path,
) -> None:
    """Compare supplied evidence-capture declarations without retrieval, mutation, or execution."""

    evidence_provenance = EvidenceProvenanceAssessment.model_validate_json(evidence_provenance_file.read_text(encoding="utf-8"))
    review_policy_evidence = ReviewPolicyEvidenceConsistencyAssessment.model_validate_json(
        review_policy_evidence_assessment_file.read_text(encoding="utf-8")
    )
    report = DeterministicReviewReport.model_validate_json(report_file.read_text(encoding="utf-8"))
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in json.loads(seals_file.read_text(encoding="utf-8"))]
    manifest = EvidenceCaptureConsistencyManifest.model_validate_json(manifest_file.read_text(encoding="utf-8"))
    assessment = assess_evidence_capture_consistency(manifest, evidence_provenance, review_policy_evidence, report, seals)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "consistent":
        raise typer.Exit(1)


@app.command("report-lifecycle-assess")
def report_lifecycle_assess(
    workflow_file: Path,
    eir_file: Path,
    context_file: Path,
    evidence_file: Path,
    schema_file: Path,
    envelope_file: Path,
    seals_file: Path,
    report_file: Path,
    report_seal_file: Path,
    transition_file: Path,
) -> None:
    """Validate report lifecycle order without mutating, publishing, or dispatching a report."""
    _, report, assessment = _report_artifacts(workflow_file, eir_file, context_file, evidence_file, schema_file, envelope_file, seals_file, report_file)
    seal = ReportProvenanceSeal.model_validate_json(report_seal_file.read_text(encoding="utf-8"))
    provenance = assess_report_provenance(report, assessment, seal)
    transition = ReportLifecycleTransition.model_validate_json(transition_file.read_text(encoding="utf-8"))
    lifecycle = assess_report_lifecycle_transition(transition, provenance)
    typer.echo(lifecycle.model_dump_json())
    if not lifecycle.valid:
        raise typer.Exit(1)


@app.command("provenance-consistency-assess")
def provenance_consistency_assess(
    eir_file: Path,
    manifest_file: Path,
    seals_file: Path,
    report_file: Path,
    evidence_provenance_file: Path,
    report_assessment_file: Path,
) -> None:
    """Compare local EIR, evidence, and report provenance references without retrieving any source."""
    ingestion = ingest_eir_file(eir_file)
    if not ingestion.accepted:
        typer.echo(ingestion.model_dump_json())
        raise typer.Exit(1)
    assert ingestion.source is not None
    assert ingestion.document is not None
    manifest = ProvenanceConsistencyManifest.model_validate_json(manifest_file.read_text(encoding="utf-8"))
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in json.loads(seals_file.read_text(encoding="utf-8"))]
    report = DeterministicReviewReport.model_validate_json(report_file.read_text(encoding="utf-8"))
    evidence_provenance = EvidenceProvenanceAssessment.model_validate_json(evidence_provenance_file.read_text(encoding="utf-8"))
    report_assessment = DeterministicReportAssessment.model_validate_json(report_assessment_file.read_text(encoding="utf-8"))
    assessment = assess_provenance_consistency(manifest, ingestion.source, ingestion.document, seals, evidence_provenance, report, report_assessment)
    typer.echo(json.dumps({"source": ingestion.source.model_dump(mode="json"), "assessment": assessment.model_dump(mode="json")}, sort_keys=True))
    if assessment.status.value != "consistent":
        raise typer.Exit(1)


@app.command("cross-artifact-assess")
def cross_artifact_assess(
    workflow_file: Path,
    eir_file: Path,
    context_file: Path,
    evidence_file: Path,
    trace_file: Path,
    approval_file: Path,
    schema_file: Path,
    envelope_file: Path,
    seals_file: Path,
    report_file: Path,
    report_seal_file: Path,
) -> None:
    """Validate local workflow, context, approval, and report artifact consistency without dispatch."""
    _, _, _, assessment = _cross_artifact_assessment(
        workflow_file, eir_file, context_file, evidence_file, trace_file, approval_file, schema_file, envelope_file, seals_file, report_file, report_seal_file
    )
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "consistent":
        raise typer.Exit(1)


@app.command("review-policy-assess")
def review_policy_assess(
    workflow_file: Path,
    eir_file: Path,
    context_file: Path,
    evidence_file: Path,
    trace_file: Path,
    approval_file: Path,
    schema_file: Path,
    envelope_file: Path,
    seals_file: Path,
    report_file: Path,
    report_seal_file: Path,
    policy_file: Path,
) -> None:
    """Apply deterministic review policy rules without generated content or dispatch."""
    _, _, report, cross = _cross_artifact_assessment(
        workflow_file, eir_file, context_file, evidence_file, trace_file, approval_file, schema_file, envelope_file, seals_file, report_file, report_seal_file
    )
    review_policy = DeterministicReviewPolicy.model_validate_json(policy_file.read_text(encoding="utf-8"))
    assessment = assess_review_policy(review_policy, report, cross)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "ready_for_review":
        raise typer.Exit(1)


@app.command("workflow-readiness-assess")
def workflow_readiness_assess(
    workflow_file: Path,
    eir_file: Path,
    context_file: Path,
    evidence_file: Path,
    trace_file: Path,
    approval_file: Path,
    schema_file: Path,
    envelope_file: Path,
    seals_file: Path,
    report_file: Path,
    report_seal_file: Path,
    policy_file: Path,
    transport_manifest_file: Path,
    transport_evidence_file: Path,
    sandbox_assessment_file: Path,
    allow_simulation: bool = False,
) -> None:
    """Aggregate review readiness and external prerequisite denials without invoking a backend."""
    execution_policy, approval, report, cross = _cross_artifact_assessment(
        workflow_file, eir_file, context_file, evidence_file, trace_file, approval_file, schema_file, envelope_file, seals_file, report_file, report_seal_file
    )
    execution_policy = execution_policy.model_copy(update={"allow_simulation": allow_simulation})
    review_policy = DeterministicReviewPolicy.model_validate_json(policy_file.read_text(encoding="utf-8"))
    policy_assessment = assess_review_policy(review_policy, report, cross)
    manifest = ReadOnlyTransportManifest.model_validate_json(transport_manifest_file.read_text(encoding="utf-8"))
    transport_evidence = TransportVerificationEvidence.model_validate_json(transport_evidence_file.read_text(encoding="utf-8"))
    transport = assess_transport(manifest, transport_evidence)
    sandbox = SandboxAssessment.model_validate_json(sandbox_assessment_file.read_text(encoding="utf-8"))
    dispatch = assess_dispatch_eligibility(approval, transport, sandbox, execution_policy)
    readiness = assess_workflow_readiness(cross, policy_assessment, dispatch)
    typer.echo(readiness.model_dump_json())
    if readiness.status.value != "ready_for_external_prerequisites":
        raise typer.Exit(1)


@app.command("dispatch-eligibility-assess")
def dispatch_eligibility_assess(
    workflow_file: Path,
    eir_file: Path,
    context_file: Path,
    evidence_file: Path,
    trace_file: Path,
    approval_file: Path,
    transport_manifest_file: Path,
    transport_evidence_file: Path,
    sandbox_assessment_file: Path,
    allow_simulation: bool = False,
) -> None:
    """Assess prerequisites for future dispatch without invoking a backend or authorizing execution."""
    _, policy, trace_assessment = _review_artifacts(workflow_file, eir_file, context_file, evidence_file, trace_file)
    policy = policy.model_copy(update={"allow_simulation": allow_simulation})
    chain = ApprovalChain.model_validate_json(approval_file.read_text(encoding="utf-8"))
    approval = assess_approval_chain(chain, trace_assessment, policy)
    manifest = ReadOnlyTransportManifest.model_validate_json(transport_manifest_file.read_text(encoding="utf-8"))
    evidence = TransportVerificationEvidence.model_validate_json(transport_evidence_file.read_text(encoding="utf-8"))
    transport = assess_transport(manifest, evidence)
    sandbox = SandboxAssessment.model_validate_json(sandbox_assessment_file.read_text(encoding="utf-8"))
    assessment = assess_dispatch_eligibility(approval, transport, sandbox, policy)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "eligible_for_verified_dispatch":
        raise typer.Exit(1)


@app.command("sandbox-assess")
def sandbox_assess(
    backend: str = "local",
    max_memory_mb: int | None = None,
    max_cpu_seconds: float | None = None,
) -> None:
    """Assess a declared sandbox envelope without attempting host-level isolation."""
    envelope = SandboxEnvelope(max_memory_mb=max_memory_mb, max_cpu_seconds=max_cpu_seconds)
    assessment = assess_sandbox(envelope, BackendSandboxCapabilities(backend=backend))
    typer.echo(assessment.model_dump_json())
    if assessment.status.value == "denied":
        raise typer.Exit(1)


@app.command("checkpoint-revalidate")
def checkpoint_revalidate(file: Path, allow_simulation: bool = False, backend: str | None = None) -> None:
    """Revalidate a checkpoint for manual review without resuming its workflow."""
    policy = ExecutionPolicy(allow_simulation=allow_simulation, allowed_backends={backend} if backend else set())
    result = WorkflowCheckpoint.load(file).revalidate(default_registry(), policy)
    typer.echo(result.model_dump_json())
    if not result.valid:
        raise typer.Exit(1)


@app.command("ledger-inspect")
def ledger_inspect(file: Path) -> None:
    """Inspect persisted execution audit records without executing them."""
    for record in ExecutionLedger(file).records():
        typer.echo(f"{record.request_id} {record.status} {record.capability_id}@{record.version} backend={record.backend} actor={record.actor}")


@app.command("ledger-verify")
def ledger_verify(file: Path) -> None:
    """Verify local ledger envelopes without executing, repairing, or compacting records."""
    assessment = ExecutionLedger(file).verify_integrity()
    typer.echo(assessment.model_dump_json())
    if not assessment.valid:
        raise typer.Exit(1)


@app.command("checkpoint-inspect")
def checkpoint_inspect(file: Path) -> None:
    """Inspect a validated workflow checkpoint without resuming execution."""
    checkpoint = WorkflowCheckpoint.load(file)
    typer.echo(f"workflow_id: {checkpoint.workflow_id}")
    typer.echo(f"revision: {checkpoint.revision}")
    typer.echo(f"stage: {checkpoint.stage}")
    typer.echo(f"execution_ids: {len(checkpoint.execution_ids)}")


@app.command()
def doctor() -> None:
    """Check local MIRAGE configuration without printing secrets."""
    typer.echo("mirage: ready")
    typer.echo(f"python: {os.sys.version.split()[0]}")
    config = os.getenv("MIRAGE_PROVIDER_CONFIG")
    typer.echo(
        f"provider_config: {'configured' if config and Path(config).exists() else 'not configured (optional for EIR CLI)'}"
    )
    for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MIRAGE_COMPATIBLE_API_KEY"):
        typer.echo(f"{key}: {'present' if os.getenv(key) else 'absent'}")
