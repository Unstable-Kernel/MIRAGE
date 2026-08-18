import json

import pytest

from mirage.eir import load_data, validate_document
from mirage.knowledge import EngineeringStateGraph, ESGEvent, ESGEventType
from mirage.runtime import CapabilityDescriptor, CapabilityRegistry, SecurityClass


def make_graph() -> EngineeringStateGraph:
    result = validate_document(load_data("examples/01-validate-eir/robot_model.yaml"))
    assert result.ok and result.document is not None
    return EngineeringStateGraph(project_id="project.demo", eir=result.document)


def test_esg_event_increments_revision_and_round_trips(tmp_path):
    graph = make_graph()
    event = ESGEvent(id="event.created", type=ESGEventType.CREATED, actor="test")
    graph.append_event(event)
    assert graph.revision == 1
    path = tmp_path / "state.json"
    graph.save(path)
    restored = EngineeringStateGraph.load(path)
    assert restored.project_id == graph.project_id
    assert restored.events[0].id == "event.created"
    assert restored.revision == 1


def test_esg_rejects_duplicate_events():
    graph = make_graph()
    event = ESGEvent(id="event.created", type=ESGEventType.CREATED, actor="test")
    graph.append_event(event)
    with pytest.raises(ValueError, match="duplicate ESG event"):
        graph.append_event(event)


def test_urcp_registry_resolves_and_filters():
    registry = CapabilityRegistry(
        [
            CapabilityDescriptor(
                capability_id="inspect_model",
                version="0.1",
                description="Inspect a validated engineering model",
                compatible_backends=["generic"],
            ),
            CapabilityDescriptor(
                capability_id="run_simulation",
                version="0.1",
                description="Run a simulation without physical side effects",
                compatible_backends=["mujoco"],
                security_class=SecurityClass.SIMULATION,
            ),
        ]
    )
    assert registry.get("inspect_model").capability_id == "inspect_model"
    assert registry.list(backend="mujoco")[0].capability_id == "run_simulation"
    assert registry.list(security_class=SecurityClass.READ_ONLY)[0].capability_id == "inspect_model"
    assert json.loads(json.dumps(registry.as_dict()))


def test_urcp_registry_rejects_duplicate_versions():
    descriptor = CapabilityDescriptor(capability_id="validate_eir", version="0.1", description="Validate EIR")
    registry = CapabilityRegistry([descriptor])
    with pytest.raises(ValueError, match="duplicate capability"):
        registry.register(descriptor)
