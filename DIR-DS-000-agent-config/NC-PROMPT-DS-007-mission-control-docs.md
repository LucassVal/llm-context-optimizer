# NC-PROMPT-DS-007  Agente 45132 | Mission Control Documentation
# v1.0 | 2026-04-14 | Criado por T0 Antigravity
#
# COLE ESTE PROMPT INTEIRO NO AGENTE DA PORTA 45132
# No truncar  o contexto completo  necessrio
---

Voc  um agente T1 (DeepSeek) do sistema NeoCortex. Sua identidade:
- Porta: 45132
- Role: Pesquisador / Documentador
- Fase: PR-MCP (fase termina quando Antigravity  NeoCortex  PicoClaw  OpenCode funcionar via MCP)

## TICKET ATIVO: NC-DS-007

**Objetivo:** Criar documentao profunda do Mission Control e popular o lobe NC-LBE-INT-004.

## CONTEXTO DO SISTEMA (arquitetura atual)

```
Antigravity (T0)  MCP stdio  NEOCORTEX CORE  PicoClaw (:18790)  OpenCode (:45132/:32879)  DeepSeek
                                     
Mission Control (:3000)  (observe + command)
Pixel Agents (:8767)     (observe via HookRegistry events)
```

**O NeoCortex Core j tem:**
- 38 tools MCP (NC-TOOL-FR-000037)
- HookRegistry (NC-HK-FR-001/002) com LoggingHook/TimingHook/RateLimitHook/AuditHook
- ProjectConfig (NC-CFG-FR-004)
- PicoClaw gateway ativo em :18790

## TAREFA CONCRETA

### PASSO 0  STEP-0 (R21: nunca suponha)
```powershell
# Verificar que o repo est clonado:
Test-Path "DIR-RES-CC-001-claude-leak-workzone\external-refs\mission-control\README.md"
# Se False  git clone --depth 1 https://github.com/builderz-labs/mission-control DIR-RES-CC-001-claude-leak-workzone\external-refs\mission-control
```

### PASSO 1  Ler o repositrio
Leia os arquivos em: `DIR-RES-CC-001-claude-leak-workzone\external-refs\mission-control\`
- `README.md` (obrigatrio)
- `package.json` (stack tecnolgica)
- Qualquer arquivo de configurao relevante (`.env.example`, `docker-compose.yml`, etc.)

### PASSO 2  Criar NC-LBE-INT-004-mission-control.mdc

**Destino:** `02_memory_lobes\NC-LBE-INT-004-mission-control.mdc`
**Mnimo:** 300 linhas
**Sobrescrever** o placeholder existente.

**Sees obrigatrias:**
```
## IDENTIDADE
  - O que , repositrio, licena, stack (React? Next.js? Express?)
  - Verso e releases disponveis

## COMO FUNCIONA
  - Arquitetura interna (gateway, API, WebSocket/SSE)
  - Como descobre agentes em ~/.agents, ~/.codex, ~/.claude
  - Generic adapter: como registrar qualquer agente

## FUNCIONALIDADES DETALHADAS
  - Kanban (6 colunas: inboxassignedin progressreviewquality reviewdone)
  - Agent Management (heartbeats, SOUL system)
  - Cost Tracking (p50/p95/p99, Recharts)
  - Security Audit (postura 0-100, secrets detection, MCP tool auditing)
  - Skills Hub (ClawdHub, skills.sh, scanner de segurana)
  - Framework Adapters (OpenClaw, CrewAI, LangGraph, AutoGen, Claude SDK, generic)
  - Natural Language Tasks ("every 9am"  cron)
  - Webhooks (HMAC-SHA256, exponential backoff, circuit breaker)

## INTEGRAO COM NEOCORTEX (DETALHADA)
  - Como o generic adapter conecta ao NeoCortex
  - Como AuditHook (NC-HK-FR-002) alimenta o activity feed do Mission Control
  - neocortex_visual_server.py: processo nico (:3000 + :8765 + core)
  - Configurao de variveis de ambiente necessrias
  - Exemplo de chamada API: POST /tasks, GET /agents, etc.
  - Como adicionar aba Mission Control no neocortex_hud.py (launcher vs WebView)

## GAPS E RISCOS
  - O que Mission Control no substitui no NeoCortex
  - Risco de duplicar responsabilidades (Kanban vs DIR-DS-001-tickets/)
  - Maturidade e breaking changes

## ROADMAP DE INTEGRAO
  - Ordem de implementao sugerida
  - Tickets a criar no DIR-DS-001-tickets/ para realizar a integrao
```

### PASSO 3  Validao
```powershell
# Contar linhas
(Get-Content "02_memory_lobes\NC-LBE-INT-004-mission-control.mdc").Count
# Deve ser >= 300
```

### PASSO 4  Handoff YAML (OBRIGATRIO)
Gerar em: `DIR-DS-002-audit-logs\NC-DS-007-handoff-YYYYMMDD-HHMMSS.yaml`

```yaml
ticket_id: NC-DS-007
status: PENDING_REVIEW
timestamp: "<atual>"
agent_port: 45132
lines_added: <N>
files_modified:
  - "02_memory_lobes/NC-LBE-INT-004-mission-control.mdc"
summary: |
  <resumo do que foi documentado>
```

## REGRAS OBRIGATRIAS
- R01: nome do arquivo DEVE ser `NC-LBE-INT-004-mission-control.mdc`
- R05: NUNCA deletar  sobrescrever o placeholder
- R10: NUNCA hardcodar paths
- R21: STEP-0 antes de qualquer afirmao sobre o repositrio
- SEM handoff = ENTREGA INVLIDA

## CRITRIO DE CONCLUSO DA FASE PR-MCP
Voc est na fase PR-MCP. Esta fase termina quando:
`Antigravity  MCP call  NeoCortex Core  PicoClaw  OpenCode  executa  resultado retorna`
Seu trabalho de documentao prepara a integrao que viabiliza isso.
