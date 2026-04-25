#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path


DEFAULT_REVIT_ROOT = Path(r"C:\Program Files\Autodesk\Revit 2023")
MACHINE_ADDINS = Path(r"C:\ProgramData\Autodesk\Revit\Addins\2023")
USER_ADDINS = Path(os.environ.get("APPDATA", "")) / "Autodesk" / "Revit" / "Addins" / "2023"
CSC_64 = Path(r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe")


def file_status(path: Path) -> str:
    return "found" if path.exists() else "missing"


def assembly_name(path: Path) -> str:
    if not path.exists():
        return "missing"
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"[System.Reflection.AssemblyName]::GetAssemblyName('{path}').FullName",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=20)
    except Exception as exc:
        return f"unreadable: {exc}"
    output = (result.stdout or result.stderr).strip()
    return output if output else f"unreadable: exit {result.returncode}"


def pythonnet_status() -> str:
    try:
        import clr  # type: ignore  # noqa: F401
    except Exception as exc:
        return f"not available ({type(exc).__name__}: {exc})"
    return "available"


def dotnet_status() -> str:
    dotnet = shutil.which("dotnet")
    if not dotnet:
        return "missing"
    try:
        result = subprocess.run([dotnet, "--version"], capture_output=True, text=True, check=False, timeout=20)
    except Exception as exc:
        return f"found but not executable: {exc}"
    version = (result.stdout or result.stderr).strip()
    return f"{dotnet} ({version})"


def csc_status() -> str:
    return f"{CSC_64} (found)" if CSC_64.exists() else f"{CSC_64} (missing)"


def build_report(revit_root: Path) -> str:
    revit_exe = revit_root / "Revit.exe"
    revit_core_console = revit_root / "RevitCoreConsole.exe"
    revit_api = revit_root / "RevitAPI.dll"
    revit_api_ui = revit_root / "RevitAPIUI.dll"

    api_present = revit_api.exists() and revit_api_ui.exists()
    addin_ready = MACHINE_ADDINS.exists() or USER_ADDINS.exists()
    in_process_ready = revit_core_console.exists()
    csc_present = CSC_64.exists()
    status = "api-assemblies-present" if api_present else "blocked"
    if api_present and addin_ready:
        status = "add-in-ready"
    if api_present and addin_ready and csc_present:
        status = "add-in-compile-ready"
    if api_present and in_process_ready:
        status = "in-process-test-ready"
    if api_present and not in_process_ready:
        execution_note = "Revit API assemblies are present, but no RevitCoreConsole.exe was found by this probe. Use an installed Revit add-in, macro, Dynamo, pyRevit-style bridge, or manual Revit launch for in-process tests."
    else:
        execution_note = "RevitCoreConsole.exe was found; in-process console testing may be possible."

    lines = ["# Revit 2023 API Probe", ""]
    lines.append(f"- status: **{status}**")
    lines.append(f"- revit root: `{revit_root}` ({file_status(revit_root)})")
    lines.append(f"- revit exe: `{revit_exe}` ({file_status(revit_exe)})")
    lines.append(f"- revit core console: `{revit_core_console}` ({file_status(revit_core_console)})")
    lines.append(f"- revit api: `{revit_api}` ({file_status(revit_api)})")
    lines.append(f"- revit api ui: `{revit_api_ui}` ({file_status(revit_api_ui)})")
    lines.append(f"- machine add-ins: `{MACHINE_ADDINS}` ({file_status(MACHINE_ADDINS)})")
    lines.append(f"- user add-ins: `{USER_ADDINS}` ({file_status(USER_ADDINS)})")
    lines.append(f"- pythonnet clr: {pythonnet_status()}")
    lines.append(f"- dotnet: {dotnet_status()}")
    lines.append(f"- .NET Framework csc: {csc_status()}")
    lines.append("")
    lines.append("## Assembly Names")
    lines.append(f"- RevitAPI.dll: `{assembly_name(revit_api)}`")
    lines.append(f"- RevitAPIUI.dll: `{assembly_name(revit_api_ui)}`")
    lines.append("")
    lines.append("## Execution Boundary")
    lines.append(f"- {execution_note}")
    lines.append("- Standalone Python can prepare JSON/DXF/add-in input files, but direct Revit element creation requires code running inside Revit.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe local Revit 2023 API readiness for GBP Structural Pipeline development.")
    parser.add_argument("--revit-root", default=str(DEFAULT_REVIT_ROOT), help="Path to the Revit 2023 installation folder.")
    parser.add_argument("--report", help="Optional markdown report output path.")
    args = parser.parse_args()

    report = build_report(Path(args.revit_root))
    if args.report:
        report_path = Path(args.report).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
