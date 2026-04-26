# Model Self-Check 0.11

## Result

Status: pass, with review-grade warnings.

Use `neutral_structural_model_v0_11.json` for the next Revit import test. Do not use `neutral_structural_model_v1.json` for Revit review unless you intentionally want a large expanded test.

## Revit Performance

- V1 expanded model size: about 2.27 MB, 2703 beams, 35 slabs, 36 levels.
- 0.11 compact model size: about 281 KB, 237 beams, 6 slabs, 7 standard levels.
- Likely Revit freeze cause: thousands of DirectShapes/text notes from repeated office floors.
- Importer guard added: if a selected JSON has more than 800 review elements, importer stops and asks for compact standard-floor input.

## Standard Floor Groups

- Basement typical: represents B2-B1.
- Ground floor: represents G/F.
- Shopping typical: represents 1/F-2/F.
- Podium roof / transfer: represents 3/F transfer and tower start.
- Office typical: represents repeated 3-31F office standard floors.
- Sky garden / refuge: special variant because the section shows different height/use.
- Roof limit: height-control level only.

## Structural Support Logic

- Slab zones supported by core walls do not duplicate beams on the same wall line.
- Atrium and skylight openings have perimeter edge beams.
- Office typical floor uses core wall support plus perimeter/long-span beams to preserve no-column/no-wall office intent.
- Long-span office beams are flagged for formal span-depth, deflection, vibration, and economy checks.

## Dimension Visibility

- JSON sections include all seed member dimensions.
- DXF labels now include dimensions, for example `C1200x1200`, `B600x1200`, `t400`, and slab thickness labels.
- Revit importer puts dimensions in DirectShape names/comments and per-view review notes.

## Counts

- Levels: 7 standard levels.
- Columns: 58.
- Beams: 237.
- Slabs: 6.
- Walls: 4.
- Openings: 2.

## Remaining Warnings

- This is review-grade only.
- Member dimensions are seed sizes, not final design.
- Long-span office beams need formal checks or an approved alternative system.
- Sky/refuge is treated as a special standard-floor variant, not a normal repeated office floor.
