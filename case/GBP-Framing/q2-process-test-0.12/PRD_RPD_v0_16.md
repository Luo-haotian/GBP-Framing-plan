# PRD / RPD Update - v0.16

Date: 2026-04-26  
Version label: `V0.12` release tag candidate  
Working model: `neutral_structural_model_v0_16_review_revit_etabs.json`

## Product Direction

The pipeline priority is now:

1. GBP -> neutral structural JSON
2. neutral JSON -> review DXF
3. neutral JSON -> Revit visual review
4. neutral JSON -> ETABS API analysis model
5. ETABS results -> JSON/DXF/Revit review update
6. YJK adapter later

YJK is no longer the immediate solver priority. ETABS 21.1 is the first formal analysis target.

## Completed In This Iteration

- v0.15 preliminary sizing reduced over-large members.
- v0.16 DXF rotates vertical beam marks by 90 degrees.
- v0.16 Revit importer guard updated from 800 to 1200 review elements.
- Revit importer rebuilt and copied into `run-001\revit-json-importer-v0_16`.
- Revit addin installed to the Revit 2023 addins folder.
- Revit addin cleanup completed: only the v0.16 addin should remain active.
- Revit DirectShape review elements now carry GBP shared parameters for ID, role, section, source, and model status.
- ETABS 21.1 local API files and COM entry points verified.
- ETABS dry-run import plan generated: `etabs_import_plan_v0_16.json`.
- ETABS API starter fixed to copy required runtime DLLs beside the EXE.
- Transfer-column check added: 10 tower columns require transfer design or lower support alignment.
- Structural self-check report generated.

## Current Deliverables

- `neutral_structural_model_v0_16_review_revit_etabs.json`
- `structural_review_v0_16_rotated_marks.dxf`
- `validation_report_v0_16_review_revit_etabs.md`
- `structural_engineer_self_check_v0_16.md`
- `etabs_import_plan_v0_16.json`
- `etabs_api_research_v0_16.md`
- `revit_package_v0_16.md`
- `transfer_column_check_v0_16.md`
- `etabs-api-starter/`

## Still Not Complete

- No ETABS `.EDB` has been created yet.
- No ETABS analysis has been run yet.
- Ten tower columns are transfer-required unless lower supports are added.
- PT/composite beam assumptions are not final ETABS design properties yet.
- HK code numeric values still need page-cited extraction before final code checks.
- Revit output remains DirectShape review geometry, not production family mapping.

## Version Policy

Do not squash or overwrite previous versions. Keep visible version files:

- v0.11 import-only baseline
- v0.12 supported but over-dense correction
- v0.13 mall open-space correction
- v0.14 opening-column cleanup
- v0.15 preliminary sizing correction
- v0.16 DXF/Revit/ETABS preparation

Git tag candidate: `V0.12`.
