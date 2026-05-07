# Output Contract

## Purpose

Use this reference when formatting user-facing outputs or machine-readable milestone outputs.

## Required Order

1. route used
2. source artifacts used
3. stage used
4. model status
5. modules touched
6. modules not touched
7. architectural recognition summary
8. architectural validation status
9. structural design summary
10. structural validation status
11. model conversion status
12. validation performed
13. open conflicts and next blocking step

## Machine-Readable Deliverables

Depending on route, prefer:
- `source_inventory.json`
- `grid_lines.json`
- `levels_storeys.json`
- `functional_zones.json`
- `geometry.json`
- `architectural_model.json`
- `architectural_review.dxf`
- `architectural_validation_report.md`
- `intent_model.json`
- `analysis_seed.json`
- `structural_model.json`
- `structural_review.dxf`
- `structural_validation_report.md`
- `neutral_structural_model.json`
- `precheck_report.json`
- `revit_mapping_report.md`
- `adapter_status.md`

## Status Vocabulary

- `blocked`
- `assumption-based`
- `review-grade`
- `analysis-seed-grade`
- `analysis-verified`

## Response Rule

Always say what is missing before implying the pipeline is complete.

When the task is a partial module update, explicitly state that unrelated modules were not rerun.

## Route Wording

Use the concise route wording:

`GBP -> Architectural JSON + Architectural Review DXF -> Structural JSON + Structural Review DXF -> Model Conversion`

Put element-level detail under module summaries, not in the route line.

Use these stage names:

- `Stage 1: Architectural Recognition`
- `Stage 2: Structural Design`
- `Stage 3: Model Conversion`
