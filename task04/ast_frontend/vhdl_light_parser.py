"""
Lightweight VHDL parser for TASK 04 Objective 5.

This is NOT a full VHDL parser. It intentionally focuses on:
- entity name
- port declarations (name : in/out type)
- detection of clocked processes (rising_edge/falling_edge or sensitivity list 'clk')
- property tags in comments:
    -- @c2vhdl:ASSUME <expr>;
    -- @c2vhdl:ASSERT <expr>;
"""

from __future__ import annotations
import re
from pathlib import Path
from typing import Tuple, List, Dict, Any

from .common_ast import new_module_ast, Port, Property

ENTITY_RE = re.compile(r'\bentity\s+(\w+)\s+is\b', re.IGNORECASE)
PORT_BLOCK_RE = re.compile(r'\bport\s*\((.*?)\)\s*;', re.IGNORECASE | re.DOTALL)
PORT_LINE_RE = re.compile(r'^\s*(\w+)\s*:\s*(in|out|inout)\s+([^;]+);', re.IGNORECASE | re.MULTILINE)

TAG_RE = re.compile(r'--\s*@c2vhdl:(ASSUME|ASSERT)\s*(.*?);?\s*$', re.IGNORECASE)

def _width_from_vhdl_type(vhdl_type: str) -> int:
    t = vhdl_type.lower()
    # std_logic_vector(7 downto 0) / (0 to 7)
    m = re.search(r'\((\s*\d+)\s*(downto|to)\s*(\d+)\s*\)', t)
    if m:
        a = int(m.group(1)); b = int(m.group(3))
        return abs(a - b) + 1
    if "std_logic_vector" in t:
        # unknown range
        return 1
    if "integer" in t:
        # if range present, estimate bits (conservative)
        rm = re.search(r'range\s+(\d+)\s+to\s+(\d+)', t)
        if rm:
            end = int(rm.group(2))
            bits = 1
            while (2**bits) <= end:
                bits += 1
            return max(1, bits)
        return 32
    return 1

def parse_vhdl_to_ast(vhdl_path: Path):
    txt = vhdl_path.read_text(encoding="utf-8", errors="replace")
    ent = ENTITY_RE.search(txt)
    design = ent.group(1) if ent else vhdl_path.stem

    ast = new_module_ast(design)
    ast.source_vhdl = str(vhdl_path)

    # Ports
    port_block = PORT_BLOCK_RE.search(txt)
    if port_block:
        block = port_block.group(1)
        for m in PORT_LINE_RE.finditer(block):
            name, direction, vtype = m.group(1), m.group(2).lower(), m.group(3).strip()
            width = _width_from_vhdl_type(vtype)
            ast.ports.append(Port(name=name, direction=direction, vhdl_type=vtype, width=width))
    else:
        # fallback: scan entire file
        for m in PORT_LINE_RE.finditer(txt):
            name, direction, vtype = m.group(1), m.group(2).lower(), m.group(3).strip()
            width = _width_from_vhdl_type(vtype)
            ast.ports.append(Port(name=name, direction=direction, vhdl_type=vtype, width=width))

    # Properties (tags)
    for i, line in enumerate(txt.splitlines(), start=1):
        tm = TAG_RE.search(line)
        if not tm:
            continue
        kind = tm.group(1).lower()
        expr = tm.group(2).strip()
        ast.properties.append(Property(kind=kind, expr=expr, msg="", source_line=i))

    # Clock detection
    if re.search(r'\brising_edge\s*\(', txt, re.IGNORECASE) or re.search(r'\bfalling_edge\s*\(', txt, re.IGNORECASE):
        ast.stats["has_clock"] = True
    elif re.search(r'process\s*\(\s*clk\s*\)', txt, re.IGNORECASE):
        ast.stats["has_clock"] = True
    else:
        ast.stats["has_clock"] = False

    return ast
