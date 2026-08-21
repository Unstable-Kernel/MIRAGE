# Evidence-gating declaration consistency

This local-only assessment compares supplied evidence-gating bindings against an ineligible dispatch assessment, capture-lineage declarations, and report evidence citations. It can prove that supplied denial reasons and identifiers agree, but it never authorizes dispatch or execution.

| Input | Deterministic check | Explicit non-goal |
|---|---|---|
| Dispatch assessment | Workflow identity, explicit ineligible state, declared denial reasons, and disabled execution | Dispatch, authority mutation, or policy enforcement |
| Capture-lineage records | Manifest identity, validated capture identifier, and evidence binding | Capture collection, ordering, or source retrieval |
| Report | Workflow identity, section placement, and evidence citation | Rendering, publication, or engineering claim generation |

The assessment always returns `execution_permitted: false`. It has no live transport, simulator, sandbox, credential, retrieval, signature, witness, mutation, or external-side-effect path.
