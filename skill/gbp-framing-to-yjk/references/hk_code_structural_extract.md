# HK Code Structural Extract (For GBP -> Framing -> YJK)

This note captures only high-value, workflow-relevant checks from the local HK code pack.

## Source Set (Detected)

- `CoP_SUC2013e.pdf` - Code of Practice for Structural Use of Concrete 2013 (2020 Edition)
- `DIL2011e.pdf` - Code of Practice for Dead and Imposed Loads 2011 (2021 Edition)
- `FoundationCode2017.pdf` - Code of Practice for Foundations 2017 (2024 Edition)
- `SUOS2011.pdf` - Code of Practice for the Structural Use of Steel 2011 (2023 Edition)
- `WindEffects2019e.pdf` - Code of Practice on Wind Effects in Hong Kong 2019
- `fs_code2011.pdf` - Code of Practice for Fire Safety in Buildings 2011 (2024 Edition)

## What To Pull Per Milestone

## M01 (GBP Interpretation)

- From `DIL2011e.pdf`:
  - floor-use imposed loads (office, parking, roof plant),
  - parking-related load class context,
  - reduction provisions for distributed imposed loads on beams/vertical members.
- From project brief:
  - parking count, stall size, aisle width, turning radius, max structural depth, internal-column-line limits.
- From `WindEffects2019e.pdf`:
  - whether the building form likely triggers torsional sensitivity checks.

## M02 (Framing + Preliminary Analysis)

- From `CoP_SUC2013e.pdf`:
  - limit-state framework (ULS/SLS/FLS),
  - RC member checks path for beams, slabs, columns, walls,
  - second-order effect awareness and robustness considerations.
- From `SUOS2011.pdf` (if steel or composite options considered):
  - limit-state framework, overall stability, integrity and robustness checks.
- From `WindEffects2019e.pdf`:
  - lateral loading basis,
  - across-wind/torsional effect consideration,
  - load-combination logic for lateral/torsional actions.
- From `fs_code2011.pdf`:
  - fire resistance constraints that affect structural member decisions.

## M03 (YJK Interface)

- Carry forward assumptions and governing checks from M02 into YJK model metadata.
- Ensure exported model can reproduce:
  - gravity load cases,
  - lateral cases (including torsion-sensitive checks when needed),
  - key design combinations used for preliminary sizing decisions.

## Traceability Rules

- Every numeric requirement used in sizing/checking must include:
  - source file name,
  - page number,
  - short label of the requirement.
- If a value is assumed due to missing data, mark as `ASSUMED` and include a replacement condition.

## Quality Gates

- Gate M01: no unresolved geometry/requirement conflict that changes structural layout materially.
- Gate M02: vertical and lateral preliminary checks complete with governing cases identified.
- Gate M03: topology/layer import checks passed and model assumptions aligned with M02.
