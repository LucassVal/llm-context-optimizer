# NC-PROMPT-FR-001  NeoCortex Master Context Prompt (v8)

> **Verso:** 8.0 | **Data:** 2026-04-14 00:18 | Por: T0 Antigravity
> Cole no incio de TODA nova sesso. Sempre atualizado com STATUS real.

---

## USO  4 CICLOS

### CICLO 1  Incio de Sesso
Cole o `NC-PROMPT-FR-001-master-context.md` inteiro  eu tenho contexto completo.  
*(Alternativa para sesses focadas: cole apenas trechos relevantes do `artifact_catalog.md` referentes aos scripts do dia.)*

### CICLO 2  Durante a Sesso
"agente X terminou"  eu valido + gero prximo prompt.

### CICLO 3  Fim de Ciclo (fim do dia ou bloco de trabalho)
```powershell
.\01_neocortex_framework\scripts\NC-SCR-FR-014-end-of-cycle.ps1 -AutoUpdate -UpdateCatalog
```
Cole o bloco STATUS gerado no prompt.

**Opes avanadas:**
- `-GenerateResume`: Gera bloco de contexto de retomada para prxima sesso
- `-ShowAll`: Mostra handoffs aprovados alm dos pendentes
- `-UpdateCatalog`: Atualiza automaticamente o catlogo de artefatos se >24h

### CICLO 4  Conciliao / Limpeza (a cada ~5-7 dias)

| O que | Quando | Como |
|---|---|---|
| Handoffs YAML em `DIR-DS-002-audit-logs/` | >10 pendentes ou 1 semana | Mover antigos para DIR-ARC-FR-001-archive-main/ |
| Roadmap NC-TODO-DS-001 | %DONE acumulando | Mover concludos para seo `## CONCLUIDOS` |
| Lobes `.mdc` | Novo sprint | Rodar `NC-SCR-FR-001-populate-lobes-ssot.py` |
| `NC-BOOT-FR-001` | Frentes mudaram | Editar seo FRENTES ATIVAS |

Arquivar YAMLs velhos:
```powershell
Get-ChildItem .\DIR-DS-002-audit-logs\ -Filter '*.yaml' |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |
  Move-Item -Destination .\DIR-ARC-FR-001-archive-main\
```

Resposta direta: voc no precisa "zerar" nada manualmente no dia a dia. O script do Ciclo 3 j cuida do STATUS. O nico que precisa de limpeza peridica so os YAMLs de handoff que se acumulam  mas s quando comear a pesar (>10 pendentes ou ~1 semana de acmulo).

---



##  R21  ZERO SUPOSIES (CRTICA MXIMA)

NUNCA afirme que arquivos existem, ferramentas esto instaladas ou mdulos importam SEM verificar.
STEP-0 completo: `DIR-DS-000-agent-config/NC-CFG-DS-005-step0-environment.md`

### STEP-0  Execute ANTES de qualquer ao

```powershell
# 1. Python
python --version              # 3.12.x

# 2. Ferramentas
python -m ruff --version
python -m pytest --version

# 3. Deps  feedback individual (ERR = instalar antes de avanar)
python -c "
import importlib, sys
libs=['mcp','fastmcp','ruamel','rich','cachetools','platformdirs',
      'notifypy','diskcache','duckdb','msgspec','psutil','yaml',
      'colorama','jsonschema','aiohttp']
falhas=[]
for lib in libs:
    try: importlib.import_module(lib); print(f'  OK  {lib}')
    except ImportError: falhas.append(lib); print(f'  ERR {lib}')
if falhas: print(f'INSTALAR: pip install {\" \".join(falhas)}'); sys.exit(1)
"

# 4. Por arquivo (aps criar/modificar qualquer .py)
python -m py_compile ARQUIVO.py                       # sintaxe
python -m ruff check --fix ARQUIVO.py                 # lint+fix
python -m ruff check ARQUIVO.py                       # confirmar 0 erros
python -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('mod','ARQUIVO.py')
mod = importlib.util.module_from_spec(spec); sys.modules['mod']=mod
try: spec.loader.exec_module(mod); print('Import OK')
except Exception as e: print(f'Import ERR: {e}')
"
```

**Ground Truth 2026-04-13:** Python 3.12.10 | ruff 0.15.10 | pytest 9.0.3 | bandit 1.9.4 | fastmcp 3.2.3

### R09  Import de mdulo com hfen (SEMPRE assim)
```python
# NUNCA: import NC-SVC-FR-005-event-bus   ERRO FATAL
import importlib.util, sys
spec = importlib.util.spec_from_file_location("event_bus",
    Path(__file__).parent / "NC-SVC-FR-005-event-bus.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["event_bus"] = mod
spec.loader.exec_module(mod)
```

### R11  Logger
```python
# NUNCA: print("...")   PROIBIDO em produo
logger = logging.getLogger(__name__)  # SEMPRE
```

---

##  SOP  Incio de Sesso (NC-SOP-FR-001)

Execute NESTA ORDEM. No pule etapas.

```
[ ] 1. MCP ativo?  netstat -an | findstr 8765
        Se no: .\start_neocortex_mcp.bat
[ ] 2. Lobos atualizados?
        python 01_neocortex_framework/scripts/NC-SCR-FR-001-populate-lobes-ssot.py --dry-run
        (Se SSOT mudou): python scripts/NC-SCR-FR-001-populate-lobes-ssot.py
[ ] 3. Handoffs PENDING_REVIEW? (validar antes de novas tasks)
        Get-ChildItem DIR-DS-002-audit-logs -Filter "*.yaml" |
          Where-Object { (Get-Content $_) -match "PENDING_REVIEW" }
[ ] 4. Roadmap relido? Ticket identificado?
        NC-TODO-DS-001-roadmap-pre-mcp.md (sprint ativo)
[ ] 5. Checkpoint criado: neocortex_checkpoint ao=create
```

---

##  SOP  Fim de Sesso (R20 obrigatrio)

>  **Script automatiza os itens 1-5:**
> ```powershell
> .\01_neocortex_framework\scripts\NC-SCR-FR-014-end-of-cycle.ps1 -AutoUpdate -UpdateCatalog
> ```
> Mostra handoffs pendentes, arquivos entregues, checklist R20 e gera bloco STATUS atualizado.

```
[ ] 0. RODAR: NC-SCR-FR-014-end-of-cycle.ps1 -AutoUpdate -UpdateCatalog
[ ] 1. @SSOT (NC-NAM-FR-001) atualizado + changelog [YYYY-MM-DD]
[ ] 2. %DONE marcado no @ROADMAP (NC-TODO-DS-001) para cada ticket concludo
[ ] 3. @POPULATE rodado: python scripts/NC-SCR-FR-001-populate-lobes-ssot.py
[ ] 4. @BOOT (NC-BOOT-FR-001) atualizado com STATUS real
[ ] 5. Este prompt (NC-PROMPT-FR-001) STATUS atualizado (cole bloco do script)
[ ] 6. Lobe NC-LBE-FR-QUALITY-001 atualizado (novos erros  Regression Buffer)
[ ] 7. Handoff com todos os campos: ajustes_aplicados, lessons_learned, deps_missing
[ ] 8. Nenhum *.db / *.wal / __pycache__ commitado
[ ] 9. Checkpoint de fim de sesso criado
```

---

##  Handoff Obrigatrio por Ticket

Todo ticket concludo deve gerar `DIR-DS-002-audit-logs/NC-DS-{NUM}-handoff-{YYYYMMDD-HHMMSS}.yaml`:

```yaml
ticket_id: NC-DS-XXX
status: PENDING_REVIEW         # PENDING_REVIEW | APPROVED | REJECTED
timestamp: "2026-04-13THH:MM:SS-03:00"
agent_port: XXXXX

lines_added: N
files_modified:
  - path/relativo/NC-TIPO-SIGLA-NUM-arquivo.py

summary: |
  1-3 linhas do que foi feito.

ajustes_aplicados:             # obrigatrio  @SYNTHESIS ajustes do ticket
  - "Backoff exponencial implementado"

lessons_learned:               # erros/descobertas desta implementao
  - "ruamel no disponvel  instalar antes"

deps_missing: []               # libs que falharam no STEP-0
ruff_violations_found: 0       # quantas violaes antes do --fix

metrics:
  ruff_check: PASS
  py_compile: PASS
  import_smoke_test: PASS
  write_zone_respected: true
  locks_respected: true
  min_80_lines: true

errors: []
warnings: []

checklist_r20:
  naming_convention: true
  no_print_statements: true
  ajustes_synthesis_applied: true
  handoff_yaml_complete: true
```

---

##  SSOT  Leia na ordem antes de qualquer trabalho

| # | Arquivo | Local | Propsito |
|---|---|---|---|
| 1 | `NC-NAM-FR-001-naming-convention.md` | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/` | Mapa + Naming + Changelog |
| 1a-1d | `NC-NAM-FR-001a/b/c/d-*.md` | idem | Sub-registros tools/lobes/config/prompts |
| 2 | `NC-TODO-FR-001-project-roadmap-consolidated.md` | idem | Roadmap macro |
| 3 | `NC-TODO-DS-001-roadmap-pre-mcp.md` | idem | **Sprint ativo PR-MCP** |
| 4 | `NC-BOOT-FR-001-system-manifest.md` | `DIR-BOOT-FR-001-bootup-main/` | Estado ao boot |
| 5 | `NC-SOP-FR-001-session-startup.md` | `DIR-DOC-FR-001-docs-main/` | SOP completo de sesso |
| 6 | `NC-CFG-DS-005-step0-environment.md` | `DIR-DS-000-agent-config/` | STEP-0 v2 |
| 7 | `NC-DOC-DS-001-prompt-template-sample.md` | `DIR-DS-000-agent-config/` | Template de prompt para agentes |
| 8 | `NC-LBE-FR-QUALITY-001-env-quality.mdc` | `01_neocortex_framework/lobes/` | Lobe qualidade + regresses |
| 9 | `NC-HANDOFF-TEMPLATE.yaml` | `DIR-DS-000-agent-config/` | Template obrigatrio de handoff |
| 10 | `artifact_catalog.json` + `.md` | `DIR-DOC-FR-001-docs-main/` | Catlogo semntico de artefatos (253 PY + 207 YAML) |

---

##  Estrutura de Pastas Raiz

```
TURBOQUANT_V42/
 01_neocortex_framework/
    neocortex/
       mcp/server.py         @LOCK
       mcp/sub_server.py     @LOCK
       mcp/tools/            NC-TOOL-FR-000036 (37 tools fsicos)
       core/services/        NC-SVC-FR-001012 (12 servios )
       core/utils/           NC-UTL-FR-001004 
       core/hooks/           NC-HK-FR-001/002 ( DS-A)
       core/config/          NC-CFG-FR-002 NC-CFG-FR-004( DS-A)
       core/review/          NC-REV-FR-001 ( DS-B)
    DIR-DOC-FR-001-docs-main/   SSOTs + artifact_catalog
    DIR-TMP-FR-001-templates-main/  Templates NC-TOOL
    scripts/                  NC-SCR-FR-001015
 DIR-ARC-FR-001-archive-main/  Obsoletos (nunca deletar)
 DIR-BOOT-FR-001-bootup-main/  Boot manifest
 DIR-DS-000-agent-config/      Config + Prompts DS + picoclaw config
 DIR-DS-001-tickets/           Tickets input
 DIR-DS-002-audit-logs/        Handoffs output ( 83 YAMLs  arquivar!)
 DIR-DS-003-entry-locks/       Entry locks ativos
 DIR-DS-004-patches/           Patches pendentes
 DIR-RES-CC-001-claude-leak-workzone/  Anlise Claude Code (fase pesquisa)
 data/                         Dados brutos
 .agents/rules/neocortexrules.md  NICO ponto cannico de regras
 NC-PROMPT-FR-001-master-context.md   ESTE ARQUIVO
```

---

##  Arquitetura de Agentes

```
T0 = Antigravity (Gemini/Claude)  Orquestra, valida handoffs, atualiza SSOT+BOOT+LOBE
T1 = DeepSeek-chat (OpenCode)     Executa tickets, gera handoffs YAML
T2/T3 = Qwen local                Futuro (MCP offline)
```

**Regra:** T0 valida TODA entrega antes de marcar %DONE. T1 nunca atualiza SSOT.

##  CONTEXTO DE RETOMADA (Reaquecimento)
*Use este bloco compacto para nova janela de 100k. Cole antes da ao imediata.*

```markdown
[NC-PROMPT] [CICLO:1] [REAQUECIMENTO]
Voc est entrando em uma sesso de trabalho no projeto NeoCortex Framework. O contexto abaixo foi gerado automaticamente pelo script NC-SCR-FR-014-end-of-cycle.ps1 e contm as informaes mnimas necessrias para continuidade.

### CONTEXTO DE RETOMADA (Gerado em {DATA})
**Status:** {PENDENTES} handoffs pendentes | {PY} PY + {YAML} YAML catalogados | Catlogo atualizado h {HORAS}h
**Problemas Crticos Ativos:**
- Plano de renomeao (87 arquivos) aguardando validao de escopo/atualidade
- Testes VectorEngine com falhas (mock/API)  documentado em NC-DS-XXX
- Discrepncia de escopo: plano atual (87) vs. auditoria (178)

**Artefatos-Chave:**
| Arquivo | Funo |
|---------|--------|
| `renaming_plan.yaml` | Plano atual com 87 arquivos |
| `artifact_catalog.json` | Mapa de dependncias de todos scripts |
| `rename_impact_analysis.json` | Impacto previsto das renomeaes |
| `DIR-DS-002-audit-logs/` | Handoffs pendentes: {LISTA} |

**ltima Ao Concluda:** {DESCRIO DA LTIMA AO}

###  INSTRUES PARA ESTA SESSO:
O usurio informar qual **foco de trabalho** deseja para hoje. Com base nisso, voc dever:
1. **Ciclo 1 (Anlise):** Consultar os artefatos-chave listados acima e fornecer um resumo executivo do estado atual.
2. **Ciclo 2 (Ao):** Propor e executar (se autorizado) os prximos passos lgicos, sempre documentando as aes em formato de handoff YAML ao final.
3. **Ciclo 3 (Fechamento):** Ao final da sesso, sugerir executar `NC-SCR-FR-014-end-of-cycle.ps1 -AutoUpdate -UpdateCatalog` para gerar novo bloco de retomada.

**Observao:** Mantenha respostas concisas e acionveis, evitando explicaes redundantes sobre o framework.

[FIM DO BLOCO DE REAQUECIMENTO]
```

---

---
\n## STATUS (2026-04-16 23:38) — Ciclo 3 Concluído, Protocolo T0 Implementado

**MCP: STARTED (port 8765 not responding)** | **Mission Control: ACTIVE (:3000)** | **PicoClaw: STOPPED** | **Handoffs Pendentes: 0** | **Catalog: 529 PY, 403 YAML**

### Sessao 2026-04-16 — Ciclo 1 Conclusão e Handoffs
| Ticket | Status | Notas |
|---|---|---|
| NC-DS-099 (FR-034) | APPROVED | Dry-run middleware integration |
| NC-DS-100 (FR-035) | APPROVED | Task broker persistence |
| NC-DS-101 (FR-036) | APPROVED | Picoclaw tool |
| NC-DS-102 (FR-037) | APPROVED | Hooks tool |
| NC-DS-108 (FR-043) | FAILED | Not implemented |
| NC-DS-110 (FR-045) | FAILED | Not implemented |
| NC-DS-114 (RETRO) | APPROVED | Retrospective handoff |
| NC-DS-116 (T0) | APPROVED | Protocolo auditoria handoff |

### Roteiro Atual
`
Ciclo 1: ✅ Concluído (baseline estabelecida)
Ciclo 2: ✅ Protocolo T0 integrado ao NC-WF-001 v3.6
Ciclo 3: ✅ Executado (catalog, bootup, sanitization, checkpoint)
PRÓXIMO: Diagnóstico servidor MCP (port 8765) + Health wrapper (8766)
`

### Ciclo 3 (Encerramento) Executado — 2026-04-16
- YAML Sanitization: ✅ OK (0 problemas críticos)
- Catalog Update: ✅ OK (529 PYs / 403 YAMLs)
- Bootup Sync: ✅ OK (frentes atualizadas, tickets críticos listados)
- Handoffs Auditados: ✅ Protocolo T0 aplicado (py_compile, ruff)
- SSOT Changelog: ✅ Atualizado com entrada 2026-04-16
- Lobe Population: ✅ 7 lobos atualizados via NC-SCR-FR-001
- Checkpoint Criado: ✅ CP-SESSION-END-20260416-233755-6faee8c8
- NC-PROMPT STATUS: ✅ Atualizado (este bloco)

### Pendente proxima sessao
- Diagnosticar servidor MCP (porta 8765 não responde)
- Iniciar health wrapper (:8766) via NC-SCR-FR-098
- Atualizar roadmaps FR/DS com %DONE para tickets concluídos
- Executar smoke test completo das ferramentas MCP
- Validar loop Antigravity → Core → PicoClaw → OpenCode (quando PicoClaw ativo)

