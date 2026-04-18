# Precheck Engine

## Purpose

Use this reference when screening a model before formal solver export.

## Scope

Prechecks are quick engineering filters. They are not formal code compliance.

## Rule Categories

### Geometry integrity

- unresolved grids
- unsupported perimeter segments
- floating members
- duplicate or overlapping members
- disconnected cores or walls

### Structural plausibility

- beam span-depth screening
- slab thickness screening
- column continuity screening
- abrupt vertical discontinuity
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

## Severity Levels

- `info`: worth noting, not blocking
- `warning`: plausible but needs review
- `error`: blocks seed export or design confidence

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

If only prechecks are complete, the model remains `review-grade` unless the user explicitly wants an `analysis-seed-grade` handoff with open warnings.
