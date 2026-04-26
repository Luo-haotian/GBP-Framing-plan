# GBP Structural Pipeline

This repository is for the workflow:

```text
GBP drawings / requirements
-> neutral structural JSON
-> review DXF
-> Revit visual coordination
-> ETABS analysis model
-> analysis feedback back to JSON
```

The neutral JSON is the source of truth. Revit is for visual/BIM review. ETABS is the first formal analysis target. YJK is future adapter scope, not the current primary route.

## Current Case

Current working case:

```text
case/GBP-Framing/q2-process-test-0.12
```

Current run outputs are mirrored from:

```text
C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2\run-001\outputs
```

## Current Version

Tag: `V0.12`

Important files:

- `neutral_structural_model_v0_16_review_revit_etabs.json`
- `structural_review_v0_16_rotated_marks.dxf`
- `structural_engineer_self_check_v0_16.md`
- `etabs_import_plan_v0_16.json`
- `etabs_api_research_v0_16.md`
- `revit_package_v0_16.md`
- `PRD_RPD_v0_16.md`

## Version History

- `v0.11`: compact standard-floor Revit import baseline. Revit import worked, but structural support logic still needed correction.
- `v0.12`: added visible slab support but became over-dense for a mall.
- `v0.13`: restored mall/open-space intent and reduced column/beam count.
- `v0.14`: removed erroneous opening helper columns near main grid columns.
- `v0.15`: reduced over-large member seed sizes and added preliminary capacity/rho sizing checks.
- `v0.16`: rotated vertical beam marks in DXF, prepared Revit review package, and generated an ETABS API dry-run import plan.

Older versions are intentionally retained in case folders and archive folders. Do not squash the version files; each version documents a design correction.

## Revit

Revit is not the calculation source of truth.

Use the v0.16 importer package with Revit 2023:

```text
C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2\run-001\revit-json-importer-v0_16
```

The add-in imports neutral JSON as review DirectShape geometry and writes GBP shared parameters such as JSON ID, role, section, source, and model status.

## ETABS

ETABS 21.1 is the active analysis target.

Starter example:

```text
C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2\run-001\etabs-api-starter
```

Dry-run import plan:

```text
C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2\run-001\outputs\etabs_import_plan_v0_16.json
```

Next target: convert the ETABS dry-run plan into a real `.EDB`, inspect geometry, then run gravity/lateral analysis.
