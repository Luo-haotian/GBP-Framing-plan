#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_ids(model: dict) -> tuple[set[str], list[str]]:
    issues: list[str] = []
    seen: set[str] = set()

    def add(items: list[dict], label: str) -> None:
        for item in items:
            item_id = item.get("id", "")
            if not item_id:
                issues.append(f"{label}: missing id")
                continue
            if item_id in seen:
                issues.append(f"duplicate id: {item_id}")
            seen.add(item_id)

    intent = model["intent_model"]
    seed = model["analysis_seed_model"]

    for key in ("grids", "levels", "columns", "beams", "walls", "slabs", "openings", "uncertainty"):
        add(intent.get(key, []), key)
    for key in ("boundaries", "keepouts", "core_zones"):
        add(intent.get(key, []), key)
    for key in ("materials", "sections", "loads", "load_combinations", "boundary_conditions", "analysis_options"):
        add(seed.get(key, []), key)

    return seen, issues


def validate_model(model: dict) -> list[str]:
    issues: list[str] = []
    required_root = [
        "metadata",
        "source_of_truth",
        "coordinate_system",
        "intent_model",
        "analysis_seed_model",
        "precheck",
    ]
    for key in required_root:
        if key not in model:
            issues.append(f"missing root field: {key}")

    if issues:
        return issues

    metadata = model["metadata"]
    for key in ("version", "source", "confidence", "units"):
        if key not in metadata:
            issues.append(f"metadata missing field: {key}")

    coord = model["coordinate_system"]
    for key in ("type", "origin", "rotation_degrees", "length_unit", "elevation_unit"):
        if key not in coord:
            issues.append(f"coordinate_system missing field: {key}")

    entity_ids, id_issues = collect_ids(model)
    issues.extend(id_issues)

    intent = model["intent_model"]
    seed = model["analysis_seed_model"]
    levels = {x["id"] for x in intent.get("levels", [])}
    sections = {x["id"] for x in seed.get("sections", [])}
    materials = {x["id"] for x in seed.get("materials", [])}
    loads = {x["id"] for x in seed.get("loads", [])}

    for section in seed.get("sections", []):
        material_id = section.get("material_id")
        if material_id and material_id not in materials:
            issues.append(f"section references missing material: {section['id']} -> {material_id}")

    for col in intent.get("columns", []):
        if col["base_level_id"] not in levels or col["top_level_id"] not in levels:
            issues.append(f"column level reference error: {col['id']}")
        if col.get("section_seed_id") and col["section_seed_id"] not in sections:
            issues.append(f"column section reference error: {col['id']} -> {col['section_seed_id']}")

    for beam in intent.get("beams", []):
        if beam["level_id"] not in levels:
            issues.append(f"beam level reference error: {beam['id']}")
        if beam.get("section_seed_id") and beam["section_seed_id"] not in sections:
            issues.append(f"beam section reference error: {beam['id']} -> {beam['section_seed_id']}")

    for wall in intent.get("walls", []):
        if wall["base_level_id"] not in levels or wall["top_level_id"] not in levels:
            issues.append(f"wall level reference error: {wall['id']}")

    for slab in intent.get("slabs", []):
        if slab["level_id"] not in levels:
            issues.append(f"slab level reference error: {slab['id']}")
        if slab.get("section_seed_id") and slab["section_seed_id"] not in sections:
            issues.append(f"slab section reference error: {slab['id']} -> {slab['section_seed_id']}")

    for opening in intent.get("openings", []):
        if opening["level_id"] not in levels:
            issues.append(f"opening level reference error: {opening['id']}")

    for item in intent.get("uncertainty", []):
        entity_id = item.get("entity_id", "")
        if entity_id and entity_id not in entity_ids:
            issues.append(f"uncertainty references missing entity: {item['id']} -> {entity_id}")

    for load in seed.get("loads", []):
        for target in load.get("target_ids", []):
            if target not in entity_ids:
                issues.append(f"load target reference error: {load['id']} -> {target}")

    for combo in seed.get("load_combinations", []):
        for factor in combo.get("factors", []):
            load_id = factor.get("load_id", "")
            if load_id not in loads:
                issues.append(f"load combination reference error: {combo['id']} -> {load_id}")

    for bc in seed.get("boundary_conditions", []):
        target_id = bc.get("target_id", "")
        if target_id not in entity_ids:
            issues.append(f"boundary condition reference error: {bc['id']} -> {target_id}")

    precheck = model["precheck"]
    if precheck.get("status") not in {"pending", "passed", "warning", "failed"}:
        issues.append("precheck has invalid status")
    if "issues" not in precheck or not isinstance(precheck["issues"], list):
        issues.append("precheck issues field must be a list")

    return issues


def build_report(model_path: Path, issues: list[str]) -> str:
    status = "pass" if not issues else "warning"
    lines = ["# Neutral Model Validation Report", ""]
    lines.append(f"- source: `{model_path}`")
    lines.append(f"- status: **{status}**")
    lines.append(f"- issue count: {len(issues)}")
    lines.append("")
    lines.append("## Issues")
    if issues:
      for issue in issues:
          lines.append(f"- {issue}")
    else:
      lines.append("- none detected in deterministic consistency checks")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate GBP Framing V2 neutral structural model references and shape.")
    parser.add_argument("input_json", help="Path to neutral structural model JSON.")
    parser.add_argument("--report", help="Optional markdown report output path.")
    args = parser.parse_args()

    model_path = Path(args.input_json).resolve()
    model = load_json(model_path)
    issues = validate_model(model)
    report = build_report(model_path, issues)

    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")

    print(f"validation_status={'pass' if not issues else 'warning'}")
    print(f"issue_count={len(issues)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
