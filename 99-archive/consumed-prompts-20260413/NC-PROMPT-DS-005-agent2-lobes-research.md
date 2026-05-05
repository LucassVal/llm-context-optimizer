# PROMPT AGENT 2  Sub-lobes CC Anlises + Pesquisa (Buddy / Config / Plugin)
# Cole este prompt em uma JANELA LIMPA (nova sesso sem contexto anterior)
# Data: 2026-04-12 | Leia este arquivo inteiro antes de comear

---

## CONTEXTO OBRIGATRIO  Leia estes arquivos ANTES de qualquer ao

1. `01_neocortex_framework/lobes/NC-LBE-DS-003-worker-patterns.mdc`  estado atual
2. `DIR-RES-CC-001-claude-leak-workzone/NC-STR-CC-001-master-strategy.md`  sees B, C, D.2/D.3/D.4/D.5
3. `DIR-RES-CC-001-claude-leak-workzone/analysis-session-b/NC-ANA-CC-004-competitive-intel.md`
4. `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-006-metrics-collector.py`  base para SessionMate
5. `01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-LBE-CC-001-claude-leak-master.mdc`

---

## PARTE 1  Criar Sub-Lobes CC Leak (conhecimento fixado em pedra)

Crie os seguintes arquivos em `01_neocortex_framework/lobes/cc-leak/`:

### 2A. NC-LBE-CC-005-session-mate.mdc
Documente extensivamente (mnimo 120 linhas):
- Como Buddy funciona no CC (sprites ASCII, gamificao, stats de sesso)
- Mtricas coletadas: tokens gastos, tasks concludas, taxa de sucesso, XP
- Output visual: ` 3 tasks |  $0.42 |  94% sucesso`
- Deciso de design NeoCortex: Buddy  SessionMate
- Mapping: `NC-SVC-FR-009-session-buddy.py`
- Integrao com NC-SVC-FR-006-metrics-collector.py (j existe)
- API proposta: start_session(), record_task(success), end_session()  str

### 2B. NC-LBE-CC-006-project-config.mdc
Documente extensivamente (mnimo 120 linhas):
- Como `.claude/` funciona no CC (config por projeto, override global)
- Subdiretrios: hooks/, commands/, plugins/
- Precedncia: local > global
- Deciso de design NeoCortex: .claude/  .nc/
- Mapping: `NC-CFG-FR-004-project-loader.py`
- Exemplo de estrutura `.nc/config.yaml`
- Como mesclar com neocortex_config.yaml global (sem quebrar @LOCKS)

### 2C. NC-LBE-CC-007-plugin-template.mdc
Documente extensivamente (mnimo 130 linhas):
- Como plugin-dev funciona no CC (estrutura .claude-plugin/, auto-discovery)
- Componentes: metadata JSON, commands/*.md, hooks/*.py, README.md
- Padro de nomenclatura: `/plugin[:subcomando]`
- Deciso de design NeoCortex:  NC-TOOL-FR-TEMPLATE/
- Nomenclatura NeoCortex: `/nc-<comando>`
- Mapping: `NC-SCR-FR-012-new-tool.py` (scaffolding)
- Estrutura completa do template com todos os arquivos necessrios

---

## PARTE 2  Pesquisa Internet (validao e alternativas)

Para cada palavra-chave, pesquise na internet e traga 3 pontos.
Formato obrigatrio:
```
### [PALAVRA-CHAVE]
Fonte: [URL ou referncia]
 Faz sentido? [nossa abordagem vs mercado]
 Alternativa melhor? [lib, padro, framework, com link]
 Como melhorar? [mudana especfica no nosso design]
```

SOBRE O QUE J TEMOS:
- "python event bus publish subscribe pattern"
- "configparser YAML merge hierarchy python"
- "python health check endpoint FastAPI lightweight"
- "savepoint snapshot before write python"
- "python cache service TTL in-memory"

SOBRE O QUE QUEREMOS IMPLEMENTAR (NC-DS-030/032/033/037):
- "session statistics developer gamification terminal"
- "per-project configuration override global python"
- "plugin system scaffolding template generator python CLI"
- "feature flag service python TTL cache"
- "python project configuration .dotfile directory"

Compile em:
`DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-002-validation-buddy-config-plugin.md`
(mnimo 200 linhas)

---

## PARTE 3  Atualizar NC-ANA-CC-004 com Nomes NeoCortex

Leia: `DIR-RES-CC-001-claude-leak-workzone/analysis-session-b/NC-ANA-CC-004-competitive-intel.md`

Adicione uma seo no FINAL do documento:
```
## G. Mapeamento de Nomes CC  NeoCortex

| Nome Original (CC) | Nome NeoCortex | Arquivo Mapping |
|---|---|---|
| KAIROS | PulseDaemon / TickEngine | NC-SVC-FR-010-kairos-service.py |
| ralph-wiggum | PersistentWorker | NC-PROMPT-DS-003-persistent-worker.md |
| hookify / security-guidance | MentorHooks / GuardHooks | NC-HK-FR-001-hook-registry.py |
| Buddy | SessionMate | NC-SVC-FR-009-session-buddy.py |
| Bridge Mode | A2AGateway | NC-SVC-FR-011-a2a-gateway.py |
| ULTRAPLAN | BatchOrchestrator | (futuro - ps-MCP) |
| Coordinator Mode | OrchestratorMode | (futuro - ps-MCP) |
| plugin-dev / marketplace | NC-TOOL-FR-TEMPLATE | NC-SCR-FR-012-new-tool.py |
| .claude/ | .nc/ | NC-CFG-FR-004-project-loader.py |
| code-review plugin | ConfidenceReviewService | NC-REV-FR-001-confidence-review.py |
```

NO modifique o restante do documento  apenas adicione esta seo ao final.

---

## ENTREGA

Gere handoff: `DIR-DS-002-audit-logs/NC-DS-042-handoff-{YYYYMMDD-HHMMSS}.yaml`
```yaml
ticket_id: NC-DS-042
status: PENDING_REVIEW
lines_added: [total real das 3 partes]
files_created:
  - 01_neocortex_framework/lobes/cc-leak/NC-LBE-CC-005-session-mate.mdc
  - 01_neocortex_framework/lobes/cc-leak/NC-LBE-CC-006-project-config.mdc
  - 01_neocortex_framework/lobes/cc-leak/NC-LBE-CC-007-plugin-template.mdc
  - DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-002-validation-buddy-config-plugin.md
files_modified:
  - DIR-RES-CC-001-claude-leak-workzone/analysis-session-b/NC-ANA-CC-004-competitive-intel.md
```

## REGRAS
- NO toque em: server.py, sub_server.py, NC-NAM-FR-001 (@LOCKS)
- NO crie arquivos .py  apenas .mdc e .md
- Janela 100k: se contexto ficar pesado, salve o handoff antes de compactar
