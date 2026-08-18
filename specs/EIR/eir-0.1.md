# EIR 0.1 Specification

EIR 0.1 is MIRAGE’s canonical JSON/YAML engineering representation. It is language- and simulator-independent.

## Document

An EIR document contains `eir_version`, stable `id`, creation time, document provenance, nodes, relationships, and extension metadata. The supported version is exactly `0.1`.

## Nodes

Nodes use stable identifiers and a typed `type` enum covering Robot, Link, Joint, Sensor, Actuator, Controller, Objective, Constraint, Metric, Experiment, Assumption, and Requirement. Each node carries schema version, provenance, source references, validation status, confidence in `[0,1]`, timestamps, properties, and metadata.

## Relationships

Relationships connect existing node IDs and use `controls`, `senses`, `derives_from`, `depends_on`, `validates`, `contradicts`, `implements`, or `generated_by`. Relationship IDs are unique.

## Invariants

Node and relationship IDs are unique. Relationship endpoints must exist. Confidence must be within `[0,1]`. Unknown engineering units are rejected by the deterministic validator. Unsupported schema versions are rejected. Provenance is required for every document and node/relationship.

## Versioning

Breaking semantic changes require a new EIR version and RFC. Additional metadata may be introduced compatibly, but consumers must not silently ignore required semantics.
