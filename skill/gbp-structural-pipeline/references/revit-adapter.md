# Revit Adapter

## Purpose

Use this reference when Revit is the checking model, BIM intermediary, or exchange stop.

## Role Of Revit

Revit is used for:
- visual review
- BIM coordination
- level and grid inspection
- human checking of framing intent
- downstream exchange control

Revit is not used as the authoritative structural calculation engine.
Revit is not the source of truth.

## Automation Boundary

Revit 2023 API work must run inside a Revit-controlled process:
- compiled Revit add-in
- macro
- Dynamo / pyRevit-style in-process bridge
- RevitCoreConsole when available and suitable

Standalone Python scripts in this skill may generate neutral JSON, review DXF, logs, or add-in input payloads. They should not claim to directly create Revit elements through `RevitAPI.dll` unless an in-process Revit command or add-in is present.

## Input Expectations

The Revit adapter should consume the neutral structural model, not raw GBP directly.

Required mapped entities:
- levels
- grids
- columns
- walls
- framing members
- slabs
- openings

## Mapping Rules

- Keep `source_of_truth` as `json`.
- Preserve neutral IDs in Revit parameters whenever possible.
- Keep grid names exactly consistent with the neutral model.
- Keep level names stable and ordered.
- Never flatten multi-level models into a single framing plan unless the user explicitly requests a legacy 2D overlay. Separate the Revit/DXF review output by standard floor type or explicit `level_id`.
- For tall commercial GBP projects, identify at least these standard floor groups when present: basement typical, ground floor, low shopping floors, podium roof / transfer floor, typical office floor, sky garden/refuge floor, roof/height limit.
- Use compact standard-floor JSON for review import. Do not import fully expanded repeated office floors into Revit unless the importer has a batching/expansion mode.
- If the importer detects an excessive review element count, stop and ask for compact standard-floor input instead of letting Revit hang.
- Show member seed dimensions in Revit element names, marks/comments, or view notes.
- Separate model elements from review-only annotations.
- Record which entities were auto-created versus manually revised in Revit.

## Review Workflow

1. import the neutral model
2. visualize framing against grids and levels
3. review obvious geometry issues
4. mark review comments or overrides
5. export reviewed state or approved mapping back to JSON

Only approved changes may return to JSON.

## Guardrails

- Do not allow Revit-only manual edits to silently replace the JSON source of truth.
- If Revit geometry deviates materially, push the approved change back into JSON with traceability.
- Keep temporary checker annotations out of solver-facing export when they are not structural entities.
- Prefer one-way-first control:
  - `JSON -> Revit` is the primary flow
  - `Revit -> JSON` is an approval-controlled review flow

## Recommended Metadata

For each mapped object, store:
- neutral ID
- adapter status
- review status
- source confidence
- last sync direction

## Sync Directions

- `JSON -> Revit`: preferred for initial import
- `Revit -> JSON`: allowed only for approved review changes
- `Revit -> ETABS/YJK/SAFE`: allowed through controlled export paths, not as an unmanaged shortcut
