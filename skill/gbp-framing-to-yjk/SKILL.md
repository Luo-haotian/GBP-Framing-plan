---
name: gbp-framing-to-yjk
description: Interpret Hong Kong GBP architectural drawings and convert them into a structural framing plan plus YJK-ready deliverables. Use when tasks involve locating core/envelope/long-span zones, proposing columns/beams/shear walls under Hong Kong code logic, outputting node-beam JSON, or generating DXF layers for YJK 8.0 import.
---

# GBP Framing To YJK

Use this skill to run a full milestone workflow:
`GBP + requirement understanding -> structural framing + preliminary calculations -> YJK interface artifacts`.

Follow the workflow in order. Keep assumptions explicit, keep every decision traceable to drawing/brief/code, and output machine-readable data.

## Scope And Philosophy

- This skill is for Hong Kong projects and must explicitly reference Hong Kong code basis.
- Structural judgement must be evidence-based: each key decision needs either:
  - a drawing/brief fact,
  - a code-based rule, or
  - a clearly tagged engineering assumption.
- Geometry-only output is not sufficient. Include preliminary vertical and lateral checks before finalizing framing.

## Required Inputs

- GBP drawing(s): PDF/DXF/image.
- Project requirement/brief text.
- Optional local code pack folder named `HK Code` in the project (preferred).

## Code Pack Integration (Mandatory When Available)

If `HK Code` folder exists in the workspace, load and prioritize it. For the current expected set:
- `CoP_SUC2013e.pdf` (Code of Practice for Structural Use of Concrete 2013 (2020 Edition))
- `DIL2011e.pdf` (Code of Practice for Dead and Imposed Loads 2011 (2021 Edition))
- `FoundationCode2017.pdf` (Code of Practice for Foundations 2017 (2024 Edition))
- `SUOS2011.pdf` (Code of Practice for the Structural Use of Steel 2011 (2023 Edition))
- `WindEffects2019e.pdf` (Code of Practice on Wind Effects in Hong Kong 2019)
- `fs_code2011.pdf` (Code of Practice for Fire Safety in Buildings 2011 (2024 Edition))

Extract and retain only structure-relevant items for this workflow:
- load definitions and combinations framework,
- floor-use imposed loads and reduction rules,
- wind lateral/torsional requirements and serviceability comfort checks where relevant,
- RC/steel design limit-state framework and robustness expectations,
- foundation selection and geotechnical compatibility checks,
- fire resistance constraints that affect structural element sizing/detailing.

Do not invent clause values. If a numeric requirement is used, quote the source file and page in notes.

## Cross-Verification For Drawing/Requirement Understanding

Never rely on one recognition path only. Use at least two channels and reconcile:

1. Native/vector extraction path:
- Parse PDF text and vector geometry first when available.

2. OCR fallback path:
- Use OCR for scanned or low-quality sheets.
- If Tesseract is installed, use it as a backup recognizer and cross-check major dimensions, labels, and room names.

3. Consistency checks:
- Envelope closure and scale sanity.
- Grid spacing sanity.
- Key dimensions consistency across brief, title block, and extracted geometry.
- Functional constraints consistency (carpark count, aisle widths, turning radius, permitted internal column lines, max structural depth).

If conflicts remain unresolved, report them immediately as blocking issues and continue with explicit temporary assumptions.

## Workflow (Milestone-Driven)

## Milestone 01: GBP-Structural Interpretation (`01_GBP_Interpretation`)

Purpose: remove non-structural noise and keep only information that drives structural design.

Produce:
- `M01_constraints.json`: structured constraints from brief + code + drawing.
- `M01_geometry.json`: envelope, grids, core zone, keepout zones, parking-relevant geometry.
- `M01_risks.md`: missing data, conflicts, and temporary assumptions.
- `M01_traceability.md`: mapping from each critical constraint to source (brief/code/drawing).

Must identify and report:
- core position and likely lateral-force center,
- long-span zones and repeated zones,
- building envelope and gravity/lateral load paths,
- parking geometry constraints and circulation-sensitive zones.

## Milestone 02: Framing + Preliminary Structural Analysis (`02_Framing_Plan`)

Purpose: build a viable framing scheme backed by preliminary calculations.

Design defaults (unless overridden by project constraints):
- column spacing target: `6m-9m`,
- preserve major openings and circulation,
- use primary/secondary beam hierarchy for shortest practical load path,
- start lateral system at core and add wing/perimeter walls if torsion/drift risk remains high,
- for non-transfer schemes, keep vertical column coordinates consistent across LG2/typical/roof.

Mandatory checks (preliminary level):
- vertical load path and tributary-based sizing checks for beams/columns/walls/slabs,
- lateral system checks (wind-governed where applicable): stability concept, torsion sensitivity, drift/serviceability screening,
- key element quick sizing with transparent formulas/inputs,
- preliminary reinforcement ratio range estimate for major RC members,
- constructability and code-compatibility notes.

Parking compatibility:
- keep parking/circulation as a geometric and functional constraint inherited from Milestone 01.
- verify stall/aisle/turning compliance and collision-free swept-path proxy.

Produce:
- `M02_framing_plan.dxf` (or per-floor framing DXFs),
- `M02_member_schedule.csv`,
- `M02_prelim_calc.xlsx` or `M02_prelim_calc.csv` + `M02_calc_notes.md`,
- `M02_design_narrative.md` (why this scheme works, what remains to be verified).

## Milestone 03: YJK Interface And Import QA (`03_YJK_Interface`)

Purpose: convert approved Milestone 02 scheme into YJK-ready assets.

Produce:
- `M03_framing.json` in schema from `references/gbp_yjk_interface.md`,
- `M03_yjk_import.dxf` using `scripts/json_to_yjk_dxf.py`,
- `M03_import_checklist.md` with pass/fail on layer mapping and topology integrity.

Use:

```bash
python scripts/json_to_yjk_dxf.py --input <framing.json> --output <framing.dxf>
```

Layer mapping:
- `YJK_COL`
- `YJK_BEAM_PRIMARY`
- `YJK_BEAM_SECONDARY`
- `YJK_SHEAR_CORE`
- `YJK_SHEAR_WING`
- `YJK_ENVELOPE`
- `YJK_NODE_ANNO`

## Structural Analysis Engine Requirement

This skill must treat structural analysis as core, not optional:
- For each candidate scheme, run preliminary multi-case checks (at least gravity + lateral).
- Document governing cases and utilization trends for key members.
- Flag where simplified checks end and full-frame analysis is required.
- If no analysis engine is available, output a clear "analysis gap" section and stop short of "design finalized".

## DXF Drafting Rules

- Use `mm` as drawing unit for all entities.
- Draw columns and walls as closed polylines with physical dimensions.
- Draw beams as closed polylines (physical width), not centerlines only.
- Add size annotations beside members (for example `600x600`, `300x450`, `WALL 250 thk`).
- Add full setting-out dimensions between adjacent grid axes, not only overall dimensions.
- Keep framing drawings free of parking entities; issue parking in separate layout sheets.

Drawing boundary rules:
- If user provides explicit axis-offset coordinates for core/service zones, treat them as hard constraints.
- Building boundary must be continuously supported by framing members.

## Output Contract

For user-facing responses, keep this order:
1. Milestone status (`M01/M02/M03` passed, blocked, or assumption-based)
2. Structural interpretation summary (from M01)
3. Framing + preliminary calculation summary (from M02)
4. YJK interface payload and generation result (from M03)
5. Open risks and next required verification

When confidence is low, still provide a best-effort draft and mark uncertainty explicitly.

## Resources

- Schema and QA: `references/gbp_yjk_interface.md`
- HK code quick extract: `references/hk_code_structural_extract.md`
- DXF converter: `scripts/json_to_yjk_dxf.py`
