#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def section_label(sections: dict[str, dict], section_id: str | None) -> str:
    if not section_id:
        return "UNKNOWN"
    section = sections.get(section_id, {})
    geom = section.get("geometry", {})
    if "b_mm" in geom and "h_mm" in geom:
        return f"{section_id}_{int(float(geom['b_mm']))}x{int(float(geom['h_mm']))}"
    if "thickness_mm" in geom:
        return f"{section_id}_t{int(float(geom['thickness_mm']))}"
    return section_id


def z_for_level(levels: dict[str, dict], level_id: str) -> float:
    return float(levels[level_id].get("elevation", 0.0))


def point3(point: dict, z: float) -> list[float]:
    return [float(point["x"]) / 1000.0, float(point["y"]) / 1000.0, z / 1000.0]


def beam_span_m(beam: dict) -> float:
    dx = float(beam["end"]["x"]) - float(beam["start"]["x"])
    dy = float(beam["end"]["y"]) - float(beam["start"]["y"])
    return math.hypot(dx, dy) / 1000.0


def build_plan(model: dict) -> dict:
    intent = model["intent_model"]
    seed = model["analysis_seed_model"]
    levels = {level["id"]: level for level in intent.get("levels", [])}
    sections = {section["id"]: section for section in seed.get("sections", [])}

    frame_properties: dict[str, dict] = {}
    area_properties: dict[str, dict] = {}

    def add_section(section_id: str | None) -> str:
        if not section_id:
            return "UNKNOWN"
        section = sections.get(section_id, {"id": section_id, "geometry": {}})
        name = section_label(sections, section_id)
        if section.get("section_type") in {"column", "beam"}:
            frame_properties[name] = section
        else:
            area_properties[name] = section
        return name

    columns = []
    for column in intent.get("columns", []):
        z0 = z_for_level(levels, column["base_level_id"])
        z1 = z_for_level(levels, column["top_level_id"])
        prop = add_section(column.get("section_seed_id"))
        loc = column["location"]
        columns.append(
            {
                "id": column["id"],
                "property": prop,
                "start": [float(loc["x"]) / 1000.0, float(loc["y"]) / 1000.0, z0 / 1000.0],
                "end": [float(loc["x"]) / 1000.0, float(loc["y"]) / 1000.0, z1 / 1000.0],
            }
        )

    beams = []
    for beam in intent.get("beams", []):
        z = z_for_level(levels, beam["level_id"])
        prop = add_section(beam.get("section_seed_id"))
        beams.append(
            {
                "id": beam["id"],
                "level_id": beam["level_id"],
                "property": prop,
                "start": point3(beam["start"], z),
                "end": point3(beam["end"], z),
                "span_m": round(beam_span_m(beam), 3),
            }
        )

    walls = []
    for wall in intent.get("walls", []):
        z0 = z_for_level(levels, wall["base_level_id"])
        z1 = z_for_level(levels, wall["top_level_id"])
        prop = add_section("SC-WA-CORE-400")
        pts = wall["centerline"]
        walls.append(
            {
                "id": wall["id"],
                "property": prop,
                "base_level_id": wall["base_level_id"],
                "top_level_id": wall["top_level_id"],
                "polyline_m": [point3(pt, z0) for pt in pts],
                "top_z_m": z1 / 1000.0,
                "thickness_m": float(wall.get("thickness", 250.0)) / 1000.0,
            }
        )

    slabs = []
    for slab in intent.get("slabs", []):
        z = z_for_level(levels, slab["level_id"])
        prop = add_section(slab.get("section_seed_id"))
        slabs.append(
            {
                "id": slab["id"],
                "level_id": slab["level_id"],
                "property": prop,
                "polygon_m": [point3(pt, z) for pt in slab["boundary"]],
                "thickness_m": float(slab.get("thickness_seed", 0.0)) / 1000.0,
            }
        )

    return {
        "source_model": model.get("metadata", {}).get("project_id", ""),
        "units": "kN_m_C",
        "etabs_version_target": "ETABS 21.1 via ETABSv1 / CSiAPIv1 COM",
        "api_entrypoints_found": ["CSI.ETABS.API.ETABSObject", "ETABSv1.Helper", "CSiAPIv1.Helper"],
        "stories": [
            {
                "id": level["id"],
                "name": level["name"],
                "elevation_m": float(level.get("elevation", 0.0)) / 1000.0,
                "role": level.get("role", "other"),
            }
            for level in intent.get("levels", [])
        ],
        "frame_properties": frame_properties,
        "area_properties": area_properties,
        "columns": columns,
        "beams": beams,
        "walls": walls,
        "slabs": slabs,
        "loads": seed.get("loads", []),
        "load_combinations": seed.get("load_combinations", []),
        "warnings": [
            "This is an ETABS API command plan, not an executed .EDB model.",
            "Standard-floor groups must be expanded or assigned story replication before ETABS analysis.",
            "PT/composite beam assumptions need ETABS section/property mapping before design checks.",
            "Opening cuts in slab areas need explicit ETABS area meshing/opening workflow.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a dry-run ETABS API import plan from a neutral structural model.")
    parser.add_argument("input_json", help="Neutral structural model JSON.")
    parser.add_argument("output_plan", help="Output ETABS import plan JSON.")
    args = parser.parse_args()

    model = load_json(Path(args.input_json).resolve())
    plan = build_plan(model)
    output = Path(args.output_plan).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"etabs_plan_written={output}")
    print(f"columns={len(plan['columns'])}")
    print(f"beams={len(plan['beams'])}")
    print(f"walls={len(plan['walls'])}")
    print(f"slabs={len(plan['slabs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
