# Support And Span Check - v0.12 Supported Review

Date: 2026-04-26  
Source JSON: `neutral_structural_model_v0_12_supported.json`  
Review DXF: `structural_review_v0_12_supported.dxf`

## Result

Status: review-grade pass with design warnings.

Version 0.11 passed Revit import only. It did not pass structural support review because large slab areas were not visibly supported by a continuous beam/column/wall system. Version 0.12 corrects the review model before any further Revit work.

## Corrections Made

- Added a visible podium beam and column grid below slab areas.
- Added intermediate office/refuge support line so the typical-floor slab is not floating across a large unsupported bay.
- Removed beams that duplicated core wall support lines.
- Kept core walls as direct slab/collector supports where the beam would sit on the same wall line.
- Segmented atrium and skylight edge beams so opening perimeter beams are not drawn as 25m to 32m unsupported members.
- Added opening perimeter support columns at review locations.

## Span Summary

| Zone | Levels | Max beam segment shown in JSON/DXF | Support logic |
| --- | --- | ---: | --- |
| Podium / basement / ground / shopping | B2-B1, G/F, 1/F-2/F | 10.0m | Beam grid supported by columns and core walls |
| Podium roof / transfer | 3/F podium roof | 10.0m | Transfer/podium beam grid supported by columns and core walls |
| Office typical | 3/F-31/F standard floor | 8.0m | Intermediate support line added; core walls support the 5m core band |
| Sky/refuge variant | Sky/refuge floor | 8.0m | Same supported review grid as office variant |
| Atrium / skylight edges | Shopping and podium roof openings | <= 8.0m after segmentation | Edge beams split and supported by perimeter/corner columns |

## Wall-Line Rule

Where the slab is directly supported by a wall, the model intentionally does not add a duplicate beam on the same wall centerline. This applies to:

- core south wall: `y=0`, `x=12m-92m`
- core north wall: `y=5m`, `x=12m-92m`
- core west wall: `x=12m`, `y=0-5m`
- core east wall: `x=92m`, `y=0-5m`

This is why the DXF should show walls without a beam directly underneath on those same lines.

## Remaining Design Warnings

- Member sizes are still seed sizes, not final design.
- The office support strategy now includes intermediate support; if the architectural requirement returns to column-free office space, this model must be replaced by a formally checked long-span/transfer/PT/composite scheme.
- Gravity, lateral, deflection, vibration, torsion, robustness, and foundation checks are still required before design approval.
- The DXF is for structural review only and should not be treated as final BIM/Revit production geometry.

## Validation

- Schema validation: pass.
- Deterministic reference check: pass.
- Duplicate beam on core wall support line: 0 detected.
- Beam segments longer than 10m: 0 detected.
