# Evidence-capture lineage consistency example

This local fixture compares one capture declaration with a supplied capture-consistency assessment and a lineage declaration. It confirms only identifier and reference-graph agreement. It does not collect evidence, establish event order, inspect source content, trust a timestamp, mutate a lifecycle, or authorize execution.

```bash
mirage evidence-capture-lineage-consistency-assess \
  capture-manifest.json \
  capture-assessment.json \
  lineage-manifest.json
```
