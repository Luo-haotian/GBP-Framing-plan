# Precheck Engine

## Purpose

Use this reference when screening a model before formal solver export.

## Scope

Prechecks are quick engineering filters. They are not formal code compliance.

## Rule Categories

### Geometry integrity

- unresolved grids
- unresolved storey grouping
- unsupported perimeter segments
- floating members
- duplicate or overlapping members
- disconnected cores or walls

### Structural plausibility

- beam span-depth screening
- slab thickness screening
- column continuity screening
- abrupt vertical discontinuity
- unmarked transfer-required condition
- missing support relation
- broken load path
- missing lateral system in a non-trivial building

### Functional compatibility

- structural members blocking required circulation
- parking or ramp conflicts
- no-column-zone violations

### Export readiness

- missing levels
- missing sections
- undefined materials
- inconsistent units
- invalid topology for target adapter
- missing entity status
- missing downstream impact

## Severity Levels

- `info`: worth noting, not blocking
- `warning`: plausible but needs review
- `error`: blocks seed export or design confidence

## Module-Level Checks

Run checks by affected module:

- M01/M02: source inventory, grid, boundary, storey, zoning, opening, keepout, traceability
- M03: schema, required entity fields, unit consistency, source-of-truth ownership
- M04: support continuity, transfer-required detection, wall-supported slab rule, preliminary sizing
- M05: DXF readability, Revit metadata, repeated-floor review strategy
- M06: ETABS story/property/load/readiness checks

Do not rerun unrelated modules unless the changed block affects them.

## Example Output

```json
{
  "issues": [
    {
      "type": "span_depth",
      "severity": "warning",
      "entity_id": "B12",
      "message": "Beam span-depth ratio exceeds office screening limit."
    }
  ]
}
```

## Reporting Rule

Always state:
- what was screened
- what was not screened
- which issues block analysis-seed release
- which modules were touched
- which downstream validators were run

If only prechecks are complete, the model remains `review-grade` unless the user explicitly wants an `analysis-seed-grade` handoff with open warnings.
