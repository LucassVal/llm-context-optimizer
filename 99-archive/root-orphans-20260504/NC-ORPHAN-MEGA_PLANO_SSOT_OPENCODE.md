# MEGA PLANO DE IMPLEMENTAÇÃO — NeoCortex × OpenCode
**Cruzamento SSOT + OpenCode + Ciclos 1-5**  
**Data:** 2026-05-03 | **Hash:** `MEGA-PLAN-v1.0-20260503`

---

## ESTADO ATUAL DO SISTEMA (APÓS CICLOS 1-5)

| Métrica | Valor | Status |
|---------|-------|--------|
| Arquivos físicos mapeados | 503 | ✅ |
| Conformidade NC- (nomenclatura) | **60.8%** | 🔴 (meta >80%) |
| SSOT entries | 273 | ✅ |
| Arquivos fantasmas (sem SSOT) | **166** | 🔴 |
| Links mortos (SSOT desatualizado) | **177** | 🔴 |
| Conformidade governança 20 regras | 75% (15/20) | 🟡 |
| Seções OpenCode documentadas | 34/34 (100%) | ✅ |
| Knowledge store entries | 41 | ✅ |
| Regras IA formalizadas | 20/20 | ✅ |

---

## FASE 0 — FUNDAÇÃO: SSOT CLEANUP (URGENTE)

### 🔴 0.1 — Resolver 166 Arquivos Fantasmas
> **Problema:** 166 arquivos existem materialmente mas não estão no SSOT (NC-NAM-FR-001)

| # | Ação | Script | Prioridade |
|---|------|--------|------------|
| 0.1.1 | Mapear todos os fantasmas por diretório | `NC-SCR-FR-023-ssot-auditor.py` | Imediata |
| 0.1.2 | Gerar entradas NC-NAM-FR-001 para cada fantasma | `NC-SCR-FR-065-rename-impact-analyzer.py` | Alta |
| 0.1.3 | Validar nomenclatura NC- para todos os fantasmas | `NC-SCR-FR-080-governance-auditor.py` | Alta |
| 0.1.4 | Executar genealogy-injector --execute (211 arquivos) | `NC-SCR-FR-075-genealogy-injector.py` | Alta |

### 🔴 0.2 — Resolver 177 Links Mortos
> **Problema:** 177 entradas SSOT não existem mais em disco

| # | Ação | Ferramenta | Prioridade |
|---|------|------------|------------|
| 0.2.1 | Auditar cada link morto (existe em backup?) | SSOT Auditor | Imediata |
| 0.2.2 | Remover entradas obsoletas do SSOT | Manual + Script | Alta |
| 0.2.3 | Restaurar do archive se necessário | DIR-ARC-FR-001 | Média |

### 🔴 0.3 — Subir Conformidade NC- de 60.8% para >80%
> **Problema:** Nomenclatura violada em 39.2% dos arquivos

| # | Ação | Script | Prioridade |
|---|------|--------|------------|
| 0.3.1 | Identificar violações NC- mais comuns | `NC-SCR-FR-080` | Imediata |
| 0.3.2 | Renomear arquivos fora do padrão | `NC-SCR-FR-065` | Alta |
| 0.3.3 | Validar 100% dos arquivos renomeados | `NC-SCR-FR-023` | Alta |

---

## FASE 1 — INTEGRAÇÃO OPENCODE + NEOCORTEX (10 PROJETOS)

### 🟡 1.1 — Plugin OpenCode: NeoCortex Gateway
> **Base:** OpenCode Plugin System (`.opencode/plugins/` + npm)

| # | Componente | Fonte OpenCode | Arquivo NeoCortex |
|---|-----------|----------------|-------------------|
| 1.1.1 | Registrar tools MCP no OpenCode | `POST /mcp` (add dinâmico) | `NC-HUB-FR-001-mcp-hub.py` |
| 1.1.2 | Expor NeoCortex tools como plugins | `tool.extend()` | `NC-TOOL-FR-*` series |
| 1.1.3 | HookRegistry ↔ OpenCode hooks | `tool.execute.before/after` | `NC-HK-FR-001-hook-registry.py` |
| 1.1.4 | Packaging npm do plugin | `opencode.json` → `plugin: []` | `package.json` + publish |

**Estimativa:** 350 linhas | **Dependência:** Fase 0.1, 0.2

### 🟡 1.2 — SessionBridge: OpenCode ↔ NeoCortex Sessions
> **Base:** OpenCode Session API + NeoCortex SessionBuddy

| # | Funcionalidade | API OpenCode | Serviço NeoCortex |
|---|---------------|-------------|-------------------|
| 1.2.1 | Sync session create | `POST /session` | `NC-SVC-FR-009-session-buddy.py` |
| 1.2.2 | Inject context via noReply | `session.prompt({ noReply: true })` | CortexService |
| 1.2.3 | Compactação customizada | `experimental.session.compacting` hook | CascadeConsolidator |
| 1.2.4 | Child session → subagent | `GET /session/:id/children` | Orchestration tools |

**Estimativa:** 400 linhas | **Dependência:** 1.1

### 🟡 1.3 — Permission Guard: OpenCode Permissions → NeoCortex Policy
> **Base:** OpenCode Permissions System + NeoCortex PolicyLoader

| # | Mapeamento | OpenCode Permission | NeoCortex Policy |
|---|-----------|-------------------|------------------|
| 1.3.1 | Read guard | `permission.read` | `NC-SEC-FR-001-atomic-locks.yaml` |
| 1.3.2 | Edit guard | `permission.edit` | Write Zones (`NC-CFG-FR-002`) |
| 1.3.3 | Bash guard | `permission.bash` glob patterns | PolicyLoader |
| 1.3.4 | External directory | `permission.external_directory` | SecurityService |

**Estimativa:** 250 linhas | **Dependência:** Nenhuma

### 🟡 1.4 — MCP Server Registry: OpenCode MCP → NeoCortex Tools
> **Base:** OpenCode MCP Servers (local + remote + OAuth)

| # | Funcionalidade | Fonte |
|---|---------------|-------|
| 1.4.1 | Listar MCPs via `/mcp` | OpenCode Server API |
| 1.4.2 | Registrar NeoCortex como MCP local | `type: "local", command: ["python", "hub.py"]` |
| 1.4.3 | OAuth flow para remote MCPs | OpenCode OAuth handler |
| 1.4.4 | Per-agent MCP enable/disable | `tools: { "mymcp_*": true }` |

**Estimativa:** 300 linhas | **Dependência:** 1.1

### 🟡 1.5 — AGENTS.md Generator: NeoCortex-aware Rules
> **Base:** OpenCode Rules (AGENTS.md + instructions)

| # | Funcionalidade | Descrição |
|---|---------------|-----------|
| 1.5.1 | `/init` customizado com contexto NeoCortex | AGENTS.md + referências @SSOT |
| 1.5.2 | Instruções remotas do SSOT | `instructions: ["url://ssot"]` |
| 1.5.3 | Lazy loading de lobes via `@` references | AGENTS.md com `@$FRONTAL` etc |
| 1.5.4 | Rules de governança como instruções | `instructions: ["NC-GOV-FR-003.md"]` |

**Estimativa:** 200 linhas | **Dependência:** Fase 0

### 🟡 1.6 — OpenCode Go/Zen Integration
> **Base:** OpenCode Zen models + NeoCortex LLM Router

| # | Funcionalidade | OpenCode | NeoCortex |
|---|---------------|----------|-----------|
| 1.6.1 | Auto-conectar OpenCode Zen | `/connect` → opencode.ai/auth | `NC-SUPER-005-llm-router.py` |
| 1.6.2 | Tier mapping (T0/T2/T3 → models) | Zen model list | LiteLLM Router |
| 1.6.3 | Budget tracking via Zen | Zen usage limits | BudgetService |
| 1.6.4 | Fallback para Go (modelos open) | Go subscription | T2 Courier |

**Estimativa:** 200 linhas | **Dependência:** Nenhuma

### 🟡 1.7 — ACP Agent: NeoCortex as ACP Provider
> **Base:** OpenCode ACP Support (`opencode acp`)

| # | Funcionalidade | Descrição |
|---|---------------|-----------|
| 1.7.1 | Expor NeoCortex como ACP agent | `opencode acp` ← NeoCortex orchestrator |
| 1.7.2 | Integração com Zed | `agent_servers: { "NeoCortex": { command: "opencode", args: ["acp"] } }` |
| 1.7.3 | Integração com JetBrains | `acp.json` → agent_servers |
| 1.7.4 | Integração com Neovim (Avante) | `acp_providers = { opencode = { command = "opencode", args = { "acp" } } }` |

**Estimativa:** 150 linhas | **Dependência:** 1.1

### 🟡 1.8 — Agent Skills Bridge
> **Base:** OpenCode Agent Skills (SKILL.md) + NeoCortex Lobes

| # | Funcionalidade | SKILL.md | Lobe equivalente |
|---|---------------|----------|------------------|
| 1.8.1 | Mapear lobes → skills | `.opencode/skills/<name>/SKILL.md` | `02_memory_lobes/<lobe>/` |
| 1.8.2 | Skill discovery via UBL | `@$FRONTAL` → `skill({name: "frontal"})` | Léxico |
| 1.8.3 | Permission sync | `permission.skill: { "*": "ask" }` | SecurityService |

**Estimativa:** 150 linhas | **Dependência:** Fase 0, 1.5

### 🟡 1.9 — Custom Tools Exporter
> **Base:** OpenCode Custom Tools (`.opencode/tools/`)

| # | Funcionalidade | Descrição |
|---|---------------|-----------|
| 1.9.1 | Exportar NC-TOOL-FR-* como custom tools | `tool()` helper → `.opencode/tools/` |
| 1.9.2 | Wrapper para Python tools | `Bun.$` → `python3 script.py` |
| 1.9.3 | Context enrichment | `context.directory`, `context.worktree` |

**Estimativa:** 200 linhas | **Dependência:** 1.1

### 🟡 1.10 — LSP Integration
> **Base:** OpenCode LSP Servers + NeoCortex Code Intelligence

| # | Funcionalidade | Descrição |
|---|---------------|-----------|
| 1.10.1 | Pyright LSP para Python | built-in no OpenCode |
| 1.10.2 | Ruff formatter para Python | built-in no OpenCode |
| 1.10.3 | Diagnostics → Governance auditor | LSP diagnostics → violation log |
| 1.10.4 | Custom LSP para NC- validation | Valida nomenclatura via LSP |

**Estimativa:** 300 linhas | **Dependência:** Nenhuma

---

## FASE 2 — GOVERNANÇA OPENCODE (5 PROJETOS)

### 🟠 2.1 — GitHub Automation Workflow
> **Base:** OpenCode GitHub Integration + NeoCortex Tickets

```yaml
# .github/workflows/opencode-neocortex.yml
name: opencode-neocortex
on:
  issue_comment:
    types: [created]
jobs:
  opencode:
    if: contains(github.event.comment.body, '/oc')
    steps:
      - uses: anomalyco/opencode/github@latest
        with:
          model: opencode/<tier-model>
          prompt: |
            Use NeoCortex governance tools:
            - @GOV rule.list → validar conformidade
            - @MEM search → buscar contexto relevante
            - @ORCH task.execute → delegar para T2/T3
```

| # | Componente | Status |
|---|-----------|--------|
| 2.1.1 | Workflow YAML template | 🔴 Pendente |
| 2.1.2 | SSOT-aware prompt | 🔴 Pendente |
| 2.1.3 | Auto-ticket on issue | 🔴 Pendente |

**Estimativa:** 100 linhas | **Dependência:** Fase 1.1, 1.2

### 🟠 2.2 — GitLab CI Integration
> **Base:** OpenCode GitLab Integration

```yaml
include:
  - component: $CI_SERVER_FQDN/nagyv/gitlab-opencode/opencode@2
    inputs:
      message: "@opencode review this MR using NeoCortex governance"
```

**Estimativa:** 80 linhas | **Dependência:** Fase 1.1

### 🟠 2.3 — Enterprise Config (MDM)
> **Base:** OpenCode Enterprise + OpenCode Config (managed .mobileconfig)

| # | Funcionalidade | Descrição |
|---|---------------|-----------|
| 2.3.1 | Managed `.mobileconfig` para NeoCortex | SSOT como remote config `.well-known/opencode` |
| 2.3.2 | Disable share for compliance | `share: "disabled"` |
| 2.3.3 | Force internal AI gateway | `enabled_providers: ["internal"]` |
| 2.3.4 | Permission baseline | `permission: { "*": "ask", "read": "allow" }` |

**Estimativa:** 100 linhas | **Dependência:** Fase 1.3

### 🟠 2.4 — Formatter Pipeline
> **Base:** OpenCode Formatters + NC Validation

| # | Formatter | Extensão | Comando |
|---|-----------|----------|---------|
| 2.4.1 | Ruff (Python) | .py | `ruff format $FILE` |
| 2.4.2 | NC-Naming validator | .py, .yaml, .md | `NC-SCR-FR-013-validate-file.py` |
| 2.4.3 | YAML sanitizer | .yaml | `NC-SCR-FR-009-sanitize-all-yamls.py` |

**Estimativa:** 100 linhas | **Dependência:** Fase 0.3

### 🟠 2.5 — Governance Dashboard (TUI)
> **Base:** OpenCode TUI Commands + NeoCortex Metrics

| # | Comando | Ação |
|---|---------|------|
| 2.5.1 | `/gov status` | Exibe estado governança (20 regras) |
| 2.5.2 | `/gov audit` | Executa `NC-SCR-FR-080` |
| 2.5.3 | `/gov ssot` | Exibe diff SSOT vs filesystem |
| 2.5.4 | `/gov tickets` | Lista tickets órfãos |

**Estimativa:** 200 linhas | **Dependência:** Fase 0, 1.1

---

## FASE 3 — OPENCODE PLATFORM EXPANSION (3 PROJETOS)

### 🔵 3.1 — SDK Client NeoCortex
> **Base:** `@opencode-ai/sdk` + TypeScript types

| # | Funcionalidade | Endpoint OpenCode | Serviço NeoCortex |
|---|---------------|------------------|-------------------|
| 3.1.1 | Client wrapper | `createOpencodeClient()` | Governança |
| 3.1.2 | Structured output | `format: { type: "json_schema" }` | Schema validation |
| 3.1.3 | Event subscription | `event.subscribe()` | EventBus |
| 3.1.4 | File operations | `find.text`, `file.read` | Search tools |

**Estimativa:** 300 linhas | **Dependência:** Fase 1.1

### 🔵 3.2 — TUI Control Integration
> **Base:** OpenCode TUI Control API

| # | Funcionalidade | API |
|---|---------------|-----|
| 3.2.1 | Toast notifications | `POST /tui/show-toast` |
| 3.2.2 | Prompt injection | `POST /tui/append-prompt` |
| 3.2.3 | Command execution | `POST /tui/execute-command` |
| 3.2.4 | Control responses | `POST /tui/control/response` |

**Estimativa:** 150 linhas | **Dependência:** Fase 1.1

### 🔵 3.3 — OpenCode Web UI for NeoCortex
> **Base:** `opencode web` + NeoCortex Server

| # | Funcionalidade | Configuração |
|---|---------------|-------------|
| 3.3.1 | Web server config | `server: { port: 4096, hostname: "0.0.0.0" }` |
| 3.3.2 | CORS for tools | `cors: ["http://localhost:5173"]` |
| 3.3.3 | mDNS discovery | `mdns: true` |

**Estimativa:** 100 linhas | **Dependência:** Nenhuma

---

## FASE 4 — GOVERNANÇA AVANÇADA (4 PROJETOS)

### 🟣 4.1 — Circuit Breaker (R16)
> **Completar regra R16 — Circuit Breaker**

| # | Funcionalidade | Descrição |
|---|---------------|-----------|
| 4.1.1 | Falha counter por agente | MetricsStore tracking |
| 4.1.2 | Auto-suspensão após threshold | PolicyLoader |
| 4.1.3 | MCP tool para gerenciamento | `NC-TOOL-FR-*` |

**Estimativa:** 200 linhas

### 🟣 4.2 — Rate Limiting Completo (R17)
> **Completar regra R17**

| # | Funcionalidade | Descrição |
|---|---------------|-----------|
| 4.2.1 | Rate limits por ferramenta | PolicyLoader |
| 4.2.2 | Limites por agente/Tier | SecurityService |
| 4.2.3 | Reset periódico | KairosService |

**Estimativa:** 150 linhas

### 🟣 4.3 — Memory Index (MEMORY.md)
> **Índice leve para lobes com carregamento JIT**

| # | Funcionalidade | Script |
|---|---------------|--------|
| 4.3.1 | Gerar MEMORY.md | `NC-SCR-FR-082-memory-index.py` |
| 4.3.2 | Carregamento JIT sob demanda | LobeService |
| 4.3.3 | Integrar com @POPULATE | `NC-SCR-FR-001` |

**Estimativa:** 250 linhas

### 🟣 4.4 — SSOT Auto-Sync Daemon
> **Manter SSOT sincronizado automaticamente**

| # | Funcionalidade | Frequência |
|---|---------------|------------|
| 4.4.1 | Watcher de filesystem → SSOT | Tempo real |
| 4.4.2 | Sync automático no Ciclo 3 | 1h |
| 4.4.3 | Full audit no Ciclo 4 | 24h |

**Estimativa:** 300 linhas

---

## ROADMAP TEMPORAL

```
SEMANA 1-2: FASE 0 (SSOT Cleanup)
  ├── Dia 1: 🔴 0.1 Fantasmas + 0.2 Links Mortos
  ├── Dia 2: 🔴 0.3 Conformidade NC-
  └── Dia 3: Validação e checkpoint

SEMANA 3-4: FASE 1 (OpenCode Integration - top 5)
  ├── Dia 4-5: 🟡 1.1 Plugin Gateway + 1.3 Permission Guard
  ├── Dia 6-7: 🟡 1.2 SessionBridge + 1.4 MCP Registry
  └── Dia 8-10: 🟡 1.5 AGENTS.md + 1.6 Go/Zen

SEMANA 5: FASE 2 (Governança)
  ├── Dia 11: 🟠 2.1 GitHub + 2.2 GitLab
  ├── Dia 12: 🟠 2.3 Enterprise + 2.5 Dashboard
  └── Dia 13: 🟠 2.4 Formatter Pipeline

SEMANA 6: FASE 3 (Platform)
  ├── Dia 14: 🔵 3.1 SDK + 3.2 TUI
  └── Dia 15: 🔵 3.3 Web UI

SEMANA 7: FASE 4 (Avançado)
  ├── Dia 16: 🟣 4.1 Circuit Breaker + 4.2 Rate Limiting
  └── Dia 17: 🟣 4.3 Memory Index + 4.4 SSOT Daemon
```

---

## MÉTRICAS DE SUCESSO

| Métrica | Atual | Meta | Prazo |
|---------|-------|------|-------|
| Conformidade NC- | 60.8% | >80% | Semana 1 |
| SSOT sync rate | ~60% (166/273) | >95% | Semana 2 |
| Arquivos fantasmas | 166 | <10 | Semana 1 |
| Links mortos | 177 | <20 | Semana 2 |
| Tools MCP integradas OpenCode | 0 | 15+ | Semana 4 |
| Plugins OpenCode-NeoCortex | 0 | 3+ | Semana 5 |
| Regras IA implementadas | 15/20 | 20/20 | Semana 7 |
| GitHub Actions operacional | 0 | 2 workflows | Semana 5 |
| Governança dashboard | 0 | 4 comandos `/gov` | Semana 5 |

---

## REFERÊNCIAS CRUZADAS

| Referência | Onde | Para quê |
|-----------|------|----------|
| `NC-DOC-FR-001` (UBL) | Dicionário ubíquo | @ $ % # símbolos |
| `NC-GOV-FR-003` (20 regras) | Governança IA | Base do plano |
| `NC-GOV-FR-005` (Ecosystem) | Mapa ecossistema | Hierarquia completa |
| `NC-CYC-FR-001` (4 Ciclos) | Validação cíclica | Rotina diária |
| `NC-NAM-FR-001` (SSOT) | Nomenclatura | Fase 0 |
| `NC-HK-FR-001` (HookRegistry) | Hooks MCP | Fase 1.1 |
| OpenCode SDK | Server/Client | Fase 3.1 |
| OpenCode Server | API REST | Fase 3.3 |
| OpenCode Plugins | Extensão | Fase 1.1-1.10 |
| OpenCode GitHub | Workflows | Fase 2.1 |
| OpenCode GitLab | CI/CD | Fase 2.2 |
| OpenCode Permissions | Segurança | Fase 1.3 |
| OpenCode MCP Servers | Protocolo | Fase 1.4 |
| OpenCode Rules (AGENTS.md) | Regras | Fase 1.5 |
| OpenCode Agents | Especialização | Fase 1.7 |
| OpenCode Agent Skills | SKILL.md | Fase 1.8 |
| OpenCode Custom Tools | .opencode/tools/ | Fase 1.9 |
| OpenCode LSP | Diagnostics | Fase 1.10 |
| OpenCode Enterprise | MDM | Fase 2.3 |
| OpenCode Formatters | Pipeline | Fase 2.4 |
| OpenCode TUI | Interface | Fase 2.5, 3.2 |
| OpenCode ACP | Protocolo | Fase 1.7 |
| OpenCode Zen/Go | Modelos | Fase 1.6 |

---

## PRÓXIMO PASSO IMEDIATO

```bash
# 1. Executar genealogy-injector real
python "01_neocortex_framework\scripts\NC-SCR-FR-075-genealogy-injector.py" --execute

# 2. Subir conformidade NC- de 60.8% para >80%
python "01_neocortex_framework\scripts\NC-SCR-FR-080-governance-auditor.py" --environment original --execute --focus-naming

# 3. Limpar 166 fantasmas + 177 links mortos
python "01_neocortex_framework\scripts\NC-SCR-FR-023-ssot-auditor.py" --fix
```
