# Evidence-capture lineage consistency

The evidence-capture lineage consistency assessment compares supplied local declarations to ensure each capture has a matching evidence identifier, every declared predecessor is known, and no declared lineage cycle exists. It can require a prior evidence-capture consistency result, but it never treats a passing comparison as proof of capture order, source existence, collector behavior, or timestamp trust.

| Input | Local check | Explicit non-goal |
|---|---|---|
| Capture manifest | Workflow and capture-manifest identity, capture and evidence bindings | Evidence collection or source retrieval |
| Capture assessment | Consistent state and validated capture identifiers when required | Reassessment of seals, policies, or report references |
| Lineage manifest | Unique declarations, expected evidence identifiers, known predecessors, self-reference, and cycles | Event ordering, timestamp verification, lifecycle mutation, or execution |

```bash
mirage evidence-capture-lineage-consistency-assess \
  examples/23-evidence-capture-lineage-consistency/capture-manifest.json \
  examples/23-evidence-capture-lineage-consistency/capture-assessment.json \
  examples/23-evidence-capture-lineage-consistency/lineage-manifest.json
```

The result is `consistent` only for aligned supplied declarations. Any identifier drift, unknown predecessor, self-reference, or lineage cycle returns structured issues and `execution_permitted: false`.
