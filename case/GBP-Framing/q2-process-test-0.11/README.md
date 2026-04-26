# Q2 Process Test 0.12 Supported Review

This case now captures the 0.12 structural support correction for `GBP and requirement.pdf`.

## Key Change From 0.11

0.11 fixed Revit import weight by using compact standard-floor groups, but it still allowed structurally unsupported slab fields in the review layout.

0.12 keeps the compact standard-floor approach but corrects the structural review model:
- slab areas now have visible beam/column/wall support,
- beams on core wall centerlines are omitted because the wall supports the slab directly,
- typical office/refuge floors now include intermediate support instead of leaving slab areas floating,
- atrium and skylight edge beams are segmented and supported,
- Revit-specific generation is paused to save time and focus on JSON/DXF review quality.

## Files

- `neutral_structural_model_v0_12_supported.json`: current supported review-grade neutral model.
- `structural_review_v0_12_supported.dxf`: current structural review DXF.
- `validation_report_v0_12_supported.md`: schema and deterministic validation report.
- `support_span_check_v0_12_supported.md`: slab/beam/wall support and span summary.
- `archive_v0_11_import_only/`: archived 0.11 files that proved Revit import but failed structural support review.

## Revit Note

Do not generate or import Revit review geometry from this case until the JSON/DXF support logic has been accepted. The next Revit version should be generated from the supported v0.12 model, not the archived v0.11 import-only model.
