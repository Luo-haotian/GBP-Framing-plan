# Geometry Extraction

## Purpose

Use this reference when extracting structural geometry from GBP drawings.

## V1 Input Boundary

Support only:
- vector PDF
- DXF

Do not support in V1:
- scanned PDF
- OCR-only workflows
- raster image interpretation

## Mandatory Strategy: Grid First

Do not begin from the building outline alone.

Use this order:
1. detect gridlines
2. detect grid bubbles and axis labels
3. resolve grid spacing and global coordinate basis
4. place other geometry relative to the grid
5. mark uncertainty where snapping or inference was needed

## Extraction Targets

Extract at minimum:
- gridlines and labels
- grid spacing
- level markers when visible
- building boundary
- core and service zones
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
  "grids": [],
  "levels": [],
  "boundary": {},
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
- boundary is closed
- core is located relative to the grid
- major members do not float without reference geometry
- parking or circulation keepouts are separate from structural members
- unresolved conflicts are listed in `uncertainty`

## Escalation Triggers

Escalate when:
- grid cannot be resolved confidently
- more than one plausible scale exists
- boundary and dimension strings disagree materially
- core or no-column zones remain ambiguous
- the source package is non-vector and would require OCR

If escalation remains unresolved, stop at `review-grade` and do not claim model readiness.
