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
