# System Architecture

## Purpose

Use this reference when the task is to explain, design, or implement the end-to-end `GBP -> JSON -> Revit -> analysis` pipeline.

## Core Pipeline

```text
GBP
-> drawing intake
-> grid/story/boundary/zoning
-> neutral JSON
-> review DXF
-> Revit
-> ETABS 21.1
```

Keep this route concise. Detailed extraction and design control live inside each stage, not in the route name.

## Ownership Rules

- `GBP source` owns raw architectural intent and visible dimensions.
- `Intent Model` owns extracted structural geometry and topology.
- `Analysis Seed Model` owns analysis inputs such as materials, sections, loads, combinations, and settings.
- `Revit model` owns BIM coordination state and human review state.
- `ETABS` owns the first-priority formal structural analysis and design-check results.
- `YJK/SAFE` are future adapter branches.

## Design Principles

- Neutral JSON is the source of truth.
- Revit is the BIM and checking hub, not the calculation authority.
- Formal code compliance comes from analysis software, not the LLM.
- ETABS 21.1 is the first-priority analysis route.
- YJK is a future adapter and must not be described as the current main workflow.
- SAFE follows later as a slab or foundation branch.
- AI may infer and screen, but must preserve uncertainty and traceability.
- Each layer should be replaceable without rewriting the whole stack.
- V1 prioritizes vector PDF and DXF inputs. OCR/manual routes are fallback and must be flagged.
- Each module must be independently runnable and must declare downstream impact.

## Layer Map

### Layer 0: Project setup and source intake

Input:
- vector PDF
- scanned PDF
- DXF
- image sheets

Output:
- source inventory
- sheet index
- extraction route
- source IDs for traceability
- version/run manifest

### Layer 1: Drawing interpretation

Run in controlled blocks:
- grid line extraction and validation
- site/building/podium/tower boundary extraction
- levels, storeys, and standard-floor grouping
- functional zoning
- openings, voids, edge conditions, and keepouts
- architectural and brief constraints
- traceability report

Process each block element by element. Do not collapse weak recognitions into one hard model.

Output:
- grids
- levels and storey groups
- envelope
- cores
- functional zones
- openings / ramps / keepouts
- uncertainty annotations

### Layer 2: Neutral structural model

Split into:
- `Intent Model`
- `Analysis Seed Model`

This layer should be software-agnostic and element-owned.
This V1 layer does not include reinforcement or detailed design results.

Each relevant element should carry or link to:
- stable ID / mark
- source / traceability
- level / storey
- geometry
- structural role
- section seed
- status
- support relation
- load path
- downstream impact

### Layer 3: Revit intermediary

Use Revit to:
- visualize extracted framing
- review levels, grids, and member placement
- coordinate with BIM workflows
- serve as a controlled exchange stop

Rules:
- `JSON -> Revit` is the primary direction.
- `Revit -> JSON` is allowed only for approved review changes.
- `source_of_truth` remains `json`.

### Layer 4: Analysis adapters

Use adapters to convert the neutral model into:
- ETABS seeds
- future YJK seeds
- future SAFE seeds

### Layer 5: Feedback loop

Capture:
- failed members
- drift or deflection warnings
- topology or modeling issues
- revised sizing suggestions

Feed them back into JSON, not only into software-local models.

## Status Levels

- `concept-grade`: geometry and intent only
- `review-grade`: geometry plus prechecks, still no formal analysis
- `analysis-seed-grade`: export-ready for solver input
- `analysis-verified`: checked by ETABS, YJK, or SAFE

## Controlled Change Rule

Change one module at a time:

1. identify the changed module
2. identify upstream inputs
3. identify downstream consumers
4. run the module validator
5. run affected downstream validators only

Run the full pipeline only when the source drawing, coordinate basis, grid backbone, schema contract, or global support/load-path rule changes.

## Iteration Triggers

Re-open only the affected block when:

- grid spacing or labels change
- storey grouping changes
- boundary or footprint changes
- functional zoning or keepout changes
- an upper support lacks lower support
- a transfer member is not marked as transfer
- a wall-supported slab line has a duplicate beam without reason
- Revit review exposes a geometry or metadata mismatch
- ETABS handoff lacks story, property, support, load, or opening data

## Minimum Deliverables By Phase

### Phase 1

- JSON schema
- geometry extraction contract
- Revit adapter design

### Phase 2

- Revit import/export mapping
- precheck engine
- basic topology QA

### Phase 3

- ETABS/YJK/SAFE seed adapters
- results feedback contract

### Phase 4

- closed-loop optimization support
- versioned review workflow
