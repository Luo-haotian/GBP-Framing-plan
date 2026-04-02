#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def to_mm_with_offset(x_m: float, y_m: float, x0: float, y0: float) -> tuple[float, float]:
    return x_m * 1000.0 + x0, y_m * 1000.0 + y0


def calc_pix(x: float, y: float, cx: float, cy: float, w: float, h: float, scale: float) -> tuple[int, int]:
    # same style as sample: pixel around image center with a scalar mapping
    xp = int(round((x - cx) * scale + w / 2.0))
    yp = int(round((cy - y) * scale + h / 2.0))
    return xp, yp


def make_line_entity(kind: str, idx: int, p1: tuple[float, float], p2: tuple[float, float], props: dict, cx: float, cy: float, w: float, h: float, scale: float) -> dict:
    x1, y1 = p1
    x2, y2 = p2
    x1p, y1p = calc_pix(x1, y1, cx, cy, w, h, scale)
    x2p, y2p = calc_pix(x2, y2, cx, cy, w, h, scale)
    direction = "x" if abs(x2 - x1) >= abs(y2 - y1) else "y"
    out = {
        "type": kind,
        "id": idx,
        "xs": [x1, x2],
        "ys": [y1, y2],
        "xspix": [x1p, x2p],
        "yspix": [y1p, y2p],
        "props": {"dir": direction, **props},
        "loads": None,
    }
    return out


def build_aistructure(logic: dict, template: dict | None = None) -> dict:
    nodes = {n["id"]: (float(n["x"]), float(n["y"])) for n in logic.get("nodes", [])}
    if not nodes:
        raise ValueError("Input logic JSON has no nodes.")

    # World offsets to mimic AIstructArchi style coordinates
    x_offset = 320000.0
    y_offset = 2000.0

    # Image mapping defaults; can be inherited from template
    img_w = 1024.0
    img_h = 512.0
    scale_ratio = 0.02
    if template:
        std0 = template.get("StdStories", [{}])[0]
        imc = std0.get("ImageConditions", {})
        img_w = float(imc.get("ImgW", img_w))
        img_h = float(imc.get("ImgH", img_h))
        scale_ratio = float(imc.get("ScaleRatio", scale_ratio))

    # Convert all logic nodes to AI world coordinates first
    world_nodes = {}
    for nid, (x, y) in nodes.items():
        world_nodes[nid] = to_mm_with_offset(x, y, x_offset, y_offset)

    xs_all = [v[0] for v in world_nodes.values()]
    ys_all = [v[1] for v in world_nodes.values()]
    cx = (min(xs_all) + max(xs_all)) / 2.0
    cy = (min(ys_all) + max(ys_all)) / 2.0

    archiwalls = []
    candibeams = []
    shearwalls = []
    beams = []
    columns = []
    windoors = []

    eid = 0

    # 1) envelope edges as archiwalls (architectural boundary)
    poly = logic.get("envelope", {}).get("polyline", [])
    for i in range(len(poly) - 1):
        x1m, y1m = float(poly[i][0]), float(poly[i][1])
        x2m, y2m = float(poly[i + 1][0]), float(poly[i + 1][1])
        p1 = to_mm_with_offset(x1m, y1m, x_offset, y_offset)
        p2 = to_mm_with_offset(x2m, y2m, x_offset, y_offset)
        archiwalls.append(make_line_entity("archiwall", eid, p1, p2, {"candiwall": "NoMove"}, cx, cy, img_w, img_h, scale_ratio))
        eid += 1

    # 2) beams as candidate beams (best compatibility with sample)
    for b in logic.get("beams", []):
        p1 = world_nodes[b["start"]]
        p2 = world_nodes[b["end"]]
        candibeams.append(make_line_entity("candibeam", eid, p1, p2, {}, cx, cy, img_w, img_h, scale_ratio))
        eid += 1

    # 3) shear walls as archiwalls + shearwalls
    for w in logic.get("shear_walls", []):
        p1 = world_nodes[w["start"]]
        p2 = world_nodes[w["end"]]
        role = w.get("role", "core")
        archiwalls.append(make_line_entity("archiwall", eid, p1, p2, {"candiwall": "NoMove", "role": role}, cx, cy, img_w, img_h, scale_ratio))
        eid += 1
        shearwalls.append(make_line_entity("shearwall", eid, p1, p2, {"role": role}, cx, cy, img_w, img_h, scale_ratio))
        eid += 1

    # 4) keep beams list as explicit structure lines too
    for b in logic.get("beams", []):
        p1 = world_nodes[b["start"]]
        p2 = world_nodes[b["end"]]
        beams.append(make_line_entity("beam", eid, p1, p2, {"kind": b.get("type", "secondary")}, cx, cy, img_w, img_h, scale_ratio))
        eid += 1

    # 5) columns as tiny crosses (two short lines) for better geometric visibility
    cross = 150.0
    for c in logic.get("columns", []):
        x, y = world_nodes[c["node"]]
        p1 = (x - cross, y)
        p2 = (x + cross, y)
        columns.append(make_line_entity("column", eid, p1, p2, {"section": c.get("section", "")}, cx, cy, img_w, img_h, scale_ratio))
        eid += 1
        p3 = (x, y - cross)
        p4 = (x, y + cross)
        columns.append(make_line_entity("column", eid, p3, p4, {"section": c.get("section", "")}, cx, cy, img_w, img_h, scale_ratio))
        eid += 1

    # Minimal space container; keep empty categories to match sample naming
    archi_spaces = {
        "Rooms": [],
        "Balconys": [],
        "Elevators": [],
        "Lavatorys": [],
        "Kitchens": [],
        "Stairs": [],
        "LDKrooms": [],
        "Bedrooms": [],
        "Baywinows": [],
    }

    # Single standard story + natural stories
    std_story = {
        "StdStoryID": 1,
        "Elements": {
            "ArchiWalls": archiwalls,
            "WinDoors": windoors,
            "ShearWalls": shearwalls,
            "Beams": beams,
            "CandiBeams": candibeams,
            "Slabs": [],
            "Columns": columns,
        },
        "ArchiSpaces": archi_spaces,
        "StoryConditions": {
            "Wallthick": 250,
            "Wallgrade": "C40",
            "Beamheight": 400,
            "Beamgrade": "C30",
            "Slabthick": 120,
            "Slabgrade": "C30",
        },
        "ImageConditions": {
            "ScaleRatio": scale_ratio,
            "CenterX": cx,
            "CenterY": cy,
            "ImgW": img_w,
            "ImgH": img_h,
        },
        "AlignPoint": {"X": archiwalls[0]["xs"][0], "Y": archiwalls[0]["ys"][0]} if archiwalls else {"X": cx, "Y": cy},
    }

    out = {
        "DesignConditions": {
            "Intensity": 0.2,
            "TotalHeight": 15.0,
            "SitePeriod": 0.4,
            "NumStdstory": 1,
        },
        "StdStories": [std_story],
        "NaturalStories": [{"NaturalStoryID": i, "StdStoryID": 1, "StoryHeight": 3000.0} for i in range(1, 6)],
    }

    # If a template exists, inherit known top-level values where helpful
    if template:
        tdc = template.get("DesignConditions", {})
        out["DesignConditions"]["Intensity"] = tdc.get("Intensity", out["DesignConditions"]["Intensity"])
        out["DesignConditions"]["SitePeriod"] = tdc.get("SitePeriod", out["DesignConditions"]["SitePeriod"])

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert logic JSON to AIstructure-style import JSON.")
    parser.add_argument("--input", required=True, help="Path to logic JSON.")
    parser.add_argument("--output", required=True, help="Path to AIstructure JSON.")
    parser.add_argument("--template", default="", help="Optional AIstructure sample JSON for defaults.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    template_path = Path(args.template) if args.template else None

    logic = load_json(input_path)
    template = load_json(template_path) if template_path and template_path.exists() else None
    out = build_aistructure(logic, template)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
