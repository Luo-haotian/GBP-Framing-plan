# GBP-Framing-Plan-YJK

This repository contains:

- `skill/gbp-framing-to-yjk`: Codex skill for GBP -> Framing -> YJK workflow.
- `skill/gbp-structural-pipeline`: Codex skill for GBP -> neutral JSON -> Revit -> analysis workflow.
- `case/GBP-to-Framing-Plan-to-YJK`: test case scripts and generated milestone outputs.
- `case/GBP-Framing`: schema demo artifacts and future test cases.

Current stable production route is `DXF -> YJK`.
JSON import is preserved for future interface development. The 0.11 structural-pipeline branch adds compact standard-floor review models, visible member dimensions, opening edge support checks, wall-supported slab logic, and a Revit 2023 JSON importer prototype.
