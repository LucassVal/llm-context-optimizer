#!/usr/bin/env python3
"""NC-SCR-FR-025-lexico-validator.py — Validate ULQ-TAG-INDEX + LEXICO paths against filesystem.
Usage: python NC-SCR-FR-025-lexico-validator.py
Exit 0 if all paths valid, 1 if any gaps found.
"""
from __future__ import annotations
# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS


import json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
LEXICO = ROOT / "01_neocortex_framework" / ".neocortex" / "lexico"
ULQ_TAG = LEXICO / "NC-ULQ-TAG-INDEX.json"
LEXICO_JSON = LEXICO / "NC-LEXICO-LATEST.json"

def audit_ulq():
    if not ULQ_TAG.exists():
        print("FAIL: ULQ-TAG-INDEX.json not found")
        return 1
    data = json.loads(ULQ_TAG.read_text(encoding="utf-8"))
    domains = data.get("domains", {})
    ok, fail = 0, 0
    for name, info in domains.items():
        path = info.get("path", "")
        exists = (ROOT / path).exists() if path else False
        status = "OK" if exists else "FAIL"
        if exists: ok += 1
        else: fail += 1
        print(f"  [{status}] {name} -> {path}")
    print(f"\nULQ-TAG-INDEX: {ok+fail} domains | OK={ok} | FAIL={fail}")
    return 1 if fail > 0 else 0

def audit_lexico():
    if not LEXICO_JSON.exists():
        print("FAIL: LEXICO.json not found")
        return 1
    data = json.loads(LEXICO_JSON.read_text(encoding="utf-8"))
    engines = data.get("engines", []) + data.get("tools", []) + data.get("services", [])
    ok, fail = 0, 0
    for entry in engines:
        path = entry.get("path", "")
        exists = (ROOT / "01_neocortex_framework" / path.replace("\\", "/")).exists()
        if exists: ok += 1
        else: fail += 1
        if not exists:
            print(f"  [FAIL] {entry.get('id','?')} -> {path}")
    print(f"\nLEXICO: {ok+fail} entries | OK={ok} | FAIL={fail}")
    return 1 if fail > 0 else 0

if __name__ == "__main__":
    print("=== LEXICO Path Validator (NC-SCR-FR-025) ===")
    r1 = audit_ulq()
    print()
    r2 = audit_lexico()
    sys.exit(r1 or r2)
