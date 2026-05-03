# GBP Structural Pipeline PRD

Version: v0.17

Document status: working PRD

Last updated: 2026-05-03

Primary product route:

`GBP -> drawing intake -> grid/story/boundary/zoning -> neutral JSON -> review DXF -> Revit -> ETABS 21.1`

Source-of-truth rule:

`Neutral Structural JSON is the source of truth.`

Revit is used for review, coordination, and import checking. ETABS 21.1 is the first-priority formal analysis route. YJK is a future adapter and must not be described as the current main workflow.

Keep the route concise. The internal drawing-understanding and structural-design processes may be detailed, but they must not obscure the product path.

## 1. Product Purpose

The GBP Structural Pipeline converts Hong Kong GBP architectural drawing packages into a controlled, traceable structural review model and downstream analysis handoff.

The product is not a one-time drawing conversion script. It is a maintainable engineering pipeline made of small modules. Each module has a defined input, output, validation gate, and downstream impact. Future changes should update only the affected module and its downstream validators.

The product must help engineers answer:

- What does the GBP drawing say?
- Which parts are confirmed by drawings and which are assumptions?
- What structural framing intent is proposed?
- Which elements are ready for review only?
- Which elements require transfer design, analysis, or human review?
- What can be sent to Revit for coordination?
- What can be sent to ETABS for formal analysis preparation?

## 2. Product Scope

### 2.1 In Scope

- Read and interpret GBP PDF drawing packages.
- Extract grid lines, levels, boundaries, functional zones, cores, openings, voids, and keepout constraints.
- Preserve traceability from model objects back to drawing sheets, notes, or assumptions.
- Generate a neutral structural JSON model as the system source of truth.
- Generate review DXF for human checking.
- Generate Revit review/import package with structural metadata.
- Generate ETABS 21.1 import or API handoff plan.
- Run pre-analysis checks for geometry, support continuity, transfer conditions, sizing reasonableness, and adapter readiness.
- Keep version history clear and non-destructive.

### 2.2 Out Of Scope For Current MVP

- Automatic final structural design.
- Construction drawings.
- Reinforcement design.
- Final code compliance approval.
- Solved ETABS analysis result feedback.
- Foundation design.
- Production-grade Revit family mapping.
- YJK as the current main workflow.

### 2.3 Future Scope

- ETABS automated model creation and analysis feedback loop.
- ETABS result ingestion into JSON, DXF, and Revit review payloads.
- YJK adapter after ETABS route is stable.
- SAFE or slab/foundation branch after the frame analysis route is stable.
- Approved Revit-to-JSON review change workflow.

## 3. Product MVP Definition

The current MVP should be defined as a review and coordination MVP.

MVP name:

`GBP-Framing Review/Coordination MVP`

MVP includes:

- GBP PDF understanding at review level.
- Grid, boundary, level, functional zone, core, opening, and keepout extraction.
- Neutral structural JSON.
- Review DXF.
- Revit review import with structural metadata.
- Preliminary ETABS 21.1 handoff plan.
- Self-check and validation reports.

MVP does not include:

- Final structural design.
- Automatic formal analysis.
- Final member sizing approval.
- Code-compliant construction documentation.
- Reinforcement schedules.
- Full ETABS analysis result feedback.

MVP success means:

- A reviewer can understand the extracted architectural constraints.
- A reviewer can inspect the proposed structural intent in DXF and Revit.
- The JSON can act as a stable source of truth.
- The ETABS handoff can identify what is ready, what is assumed, and what is missing.
- Transfer-required conditions and other engineering risks are visible rather than hidden.

## 4. Product Principles

1. JSON is the source of truth.
2. Drawings own architectural facts.
3. Structural logic owns framing intent and engineering assumptions.
4. Revit is a review and coordination interface, not the analysis authority.
5. ETABS is the first formal analysis target.
6. YJK is a future adapter.
7. Every assumption must be explicit.
8. Every version must remain traceable.
9. Old outputs must not be overwritten.
10. A local module change should only trigger that module and downstream validation.

## 5. User Roles

### 5.1 Structural Engineer

Uses the pipeline to review drawing interpretation, framing intent, support continuity, transfer conditions, and ETABS handoff readiness.

### 5.2 BIM / Revit Coordinator

Uses Revit review output to inspect levels, grids, member locations, object metadata, and coordination issues.

### 5.3 Technical Lead

Uses the PRD and version log to understand product direction, development status, release scope, and module ownership.

### 5.4 Developer / Pipeline Maintainer

Uses module contracts to update one block at a time without rerunning or rewriting the whole system.

## 6. System Architecture

The system is divided into controlled modules.

```text
M00 Project Setup / Version Control
M01 Drawing Intake And Source Management
M02 GBP Understanding / Drawing Interpretation
M03 Neutral Structural JSON Model
M04 Structural Design Logic
M05 Review Deliverables: DXF And Revit
M06 ETABS 21.1 Handoff
M07 QA / Validation / Self-Check
M08 Future Adapters
```

Each module must define:

- purpose
- inputs
- outputs
- current status
- completed capability
- in-progress capability
- unresolved problems
- downstream impact
- validation method
- MVP requirement

The modules are internal controls. They should not replace the concise product route.

## 7. Module Requirements

## M00 Project Setup / Version Control

### Purpose

Control project paths, version naming, run folders, release artifacts, tags, and non-overwrite behavior.

### Inputs

- Project working directory.
- Main run directory.
- Input PDF location.
- Output directory.
- Git branch and tags.
- Prior PRD versions and release notes.

### Outputs

- Version manifest.
- Artifact index.
- Run log.
- Dependency map.
- Tag policy.

### Required Capabilities

1. Track every run and version.
2. Preserve old outputs.
3. Prevent accidental overwrite of earlier versions.
4. Record source input path and output path.
5. Record which module generated each artifact.
6. Record which downstream modules depend on each artifact.
7. Keep release notes in this PRD under the Version Update Log.

### Current Status

In progress.

### Completed

- Versioned output naming exists.
- Prior version artifacts are retained.
- Git tags exist for prior milestones.

### In Progress

- A formal version manifest is still needed.
- Branch and tag naming need to be reconciled and standardized.

### Unresolved Problems

- Local branch state may not match the expected working branch.
- Some historical PRD paths need environment reconciliation.

### Downstream Impact

M00 affects all modules. If version control is wrong, model lineage and review history become unreliable.

### Validation

- Check Git branch.
- Check Git tags.
- Check artifact existence.
- Check manifest consistency.

### MVP Required

Yes.

### Estimated Completion

-

## M01 Drawing Intake And Source Management

### Purpose

Register and classify input files before interpretation. This module should know what the source files are, what can be extracted directly, and what requires fallback processing.

### Inputs

- GBP PDF.
- Requirement notes in the same package.
- Optional DXF or vector drawing source if provided later.
- Optional OCR output if source quality requires it.

### Outputs

- Source inventory.
- Drawing sheet index.
- Source quality assessment.
- Extraction method selection.
- Source traceability root IDs.

### Required Capabilities

1. Identify source type: vector PDF, scanned PDF, DXF, image, or mixed package.
2. Index sheets and title blocks where available.
3. Identify drawing scale, units, and coordinate assumptions.
4. Detect whether vector extraction is available.
5. Mark OCR or manual interpretation as fallback, not confirmed fact.
6. Assign stable source IDs for traceability.

### Current Status

Partly complete.

### Completed

- The current PDF source is registered in the neutral model metadata.
- The current model identifies the source as a drawing package and requirement source.

### In Progress

- A complete sheet index is still needed.
- Extraction quality should be stored separately from structural assumptions.

### Unresolved Problems

- Source page-level traceability is not yet complete enough for all extracted facts.
- Scanned or low-quality fallback rules need to be formalized.

### Downstream Impact

M01 affects every drawing-derived object in M02, M03, M04, M05, and M06.

### Validation

- Source file exists.
- Source type is declared.
- Sheet index is complete enough for review.
- Every extracted object references a source root ID.

### MVP Required

Yes.

### Estimated Completion

-

## M02 GBP Understanding / Drawing Interpretation

### Purpose

Convert drawing information into structured architectural and spatial constraints. This module must happen before structural design logic.

### Submodules

### M02.01 Grid Line Extraction And Validation

Purpose:

Build the grid backbone before extracting or placing structural objects.

Inputs:

- Drawing source inventory.
- Vector geometry or recognized grid labels.
- Drawing scale and units.

Outputs:

- Grid lines.
- Grid labels.
- Grid spacing.
- Grid confidence.
- Grid conflict report.

Validation:

- Grid spacing sanity check.
- Duplicate grid detection.
- Missing grid label check.
- Grid direction and coordinate consistency check.

Downstream impact:

- A grid change affects all geometry, all structural members, DXF, Revit, ETABS, and future adapters.

MVP required:

Yes.

### M02.02 Site Boundary And Building Boundary

Purpose:

Extract site boundary, building footprint, podium footprint, tower footprint, and structural envelope constraints.

Inputs:

- Grid backbone.
- Drawing boundary lines.
- Brief constraints.

Outputs:

- Site boundary.
- Building boundary.
- Podium boundary.
- Tower boundary.
- Boundary traceability.

Validation:

- Closed polyline check.
- Boundary-grid alignment check.
- Scale sanity check.
- Envelope conflict check.

Downstream impact:

- Boundary changes affect slabs, edge beams, perimeter supports, Revit model, and ETABS area objects.

MVP required:

Yes.

### M02.03 Levels, Storeys, And Standard-Floor Grouping

Purpose:

Extract level structure and define standard-floor grouping before Revit and ETABS handoff.

Inputs:

- Drawing levels.
- Section/elevation notes if available.
- Brief and height constraints.

Outputs:

- Level list.
- Storey grouping.
- Standard-floor templates.
- Repeat metadata.
- Level traceability.

Validation:

- Elevation order check.
- Duplicate level check.
- Missing standard-floor repeat check.
- Revit level compatibility check.
- ETABS story compatibility check.

Downstream impact:

- Level changes affect Revit levels, ETABS stories, repeated floor strategy, loads, masses, and analysis assumptions.

MVP required:

Yes.

### M02.04 Functional Zoning

Purpose:

Extract architectural zones that affect structural layout and support strategy.

Functional zones include:

- mall
- office
- core
- atrium
- refuge
- parking
- passage
- plant room
- lobby
- service area
- roof or sky garden zone

Inputs:

- Drawing labels.
- Brief requirements.
- Boundaries.
- Openings and keepouts.

Outputs:

- Functional zone map.
- Zone constraints.
- No-column or limited-column zones.
- Zone traceability.

Validation:

- Zone-boundary containment check.
- Zone overlap check.
- Keepout consistency check.
- Architectural conflict check.

Downstream impact:

- Functional zones affect column density, span strategy, transfer requirements, slab loads, Revit review, and ETABS load assignments.

MVP required:

Yes.

### M02.05 Openings, Voids, Edges, And Keepout Zones

Purpose:

Extract voids and constraints that affect slab continuity, edge beams, support layout, and load path.

Inputs:

- Boundary data.
- Functional zoning.
- Drawing notes and requirements.

Outputs:

- Openings.
- Voids.
- Edge conditions.
- Keepout zones.
- Required edge support conditions.

Validation:

- Opening boundary closure check.
- Keepout violation check.
- Edge support check.
- Slab continuity warning check.

Downstream impact:

- Opening and keepout changes affect beams, slabs, columns, DXF, Revit, ETABS meshing, and transfer logic.

MVP required:

Yes.

### M02.06 Architectural And Brief Constraints

Purpose:

Capture non-geometric constraints that affect structural choices.

Inputs:

- Requirement notes.
- Client brief.
- Drawing annotations.

Outputs:

- Constraint list.
- Priority level.
- Source reference.
- Structural implication.

Validation:

- Every constraint has a source.
- Every structural implication is tagged as confirmed or assumed.

Downstream impact:

- Brief constraints can affect all structural design logic and review status.

MVP required:

Yes.

### M02.07 Traceability Report

Purpose:

Make every recognized object reviewable by source.

Inputs:

- Source inventory.
- Extracted objects.
- Assumption log.

Outputs:

- Traceability report.
- Source-to-object map.
- Object-to-source map.
- Assumption register.

Validation:

- Every object has a source or assumption.
- Every assumption is visible.
- No silent inferred geometry.

Downstream impact:

- Traceability affects reviewer trust, Revit metadata, ETABS assumption review, and future auditability.

MVP required:

Yes.

## M03 Neutral Structural JSON Model

### Purpose

Store drawing interpretation and structural intent in a software-neutral source-of-truth model.

### Inputs

- M02 drawing interpretation outputs.
- M04 structural design logic outputs.
- Analysis seed data.
- Traceability data.

### Outputs

- Neutral structural JSON.
- Schema validation report.
- Model status summary.
- Assumption register.

### Required Root Structure

```json
{
  "metadata": {},
  "source_of_truth": "json",
  "coordinate_system": {},
  "intent_model": {},
  "analysis_seed_model": {},
  "precheck": {}
}
```

### Required Entity Fields

Each relevant entity should carry, directly or through equivalent linked data:

- `id`
- `mark`
- `source`
- `traceability`
- `level`
- `storey`
- `geometry`
- `structural_role`
- `section_seed`
- `status`
- `supported_by`
- `supports`
- `load_path`
- `downstream_impact`

Allowed status values:

- `confirmed`
- `assumed`
- `needs_review`
- `transfer_required`

### Current Status

Partly complete.

### Completed

- Neutral model root structure exists.
- Intent model and analysis seed model are separated.
- Stable IDs and traceability exist for many objects.
- Schema validation exists.

### In Progress

- Entity-level status fields need to be standardized.
- Support relation fields need to be added consistently.
- Downstream impact fields need to be added consistently.

### Unresolved Problems

- Some assumptions are still narrative-only.
- Some support relations are not machine-checkable.
- Standard-floor repeat metadata needs stronger representation.

### Downstream Impact

M03 affects all deliverables because it is the source of truth.

### Validation

- JSON schema validation.
- Required field completeness check.
- Coordinate system check.
- Unit consistency check.
- Traceability completeness check.

### MVP Required

Yes.

### Estimated Completion

-

## M04 Structural Design Logic

### Purpose

Convert drawing constraints into structural framing intent while keeping engineering assumptions explicit.

### Submodules

### M04.01 Structural Grid And Support Philosophy

Purpose:

Define how structural supports relate to the architectural grid and functional zones.

Outputs:

- Support philosophy.
- Column/wall placement rules.
- Span strategy.
- Architectural conflict notes.

Validation:

- Support layout follows the grid or explicitly records offsets.
- Support strategy respects keepout and functional zones.

Downstream impact:

- Affects all structural members, Revit review, ETABS model setup, and future adapters.

MVP required:

Yes.

### M04.02 Vertical Support System

Purpose:

Define columns, walls, core walls, and vertical continuity.

Outputs:

- Column intent.
- Wall intent.
- Core wall intent.
- Vertical continuity map.

Validation:

- Upper supports have lower support or transfer status.
- Core and wall elements are connected to the level system.
- No structural support violates no-column zones without review status.

Downstream impact:

- Affects transfer strategy, load path, Revit, ETABS, and QA.

MVP required:

Yes.

### M04.03 Transfer Strategy

Purpose:

Identify and manage conditions where upper columns or walls do not continue to lower supports.

Product rule:

If an upper column lands on a beam and no lower column or wall exists below, the condition must be marked `transfer_required`. It must not be treated as an ordinary beam-column joint.

Outputs:

- Transfer-required object list.
- Transfer candidate members.
- Transfer design priority.
- ETABS analysis requirement.

Validation:

- Every discontinuous upper support is flagged.
- Every flagged condition has a proposed resolution route.
- Ordinary beams and transfer members are not mixed silently.

Downstream impact:

- Affects section seeds, member roles, ETABS priority, DXF review marks, Revit metadata, and design approval status.

MVP required:

Yes.

### M04.04 Floor System

Purpose:

Define slab, beam, long-span, and opening-edge support strategy.

Outputs:

- Slab system intent.
- Beam hierarchy.
- Long-span zone strategy.
- Opening-edge support strategy.

Validation:

- Slabs have support path.
- Long-span assumptions are explicit.
- Opening edges have support review.

Downstream impact:

- Affects DXF, Revit, ETABS area objects, loads, and deflection/vibration review.

MVP required:

Yes.

### M04.05 Wall-Supported Slab Rule

Purpose:

Avoid duplicate beams where walls already provide slab support, unless a collector, transfer, edge, or detailing reason exists.

Outputs:

- Wall-supported slab conditions.
- Duplicate-beam exceptions.
- Collector or transfer reason tags.

Validation:

- Wall lines are not automatically duplicated with beams.
- Exceptions carry explicit reasons.

Downstream impact:

- Affects beam count, Revit clarity, ETABS modeling, and review readability.

MVP required:

Yes.

### M04.06 Lateral System

Purpose:

Represent the core, shear wall, wind, torsion, and drift logic at concept and analysis-preparation level.

Outputs:

- Lateral system intent.
- Core and wall roles.
- Torsion risk notes.
- ETABS lateral analysis requirements.

Validation:

- A non-trivial building must have a lateral system intent.
- Wind and torsion are marked as unresolved until formal analysis.

Downstream impact:

- Affects ETABS model, wall roles, load combinations, and design status.

MVP required:

Yes, at review level.

### M04.07 Preliminary Sizing

Purpose:

Provide review-grade member size seeds that are reasonable enough for coordination but not final design.

Outputs:

- Section seed list.
- Preliminary sizing notes.
- Reasonableness warnings.
- Analysis-required tags.

Validation:

- Span-depth screening.
- Column capacity screening.
- Long-span warning checks.
- PT/composite assumptions are explicit.

Downstream impact:

- Affects DXF labels, Revit parameters, ETABS properties, and reviewer expectations.

MVP required:

Yes, as review-grade sizing only.

### M04.08 Load Path Continuity

Purpose:

Track gravity load path from slab to beam or wall, then to column or wall, then to foundation interface.

Outputs:

- Load path graph.
- Unsupported element warnings.
- Transfer-required warnings.
- Foundation interface assumptions.

Validation:

- Slab support check.
- Beam support check.
- Column/wall continuity check.
- Transfer check.

Downstream impact:

- Affects QA, ETABS readiness, and design confidence.

MVP required:

Yes.

### M04.09 ETABS Handoff Requirements

Purpose:

Define what structural logic must be available before ETABS model creation.

Outputs:

- Story data requirements.
- Frame object requirements.
- Shell object requirements.
- Section and material requirements.
- Support and load requirements.
- Unsupported feature list.

Validation:

- ETABS readiness checklist.
- Missing property check.
- Load placeholder check.
- Story expansion or repetition strategy check.

Downstream impact:

- Affects M06 directly.

MVP required:

Yes, as preliminary handoff.

## M05 Review Deliverables: DXF And Revit

### Purpose

Create review outputs from the neutral JSON without changing the source-of-truth rule.

### Inputs

- Neutral structural JSON.
- DXF style rules.
- Revit importer mapping rules.

### Outputs

- Review DXF.
- Revit review/import package.
- Revit parameter mapping report.
- Review checklist.

### Required Capabilities

1. Generate review DXF from JSON.
2. Show grids, boundaries, columns, walls, beams, slabs, openings, and important annotations.
3. Rotate directional beam marks where required for readability.
4. Import review geometry into Revit.
5. Preserve structural metadata in Revit parameters.
6. Keep Revit edits separate from JSON source of truth unless approved.
7. Use Group, Link, or compact repeated-floor strategy for standard floors.

### Revit Metadata

Revit review objects should expose:

- `GBP_JSON_ID`
- `GBP_STRUCTURAL_ROLE`
- `GBP_SECTION`
- `GBP_MODEL_STATUS`
- `GBP_SOURCE`
- `Mark`
- `Comments`

### Current Status

Partly complete.

### Completed

- Review DXF generation exists.
- Revit review import exists.
- Structural metadata parameters exist in the importer.

### In Progress

- Revit standard-floor strategy needs stronger workflow control.
- Revit parameter visibility and shared parameter setup need a stable checklist.

### Unresolved Problems

- Revit output is review geometry, not production family mapping.
- Revit must not become the analysis source.

### Downstream Impact

M05 affects review workflows, BIM coordination, and user trust. It should not silently affect M03 unless reviewed changes are approved.

### Validation

- DXF visual checklist.
- Layer and label check.
- Revit import guard check.
- Revit metadata visibility check.
- Standard-floor compact strategy check.

### MVP Required

Yes.

### Estimated Completion

-

## M06 ETABS 21.1 Handoff

### Purpose

Convert the neutral JSON into an ETABS 21.1 analysis preparation package.

### Inputs

- Neutral structural JSON.
- Structural design logic from M04.
- Materials and sections.
- Story data.
- Load and combination definitions.
- ETABS API starter.

### Outputs

- ETABS import plan.
- ETABS API command plan.
- Future ETABS `.EDB`.
- ETABS readiness report.
- Future analysis feedback payload.

### Required Capabilities

1. Read neutral JSON.
2. Define stories.
3. Define materials.
4. Define frame and shell properties.
5. Add columns, beams, walls, and slabs.
6. Assign supports.
7. Assign loads and combinations.
8. Save ETABS model.
9. Run visual/model sanity check before analysis.
10. Feed analysis warnings and results back to JSON review payload in future versions.

### Current Status

Preparation stage.

### Completed

- ETABS 21.1 has been selected as first-priority analysis interface.
- ETABS API starter exists.
- Runtime DLL copy issue has been addressed in the starter workflow.
- ETABS handoff plan exists.

### In Progress

- Replace starter one-beam/one-column workflow with loops over JSON-derived command plan.
- Define story expansion or repeat-floor mass strategy.
- Map PT/composite assumptions to ETABS-compatible properties.

### Unresolved Problems

- No full ETABS model has been created from JSON yet.
- No ETABS analysis has been run.
- Some load values remain placeholders pending code-cited input.
- Slab openings need an ETABS meshing/opening workflow.
- Transfer conditions require formal analysis before acceptance.

### Downstream Impact

M06 is the bridge from review-grade model to analysis-seed-grade and later analysis-verified workflow.

### Validation

- ETABS command plan validation.
- Missing property check.
- Story compatibility check.
- Load placeholder check.
- API smoke test.
- Future model-open check.
- Future analysis run check.

### MVP Required

Yes, as preliminary handoff plan only.

### Estimated Completion

-

## M07 QA / Validation / Self-Check

### Purpose

Provide deterministic checks and engineering self-review before any output is trusted.

### Inputs

- M01 source inventory.
- M02 drawing interpretation.
- M03 neutral JSON.
- M04 structural logic.
- M05 review deliverables.
- M06 ETABS handoff.

### Outputs

- Geometry validation report.
- Traceability validation report.
- Entity field completeness report.
- Support continuity report.
- Transfer check report.
- Preliminary sizing screen.
- Revit review checklist.
- ETABS readiness report.
- Release gate summary.

### Required Capabilities

1. Validate geometry.
2. Validate schema.
3. Validate traceability.
4. Validate required entity fields.
5. Detect keepout conflicts.
6. Detect unsupported members.
7. Detect transfer-required conditions.
8. Screen preliminary sizing.
9. Check standard-floor compact model strategy.
10. Check Revit parameter visibility.
11. Check ETABS readiness.

### Current Status

Partly complete.

### Completed

- Schema validation exists.
- Structural self-check reporting exists.
- Transfer check reporting exists.
- Preliminary sizing screen exists.
- DXF readability check exists.

### In Progress

- Convert current checks into module-level validators.
- Add downstream-only validation flow.

### Unresolved Problems

- Load path graph is not fully machine-checkable.
- Formal ETABS analysis validation does not exist yet.
- Code-cited final design checks do not exist yet.

### Downstream Impact

M07 controls release status. A QA failure should block promotion to the next product grade.

### Validation

M07 is itself the validation layer and should output pass, warning, or block status.

### MVP Required

Yes.

### Estimated Completion

-

## M08 Future Adapters

### Purpose

Support future analysis and regional workflow adapters after the ETABS-first route is stable.

### Inputs

- Neutral JSON.
- Approved adapter contract.
- Target software requirements.

### Outputs

- Future YJK adapter payload.
- Future SAFE adapter payload.
- Adapter-specific QA reports.

### Required Capabilities

1. Consume neutral JSON without changing source-of-truth ownership.
2. Declare unsupported features.
3. Preserve element IDs where possible.
4. Report adapter readiness.
5. Keep adapter-specific data separate from core neutral model state.

### Current Status

Future planning.

### Completed

- YJK is recognized as a future adapter concept.

### In Progress

- None for current MVP.

### Unresolved Problems

- YJK should not be mixed into the current main route.
- Adapter contract should wait until ETABS data model is stable.

### Downstream Impact

M08 should not affect the current MVP or ETABS-first development unless explicitly scheduled.

### Validation

- Adapter contract review.
- Import QA checklist.
- Schema compatibility check.

### MVP Required

No.

### Estimated Completion

-

## 8. Controlled Change Workflow

Each future implementation change must follow this workflow:

1. Identify the module being changed.
2. Identify upstream inputs.
3. Identify downstream outputs.
4. Update only the required code block or data block.
5. Run the module validator.
6. Run only affected downstream validators.
7. Add an entry to the Version Update Log.

Full-pipeline rerun is allowed only when:

- source drawing changes,
- coordinate system changes,
- grid backbone changes,
- schema has a breaking change,
- support/load-path rules change globally,
- or the user explicitly asks for a full refresh.

## 9. Release Grades

### Concept-Grade

Drawing interpretation and structural intent exist, but validation is incomplete.

### Review-Grade

Geometry and structural intent are good enough for visual review, coordination, and issue discovery. Formal analysis is not complete.

### Analysis-Seed-Grade

The model has enough properties, loads, support data, and story logic to create a formal analysis model.

### Analysis-Verified

The model has been run in ETABS or another approved solver, and results have been reviewed and fed back into the product workflow.

Current product grade:

`Review-grade / ETABS-preparation`

## 10. Release Gates

| Gate | Review MVP | Analysis-Seed | Analysis-Verified |
| --- | --- | --- | --- |
| Source inventory | required | required | required |
| Grid extraction | required | required | required |
| Level and storey grouping | required | required | required |
| Functional zoning | required | required | required |
| Traceability | required | required | required |
| Neutral JSON schema validation | required | required | required |
| Structural support logic | review-grade | required | solver-reviewed |
| Transfer-required detection | required | required | solver-reviewed |
| Preliminary sizing screen | required | required | solver-updated |
| Review DXF | required | optional | optional |
| Revit review import | required | optional | optional |
| ETABS handoff plan | required | required | replaced by solved model |
| ETABS analysis run | not required | not required | required |
| Code-cited final checks | not required | partial | required |

## 11. Implementation Work Packages

The next programming updates should be split according to this PRD.

### WP-00 Version Manifest

Module:

M00

Goal:

Add a version manifest that records input, output, module, upstream dependency, downstream dependency, and validation status.

### WP-01 Drawing Interpretation Blocks

Module:

M01 and M02

Goal:

Separate grid extraction, level/story grouping, boundary extraction, functional zoning, openings, keepouts, and traceability into separate blocks.

### WP-02 Neutral JSON Entity Contract

Module:

M03

Goal:

Add or normalize entity fields for status, support relations, load path, and downstream impact.

### WP-03 Transfer And Support Continuity

Module:

M04 and M07

Goal:

Convert narrative transfer warnings into machine-readable `transfer_required` status and support continuity checks.

### WP-04 Review Outputs

Module:

M05

Goal:

Keep DXF and Revit generation downstream of JSON. Improve review parameters, standard-floor handling, and visual review checks.

### WP-05 ETABS Adapter

Module:

M06

Goal:

Move from ETABS handoff plan to JSON-driven ETABS API model creation.

### WP-06 QA Gates

Module:

M07

Goal:

Create module-level validators so one change only reruns the affected module and downstream checks.

## 12. Version Update Log

This PRD is intended to remain the single active PRD. Future updates should append to this section instead of creating separate standalone PRDs, unless a major product reset is approved.

### v0.11 - Import-Only Baseline

Product meaning:

- Established the initial concept of converting GBP-derived information into importable structural review artifacts.
- Focus was on proving that an import route could exist.

Limitations:

- The workflow was not yet modular.
- YJK-related direction was too prominent for what is now the current product route.
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
- Strengthened the product requirement that architectural function must constrain structural layout.

Limitations:

- Long-span strategy remained review-level and required formal analysis.

### v0.14 - Opening And Local Cleanup

Product meaning:

- Improved handling of openings and local column conflicts.
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

- Reframes the work as a single long-lived product PRD.
- Defines module boundaries from drawing intake through ETABS handoff.
- Defines block-level development and downstream-only validation.
- Confirms JSON-Revit-ETABS as the current main route.
- Confirms YJK as a future adapter.
- Defines review/coordination MVP boundaries.

Limitations:

- This version is a product and process update, not a code update.
- Implementation work packages still need to be applied module by module.

### v0.18 - Skill And Element-Control Contract Update

Product meaning:

- Updates the active GBP skill direction from legacy YJK-first wording to JSON-Revit-ETABS-first workflow.
- Adds module-level execution guidance for drawing intake, grid extraction, storey grouping, boundary extraction, functional zoning, openings/keepouts, traceability, structural logic, review deliverables, ETABS handoff, and QA.
- Adds independent element contract requirements for `status`, `support_relation`, `load_path`, and `downstream_impact`.
- Extends the neutral schema to support independent element fields and functional zones.
- Adds optional validator mode for independent-field completeness checks.
- Keeps old models backward-compatible under base validation while exposing missing modular-control fields through stricter checks.

Limitations:

- Existing v0.16 model data has not yet been backfilled with all independent element fields.
- Grid/story/boundary extraction blocks are specified in the skill but still need implementation work packages.
- ETABS full model creation remains a future implementation step.

### v0.19 - Concise Route With Element-Level Governance

Product meaning:

- Keeps the product route concise as `GBP -> drawing intake -> grid/story/boundary/zoning -> neutral JSON -> review DXF -> Revit -> ETABS 21.1`.
- Moves complexity into element-by-element drawing understanding and structural arrangement stages.
- Aligns the skill style with integrated engineering workflows: short route, clear internal sequence, iteration triggers, and output checks.
- Clarifies that grid lines, storeys, boundaries, zoning, openings, keepouts, traceability, supports, transfer conditions, and load paths are internal element-control blocks, not separate product routes.

Limitations:

- Element-level extraction scripts still need implementation after the skill/control update.
- Existing model data still needs backfill before strict independent-field checks can pass.

## 13. Open Decisions

- Standard tag naming convention.
- Whether v0.17 should be tagged after PRD approval.
- Final branch alignment for this product line.
- Transfer strategy preference: lower support alignment or explicit transfer members.
- Office long-span system direction.
- Mall open-space priority versus transfer/long-span member weight.
- Timing for ETABS automated model creation.
- Timing for future YJK adapter.
