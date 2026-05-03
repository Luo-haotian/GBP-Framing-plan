# Output Contract

## Purpose

Use this reference when formatting user-facing outputs or machine-readable milestone outputs.

## Required Order

1. route used
2. source artifacts used
3. model status
4. modules touched
5. modules not touched
6. drawing interpretation summary
7. neutral model summary
8. Revit intermediary status
9. analysis-seed status
10. validation performed
11. open conflicts and next blocking step

## Machine-Readable Deliverables

Depending on route, prefer:
- `source_inventory.json`
- `grid_lines.json`
- `levels_storeys.json`
- `functional_zones.json`
- `geometry.json`
- `intent_model.json`
- `analysis_seed.json`
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

`GBP -> drawing intake -> grid/story/boundary/zoning -> neutral JSON -> review DXF -> Revit -> ETABS 21.1`

Put element-level detail under module summaries, not in the route line.
