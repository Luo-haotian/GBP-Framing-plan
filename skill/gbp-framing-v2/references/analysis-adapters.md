# Analysis Adapters

## Purpose

Use this reference during Stage 3 Model Conversion when designing or discussing ETABS, YJK, or SAFE handoff.

## Shared Adapter Contract

Each adapter should declare:
- consumed JSON version
- consumed stage artifacts
- required entities
- required analysis metadata
- unsupported features
- fallback assumptions
- export status

Current priority:

1. ETABS 21.1
2. future YJK after the ETABS-first contract is stable
3. future SAFE or slab/foundation branch after the frame route is stable

## ETABS Adapter

Use for:
- frame and shell analysis seeds
- load patterns and combinations
- drift and force extraction
- iterative analysis feedback

Priority:
- first-priority analysis route for the platform

Primary inputs:

- `architectural_model.json` for stories, grids, boundaries, openings, and architectural constraints
- `structural_model.json` for frame/shell objects, supports, materials, sections, loads, load paths, and transfer flags

Outputs:

- ETABS import plan
- ETABS API command plan or model
- ETABS conversion validation report

Minimum requirements:
- levels / story data
- frame elements
- wall or shell definitions
- materials and sections
- supports
- loads and combinations
- transfer-required flags
- story expansion or repeated-floor mass strategy
- unsupported-feature warnings

## YJK Adapter

Use for:
- Hong Kong / regional workflow compatibility where YJK is the preferred modeling engine
- framing import and structural arrangement review

Priority:
- future route after ETABS-first contract is stable

Minimum requirements:
- grids or coordinate backbone
- member geometry
- wall/core topology
- story consistency
- import QA checklist

## SAFE Adapter

Use for:
- slab and foundation focused analysis
- mat, slab, and local floor-system follow-up

Priority:
- later branch after ETABS and floor/foundation scope is scheduled

Minimum requirements:
- slab geometry
- openings
- supports or spring logic
- loads and combinations relevant to slab/foundation design

## Export Grades

- `seed-ready`: enough for solver model startup
- `review-ready`: enough for human completion in the target software
- `auto-analysis-ready`: enough for scripted solve

Do not claim `auto-analysis-ready` unless all required metadata is present.

## Adapter Ownership Rule

Adapters consume JSON. They must not become the source of truth. Target-software object IDs belong in adapter metadata or result payloads, not as primary JSON identities.

## Result Feedback Contract

Capture at minimum:
- member ID
- governing case
- failure or warning type
- demand / capacity style summary when available
- recommended action

Feed results back into JSON or a related review payload, not only a narrative summary.
