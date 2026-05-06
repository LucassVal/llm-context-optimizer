<!-- NC-READ-HASH: NC-BOOT-FR-001-v7 -->
<!-- DEDUP: Se NC-BOOT-FR-001-v7 ja esta no contexto desta sessao, SALTE. -->

# NC-BOOT-FR-001  NeoCortex: Boot Universal Completo

> **LEIA ESTE ARQUIVO PRIMEIRO — e apenas este.** Ele contem TUDO.  
> Qualquer IA (Antigravity, OpenCode, Cursor, Claude, DeepSeek) comeca aqui.  
> Ultima atualizacao: 2026-05-06 | **v8** — LEXICO v4.6 | 258 files | 19 tools 3W+gateway+mcp_response | 6 tickets OPEN

---

## 1. IDENTIDADE DO SISTEMA

**Projeto:** NeoCortex MCP Framework v5.0  
**GitHub:** https://github.com/LucassVal/llm-context-optimizer  
**Raiz:** `C:\Users\Lucas Valerio\Desktop\TURBOQUANT_V42\`  
**Framework:** `01_neocortex_framework\`  
**Objetivo:** Framework MCP industrial com governanca de IA, memoria persistente (lobos) e resolvedor semantico de paths (LEXICO).  
**Dono:** Lucas Valerio  
**Fase atual:** GOVERNANCA & MULTI-AGENTE. MCP ativo via stdio local. 19 tools MCP com 3W documentadas. Semantic Response Cache integrado no DeepSeekBackend. Ollama :11434 com Qwen 1.5B/3B. LiteLLM e PicoClaw removidos. NC- 67.9%.

**Versoes dos componentes:**
| Componente | Versao |
|-----------|--------|
| Package | 4.2.0 |
| LEXICO | v4.6 |
| SSOT (NC-NAM-FR-001) | v2.1 |
| Governance Rules | v4.0 (133) |

---

## 2. ARQUITETURA ATUAL (v7 — 2026-05-04)

```
  T0 (DeepSeek V4 Pro via OpenCode)
   │
   ├─ Ollama :11434 (LOCAL iGPU)
   │   ├─ Qwen 2.5 Coder 1.5B → nc-courier (T1, rotinas) + nc-guardian (T3, validacao)
   │   └─ Qwen 2.5 Coder 3B  → nc-engineer (T2, micro-tarefas em sandbox)
   │
   ├─ MCP stdio local (neocortex.mcp.server)
   │   └─ 155 serviços no LEXICO v4.1 (#TOOLGUARD, #GATEWAY, etc.)
   │
   └─ Agentes OpenCode (.opencode/agents/)
      ├─ nc-courier  → Qwen 1.5B (T1), rotinas mecanicas, ciclos, dados. Nunca decide.
      ├─ nc-engineer → Qwen 3B (T2), micro-tarefas em sandbox. T0 aprova.
      ├─ nc-guardian → Qwen 1.5B (T3), validacao read-only. @LOCKS + naming + secrets.
      └─ nc-auditor  → DeepSeek Flash (TA), auditoria pesada. Reporta ao T0.

  RESOLUÇÃO DE PATHS (ADR-008)
   SSOT → referencia #TOOLGUARD → LEXICO v4.1 resolve → path real
   NENHUM código, ticket ou documento hardcoda paths.
```
| **DeepSeek** | LLM executor via API direta | cloud | DeepSeekBackend (NC-LLM-FR-001) |
| **Ollama (Qwen)** | Worker pool bracal | :11434 | local iGPU |
| **Semantic Cache** | Response cache com embeddings | LanceDB local | NC-CORE-FR-174 |
| **neocortex_hud.py** | Dashboard local | GUI Tkinter | Read-only monitor |

### Regra de ouro
> T0 (OpenCode) **pensa e decide**. Agentes (nc-courier, nc-engineer, nc-guardian, nc-auditor) **executam**. OpenCode **orquestra** nativamente. Hierarquia completa: **Constitution §4** (`@UBL agent-rules`).
> O Core **não sabe** que Mission Control ou Pixel Agents existem — DDD hexagonal.

### Blindagem do Servidor MCP (STDIO & WAL) - INTEGRAÇÃO OPENCODE/ANTIGRAVITY
> **Transporte Oficial (Launch Mode):** Antigravity e OpenCode DEVEM instanciar o MCP via **`stdio`** (chave `command: python`). A IDE governa o ciclo de vida do processo filho. O uso de `httpUrl` (Attach Mode/SSE) para MCP é banido por risco de portas órfãs.
> **Canal JSON-RPC Blindado:** O NeoCortex redireciona cirurgicamente todos os logs do ciclo de vida nativo para `sys.stderr`. O `stdout` é isolado de corrupções para garantir sincronia do JSON-RPC da IDE.
> **Crash Recovery (WAL):** Em caso de fechamento súbito do OpenCode/Antigravity (kill process), as transações de contexto não são perdidas. O Hook de `PostToolUse` injeta diretamente na base SQLite cada requisição finalizada (`TOOL_TRANSACTION`), garantindo Commit Imediato no FileSystem.

### Mapeamento de Portas NeoCortex (Orquestrador Unitário)

**8 portas para serviços core:**
1. `8765` - MCP Server (WebSocket/SSE) - core principal
2. `8766` - Health wrapper (HTTP) - endpoint /health e /ready
3. `8767` - Pixel Agents HTTP server (hooks) - recebe eventos do Claude Code
4. `8768` - A2A Gateway - comunicação entre agentes
5. `8769` - Courier service - entrega de mensagens
6. `8770` - Engineer service - execução de tasks
7. `8771` - FastAPI Web - interface administrativa
8. `8772` - Webhook receiver - recebe webhooks externos

**8 portas para comunicação A2A (Agent-to-Agent):**
9. `8773` - A2A Channel 1
10. `8774` - A2A Channel 2
11. `8775` - A2A Channel 3
12. `8776` - A2A Channel 4
13. `8777` - A2A Channel 5
14. `8778` - A2A Channel 6
15. `8779` - A2A Channel 7
16. `8780` - A2A Channel 8

**Serviços externos (não gerenciados pelo orquestrador):**
- **LiteLLM Gateway**: `4000` — proxy LLM unificado (DeepSeek API + Ollama local)
- Mission Control: `3000`
- PicoClaw: `18790`
- OpenCode: `45132` / `32879`
- Ollama: `11434`

---

## 3. COMO INICIAR (ordem obrigatria)

```powershell
# ORDEM DE STARTUP OBRIGATÓRIA:

# 0. LiteLLM Gateway (Windows Task Scheduler ou manual):
litellm --config config.yaml --port 4000
# OU via script: .\01_neocortex_framework\scripts\NC-SCR-FR-110-litellm-startup.ps1 -Start

# 1. Verificar MCP core:
netstat -an | findstr 8765

# 2. Se no estiver rodando:
cd C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42
.\start_neocortex_mcp.ps1

# 3. Verificar LiteLLM health:
Invoke-RestMethod http://localhost:4000/health -Headers @{Authorization='Bearer sk-my-master-key-123'}

# 4. Verificar PicoClaw gateway:
netstat -an | findstr 18790

# 5. HUD local:
python 01_neocortex_framework\scripts\neocortex_hud.py

# 6. Verificar lobos (se SSOT mudou):
python 01_neocortex_framework\scripts\NC-SCR-FR-001-populate-lobes-ssot.py --dry-run
```

---

## 4. MAPA DE LOBOS ATIVOS

| Smbolo | Lobo | Contedo |
|---|---|---|
| `$ARCH` | `NC-LBE-FR-ARCHITECTURE-001` | Roadmap + Naming + ADRs |
| `$SEC` | `NC-LBE-FR-SECURITY-001` | Locks + Policy + SOP |
| `$DEV` | `NC-LBE-FR-DEVELOPMENT-001` | Auditorias + Alinhamentos |
| `$DEEPSEEK` | `NC-LBE-FR-DEEPSEEK-001`  | API completa DeepSeek |
| `$LITELLM` | `NC-LBE-FR-LITELLM-001` | Gateway unificado LLMs :4000 |
| `$DS_A` | `NC-LBE-DS-001-deepseek-agent.mdc` | Agente DS-A executor |
| `$DS_B` | `NC-LBE-DS-002-deepseek-agent-b.mdc` | Agente DS-B pesquisa |
| `$DS_C` | `NC-LBE-DS-003-deepseek-agent-c.mdc` | Agente DS-C tools |
| `$DS_D` | `NC-LBE-DS-004-deepseek-agent-d.mdc` | Agente DS-D observabilidade |
| `$WORKER_PATTERNS`  | `NC-LBE-DS-003-worker-patterns.mdc` | REG-001010, claim protocol |
| `$ANTIGRAVITY` | `NC-LBE-INT-003-antigravity-integration.mdc` | Papel T0, 40 tools MCP |
| `$MISSION_CTRL` | `NC-LBE-INT-004-mission-control.mdc` | Mission Control integrao |
| `$PIXEL_AGENTS` | `NC-LBE-INT-005-pixel-agents.mdc` | Pixel Agents + bridge spec |

---

## 5. MAPA SSOT  ONDE FICA CADA COISA

| Smbolo | Path | Funo |
|---|---|---|
| `@SSOT` | `01_neocortex_framework/23-docs/NC-NAM-FR-001-naming-convention.md` | Naming + mapa + changelog |
| `@ROADMAP` | `01_neocortex_framework/23-docs/NC-TODO-FR-001-project-roadmap-consolidated.md` | Roadmap unificado (FR + DS) |
| `@LOCKS` | `01_neocortex_framework/23-docs/NC-SEC-FR-001-atomic-locks.yaml` | Arquivos protegidos DENY |
| `@POLICY` | `01_neocortex_framework/23-docs/NC-CFG-FR-002-rules-policy.yaml` | Regras machine-readable |
| `@GOVERNANCE` | `01_neocortex_framework/23-docs/NC-GOV-FR-003-ia-governance-rules.yaml` | 133 regras de governanca (R01-R133) |
| `@BOOT` | `06-boot/NC-BOOT-FR-001-system-manifest.md` | **Este arquivo** |
| `@SOP` | `01_neocortex_framework/23-docs/NC-SOP-FR-001-session-startup.md` | SOP de sesso |
| `@POPULATE` | `01_neocortex_framework/scripts/NC-SCR-FR-001-populate-lobes-ssot.py` | Popula lobos |
| `@APPENDIX` | `01_neocortex_framework/23-docs/NC-APP-FR-001-technical-appendix.md` | Tools, libs, LLMs |
| `@ULQ` | `01_neocortex_framework/23-docs/NC-DOC-FR-001-ubiquitous-language-dictionary.md` | Dicionário @$% |
| `@CHANGELOG` | `01_neocortex_framework/23-docs/NC-CHG-FR-001-changelog.yaml` | Changelog + Kaizen unificado |
| `@MAPS` | `01_neocortex_framework/23-docs/NC-MAP-FR-001-structural-maps.yaml` | 6 mapas estruturais |
| `@PROMPT` | `01_neocortex_framework/DIR-PRF-FR-001-profiles-main/NC-PRF-FR-001-master-governance-prompt.md` | T1 Master context |
| **@P0** | `.agents/workflows/NC-WF-002-master-governance.md` | **Master Governance (Lente Analítica)** |

---

## 6. FRENTES OPERACIONAIS ATIVAS (2026-05-04)

** FRENTE ATIVA:** Correes Crticas NeoCortex (Orquestrao T0)

1. **Outros  Tarefas diversas**
   - Handoff: NC-DS-223  COMPLETED
   - Handoff: NC-DS-262  %DONE (Pivotação DDD e Saneamento de Órfãos. 5 scripts arquivados. Zero imports cross-domain)

**Prximo passo:** Executar testes corrigidos (`pytest tests/test_vector_engine.py -v --asyncio-mode=auto`)

**MCP-WQUEUE:** Tickets YAML em `DIR-DS-001-tickets/`. Agentes OpenCode executam e geram handoffs em `DIR-DS-002-audit-logs/`. T0 (Antigravity) valida e aprova.

---
## 7. ESTADO ACUMULADO  O QUE FOI CONSTRUDO

| Grupo | Quantidade | Status |
|---|---|---|
| Serviços core (`NC-SVC-FR-*`) | 18 |  DONE |
| Utils (`NC-UTL-FR-*`) | 4 |  DONE |
| Tools MCP (`NC-TOOL-FR-000037`) | 38 |  DONE |
| Hooks core (`NC-HK-FR-001/002`) | 2 |  DONE |
| Config core (`NC-CFG-FR-004`) | 1 |  DONE |
| Lobes de integração (`NC-LBE-INT-004/005`) | 2 |  Em documentação |
| HUD Tkinter (5 abas) | 1 |  FUNCIONAL |
| PicoClaw gateway | 1 |  :18790 ativo |

**Serviços adicionados em 2026-04-16 (Ciclo 3):**

| Serviço | ID | Status | Descrição |
|---|---|---|---|
| CryptoHub | `NC-SVC-FR-017` | ✅ ACTIVE | Fernet AES-128 + HMAC-SHA256. Key via PBKDF2(MASTER_KEY). Fallback hash-only. |
| TagNormalizer | `NC-SVC-FR-018` | ✅ ACTIVE | Valida @/$/% contra NC-DOC-FR-001 SSOT. scan(), normalize(), validate_lobe(). |

**Entregas da sessão 2026-04-20 (Reorganização Semântica + Governança + PICOCLAW):**

| Entrega | ID | Status | Descrição |
|---|---|---|---|
| PICOCLAW Server | `NC-SVC-FR-019` | ✅ ACTIVE | HTTP A2A :18790. /event/publish, /event/poll, /task/dispatch, /llm/call (LiteLLM :4000 + Ollama fallback) |
| PICOCLAW MCP Tool | `NC-SUPER-016` | ✅ ACTIVE | 8 actions: start, stop, status, publish, poll, dispatch, task_status, llm_call |
| LEXICO-002 | `NC-SCR-FR-135` | ✅ DONE | 1041 termos classificados em 6 regiões cerebrais via keyword + LLM (Qwen 1.5b) |
| Orphan Scripts | `NC-SCR-FR-136..144` | ✅ DONE | 9 renomeados + 25 arquivados em DIR-ARC-FR-001 |
| Manifests Dirs | `_INDEX.mdc` x14 | ✅ DONE | 14 dirs indexados (CFG, REF, TEST, DS-001..004, templates, docs, etc.) |
| **DDD Memory Indust.** | `NC-DS-202` | ✅ **DONE** | **Arquitetura DDD Canônica: _INDEX.yaml + Junctions para 8 domínios cerebrais.** |
| **DeepSeek v4/R1** | `deepseek-v4` | ✅ **DONE** | **Payloads industrializados: Thinking Mode (Enabled/Effort) + Multi-Round Chat.** |
| .gitignore | — | ✅ DONE | +10 entradas: node_modules, *.archived, logs, reports, **02_memory_lobes/$lobe/** |

**Distribuição semântica atual (FTS5 — 1041 termos):**
```
$frontal   438 (42%)  governance, naming, roadmap
$parietal  290 (28%)  MCP, tools, integration
$occipital 207 (20%)  patterns, architecture
$cerebelo   46  (4%)  guardian, ciclos
$hipocampo  46  (4%)  sessions, audit
$temporal   14  (1%)  lexico, KG, NLP
```


**Governança:** Compliance 44.9% → meta >80% (NC-DS-108 FAILED)

### Colisões resolvidas (2026-04-13)
FR-032, FR-033, FR-020-categories, FR-028-export  arquivados em `DIR-ARC-FR-001-archive-main/tools-duplicates-20260413/`

### SSOT + Tool Manifest Sync (2026-04-16)
- **SSOT**: Tabela NC-NAM-FR-001 atualizada com 17 NC-SVC, 35 NC-TOOL, 37 NC-SCR faltantes (drift corrigido).
- **Tool Manifest**: Regenerado com 38 tools + placeholders para hooks FR-003.
- **Registry**: NC-GOV-FR-004 atualizado com paths de todas as 35 tools físicas.
- **Boot Manifest**: Esta atualização (NC-DS-113) concluída.


## 8. CAMINHO CRTICO PR-MCP

```
FASE PR-MCP [ATUAL]:
   Antigravity ↔ MCP stdio ↔ NeoCortex Core — configurado
   PicoClaw ↔ OpenCode ↔ DeepSeek — operacional
   38 tools MCP físicos — criados e manifestados
   ORCH-301 — DONE (NC-DS-096, send_task() HTTP POST :18790)
   ORCH-302 — DONE (NC-DS-096, neocortex_task SSE polling)
   SAVE-005 — WIRED (dry-run preview middleware)

CRITRIO DE ENCERRAMENTO DA FASE PR-MCP:
  Antigravity chama tool MCP → Core recebe → PicoClaw despacha → OpenCode executa → resultado retorna

## 9. DDD MEMORY ARCHITECTURE (2026-04-27)

Estrutura de diretórios em `02_memory_lobes/` organizada por domínios canônicos e vinculada via **Directory Junctions** aos domínios cerebrais ($).

| Lobe Canônico | Domínio DDD | Brain Link ($) | DeepSeek Capabilities |
|---|---|---|---|
| ARCHITECTURE-001 | `01_architecture` | `$occipital/` | chat, reasoner, thinking |
| SECURITY-001 | `02_security` | `$hipocampo/` | chat, reasoner |
| DEVELOPMENT-001 | `03_development` | `$parietal/` | chat, reasoner, thinking |
| PROFILES-001 | `04_profiles` | `$parietal/` | chat |
| WHITELABEL-001 | `05_whitelabel` | `$temporal/` | chat |
| FRONTAL-001 | `06_governance` | `$frontal/` | reasoner, thinking |
| TEMPORAL-001 | `07_lexicon` | `$temporal/` | chat, reasoner |
| HIPOCAMPO-001 | `08_sessions` | `$hipocampo/` | chat, reasoner |

> **Nota:** Todos os links são gerados automaticamente pelo script `@POPULATE` baseado no `_INDEX.yaml`.
  = Loop completo Antigravity ↔ Core ↔ PicoClaw ↔ OpenCode via MCP

PRÓXIMOS PASSOS:
  [ ] Executar SAVE-005 (dry-run preview)
  [ ] Executar SCR-064 (catalog) + SCR-066 (bootup sync)
  [ ] Validar loop completo Antigravity → Core → PicoClaw → OpenCode
```


## 9. TICKETS CRTICOS (PR-MCP & RUST MIGRATION)

| Ticket | Status | Prxima ao |
|---|---|---|
| **NC-DS-160** |  DONE | Revisão FastMCP health_check() aprovada. |
| **NC-DS-161** |  DONE | Sockets migrados para 127.0.0.1. Sub-serviços verificados como stubs funcionais. |
| **NC-DS-156** |  DONE (MVP) | Zero-Trust RBAC (CryptoHub Interceptor) em Python. |
| **NC-DS-157** |  DONE (MVP) | Shared Memory (mmap) IPC no PicoClaw. |
| **NC-DS-158** |  DONE (MVP) | Otimização LanceDB (HNSW + IVFPQ) ativa no LexicoService. |
| **NC-DS-159** |  DONE (MVP) | Thermal Context Decay GC no Pulse Scheduler. |
| **INT-001** |  Entregue | Concluído (Fase 3 pré-MCP completa) |

---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---

## 10. REGRAS OBRIGATRIAS

| ID | Regra |
|---|---|
| **R01** | `NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext`  SEMPRE |
| **R02** | Arquivo criado  atualizar `@SSOT` com changelog |
| **R04** | `@LOCKS` so IMUTVEIS: `server.py`, `sub_server.py`, `NC-NAM-FR-001`, `neocortex_config.yaml` |
| **R05** | NUNCA deletar  arquivar em `DIR-ARC-FR-001-archive-main/` |
| **R09** | NUNCA `import NC-SVC-*` direto  usar `importlib.util` |
| **R10** | NUNCA hardcodar paths  usar `get_config()` |
| **R11** | NUNCA `print()`  `logger = logging.getLogger(__name__)` |
| **R17** | T0 orquestra. OpenCode/DeepSeek executam. Nunca inverter. |
| **R21** |  ZERO suposies  verificar ambiente real antes de qualquer afirmao |

### Zonas de escrita

| Zona | Path | Quem |
|---|---|---|
| PROD | `01_neocortex_framework/neocortex/` | T0, T1 |
| DOCS | `DIR-DOC-FR-001-docs-main/` | T0 apenas |
| LOBES | `02_memory_lobes/` | T0 via `@POPULATE` |
| BOOT | `DIR-BOOT-FR-001-bootup-main/` | T0 apenas |
| TEST | `05_examples/` | T0, T1 |

---

## 10.5 GOVERNANA DE IA  20 REGRAS

**Framework**: `NCGOVFR003iagovernancerules.yaml` + auditoria `NCSCRFR080governanceauditor.py`

**Categorias**:
1. **Fundao** (R01R05): Inventrio, poltica, estrutura, nomenclatura, ambientes
2. **Controle de Acesso** (R06R09): Identidade, privilgio mnimo, atomic locks, zonas de escrita
3. **Rastreabilidade** (R10R13): Trilha de auditoria, versionamento, handoffs, checkpoints
4. **Execuo** (R14R17): STEP0 (mentor_step_0), STEP1 (save point), circuit breaker, rate limiting
5. **Ciclo de Vida** (R18R20): Tickets, rotina de 4 ciclos, reviso e arquivo

**Status**: 12 implementadas, 3 parciais, 5 pendentes (ver auditoria)

**Integrao**:
- **Mentor Mode**: STEP0 valida tarefas contra Regression Buffer e polticas
- **Atomic Locks**: Proteo proativa de arquivos crticos (@LOCKS)
- **Hooks Reativos**: HookRegistry (PreToolUse/PostToolUse/ToolError) complementa locks
- **Ciclo 4**: Auditoria de governana semanal via `NCSCRFR080`

**Prximos passos**:
1. Implementar verificaes completas para regras pendentes
2. Integrar hooks de segurana com atomic locks
3. Migrar configurao para por projeto (`.nc/config.yaml`)
4. Criar template de plugin para tools MCP

---

## 10.6 STATUS DOS CICLOS — 2026-04-17

**Ciclo 2 (Durante a Sessão) — ✅ EXECUTADO**
- [x] Consulta ao catálogo de artefatos antes de editar
- [x] Verificação de zonas de escrita permitidas
- [x] SSOT atualizado após criação/renomeação
- [x] Handoff gerado para tickets concluídos (NC-DS-098 aprovado)
- [x] Integração MCP OpenCode documentada (NC-LBE-USR-003)

**Ciclo 3 (Fim de Sessão) — ✅ EXECUTADO**
- [x] Catálogo de artefatos atualizado (540 PY, 405 YAML)
- [x] Bootup sincronizado com estado real (NC-SCR-FR-066)
- [x] YAMLs de rotina sanitizados (NC-SCR-FR-009)
- [x] Rotina de fim de ciclo executada (NC-SCR-FR-014)
- [x] Lint/typecheck/testes passando (verificação completa)

**Progresso da Integração MCP:**
- ✅ Conflito de portas 8765/8767 resolvido (Pixel Agents → 8767)
- ✅ Health wrapper atualizado com verificação SSE
- ✅ MCP Server operacional em modo SSE (:8765)
- ✅ Configuração OpenCode MCP pronta (opencode.json)
- 🔄 Conexão SSE em teste (API mcp v1.26.0 em investigação)

---

## 11. CHECKLIST FIM DE SESSO  R20

```
 @SSOT atualizado + changelog [YYYY-MM-DD]
 %DONE no @ROADMAP para cada ticket concludo
 @POPULATE rodado (se algum lobe mudou)
 @BOOT atualizado (frentes + tickets + status)    OBRIGATRIO
 Nenhum *.db / *.wal / __pycache__ commitado
```


## STEP 0 ENFORCEMENT (added 2026-04-29)
Gateway now reads this manifest on first action (R16).
SSOT files listed here MUST be consulted before any action.
RAC+3W+KISS+R117 enforced via NC-RULE-009.

| Semantic Router (FR-165) | Central index + Domain Routers (8 domains, 763 items) | R118 |
| NC-ARC-FR-002-architecture-blueprint.yaml | DDD Architecture + Orbitals + Semantic Router | DDD |
| NC-LBE-FR-CONSTITUTION-001.mdc | AI Constitution (Shared Kernel, 13 sections) | R82 |
| NC-LBE-FR-RULES-MULTILAYER-001.mdc | 123 Rules + 4 Mordacas (H/C/S/U) v3.2 | R01-R120 |
