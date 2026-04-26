# Q2 Process Test 0.12

This folder is the versioned repository mirror of the current `run-001` review iteration.

## Version Contents

- v0.15: preliminary member sizing correction.
- v0.16: DXF beam mark rotation, Revit review package, and ETABS API preparation.

## Current Review Files

- `neutral_structural_model_v0_16_review_revit_etabs.json`
- `structural_review_v0_16_rotated_marks.dxf`
- `validation_report_v0_16_review_revit_etabs.md`
- `structural_engineer_self_check_v0_16.md`
- `etabs_import_plan_v0_16.json`
- `etabs_api_research_v0_16.md`
- `revit_package_v0_16.md`
- `transfer_column_check_v0_16.md`
- `etabs-api-starter/`
- `PRD_RPD_v0_16.md`

## Current Warnings

- Ten tower columns currently start at podium roof without direct lower column/wall continuity. Treat these as transfer-required unless the next version adds continuous lower supports.
- Revit review geometry is DirectShape-based but now includes GBP shared parameters for JSON ID, structural role, section, model status, and source.
- ETABS is the analysis target; the starter project demonstrates API startup and blank model creation.

## Version Policy

Do not squash earlier iterations. The prior `q2-process-test-0.11` folder remains as the import/support-history baseline, and this folder records the next release candidate for Git tag `V0.12`.
