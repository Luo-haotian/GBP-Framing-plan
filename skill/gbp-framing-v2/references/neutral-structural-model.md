# Neutral Structural Model

## Purpose

Use this reference when defining or extending the JSON contract that sits between GBP interpretation, Revit, and analysis software.

## V1 Scope Boundary

This V1 model includes only:
- `Intent Model`
- `Analysis Seed Model`

This V1 model excludes:
- reinforcement
- detailed design results
- code-specific design outputs

## Two-Part Model

### 1. Intent Model

Use for extracted or inferred structural intent:
- grids
- levels
- geometry
- topology
- candidate member types
- keepouts
- uncertainty

### 2. Analysis Seed Model

Use for solver-facing inputs:
- materials
- sections
- boundary conditions
- loads
- load combinations
- analysis options

Do not collapse these layers unless the project is very small and the user explicitly wants a merged contract.

## Required Root Shape

```json
{
  "metadata": {},
  "source_of_truth": "json",
  "coordinate_system": {},
  "intent_model": {},
  "analysis_seed_model": {},
  "precheck": {}
}
```

## Required Metadata

- version
- source
- confidence
- units

## Required Intent Model Shape

```json
{
  "grids": [],
  "levels": [],
  "boundaries": [],
  "functional_zones": [],
  "columns": [],
  "beams": [],
  "walls": [],
  "slabs": [],
  "openings": [],
  "uncertainty": []
}
```

## Required Analysis Seed Shape

```json
{
  "materials": [],
  "sections": [],
  "loads": [],
  "load_combinations": [],
  "boundary_conditions": [],
  "analysis_options": []
}
```

## Required Precheck Shape

```json
{
  "status": "pending",
  "issues": []
}
```

## Identity Rules

- Every entity gets a stable ID.
- IDs should survive adapter hops where possible.
- IDs should be unique within the model.
- Keep source traceability:
  - source drawing
  - source sheet
  - source entity or note
      - assumption basis

## Independent Element Contract

Every relevant element should carry these fields directly or through a linked relation block:

- `id`
- `mark`
- `source`
- `traceability`
- `level` / `storey`
- `geometry`
- `structural_role`
- `section_seed`
- `status`
- `supported_by`
- `supports`
- `load_path`
- `downstream_impact`

Allowed `status` values:

- `confirmed`: drawing/brief/code/approved decision supports the element
- `assumed`: review-grade assumption
- `needs_review`: human review required
- `transfer_required`: vertical discontinuity or transfer behavior must be analyzed

Allowed `downstream_impact` values:

- `DXF`
- `Revit`
- `ETABS`
- `future_YJK`

Support relations should be object IDs, not free-text descriptions, whenever possible.

## Units Rules

- Declare units at the top level.
- Use one geometric unit system inside each payload.
- Do not infer units from section labels alone.
- Keep coordinate system ownership explicit:
  - global project coordinates at root
  - local or element-specific references only when required

## Uncertainty Contract

Each uncertain item should record:
- entity ID
- field name
- confidence
- reason
- evidence path
- fallback assumption if used

## Adapter Boundary

The neutral model should not contain:
- Revit family IDs as primary identifiers
- ETABS local object handles as primary identifiers
- YJK-only layer names as primary identifiers
- solver result envelopes as core model state
- reinforcement schedules as core model state

Those belong in adapter-specific metadata blocks if needed.

## Recommended Next Reference

When the task needs concrete field definitions or validation, read `references/neutral-structural-schema.md`.
