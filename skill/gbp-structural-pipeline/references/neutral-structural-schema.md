# Neutral Structural Schema

## Purpose

Use this reference when the task needs the concrete V1 schema structure for the neutral structural model.

## V1 Design Decisions

- Include only `Intent Model` and `Analysis Seed Model`.
- Exclude reinforcement and detailed design results.
- Keep the contract code-neutral.
- Keep `source_of_truth` fixed as `json`.
- Use ETABS-first, YJK-second, SAFE-later adapter readiness.
- Support vector PDF and DXF source packages only in V1.

## Root Contract

The root object should contain:
- `metadata`
- `source_of_truth`
- `coordinate_system`
- `intent_model`
- `analysis_seed_model`
- `precheck`

## Required Metadata Fields

```json
{
  "metadata": {
    "version": "v1",
    "source": "AI",
    "confidence": 0.85,
    "units": "metric"
  }
}
```

Recommended additional metadata:
- `project_id`
- `project_name`
- `created_at`
- `updated_at`
- `input_artifacts`
- `notes`

## Coordinate System

The model must declare:
- global origin
- axis orientation
- length unit
- elevation unit

Recommended fields:
- `type`
- `origin`
- `rotation_degrees`
- `length_unit`
- `elevation_unit`
- `grid_reference_basis`

## Intent Model

Required arrays:
- `grids`
- `levels`
- `columns`
- `beams`
- `walls`
- `slabs`
- `openings`
- `uncertainty`

Recommended optional arrays:
- `boundaries`
- `keepouts`
- `core_zones`

## Analysis Seed Model

Required arrays:
- `materials`
- `sections`
- `loads`
- `load_combinations`
- `boundary_conditions`
- `analysis_options`

## Precheck

Required fields:
- `status`
- `issues`

Recommended statuses:
- `pending`
- `passed`
- `warning`
- `failed`

## ID Rules

- Every object must have a unique `id`.
- Prefix IDs by entity type where practical:
  - `GR-`
  - `LV-`
  - `CO-`
  - `BM-`
  - `WA-`
  - `SL-`
  - `OP-`
  - `MT-`
  - `SC-`
  - `LD-`
  - `LC-`
  - `BC-`

## Mapping Rules

- Geometry-bearing intent entities should be mappable to Revit review objects.
- Analysis seed entities should be sufficient for ETABS-first export.
- YJK and SAFE may consume subsets or transformed views of the same root schema.
- Opening edge beams are explicit structural support elements and may use `beam_role: "opening_edge"`.
- Repeated office/storey layouts should be represented as standard floor groups or templates in analysis options and review outputs; expand every repeated floor only when the target adapter requires it.

## Validation Artifact

Use `references/neutral-structural-schema.json` as the validation schema for this V1 contract.

For deterministic project-side checking, use:
- `scripts/check_neutral_model.py`
- `scripts/neutral_model_to_review_dxf.py`
