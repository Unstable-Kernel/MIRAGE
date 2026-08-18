from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

import typer

from .eir import load_data, validate_document

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
