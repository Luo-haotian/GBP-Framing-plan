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

Then open Revit 2023, open a project, run the external command, and select the 0.11 compact standard-floor file:

```text
C:\Users\11131\Documents\New project\case\GBP-Framing\q2-process-test-0.11\neutral_structural_model_v0_11.json
```

The importer now stops when the selected JSON has too many repeated review elements, to avoid freezing Revit on fully expanded office-floor geometry.

Keep this as a manual test step until we decide the add-in is safe enough to install automatically.
