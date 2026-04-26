# Product Requirement Document (PRD)

Project: GBP Structural Pipeline - Q2 Standard-Floor Review Model  
Version: 0.11 PRD  
Date: 2026-04-26  
Owner: GBP Structural Pipeline / Revit-YJK workflow  
Test folder: `C:\Users\11131\Documents\New project\case\GBP-Framing\q2-process-test-0.11`

## 1. Product Goal

Build a review-grade structural pipeline that converts Hong Kong GBP architectural input into compact, traceable structural review outputs for DXF, Revit, and later YJK/analysis use.

The immediate product goal is not final structural design. The goal is to create a reliable MVP workflow that:

- understands GBP geometry and architectural intent,
- produces a compact neutral structural model,
- preserves standard-floor logic instead of expanding every repeated floor,
- imports into Revit without hanging,
- exposes member seed dimensions and review warnings clearly,
- leaves a clean path toward formal analysis and production BIM family mapping.

## 2. Key Product Principle

Repeated Revit floors must be managed by standard-floor templates using Revit Group or Link logic, not by copying one full set of elements onto every floor.

For review import:

- One office typical standard floor should represent repeated 3/F-31/F office floors.
- Special floors such as sky garden/refuge and transfer/podium roof should remain separate variants.
- Revit import should stay compact until production BIM requirements justify controlled expansion.
- Expanded repeated-floor import is allowed only for batching, stress testing, or final downstream workflows with explicit import limits.

This is required because the fully expanded V1 model caused Revit performance risk: about 36 levels, 2703 beams, and many DirectShapes/text notes. Version 0.11 reduced the review model to 7 standard levels, 237 beams, 6 slabs, 58 columns, 4 walls, and 2 openings.

## 3. Users And Use Cases

Primary users:

- Structural engineer reviewing feasibility and load path.
- BIM/Revit user testing structural review import.
- Pipeline developer improving GBP-to-structural automation.

Main use cases:

- Read a GBP PDF and requirements brief.
- Generate a review-grade structural layout with explicit assumptions.
- Validate neutral model schema and structural prechecks.
- Generate DXF review output with visible member dimensions.
- Import a compact structural review model into Revit 2023.
- Prepare future YJK/analysis-ready outputs after structural checks mature.

## 4. Current Status

### Completed

- Created compact standard-floor neutral model: `neutral_structural_model_v0_11.json`.
- Generated review DXF: `revit_review_import_v0_11_standard_floors.dxf`.
- Added validation report with zero schema issues: `validation_report_v0_11.md`.
- Added independent model self-check: `model_self_check_v0_11.md`.
- Reduced Revit import payload from expanded repeated-floor V1 to compact 0.11 review model.
- Added Revit importer guard: stop import when selected JSON has more than 800 importable review elements.
- Added visible seed dimensions in JSON, DXF labels, Revit element names/comments, and review notes.
- Added standard-floor groups for basement typical, ground floor, shopping typical, podium roof/transfer, office typical, sky/refuge, and roof limit.
- Added structural support logic checks for wall-supported slabs, opening perimeter support, and long-span warning.

### In Progress

- Manual Revit 2023 import test using `neutral_structural_model_v0_11.json`.
- Importer performance hardening for DirectShape and TextNote creation.
- Category-level import toggles or batching if Revit still hangs.
- Precheck improvement for wall-supported slab detection, opening edge support detection, long-span/economic warnings, and visible dimension audit.
- Keeping skill references, scripts, importer prototype, and case outputs synchronized.

### Future Planning

- Convert review DirectShapes into real Revit family/type mapping after compact import is stable.
- Implement Group/Link based repeated-floor management in Revit workflow.
- Add controlled expansion mode from standard-floor template to actual levels only when needed.
- Add formal preliminary structural analysis loop for gravity and lateral cases.
- Add YJK-ready export once framing and analysis seed model reach acceptance quality.
- Add import QA dashboard covering element counts, grouped floors, missing dimensions, unsupported openings, and long-span warnings.
- Improve HK code traceability with source page references for numeric load/design assumptions.

## 5. Functional Requirements

### FR-1 GBP Input Understanding

The pipeline shall parse the GBP PDF and requirements brief into a traceable structural intent model.

Acceptance criteria:

- Building envelope, core zone, grids, level intent, openings, and repeated zones are represented.
- Each major decision has a source, assumption, or review warning.
- Ambiguous or missing drawing data is marked rather than silently resolved.

Status: partially complete.

### FR-2 Compact Neutral Structural Model

The pipeline shall output a neutral JSON model suitable for review and downstream adapters.

Acceptance criteria:

- JSON passes schema validation.
- Standard floors are represented as templates/groups, not duplicated floor-by-floor.
- Element counts are small enough for Revit review import.
- Member seed sizes are visible in machine-readable sections.

Status: complete for 0.11 review-grade model.

### FR-3 Structural Precheck

The pipeline shall run deterministic review checks before delivery.

Acceptance criteria:

- Standard-floor compaction is checked.
- Wall-supported slab zones do not receive duplicate beams unless justified.
- Openings have perimeter support or explicit wall/edge support.
- Long-span beams are flagged for formal checks.
- Member dimension visibility is checked.

Status: partially complete; needs stronger geometry-based detection.

### FR-4 DXF Review Output

The pipeline shall generate a review DXF with physical member shapes and labels.

Acceptance criteria:

- Columns, beams, walls, slabs, and openings are visible.
- Labels include member IDs and seed dimensions.
- DXF remains review-focused and avoids unnecessary parking/detail noise.

Status: complete for 0.11 review output.

### FR-5 Revit Review Import

The pipeline shall import the compact neutral model into Revit 2023 without freezing.

Acceptance criteria:

- Import uses compact standard-floor JSON by default.
- Importer refuses overly expanded JSON payloads.
- Imported review elements carry JSON traceability and seed dimensions.
- Standard repeated floors are managed by Group or Link workflow in the product design, not by repeated independent copies.

Status: in progress; manual Revit test still required.

### FR-6 Future YJK Interface

The pipeline shall prepare YJK-ready geometry only after review framing and analysis assumptions are acceptable.

Acceptance criteria:

- Structural nodes, beams, columns, walls, slabs, and load assumptions are exportable.
- Topology integrity checks pass.
- Output distinguishes review-grade seed sizes from analysis-approved member sizes.

Status: planned.

## 6. Non-Functional Requirements

Performance:

- Review JSON should remain compact. The 0.11 target is around 281 KB and below 800 importable review elements.
- Revit import should complete interactively without long UI hangs.

Maintainability:

- Standard floors must be edited once and reused through Group/Link/template logic.
- Case outputs, skill references, and scripts must stay version synchronized.

Traceability:

- Every generated element should retain source or assumption context.
- Review warnings must remain visible in JSON, reports, and Revit notes.

Extensibility:

- DirectShape review geometry should be replaceable by real family/type mapping without changing the neutral model contract.
- Group/Link floor management should support later controlled expansion when needed.

## 7. MVP Definition

Yes, we have enough to build an MVP now, with a clear boundary.

MVP scope:

- Use `GBP and requirement.pdf` as the input case.
- Generate one compact standard-floor neutral JSON.
- Validate schema and deterministic prechecks.
- Generate DXF review output.
- Import compact review geometry into Revit 2023 using DirectShape.
- Preserve repeated floors as standard-floor groups/templates.
- Show seed dimensions and review-grade warnings.

MVP exclusions:

- Final structural design.
- Production Revit families and detailed type mapping.
- Full YJK import/export sign-off.
- Formal lateral/gravity analysis approval.
- Automatic Revit install and production BIM documentation.

MVP success criteria:

- `neutral_structural_model_v0_11.json` passes validation.
- DXF review output opens and shows dimensions.
- Revit import of 0.11 compact JSON finishes without hanging.
- Repeated floors are not expanded into independent copied elements for review.
- Long-span, seed-size, and review-grade limitations are visible to the user.

## 8. Risks And Open Questions

- Revit may still hang if DirectShape/TextNote creation is too heavy or runs in one large transaction.
- Group/Link management is a product requirement but is not yet fully implemented in the importer.
- DirectShape output is useful for review but not production BIM.
- Long-span office beams require formal span/depth, deflection, vibration, and economy checks.
- Member sizes are seed dimensions only.
- HK code numeric assumptions need stronger source-page traceability before design-grade use.

## 9. Near-Term Roadmap

### Step 1: Stabilize Revit MVP

- Run manual Revit import with `neutral_structural_model_v0_11.json`.
- Measure import time and inspect created levels, views, grids, and review elements.
- Add batching or category toggles if import is slow.

### Step 2: Implement Standard-Floor Revit Management

- Add importer mode for standard-floor Group creation or linked standard-floor container workflow.
- Keep one editable office typical model and reference it for repeated floors.
- Keep special variants separate: transfer/podium roof, sky/refuge, roof limit.

### Step 3: Strengthen Prechecks

- Improve slab-wall support detection.
- Improve opening edge support detection.
- Add long-span severity thresholds and economic warning rules.
- Add visible-dimension audit across JSON, DXF, and Revit naming/comments.

### Step 4: Move Toward Analysis/YJK

- Add preliminary gravity and lateral calculation artifacts.
- Convert neutral model into YJK-ready topology only after support and span warnings are resolved or explicitly accepted.
- Add import checklist and topology QA for downstream engineering software.

## 10. Release Decision

MVP can proceed if the next Revit manual import test passes with the 0.11 compact JSON.

Recommended next action:

1. Test Revit import using `neutral_structural_model_v0_11.json`.
2. If it passes, freeze 0.11 as the MVP review baseline.
3. If it fails, implement category toggles and batched DirectShape/TextNote creation before adding new structural features.
