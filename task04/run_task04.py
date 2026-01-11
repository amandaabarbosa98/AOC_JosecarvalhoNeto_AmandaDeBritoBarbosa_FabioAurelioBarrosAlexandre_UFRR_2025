#!/usr/bin/env python3
"""
TASK 04 pipeline (automation) + Objective 5 (Common AST).

This script does NOT assume tools are installed. It will:
- detect VHDL files (recursively)
- generate auxiliary specs (ports + @c2vhdl tags)
- optionally run external tools (vhd2vl, yosys prep, sby, v2c, esbmc)
- generate a summary.json / summary.csv
- optionally generate a common AST JSON (Objective 5) by merging VHDL tags + Yosys JSON

Usage (basic):
  python3 task04/run_task04.py --in task04/inputs_vhdl --out task04

Optional:
  --run-yosys  (requires yosys)
  --run-sby    (requires symbiyosys 'sby')
  --run-esbmc  (requires esbmc + v2c configured)
  --gen-ast    (requires yosys for structural AST, but still works VHDL-only)
"""

from __future__ import annotations
import argparse
import csv
import json
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from ast_frontend.vhdl_light_parser import parse_vhdl_to_ast
from ast_frontend.yosys_json_adapter import yosys_json_to_ast
from unify_ast import merge_ast  # common merge fn

def find_existing_verilog(design: str, search_dir: Path) -> Optional[Path]:
    """Best-effort fallback: use pre-generated Verilog (e.g., elaborado_*.v).

    This is useful when VHD2VL is not installed/configured. We look for common
    filenames and then fall back to searching for a `module <design>` declaration.
    """
    if not search_dir.exists():
        return None

    candidates = [
        search_dir / f"{design}.v",
        search_dir / f"elaborado_{design}.v",
        search_dir / "elaborado.v",
    ]
    for c in candidates:
        if c.exists():
            return c

    for f in sorted(search_dir.glob("*.v")):
        try:
            body = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if f"module {design}" in body:
            return f
    return None


def load_tools(tools_path: Path) -> Dict[str, str]:
    if not tools_path.exists():
        return {}
    return json.loads(tools_path.read_text(encoding="utf-8", errors="replace"))

def tool_available(cmd: str) -> bool:
    parts = shlex.split(cmd)
    if not parts:
        return False
    return shutil.which(parts[0]) is not None

def sh(cmd: str, cwd: Optional[Path] = None) -> Dict[str, Any]:
    p = subprocess.run(cmd, shell=True, cwd=str(cwd) if cwd else None,
                       text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"ok": p.returncode == 0, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}

def ensure_dirs(out_root: Path):
    for p in ["specs", "generated/verilog", "generated/verilog_prep", "generated/yosys_json",
              "generated/c", "generated/harness", "logs/translate", "logs/sby", "logs/esbmc",
              "results", "results/ast"]:
        (out_root / p).mkdir(parents=True, exist_ok=True)

def extract_spec_from_ast(vhdl_ast) -> Dict[str, Any]:
    ports_in = [p.__dict__ for p in vhdl_ast.ports if p.direction == "in"]
    ports_out = [p.__dict__ for p in vhdl_ast.ports if p.direction == "out"]
    assumes = [pr.__dict__ for pr in vhdl_ast.properties if pr.kind == "assume"]
    asserts = [pr.__dict__ for pr in vhdl_ast.properties if pr.kind == "assert"]
    return {
        "design_name": vhdl_ast.design_name,
        "source_vhdl": vhdl_ast.source_vhdl,
        "ports": {"inputs": ports_in, "outputs": ports_out},
        "assumes": assumes,
        "asserts": asserts,
        "has_clock": bool((vhdl_ast.stats or {}).get("has_clock", False)),
    }

def generate_harness_c(spec: Dict[str, Any], out_c: Path):
    """
    Generates a minimal ESBMC harness template.
    IMPORTANT: You MUST adjust the entry-point call to match your V2C output.
    """
    design = spec["design_name"]
    inputs = spec["ports"]["inputs"]
    outputs = spec["ports"]["outputs"]
    assumes = spec.get("assumes", [])
    asserts = spec.get("asserts", [])

    def c_type(bits: int) -> str:
        if bits <= 1: return "unsigned char"
        if bits <= 8: return "unsigned char"
        if bits <= 16: return "unsigned short"
        if bits <= 32: return "unsigned int"
        return "unsigned long long"

    lines = []
    lines.append("// Auto-generated harness for ESBMC (TASK 04)")
    lines.append("#include <assert.h>")
    lines.append("")
    lines.append("extern unsigned char __VERIFIER_nondet_uchar(void);")
    lines.append("extern unsigned short __VERIFIER_nondet_ushort(void);")
    lines.append("extern unsigned int __VERIFIER_nondet_uint(void);")
    lines.append("extern unsigned long long __VERIFIER_nondet_ulonglong(void);")
    lines.append("")
    lines.append("static unsigned long long nondet_u(unsigned bits){")
    lines.append("  if(bits<=8) return (unsigned long long)__VERIFIER_nondet_uchar();")
    lines.append("  if(bits<=16) return (unsigned long long)__VERIFIER_nondet_ushort();")
    lines.append("  if(bits<=32) return (unsigned long long)__VERIFIER_nondet_uint();")
    lines.append("  return (unsigned long long)__VERIFIER_nondet_ulonglong();")
    lines.append("}")
    lines.append("")
    lines.append("/*")
    lines.append(" * TODO: ajuste a assinatura abaixo para bater com o C gerado pelo V2C")
    lines.append(" */")
    lines.append(f"void {design}_step(void);")
    lines.append("")
    lines.append("#define __VERIFIER_assume(x) do { if(!(x)) __builtin_unreachable(); } while(0)")
    lines.append("")
    lines.append("int main(void){")
    for p in inputs:
        bits = int(p.get("width", 1))
        lines.append(f"  {c_type(bits)} {p['name']} = ({c_type(bits)})nondet_u({bits});")
    for p in outputs:
        bits = int(p.get("width", 1))
        lines.append(f"  {c_type(bits)} {p['name']} = 0;")
    lines.append("")
    lines.append("  // Assumptions extraídas do VHDL")
    for a in assumes:
        expr = (a.get("expr") or "").strip()
        if expr:
            lines.append(f"  // ASSUME: {expr}")
    lines.append("")
    lines.append("  // Chamada do modelo (edite para passar entradas/saídas)")
    lines.append(f"  // {design}_step();")
    lines.append("")
    lines.append("  // Assertions extraídas do VHDL")
    for at in asserts:
        expr = (at.get("expr") or "").strip()
        if expr:
            lines.append(f"  // ASSERT: {expr}")
    lines.append("  return 0;")
    lines.append("}")
    out_c.write_text("\n".join(lines), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input folder (VHDL files)")
    ap.add_argument("--out", dest="out", required=True, help="Output root (task04 folder)")
    ap.add_argument("--tools", dest="tools", default=None, help="tools.json path (optional)")
    ap.add_argument("--run-yosys", action="store_true")
    ap.add_argument("--run-sby", action="store_true")
    ap.add_argument("--run-esbmc", action="store_true")
    ap.add_argument("--gen-ast", action="store_true")
    args = ap.parse_args()

    inp = Path(args.inp)
    out = Path(args.out)
    ensure_dirs(out)

    tools_path = Path(args.tools) if args.tools else (out / "tools.json")
    tools = load_tools(tools_path)

    vhdl_files = sorted([p for p in inp.rglob("*.vhd")] + [p for p in inp.rglob("*.vhdl")])
    if not vhdl_files:
        raise SystemExit(f"No VHDL found under: {inp}")

    summary = []
    for vf in vhdl_files:
        vhdl_ast = parse_vhdl_to_ast(vf)
        spec = extract_spec_from_ast(vhdl_ast)

        verilog_dir = out / "inputs_verilog"

        spec_path = out / "specs" / f"{spec['design_name']}.json"
        spec_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")

        entry = {
            "design": spec["design_name"],
            "vhdl": str(vf),
            "spec": str(spec_path),
            "steps": {},
            "notes": [],
            "generated": {},
        }

        # VHD2VL
        verilog_out = out / "generated" / "verilog" / f"{spec['design_name']}.v"
        if "vhd2vl" in tools:
            cmd = tools["vhd2vl"].format(in_vhdl=vf, out_verilog=verilog_out)
            if tool_available(cmd):
                r = sh(cmd)
                (out/"logs"/"translate"/f"{spec['design_name']}_vhd2vl.log").write_text(r["stdout"]+"\n"+r["stderr"], encoding="utf-8")
                entry["steps"]["vhd2vl"] = {"ok": r["ok"], "cmd": cmd}
            else:
                entry["steps"]["vhd2vl"] = {"ok": False, "cmd": cmd, "skipped": True}
                entry["notes"].append("vhd2vl not found in PATH (configure/install)")
        else:
            entry["steps"]["vhd2vl"] = {"ok": False, "cmd": "", "skipped": True}
            entry["notes"].append("vhd2vl not configured in tools.json")

        # Fallback: use pre-generated Verilog if VHD2VL was skipped/failed
        if not verilog_out.exists():
            src_v = find_existing_verilog(spec["design_name"], verilog_dir)
            if src_v is not None:
                shutil.copyfile(src_v, verilog_out)
                entry["notes"].append(f"Used existing Verilog fallback: {src_v}")
                # Mark vhd2vl as effectively ok for downstream steps
                st = entry["steps"].get("vhd2vl", {})
                st.update({"ok": True, "skipped": False, "fallback": True, "src": str(src_v)})
                entry["steps"]["vhd2vl"] = st
            else:
                entry["notes"].append("No existing Verilog found for fallback (put elaborado_*.v in task04/inputs_verilog).")

        entry["generated"]["verilog"] = str(verilog_out) if verilog_out.exists() else ""

        # Yosys prep + json
        verilog_prep = out / "generated" / "verilog_prep" / f"{spec['design_name']}_prep.v"
        yosys_json = out / "generated" / "yosys_json" / f"{spec['design_name']}.json"
        if args.run_yosys and "yosys_prep" in tools:
            cmd = tools["yosys_prep"].format(in_verilog=verilog_out, out_verilog_prep=verilog_prep, out_yosys_json=yosys_json, top=spec["design_name"])
            if tool_available(cmd):
                r = sh(cmd)
                (out/"logs"/"translate"/f"{spec['design_name']}_yosys.log").write_text(r["stdout"]+"\n"+r["stderr"], encoding="utf-8")
                entry["steps"]["yosys_prep"] = {"ok": r["ok"], "cmd": cmd}
            else:
                entry["steps"]["yosys_prep"] = {"ok": False, "cmd": cmd, "skipped": True}
                entry["notes"].append("yosys not found in PATH (configure/install)")
        else:
            entry["steps"]["yosys_prep"] = {"ok": False, "cmd": "", "skipped": True}
            if args.run_yosys:
                entry["notes"].append("yosys_prep not configured in tools.json")
        entry["generated"]["verilog_prep"] = str(verilog_prep) if verilog_prep.exists() else ""
        entry["generated"]["yosys_json"] = str(yosys_json) if yosys_json.exists() else ""

        # Objective 5: common AST
        if args.gen_ast:
            if yosys_json.exists():
                y_ast = yosys_json_to_ast(yosys_json, design_name=spec["design_name"])
                out_ast = merge_ast(vhdl_ast, y_ast)
            else:
                out_ast = vhdl_ast
                entry["notes"].append("AST generated from VHDL only (no yosys json).")
            ast_path = out / "results" / "ast" / f"{spec['design_name']}.ast.json"
            ast_path.write_text(json.dumps(out_ast.to_dict(), indent=2), encoding="utf-8")
            entry["generated"]["common_ast"] = str(ast_path)

        # SymbiYosys (optional)
        if args.run_sby and "sby" in tools:
            sby_file = out / "generated" / f"{spec['design_name']}.sby"
            sby_file.write_text(f"""[options]
mode bmc
depth 20

[engines]
smtbmc z3

[script]
read_verilog {verilog_prep if verilog_prep.exists() else verilog_out}
prep -top {spec['design_name']}

[files]
{verilog_prep if verilog_prep.exists() else verilog_out}
""", encoding="utf-8")
            cmd = tools["sby"].format(sby_file=sby_file)
            if tool_available(cmd):
                r = sh(cmd, cwd=sby_file.parent)
                (out/"logs"/"sby"/f"{spec['design_name']}.log").write_text(r["stdout"]+"\n"+r["stderr"], encoding="utf-8")
                entry["steps"]["sby"] = {"ok": r["ok"], "cmd": cmd, "sby": str(sby_file)}
            else:
                entry["steps"]["sby"] = {"ok": False, "cmd": cmd, "skipped": True}
                entry["notes"].append("sby not found in PATH (configure/install)")
        else:
            entry["steps"]["sby"] = {"ok": False, "cmd": "", "skipped": True}
            if args.run_sby:
                entry["notes"].append("sby not configured in tools.json")

        # V2C + ESBMC (optional) – generates harness template even if tools missing
        if args.run_esbmc:
            harness_out = out / "generated" / "harness" / f"{spec['design_name']}_harness.c"
            generate_harness_c(spec, harness_out)
            entry["generated"]["harness_c"] = str(harness_out)

            c_model = out / "generated" / "c" / f"{spec['design_name']}.c"
            if "v2c" in tools:
                cmd = tools["v2c"].format(in_verilog=(verilog_prep if verilog_prep.exists() else verilog_out), out_c=c_model)
                if tool_available(cmd):
                    r = sh(cmd)
                    (out/"logs"/"translate"/f"{spec['design_name']}_v2c.log").write_text(r["stdout"]+"\n"+r["stderr"], encoding="utf-8")
                    entry["steps"]["v2c"] = {"ok": r["ok"], "cmd": cmd}
                else:
                    entry["steps"]["v2c"] = {"ok": False, "cmd": cmd, "skipped": True}
                    entry["notes"].append("v2c not found in PATH (configure/install)")
            else:
                entry["steps"]["v2c"] = {"ok": False, "cmd": "", "skipped": True}
                entry["notes"].append("v2c not configured in tools.json")

            if "esbmc" in tools:
                cmd = tools["esbmc"].format(in_c=harness_out)
                if tool_available(cmd):
                    r = sh(cmd)
                    (out/"logs"/"esbmc"/f"{spec['design_name']}.log").write_text(r["stdout"]+"\n"+r["stderr"], encoding="utf-8")
                    entry["steps"]["esbmc"] = {"ok": r["ok"], "cmd": cmd}
                else:
                    entry["steps"]["esbmc"] = {"ok": False, "cmd": cmd, "skipped": True}
                    entry["notes"].append("esbmc not found in PATH (configure/install)")
            else:
                entry["steps"]["esbmc"] = {"ok": False, "cmd": "", "skipped": True}
                entry["notes"].append("esbmc not configured in tools.json")
        else:
            entry["steps"]["v2c"] = {"ok": False, "cmd": "", "skipped": True}
            entry["steps"]["esbmc"] = {"ok": False, "cmd": "", "skipped": True}

        summary.append(entry)

    (out/"results"/"summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    csv_path = out/"results"/"summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["design", "vhd2vl", "yosys_prep", "sby", "v2c", "esbmc", "notes"])
        steps = ["vhd2vl", "yosys_prep", "sby", "v2c", "esbmc"]
        for e in summary:
            def status(step):
                st = e["steps"].get(step, {})
                if st.get("skipped"):
                    return "SKIP"
                return "OK" if st.get("ok") else "FAIL"
            w.writerow([e["design"]] + [status(s) for s in steps] + [" | ".join(e.get("notes", []))])

    print(f"Wrote: {out/'results'/'summary.json'}")
    print(f"Wrote: {csv_path}")

if __name__ == "__main__":
    main()
