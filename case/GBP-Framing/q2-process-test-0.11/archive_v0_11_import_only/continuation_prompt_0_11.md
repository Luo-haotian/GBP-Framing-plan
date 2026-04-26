# Continuation Prompt For New Codex Conversation

Use this prompt at the start of the next conversation:

```text
We are continuing development of the GBP Structural Pipeline skill in:
C:\Users\11131\Documents\New project

Use the skill at:
C:\Users\11131\Documents\New project\skill\gbp-structural-pipeline

Current branch should be:
codex/gbp-structural-pipeline-0.11

Current test folder is:
C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2

The source PDF is:
C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2\GBP and requirement.pdf

The important 0.11 repo case is:
C:\Users\11131\Documents\New project\case\GBP-Framing\q2-process-test-0.11

Use this compact standard-floor JSON for Revit tests:
C:\Users\11131\Documents\New project\case\GBP-Framing\q2-process-test-0.11\neutral_structural_model_v0_11.json

Do not use the fully expanded V1 JSON for Revit import unless testing batching. It caused Revit to hang because it had 36 levels, 2703 beams, and many DirectShapes/text notes. 0.11 reduced this to 7 standard levels, 237 beams, 6 slabs, 58 columns, 4 walls, and 2 openings.

Core 0.11 rules:
1. Repeated floors must be represented as standard floor groups/templates, not copied floor-by-floor for review.
2. 3-31F office should be treated as an office typical standard floor for review, with sky/refuge as a special variant when relevant.
3. Structural layout must support the architectural intent, not just trace the GBP.
4. If a slab is supported directly by a wall, do not duplicate a beam on that same wall line unless there is transfer/edge/collector/local detailing need.
5. Every opening must have perimeter support, at least edge beams or explicit wall/edge support.
6. Long-span beams must terminate at vertical supports or transfer supports. If no-column architectural intent forces a long span, flag it for formal span-depth, deflection, vibration, and economic section checks.
7. Member seed dimensions must be visible in JSON, DXF labels, and Revit element names/comments/view notes.
8. Before any delivery, run independent self-check: standard floor groups, support system per slab-bearing floor, opening support, long spans, member dimensions, Revit import weight, and model status.

Relevant files:
- skill references:
  - references/structural-layout-rules.md
  - references/precheck-engine.md
  - references/revit-adapter.md
  - references/revit-2023-api.md
  - references/neutral-structural-schema.md/json
- scripts:
  - scripts/check_neutral_model.py
  - scripts/neutral_model_to_review_dxf.py
  - scripts/probe_revit_2023_api.py
- Revit importer prototype:
  - skill/gbp-structural-pipeline/assets/revit-json-importer/GbpStructuralPipelineImporter.cs
  - build.ps1
  - GbpStructuralPipelineImporter.addin

Next development tasks:
1. Test Revit import with neutral_structural_model_v0_11.json.
2. If Revit still hangs, inspect importer DirectShape/text-note creation and add batching or import toggles by category.
3. Upgrade review DirectShape geometry toward real Revit family/type mapping only after compact import is stable.
4. Improve structural prechecks: wall-supported slab detection, opening edge support detection, long-span/economic warning, visible dimension audit.
5. Keep skill and case outputs synchronized, validate with quick_validate.py and check_neutral_model.py.
```
