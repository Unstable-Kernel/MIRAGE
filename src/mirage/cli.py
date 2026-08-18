from __future__ import annotations

import asyncio
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

import typer

from .eir import load_data, validate_document
from .knowledge import EngineeringStateGraph
from .runtime import (
    BackendSandboxCapabilities,
    CapabilityExecutor,
    CoppeliaSimReadOnlyAdapter,
    ExecutionLedger,
    ExecutionPolicy,
    ExecutionRequest,
    FixtureSimulatorAdapter,
    SandboxEnvelope,
    WorkflowCheckpoint,
    assess_sandbox,
    default_inspection_backends,
    default_registry,
)

app = typer.Typer(help="MIRAGE engineering compiler and runtime CLI")
FIXTURE_ARGUMENT = typer.Argument(default=None, help="Deterministic read-only fixture JSON path.")


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
