# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
import yaml, os, glob

base = r'C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-DS-001-tickets'

# Protocol to inject into all tickets
protocol = {
    'protocol': {
        'rca_applied': True,
        'three_w_applied': True,
        'kiss_check': '<2500 chars per ticket description',
        'validation': {
            'py': ['ruff check --fix', 'ruff format', 'ruff check', 'mypy --ignore-missing-imports', 'py_compile', 'bandit -q'],
            'yaml': ['yaml.safe_load', 'naming NC- check', 'secret scan'],
            'mdc': ['frontmatter YAML validate', 'NC-READ-HASH check', 'naming NC- check'],
            'json': ['json.loads parse', 'naming NC- check'],
            'all': ['@LOCKS check', 'Write Zone check', '@SSOT update', 'Handoff YAML', '3W check', 'SSOT Header'],
        },
        'sandbox_required': True,
        'sandbox_steps': [
            '1. Copiar arquivo alvo para *-sandbox.py',
            '2. Fazer alteracoes no sandbox',
            '3. Validar sandbox (ruff+mypy+py_compile)',
            '4. Testar sandbox',
            '5. Aplicar no real (com backup)',
            '6. Rollback via backup se falhar',
        ],
        'handoff_required': True,
        'handoff_template': 'DIR-DS-001-tickets/NC-DS-HANDOFF-TEMPLATE.yaml',
        'handoff_dest': 'DIR-DS-002-audit-logs/',
        'handoff_format': 'NC-DS-{TICKET_ID}-handoff-{YYYYMMDDTHHMMSS}.yaml',
        'handoff_fields': ['ticket_id', 'status', 'submitted_at', 'submitted_by', 'summary', 'files_created', 'files_modified', 'validation_rounds', 'barriers_passed', 'locks_violated', 't0_review'],
        'governance': {
            'eisenhower_applied': True,
            'mordaca_h': 'HOOK — bloqueia acao invalida ANTES de executar (FAIL-FAST)',
            'mordaca_c': 'CHECKPOINT — audita estado a cada 300s (PulseScheduler)',
            'mordaca_s': 'SCHEDULE — consolida no CICLO 4 semanal',
            'mordaca_u': 'USER — T0 aprova/rejeita via handoff review',
            'kaizen': 'Registrar micro-melhoria no @CHANGELOG apos conclusao',
            'roadmap': 'Marcar %DONE no @ROADMAP apos handoff aprovado',
        },
    }
}

updated = 0
for f in glob.glob(os.path.join(base, 'NC-DS-*.yaml')):
    if 'HANDOFF-TEMPLATE' in f or 'TICKET-TEMPLATE' in f:
        continue
    
    with open(f, 'r', encoding='utf-8') as fh:
        try:
            data = yaml.safe_load(fh)
        except:
            continue
    
    if data is None:
        continue
    
    # Add protocol if missing
    if 'protocol' not in data:
        data['protocol'] = protocol['protocol']
        with open(f, 'w', encoding='utf-8') as fh:
            yaml.dump(data, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)
        updated += 1

print(f'Updated {updated} tickets with full protocol (RCA+3W+KISS+Sandbox+Handoff+Governance)')
