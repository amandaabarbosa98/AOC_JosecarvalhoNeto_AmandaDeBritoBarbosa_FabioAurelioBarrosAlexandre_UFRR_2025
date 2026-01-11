"""
Yosys JSON adapter -> Common AST.

Input: Yosys write_json output.
We extract:
- module ports (direction, width via bits list length)
- wires (name, width)
- cells (type, connections)
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

from .common_ast import new_module_ast, Port, Wire, Cell

def yosys_json_to_ast(yosys_json_path: Path, design_name: str | None = None):
    data = json.loads(yosys_json_path.read_text(encoding="utf-8", errors="replace"))
    modules = data.get("modules", {})
    if not modules:
        ast = new_module_ast(design_name or yosys_json_path.stem)
        ast.notes.append("No modules found in yosys json.")
        return ast

    # pick first module if top not provided
    top_name = design_name if design_name in modules else next(iter(modules.keys()))
    mod = modules[top_name]
    ast = new_module_ast(top_name)
    ast.stats["yosys_top"] = top_name
    ast.source_verilog = str(yosys_json_path)

    # Ports
    for pname, pinfo in (mod.get("ports") or {}).items():
        direction = pinfo.get("direction", "in")
        bits = pinfo.get("bits", [])
        width = len(bits) if isinstance(bits, list) else 1
        ast.ports.append(Port(name=pname, direction=direction, width=max(1, width)))

    # Wires
    for wname, winfo in (mod.get("netnames") or {}).items():
        bits = winfo.get("bits", [])
        width = len(bits) if isinstance(bits, list) else 1
        ast.wires.append(Wire(name=wname, width=max(1, width)))

    # Cells
    cells = mod.get("cells") or {}
    for cname, cinfo in cells.items():
        ctype = cinfo.get("type", "")
        conn = cinfo.get("connections", {})
        ast.cells.append(Cell(name=cname, type=ctype, connections=conn))

    ast.stats["cell_count"] = len(ast.cells)
    ast.stats["wire_count"] = len(ast.wires)
    return ast
