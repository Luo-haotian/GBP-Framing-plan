# GBP -> Framing -> YJK Interface

## JSON Schema

Use this schema for stable machine handoff.

```json
{
  "meta": {
    "project_name": "string",
    "units": "m",
    "code_basis": "HK CoP 2013/2019 (or user-provided)",
    "assumptions": ["string"]
  },
  "envelope": {
    "polyline": [[0.0, 0.0], [40.0, 0.0], [40.0, 25.0], [0.0, 25.0], [0.0, 0.0]]
  },
  "nodes": [
    { "id": "N1", "x": 0.0, "y": 0.0 },
    { "id": "N2", "x": 8.0, "y": 0.0 }
  ],
  "columns": [
    { "id": "C1", "node": "N1", "section": "600x600" }
  ],
  "beams": [
    { "id": "B1", "start": "N1", "end": "N2", "type": "primary" },
    { "id": "B2", "start": "N2", "end": "N3", "type": "secondary" }
  ],
  "shear_walls": [
    { "id": "W1", "start": "N5", "end": "N6", "role": "core" },
    { "id": "W2", "start": "N10", "end": "N11", "role": "wing" }
  ],
  "load_path_notes": [
    "Gravity load from long-span roof transfers to primary beam grid and then to perimeter/core columns.",
    "Lateral resistance dominated by core walls; wing walls used to reduce torsion."
  ]
}
```

## Logic Guards

- Keep node IDs unique and consistent across all entities.
- Keep coordinates numeric and in one unit system.
- Use `primary` or `secondary` for beam type only.
- Use `core` or `wing` for shear wall role only.
- Close envelope polyline (first point equals last point).
- For non-transfer systems, keep column node coordinates identical across stacked floors.
- Keep service core as a geometric keepout for parking layouts.

## Quick QA Checklist

- Grid spacing mostly within `6m-9m` unless explicitly justified.
- Beam path follows shortest practical load path.
- Core and wing walls do not block essential circulation unless stated.
- Every beam endpoint references an existing node ID.
- Every column references an existing node ID.
- Beams are represented as physical-width entities in DXF (closed profiles), not single centerlines.
- Member dimensions are text-labeled near geometry (`column`, `beam`, `wall`).
- Setting-out dimensions include adjacent axis spacing plus overall dimensions.
- Parking validation passes both:
  1. Rule geometry check (`stall size`, `aisle width`, `turning radius`)
  2. Swept-path proxy check against columns and core keepout
- Framing drawings do not include parking entities; parking layouts are issued as separate drawings.
- Core keepout follows user-specified axis offsets exactly when provided.
- All building-boundary edges are supported by framing (no isolated or unsupported perimeter edge segment).
