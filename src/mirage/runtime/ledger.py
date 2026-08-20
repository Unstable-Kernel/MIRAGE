import hashlib
import json
import os
import re
import tempfile
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from .execution import ExecutionRequest, ExecutionResult

_SECRET_KEY = re.compile(r"(key|token|secret|password|credential)", re.IGNORECASE)
LEDGER_FORMAT_VERSION = "mirage.execution-ledger.v1"


def redact(value: Any, key: str = "") -> Any:
    if _SECRET_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {name: redact(item, name) for name, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


class ExecutionAuditRecord(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    actor: str
    capability_id: str
    version: str | None = None
    backend: str
    status: str
    started_at: datetime
    completed_at: datetime
    policy: dict[str, Any] = Field(default_factory=dict)
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    message: str = ""
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_execution(cls, request: ExecutionRequest, result: ExecutionResult) -> "ExecutionAuditRecord":
        return cls(
            actor=request.actor,
            capability_id=request.capability_id,
            version=result.version,
            backend=request.backend,
            status=result.status.value,
            started_at=result.started_at,
            completed_at=result.completed_at,
            policy=redact(request.policy.model_dump()),
            inputs=redact(request.inputs),
            outputs=redact(result.outputs),
            message=result.message,
        )


class LedgerRetentionAnchor(BaseModel):
    discarded_records: int = Field(gt=0)
    preceding_terminal_digest: str = Field(pattern=r"^[a-f0-9]{64}$")


class LedgerEnvelope(BaseModel):
    format_version: Literal["mirage.execution-ledger.v1"]
    record: ExecutionAuditRecord
    previous_digest: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    retention_anchor: LedgerRetentionAnchor | None = None
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")


class LedgerIntegrityIssue(BaseModel):
    line_number: int | None = None
    message: str


class LedgerIntegrityAssessment(BaseModel):
    status: Literal["empty", "valid", "invalid"]
    valid: bool
    record_count: int
    first_digest: str | None = None
    last_digest: str | None = None
    retention_anchor: LedgerRetentionAnchor | None = None
    issues: list[LedgerIntegrityIssue] = Field(default_factory=list)


class LedgerRetentionResult(BaseModel):
    status: Literal["unchanged", "compacted"]
    max_records: int = Field(gt=0)
    discarded_records: int = Field(ge=0)
    retained_records: int = Field(ge=0)
    retention_anchor: LedgerRetentionAnchor | None = None


class LedgerFormatError(ValueError):
    def __init__(self, line_number: int, message: str) -> None:
        super().__init__(f"ledger line {line_number}: {message}")
        self.line_number = line_number
        self.message = message


class LedgerIntegrityError(RuntimeError):
    pass


@dataclass(frozen=True)
class _LedgerEntry:
    line_number: int
    record: ExecutionAuditRecord
    envelope: LedgerEnvelope | None


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _digest_payload(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _digest_envelope(envelope: LedgerEnvelope) -> str:
    return _digest_payload(envelope.model_dump(mode="json", exclude={"digest"}))


class ExecutionLedger:
    """Local JSONL audit storage with advisory POSIX locking and chained integrity checks.

    The ledger is intentionally local-only. Its digest chain detects accidental or
    unsophisticated edits but does not provide signatures, remote witnessing, or
    distributed coordination.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.lock_path = self.path.with_name(f"{self.path.name}.lock")

    @contextmanager
    def _locked(self, exclusive: bool) -> Iterator[None]:
        try:
            import fcntl
        except ImportError as error:  # pragma: no cover
            raise LedgerIntegrityError("ledger locking requires a POSIX fcntl implementation") from error

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+", encoding="utf-8") as lock_stream:
            mode = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(lock_stream.fileno(), mode)
            try:
                yield
            finally:
                fcntl.flock(lock_stream.fileno(), fcntl.LOCK_UN)

    def _read_entries(self) -> list[_LedgerEntry]:
        if not self.path.exists():
            return []

        entries: list[_LedgerEntry] = []
        for line_number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as error:
                raise LedgerFormatError(line_number, "invalid JSON") from error

            try:
                if "record" in payload or "format_version" in payload:
                    envelope = LedgerEnvelope.model_validate(payload)
                    entries.append(_LedgerEntry(line_number=line_number, record=envelope.record, envelope=envelope))
                else:
                    record = ExecutionAuditRecord.model_validate(payload)
                    entries.append(_LedgerEntry(line_number=line_number, record=record, envelope=None))
            except ValueError as error:
                raise LedgerFormatError(line_number, "invalid ledger record") from error
        return entries

    @staticmethod
    def _assess_entries(entries: list[_LedgerEntry]) -> LedgerIntegrityAssessment:
        if not entries:
            return LedgerIntegrityAssessment(status="empty", valid=True, record_count=0)

        issues: list[LedgerIntegrityIssue] = []
        expected_previous: str | None = None
        envelopes = [entry.envelope for entry in entries]
        first_envelope = envelopes[0]

        for index, entry in enumerate(entries):
            envelope = entry.envelope
            if envelope is None:
                issues.append(LedgerIntegrityIssue(line_number=entry.line_number, message="legacy record has no integrity envelope"))
                continue
            if envelope.previous_digest != expected_previous:
                issues.append(LedgerIntegrityIssue(line_number=entry.line_number, message="previous digest does not match the preceding record"))
            if envelope.digest != _digest_envelope(envelope):
                issues.append(LedgerIntegrityIssue(line_number=entry.line_number, message="record digest does not match canonical content"))
            if envelope.retention_anchor is not None and (index != 0 or envelope.previous_digest is not None):
                issues.append(LedgerIntegrityIssue(line_number=entry.line_number, message="retention anchor is only valid on the first retained record"))
            expected_previous = envelope.digest

        first_digest = first_envelope.digest if first_envelope is not None else None
        last_envelope = envelopes[-1]
        last_digest = last_envelope.digest if last_envelope is not None else None
        anchor = first_envelope.retention_anchor if first_envelope is not None else None
        return LedgerIntegrityAssessment(
            status="valid" if not issues else "invalid",
            valid=not issues,
            record_count=len(entries),
            first_digest=first_digest,
            last_digest=last_digest,
            retention_anchor=anchor,
            issues=issues,
        )

    @staticmethod
    def _envelope(
        record: ExecutionAuditRecord,
        previous_digest: str | None,
        retention_anchor: LedgerRetentionAnchor | None = None,
    ) -> LedgerEnvelope:
        payload = {
            "format_version": LEDGER_FORMAT_VERSION,
            "record": record.model_dump(mode="json"),
            "previous_digest": previous_digest,
            "retention_anchor": retention_anchor.model_dump(mode="json") if retention_anchor else None,
        }
        return LedgerEnvelope(**payload, digest=_digest_payload(payload))

    def _write_envelopes(self, envelopes: list[LedgerEnvelope]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent, prefix=f".{self.path.name}.", delete=False) as stream:
            temporary_path = Path(stream.name)
            for envelope in envelopes:
                stream.write(envelope.model_dump_json() + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.replace(temporary_path, self.path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

    def append(self, record: ExecutionAuditRecord) -> None:
        with self._locked(exclusive=True):
            entries = self._read_entries()
            assessment = self._assess_entries(entries)
            if not assessment.valid:
                raise LedgerIntegrityError("ledger integrity verification failed; append refused")
            envelope = self._envelope(record, assessment.last_digest)
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(envelope.model_dump_json() + "\n")
                stream.flush()
                os.fsync(stream.fileno())

    def verify_integrity(self) -> LedgerIntegrityAssessment:
        if not self.path.exists():
            return LedgerIntegrityAssessment(status="empty", valid=True, record_count=0)
        try:
            with self._locked(exclusive=False):
                return self._assess_entries(self._read_entries())
        except LedgerFormatError as error:
            return LedgerIntegrityAssessment(
                status="invalid",
                valid=False,
                record_count=0,
                issues=[LedgerIntegrityIssue(line_number=error.line_number, message=error.message)],
            )

    def retain(self, max_records: int) -> LedgerRetentionResult:
        if max_records < 1:
            raise ValueError("max_records must be at least 1")
        if not self.path.exists():
            return LedgerRetentionResult(status="unchanged", max_records=max_records, discarded_records=0, retained_records=0)

        with self._locked(exclusive=True):
            entries = self._read_entries()
            assessment = self._assess_entries(entries)
            if not assessment.valid:
                raise LedgerIntegrityError("ledger integrity verification failed; retention refused")
            if len(entries) <= max_records:
                return LedgerRetentionResult(
                    status="unchanged",
                    max_records=max_records,
                    discarded_records=0,
                    retained_records=len(entries),
                    retention_anchor=assessment.retention_anchor,
                )

            discarded_records = len(entries) - max_records
            preceding = entries[discarded_records - 1].envelope
            assert preceding is not None
            anchor = LedgerRetentionAnchor(
                discarded_records=discarded_records,
                preceding_terminal_digest=preceding.digest,
            )
            retained = entries[discarded_records:]
            envelopes: list[LedgerEnvelope] = []
            previous_digest: str | None = None
            for index, entry in enumerate(retained):
                envelope = self._envelope(entry.record, previous_digest, anchor if index == 0 else None)
                envelopes.append(envelope)
                previous_digest = envelope.digest
            self._write_envelopes(envelopes)
            return LedgerRetentionResult(
                status="compacted",
                max_records=max_records,
                discarded_records=discarded_records,
                retained_records=len(envelopes),
                retention_anchor=anchor,
            )

    def records(self) -> Iterable[ExecutionAuditRecord]:
        if not self.path.exists():
            return []
        with self._locked(exclusive=False):
            return [entry.record for entry in self._read_entries()]

    def get(self, request_id: str) -> ExecutionAuditRecord:
        for record in self.records():
            if record.request_id == request_id:
                return record
        raise KeyError(f"execution record not found: {request_id}")
