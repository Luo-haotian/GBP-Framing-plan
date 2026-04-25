# Structural Layout Rules

## Purpose

Use this reference before generating or reviewing a GBP-derived structural layout.

## Standard Floor Rule

Do not expand every repeated office/storey level during review modeling. Represent repeated floors as standard floor templates or groups, then expand only when a downstream adapter requires individual storeys.

For Figure Q2-style commercial towers:
- basement typical may represent B2-B1
- shopping typical may represent repeated shopping floors
- office typical may represent 3-31F or another repeated office range
- sky garden/refuge is a special variant when the GBP shows different height or use
- roof/height limit is not a normal framing floor

## Support Logic

- Structural layout must support the architectural intent, not merely trace visible outlines.
- If a slab is supported directly by a wall line, do not add a duplicate beam on the same line unless a transfer, edge, diaphragm collector, or local detailing reason exists.
- Every slab-bearing standard floor must have an explicit support system: walls, beams, columns, transfer elements, or a stated slab system such as PT/composite.
- Every opening must have perimeter support. At review level, add edge beams or explicit wall/edge support around atrium, skylight, shaft, and major void openings.
- Long beams must terminate at vertical supports or transfer supports. If a beam span is long because the brief requires a column-free zone, flag the span for formal span-depth, deflection, vibration, and economic section checks instead of silently accepting it.
- Do not place vertical supports inside stated no-column/no-wall zones unless the user explicitly approves a change to the architectural intent.

## Dimension And Review Output Rule

Every review output must make member seed dimensions visible:
- JSON sections must include column sizes, beam sizes, wall thicknesses, and slab thicknesses.
- Revit importer should put dimensions in element names, marks/comments, or review notes.
- DXF review drawings must label columns, beams, walls, and slabs with dimensions, not only IDs.

## Revit Performance Rule

Review imports should use compact standard-floor JSON. Do not import fully expanded repeated-floor JSON into Revit unless the importer has a batching or group expansion mode.

If the importable review element count is high, stop and compact by standard floor group before importing.

## Mandatory Self-Check

Before delivery, report:
- standard floor groups and what each represents
- count of levels, columns, beams, slabs, walls, and openings
- whether every slab-bearing standard floor has supports
- whether every opening has perimeter support
- longest notable beam spans and whether they need formal design checks
- whether member dimensions are visible in JSON, DXF, and Revit review output
- whether the model is concept-grade, review-grade, analysis-seed-grade, or analysis-verified
