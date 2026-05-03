# Geometry Extraction

## Purpose

Use this reference when extracting structural geometry from GBP drawings.

## V1 Input Boundary

Prioritize:
- vector PDF
- DXF

Fallback only, explicitly flagged:
- scanned PDF
- OCR-assisted scanned PDF
- raster image interpretation

## Mandatory Strategy: Grid First

Do not begin from the building outline alone.

Use this order:
1. register source files and sheets
2. detect gridlines
3. detect grid bubbles and axis labels
4. resolve grid spacing and global coordinate basis
5. extract levels, storeys, and standard-floor grouping
6. extract boundaries
7. extract functional zones
8. extract openings, voids, edge conditions, and keepouts
9. place other geometry relative to the grid
10. mark uncertainty where snapping or inference was needed

Stop after the drawing-understanding blocks if the grid/story/boundary basis is unstable. Do not proceed to final framing or ETABS.

## Extraction Targets

Extract at minimum:
- gridlines and labels
- grid spacing
- levels, storeys, and standard-floor grouping
- building boundary
- site/podium/tower footprints when available
- core and service zones
- functional zones such as mall, office, parking, refuge, plant room, passage, atrium, lobby, and service areas
- walls and major openings
- column locations or candidate column centers if shown
- ramps, circulation-sensitive zones, and parking keepouts
- long-span and transfer-sensitive zones

## Entity Priority

### Tier 1: Backbone geometry

- grids
- levels
- overall dimensions
- title-block scale and units

### Tier 2: Structural-driving geometry

- boundary
- functional zones
- core
- walls
- columns
- openings
- ramps and shafts

### Tier 3: Functional constraints

- parking stalls
- aisles
- turning zones
- circulation keepouts
- no-column zones

## Coordinate Rules

- Use a project coordinate system tied to the resolved grid.
- Prefer axis-relative references such as `B-3 + 1200` when communicating uncertain geometry.
- Store absolute coordinates and axis-relative references together when possible.
- Do not mix `mm` and `m` silently.

## Conflict Resolution

When these disagree:
- drawn vector distance
- dimension text
- scale inference

apply this order unless the drawing explicitly says otherwise:
1. explicit dimension text
2. consistent grid spacing logic
3. vector geometry

Always report the chosen basis.

## Recognition Paths

### Vector-first path

Use when PDF or DXF includes lines, text, or curves that can be parsed deterministically.

## Output Shape

At minimum, produce:

```json
{
  "source_inventory": [],
  "grids": [],
  "levels": [],
  "storey_groups": [],
  "boundaries": [],
  "functional_zones": [],
  "core_zones": [],
  "columns": [],
  "walls": [],
  "openings": [],
  "keepouts": [],
  "uncertainty": []
}
```

## QA Gates

- grid labels are unique and ordered
- grid spacing is numerically consistent
- storey groups are explicit where floors are repeated
- boundary is closed
- functional zones do not silently overlap in conflicting ways
- core is located relative to the grid
- major members do not float without reference geometry
- parking or circulation keepouts are separate from structural members
- unresolved conflicts are listed in `uncertainty`

## Block Outputs

For complex GBP inputs, output these blocks separately before structural design:

- `M02.01_grid_lines`
- `M02.02_boundaries`
- `M02.03_levels_storeys`
- `M02.04_functional_zones`
- `M02.05_openings_keepouts`
- `M02.07_traceability`

## Escalation Triggers

Escalate when:
- grid cannot be resolved confidently
- more than one plausible scale exists
- boundary and dimension strings disagree materially
- core or no-column zones remain ambiguous
- the source package is non-vector and would require OCR

If escalation remains unresolved, stop at `review-grade` and do not claim model readiness.
