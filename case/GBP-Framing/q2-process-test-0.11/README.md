# Q2 Process Test 0.11

This case captures the 0.11 workflow correction for `GBP and requirement.pdf`.

## Key Change From 0.10

0.10 expanded repeated office floors into many individual levels and Revit review elements. That made the JSON and Revit import too heavy and did not match standard structural drawing practice.

0.11 uses compact standard floor groups:
- basement typical
- ground floor
- shopping typical
- podium roof / transfer
- office typical
- sky garden / refuge variant
- roof / height limit

## Files

- `neutral_structural_model_v0_11.json`: compact review-grade neutral model.
- `validation_report_v0_11.md`: schema and deterministic validation report.
- `model_self_check_v0_11.md`: independent model self-check.
- `revit_review_import_v0_11_standard_floors.dxf`: DXF review output with member dimensions in labels.

## Revit Note

Use the compact JSON for Revit import. Do not import the fully expanded V1 JSON unless testing batching or expansion logic.
