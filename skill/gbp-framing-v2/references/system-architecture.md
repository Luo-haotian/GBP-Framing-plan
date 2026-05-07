# System Architecture

## Purpose

Use this reference when the task is to explain, design, or implement the end-to-end GBP product pipeline.

## Core Pipeline

```text
GBP
-> Architectural JSON + Architectural Review DXF
-> Structural JSON + Structural Review DXF
-> Model Conversion
```

Keep this route concise. Detailed extraction, design control, and validation live inside each stage, not in the route name.

Stage 3 Model Conversion prioritizes:

1. Revit review/coordination conversion
2. ETABS 21.1 model/API conversion

YJK and SAFE are future adapters.

## Ownership Rules

- `GBP source` owns raw architectural intent and visible dimensions.
- `Architectural JSON` owns recognized architectural facts, constraints, traceability, and uncertainty.
- `Structural JSON` owns structural intent, support/load-path relations, preliminary sizing seeds, and analysis seed data.
- `Revit model` owns BIM coordination state and human review state.
- `ETABS` owns the first-priority formal structural analysis and design-check results.
- `YJK/SAFE` are future adapter branches.

## Design Principles

- JSON is the source of truth.
- Architectural recognition and structural design are separate data stages.
- Revit is the BIM and checking hub, not the calculation authority.
- Formal code compliance comes from analysis software, not the LLM.
- ETABS 21.1 is the first-priority analysis route.
- YJK is a future adapter and must not be described as the current main workflow.
- SAFE follows later as a slab or foundation branch.
- AI may infer and screen, but must preserve uncertainty and traceability.
- Each layer should be replaceable without rewriting the whole stack.
- V1 prioritizes vector PDF and DXF inputs. OCR/manual routes are fallback and must be flagged.
- Each module must be independently runnable and must declare downstream impact.

## Stage Map

### M00: Project setup and source intake

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

### Stage 1: Architectural Recognition

Run in controlled blocks:
1. source inventory and sheet index
2. grid line extraction and validation
3. levels, storeys, and standard-floor grouping
4. site/building/podium/tower boundary extraction
5. functional zoning
6. cores and service zones
7. openings, voids, shafts, ramps, atria, edge conditions, and keepouts
8. architectural and brief constraints
9. traceability and uncertainty report

Process each block element by element. Do not collapse weak recognitions into one hard model.

Output:
- `architectural_model.json`
- `architectural_review.dxf`
- `architectural_validation_report.md`
- block-level source maps and uncertainty annotations

Validation after every block:

- compare new data with source sheets
- cross-check grid, story, boundary, zoning, opening, and keepout consistency
- mark missing data, conflicts, and assumptions before continuing

### Stage 2: Structural Design

Split into:
- structural intent
- analysis seed data

This stage consumes `architectural_model.json`. It must not silently reinterpret architectural facts.

Run in controlled blocks:

1. structural grid and support philosophy
2. vertical support system: columns, walls, cores
3. transfer strategy
4. floor system: slabs, beams, long-span zones
5. wall-supported slab checks
6. lateral system intent
7. preliminary sizing and calculation basis
8. load path continuity
9. ETABS handoff requirements

Output:

- `structural_model.json`
- `structural_review.dxf`
- `structural_validation_report.md`
- analysis seed readiness report

Validation after every block:

- architectural completeness check
- architectural intent compliance check
- support continuity and transfer check
- calculation-basis check
- downstream feasibility check

This stage does not include reinforcement, final design results, or construction documents.

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

### Stage 3: Model Conversion

Convert approved JSON data into target models without changing source-of-truth ownership.

Input:

- `architectural_model.json`
- `structural_model.json`
- validation reports

Output:

- Revit review/coordination package
- ETABS 21.1 model/API command plan
- conversion validation reports

Validation after every adapter step:

- JSON readability and required-field completeness
- target model feasibility
- element ID and metadata preservation
- unsupported feature report
- assumptions and conversion limitations

### Revit intermediary

Use Revit to:
- visualize extracted framing
- review levels, grids, and member placement
- coordinate with BIM workflows
- serve as a controlled exchange stop

Rules:
- `JSON -> Revit` is the primary direction.
- `Revit -> JSON` is allowed only for approved review changes.
- `source_of_truth` remains `json`.

### Analysis adapters

Use adapters to convert the neutral model into:
- ETABS seeds
- future YJK seeds
- future SAFE seeds

### Feedback loop

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
