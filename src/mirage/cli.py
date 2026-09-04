from __future__ import annotations

import asyncio
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, NoReturn

import typer
import yaml
from pydantic import BaseModel

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
    DispatchEligibilityAssessment,
    EvaluationEvidence,
    EvidenceCaptureConsistencyAssessment,
    EvidenceCaptureConsistencyManifest,
    EvidenceCaptureLineageConsistencyAssessment,
    EvidenceCaptureLineageConsistencyManifest,
    EvidenceGatingConsistencyManifest,
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
    assess_evidence_capture_lineage_consistency,
    assess_evidence_gating_consistency,
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

# OSError covers missing/unreadable paths; ValueError covers JSONDecodeError and
# pydantic ValidationError; YAMLError covers malformed YAML documents.
INPUT_ERRORS = (OSError, ValueError, yaml.YAMLError)


def _input_error(path: Path, error: BaseException) -> NoReturn:
    typer.echo(f"error: cannot read {path}: {error}", err=True)
    raise typer.Exit(1) from None


def _read_text(path: Path) -> str:
    """Read a user-supplied artifact, exiting with a concise message instead of a traceback."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        _input_error(path, error)


def _validate_json_file(model: type[BaseModel], path: Path) -> Any:
    try:
        return model.model_validate_json(_read_text(path))
    except INPUT_ERRORS as error:
        _input_error(path, error)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(_read_text(path))
    except INPUT_ERRORS as error:
        _input_error(path, error)


def _result(path: Path) -> Any:
    try:
        return validate_document(load_data(path))
    except INPUT_ERRORS as error:
        _input_error(path, error)


def _workflow_document(eir_file: Path):
    try:
        validation = validate_document(load_data(eir_file))
    except INPUT_ERRORS as error:
        _input_error(eir_file, error)
    if not validation.ok:
        typer.echo(json.dumps(validation.as_dict(), sort_keys=True))
        raise typer.Exit(1)
    assert validation.document is not None
    return validation.document


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
    try:
        graph = EngineeringStateGraph.load(file)
    except INPUT_ERRORS as error:
        _input_error(file, error)
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
        try:
            adapter = FixtureSimulatorAdapter.from_file(fixture)
        except INPUT_ERRORS as error:
            _input_error(fixture, error)
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
    manifest = _validate_json_file(ReadOnlyTransportManifest, manifest_file)
    evidence = None
    if evidence_file is not None:
        evidence = _validate_json_file(TransportVerificationEvidence, evidence_file)
    report = assess_transport(manifest, evidence)
    typer.echo(report.model_dump_json())
    if not report.valid:
        raise typer.Exit(1)


@app.command("goal-workflow-review")
def goal_workflow_review(file: Path, backend: str | None = None, allow_simulation: bool = False) -> None:
    """Revalidate a goal-to-evaluate workflow for manual review without executing a step."""
    workflow = _validate_json_file(GoalToEvaluateWorkflow, file)
    policy = ExecutionPolicy(
        allow_read_only=True,
        allow_simulation=allow_simulation,
        allowed_backends={backend} if backend else set(),
    )
    review = workflow.review(default_registry(), policy)
    typer.echo(review.model_dump_json())
    if review.status.value != "ready_for_review":
        raise typer.Exit(1)


@app.command("goal-workflow-plan")
def goal_workflow_plan(workflow_file: Path, eir_file: Path) -> None:
    """Validate an EIR-bound goal workflow plan without model or backend invocation."""
    workflow = _validate_json_file(GoalToEvaluateWorkflow, workflow_file)
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    typer.echo(plan.model_dump_json())
    if plan.status.value != "ready_for_review":
        raise typer.Exit(1)


@app.command("goal-workflow-evidence")
def goal_workflow_evidence(workflow_file: Path, eir_file: Path, evidence_file: Path) -> None:
    """Assess cited workflow evidence without evaluating or executing engineering work."""
    workflow = _validate_json_file(GoalToEvaluateWorkflow, workflow_file)
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    evidence = [EvaluationEvidence.model_validate(item) for item in _read_json(evidence_file)]
    assessment = assess_evaluation_evidence(workflow, plan, evidence)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "ready_for_review":
        raise typer.Exit(1)


@app.command("workflow-context-inspect")
def workflow_context_inspect(workflow_file: Path, eir_file: Path, context_file: Path) -> None:
    """Validate a local redacted context bundle against a deterministic workflow plan."""
    workflow = _validate_json_file(GoalToEvaluateWorkflow, workflow_file)
    policy = ExecutionPolicy()
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    context = _validate_json_file(WorkflowContextBundle, context_file)
    assessment = assess_workflow_context(context, workflow, plan, policy)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "ready_for_review":
        raise typer.Exit(1)


@app.command("review-trace-assess")
def review_trace_assess(workflow_file: Path, eir_file: Path, context_file: Path, evidence_file: Path, trace_file: Path) -> None:
    """Assess a complete local provenance trace without changing workflow state."""
    workflow = _validate_json_file(GoalToEvaluateWorkflow, workflow_file)
    policy = ExecutionPolicy()
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    context = _validate_json_file(WorkflowContextBundle, context_file)
    context_assessment = assess_workflow_context(context, workflow, plan, policy)
    evidence = [EvaluationEvidence.model_validate(item) for item in _read_json(evidence_file)]
    evidence_assessment = assess_evaluation_evidence(workflow, plan, evidence)
    trace = _validate_json_file(WorkflowReviewTrace, trace_file)
    assessment = assess_review_trace(trace, workflow, context_assessment, evidence_assessment, policy)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "ready_for_review":
        raise typer.Exit(1)


def _review_artifacts(workflow_file: Path, eir_file: Path, context_file: Path, evidence_file: Path, trace_file: Path):
    workflow = _validate_json_file(GoalToEvaluateWorkflow, workflow_file)
    policy = ExecutionPolicy()
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    context = _validate_json_file(WorkflowContextBundle, context_file)
    context_assessment = assess_workflow_context(context, workflow, plan, policy)
    evidence = [EvaluationEvidence.model_validate(item) for item in _read_json(evidence_file)]
    evidence_assessment = assess_evaluation_evidence(workflow, plan, evidence)
    trace = _validate_json_file(WorkflowReviewTrace, trace_file)
    trace_assessment = assess_review_trace(trace, workflow, context_assessment, evidence_assessment, policy)
    return workflow, policy, trace_assessment


def _approval_artifacts(workflow_file: Path, eir_file: Path, context_file: Path, evidence_file: Path, trace_file: Path, approval_file: Path):
    workflow, policy, trace_assessment = _review_artifacts(workflow_file, eir_file, context_file, evidence_file, trace_file)
    chain = _validate_json_file(ApprovalChain, approval_file)
    return workflow, policy, chain, assess_approval_chain(chain, trace_assessment, policy)


def _evidence_artifacts(workflow_file: Path, eir_file: Path, evidence_file: Path):
    workflow = _validate_json_file(GoalToEvaluateWorkflow, workflow_file)
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    evidence = [EvaluationEvidence.model_validate(item) for item in _read_json(evidence_file)]
    return workflow, evidence, assess_evaluation_evidence(workflow, plan, evidence)


def _controlled_context_artifacts(workflow_file: Path, eir_file: Path, context_file: Path, schema_file: Path, envelope_file: Path):
    workflow = _validate_json_file(GoalToEvaluateWorkflow, workflow_file)
    policy = ExecutionPolicy()
    plan = build_deterministic_plan(workflow, _workflow_document(eir_file))
    bundle = _validate_json_file(WorkflowContextBundle, context_file)
    context_assessment = assess_workflow_context(bundle, workflow, plan, policy)
    schema = _validate_json_file(ControlledContextSchema, schema_file)
    envelope = _validate_json_file(ControlledContextEnvelope, envelope_file)
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
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in _read_json(seals_file)]
    provenance = assess_evidence_provenance(evidence_assessment, evidence, seals)
    report = _validate_json_file(DeterministicReviewReport, report_file)
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
    report_seal = _validate_json_file(ReportProvenanceSeal, report_seal_file)
    report_provenance = assess_report_provenance(report, report_assessment, report_seal)
    _, _, trace = _review_artifacts(workflow_file, eir_file, context_file, evidence_file, trace_file)
    return policy, approval, report, assess_cross_artifacts(controlled, trace, approval, report_assessment, report_provenance)


@app.command("approval-chain-assess")
def approval_chain_assess(workflow_file: Path, eir_file: Path, context_file: Path, evidence_file: Path, trace_file: Path, approval_file: Path) -> None:
    """Assess a local human approval chain without granting authority or changing workflow state."""
    _, policy, trace_assessment = _review_artifacts(workflow_file, eir_file, context_file, evidence_file, trace_file)
    chain = _validate_json_file(ApprovalChain, approval_file)
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
    descriptor = _validate_json_file(ApprovalPersistenceDescriptor, persistence_file)
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
    record = _validate_json_file(ApprovalRevocationRecord, revocation_file)
    assessment = assess_approval_revocation(record, chain, policy)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "declared":
        raise typer.Exit(1)


@app.command("evidence-provenance-assess")
def evidence_provenance_assess(workflow_file: Path, eir_file: Path, evidence_file: Path, seals_file: Path) -> None:
    """Assess local evidence reference seals without retrieving any evidence content."""
    _, evidence, assessment = _evidence_artifacts(workflow_file, eir_file, evidence_file)
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in _read_json(seals_file)]
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
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in _read_json(seals_file)]
    provenance = assess_evidence_provenance(evidence_assessment, evidence, seals)
    transition = _validate_json_file(WorkflowLifecycleTransition, transition_file)
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
    seal = _validate_json_file(ReportProvenanceSeal, report_seal_file)
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
    report = _validate_json_file(DeterministicReviewReport, report_file)
    seal = _validate_json_file(ReportProvenanceSeal, seal_file)
    provenance = _validate_json_file(ReportProvenanceAssessment, provenance_assessment_file)
    trace = _validate_json_file(WorkflowReviewTrace, trace_file)
    trace_assessment = _validate_json_file(ReviewTraceAssessment, trace_assessment_file)
    manifest = _validate_json_file(ReportSealConsistencyManifest, manifest_file)
    assessment = assess_report_seal_consistency(manifest, report, seal, provenance, trace, trace_assessment)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "consistent":
        raise typer.Exit(1)


@app.command("review-trace-event-consistency-assess")
def review_trace_event_consistency_assess(trace_file: Path, trace_assessment_file: Path, manifest_file: Path) -> None:
    """Compare supplied review-trace event declarations without retrieval, signing, mutation, or execution."""
    trace = _validate_json_file(WorkflowReviewTrace, trace_file)
    trace_assessment = _validate_json_file(ReviewTraceAssessment, trace_assessment_file)
    manifest = _validate_json_file(ReviewTraceEventConsistencyManifest, manifest_file)
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
    policy = _validate_json_file(ExecutionPolicy, policy_file)
    context_bundle = _validate_json_file(WorkflowContextBundle, context_bundle_file)
    context_envelope = _validate_json_file(ControlledContextEnvelope, context_envelope_file)
    trace = _validate_json_file(WorkflowReviewTrace, trace_file)
    report = _validate_json_file(DeterministicReviewReport, report_file)
    review_policy = _validate_json_file(DeterministicReviewPolicy, review_policy_file)
    review_policy_assessment = _validate_json_file(ReviewPolicyAssessment, review_policy_assessment_file)
    manifest = _validate_json_file(PolicyProvenanceConsistencyManifest, manifest_file)
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
    review_policy = _validate_json_file(DeterministicReviewPolicy, review_policy_file)
    review_policy_assessment = _validate_json_file(ReviewPolicyAssessment, review_policy_assessment_file)
    report = _validate_json_file(DeterministicReviewReport, report_file)
    report_assessment = _validate_json_file(DeterministicReportAssessment, report_assessment_file)
    evidence_provenance = _validate_json_file(EvidenceProvenanceAssessment, evidence_provenance_file)
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in _read_json(seals_file)]
    manifest = _validate_json_file(ReviewPolicyEvidenceConsistencyManifest, manifest_file)
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

    evidence_provenance = _validate_json_file(EvidenceProvenanceAssessment, evidence_provenance_file)
    review_policy_evidence = ReviewPolicyEvidenceConsistencyAssessment.model_validate_json(
        _read_text(review_policy_evidence_assessment_file)
    )
    report = _validate_json_file(DeterministicReviewReport, report_file)
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in _read_json(seals_file)]
    manifest = _validate_json_file(EvidenceCaptureConsistencyManifest, manifest_file)
    assessment = assess_evidence_capture_consistency(manifest, evidence_provenance, review_policy_evidence, report, seals)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "consistent":
        raise typer.Exit(1)


@app.command("evidence-capture-lineage-consistency-assess")
def evidence_capture_lineage_consistency_assess(
    capture_manifest_file: Path,
    capture_assessment_file: Path,
    lineage_manifest_file: Path,
) -> None:
    """Compare supplied capture-lineage declarations without retrieval, mutation, or execution."""

    capture_manifest = _validate_json_file(EvidenceCaptureConsistencyManifest, capture_manifest_file)
    capture_assessment = _validate_json_file(EvidenceCaptureConsistencyAssessment, capture_assessment_file)
    lineage_manifest = _validate_json_file(EvidenceCaptureLineageConsistencyManifest, lineage_manifest_file)
    assessment = assess_evidence_capture_lineage_consistency(lineage_manifest, capture_manifest, capture_assessment)
    typer.echo(assessment.model_dump_json())
    if assessment.status.value != "consistent":
        raise typer.Exit(1)


@app.command("evidence-gating-consistency-assess")
def evidence_gating_consistency_assess(
    lineage_manifest_file: Path,
    lineage_assessment_file: Path,
    dispatch_assessment_file: Path,
    report_file: Path,
    manifest_file: Path,
) -> None:
    """Compare supplied evidence-gating declarations without retrieval, mutation, or execution."""

    lineage_manifest = _validate_json_file(EvidenceCaptureLineageConsistencyManifest, lineage_manifest_file)
    lineage_assessment = _validate_json_file(EvidenceCaptureLineageConsistencyAssessment, lineage_assessment_file)
    dispatch_assessment = _validate_json_file(DispatchEligibilityAssessment, dispatch_assessment_file)
    report = _validate_json_file(DeterministicReviewReport, report_file)
    manifest = _validate_json_file(EvidenceGatingConsistencyManifest, manifest_file)
    assessment = assess_evidence_gating_consistency(manifest, lineage_manifest, lineage_assessment, dispatch_assessment, report)
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
    seal = _validate_json_file(ReportProvenanceSeal, report_seal_file)
    provenance = assess_report_provenance(report, assessment, seal)
    transition = _validate_json_file(ReportLifecycleTransition, transition_file)
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
    manifest = _validate_json_file(ProvenanceConsistencyManifest, manifest_file)
    seals = [EvidenceProvenanceSeal.model_validate(item) for item in _read_json(seals_file)]
    report = _validate_json_file(DeterministicReviewReport, report_file)
    evidence_provenance = _validate_json_file(EvidenceProvenanceAssessment, evidence_provenance_file)
    report_assessment = _validate_json_file(DeterministicReportAssessment, report_assessment_file)
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
    review_policy = _validate_json_file(DeterministicReviewPolicy, policy_file)
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
    review_policy = _validate_json_file(DeterministicReviewPolicy, policy_file)
    policy_assessment = assess_review_policy(review_policy, report, cross)
    manifest = _validate_json_file(ReadOnlyTransportManifest, transport_manifest_file)
    transport_evidence = _validate_json_file(TransportVerificationEvidence, transport_evidence_file)
    transport = assess_transport(manifest, transport_evidence)
    sandbox = _validate_json_file(SandboxAssessment, sandbox_assessment_file)
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
    chain = _validate_json_file(ApprovalChain, approval_file)
    approval = assess_approval_chain(chain, trace_assessment, policy)
    manifest = _validate_json_file(ReadOnlyTransportManifest, transport_manifest_file)
    evidence = _validate_json_file(TransportVerificationEvidence, transport_evidence_file)
    transport = assess_transport(manifest, evidence)
    sandbox = _validate_json_file(SandboxAssessment, sandbox_assessment_file)
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
    try:
        checkpoint = WorkflowCheckpoint.load(file)
    except INPUT_ERRORS as error:
        _input_error(file, error)
    result = checkpoint.revalidate(default_registry(), policy)
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
    try:
        checkpoint = WorkflowCheckpoint.load(file)
    except INPUT_ERRORS as error:
        _input_error(file, error)
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
