---
name: gbp-framing-v2
description: Interpret Hong Kong GBP architectural drawings into a neutral structural model, Revit review model, and downstream analysis seeds for ETABS first, YJK second, and SAFE later. Use when Codex needs to extract grid-based geometry from vector PDF or DXF drawings, define structural framing intent, prepare code-neutral JSON schemas or exchange payloads, treat Revit as a checking and BIM intermediary, run preliminary prechecks before formal analysis, or design the GBP-to-JSON-to-Revit-to-analysis workflow.
---

# GBP Framing V2

Use this skill as a system-level workflow, not as a one-shot drawing conversion.

The core path is:
`GBP -> geometry extraction -> neutral structural JSON -> Revit review model -> ETABS/YJK/SAFE analysis seed -> result feedback`

## Start By Choosing The Route

Identify the task first. Then load only the references needed for that route.

1. **System architecture / planning**
   - Use when the user wants the overall pipeline, module breakdown, adapter design, or phased implementation plan.
   - Always read `references/system-architecture.md`.
   - Read `references/neutral-structural-model.md` and `references/output-contract.md`.
2. **Geometry extraction from GBP**
   - Use when the user wants geometry extracted from vector PDF or DXF drawings.
   - Always read `references/geometry-extraction.md`.
   - Read `references/hk-code-basis.md` when project constraints or code-derived geometry checks matter.
3. **Neutral structural model authoring**
   - Use when the user wants JSON schema design, intent-model fields, analysis-seed fields, or exchange contracts.
   - Always read `references/neutral-structural-model.md`.
   - Read `references/neutral-structural-schema.md` when the task needs concrete schema structure.
   - Read `references/output-contract.md` when user-facing payload structure matters.
   - Run `scripts/check_neutral_model.py` when a concrete instance needs deterministic reference validation.
4. **Revit intermediary route**
   - Use when the user wants Revit as the checking model, BIM hub, or exchange stop between AI and analysis software.
   - Always read `references/revit-adapter.md`.
   - Read `references/neutral-structural-model.md` for entity ownership and mapping.
   - Run `scripts/neutral_model_to_review_dxf.py` when a review-only DXF should be generated from neutral JSON.
5. **Analysis seed / adapter route**
   - Use when the user wants ETABS, YJK, or SAFE handoff design.
   - Always read `references/analysis-adapters.md`.
   - Read `references/precheck-engine.md` if the task includes screening before formal analysis.
6. **Review / parity / gap assessment**
   - Use when the user wants to compare the skill to an existing spreadsheet, model, office workflow, or prior GBP framing logic.
   - Read `references/parity-and-review.md`.
   - Read only the route-specific references needed to explain the gap clearly.

## Always-Loaded References

For most tasks in this skill, keep these references in scope:
- `references/system-architecture.md`
- `references/neutral-structural-model.md`

Load `references/geometry-extraction.md` whenever the source artifact is a drawing.

Load `references/output-contract.md` whenever the answer should be checker-ready, machine-readable, or milestone-based.

## Required System Stance

- Treat the neutral structural JSON as the system source of truth.
- Treat Revit as a review and BIM intermediary, not as the structural calculation authority.
- Treat ETABS as the first-priority formal analysis engine, YJK as the second, and SAFE as a later slab or foundation-focused branch.
- Split the data model into:
  - `Intent Model`: geometric and topological structural intent from GBP
  - `Analysis Seed Model`: materials, sections, loads, combinations, and analysis settings
- Do not include reinforcement or detailed design results in V1 of the neutral structural model.
- Use a grid-first geometry extraction strategy for vector PDF and DXF drawings.
- Keep uncertainty explicit. Do not convert uncertain recognition into silent hard geometry.
- Do not present AI prechecks or approximations as final code compliance.
- When formal analysis is absent, mark the result as concept-grade or review-grade only.

## Geometry Governance

- Establish gridlines and spacing before extracting boundaries, cores, columns, walls, or openings.
- Express important geometry relative to the grid whenever possible.
- If dimensions, grid spacing, and raw geometry disagree, report the conflict and tag the chosen temporary basis.
- V1 supports vector PDF and DXF only. Do not route scanned drawings through OCR in this version.

## Route-Specific Execution Order

### Geometry extraction route

1. Identify source type: vector PDF, DXF, or mixed vector package.
2. Build the grid backbone first.
3. Derive envelope, core, columns, walls, openings, ramps, and keepout zones relative to the grid.
4. Assign uncertainty tags to weak or conflicting entities.
5. Output an `Intent Model` before discussing framing proposals.

### Neutral model route

1. Define model scope and discipline boundary.
2. Separate `Intent Model` fields from `Analysis Seed Model` fields.
3. Keep stable IDs and coordinate systems explicit.
4. Validate topology and units before adapter design.

### Revit route

1. Map levels, grids, columns, walls, beams, slabs, and openings from the neutral model.
2. Preserve review visibility and traceability back to JSON IDs.
3. Use Revit for checking, coordination, and downstream export readiness.
4. Do not let Revit-only edits silently replace the JSON source of truth.
5. Allow `Revit -> JSON` only for approved review changes.

### Analysis adapter route

1. Run prechecks before formal export when possible.
2. Convert only analysis-relevant entities and metadata to the target adapter.
3. State what was seeded automatically versus assumed manually.
4. Keep failures and governing results available for feedback into JSON.

### Review / parity route

1. Identify which artifact is being compared: old skill, spreadsheet, Revit model, YJK model, or narrative workflow.
2. Compare at the level of engineering intent first, not UI similarity.
3. Report missing branches, hidden assumptions, and brittle manual steps.
4. Recommend updates that improve transferability and executability.

## Output Requirements

Always make the answer explicit about:
- route used
- source artifacts used
- current system boundary
- model status: concept-grade, review-grade, analysis-seed-grade, or analysis-verified
- geometry certainty and unresolved conflicts
- whether Revit is acting as importer, checker, coordinator, or exporter
- whether formal analysis has been completed
- next blocking gap in the pipeline

## Architecture Map

Use these references as the runtime map:
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

Keep responses concise, engineering-led, and explicit about which layer owns each decision.
