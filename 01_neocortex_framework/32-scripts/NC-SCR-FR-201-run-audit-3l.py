import json, sys, importlib.util, os
base = r'C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42'
fw = os.path.join(base, '01_neocortex_framework')

spec = importlib.util.spec_from_file_location('a3l', os.path.join(fw, 'neocortex', 'core', 'NC-CORE-FR-173-mcp-audit-3-levels.py'))
mod = importlib.util.module_from_spec(spec)
sys.modules['a3l'] = mod
spec.loader.exec_module(mod)

print("Running MCP Audit 3 Levels...")
auditor = mod.get_auditor_3l()
report = auditor.audit_all_levels()

print(f"\n=== OVERALL SCORE: {report['overall_score']}% | STATUS: {report['status']} ===")
print(f"Total checks: {report['total_checks']} | Passed: {report['total_passed']}")

for camada in ['camada_1', 'camada_2', 'camada_3']:
    c = report[camada]
    print(f"\n--- {camada.upper()} (score: {c.get('score',0)}%) ---")
    for key, val in c.items():
        if key in ('score', 'checks', 'passed'):
            continue
        if isinstance(val, dict):
            print(f"  {key}: checks={val.get('checks','?')} passed={val.get('passed','?')}")
            if val.get('bad_files'):
                for bf in val['bad_files'][:3]:
                    print(f"    FAIL: {bf}")
            if val.get('stub_files'):
                print(f"    STUBS: {val['stub_files']}")
            if val.get('fail'):
                for f in val['fail'][:3]:
                    print(f"    FAIL: {f}")
            if val.get('files') and len(val.get('files',[])) > 0:
                print(f"    Hardcoded paths: {len(val['files'])} files")
                for hf in val['files'][:5]:
                    print(f"      {hf}")

# Save report
out = os.path.join(base, 'DIR-DS-002-audit-logs', 'NC-AUDIT-3L-20260430.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False, default=str)
print(f"\nReport saved: {out}")
