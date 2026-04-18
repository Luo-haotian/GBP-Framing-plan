# System Architecture

## Purpose

Use this reference when the task is to explain, design, or implement the end-to-end `GBP -> JSON -> Revit -> analysis` pipeline.

## Core Pipeline

```text
GBP / PDF / DXF / image
-> geometry extraction
-> neutral structural JSON
-> Revit review model
-> ETABS / YJK / SAFE analysis seeds
-> analysis results and failures
-> AI explanation and iteration
```

## Ownership Rules

- `GBP source` owns raw architectural intent and visible dimensions.
- `Intent Model` owns extracted structural geometry and topology.
- `Analysis Seed Model` owns analysis inputs such as materials, sections, loads, combinations, and settings.
- `Revit model` owns BIM coordination state and human review state.
- `ETABS/YJK/SAFE` own formal structural analysis and design-check results.

## Design Principles

- Neutral JSON is the source of truth.
- Revit is the BIM and checking hub, not the calculation authority.
- Formal code compliance comes from analysis software, not the LLM.
- ETABS is the first-priority analysis route, YJK is the second, and SAFE follows as a slab or foundation branch.
- AI may infer and screen, but must preserve uncertainty and traceability.
- Each layer should be replaceable without rewriting the whole stack.
- V1 supports vector PDF and DXF inputs only.

## Layer Map

### Layer 1: Geometry extraction

Input:
- vector PDF
- scanned PDF
- DXF
- image sheets

Output:
- grids
- levels if available
- envelope
- cores
- columns
- walls
- beams if architecturally shown
- slabs / openings / ramps / keepouts
- uncertainty annotations

### Layer 2: Neutral structural model

Split into:
- `Intent Model`
- `Analysis Seed Model`

This layer should be software-agnostic.
This V1 layer does not include reinforcement or detailed design results.

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
- YJK seeds
- SAFE seeds

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
