# ETABS API Starter

This folder shows the smallest practical ETABS 21.1 API workflow using C# and the installed `ETABSv1.dll`.

## Build

Run in PowerShell:

```powershell
cd "C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2\run-001\etabs-api-starter"
.\build.ps1
```

This creates:

```text
EtabsApiStarter.exe
ETABSv1.dll
CSiAPIv1.dll
```

The two DLLs are copied next to the EXE because a normal console program does not automatically probe the ETABS installation folder at runtime.

## Run

Close any important ETABS models first. Then run:

```powershell
.\EtabsApiStarter.exe
```

It will:

1. start ETABS 21.1,
2. create a blank model,
3. set units to `kN-m-C`,
4. define simple concrete material/sections,
5. add one column and one beam,
6. save:

```text
C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2\run-001\outputs\etabs_api_starter_blank.edb
```

## How This Relates To Our Pipeline

The current generated file:

```text
C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2\run-001\outputs\etabs_import_plan_v0_16.json
```

is a dry-run command plan. The next step is to replace the starter's one beam/one column with loops over that plan:

- define stories,
- define frame and area properties,
- add columns/beams/walls/slabs,
- assign loads,
- save `.EDB`,
- then run analysis only after geometry is visually checked.
