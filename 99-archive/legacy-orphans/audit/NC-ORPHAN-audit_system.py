#!/usr/bin/env python3
"""
System-wide YAML/JSON audit + template coverage check.
Output: audit_results.txt
"""
import os, sys, yaml, json, glob, re
sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.getcwd()
results = {"yaml_errors": [], "yaml_ok": [], "json_errors": [], "json_ok": [],
           "templates_missing": [], "templates_ok": [], "governance_summary": []}

# ── 1. GOVERNANCE/SSOT YAMLs (priority) ─────────────────────────────────────
GOV_YAMLS = [
    "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-003-ia-governance-rules.yaml",
    "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml",
    "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-FR-002-rules-policy.yaml",
    "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-002-ticket-lifecycle.yaml",
    "01_neocortex_framework/DIR-CFG-FR-001-config-main/neocortex_config.yaml",
    "01_neocortex_framework/DIR-CFG-FR-001-config-main/neocortex_config_dev.yaml",
]

print("=" * 70)
print("AUDIT GOVERNANÇA/SSOT (prioridade crítica)")
print("=" * 70)
for path in GOV_YAMLS:
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        msg = f"MISSING  | {path}"
        results["yaml_errors"].append({"path": path, "error": "FILE NOT FOUND"})
        print(msg)
        continue
    try:
        with open(full, encoding='utf-8', errors='replace') as f:
            yaml.safe_load(f)
        results["yaml_ok"].append(path)
        print(f"OK       | {path}")
    except yaml.YAMLError as e:
        err = str(e).split('\n')[0]
        results["yaml_errors"].append({"path": path, "error": err})
        print(f"ERROR    | {path}")
        print(f"         | {err}")

# ── 2. ALL YAML files in project ─────────────────────────────────────────────
print()
print("=" * 70)
print("VARREDURA COMPLETA DE YAMLs")
print("=" * 70)
all_yamls = glob.glob(os.path.join(ROOT, "**", "*.yaml"), recursive=True)
skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}

error_yamls = []
for ypath in sorted(all_yamls):
    # skip hidden/env dirs
    parts = ypath.replace(ROOT, '').split(os.sep)
    if any(s in skip_dirs for s in parts):
        continue
    rel = os.path.relpath(ypath, ROOT)
    if rel in [os.path.normpath(g) for g in GOV_YAMLS]:
        continue  # already checked
    try:
        with open(ypath, encoding='utf-8', errors='replace') as f:
            yaml.safe_load(f)
        results["yaml_ok"].append(rel)
    except yaml.YAMLError as e:
        err = str(e).split('\n')[0]
        error_yamls.append({"path": rel, "error": err})
        results["yaml_errors"].append({"path": rel, "error": err})

print(f"YAMLs verificados: {len(all_yamls)} | OK: {len(results['yaml_ok'])} | ERROS: {len(error_yamls)}")
if error_yamls:
    print("\nArquivos com erro:")
    for e in error_yamls:
        print(f"  ERROR | {e['path']}")
        print(f"        | {e['error'][:80]}")

# ── 3. ALL JSON files ─────────────────────────────────────────────────────────
print()
print("=" * 70)
print("VARREDURA DE JSONs")
print("=" * 70)
all_jsons = glob.glob(os.path.join(ROOT, "**", "*.json"), recursive=True)
json_errors = []
for jpath in sorted(all_jsons):
    parts = jpath.replace(ROOT, '').split(os.sep)
    if any(s in skip_dirs for s in parts):
        continue
    rel = os.path.relpath(jpath, ROOT)
    try:
        with open(jpath, encoding='utf-8', errors='replace') as f:
            json.load(f)
        results["json_ok"].append(rel)
    except json.JSONDecodeError as e:
        json_errors.append({"path": rel, "error": str(e)[:80]})
        results["json_errors"].append({"path": rel, "error": str(e)[:80]})

print(f"JSONs verificados: {len(all_jsons)} | OK: {len(results['json_ok'])} | ERROS: {len(json_errors)}")
if json_errors:
    print("\nArquivos com erro:")
    for e in json_errors:
        print(f"  ERROR | {e['path']}")
        print(f"        | {e['error']}")

# ── 4. TEMPLATE COVERAGE ──────────────────────────────────────────────────────
print()
print("=" * 70)
print("TEMPLATES — COBERTURA (referenciados no SSOT)")
print("=" * 70)

EXPECTED_TEMPLATES = [
    "01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-LBE-DS-000-parent.mdc",
    "01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TMP-WL-001-cortex-template.mdc",
    "01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-LBE-CC-001-claude-leak-master.mdc",
    "01_neocortex_framework/DIR-TMP-FR-001-templates-main/00-cortex-FULL.mdc",
    "01_neocortex_framework/DIR-TMP-FR-001-templates-main/00-cortex-STARTER.mdc",
    "01_neocortex_framework/DIR-TMP-FR-001-templates-main/memory-ledger-TEMPLATE.json",
    "01_neocortex_framework/DIR-TMP-FR-001-templates-main/phase-lobe-TEMPLATE.mdc",
    "01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TOOL-FR-TEMPLATE/NC-CFG-FR-001-plugin.json",
    "01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TOOL-FR-TEMPLATE/README.md",
    "DIR-DS-001-tickets/NC-DS-HANDOFF-TEMPLATE.yaml",
    "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-FR-001-agent-policy-template.yaml",
]
# Try to read from NC-TPL-FR-001 index if exists
tpl_index = os.path.join(ROOT, "01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TPL-FR-001-template-central-index.yaml")
if os.path.exists(tpl_index):
    print(f"  NC-TPL-FR-001-template-central-index.yaml: EXISTS")
else:
    print(f"  NC-TPL-FR-001-template-central-index.yaml: MISSING ← CRÍTICO")
    results["templates_missing"].append("NC-TPL-FR-001-template-central-index.yaml")

for tpl in EXPECTED_TEMPLATES:
    full = os.path.join(ROOT, tpl)
    if os.path.exists(full):
        results["templates_ok"].append(tpl)
        print(f"  OK      | {os.path.basename(tpl)}")
    else:
        results["templates_missing"].append(tpl)
        print(f"  MISSING | {tpl}")

# ── 5. SUMMARY ────────────────────────────────────────────────────────────────
print()
print("=" * 70)
print("RESUMO EXECUTIVO")
print("=" * 70)
total_yaml = len(results['yaml_ok']) + len(results['yaml_errors'])
total_json = len(results['json_ok']) + len(results['json_errors'])
print(f"YAML:      {len(results['yaml_ok'])}/{total_yaml} OK | {len(results['yaml_errors'])} ERROS")
print(f"JSON:      {len(results['json_ok'])}/{total_json} OK | {len(results['json_errors'])} ERROS")
print(f"Templates: {len(results['templates_ok'])}/{len(EXPECTED_TEMPLATES)+1} OK | {len(results['templates_missing'])} FALTANDO")
print()
print("TICKETS A CRIAR:")
ticket_n = 167
if results['yaml_errors']:
    crit_gov = [e for e in results['yaml_errors'] if 'DIR-DOC-FR-001' in e['path'] or 'DIR-CFG-FR-001' in e['path']]
    other = [e for e in results['yaml_errors'] if e not in crit_gov]
    if crit_gov:
        print(f"  NC-DS-{ticket_n}: CRÍTICO — Corrigir {len(crit_gov)} YAML(s) de governança/config inválidos")
        ticket_n += 1
    if other:
        print(f"  NC-DS-{ticket_n}: ALTA    — Corrigir {len(other)} YAML(s) gerais inválidos")
        ticket_n += 1
if results['json_errors']:
    print(f"  NC-DS-{ticket_n}: ALTA    — Corrigir {len(results['json_errors'])} JSON(s) inválidos")
    ticket_n += 1
if results['templates_missing']:
    print(f"  NC-DS-{ticket_n}: MÉDIA   — Criar {len(results['templates_missing'])} template(s) ausentes do SSOT")
    ticket_n += 1

# Save results
with open('audit_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print()
print("Resultados salvos em audit_results.json")
