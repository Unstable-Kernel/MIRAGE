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
from .runtime import CapabilityExecutor, ExecutionLedger, ExecutionPolicy, ExecutionRequest, WorkflowCheckpoint, default_registry

app = typer.Typer(help="MIRAGE engineering compiler and runtime CLI")


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
) -> None:
    """Execute only through the policy-gated local runtime; no host commands are accepted."""
    request = ExecutionRequest(
        capability_id=capability_id,
        backend=backend,
        policy=ExecutionPolicy(allow_simulation=allow_simulation, allowed_backends={backend}),
    )
    audit_ledger = ExecutionLedger(ledger) if ledger else None
    result = asyncio.run(CapabilityExecutor(default_registry(), ledger=audit_ledger).execute(request))
    typer.echo(result.model_dump_json())
    if result.status.value != "succeeded":
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
