#!/usr/bin/env python3
"""
Convert framing JSON to a YJK-oriented DXF with layer attributes.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

try:
    import ezdxf
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: ezdxf. Install with: pip install ezdxf"
    ) from exc


LAYER_MAP = {
    "envelope": "YJK_ENVELOPE",
    "column": "YJK_COL",
    "beam_primary": "YJK_BEAM_PRIMARY",
    "beam_secondary": "YJK_BEAM_SECONDARY",
    "wall_core": "YJK_SHEAR_CORE",
    "wall_wing": "YJK_SHEAR_WING",
    "node_anno": "YJK_NODE_ANNO",
}


def _ensure_layers(doc: ezdxf.EzDxf) -> None:
    for name in LAYER_MAP.values():
        if name not in doc.layers:
            doc.layers.new(name)


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON at line {exc.lineno}: {exc.msg}") from exc


def _node_index(data: dict) -> dict[str, tuple[float, float]]:
    nodes = {}
    for node in data.get("nodes", []):
        node_id = node["id"]
        nodes[node_id] = (float(node["x"]), float(node["y"]))
    return nodes


def _add_envelope(msp, data: dict) -> None:
    poly = data.get("envelope", {}).get("polyline", [])
    if len(poly) < 2:
        return
    points = [(float(p[0]), float(p[1])) for p in poly]
    msp.add_lwpolyline(points, dxfattribs={"layer": LAYER_MAP["envelope"]})


def _add_columns(msp, nodes: dict[str, tuple[float, float]], data: dict) -> None:
    for col in data.get("columns", []):
        node_id = col["node"]
        if node_id not in nodes:
            raise SystemExit(f"Column {col.get('id', '?')} references missing node: {node_id}")
        x, y = nodes[node_id]
        msp.add_circle((x, y), radius=0.25, dxfattribs={"layer": LAYER_MAP["column"]})
        msp.add_text(
            col.get("id", "COL"),
            dxfattribs={"layer": LAYER_MAP["node_anno"], "height": 0.25},
        ).set_placement((x + 0.3, y + 0.3))


def _add_beams(msp, nodes: dict[str, tuple[float, float]], data: dict) -> None:
    for beam in data.get("beams", []):
        start_id = beam["start"]
        end_id = beam["end"]
        if start_id not in nodes or end_id not in nodes:
            raise SystemExit(f"Beam {beam.get('id', '?')} has unknown node reference.")
        layer = (
            LAYER_MAP["beam_primary"]
            if beam.get("type", "").lower() == "primary"
            else LAYER_MAP["beam_secondary"]
        )
        msp.add_line(nodes[start_id], nodes[end_id], dxfattribs={"layer": layer})


def _add_shear_walls(msp, nodes: dict[str, tuple[float, float]], data: dict) -> None:
    for wall in data.get("shear_walls", []):
        start_id = wall["start"]
        end_id = wall["end"]
        if start_id not in nodes or end_id not in nodes:
            raise SystemExit(f"Wall {wall.get('id', '?')} has unknown node reference.")
        role = wall.get("role", "").lower()
        layer = LAYER_MAP["wall_core"] if role == "core" else LAYER_MAP["wall_wing"]
        (x1, y1), (x2, y2) = nodes[start_id], nodes[end_id]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        nx, ny = -dy / length, dx / length
        t = 0.15
        poly = [
            (x1 + nx * t, y1 + ny * t),
            (x1 - nx * t, y1 - ny * t),
            (x2 - nx * t, y2 - ny * t),
            (x2 + nx * t, y2 + ny * t),
            (x1 + nx * t, y1 + ny * t),
        ]
        msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": layer})


def convert(input_path: Path, output_path: Path) -> None:
    data = _load_json(input_path)
    nodes = _node_index(data)

    doc = ezdxf.new(setup=True)
    _ensure_layers(doc)
    msp = doc.modelspace()

    _add_envelope(msp, data)
    _add_columns(msp, nodes, data)
    _add_beams(msp, nodes, data)
    _add_shear_walls(msp, nodes, data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert framing JSON to DXF for YJK workflows.")
    parser.add_argument("--input", required=True, help="Path to framing JSON.")
    parser.add_argument("--output", required=True, help="Path to output DXF.")
    args = parser.parse_args()

    convert(Path(args.input), Path(args.output))
    print(f"DXF written: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
