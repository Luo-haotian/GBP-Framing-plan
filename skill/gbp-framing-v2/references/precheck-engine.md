# Precheck Engine

## Purpose

Use this reference when screening architectural recognition, structural design, or model conversion outputs before promotion to the next stage.

## Scope

Prechecks are quick engineering filters. They are not formal code compliance.

Every small block should be checked immediately after it is produced. Do not wait until the whole pipeline is complete to discover that a grid, storey, boundary, zoning, support, or adapter assumption is broken.

## Rule Categories

### Architectural recognition completeness

- missing source sheet reference
- unresolved grid label or spacing
- unresolved storey grouping
- incomplete boundary
- unresolved functional zoning
- missing core or service-zone relation
- unclosed opening or void
- keepout/no-column-zone ambiguity
- missing traceability
- drawing conflict not recorded as uncertainty

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

### Model conversion readiness

- architectural JSON cannot be read by converter
- structural JSON cannot be read by converter
- missing element IDs for Revit or ETABS
- missing story data
- missing Revit metadata mapping
- missing ETABS frame/shell property data
- unsupported adapter feature not reported

## Severity Levels

- `info`: worth noting, not blocking
- `warning`: plausible but needs review
- `error`: blocks seed export or design confidence

## Module-Level Checks

Run checks by affected stage and module:

- Stage 1 / A01-A08: source inventory, grid, boundary, storey, zoning, core, opening, keepout, traceability, architectural review DXF
- Stage 2 / S01-S09: schema, required entity fields, unit consistency, support continuity, transfer-required detection, wall-supported slab rule, preliminary sizing, load path
- Stage 3 / C01-C03: Revit metadata, repeated-floor review strategy, ETABS story/property/load/readiness checks, unsupported feature reporting

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
- which stage was screened
- which issues block analysis-seed release
- which modules were touched
- which downstream validators were run

If only prechecks are complete, the model remains `review-grade` unless the user explicitly wants an `analysis-seed-grade` handoff with open warnings.
