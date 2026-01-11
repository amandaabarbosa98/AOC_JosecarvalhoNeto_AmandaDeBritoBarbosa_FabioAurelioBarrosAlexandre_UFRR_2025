#!/usr/bin/env python3
"""
Objective 5 (advanced): Front-end unifier producing a COMMON AST.

Usage:
  python3 task04/unify_ast.py --vhdl path/to/design.vhd --out out.ast.json
  python3 task04/unify_ast.py --yosys-json path/to/design.json --out out.ast.json
  python3 task04/unify_ast.py --vhdl design.vhd --yosys-json design.json --out out.ast.json

Merging rules:
- structural view (cells/wires/port widths) prefers Yosys JSON when available
- property tags (assume/assert) come from VHDL
- notes/stats are merged
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path

from ast_frontend.vhdl_light_parser import parse_vhdl_to_ast
from ast_frontend.yosys_json_adapter import yosys_json_to_ast
from ast_frontend.common_ast import new_module_ast

def merge_ast(vhdl_ast, yosys_ast):
    out = new_module_ast(yosys_ast.design_name or vhdl_ast.design_name)

    out.source_vhdl = vhdl_ast.source_vhdl or ""
    out.source_verilog = yosys_ast.source_verilog or ""

    # Ports: prefer Yosys direction/width when present, else VHDL
    ports_by_name = {}
    for p in vhdl_ast.ports:
        ports_by_name[p.name] = p
    for p in yosys_ast.ports:
        ports_by_name[p.name] = p

    out.ports = list(ports_by_name.values())

    # Structural: from yosys
    out.wires = yosys_ast.wires or []
    out.cells = yosys_ast.cells or []

    # Properties: from vhdl
    out.properties = vhdl_ast.properties or []

    # Stats/notes
    out.stats = {}
    out.stats.update(vhdl_ast.stats or {})
    out.stats.update(yosys_ast.stats or {})
    out.notes = (vhdl_ast.notes or []) + (yosys_ast.notes or [])
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vhdl", type=str, default=None)
    ap.add_argument("--yosys-json", type=str, default=None)
    ap.add_argument("--out", type=str, required=True)
    ap.add_argument("--design-name", type=str, default=None)
    args = ap.parse_args()

    vhdl_ast = None
    yosys_ast = None

    if args.vhdl:
        vhdl_ast = parse_vhdl_to_ast(Path(args.vhdl))
    if args.yosys_json:
        yosys_ast = yosys_json_to_ast(Path(args.yosys_json), design_name=args.design_name)

    if vhdl_ast and yosys_ast:
        out_ast = merge_ast(vhdl_ast, yosys_ast)
    elif vhdl_ast:
        out_ast = vhdl_ast
    elif yosys_ast:
        out_ast = yosys_ast
    else:
        raise SystemExit("Provide --vhdl and/or --yosys-json")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out_ast.to_dict(), indent=2), encoding="utf-8")
    print(f"Wrote common AST to: {args.out}")

if __name__ == "__main__":
    main()
