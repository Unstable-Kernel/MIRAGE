import hashlib
import json
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from .schema import EIRDocument
from .validate import validate_document


class EIRSourceFormat(StrEnum):
    JSON = "json"
    YAML = "yaml"


class EIRIngestionStatus(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class LocalEIRSource(BaseModel):
    path: str
    format: EIRSourceFormat
    byte_count: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class EIRIngestionDiagnostic(BaseModel):
    code: str
    message: str
    path: str = ""


class EIRIngestionResult(BaseModel):
    status: EIRIngestionStatus
    source: LocalEIRSource | None = None
    document: EIRDocument | None = None
    diagnostics: list[EIRIngestionDiagnostic] = Field(default_factory=list)

    @property
    def accepted(self) -> bool:
        return self.status == EIRIngestionStatus.ACCEPTED


def _source_format(path: Path) -> EIRSourceFormat | None:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return EIRSourceFormat.JSON
    if suffix in {".yaml", ".yml"}:
        return EIRSourceFormat.YAML
    return None


def _rejected(code: str, message: str, path: str = "") -> EIRIngestionResult:
    return EIRIngestionResult(
        status=EIRIngestionStatus.REJECTED,
        diagnostics=[EIRIngestionDiagnostic(code=code, message=message, path=path)],
    )


def ingest_eir_file(path: str | Path, allowed_root: str | Path | None = None) -> EIRIngestionResult:
    """Read one local JSON or YAML EIR candidate without retrieval or execution.

    The candidate document is passed unchanged to the canonical EIR validator. The
    returned source record adds file format, byte length, and content digest for
    review without mutating document, node, or relationship provenance.
    """

    file_path = Path(path).expanduser()
    source_format = _source_format(file_path)
    if source_format is None:
        return _rejected("UNSUPPORTED_SOURCE_FORMAT", "only local JSON and YAML sources are supported", str(file_path))

    resolved_path = file_path.resolve()
    if allowed_root is not None:
        root = Path(allowed_root).expanduser().resolve()
        try:
            resolved_path.relative_to(root)
        except ValueError:
            return _rejected("SOURCE_OUTSIDE_ALLOWED_ROOT", "source is outside the allowed local root", str(resolved_path))

    try:
        raw_bytes = resolved_path.read_bytes()
    except OSError as error:
        return _rejected("SOURCE_READ_FAILED", "unable to read the local source", str(error.filename or resolved_path))

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return _rejected("SOURCE_ENCODING_INVALID", "source must use UTF-8 encoding", str(resolved_path))

    try:
        data: Any = json.loads(text) if source_format == EIRSourceFormat.JSON else yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError):
        return _rejected("SOURCE_PARSE_FAILED", f"invalid {source_format.value} syntax", str(resolved_path))

    if not isinstance(data, dict):
        return _rejected("SOURCE_NOT_MAPPING", "EIR source root must be a mapping", str(resolved_path))

    validation = validate_document(data)
    if not validation.ok:
        return EIRIngestionResult(
            status=EIRIngestionStatus.REJECTED,
            diagnostics=[EIRIngestionDiagnostic(**error.as_dict()) for error in validation.errors],
        )

    assert validation.document is not None
    return EIRIngestionResult(
        status=EIRIngestionStatus.ACCEPTED,
        source=LocalEIRSource(
            path=str(resolved_path),
            format=source_format,
            byte_count=len(raw_bytes),
            sha256=hashlib.sha256(raw_bytes).hexdigest(),
        ),
        document=validation.document,
    )
