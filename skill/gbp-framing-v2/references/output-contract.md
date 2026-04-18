# Output Contract

## Purpose

Use this reference when formatting user-facing outputs or machine-readable milestone outputs.

## Required Order

1. route used
2. source artifacts used
3. model status
4. geometry extraction summary
5. neutral model summary
6. Revit intermediary status
7. analysis-seed status
8. open conflicts and next blocking step

## Machine-Readable Deliverables

Depending on route, prefer:
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
