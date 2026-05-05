import sys, importlib.util
base = r'C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework'
spec = importlib.util.spec_from_file_location("sr", base + r"\neocortex\core\NC-CORE-FR-165-semantic-router.py")
sr = importlib.util.module_from_spec(spec)
sys.modules["sr"] = sr
spec.loader.exec_module(sr)
router = sr.get_router()

symbols = [
    '@SSOT', '@ROADMAP', '@LOCKS', '@BOOT', '@ULQ', '@RULES', '@CHANGELOG', '@MAPS',
    '@LEXICO', '@POPULATE', '@PREP', '@POLICY', '@SOP', '@ADR',
    '$FRONTAL', '$TEMPORAL', '$PARIETAL',
    '%DONE', '%NOW', '%NEXT',
    '#GOV', '#ORCH', '#MEM', '#STATE',
]

ok = 0
fail = 0
for s in symbols:
    r = router.resolve_symbol(s)
    status = 'OK' if r.get('found') else 'FAIL'
    if r.get('found'):
        ok += 1
    else:
        fail += 1
    extra = ''
    if r.get('path'):
        extra = f' -> {r["path"][:60]}'
    if r.get('level'):
        extra += f' [level={r["level"]}]'
    print(f'  {status} {s}{extra}')

print(f'\n{ok}/{ok+fail} symbols resolved')

# Test resolve_path (actual file existence)
print('\n=== resolve_path test ===')
for s in ['@LOCKS', '@SSOT', '@ULQ', '@LEXICO']:
    p = router.resolve_path(s)
    status = 'EXISTS' if p else 'MISSING'
    print(f'  {status} {s} -> {p}')
