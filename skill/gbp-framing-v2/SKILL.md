---
name: gbp-framing-v2
description: "Interpret Hong Kong GBP architectural drawing packages through a three-stage controlled pipeline: Stage 1 Architectural Recognition outputs architectural JSON and architectural review DXF; Stage 2 Structural Design outputs structural JSON and structural review DXF; Stage 3 Model Conversion sends JSON data to Revit review/coordination and ETABS 21.1 first. Use when Codex needs grid/story/boundary/zoning extraction, traceable architectural elements, independent structural element records, support/load-path relations, transfer-required flags, Revit metadata, ETABS adapter requirements, or module-level QA from GBP/PDF/DXF sources."
---

# GBP Framing V2

Use this skill as a controlled engineering pipeline, not as a one-shot drawing conversion.

Current main route. Keep this route concise and stable:

`GBP -> Architectural JSON + Architectural Review DXF -> Structural JSON + Structural Review DXF -> Model Conversion`

Stage 3 Model Conversion prioritizes Revit review/coordination and ETABS 21.1. The route stays simple. The internal work inside each stage can be detailed and element-by-element.

YJK is a future adapter. Do not present YJK as the current main workflow.

## Start By Choosing The Route

Identify the task first. Load only the references needed for that route.

1. **Product architecture / PRD / module planning**
   - Read `references/system-architecture.md`.
   - Read `references/output-contract.md`.
   - Use when the user asks for product flow, module boundaries, controlled reruns, MVP scope, or version strategy.

2. **Stage 1: Architectural Recognition**
   - Read `references/geometry-extraction.md`.
   - Read `references/hk-code-basis.md` only when code-derived constraints or Hong Kong basis must be stated.
   - Use when the next task is identifying source sheets, grid lines, storeys, boundaries, zoning, cores, openings, keepouts, and traceability from a GBP/PDF/DXF package.
   - Output `architectural_model.json`, `architectural_review.dxf`, and `architectural_validation_report.md` or equivalent block outputs before structural design.

3. **Stage 2: Structural Design / structural JSON**
   - Read `references/neutral-structural-model.md`.
   - Read `references/neutral-structural-schema.md` for concrete field requirements.
   - Read `references/precheck-engine.md` for support, transfer, and load-path validation.
   - Run `scripts/check_neutral_model.py` when a JSON instance must be validated.
   - Output `structural_model.json`, `structural_review.dxf`, and `structural_validation_report.md` or equivalent block outputs.

4. **Structural design logic and prechecks**
   - Read `references/precheck-engine.md`.
   - Read `references/neutral-structural-model.md` for entity ownership and support relations.
   - Use when identifying support continuity, transfer-required conditions, wall-supported slabs, long-span assumptions, or review-grade sizing.

5. **Stage 3: Model Conversion**
   - Read `references/revit-adapter.md`.
   - Read `references/analysis-adapters.md`.
   - Run `scripts/neutral_model_to_review_dxf.py` when generating a review DXF from JSON.
   - Use Revit for review/coordination and ETABS 21.1 as the first analysis conversion target.

6. **Analysis adapter route**
   - Read `references/analysis-adapters.md`.
   - Use ETABS 21.1 as first priority.
   - Treat YJK and SAFE as future adapters unless the user explicitly asks for them.

7. **Review / parity / gap assessment**
   - Read `references/parity-and-review.md`.
   - Use when comparing against old PRDs, spreadsheets, Revit models, ETABS/YJK models, or office workflows.

## Always-Loaded Stance

- Treat JSON as the source of truth at each stage:
  - `architectural_model.json` owns recognized architectural facts and constraints.
  - `structural_model.json` owns structural intent and analysis seed data.
- Treat Revit as review, coordination, and import checking, not as calculation authority.
- Treat ETABS 21.1 as the first-priority formal analysis route.
- Keep YJK as future adapter.
- Split the model into:
  - `Intent Model`: drawing-derived and engineering-intent geometry/topology.
  - `Analysis Seed Model`: materials, sections, supports, loads, load combinations, and analysis options.
- Keep every assumption explicit.
- Stop at `review-grade` when formal analysis is absent.
- Do not claim final design, code compliance, reinforcement design, or construction drawing readiness from AI prechecks alone.

## Modular Execution Order

Use the smallest stage that satisfies the task. For a complex new GBP, begin with Stage 1 only and do not jump to framing, Revit, or ETABS until the architectural backbone is stable.

## Three-Stage Control

### Stage 1: Architectural Recognition

Goal: read the GBP package element by element and output architectural data plus a DXF that can be visually checked.

Controlled blocks:

1. source intake and sheet index
2. grid line extraction and validation
3. level, storey, and standard-floor grouping
4. site, building, podium, and tower boundaries
5. functional zoning
6. cores and service zones
7. openings, voids, shafts, ramps, atria, and edge conditions
8. keepout and no-column zones
9. traceability and uncertainty

Validation after every block:

- compare against source sheets
- cross-check with grid, level, boundary, and zoning data already extracted
- record missing data, conflicts, and assumptions before continuing

### Stage 2: Structural Design

Goal: consume architectural JSON and create structural JSON element by element.

Controlled blocks:

1. structural grid and support philosophy
2. vertical supports: columns, walls, cores
3. transfer-required conditions
4. slabs and floor-system zones
5. beams by role: primary, secondary, transfer, collector, opening-edge
6. wall-supported slab checks
7. lateral system intent
8. preliminary section seeds and calculation basis
9. load-path graph
10. ETABS handoff requirements

Validation after every block:

- check completeness against architectural JSON
- check whether the structural proposal respects architectural intent
- flag missing calculation basis, unsupported elements, and transfer requirements
- keep final design claims blocked until formal analysis exists

### Stage 3: Model Conversion

Goal: convert approved JSON data into downstream models without changing source-of-truth ownership.

Current priority:

1. Revit review/coordination conversion
2. ETABS 21.1 model/API conversion

Validation after every adapter step:

- check JSON readability and required fields
- check target model feasibility
- preserve element IDs and review metadata
- report unsupported features and assumptions

Future adapters, including YJK and SAFE, must stay outside the current main route unless explicitly requested.

## Element-By-Element Governance

Use pile-foundation-style governance: keep the top-level route short, then control the detailed work inside each stage.

### Stage 1 Drawing Recognition Sequence

For each drawing package, identify elements one by one:

1. source sheets, scale, units, and drawing roles
2. grid lines and grid labels
3. storeys, levels, and standard-floor groups
4. site/building/podium/tower boundaries
5. functional zones
6. cores and service zones
7. openings, voids, atria, shafts, ramps
8. keepout and no-column zones
9. edge conditions
10. traceability and uncertainty

Do not merge weak recognitions into a single hard model. Each recognized element needs its own source, confidence, status, and downstream impact.

### Stage 2 Structural Arrangement Sequence

Arrange structural intent element by element:

1. structural grid and support philosophy
2. vertical supports: columns, walls, cores
3. transfer-required upper supports
4. slabs and floor-system zones
5. beams by role: primary, secondary, transfer, collector, opening-edge
6. wall-supported slab conditions
7. lateral system intent
8. preliminary section seeds
9. load-path relations
10. ETABS handoff requirements

Do not finalize a framing scheme until support continuity, transfer conditions, and major architectural conflicts are visible.

### Iteration Triggers

Re-open the relevant element block when:

- grid spacing changes
- storey grouping changes
- a boundary shifts
- a functional zone or keepout changes
- an upper support lacks lower support
- a beam is acting as transfer but is not marked as transfer
- a wall already supports a slab and a duplicate beam appears without reason
- Revit review exposes geometry or metadata mismatch
- ETABS handoff lacks story, support, load, or property data

### M00 Project Setup / Version Control

Confirm source paths, run directory, output directory, version naming, and non-overwrite rules. Create or update a manifest when implementation work touches outputs.

### M01 Drawing Intake

Register sources and choose extraction path:

1. identify source type: vector PDF, DXF, scanned PDF, image, or mixed package
2. index sheets and drawing roles
3. detect scale/unit/coordinate basis
4. create source IDs for traceability
5. mark OCR/manual interpretation as fallback, not confirmed fact

### M02 GBP Understanding / Drawing Interpretation

Run as independent blocks:

1. `M02.01 Grid Line Extraction And Validation`
2. `M02.02 Site / Building / Podium / Tower Boundary`
3. `M02.03 Levels, Storeys, And Standard-Floor Grouping`
4. `M02.04 Functional Zoning`
5. `M02.05 Openings, Voids, Edge Conditions, Keepout Zones`
6. `M02.06 Architectural And Brief Constraints`
7. `M02.07 Traceability Report`

For the next complex GBP, prioritize:

- grid labels and grid spacing,
- story/level grouping,
- boundaries,
- core and service zones,
- atrium/void/opening zones,
- no-column/keepout zones,
- functional zones such as mall, office, parking, refuge, passage, and plant room,
- source traceability and uncertainty.

### M03 JSON Source-Of-Truth Contracts

Write drawing facts, assumptions, structural intent, and analysis seed data into stable JSON contracts. Each element must be independently identifiable and reviewable, but keep the overall route concise.

Stage 1 owns:

- `architectural_model.json`
- recognized architectural facts
- architectural assumptions and uncertainty
- architectural review DXF data

Stage 2 owns:

- `structural_model.json`
- structural intent
- support/load-path relations
- analysis seed data
- structural review DXF data

Every relevant entity should carry or link to:

- `id`
- `mark`
- `source`
- `traceability`
- `level` / `storey`
- `geometry`
- `structural_role`
- `section_seed`
- `status`
- `supported_by`
- `supports`
- `load_path`
- `downstream_impact`

Allowed statuses:

- `confirmed`
- `assumed`
- `needs_review`
- `transfer_required`

### M04 Structural Design Logic

Only run after M02 is stable enough. Split logic into controlled blocks:

1. structural grid and support philosophy
2. vertical support system
3. transfer strategy
4. floor system
5. wall-supported slab rule
6. lateral system intent
7. preliminary sizing
8. load path continuity
9. ETABS handoff requirements

Transfer rule:

If an upper column or wall does not have a lower column/wall support, mark the condition `transfer_required`. Do not treat it as an ordinary beam-column joint.

Wall-supported slab rule:

Do not duplicate beams along wall support lines unless there is a collector, transfer, opening-edge, or detailing reason.

### M05 Review Deliverables

Generate architectural review DXF, structural review DXF, and Revit import outputs from JSON only. Preserve JSON IDs and review metadata. Use compact repeated-floor strategy for standard floors; avoid blindly copying every repeated floor.

### M06 Stage 3 Model Conversion / ETABS 21.1 Handoff

Generate ETABS command plans or API models from JSON. Required handoff data includes stories, frame/shell objects, materials, sections, supports, loads, combinations, and unsupported-feature warnings.

### M07 QA / Validation / Self-Check

Run validators by module and downstream dependency. Report pass/warning/block. Do not upgrade model grade if any blocking QA remains.

### M08 Future Adapters

Use for YJK/SAFE only after the ETABS-first contract is stable or when the user explicitly requests future adapter work.

## Controlled Change Rule

When changing the implementation:

1. identify the module being changed
2. identify upstream inputs
3. identify downstream consumers
4. edit only the relevant block
5. run that module validator
6. run affected downstream validators only
7. append a version/update note in the active PRD or manifest

Run the full pipeline only when the source drawing, coordinate basis, grid backbone, schema contract, or global support/load-path rule changes.

## Output Requirements

Always state:

- route used
- source artifacts used
- model status: `concept-grade`, `review-grade`, `analysis-seed-grade`, or `analysis-verified`
- modules touched
- modules not touched
- assumptions and uncertain items
- validation performed
- next blocking gap

## Architecture Map

- `references/system-architecture.md`
- `references/geometry-extraction.md`
- `references/neutral-structural-model.md`
- `references/neutral-structural-schema.md`
- `references/revit-adapter.md`
- `references/analysis-adapters.md`
- `references/precheck-engine.md`
- `references/parity-and-review.md`
- `references/hk-code-basis.md`
- `references/output-contract.md`
