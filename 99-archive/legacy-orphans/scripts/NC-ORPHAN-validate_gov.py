import yaml, sys
sys.stdout.reconfigure(encoding='utf-8')
path = '01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-003-ia-governance-rules.yaml'
try:
    with open(path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    print('YAML: VALIDO')
    rules = data.get('rules', {})
    total = 0
    status_counts = {}
    all_ids = []
    for cat, val in rules.items():
        cat_rules = val.get('rules', []) if isinstance(val, dict) else []
        ids = [r.get('id','?') for r in cat_rules]
        for r in cat_rules:
            s = r.get('status','?')
            status_counts[s] = status_counts.get(s, 0) + 1
            all_ids.append(r.get('id','?'))
        print(f'  {cat}: {ids}')
        total += len(cat_rules)
    print(f'\nTotal regras: {total}')
    print(f'Status breakdown: {status_counts}')
    print(f'IDs presentes: {sorted(all_ids)}')
    expected = [f'R{i:02d}' if i > 9 else f'R{i:02d}' for i in range(1,31)]
    missing = [f'R{str(i).zfill(2)}' for i in range(1,31) if f'R{str(i).zfill(2)}' not in all_ids and f'R{i}' not in all_ids]
    print(f'IDs faltando (R01-R30): {missing}')
    cm = data.get('compliance_metrics', {})
    print(f'\ncompliance_metrics:')
    for k,v in cm.items():
        print(f'  {k}: {v}')
    checklist = data.get('implementation_checklist', [])
    pending_tasks = [t.get('task','?') for t in checklist if t.get('status') == 'pending']
    print(f'\nChecklist pendente ({len(pending_tasks)} items):')
    for t in pending_tasks:
        print(f'  - {t}')
except yaml.YAMLError as e:
    print(f'YAML INVALIDO: {e}')
except Exception as e:
    import traceback
    traceback.print_exc()
