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
