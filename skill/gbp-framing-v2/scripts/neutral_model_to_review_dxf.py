#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import ezdxf
from ezdxf import units


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def add_text(msp, text: str, x: float, y: float, height: float = 180, layer: str = "TEXT", rotation: float = 0.0) -> None:
    msp.add_text(text, dxfattribs={"layer": layer, "height": height, "rotation": rotation}).set_placement((x, y))


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


def wall_width(wall: dict) -> float:
    return float(wall.get("thickness", 250))


def build_dxf(model: dict, output_path: Path) -> None:
    intent = model["intent_model"]
    sections = {s["id"]: s for s in model["analysis_seed_model"]["sections"]}

    doc = ezdxf.new(setup=True)
    doc.units = units.MM
    layers = {
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
    for name, color in layers.items():
        if name not in doc.layers:
            doc.layers.new(name, dxfattribs={"color": color})

    msp = doc.modelspace()

    for grid in intent.get("grids", []):
        pts = [(p["x"], p["y"]) for p in grid["curve"]]
        msp.add_lwpolyline(pts, dxfattribs={"layer": "GRID"})
        x, y = pts[-1]
        add_text(msp, grid["label"], x + 250, y + 250, 220, "TEXT")

    for boundary in intent.get("boundaries", []):
        pts = [(p["x"], p["y"]) for p in boundary["polyline"]]
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "BOUNDARY"})

    for keepout in intent.get("keepouts", []):
        pts = [(p["x"], p["y"]) for p in keepout["boundary"]]
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "KEEP_OUT"})

    for core_zone in intent.get("core_zones", []):
        pts = [(p["x"], p["y"]) for p in core_zone["boundary"]]
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "CORE_ZONE"})

    for slab in intent.get("slabs", []):
        pts = [(p["x"], p["y"]) for p in slab["boundary"]]
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "SLAB"})
        add_text(msp, slab["id"], pts[0][0] + 300, pts[0][1] + 300, 140, "TEXT")

    for opening in intent.get("openings", []):
        pts = [(p["x"], p["y"]) for p in opening["boundary"]]
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "OPENING"})
        cx = sum(x for x, _ in pts[:-1]) / max(len(pts) - 1, 1)
        cy = sum(y for _, y in pts[:-1]) / max(len(pts) - 1, 1)
        add_text(msp, opening["id"], cx, cy, 140, "TEXT")

    for wall in intent.get("walls", []):
        pts = [(p["x"], p["y"]) for p in wall["centerline"]]
        poly = thick_polyline(pts[0], pts[-1], wall_width(wall))
        if poly:
            msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": "WALL"})
            add_text(msp, wall["id"], pts[0][0] + 180, pts[0][1] + 180, 120, "TEXT")

    for beam in intent.get("beams", []):
        p1 = (beam["start"]["x"], beam["start"]["y"])
        p2 = (beam["end"]["x"], beam["end"]["y"])
        poly = thick_polyline(p1, p2, beam_width(sections, beam.get("section_seed_id")))
        if poly:
            msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": "BEAM"})
            cx = (p1[0] + p2[0]) / 2.0
            cy = (p1[1] + p2[1]) / 2.0
            add_text(msp, beam["id"], cx + 150, cy + 150, 110, "TEXT")

    for column in intent.get("columns", []):
        x = column["location"]["x"]
        y = column["location"]["y"]
        rect = column_rect(sections, column.get("section_seed_id"), x, y)
        msp.add_lwpolyline(rect, close=True, dxfattribs={"layer": "COLUMN"})
        add_text(msp, column["id"], x + 420, y + 420, 110, "TEXT")

    add_text(msp, "GBP Framing V2 Review DXF", 500, 17000, 240, "TEXT")
    add_text(msp, "JSON remains source_of_truth; DXF is review-only.", 500, 16650, 160, "TEXT")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert GBP Framing V2 neutral model JSON to a Revit review DXF.")
    parser.add_argument("input_json", help="Path to neutral structural model JSON.")
    parser.add_argument("output_dxf", help="Path to output DXF.")
    args = parser.parse_args()

    model = load_json(Path(args.input_json).resolve())
    build_dxf(model, Path(args.output_dxf).resolve())
    print(f"dxf_written={args.output_dxf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
