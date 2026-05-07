# GBP Structural Pipeline PRD

Version: v0.20

Document status: working PRD

Last updated: 2026-05-07

Primary product route:

`GBP -> Architectural JSON + Architectural Review DXF -> Structural JSON + Structural Review DXF -> Model Conversion`

Stage 3 Model Conversion currently prioritizes:

1. Revit review and coordination conversion
2. ETABS 21.1 analysis model/API conversion

YJK and SAFE are future adapters. They must not be described as the current main workflow.

## 1. Product Purpose

The GBP Structural Pipeline converts Hong Kong GBP architectural drawing packages into traceable architectural data, reviewable structural intent, and downstream Revit/ETABS conversion artifacts.

The product is not a one-time drawing conversion script. It is a controlled engineering system made of small modules. Each module has a defined input, output, validation gate, downstream impact, and rerun boundary.

The product must help engineers answer:

- What architectural information has been recognized from the GBP package?
- Which recognized items are confirmed, assumed, incomplete, or conflicting?
- What structural design intent is proposed from the architectural JSON?
- Which structural elements are supported, unsupported, or transfer-required?
- Which outputs are ready for review in DXF or Revit?
- Which data is ready for ETABS 21.1 conversion?
- Which assumptions block formal design or analysis verification?

## 2. Product Scope

### 2.1 In Scope

- Read GBP PDF/DXF drawing packages and project briefs.
- Recognize architectural information step by step.
- Output architectural JSON as the source of recognized architectural facts.
- Output architectural review DXF for visual checking of the recognition result.
- Generate structural JSON from architectural JSON.
- Output structural review DXF for checking structural arrangement.
- Preserve traceability from JSON objects back to drawings, notes, or explicit assumptions.
- Convert approved JSON data to Revit review/coordination packages.
- Convert approved JSON data to ETABS 21.1 handoff plans or API models.
- Run validation after every small recognition, design, and conversion step.
- Keep version history in one active PRD and append product updates to the version log.

### 2.2 Out Of Scope For Current MVP

- Automatic final structural design.
- Construction drawings.
- Reinforcement design.
- Final code compliance approval.
- Fully solved ETABS analysis feedback.
- Production-grade Revit family mapping.
- Foundation design.
- YJK as the current main route.

### 2.3 Future Scope

- ETABS automated model creation from structural JSON.
- ETABS result ingestion and feedback into JSON, DXF, and Revit review payloads.
- Approved Revit-to-JSON review change workflow.
- YJK adapter after ETABS route is stable.
- SAFE or slab/foundation branch after the frame route is stable.

## 3. Product MVP

The current MVP is a review and coordination MVP, not final structural design automation.

MVP name:

`GBP-Framing Review/Coordination MVP`

MVP includes:

- GBP drawing intake.
- Stage 1 architectural recognition for grids, levels, boundaries, zoning, cores, openings, voids, keepouts, edge conditions, and traceability.
- Architectural JSON.
- Architectural review DXF.
- Stage 2 structural design intent from architectural JSON.
- Structural JSON.
- Structural review DXF.
- Revit review/coordination import with JSON IDs and structural metadata.
- Preliminary ETABS 21.1 handoff plan.
- Validation reports for architectural recognition, structural design, and conversion readiness.

MVP does not include:

- Automatic formal structural analysis.
- Final member sizing approval.
- Construction document production.
- Reinforcement schedules.
- Solver-verified code compliance.

MVP success means:

- A reviewer can inspect recognized architectural information before structural design begins.
- A reviewer can inspect proposed structural intent separately from the architectural recognition result.
- JSON remains the source of truth for both architectural and structural data.
- Revit receives a review/coordination model with stable IDs and metadata.
- ETABS receives a clear handoff plan showing ready data, missing data, unsupported features, and assumptions.
- Transfer-required and load-path risks are visible rather than hidden.

## 4. Product Principles

1. JSON is the source of truth.
2. Architectural recognition and structural design are separate stages.
3. Stage 1 must not silently become structural design.
4. Stage 2 must consume architectural JSON and respect architectural intent.
5. Stage 3 converts JSON to target models and must not replace JSON ownership.
6. Revit is for review, coordination, import checking, and BIM communication.
7. ETABS 21.1 is the first formal analysis target.
8. YJK and SAFE are future adapters.
9. Every assumption must be explicit.
10. Every object must be traceable or clearly assumption-based.
11. Every small step must have a validation gate.
12. A module change should rerun only that module and affected downstream validators.
13. Old outputs and old version history must not be overwritten.

## 5. User Roles

### 5.1 Structural Engineer

Reviews drawing interpretation, structural intent, support continuity, transfer conditions, preliminary sizing, load paths, and ETABS readiness.

### 5.2 BIM / Revit Coordinator

Reviews levels, grids, member locations, repeated-floor strategy, object metadata, and coordination issues in Revit.

### 5.3 Technical Lead

Uses this PRD to understand product direction, stage boundaries, MVP scope, release meaning, and module ownership.

### 5.4 Pipeline Maintainer

Updates one module at a time and runs only the relevant module validators plus affected downstream checks.

## 6. System Architecture

### 6.1 Product Route

```text
GBP
-> Architectural JSON + Architectural Review DXF
-> Structural JSON + Structural Review DXF
-> Model Conversion
```

### 6.2 Stage Ownership

Stage 1 Architectural Recognition owns recognized architectural facts:

- source inventory
- grids
- levels and storey groups
- boundaries
- functional zones
- cores and service zones
- openings, voids, shafts, ramps, atria, and edge conditions
- keepout and no-column zones
- traceability and uncertainty

Stage 2 Structural Design owns structural intent:

- structural grid and support philosophy
- columns, walls, cores, beams, slabs, and structural zones
- support relations
- transfer-required conditions
- wall-supported slab decisions
- lateral system intent
- preliminary section seeds
- load-path graph
- analysis seed data

Stage 3 Model Conversion owns adapter outputs:

- Revit review/coordination package
- Revit parameter and mapping report
- ETABS 21.1 import plan or API command plan
- conversion validation report
- unsupported-feature report

## 7. Stage 1: Architectural Recognition

### Purpose

Convert GBP drawing information into structured architectural JSON before structural design starts.

### Inputs

- GBP PDF/DXF package.
- Drawing title blocks, notes, dimensions, grids, plans, sections, and schedules when available.
- Project brief or requirement notes.
- Optional OCR/vector extraction output.

### Outputs

- `architectural_model.json`
- `architectural_review.dxf`
- `architectural_validation_report.md`
- source-to-object and object-to-source traceability maps

### Current Status

In progress.

### Completed Capability

- Grid-first drawing understanding is established as the required strategy.
- The product recognizes the need for architectural zoning, openings, keepouts, and traceability before structural design.
- Review DXF is required for checking recognition output.

### In-Progress Capability

- Splitting architectural recognition into independent blocks.
- Producing architectural JSON separately from structural JSON.
- Running validation after each small block instead of after the whole pipeline.

### Unresolved Problems

- Page-level and object-level traceability must be completed consistently.
- Source quality and OCR fallback rules need stronger formalization.
- Architectural JSON schema should become a stable implementation contract.

### Downstream Impact

Stage 1 affects all later stages. Changes to grids, levels, boundaries, zones, openings, or keepouts affect structural design, review DXF, Revit, ETABS, and future adapters.

### Validation

- Source inventory check.
- Grid label and spacing check.
- Level/storey consistency check.
- Boundary closure check.
- Zone overlap and containment check.
- Opening/void/keepout check.
- Traceability completeness check.
- Architectural review DXF visual check.

### MVP Required

Yes.

### Estimated Completion

-

## 8. Stage 1 Module Breakdown

### A01 Source Intake And Sheet Index

Purpose:

Register source files, sheet roles, scale, units, coordinate basis, and extraction method.

Outputs:

- source inventory
- sheet index
- source IDs
- extraction quality status

Validation:

- source file exists
- source type is declared
- sheet roles are identifiable or explicitly unresolved
- every later object can reference a source root

MVP required:

Yes.

### A02 Grid Line Extraction And Validation

Purpose:

Build the drawing coordinate backbone.

Outputs:

- grid lines
- grid labels
- grid spacing
- coordinate basis
- grid conflicts

Validation:

- unique labels
- ordered axes
- spacing sanity check
- direction consistency
- source traceability

Downstream impact:

Grid changes affect every geometric and adapter output.

MVP required:

Yes.

### A03 Level, Storey, And Standard-Floor Grouping

Purpose:

Define vertical organization for recognition, structural design, Revit, and ETABS.

Outputs:

- level list
- storey groups
- standard-floor templates
- repeat metadata

Validation:

- elevation order
- duplicate level check
- missing floor group check
- Revit level compatibility
- ETABS story compatibility

Downstream impact:

Level changes affect repeated floors, loads, Revit levels, ETABS stories, and structural continuity.

MVP required:

Yes.

### A04 Site, Building, Podium, And Tower Boundaries

Purpose:

Recognize spatial limits and structural footprint constraints.

Outputs:

- site boundary
- building boundary
- podium boundary
- tower boundary
- boundary traceability

Validation:

- closed polyline check
- boundary-grid alignment check
- scale sanity check
- envelope conflict check

Downstream impact:

Boundary changes affect slabs, edge supports, perimeter beams/walls, Revit, and ETABS shells.

MVP required:

Yes.

### A05 Functional Zoning

Purpose:

Recognize architectural uses that constrain structural layout.

Typical zones:

- mall
- office
- parking
- core
- atrium
- refuge
- passage
- plant room
- lobby
- service area

Outputs:

- zone map
- zone constraints
- no-column or limited-column areas
- zone traceability

Validation:

- zone containment check
- zone overlap check
- keepout consistency
- label/source check

Downstream impact:

Zoning affects column density, span strategy, transfer needs, loads, Revit review, and ETABS load assignments.

MVP required:

Yes.

### A06 Cores And Service Zones

Purpose:

Recognize cores, shafts, vertical circulation, and service zones that affect support and lateral-system logic.

Outputs:

- core zones
- lift/stair/service zones
- vertical continuity hints
- source traceability

Validation:

- core location relative to grid
- level continuity check
- conflict with openings and keepouts

Downstream impact:

Cores affect lateral intent, walls, openings, Revit coordination, and ETABS wall/shell setup.

MVP required:

Yes.

### A07 Openings, Voids, Edge Conditions, And Keepouts

Purpose:

Recognize slab interruptions and architectural restrictions.

Outputs:

- openings
- voids
- shafts
- ramps
- atria
- edge conditions
- keepout and no-column zones

Validation:

- closed opening boundary
- keepout violation check
- slab continuity warning
- edge support requirement check

Downstream impact:

This module affects slab design, beam layout, column placement, DXF, Revit, ETABS meshing, and transfer strategy.

MVP required:

Yes.

### A08 Traceability And Architectural Validation

Purpose:

Make every architectural recognition result reviewable.

Outputs:

- source-to-object map
- object-to-source map
- assumption register
- architectural validation report

Validation:

- every object has source or assumption
- every assumption is visible
- unresolved conflicts are recorded
- architectural review DXF matches architectural JSON

Downstream impact:

Traceability affects reviewer trust, Revit metadata, ETABS assumptions, and future auditability.

MVP required:

Yes.

## 9. Stage 2: Structural Design

### Purpose

Convert architectural JSON into structural JSON and structural review outputs.

### Inputs

- `architectural_model.json`
- architectural validation report
- engineering basis and explicit assumptions
- preliminary materials, sections, loads, and support rules

### Outputs

- `structural_model.json`
- `structural_review.dxf`
- `structural_validation_report.md`
- analysis seed readiness report

### Current Status

In progress.

### Completed Capability

- Structural intent modeling exists at review level.
- Transfer-required conditions are recognized as product-critical.
- Preliminary sizing is treated as review-grade, not final design.
- Wall-supported slab duplication is recognized as a rule-controlled condition.

### In-Progress Capability

- Separating structural JSON from architectural JSON.
- Making support relations and load paths machine-checkable.
- Making transfer-required conditions element-level data.
- Adding stricter calculation-basis checks before ETABS handoff.

### Unresolved Problems

- Some support relations still need graph-level validation.
- Preliminary sizing requires better engineering basis and future solver feedback.
- Formal ETABS analysis has not yet replaced review-grade screening.

### Downstream Impact

Stage 2 affects structural review DXF, Revit structural objects, ETABS model conversion, and future analysis adapters.

### Validation

- Architectural completeness check.
- Architectural intent compliance check.
- Support continuity check.
- Transfer-required check.
- Wall-supported slab rule check.
- Preliminary sizing screen.
- Load-path continuity check.
- ETABS readiness check.

### MVP Required

Yes.

### Estimated Completion

-

## 10. Stage 2 Module Breakdown

### S01 Structural Grid And Support Philosophy

Purpose:

Define how structural supports relate to the architectural grid, zones, and keepouts.

Validation:

- support strategy references architectural JSON
- offsets are explicit
- conflicts with architectural constraints are visible

MVP required:

Yes.

### S02 Vertical Support System

Purpose:

Define columns, walls, core walls, and vertical continuity.

Validation:

- upper supports have lower supports or transfer status
- no support silently violates keepout zones
- core and wall continuity is reviewable

MVP required:

Yes.

### S03 Transfer Strategy

Purpose:

Identify upper supports that do not continue to lower columns or walls.

Rule:

If an upper column or wall lands on a beam and no lower column or wall exists below, mark `transfer_required`. Do not treat it as an ordinary beam-column joint.

Validation:

- every discontinuity is flagged
- every transfer candidate has source and downstream impact
- formal analysis requirement is visible

MVP required:

Yes.

### S04 Floor System

Purpose:

Define slabs, beams, long-span zones, opening-edge members, and floor-system assumptions.

Validation:

- slab support path exists
- long-span assumptions are explicit
- opening edges have support review

MVP required:

Yes.

### S05 Wall-Supported Slab Rule

Purpose:

Avoid duplicate beams along wall-supported slab lines unless there is a collector, transfer, opening-edge, or detailing reason.

Validation:

- duplicate beams have explicit reasons
- wall support is not ignored

MVP required:

Yes.

### S06 Lateral System Intent

Purpose:

Represent core, shear wall, wind, torsion, and drift logic at review and ETABS-preparation level.

Validation:

- lateral intent exists for non-trivial buildings
- wind/torsion remain unresolved until solver analysis

MVP required:

Yes, at review level.

### S07 Preliminary Sizing And Calculation Basis

Purpose:

Provide reasonable section seeds for review and ETABS startup without claiming final design.

Validation:

- span-depth screening
- column capacity screening
- slab thickness screening
- load and system assumptions are explicit
- formal analysis blockers are listed

MVP required:

Yes, as review-grade sizing only.

### S08 Load Path Continuity

Purpose:

Track gravity load path from slab to beam/wall, then to column/wall, then to foundation interface assumptions.

Validation:

- slab support check
- beam support check
- column/wall continuity check
- transfer check
- unsupported element report

MVP required:

Yes.

### S09 ETABS Handoff Requirements

Purpose:

Define what must exist before ETABS conversion.

Validation:

- stories exist
- materials and sections exist
- frame/shell objects are valid
- supports exist
- loads and combinations are declared or explicitly placeholder
- unsupported features are reported

MVP required:

Yes, as preliminary handoff.

## 11. Stage 3: Model Conversion

### Purpose

Convert approved JSON data into Revit and ETABS artifacts while preserving JSON ownership.

### Inputs

- `architectural_model.json`
- `structural_model.json`
- validation reports
- adapter mapping rules

### Outputs

- Revit review/coordination package
- Revit mapping and parameter report
- ETABS 21.1 import plan or API command plan
- conversion validation reports
- unsupported-feature reports

### Current Status

In progress.

### Completed Capability

- Revit review import exists.
- Revit importer includes JSON ID, role, section, status, source, Mark, and Comments metadata.
- ETABS 21.1 is selected as the first analysis target.
- ETABS API starter exists.
- Runtime DLL copy issue has been addressed in the ETABS starter workflow.

### In-Progress Capability

- Converting JSON-derived command plans into full ETABS API model creation.
- Strengthening Revit repeated-floor strategy.
- Validating JSON readability before adapter conversion.
- Reporting unsupported adapter features.

### Unresolved Problems

- Full ETABS model creation from JSON is not yet complete.
- ETABS solver results have not yet been fed back into JSON.
- Revit output remains review/coordination geometry, not production family mapping.

### Downstream Impact

Stage 3 affects coordination, review, and solver startup. It must not silently change architectural or structural JSON.

### Validation

- JSON readability check.
- Required adapter field check.
- Revit parameter visibility check.
- Revit repeated-floor strategy check.
- ETABS story/property/load/support check.
- Unsupported feature report.

### MVP Required

Yes, for Revit review import and preliminary ETABS handoff.

### Estimated Completion

-

## 12. Stage 3 Module Breakdown

### C01 Revit Review / Coordination Conversion

Purpose:

Create a Revit review model from JSON.

Required metadata:

- `GBP_JSON_ID`
- `GBP_STRUCTURAL_ROLE`
- `GBP_SECTION`
- `GBP_MODEL_STATUS`
- `GBP_SOURCE`
- `Mark`
- `Comments`

Rules:

- Use Group, Link, or compact repeated-floor strategy for standard floors.
- Do not blindly copy every repeated floor.
- Revit is not the source of truth.
- Approved Revit review changes must be written back to JSON with traceability.

MVP required:

Yes.

### C02 ETABS 21.1 Conversion

Purpose:

Create an ETABS analysis startup model or command plan from JSON.

Required data:

- stories
- frame objects
- wall/shell objects
- slab/shell objects
- materials
- sections
- supports
- loads
- load combinations
- transfer flags
- unsupported feature warnings

MVP required:

Yes, as preliminary handoff.

### C03 Future Adapter Gate

Purpose:

Keep future adapters separate from the current MVP.

Rules:

- YJK starts only after ETABS-first contract is stable or when explicitly requested.
- SAFE starts only when slab/foundation branch is scheduled.
- Future adapters must consume JSON and report unsupported features.

MVP required:

No.

## 13. Required Entity Contract

Every relevant architectural or structural element must carry these fields directly or through equivalent linked records:

- `id` / `mark`
- `source` / `traceability`
- `level` / `storey`
- `geometry`
- `role`
- `status`
- `support_relation` where applicable
- `load_path` where applicable
- `downstream_impact`

Structural entities also require:

- `structural_role`
- `section_seed`
- `supported_by`
- `supports`

Allowed status values:

- `confirmed`
- `assumed`
- `needs_review`
- `transfer_required`

Downstream impact values:

- `architectural_DXF`
- `structural_DXF`
- `Revit`
- `ETABS`
- `future_YJK`
- `future_SAFE`

## 14. Validation Strategy

Validation must happen after every small step.

### Architectural Validation

Checks:

- source completeness
- grid correctness
- level and storey correctness
- boundary completeness
- zoning completeness
- opening/void/keepout correctness
- traceability completeness
- architectural review DXF consistency

### Structural Validation

Checks:

- architectural input completeness
- architectural intent compliance
- support continuity
- transfer-required detection
- wall-supported slab rule
- preliminary sizing basis
- load-path completeness
- ETABS handoff readiness

### Conversion Validation

Checks:

- JSON readability
- required adapter fields
- Revit metadata
- repeated-floor strategy
- ETABS story and object feasibility
- unsupported features
- assumptions and limitations

## 15. Controlled Change Workflow

Each implementation change must follow this workflow:

1. Identify the stage and module being changed.
2. Identify upstream inputs.
3. Identify downstream outputs.
4. Update only the relevant code or data block.
5. Run that module validator.
6. Run affected downstream validators only.
7. Add an entry to the Version Update Log.

Full-pipeline rerun is allowed only when:

- source drawing changes,
- coordinate system changes,
- grid backbone changes,
- schema has a breaking change,
- global support/load-path rule changes,
- or the user explicitly requests a full refresh.

## 16. Release Grades

### Concept-Grade

Drawing interpretation or structural intent exists, but validation is incomplete.

### Review-Grade

Geometry, intent, and assumptions are good enough for visual review and coordination. Formal analysis is not complete.

### Analysis-Seed-Grade

The model has enough stories, properties, support data, loads, combinations, and topology to create a formal analysis model.

### Analysis-Verified

The model has been run in ETABS or another approved solver, and the results have been reviewed and fed back into the product workflow.

Current product grade:

`Review-grade / ETABS-preparation`

## 17. Release Gates

| Gate | Review MVP | Analysis-Seed | Analysis-Verified |
| --- | --- | --- | --- |
| Source inventory | required | required | required |
| Grid extraction | required | required | required |
| Level and storey grouping | required | required | required |
| Boundary extraction | required | required | required |
| Functional zoning | required | required | required |
| Openings and keepouts | required | required | required |
| Architectural JSON | required | required | required |
| Architectural review DXF | required | optional | optional |
| Structural JSON | required | required | required |
| Structural review DXF | required | optional | optional |
| Support continuity | review-grade | required | solver-reviewed |
| Transfer-required detection | required | required | solver-reviewed |
| Preliminary sizing | review-grade | required | solver-updated |
| Revit review import | required | optional | optional |
| ETABS handoff plan | required | required | replaced by solved model |
| ETABS analysis run | not required | not required | required |
| Code-cited final checks | not required | partial | required |

## 18. Implementation Work Packages

### WP-00 Version Manifest

Module:

M00

Goal:

Record input artifacts, output artifacts, stage, module, upstream dependency, downstream dependency, validation status, version, and tag.

### WP-01 Architectural Recognition Blocks

Module:

A01-A08

Goal:

Implement independent architectural blocks for source intake, grid, levels/storeys, boundaries, zoning, cores, openings/voids/keepouts, traceability, and architectural review DXF.

### WP-02 Architectural JSON Contract

Module:

Stage 1

Goal:

Define and validate `architectural_model.json`.

### WP-03 Structural JSON Contract

Module:

Stage 2

Goal:

Define and validate `structural_model.json` as a consumer of architectural JSON.

### WP-04 Support, Transfer, And Load Path Checks

Module:

S02, S03, S08

Goal:

Make support continuity, transfer-required status, and load paths machine-checkable.

### WP-05 Review DXF Outputs

Module:

Stage 1 and Stage 2

Goal:

Generate separate architectural and structural DXF review outputs.

### WP-06 Revit Conversion

Module:

C01

Goal:

Improve Revit review import, metadata visibility, and compact repeated-floor strategy.

### WP-07 ETABS 21.1 Conversion

Module:

C02

Goal:

Move from ETABS handoff plan to JSON-driven ETABS API model creation.

### WP-08 QA Gates

Module:

All stages

Goal:

Create stage-level and block-level validators so one change only reruns the affected module and downstream checks.

## 19. Version Update Log

This PRD is intended to remain the single active PRD. Future updates should append to this section instead of creating separate standalone PRDs, unless a major product reset is approved.

### v0.11 - Import-Only Baseline

Product meaning:

- Established the initial concept of converting GBP-derived information into importable structural review artifacts.
- Focus was on proving that an import route could exist.

Limitations:

- The workflow was not yet modular.
- Source-of-truth ownership and downstream validation were not yet clear enough.

### v0.12 - Supported Framing Correction

Product meaning:

- Improved the idea that generated framing must be structurally supported, not just geometrically drawn.
- Began moving from geometry output toward structural intent.

Limitations:

- The product still needed better control over architectural open space and module-level reruns.

### v0.13 - Mall Open-Space Correction

Product meaning:

- Recognized that commercial/mall space cannot be over-filled with columns.
- Strengthened the requirement that architectural function must constrain structural layout.

Limitations:

- Long-span strategy remained review-level and required formal analysis.

### v0.14 - Opening And Local Cleanup

Product meaning:

- Improved handling of openings and local conflicts.
- Moved toward cleaner review geometry.

Limitations:

- Still needed stronger sizing logic and explicit transfer rules.

### v0.15 - Preliminary Sizing Correction

Product meaning:

- Added more realistic preliminary sizing philosophy.
- Distinguished review-grade sizing from final design.
- Made long-span and PT/composite assumptions more explicit.

Limitations:

- Formal ETABS analysis was still not available.
- Preliminary sizing remained a screening step, not final design.

### v0.16 - DXF / Revit / ETABS Preparation

Product meaning:

- Improved DXF review readability.
- Strengthened Revit review import metadata.
- Established ETABS 21.1 as the first-priority analysis interface.
- Added ETABS API starter and handoff planning.
- Identified transfer-required conditions as a key engineering blocker.

Limitations:

- No full ETABS model had been created from JSON.
- No ETABS analysis had been run.
- Revit remained review geometry, not production family mapping.

### v0.17 - Modular PRD And Controlled Pipeline Definition

Product meaning:

- Reframed the work as a single long-lived product PRD.
- Defined module boundaries from drawing intake through ETABS handoff.
- Defined block-level development and downstream-only validation.
- Confirmed JSON-Revit-ETABS as the current main route.
- Confirmed YJK as a future adapter.
- Defined review/coordination MVP boundaries.

Limitations:

- This version was mainly product and process definition.

### v0.18 - Skill And Element-Control Contract Update

Product meaning:

- Updated the active GBP skill direction from legacy YJK-first wording to JSON-Revit-ETABS-first workflow.
- Added independent element contract requirements for status, support relations, load path, and downstream impact.
- Extended the neutral schema to support independent element fields and functional zones.
- Added optional validator mode for independent-field completeness checks.

Limitations:

- Existing models were not fully backfilled with all independent element fields.
- Grid/story/boundary extraction blocks still needed implementation.

### v0.19 - Concise Route With Element-Level Governance

Product meaning:

- Kept the product route concise.
- Moved complexity into element-by-element drawing understanding and structural arrangement stages.
- Clarified that grid lines, storeys, boundaries, zoning, openings, keepouts, traceability, supports, transfer conditions, and load paths are internal control blocks.

Limitations:

- The overall route was still too long for global product control.
- Architectural recognition and structural design were not separated strongly enough.

### v0.20 - Three-Stage Product Architecture

Product meaning:

- Reorganized the pipeline into three product stages:
  - Stage 1 Architectural Recognition
  - Stage 2 Structural Design
  - Stage 3 Model Conversion
- Established `architectural_model.json` and `architectural_review.dxf` as Stage 1 outputs.
- Established `structural_model.json` and `structural_review.dxf` as Stage 2 outputs.
- Defined Stage 3 Model Conversion as Revit and ETABS 21.1 first.
- Added validation after every small architectural, structural, and conversion block.
- Clarified that the current MVP is a review/coordination MVP, not final structural design automation.
- Preserved YJK and SAFE as future adapters only.

Limitations:

- Stage-separated JSON schemas still need implementation.
- Architectural and structural review DXF generation need to be separated in code.
- ETABS full API model creation remains future implementation work.

## 20. Open Decisions

- Standard tag naming convention.
- Final branch alignment for this product line.
- Architectural JSON schema file location and naming.
- Structural JSON schema migration strategy from the current neutral schema.
- How to store validation results after every small block.
- Transfer strategy preference when architectural constraints conflict with direct vertical continuity.
- Timing for ETABS automated model creation.
- Timing for future YJK adapter.
