# ETABS 21.1 API Research - v0.16

Date: 2026-04-26  
Installed target: ETABS 21.1  
Neutral source: `neutral_structural_model_v0_16_review_revit_etabs.json`

## Local API Evidence

ETABS is installed at:

```text
C:\Program Files\Computers and Structures\ETABS 21
```

Local API files found:

- `CSI API ETABS v1.chm`
- `ETABSv1.dll`
- `ETABSv1.tlb`
- `CSiAPIv1.dll`
- `CSiAPIv1.tlb`

Registered COM/API entry points found:

- `CSI.ETABS.API.ETABSObject`
- `ETABSv1.Helper`
- `CSiAPIv1.Helper`

## Adapter Direction

Primary flow:

```text
neutral JSON -> ETABS API command plan -> ETABS .EDB model -> analysis results -> JSON review update
```

Revit is not the analysis source of truth. Revit remains for visual/BIM review. ETABS becomes the first formal analysis engine. YJK remains future scope.

## Current Artifact

Generated dry-run command plan:

```text
etabs_import_plan_v0_16.json
```

Current plan contents:

- stories: 7 standard/review levels
- frame properties: 9
- columns: 70
- beams: 721
- walls: 4
- slabs: 6

This plan does not launch ETABS or write an `.EDB` yet.

## ETABS Mapping To Implement Next

### Stories

Map neutral `intent_model.levels` to ETABS story definitions. Standard floor groups need a repeat/replication strategy before final analysis:

- office typical must be expanded or assigned through repeated story mass/stiffness logic
- sky/refuge stays a special story
- podium/transfer stays explicit

### Frame Objects

Map:

- neutral columns -> ETABS frame objects, vertical coordinates
- neutral beams -> ETABS frame objects at story elevation
- section seeds -> ETABS frame properties

### Area Objects

Map:

- slabs -> ETABS floor area objects
- walls -> ETABS wall/shell objects
- openings -> ETABS area openings or mesh/cut workflow

### Loads

Map current screening loads to ETABS load patterns:

- dead
- superimposed dead
- live
- wind, after code basis is set

### Analysis Feedback

Pull back:

- frame utilization / forces
- story drift
- reactions
- modal periods
- shell forces for core walls
- transfer beam forces

## Risks

- ETABS API object signatures must be tested in-process through COM; this report only confirms installation and registry entry points.
- Composite/PT beam design cannot be represented by RC rectangular dimensions alone.
- Repeated standard floors must be expanded or modeled with an approved equivalent strategy before analysis.
- Area openings and diaphragms require careful meshing.

## Next Step

Create a controlled ETABS writer script that can:

1. open ETABS 21.1 through COM,
2. create a blank model,
3. define units/stories/materials/sections,
4. add frames and areas,
5. save an `.EDB`,
6. run analysis only after the generated geometry is visually checked.
