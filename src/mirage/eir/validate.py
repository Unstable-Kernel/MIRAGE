from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from .schema import EIRDocument

ALLOWED_UNITS = {"1", "m", "s", "kg", "A", "K", "N", "Pa", "rad", "m/s", "m/s^2", "rad/s"}


@dataclass(frozen=True)
class ValidationErrorItem:
    code: str
    message: str
    path: str = ""

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    document: EIRDocument | None
    errors: list[ValidationErrorItem]

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "errors": [error.as_dict() for error in self.errors]}


def validate_document(data: Any) -> ValidationResult:
    try:
        document = EIRDocument.model_validate(data)
    except ValidationError as exc:
        errors = [
            ValidationErrorItem("SCHEMA_INVALID", error["msg"], ".".join(map(str, error["loc"])))
            for error in exc.errors()
        ]
        return ValidationResult(False, None, errors)

    errors: list[ValidationErrorItem] = []
    node_ids = [node.id for node in document.nodes]
    if len(node_ids) != len(set(node_ids)):
        errors.append(ValidationErrorItem("DUPLICATE_NODE_ID", "node IDs must be unique", "nodes"))
    relationship_ids = [rel.id for rel in document.relationships]
    if len(relationship_ids) != len(set(relationship_ids)):
        errors.append(
            ValidationErrorItem(
                "DUPLICATE_RELATIONSHIP_ID", "relationship IDs must be unique", "relationships"
            )
        )
    known_ids = set(node_ids)
    for index, relationship in enumerate(document.relationships):
        if relationship.source_id not in known_ids or relationship.target_id not in known_ids:
            errors.append(
                ValidationErrorItem(
                    "RELATIONSHIP_ENDPOINT_MISSING",
                    "relationship endpoints must reference existing nodes",
                    f"relationships[{index}]",
                )
            )
    for index, node in enumerate(document.nodes):
        unit = node.properties.get("unit")
        if unit is not None and unit not in ALLOWED_UNITS:
            errors.append(
                ValidationErrorItem(
                    "UNKNOWN_UNIT",
                    f"unit is not in the EIR 0.1 allowlist: {unit}",
                    f"nodes[{index}].properties.unit",
                )
            )
    if document.eir_version != "0.1":
        errors.append(
            ValidationErrorItem("UNSUPPORTED_VERSION", document.eir_version, "eir_version")
        )
    return ValidationResult(not errors, document, errors)
