# Revit Review Package - v0.16

Date: 2026-04-26  
Source JSON: `neutral_structural_model_v0_16_review_revit_etabs.json`

## Status

The Revit 2023 importer has been rebuilt for v0.16 review import.

Built DLL:

```text
C:\Users\11131\Documents\New project\skill\gbp-structural-pipeline\assets\revit-json-importer\GbpStructuralPipelineImporter.dll
```

Run copy:

```text
C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2\run-001\revit-json-importer-v0_16
```

Installed `.addin` location:

```text
C:\Users\11131\AppData\Roaming\Autodesk\Revit\Addins\2023\GbpStructuralPipelineImporter.addin
```

## Import Guard

The old guard stopped imports over 800 review elements. v0.16 is a compact standard-floor model but has about 830 importable review elements, so the guard was adjusted to 1200.

This still blocks fully expanded repeated-floor imports.

## Manual Revit Step

In Revit 2023:

1. open a project,
2. run `GBP Structural Pipeline Importer`,
3. select:

```text
C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2\run-001\outputs\neutral_structural_model_v0_16_review_revit_etabs.json
```

## Boundary

This creates DirectShape review geometry. It is not final production Revit family mapping and is not structural calculation output.

## Revit Element Information

The importer now writes these shared instance parameters where Revit allows them:

- `GBP_JSON_ID`
- `GBP_STRUCTURAL_ROLE`
- `GBP_SECTION`
- `GBP_MODEL_STATUS`
- `GBP_SOURCE`

It also writes `Mark` and `Comments`.

If the properties do not appear after import, close Revit completely and reopen it so the v0.16 DLL is loaded. Only one addin should be active:

```text
GbpStructuralPipelineImporter_v0_16.addin
```
