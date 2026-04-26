# Transfer Column Check - v0.16

Date: 2026-04-26  
Source: `neutral_structural_model_v0_16_review_revit_etabs.json`

## Engineering Rule

If an upper column starts at podium roof and there is no lower column or wall directly below it, the support must be treated as a transfer condition.

There are only two acceptable strategies:

1. provide a continuous lower column/wall below the upper column, or
2. explicitly design a transfer beam/girder/wall/slab system and verify it in ETABS.

It must not be treated as an ordinary beam-column joint.

## Current Check Result

Upper tower columns checked: 12  
Columns with direct lower support found: 2  
Columns requiring transfer design: 10

## Transfer-Required Columns

| Upper column | Location (mm) | Nearby podium roof beam |
| --- | ---: | --- |
| `CO-TWR-078` | `(0, 5000)` | `BM-LV-PODIUM-ROOF-0562` |
| `CO-TWR-079` | `(0, 20000)` | `BM-LV-PODIUM-ROOF-0563` |
| `CO-TWR-080` | `(12000, 20000)` | `BM-LV-PODIUM-ROOF-0570` |
| `CO-TWR-081` | `(28000, 20000)` | `BM-LV-PODIUM-ROOF-0577` |
| `CO-TWR-082` | `(44000, 20000)` | `BM-LV-PODIUM-ROOF-0584` |
| `CO-TWR-083` | `(60000, 20000)` | `BM-LV-PODIUM-ROOF-0591` |
| `CO-TWR-084` | `(76000, 20000)` | `BM-LV-PODIUM-ROOF-0598` |
| `CO-TWR-085` | `(92000, 20000)` | `BM-LV-PODIUM-ROOF-0605` |
| `CO-TWR-087` | `(104000, 5000)` | `BM-LV-PODIUM-ROOF-0611` |
| `CO-TWR-088` | `(104000, 20000)` | `BM-LV-PODIUM-ROOF-0612` |

## Recommendation

For the next version, choose one of these:

- **Option A: column continuity**: add or align lower podium columns/walls below these tower columns where the mall layout allows it.
- **Option B: explicit transfer scheme**: rename/mark the supporting podium roof members as transfer girders/walls, increase analysis priority, and send the load path to ETABS before accepting member sizes.

Because this is a mall and open space is important, Option B may be architecturally attractive, but it must be explicitly analyzed. Current v0.16 remains review-grade only.
