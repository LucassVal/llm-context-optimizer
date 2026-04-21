# PROMPT AGENT 1  Sub-lobes CC Leak + Pesquisa (Hooks / Worker / Review)
# Cole este prompt em uma JANELA LIMPA (nova sesso sem contexto anterior)
# Data: 2026-04-12 | Leia este arquivo inteiro antes de comear

---

## CONTEXTO OBRIGATRIO  Leia estes arquivos ANTES de qualquer ao

1. `01_neocortex_framework/lobes/NC-LBE-DS-003-worker-patterns.mdc`  estado atual do sistema
2. `DIR-RES-CC-001-claude-leak-workzone/NC-STR-CC-001-master-strategy.md`  anlise mestre CC leak
3. `DIR-RES-CC-001-claude-leak-workzone/analysis-session-b/NC-ANA-CC-005-plugins-deep.md`  plugins CC
4. `DIR-RES-CC-001-claude-leak-workzone/analysis-session-b/NC-ANA-CC-004-competitive-intel.md`
5. `01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-LBE-CC-001-claude-leak-master.mdc`

---

## PARTE 1  Criar Sub-Lobes CC Leak (conhecimento fixado em pedra)

Crie os seguintes arquivos em `01_neocortex_framework/lobes/cc-leak/`:

### 1A. NC-LBE-CC-002-hooks-system.mdc
Documente extensivamente (mnimo 150 linhas):
- Como o sistema de hooks funciona no CC (hookify, security-guidance, PreToolUse, PostToolUse)
- Estrutura dos arquivos hooks.json + scripts Python externos
- Eventos disponveis: tool_called, file_written, bash_executed, Stop
- Padro de contexto passado via stdin/env para os scripts
- Como o security-guidance usa hooks para anlise de risco
- Deciso de design NeoCortex: HookRegistry  MentorHooks/GuardHooks
- Mapping: hookify  `NC-HK-FR-001-hook-registry.py`
- Exemplos de regras YAML para guards de SSOT e @LOCKS

### 1B. NC-LBE-CC-003-persistent-worker.mdc
Documente extensivamente (mnimo 120 linhas):
- Como ralph-wiggum funciona no CC (loop while-true, paradas, condies)
- Flags: DAEMON, PROACTIVE, BRIDGE_MODE, COORDINATOR_MODE
- Funes: maybeActivateProactive(), maybeActivateBrief()
- EXIT_CODE_PERMANENT = 42 (errors no-retentveis)
- Deciso de design NeoCortex: ralph-wiggum  PersistentWorker
- Mapping: `NC-PROMPT-DS-003-persistent-worker.md`
- Condies de parada: fila vazia 3x consecutivas

### 1C. NC-LBE-CC-004-confidence-review.mdc
Documente extensivamente (mnimo 120 linhas):
- Como code-review plugin funciona no CC (score 0-100, mltiplos agentes paralelos)
- Validadores usados: naming, compile, barreiras, forbidden zones, SSOT
- Thresholds: >80 aprovao automtica, <50 rejeio, 50-80 manual
- Deciso de design NeoCortex:  ConfidenceReviewService
- Mapping: `NC-REV-FR-001-confidence-review.py`
- Substituio do batch_approve.py atual

---

## PARTE 2  Pesquisa Internet (validao e alternativas)

Para cada palavra-chave abaixo, pesquise na internet e traga 3 pontos.
Formato obrigatrio por item:
```
### [PALAVRA-CHAVE]
Fonte: [URL ou referncia]
 Faz sentido? [nossa abordagem vs mercado]
 Alternativa melhor? [lib, padro, framework, com link]
 Como melhorar? [mudana especfica no nosso design]
```

**Palavras-chave para pesquisar:**

SOBRE O QUE J TEMOS:
- "python hook registry event system"
- "MCP tool hook pre post execution python"
- "plugin system python auto-discovery"
- "atomic file locking python concurrent agents"
- "YAML state machine python FSM"
- "python metrics collector tokens cost tracking"

SOBRE O QUE QUEREMOS IMPLEMENTAR (NC-DS-029031/034):
- "persistent worker loop python AI agent"
- "AI agent while true loop task queue"
- "session statistics gamification developer tools"
- "confidence score code review automated validation"
- "pre-commit hook security policy enforcement python"

Compile os resultados em:
`DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-001-validation-hooks-worker-review.md`
(mnimo 200 linhas)

---

## PARTE 3  Renomear Referncias CC nos Seus Lobes

Nos arquivos que VOC criou (1A, 1B, 1C), garanta que:
- NUNCA aparece "ralph-wiggum"  use "PersistentWorker"
- NUNCA aparece "hookify"  use "MentorHooks" ou "GuardHooks"
- NUNCA aparece "Buddy" sozinho  use "SessionMate"
- NUNCA aparece "KAIROS"  use "PulseDaemon" ou "TickEngine"
- NUNCA aparece "Bridge Mode"  use "A2AGateway"
- Manter apenas como referncia histrica entre aspas: `"ralph-wiggum (CC)  PersistentWorker (NC)"`

---

## ENTREGA

Gere handoff: `DIR-DS-002-audit-logs/NC-DS-041-handoff-{YYYYMMDD-HHMMSS}.yaml`
```yaml
ticket_id: NC-DS-041
status: PENDING_REVIEW
lines_added: [total real das 3 partes]
files_created:
  - 01_neocortex_framework/lobes/cc-leak/NC-LBE-CC-002-hooks-system.mdc
  - 01_neocortex_framework/lobes/cc-leak/NC-LBE-CC-003-persistent-worker.mdc
  - 01_neocortex_framework/lobes/cc-leak/NC-LBE-CC-004-confidence-review.mdc
  - DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-001-validation-hooks-worker-review.md
```

## REGRAS
- NO toque em: server.py, sub_server.py, NC-NAM-FR-001 (@LOCKS)
- NO crie arquivos .py  apenas .mdc e .md
- Janela 100k: se contexto ficar pesado, salve o handoff antes de compactar
