#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import ezdxf
from ezdxf import units


BASE_LAYERS = {
    "GRID": 8,
    "BOUNDARY": 6,
    "KEEP_OUT": 4,
    "CORE_ZONE": 30,
    "COLUMN": 1,
    "BEAM": 5,
    "WALL": 3,
    "SLAB": 7,
    "OPENING": 2,
    "TEXT": 7,
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def layer_name(base: str, level_id: str | None, separate_levels: bool) -> str:
    if not separate_levels or not level_id or base == "TEXT":
        return base
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in level_id)
    return f"{safe}_{base}"


def ensure_layer(doc, name: str, color: int) -> None:
    if name not in doc.layers:
        doc.layers.new(name, dxfattribs={"color": color})


def add_text(msp, text: str, x: float, y: float, height: float = 180, layer: str = "TEXT", rotation: float = 0.0) -> None:
    msp.add_text(text, dxfattribs={"layer": layer, "height": height, "rotation": rotation}).set_placement((x, y))


def shift_point(point: dict, dx: float, dy: float) -> tuple[float, float]:
    return (float(point["x"]) + dx, float(point["y"]) + dy)


def shift_xy(x: float, y: float, dx: float, dy: float) -> tuple[float, float]:
    return (float(x) + dx, float(y) + dy)


def rect_from_center(x: float, y: float, b: float, h: float) -> list[tuple[float, float]]:
    bx = b / 2.0
    hy = h / 2.0
    return [(x - bx, y - hy), (x + bx, y - hy), (x + bx, y + hy), (x - bx, y + hy), (x - bx, y - hy)]


def thick_polyline(p1: tuple[float, float], p2: tuple[float, float], width: float) -> list[tuple[float, float]] | None:
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return None
    nx = -dy / length
    ny = dx / length
    t = width / 2.0
    return [
        (x1 + nx * t, y1 + ny * t),
        (x1 - nx * t, y1 - ny * t),
        (x2 - nx * t, y2 - ny * t),
        (x2 + nx * t, y2 + ny * t),
        (x1 + nx * t, y1 + ny * t),
    ]


def beam_width(section_lookup: dict[str, dict], section_id: str | None) -> float:
    if not section_id:
        return 250.0
    section = section_lookup.get(section_id, {})
    return float(section.get("geometry", {}).get("b_mm", 250))


def column_rect(section_lookup: dict[str, dict], section_id: str | None, x: float, y: float) -> list[tuple[float, float]]:
    section = section_lookup.get(section_id or "", {})
    geom = section.get("geometry", {})
    b = float(geom.get("b_mm", 600))
    h = float(geom.get("h_mm", 600))
    return rect_from_center(x, y, b, h)


def section_label(section_lookup: dict[str, dict], section_id: str | None, fallback: str = "section?") -> str:
    if not section_id:
        return fallback
    section = section_lookup.get(section_id, {})
    geom = section.get("geometry", {})
    if "b_mm" in geom and "h_mm" in geom:
        return f"{int(float(geom['b_mm']))}x{int(float(geom['h_mm']))}"
    if "thickness_mm" in geom:
        return f"t{int(float(geom['thickness_mm']))}"
    return section.get("name", section_id)


def wall_width(wall: dict) -> float:
    return float(wall.get("thickness", 250))


def drawing_extent(intent: dict) -> tuple[float, float]:
    max_x = 0.0
    max_y = 0.0

    def add_points(points: list[dict]) -> None:
        nonlocal max_x, max_y
        for point in points:
            max_x = max(max_x, float(point["x"]))
            max_y = max(max_y, float(point["y"]))

    for grid in intent.get("grids", []):
        add_points(grid.get("curve", []))
    for key, field in (("boundaries", "polyline"), ("keepouts", "boundary"), ("core_zones", "boundary"), ("slabs", "boundary"), ("openings", "boundary")):
        for item in intent.get(key, []):
            add_points(item.get(field, []))
    for beam in intent.get("beams", []):
        add_points([beam["start"], beam["end"]])
    for column in intent.get("columns", []):
        add_points([column["location"]])
    for wall in intent.get("walls", []):
        add_points(wall.get("centerline", []))
    return max(max_x, 1000.0), max(max_y, 1000.0)


def level_groups(intent: dict, separate_levels: bool) -> list[dict]:
    levels = intent.get("levels", [])
    if not separate_levels:
        return [{"id": None, "name": "Flattened review plan", "elevation": 0.0}]

    explicit_ids: set[str] = set()
    for key in ("beams", "slabs", "openings", "boundaries", "keepouts", "core_zones"):
        for item in intent.get(key, []):
            level_id = item.get("level_id")
            if level_id:
                explicit_ids.add(level_id)

    groups = [level for level in levels if level["id"] in explicit_ids]
    if groups:
        return groups
    return levels or [{"id": None, "name": "Review plan", "elevation": 0.0}]


def level_in_vertical_range(level: dict, item: dict, level_lookup: dict[str, dict]) -> bool:
    level_id = level.get("id")
    if not level_id:
        return True
    base = level_lookup.get(item.get("base_level_id", ""))
    top = level_lookup.get(item.get("top_level_id", ""))
    if not base or not top:
        return True
    z = float(level.get("elevation", 0))
    z0 = min(float(base.get("elevation", 0)), float(top.get("elevation", 0)))
    z1 = max(float(base.get("elevation", 0)), float(top.get("elevation", 0)))
    return z0 <= z <= z1


def build_dxf(model: dict, output_path: Path, separate_levels: bool = True) -> None:
    intent = model["intent_model"]
    sections = {s["id"]: s for s in model["analysis_seed_model"]["sections"]}
    level_lookup = {level["id"]: level for level in intent.get("levels", [])}
    groups = level_groups(intent, separate_levels)
    extent_x, extent_y = drawing_extent(intent)
    margin_x = 15000.0
    margin_y = 25000.0
    panel_width = extent_x + margin_x
    panel_height = extent_y + margin_y

    doc = ezdxf.new(setup=True)
    doc.units = units.MM
    for name, color in BASE_LAYERS.items():
        ensure_layer(doc, name, color)
    for group in groups:
        for base, color in BASE_LAYERS.items():
            ensure_layer(doc, layer_name(base, group.get("id"), separate_levels), color)

    msp = doc.modelspace()

    for index, group in enumerate(groups):
        dx = (index % 2) * panel_width
        dy = -(index // 2) * panel_height
        level_id = group.get("id")
        title = group.get("name", level_id or "Flattened review plan")
        add_text(msp, f"{title} ({level_id or 'ALL'})", dx, dy + extent_y + 7000, 900, "TEXT")
        add_text(msp, "JSON remains source_of_truth; DXF is review-only.", dx, dy + extent_y + 5600, 350, "TEXT")

        for grid in intent.get("grids", []):
            pts = [shift_point(p, dx, dy) for p in grid["curve"]]
            msp.add_lwpolyline(pts, dxfattribs={"layer": layer_name("GRID", level_id, separate_levels)})
            x, y = pts[-1]
            add_text(msp, grid["label"], x + 250, y + 250, 220, "TEXT")

        for boundary in intent.get("boundaries", []):
            if separate_levels and boundary.get("level_id") != level_id:
                continue
            pts = [shift_point(p, dx, dy) for p in boundary["polyline"]]
            msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer_name("BOUNDARY", level_id, separate_levels)})

        for keepout in intent.get("keepouts", []):
            if separate_levels and keepout.get("level_id") != level_id:
                continue
            pts = [shift_point(p, dx, dy) for p in keepout["boundary"]]
            msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer_name("KEEP_OUT", level_id, separate_levels)})

        for core_zone in intent.get("core_zones", []):
            if separate_levels and core_zone.get("level_id") != level_id:
                continue
            pts = [shift_point(p, dx, dy) for p in core_zone["boundary"]]
            msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer_name("CORE_ZONE", level_id, separate_levels)})

        for slab in intent.get("slabs", []):
            if separate_levels and slab.get("level_id") != level_id:
                continue
            pts = [shift_point(p, dx, dy) for p in slab["boundary"]]
            msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer_name("SLAB", level_id, separate_levels)})
            label = f"{slab['id']} slab {int(float(slab.get('thickness_seed', 0)))}mm"
            add_text(msp, label, pts[0][0] + 300, pts[0][1] + 300, 220, "TEXT")

        for opening in intent.get("openings", []):
            if separate_levels and opening.get("level_id") != level_id:
                continue
            pts = [shift_point(p, dx, dy) for p in opening["boundary"]]
            msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer_name("OPENING", level_id, separate_levels)})
            cx = sum(x for x, _ in pts[:-1]) / max(len(pts) - 1, 1)
            cy = sum(y for _, y in pts[:-1]) / max(len(pts) - 1, 1)
            add_text(msp, opening["id"], cx, cy, 180, "TEXT")

        for wall in intent.get("walls", []):
            if separate_levels and not level_in_vertical_range(group, wall, level_lookup):
                continue
            pts = [shift_point(p, dx, dy) for p in wall["centerline"]]
            poly = thick_polyline(pts[0], pts[-1], wall_width(wall))
            if poly:
                msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": layer_name("WALL", level_id, separate_levels)})
                add_text(msp, f"{wall['id']} t{int(float(wall_width(wall)))}", pts[0][0] + 180, pts[0][1] + 180, 180, "TEXT")

        for beam in intent.get("beams", []):
            if separate_levels and beam.get("level_id") != level_id:
                continue
            p1 = shift_point(beam["start"], dx, dy)
            p2 = shift_point(beam["end"], dx, dy)
            poly = thick_polyline(p1, p2, beam_width(sections, beam.get("section_seed_id")))
            if poly:
                msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": layer_name("BEAM", level_id, separate_levels)})
                cx = (p1[0] + p2[0]) / 2.0
                cy = (p1[1] + p2[1]) / 2.0
                label = f"{beam['id']} B{section_label(sections, beam.get('section_seed_id'))}"
                add_text(msp, label, cx + 150, cy + 150, 160, "TEXT")

        for column in intent.get("columns", []):
            if separate_levels and not level_in_vertical_range(group, column, level_lookup):
                continue
            x, y = shift_xy(column["location"]["x"], column["location"]["y"], dx, dy)
            rect = column_rect(sections, column.get("section_seed_id"), x, y)
            msp.add_lwpolyline(rect, close=True, dxfattribs={"layer": layer_name("COLUMN", level_id, separate_levels)})
            label = f"{column['id']} C{section_label(sections, column.get('section_seed_id'))}"
            add_text(msp, label, x + 420, y + 420, 160, "TEXT")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert GBP Structural Pipeline neutral model JSON to a level-separated Revit review DXF.")
    parser.add_argument("input_json", help="Path to neutral structural model JSON.")
    parser.add_argument("output_dxf", help="Path to output DXF.")
    parser.add_argument("--flatten", action="store_true", help="Draw all entities on one 2D plan, matching the legacy review output.")
    args = parser.parse_args()

    model = load_json(Path(args.input_json).resolve())
    build_dxf(model, Path(args.output_dxf).resolve(), separate_levels=not args.flatten)
    print(f"dxf_written={args.output_dxf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
