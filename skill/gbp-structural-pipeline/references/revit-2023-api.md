# Revit 2023 API

## Purpose

Use this reference when checking local Revit 2023 API readiness or designing the Revit-side automation branch.

## Local API Boundary

Revit 2023 API assemblies normally live in:

```text
C:\Program Files\Autodesk\Revit 2023\RevitAPI.dll
C:\Program Files\Autodesk\Revit 2023\RevitAPIUI.dll
```

These assemblies are compile-time references for Revit add-ins. They are not a normal standalone Python API for model editing.

## Preferred Development Route

Use this sequence:

1. Generate or validate `neutral_structural_model.json`.
2. Generate a review DXF for visual checking when no add-in exists yet.
3. Build a Revit 2023 add-in that reads the neutral JSON and creates levels, grids, columns, walls, framing, slabs, and openings inside Revit.
4. Store neutral IDs on created Revit elements for traceability.
5. Export approved review changes back into JSON only through an explicit approval path.

## Multi-Level Review Rule

Do not treat a commercial tower as one framing plan. The importer and any review DXF should preserve explicit `level_id` ownership and standard floor group intent:
- basement typical
- ground floor
- low shopping floors
- podium roof / transfer floor
- typical office floor
- sky garden/refuge floor
- roof / height limit

If a 2D exchange format is used, lay out separate review panels or layers for each standard floor group instead of drawing all beams, slabs, openings, and keepouts on top of one another.

For Revit add-ins, prefer compact standard-floor JSON for review imports. A fully expanded repeated-office model can create thousands of DirectShapes and view notes, causing Revit to hang. Add import guards or batching before full-storey expansion.

## Probe Script

Run:

```bash
python scripts/probe_revit_2023_api.py --report <report.md>
```

The probe checks:
- Revit installation folder
- `Revit.exe`
- `RevitAPI.dll`
- `RevitAPIUI.dll`
- `RevitCoreConsole.exe`
- machine and user add-in folders
- Python `clr` / pythonnet availability
- .NET SDK visibility
- .NET Framework `csc.exe` visibility for simple add-in compile smoke tests

## Add-in Locations

Machine add-ins:

```text
C:\ProgramData\Autodesk\Revit\Addins\2023
```

User add-ins:

```text
%APPDATA%\Autodesk\Revit\Addins\2023
```

Use these only when the user explicitly wants to install or test an add-in. During skill development, keep generated add-in packages in the project or test folder first.

## Feasibility Labels

- `api-assemblies-present`: DLLs exist and can be referenced by an add-in project.
- `add-in-ready`: add-in folder exists and a compiled command can be installed.
- `add-in-compile-ready`: add-in folders and .NET Framework C# compiler are present.
- `in-process-test-ready`: Revit, Dynamo, macro, pyRevit, or RevitCoreConsole route is available for execution.
- `exchange-only`: only JSON/DXF artifacts can be generated from outside Revit.
