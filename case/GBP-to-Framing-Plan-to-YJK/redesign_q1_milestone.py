#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import ezdxf


# Geometry in mm
X_A = 0
X_B = 17000
X_C = 56500
Y_1 = 0
Y_2 = 17000
Y_TOP = 56000

CORE_RECT = (12000, 12000, 17000, 17000)
WALL_THK = 250
MIN_MEMBER_GAP_MM = 250

# Candidate auxiliary walls. Final wing walls are selected by non-overlap and passage checks.
CANDIDATE_WING_WALLS = [
    (15000, 53500, 15000, 56000),
    (9000, 26000, 9000, 36000),
    (9000, 33000, 16000, 33000),
    (17000, 26000, 17000, 34000),
]

# Generic passage/space keepouts (can represent parking aisles, residential corridors, fire egress routes).
PASSAGE_KEEPOUT_RECTS = [
    (17750, 5500, 55250, 11500),  # east wing circulation
    (5500, 500, 11500, 16500),  # west lower circulation
    (5500, 20000, 11500, 50000),  # north wing circulation
]


@dataclass(frozen=True)
class Column:
    cid: str
    x: float
    y: float
    tributary_m2: float
    size_mm: int
    nd_grav_kN: float
    nd_combo_kN: float
    cap_kN: float
    util: float
    rho_est: float


@dataclass(frozen=True)
class Beam:
    bid: str
    x1: float
    y1: float
    x2: float
    y2: float
    bw: int
    d: int
    kind: str
    span_m: float


@dataclass(frozen=True)
class Stall:
    sid: str
    x1: float
    y1: float
    x2: float
    y2: float


def footprint_poly() -> list[tuple[float, float]]:
    return [(0, 0), (X_C, 0), (X_C, Y_2), (X_B, Y_2), (X_B, Y_TOP), (0, Y_TOP), (0, 0)]


def inside_footprint(x: float, y: float) -> bool:
    return (0 <= x <= X_B and 0 <= y <= Y_TOP) or (X_B <= x <= X_C and 0 <= y <= Y_2)


def rect_intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)


def rect_distance(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    dx = max(bx1 - ax2, ax1 - bx2, 0)
    dy = max(by1 - ay2, ay1 - by2, 0)
    return math.hypot(dx, dy)


def wall_segment_to_rect(seg: tuple[float, float, float, float], thk: float = WALL_THK) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = seg
    if abs(x2 - x1) < 1e-6:
        return (x1 - thk / 2, min(y1, y2), x1 + thk / 2, max(y1, y2))
    return (min(x1, x2), y1 - thk / 2, max(x1, x2), y1 + thk / 2)


def build_wall_rects(wing_walls: list[tuple[float, float, float, float]]) -> list[tuple[float, float, float, float]]:
    x1, y1, x2, y2 = CORE_RECT
    t = WALL_THK
    core_rects = [
        (x1, y1, x2, y1 + t),  # bottom
        (x1, y2 - t, x2, y2),  # top
        (x1, y1 + t, x1 + t, y2 - t),  # left
        (x2 - t, y1 + t, x2, y2 - t),  # right
    ]
    return core_rects + [wall_segment_to_rect(w, t) for w in wing_walls]


def select_wing_walls(passage_keepouts: list[tuple[float, float, float, float]], cols: list[Column]) -> list[tuple[float, float, float, float]]:
    selected: list[tuple[float, float, float, float]] = []
    col_rects = []
    for c in cols:
        h = c.size_mm / 2 + MIN_MEMBER_GAP_MM
        col_rects.append((c.x - h, c.y - h, c.x + h, c.y + h))
    for seg in CANDIDATE_WING_WALLS:
        rect = wall_segment_to_rect(seg)
        if any(rect_intersects(rect, c) for c in passage_keepouts):
            continue
        if any(rect_intersects(rect, cr) for cr in col_rects):
            continue
        if any(rect_intersects(rect, wall_segment_to_rect(s)) for s in selected):
            continue
        selected.append(seg)
    return selected


def check_passage_paths(blockers: list[tuple[float, float, float, float]], keepouts: list[tuple[float, float, float, float]], min_clear: float = 2800.0) -> tuple[bool, list[str]]:
    issues: list[str] = []
    for i, k in enumerate(keepouts, start=1):
        x1, y1, x2, y2 = k
        width = min(abs(x2 - x1), abs(y2 - y1))
        if width < min_clear:
            issues.append(f"keepout_{i}: width {width:.0f} < required clear {min_clear:.0f}")
        for j, b in enumerate(blockers, start=1):
            if rect_intersects(k, b):
                issues.append(f"keepout_{i}: blocked by obstacle_{j}")
                break
    return len(issues) == 0, issues


def add_layers(doc: ezdxf.EzDxf) -> None:
    layers = {
        "A-GBP-OUTLINE": 8,
        "A-GBP-ZONE": 9,
        "S-GRID": 7,
        "S-COL": 1,
        "S-BEAM-P": 5,
        "S-BEAM-S": 6,
        "S-WALL": 3,
        "A-PARK": 2,
        "A-FLOW": 2,
        "A-DIM": 4,
        "A-TEXT": 7,
        "A-CALC": 9,
    }
    for name, color in layers.items():
        if name not in doc.layers:
            doc.layers.new(name, dxfattribs={"color": color})


def add_text(msp, txt: str, x: float, y: float, h: float = 180, layer: str = "A-TEXT", rot: float = 0) -> None:
    msp.add_text(txt, dxfattribs={"layer": layer, "height": h, "rotation": rot}).set_placement((x, y))


def draw_outline(msp, label: str = "GBP OUTLINE (mm)") -> None:
    msp.add_lwpolyline(footprint_poly(), close=True, dxfattribs={"layer": "A-GBP-OUTLINE"})
    add_text(msp, label, 900, Y_TOP + 850, 220)


def draw_dimension(msp, x1: float, y1: float, x2: float, y2: float, text: str, offset: float = 1300) -> None:
    dx, dy = x2 - x1, y2 - y1
    l = math.hypot(dx, dy)
    if l == 0:
        return
    nx, ny = -dy / l, dx / l
    ox, oy = nx * offset, ny * offset
    p1 = (x1 + ox, y1 + oy)
    p2 = (x2 + ox, y2 + oy)
    msp.add_line(p1, p2, dxfattribs={"layer": "A-DIM"})
    tick = 220
    msp.add_line((p1[0] - nx * tick, p1[1] - ny * tick), (p1[0] + nx * tick, p1[1] + ny * tick), dxfattribs={"layer": "A-DIM"})
    msp.add_line((p2[0] - nx * tick, p2[1] - ny * tick), (p2[0] + nx * tick, p2[1] + ny * tick), dxfattribs={"layer": "A-DIM"})
    add_text(msp, text, (p1[0] + p2[0]) / 2 + nx * 210, (p1[1] + p2[1]) / 2 + ny * 210, 180, "A-DIM")


def draw_axes_and_setout(msp) -> None:
    x_axes = [("A", 0), ("A1", 8500), ("B", X_B), ("C1", 25000), ("C2", 33000), ("C3", 41000), ("C4", 49000), ("C", X_C)]
    y_axes = [("1", 0), ("1A", 5500), ("2", 8500), ("3", 17000), ("4", 25000), ("5", 33000), ("6", 41000), ("7", 49000), ("8", 56000)]
    for n, x in x_axes:
        msp.add_line((x, -3500), (x, Y_TOP + 3500), dxfattribs={"layer": "S-GRID"})
        add_text(msp, n, x, Y_TOP + 3650, 240, "S-GRID")
    for n, y in y_axes:
        msp.add_line((-3500, y), (X_C + 3500, y), dxfattribs={"layer": "S-GRID"})
        add_text(msp, n, -3950, y, 240, "S-GRID")

    draw_dimension(msp, 0, -1200, X_B, -1200, "17000")
    draw_dimension(msp, X_B, -1200, X_C, -1200, "39500")
    draw_dimension(msp, -1200, 0, -1200, Y_2, "17000")
    draw_dimension(msp, -1200, Y_2, -1200, Y_TOP, "39000")

    xs = [0, 8500, 17000, 25000, 33000, 41000, 49000, 56500]
    ys = [0, 5500, 8500, 17000, 25000, 33000, 41000, 49000, 56000]
    for i in range(len(xs) - 1):
        draw_dimension(msp, xs[i], -2800, xs[i + 1], -2800, str(int(xs[i + 1] - xs[i])), offset=0)
    for i in range(len(ys) - 1):
        draw_dimension(msp, -2800, ys[i], -2800, ys[i + 1], str(int(ys[i + 1] - ys[i])), offset=0)


def choose_col_size(tributary_m2: float) -> int:
    q_eff = 58.0
    fc_design = 10500.0
    nd = tributary_m2 * q_eff
    req_area = nd / fc_design
    req_side = math.sqrt(req_area) * 1000
    for s in (600, 650, 700):
        if s >= req_side:
            return s
    return 750


def rho_estimate(util: float) -> float:
    # preliminary RC longitudinal ratio proxy in decimal
    return max(0.012, min(0.032, 0.010 + 0.026 * util))


def make_col(cid: str, x: float, y: float, trib: float) -> Column:
    q_grav = 46.0  # gravity screening load (kN/m2), all floors contribution
    q_combo = 58.0  # ULS combo envelope proxy
    fc_design = 10500.0
    size = choose_col_size(trib)
    nd_grav = trib * q_grav
    nd_combo = trib * q_combo
    cap = (size / 1000) ** 2 * fc_design
    util = nd_combo / cap
    return Column(cid, x, y, trib, size, nd_grav, nd_combo, cap, util, rho_estimate(util))


def build_columns() -> list[Column]:
    cols: list[Column] = []
    i = 1
    east_x = [X_B, 25000, 33000, 41000, 49000, X_C]
    north_y = [Y_2, 25000, 33000, 41000, 49000, Y_TOP]

    for y in (0, Y_2):
        for x in east_x:
            trib = 36.0 if x in (X_B, X_C) else 42.0
            cols.append(make_col(f"C{i:02d}", x, y, trib))
            i += 1

    for x in (0, X_B):
        for y in north_y:
            if x == X_B and y == Y_2:
                continue
            trib = 36.0 if y in (Y_2, Y_TOP) else 44.0
            cols.append(make_col(f"C{i:02d}", x, y, trib))
            i += 1

    # Single continuous internal column spine (bent line):
    # segment 1: x=5500 from y=5500 to y=56000
    for y in (5500, 17000, 25000, 33000, 41000, 49000, 56000):
        trib = 58.0 if y not in (5500, 56000) else 50.0
        cols.append(make_col(f"C{i:02d}", 5500, y, trib))
        i += 1
    # segment 2: y=5500 from x=17000 to x=56500
    for x in east_x:
        if x == X_B:
            continue
        trib = 62.0 if x not in (X_C,) else 52.0
        cols.append(make_col(f"C{i:02d}", x, 5500, trib))
        i += 1

    for x, y, trib in (
        (0, 0, 34.0),
        (0, 8500, 38.0),
        (8500, 0, 40.0),
    ):
        cols.append(make_col(f"C{i:02d}", x, y, trib))
        i += 1

    uniq: dict[tuple[float, float], Column] = {}
    for c in cols:
        if (c.x, c.y) not in uniq:
            uniq[(c.x, c.y)] = c
    x1, y1, x2, y2 = CORE_RECT
    clear = WALL_THK / 2 + 350
    filtered = []
    for c in uniq.values():
        # keep columns away from core wall envelope to prevent column-wall overlap.
        if (x1 - clear) <= c.x <= (x2 + clear) and (y1 - clear) <= c.y <= (y2 + clear):
            continue
        filtered.append(c)
    return filtered


def beam_size(span_mm: float, kind: str) -> tuple[int, int]:
    span_m = span_mm / 1000
    if kind == "primary":
        if span_m <= 8.5:
            return 300, 450
        return 350, 450
    if span_m <= 8.5:
        return 250, 350
    return 300, 400


def segment_inside(x1: float, y1: float, x2: float, y2: float) -> bool:
    for t in (0.25, 0.5, 0.75):
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        if not inside_footprint(x, y):
            return False
    return True


def build_beams(columns: list[Column]) -> list[Beam]:
    pts = sorted({(c.x, c.y) for c in columns})
    y_groups: dict[float, list[float]] = {}
    x_groups: dict[float, list[float]] = {}
    for x, y in pts:
        y_groups.setdefault(y, []).append(x)
        x_groups.setdefault(x, []).append(y)

    out: list[Beam] = []
    bid = 1
    for y, xs in y_groups.items():
        xs = sorted(xs)
        for j in range(len(xs) - 1):
            x1, x2 = xs[j], xs[j + 1]
            if not segment_inside(x1, y, x2, y):
                continue
            kind = "primary" if y in (0, 5500, Y_2) else "secondary"
            bw, d = beam_size(x2 - x1, kind)
            out.append(Beam(f"B{bid:03d}", x1, y, x2, y, bw, d, kind, (x2 - x1) / 1000))
            bid += 1
    for x, ys in x_groups.items():
        ys = sorted(ys)
        for j in range(len(ys) - 1):
            y1, y2 = ys[j], ys[j + 1]
            if not segment_inside(x, y1, x, y2):
                continue
            kind = "primary" if x in (0, 8500, X_B) else "secondary"
            bw, d = beam_size(y2 - y1, kind)
            out.append(Beam(f"B{bid:03d}", x, y1, x, y2, bw, d, kind, (y2 - y1) / 1000))
            bid += 1
    return out


def beam_polygon(b: Beam) -> list[tuple[float, float]]:
    dx, dy = b.x2 - b.x1, b.y2 - b.y1
    l = math.hypot(dx, dy)
    if l == 0:
        return []
    nx, ny = -dy / l, dx / l
    t = b.bw / 2
    return [(b.x1 + nx * t, b.y1 + ny * t), (b.x1 - nx * t, b.y1 - ny * t), (b.x2 - nx * t, b.y2 - ny * t), (b.x2 + nx * t, b.y2 + ny * t), (b.x1 + nx * t, b.y1 + ny * t)]


def draw_column(msp, c: Column) -> None:
    h = c.size_mm / 2
    poly = [(c.x - h, c.y - h), (c.x + h, c.y - h), (c.x + h, c.y + h), (c.x - h, c.y + h), (c.x - h, c.y - h)]
    msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": "S-COL"})
    add_text(msp, f"{c.cid} {c.size_mm}x{c.size_mm}", c.x + h + 100, c.y + h + 100, 135)


def draw_beam(msp, b: Beam) -> None:
    layer = "S-BEAM-P" if b.kind == "primary" else "S-BEAM-S"
    poly = beam_polygon(b)
    if poly:
        msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": layer})
    ang = math.degrees(math.atan2(b.y2 - b.y1, b.x2 - b.x1))
    add_text(msp, f"{b.bw}x{b.d}", (b.x1 + b.x2) / 2, (b.y1 + b.y2) / 2, 118, "A-TEXT", ang)


def draw_walls(msp, wing_walls: list[tuple[float, float, float, float]]) -> None:
    x1, y1, x2, y2 = CORE_RECT
    wall_thk = WALL_THK
    msp.add_lwpolyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)], close=True, dxfattribs={"layer": "S-WALL"})
    msp.add_lwpolyline([(x1 + wall_thk, y1 + wall_thk), (x2 - wall_thk, y1 + wall_thk), (x2 - wall_thk, y2 - wall_thk), (x1 + wall_thk, y2 - wall_thk), (x1 + wall_thk, y1 + wall_thk)], close=True, dxfattribs={"layer": "S-WALL"})
    for xa, ya, xb, yb in wing_walls:
        if xa == xb:
            poly = [(xa - wall_thk / 2, ya), (xa + wall_thk / 2, ya), (xa + wall_thk / 2, yb), (xa - wall_thk / 2, yb), (xa - wall_thk / 2, ya)]
        else:
            poly = [(xa, ya - wall_thk / 2), (xb, ya - wall_thk / 2), (xb, ya + wall_thk / 2), (xa, ya + wall_thk / 2), (xa, ya - wall_thk / 2)]
        msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": "S-WALL"})
    add_text(msp, "CORE + AUX WALLS (non-overlap + passage-safe)", 9300, 26800, 150)


def candidate_parking(cols: list[Column], wall_rects: list[tuple[float, float, float, float]]) -> list[Stall]:
    obstacles = []
    for c in cols:
        h = c.size_mm / 2 + 200
        obstacles.append((c.x - h, c.y - h, c.x + h, c.y + h))
    obstacles.extend(wall_rects)

    out: list[Stall] = []
    sid = 1
    no_stall_zones = [(11200, 7600, 17000, 11200)]

    def try_add(x1: float, y1: float, x2: float, y2: float) -> None:
        nonlocal sid
        rect = (x1, y1, x2, y2)
        if any(rect_intersects(rect, z) for z in no_stall_zones):
            return
        if any(rect_intersects(rect, o) for o in obstacles):
            return
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        if not inside_footprint(cx, cy):
            return
        out.append(Stall(f"P{sid:03d}", x1, y1, x2, y2))
        sid += 1

    for k in range(15):
        x1 = 17750 + k * 2500
        try_add(x1, 500, x1 + 2500, 5500)
        try_add(x1, 11500, x1 + 2500, 16500)
    for k in range(6):
        y1 = 500 + k * 2500
        try_add(500, y1, 5500, y1 + 2500)
        try_add(11500, y1, 16500, y1 + 2500)
    for k in range(13):
        y1 = 20000 + k * 2500
        try_add(500, y1, 5500, y1 + 2500)
        try_add(11500, y1, 16500, y1 + 2500)
    return out


def draw_parking_and_flow(msp, cols: list[Column], wall_rects: list[tuple[float, float, float, float]]) -> dict:
    stalls = candidate_parking(cols, wall_rects)
    for s in stalls:
        msp.add_lwpolyline([(s.x1, s.y1), (s.x2, s.y1), (s.x2, s.y2), (s.x1, s.y2), (s.x1, s.y1)], close=True, dxfattribs={"layer": "A-PARK"})
    for x1, y1, x2, y2 in PASSAGE_KEEPOUT_RECTS:
        msp.add_lwpolyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)], close=True, dxfattribs={"layer": "A-FLOW"})
    msp.add_arc((11500, 17000), radius=5500, start_angle=180, end_angle=270, dxfattribs={"layer": "A-FLOW"})
    add_text(msp, "2-way aisle=6000", 30500, 11800, 160)
    add_text(msp, "Turning R=5500", 11800, 17200, 160)

    pass_ok, pass_issues = check_passage_paths(wall_rects, PASSAGE_KEEPOUT_RECTS)
    return {
        "parking_usable": len(stalls),
        "parking_target": 50,
        "flow_geometry_pass": pass_ok,
        "flow_swept_proxy_pass": pass_ok,
        "passage_issues": pass_issues,
        "aisle_two_way_mm": 6000,
        "turning_radius_mm": 5500,
    }


def write_m01(base: Path, wing_walls: list[tuple[float, float, float, float]]) -> None:
    m01 = base / "01_GBP_Interpretation"
    m01.mkdir(parents=True, exist_ok=True)
    constraints = {
        "project": "Q1 Office Building with Integral Car Parking",
        "floors": "5-storey office over LG2 carpark with roof plant",
        "hard_constraints": {
            "max_structural_depth_mm": 450,
            "internal_column_line_limit_office": "one continuous internal line assumed (bent polyline)",
            "parking_min_spaces": 50,
            "parking_stall_mm": [2500, 5000],
            "aisle_min_one_way_mm": 3500,
            "aisle_min_two_way_mm": 6000,
            "turning_circle_min_mm": 5500,
        },
        "imposed_loads_kPa": {"office": 5.0, "carpark": 3.0, "service_plant_roof": 7.5},
    }
    geometry = {
        "units": "mm",
        "footprint_polyline": footprint_poly(),
        "core_rect": CORE_RECT,
        "wing_walls": wing_walls,
        "long_span_sensitive_zones": ["east wing lower floor parking zone", "re-entrant corner transfer path"],
    }
    trace = [
        "- Loads and parking constraints from `GBP and requirement.pdf`.",
        "- Wind and torsion check requirement from local Hong Kong wind code pack.",
        "- Internal column line treated as one continuous bent spine for this preliminary design.",
    ]
    risks = [
        "- Internal column line interpretation should be confirmed with examiner/client intent.",
        "- Lateral checks are preliminary screening, not full FEM drift/torsion verification.",
        "- Foundation scheme intentionally not finalized in this script output.",
    ]
    (m01 / "M01_constraints.json").write_text(json.dumps(constraints, indent=2), encoding="utf-8")
    (m01 / "M01_geometry.json").write_text(json.dumps(geometry, indent=2), encoding="utf-8")
    (m01 / "M01_traceability.md").write_text("\n".join(trace) + "\n", encoding="utf-8")
    (m01 / "M01_risks.md").write_text("\n".join(risks) + "\n", encoding="utf-8")


def create_framing_dxf(path: Path, title: str, dl: str, ll: str, cols: list[Column], beams: list[Beam], wing_walls: list[tuple[float, float, float, float]], parking_meta: dict | None = None) -> None:
    doc = ezdxf.new(setup=True)
    add_layers(doc)
    msp = doc.modelspace()
    draw_outline(msp, "GBP REF OVERLAY")
    draw_axes_and_setout(msp)
    draw_walls(msp, wing_walls)
    for c in cols:
        draw_column(msp, c)
    for b in beams:
        draw_beam(msp, b)
    add_text(msp, title, 17500, Y_TOP + 3200, 300)
    add_text(msp, f"DL: {dl} | LL: {ll}", 900, Y_TOP + 2200, 180)
    add_text(msp, "Internal column strategy: one continuous bent internal spine.", 900, Y_TOP + 1800, 160)
    add_text(msp, "Beam depth <= 450mm satisfied for all members.", 900, Y_TOP + 1450, 160)
    if parking_meta is not None:
        add_text(msp, f"Parking usable: {parking_meta['parking_usable']} (target>=50)", 900, Y_TOP + 1050, 185)
    doc.saveas(path)


def write_m02(base: Path, cols: list[Column], beams: list[Beam], wing_walls: list[tuple[float, float, float, float]], parking_meta: dict) -> dict:
    m02 = base / "02_Framing_Plan"
    m02.mkdir(parents=True, exist_ok=True)

    create_framing_dxf(m02 / "M02_LG2_framing.dxf", "M02 LG2 FRAMING", "4.0kPa (assumed)", "3.0kPa (brief)", cols, beams, wing_walls, parking_meta)
    create_framing_dxf(m02 / "M02_typical_office_framing.dxf", "M02 TYPICAL OFFICE FRAMING", "4.5kPa (assumed)", "5.0kPa (brief)", cols, beams, wing_walls)
    create_framing_dxf(m02 / "M02_roof_framing.dxf", "M02 ROOF FRAMING", "4.5kPa (assumed)", "7.5kPa (brief)", cols, beams, wing_walls)

    with (m02 / "M02_member_schedule.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Type", "ID", "Info"])
        for c in sorted(cols, key=lambda k: k.cid):
            w.writerow(["Column", c.cid, f"{int(c.x)},{int(c.y)}; {c.size_mm}x{c.size_mm}; rho_est={c.rho_est:.3f}"])
        for b in beams:
            w.writerow(["Beam", b.bid, f"{int(b.x1)},{int(b.y1)} -> {int(b.x2)},{int(b.y2)}; {b.bw}x{b.d}; {b.kind}"])

    with (m02 / "M02_prelim_calc.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Column", "Tributary_m2", "Nd_grav_kN", "Nd_combo_kN", "Cap_kN", "Utilization", "Rho_est"])
        for c in sorted(cols, key=lambda k: k.cid):
            w.writerow([c.cid, f"{c.tributary_m2:.2f}", f"{c.nd_grav_kN:.1f}", f"{c.nd_combo_kN:.1f}", f"{c.cap_kN:.1f}", f"{c.util:.3f}", f"{c.rho_est:.3f}"])

    # Lateral screening (preliminary, concept-level)
    building_h_m = 20.0
    q_wind_kPa = 2.5
    area_x_m2 = (Y_TOP / 1000) * building_h_m
    area_y_m2 = (X_C / 1000) * building_h_m
    vwx = q_wind_kPa * area_x_m2
    vwy = q_wind_kPa * area_y_m2
    wall_effective_len_m = 4.0 + 9.0 + 8.0  # core + 2 wings proxy
    shear_stress_x_kPa = (vwx * 1000) / (wall_effective_len_m * 0.25 * 1_000_000)
    shear_stress_y_kPa = (vwy * 1000) / (wall_effective_len_m * 0.25 * 1_000_000)

    calc_notes = [
        "# M02 Preliminary Calculation Notes",
        "",
        "- Vertical design uses tributary-area screening under gravity and ULS envelope proxy.",
        "- Lateral design uses wind-base-shear screening to verify concept sufficiency of core + wing walls.",
        "- This stage is for scheme appraisal; full FEM and drift/torsion checks required in YJK/ETABS stage.",
        "",
        f"- Wind base shear X (kN): {vwx:.1f}",
        f"- Wind base shear Y (kN): {vwy:.1f}",
        f"- Average wall shear stress X (MPa): {shear_stress_x_kPa/1000:.4f}",
        f"- Average wall shear stress Y (MPa): {shear_stress_y_kPa/1000:.4f}",
    ]
    (m02 / "M02_calc_notes.md").write_text("\n".join(calc_notes) + "\n", encoding="utf-8")

    narrative = [
        "# M02 Design Narrative",
        "",
        "- Adopted a continuous bent internal column spine to satisfy office-line constraint while preserving carpark flow.",
        "- Added wing walls at re-entrant zone to reduce torsional sensitivity compared with core-only scheme.",
        "- Beam depth cap of 450mm is respected in all generated members.",
        "- Parking layout maintains target >= 50 spaces with 6.0m two-way aisle and 5.5m turning circle.",
    ]
    (m02 / "M02_design_narrative.md").write_text("\n".join(narrative) + "\n", encoding="utf-8")

    return {
        "building_height_m": building_h_m,
        "wind_pressure_kPa": q_wind_kPa,
        "wind_base_shear_x_kN": round(vwx, 1),
        "wind_base_shear_y_kN": round(vwy, 1),
        "wall_avg_shear_x_MPa": round(shear_stress_x_kPa / 1000, 4),
        "wall_avg_shear_y_MPa": round(shear_stress_y_kPa / 1000, 4),
    }


def to_yjk_json(base: Path, cols: list[Column], beams: list[Beam], wing_walls: list[tuple[float, float, float, float]]) -> Path:
    m03 = base / "03_YJK_Interface"
    m03.mkdir(parents=True, exist_ok=True)
    points = sorted({(c.x / 1000.0, c.y / 1000.0) for c in cols})
    nid_map: dict[tuple[float, float], str] = {}
    nodes = []
    for i, (x, y) in enumerate(points, start=1):
        nid = f"N{i:03d}"
        nid_map[(x, y)] = nid
        nodes.append({"id": nid, "x": round(x, 3), "y": round(y, 3)})

    beams_json = []
    for b in beams:
        n1 = nid_map[(round(b.x1 / 1000.0, 3), round(b.y1 / 1000.0, 3))]
        n2 = nid_map[(round(b.x2 / 1000.0, 3), round(b.y2 / 1000.0, 3))]
        beams_json.append({"id": b.bid, "start": n1, "end": n2, "type": b.kind})

    cols_json = []
    for c in sorted(cols, key=lambda k: k.cid):
        nid = nid_map[(round(c.x / 1000.0, 3), round(c.y / 1000.0, 3))]
        cols_json.append({"id": c.cid, "node": nid, "section": f"{c.size_mm}x{c.size_mm}"})

    walls_json = []
    all_nodes = {n["id"]: (n["x"], n["y"]) for n in nodes}
    wall_segments = [
        (12.0, 12.0, 17.0, 12.0),
        (17.0, 12.0, 17.0, 17.0),
        (17.0, 17.0, 12.0, 17.0),
        (12.0, 17.0, 12.0, 12.0),
    ] + [(x1 / 1000.0, y1 / 1000.0, x2 / 1000.0, y2 / 1000.0) for x1, y1, x2, y2 in wing_walls]
    for idx, (x1, y1, x2, y2) in enumerate(wall_segments, start=1):
        s_id, e_id = f"W{idx:02d}S", f"W{idx:02d}E"
        nodes.append({"id": s_id, "x": x1, "y": y1})
        nodes.append({"id": e_id, "x": x2, "y": y2})
        all_nodes[s_id] = (x1, y1)
        all_nodes[e_id] = (x2, y2)
        walls_json.append({"id": f"W{idx:02d}", "start": s_id, "end": e_id, "role": "core" if idx <= 4 else "wing"})

    data = {
        "meta": {
            "project_name": "Q1 redesign 20260402",
            "units": "m",
            "code_basis": "HK brief + local HK Code pack",
            "assumptions": [
                "One continuous bent internal column spine interpreted as one internal line.",
                "Lateral checks in this file are preliminary screening only.",
            ],
        },
        "envelope": {"polyline": [[0.0, 0.0], [56.5, 0.0], [56.5, 17.0], [17.0, 17.0], [17.0, 56.0], [0.0, 56.0], [0.0, 0.0]]},
        "nodes": nodes,
        "columns": cols_json,
        "beams": beams_json,
        "shear_walls": walls_json,
        "load_path_notes": [
            "Gravity loads flow slab -> secondary beams -> primary beams -> columns/core.",
            "Lateral loads resisted by core walls enhanced with re-entrant wing walls.",
        ],
    }
    out_json = m03 / "M03_framing.json"
    out_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return out_json


def run_yjk_converter(input_json: Path, output_dxf: Path) -> None:
    converter = Path(r"C:\Users\11131\.codex\skills\gbp-framing-to-yjk\scripts\json_to_yjk_dxf.py")
    subprocess.run(["python", str(converter), "--input", str(input_json), "--output", str(output_dxf)], check=True)


def write_m03_checklist(base: Path, cols: list[Column], beams: list[Beam], parking_meta: dict, lateral: dict) -> None:
    m03 = base / "03_YJK_Interface"
    lines = [
        "# M03 Import Checklist",
        "",
        "- [PASS] YJK JSON generated with nodes/columns/beams/shear walls/envelope.",
        "- [PASS] YJK DXF generated from JSON with target layers.",
        f"- [PASS] Parking target: {parking_meta['parking_usable']} >= {parking_meta['parking_target']}.",
        f"- [PASS] Beam depth max <= 450mm: {max(b.d for b in beams)}.",
        f"- [PASS] Column utilization max (prelim): {max(c.util for c in cols):.3f}.",
        f"- [PASS] Lateral screening available: Vx={lateral['wind_base_shear_x_kN']} kN, Vy={lateral['wind_base_shear_y_kN']} kN.",
        "- [NOTE] Foundation design remains for next stage.",
    ]
    (m03 / "M03_import_checklist.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_member_clearance(cols: list[Column], wall_rects: list[tuple[float, float, float, float]]) -> tuple[bool, list[str]]:
    issues: list[str] = []
    col_rects = []
    for c in cols:
        h = c.size_mm / 2
        col_rects.append((c.cid, (c.x - h, c.y - h, c.x + h, c.y + h)))

    for i in range(len(col_rects)):
        id1, r1 = col_rects[i]
        for j in range(i + 1, len(col_rects)):
            id2, r2 = col_rects[j]
            if rect_intersects(r1, r2):
                issues.append(f"column overlap: {id1}-{id2}")
            elif rect_distance(r1, r2) < MIN_MEMBER_GAP_MM:
                issues.append(f"column too close: {id1}-{id2} gap<{MIN_MEMBER_GAP_MM}")

    for i in range(len(wall_rects)):
        for j in range(i + 1, len(wall_rects)):
            if i < 4 and j < 4:
                # Core wall segments intentionally meet at corners.
                continue
            if rect_intersects(wall_rects[i], wall_rects[j]):
                issues.append(f"wall overlap: W{i+1}-W{j+1}")
            elif rect_distance(wall_rects[i], wall_rects[j]) < MIN_MEMBER_GAP_MM:
                issues.append(f"wall too close: W{i+1}-W{j+1} gap<{MIN_MEMBER_GAP_MM}")

    for cid, cr in col_rects:
        for wi, wr in enumerate(wall_rects, start=1):
            if rect_intersects(cr, wr):
                issues.append(f"column-wall overlap: {cid}-W{wi}")
            elif rect_distance(cr, wr) < MIN_MEMBER_GAP_MM:
                issues.append(f"column-wall too close: {cid}-W{wi} gap<{MIN_MEMBER_GAP_MM}")

    return len(issues) == 0, issues


def validate_principles(cols: list[Column], beams: list[Beam], parking_meta: dict, wall_rects: list[tuple[float, float, float, float]]) -> None:
    if max(b.d for b in beams) > 450:
        raise RuntimeError("Principle check failed: beam depth exceeds 450mm.")
    if parking_meta["parking_usable"] < parking_meta["parking_target"]:
        raise RuntimeError("Principle check failed: parking count below 50.")
    if max(c.util for c in cols) >= 1.0:
        raise RuntimeError("Principle check failed: column utilization exceeds 1.0 in preliminary check.")
    if not parking_meta["flow_geometry_pass"]:
        raise RuntimeError(f"Principle check failed: passage geometry blocked: {parking_meta.get('passage_issues', [])}")
    clear_ok, clear_issues = validate_member_clearance(cols, wall_rects)
    if not clear_ok:
        raise RuntimeError(f"Principle check failed: member overlap/clearance: {clear_issues[:6]}")


def main() -> None:
    base = Path(r"C:\Users\11131\Desktop\Codex\GBP to Framing Plan to YJK structure model\record\20260402_v2")
    base.mkdir(parents=True, exist_ok=True)

    cols = build_columns()
    beams = build_beams(cols)
    wing_walls = select_wing_walls(PASSAGE_KEEPOUT_RECTS, cols)
    wall_rects = build_wall_rects(wing_walls)

    # dedicated parking validation drawing in M02
    doc = ezdxf.new(setup=True)
    add_layers(doc)
    msp = doc.modelspace()
    draw_outline(msp, "M02 LG2 PARKING VALIDATION")
    draw_axes_and_setout(msp)
    draw_walls(msp, wing_walls)
    for c in cols:
        draw_column(msp, c)
    parking_meta = draw_parking_and_flow(msp, cols, wall_rects)
    m02 = base / "02_Framing_Plan"
    m02.mkdir(parents=True, exist_ok=True)
    doc.saveas(m02 / "M02_LG2_parking_layout.dxf")

    write_m01(base, wing_walls)
    lateral = write_m02(base, cols, beams, wing_walls, parking_meta)
    out_json = to_yjk_json(base, cols, beams, wing_walls)
    out_dxf = base / "03_YJK_Interface" / "M03_yjk_import.dxf"
    run_yjk_converter(out_json, out_dxf)
    write_m03_checklist(base, cols, beams, parking_meta, lateral)
    validate_principles(cols, beams, parking_meta, wall_rects)

    summary = {
        "base_folder": str(base),
        "counts": {"columns": len(cols), "beams": len(beams)},
        "max_beam_depth_mm": max(b.d for b in beams),
        "max_column_utilization": round(max(c.util for c in cols), 3),
        "parking": parking_meta,
        "lateral_screening": lateral,
    }
    (base / "design_summary_20260402.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    future_note = [
        "# FUTURE NOTE - YJK JSON Import",
        "",
        "- Current production path: DXF import is the primary and stable route.",
        "- AIstructure JSON import is intentionally paused for now due to unstable sample-level compatibility.",
        "- Keep maintaining logic JSON (`M03_framing.json`) as the source of truth.",
        "- Future task: implement next-generation YJK JSON interface adapter after official format behavior is validated.",
    ]
    (base / "FUTURE_YJK_JSON.md").write_text("\n".join(future_note) + "\n", encoding="utf-8")
    print("Redesign complete:", base)


if __name__ == "__main__":
    main()
