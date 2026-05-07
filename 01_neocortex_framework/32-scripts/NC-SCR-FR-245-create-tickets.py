# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
import yaml, os
from datetime import datetime

base = r'C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-DS-001-tickets'

tickets = [
    ('NC-DS-210','URGENT','Gateway le MCP hook registry - unificar hooks (SSOT unico)','FASE 2: HOOKS','Gateway consulta MCP hook registry como fonte unica de verdade. Remove listas hardcoded de _check_per_action. NC-CORE-FR-129-shared-kernel-gateway.py (ATENCAO: @LOCK).'),
    ('NC-DS-211','URGENT','Gateway orquestra LockGuard+BashGuard+ToolGuard - validacao unificada','FASE 2: VALIDATION','Gateway.validate_action() orquestra todos os validadores. LockGuard.check(), BashGuard.check(), ToolGuard.check() viram metodos chamados pelo Gateway.'),
    ('NC-DS-216','URGENT','Substituir 20 hardcoded paths por ulq.resolve() + wire-up nos 77 engines','FASE 2: ULQ','Todo hardcoded path substituido por ulq.resolve("@SIMBOLO"). 20 arquivos afetados. 77 engines para wire-up.'),
    ('NC-DS-217','URGENT','Sanitizar 3 YAMLs quebrados (multi-doc) - NC-DIAG-GOV-001, NC-DS-122, NC-DS-170','FASE 2: YAML','3 tickets com YAML multi-documento que falham yaml.safe_load. Corrigir sintaxe.'),
    ('NC-DS-221','URGENT','Reiniciar PulseScheduler + criar baseline no Regression Buffer','FASE 2: ENFORCE','PulseScheduler crashado (is_running bug corrigido). Reiniciar. Criar primeira baseline no regression buffer.'),
    ('NC-DS-222','URGENT','S2 - Template Injection automatico (frontmatter+hash+3W ao criar arquivo)','FASE 2: PREVENCAO','VACINA preventiva: todo novo arquivo .py/.yaml/.mdc recebe template automatico com frontmatter, NC-READ-HASH, e 3W header.'),
    ('NC-DS-223','URGENT','Atualizar requirements.txt (2 deps vs ~15 reais)','FASE 2: DEPENDENCIAS','Adicionar: fastmcp, ruamel.yaml, rich, cachetools, platformdirs, notifypy, diskcache, duckdb, msgspec, psutil, PyYAML, jsonschema, aiohttp.'),
    ('NC-DS-212','HIGH','FR-173 absorve FR-149 - auditor unico 3 camadas','FASE 2: AUDIT','FR-173 absorve todas as funcoes do FR-149. FR-149 deprecated. #GOV chama FR-173 via audit.full.'),
    ('NC-DS-213','HIGH','LEXICO como SSOT unico - deletar _INDEX.yaml + _INDEX.mdc (x5)','FASE 2: CATALOG','NC-LEXICO-LATEST.json vira catalogo unico com 3 secoes. Deletar _INDEX.yaml e _INDEX.mdc duplicados.'),
    ('NC-DS-214','HIGH','ConfigProvider central via ulq.resolve - cache 60s, hot-reload','FASE 2: CONFIG','8 modulos carregam YAML independentemente. Criar ConfigProvider unico com cache 60s e hot-reload no PulseScheduler.'),
    ('NC-DS-220','HIGH','STEP 0 + Mentor Mode ativo no Gateway (validate_action)','FASE 2: ENFORCE','Ativar verificacao de ambiente (python, ruff, mypy) antes de toda acao MCP. Mentor mode: instrucoes injetadas antes de calls LLM.'),
    ('NC-DS-215','HIGH','Documentar 54 engines no Master Map + Blueprint','FASE 2: DOCS','77 engines no disco, 23 documentadas. Documentar as 54 restantes com proposito, regra associada, e status.'),
    ('NC-DS-224','MEDIUM','S1 - Pre-commit hook local (ruff+yaml antes do commit)','FASE 2: PREVENCAO','Hook .git/hooks/pre-commit que roda ruff check + yaml.safe_load em arquivos staged. Bloqueia commit se falhar.'),
    ('NC-DS-225','MEDIUM','S3 - Auto-fix Pipeline no PulseScheduler (corrige erros triviais)','FASE 2: AUTOMACAO','PulseScheduler nao so detecta - CORRIGE: ruff --fix, ruff format, hash inject, YAML format.'),
    ('NC-DS-226','MEDIUM','S4 - Regression baseline semanal (CICLO 4)','FASE 2: QUALIDADE','Salvar estado do sistema a cada CICLO 4. Comparar semana a semana. Score caiu - alerta + RCA.'),
    ('NC-DS-227','MEDIUM','S6 - Circuito Anti-Fragil (R96) vacina de erros','FASE 2: RESILIENCIA','Erro detectado - corrigido - vacina registrada. Mesmo erro nao se repete. Regression buffer expandido.'),
    ('NC-DS-228','MEDIUM','S5 - Verification Gates por regiao cerebral (STRICT/MEDIUM/BASIC)','FASE 2: GOVERNANCA','Arquivos no $FRONTAL tem gates mais rigidos que $TEMPORAL. Criticidade proporcional ao risco.'),
    ('NC-DS-229','LOW','DIR-RES-CC-001 analysis sessions (37 files) - integrar ou arquivar','FASE 2: LIMPEZA','Sessoes de analise antigas em DIR-RES-CC. Avaliar se ha artefatos uteis ou arquivar tudo.'),
    ('NC-DS-230','HIGH','Documentar metodologia CICLO 5 completa (BSC+SWOT+KPI+OKR+ROI+PDCA+MRM)','CICLO 5','Criar documento formal NC-CYC-FR-005 com a metodologia de consultoria estrategica. Templates de relatorio e periodicidade.'),
    ('NC-DS-231','HIGH','Primeira execucao completa CICLO 5 - mega-audit + relatorio executivo','CICLO 5','Executar CICLO 5: scan 3L - BSC+SWOT - RCA+Pareto+Eisenhower - OKRs+PDCA+MRM - Relatorio - Tickets+Kaizen.'),
    ('NC-DS-232','LOW','Gerar NC-READ-HASH nos ~259 MDCs restantes (dirs externos)','FASE 2: DEDUP','Lobes em 03_external_integrations e outros dirs sem hash de deduplicacao. Gerar em lote.'),
    ('NC-DS-233','LOW','Subir LiteLLM Gateway :4000','INFRA','LiteLLM DOWN desde inicio da sessao. Tentar startup via NC-SCR-FR-110-litellm-startup.ps1.'),
    ('NC-DS-234','LOW','Subir PicoClaw :18790','INFRA','PicoClaw DOWN. Tentar startup via NC-SCR-PIC-001-picoclaw-watchdog.bat. Dependencia para dispatch de agentes T1.'),
    ('NC-DS-235','LOW','S7 - Health Dashboard endpoint (/health/dashboard)','INFRA','Endpoint que retorna score das 3 camadas em tempo real. Consumido pelo Mission Control.'),
    ('NC-DS-236','LOW','Atualizar @SSOT (NC-NAM-FR-001) com todos os novos arquivos da Fase 1+2','SSOT','Registrar NC-RULE-010, NC-CHG-FR-001, NC-MAP-FR-001, NC-CORE-FR-173, tickets NC-DS-210 a 245.'),
    ('NC-DS-237','LOW','Atualizar @BLUEPRINT (NC-ARC-FR-002) - orbital VERIFICATION + ULQ CAMADA 0','SSOT','Adicionar orbital VERIFICATION no FORUM. Documentar ULQ como CAMADA 0. Atualizar para v3.0.'),
    ('NC-DS-238','LOW','Atualizar @CHANGELOG (NC-CHG-FR-001) - Fase 1+2 + CICLO 5 + hooks 9/9','SSOT','Registrar todas as entregas: consolidacao, auditoria MCP, ULQ resolver, pipeline 3L, hooks, CICLO 5.'),
    ('NC-DS-239','LOW','Atualizar @MAPS (NC-MAP-FR-001) - organograma atualizado + fluxo ULQ-centrico','SSOT','Refletir novo orbital VERIFICATION, ULQ como CAMADA 0, pipeline 3 camadas, CICLO 5.'),
    ('NC-DS-240','LOW','Atualizar @BOOT (NC-BOOT-FR-001) - @MAPS + CICLO 5 + ULQ boot obrigatorio','SSOT','Adicionar @MAPS e @CHANGELOG na secao 5. Adicionar CICLO 5 na secao de ciclos.'),
    ('NC-DS-241','LOW','Ativar Central de Templates (NC-TPL-FR-001)','INFRA','Template central para criacao de novos arquivos. Integrar com S2 (Template Injection).'),
    ('NC-DS-242','LOW','Criar arquivo LICENSE','LEGAL','Sistema sem LICENSE. Criar MIT ou Apache 2.0.'),
    ('NC-DS-243','LOW','Popular ou remover 03_white_label_templates/ (so tem _INDEX)','LIMPEZA','Diretorio vazio. Popular com templates white-label ou remover.'),
    ('NC-DS-244','LOW','Avaliar remocao de node_modules/ (598 files, regeneravel com npm install)','LIMPEZA','node_modules pode ser removido e regenerado. Reduz tamanho do repo.'),
    ('NC-DS-245','LOW','git gc para reduzir .git de 49.7MB','LIMPEZA','Repositorio com 49.7MB. Rodar git gc --aggressive para compactar.'),
]

ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
count = 0
for t in tickets:
    tid, priority, title, front, desc = t
    yaml_data = {
        'ticket_id': tid,
        'status': 'OPEN',
        'priority': priority,
        'title': title,
        'front': front,
        'description': desc,
        'created_at': ts,
        'created_by': 'T0-Antigravity',
        'roadmap_ref': 'CICLO_5',
        'handoff_required': True,
        'verification_pipeline': ['ruff','mypy','py_compile','yaml.safe_load','secret_scan','handoff'],
    }
    filepath = os.path.join(base, f'{tid}-ticket.yaml')
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    count += 1

print(f'Created {count} ticket YAMLs in {base}')
