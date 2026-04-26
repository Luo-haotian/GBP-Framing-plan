# GBP Structural Pipeline Revit 2023 Importer

This is a development add-in prototype for importing compact standard-floor neutral JSON into Revit 2023.

## What It Creates

- Revit Levels from `intent_model.levels`
- Revit structural plan views for each imported level
- Revit Grids from `intent_model.grids`
- Review-grade DirectShape columns, beams, walls, slabs, and opening placeholders
- `GBP_JSON_ID` shared parameter where Revit allows it
- Mark/comments traceability back to neutral JSON IDs
- Per-view review notes listing column, beam, wall, and slab seed dimensions

## Current Boundary

This importer creates review geometry, not final production Revit families. Columns, beams, walls, slabs, and openings are represented as DirectShape solids so the import can work before family/type mapping is fully defined.

## Build

Run:

```powershell
.\build.ps1
```

## Manual Install For Revit Test

Copy `GbpStructuralPipelineImporter.addin` to:

```text
C:\Users\11131\AppData\Roaming\Autodesk\Revit\Addins\2023
```

Then open Revit 2023, open a project, run the external command, and select the current compact standard-floor review file:

```text
C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2\run-001\outputs\neutral_structural_model_v0_16_review_revit_etabs.json
```

The importer now stops when the selected JSON has more than 1200 importable review elements, to avoid freezing Revit on fully expanded office-floor geometry. Current v0.16 standard-floor review models should stay below that guard.

Keep this as a manual test step until we decide the add-in is safe enough to install automatically.
