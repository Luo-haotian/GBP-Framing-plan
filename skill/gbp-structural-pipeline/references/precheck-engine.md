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

## Mandatory Self-Check Before Delivery

Before presenting a GBP-derived structural layout, independently check and report:
- standard floor groups and explicit levels created
- whether office tower footprint is separated from podium footprint when the GBP section shows a smaller tower
- whether repeated office/storey layouts are compacted into standard floor groups instead of blindly expanded
- whether every slab-bearing level has at least one slab object and a supporting beam/framing system
- whether vertical columns and walls stop/start at the intended levels
- whether member seed dimensions are visible in JSON and Revit review outputs
- whether openings, atrium, lobby, passageway, service core, and office no-column/no-wall zones are preserved
- whether every opening edge has beams or an explicitly identified wall/edge support
- whether beams with long spans have vertical supports or an explicit formal-check warning
- whether the result is concept-grade, review-grade, analysis-seed-grade, or analysis-verified

Do not proceed to Revit/export delivery when the self-check finds missing beams, missing slabs, missing levels, or a flattened standard-floor model.
