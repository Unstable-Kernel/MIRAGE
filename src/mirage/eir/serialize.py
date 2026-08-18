from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .schema import EIRDocument


def load_data(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    if file_path.suffix.lower() in {".yaml", ".yml"}:
        value = yaml.safe_load(text)
    else:
        value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("EIR input must be a mapping")
    return value


def load_document(path: str | Path) -> EIRDocument:
    return EIRDocument.model_validate(load_data(path))


def dump_document(document: EIRDocument, path: str | Path) -> None:
    file_path = Path(path)
    payload = document.model_dump(mode="json")
    if file_path.suffix.lower() in {".yaml", ".yml"}:
        file_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    else:
        file_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
