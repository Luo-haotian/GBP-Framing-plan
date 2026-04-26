# Structural Engineer Self-Check - v0.16

Date: 2026-04-26  
Basis model: `neutral_structural_model_v0_16_review_revit_etabs.json`

## Status

Status: **review-grade / ETABS-preparation**, not analysis-verified.

v0.16 is acceptable for visual review, Revit import testing, and ETABS API mapping research. It is not acceptable as final structural design.

## Checks Completed

### Drawing Readability

- Vertical beam labels are rotated 90 degrees in `structural_review_v0_16_rotated_marks.dxf`.
- Beam text count: 721.
- Beam text rotations: 437 at 0 degrees, 284 at 90 degrees.

### Layout And Support Logic

- Standard floor approach retained: basement typical, GF, shopping typical, podium roof/transfer, office typical, sky/refuge, roof.
- Slab-bearing floors have visible support by beams, columns, walls, or stated long-span system.
- Core wall centerlines do not receive duplicate beams where the wall directly supports the slab/collector line.
- Atrium/skylight opening support is shown by edge beams and nearby main grid support.
- No `CO-OPEN` near-duplicate opening columns remain.
- No same-range column pairs under 2m were found in v0.14/v0.15 checks; v0.16 inherits that geometry.

### Member Sizing Screen

- Ordinary low-rise mall columns are no longer `1200x1200`.
- v0.15/v0.16 sizing uses:
  - mall edge/perimeter columns: `700x700`
  - mall typical columns: `900x900`
  - mall transfer-critical columns: `1000x1000`
  - tower columns: `900x900`, kept pending tower load take-down
  - office slim beam envelope: `450x650`, treated as composite/PT concept, not ordinary RC

### Code/Reference Discipline

- Local HK code pack exists and remains the preferred source for formal design values:
  - `DIL2011e.pdf`
  - `CoP_SUC2013e.pdf`
  - `SUOS2011.pdf`
  - `WindEffects2019e.pdf`
  - `FoundationCode2017.pdf`
- The current report uses screening load assumptions only. Numeric code values must be page-cited before final design.

## Open Engineering Problems

### Blocking Before Design Approval

- ETABS gravity and lateral model has not yet been solved.
- Tower load take-down into podium transfer elements is not known.
- Transfer beam/wall behavior at podium roof is not checked.
- PT/composite assumptions are not yet mapped to real ETABS design properties.
- Deflection and vibration checks are not done.
- Wind/torsion and core-wall lateral checks are not done.
- Foundation reactions and pile/raft selection are not checked.

### Important Warnings

- A `450x650` office beam is only reasonable as a slim composite/PT envelope. It is not a normal RC long-span beam pass.
- A `500x900` or `700x1100` mall beam at 16m span is preliminary only. Formal PT/composite design may change size or system.
- Standard floor compaction is good for Revit review, but ETABS analysis needs either story replication or explicit assignment of repeat counts/masses.

## Next Engineering Iteration

1. Use v0.16 JSON as source of truth.
2. Import into Revit for visual/model coordination only.
3. Convert v0.16 into an ETABS API command plan.
4. Expand/assign repeated stories in ETABS.
5. Run gravity/lateral preliminary analysis.
6. Feed member utilization, drift, and reactions back into JSON and DXF as v0.17.
