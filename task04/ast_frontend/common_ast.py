"""
Common AST schema for TASK 04 (Objective 5) - AOC.
Version: aoc-task04-common-ast-v1

This is intentionally lightweight: it is a unifying IR that can be built from:
  (a) VHDL (entity/ports + property tags)
  (b) Yosys JSON netlist (cells/wires/ports)
and merged into a single representation.

The goal is to keep a stable schema that supports:
  - IO discovery (for auxiliary spec + harness generation)
  - Property discovery (assume/assert tags)
  - Structural stats (cell counts) when Yosys is available
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Literal, Optional

Direction = Literal["in", "out", "inout"]
PropKind = Literal["assume", "assert"]

@dataclass
class Port:
    name: str
    direction: Direction
    vhdl_type: str = ""
    width: int = 1

@dataclass
class Property:
    kind: PropKind
    expr: str
    msg: str = ""
    source_line: Optional[int] = None

@dataclass
class Cell:
    name: str
    type: str
    connections: Dict[str, Any]  # keep generic

@dataclass
class Wire:
    name: str
    width: int = 1

@dataclass
class ModuleAST:
    schema: str
    design_name: str
    source_vhdl: str = ""
    source_verilog: str = ""
    ports: List[Port] = None
    properties: List[Property] = None
    wires: List[Wire] = None
    cells: List[Cell] = None
    stats: Dict[str, Any] = None
    notes: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # dataclasses default None lists – normalize
        for k in ["ports", "properties", "wires", "cells", "notes"]:
            if d.get(k) is None:
                d[k] = []
        if d.get("stats") is None:
            d["stats"] = {}
        return d

def new_module_ast(design_name: str) -> ModuleAST:
    return ModuleAST(
        schema="aoc-task04-common-ast-v1",
        design_name=design_name,
        ports=[],
        properties=[],
        wires=[],
        cells=[],
        stats={},
        notes=[],
    )
