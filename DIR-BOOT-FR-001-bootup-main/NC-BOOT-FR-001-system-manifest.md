<!-- NC-READ-HASH: NC-BOOT-FR-001-v5 -->
<!-- DEDUP: Se NC-BOOT-FR-001-v5 j est no teu contexto desta sesso, SALTE este bloco inteiro. -->

# NC-BOOT-FR-001  NeoCortex: Boot Universal Completo

> **LEIA ESTE ARQUIVO PRIMEIRO  e apenas este.** Ele contm TUDO.  
> Qualquer IA (Antigravity, OpenCode, Cursor, Claude, DeepSeek) comea aqui.  
> Última atualização: 2026-04-18 | **v5**  SPRINT-ACELERADO-MCP | GPU Split ativo

---

## 1. IDENTIDADE DO SISTEMA

**Projeto:** NeoCortex MCP Framework  
**GitHub:** https://github.com/LucassVal/llm-context-optimizer  
**Raiz:** `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`  
**Framework:** `01_neocortex_framework\`  
**Objetivo:** Servidor MCP local que reduz custo de API substituindo tokens de cloud por memria persistente (lobos) + orquestrao multi-agente via PicoClaw + integrao visual via Mission Control e Pixel Agents.  
**Dono:** Lucas Valrio  
**Fase atual:** FASE 4 (MIGRAÇÃO RUST & SOTA). MCP-ATIVO — Python MVP 100% OK. Implementado: Zero-Trust, mmap IPC, LanceDB Indexing e Thermal Decay. Pronto para migração infra para Rust via `neocortex-mcp-rs`. Socket TCP :8765 blindado. 17 tools nativas auditadas.

---

## 2. ARQUITETURA COMPLETA DE PORTAS (Mapa Maduro v4)

```
 COMANDO (entram ordens no core) 

  Antigravity (T0)            Mission Control
  IDE via MCP stdio/SSE        :3000 HTTP/WS (React app)
                                   
        
                    
 NEOCORTEX CORE (Domnio DDD) 
  Lobes  HookRegistry  Checkpoint  SSOT  TaskQueue  ProjectConfig

                                              
      despacha tasks              emite eventos (HookRegistry)
                                             
PicoClaw (:18790)                       bridge JSONL
gateway A2A                                   
                                             
                                      Pixel Agents (:8767)
OpenCode (:45132 / :32879)             visualizao pixel-art
DeepSeek T1 executor                   (obs. passivo)

 OBSERVABILIDADE 
  Mission Control activity feed  SSE/WS  HookRegistry (AuditHook)
  neocortex_hud.py              polling local  server.py
```

### Papis por componente

| Componente | Papel DDD | Porta | Direo |
|---|---|---|---|
| **Antigravity** | Adaptador primrio | MCP stdio |  Core (comanda) |
| **Mission Control** | Adaptador primrio | :3000 |  Core (comanda + observa) |
| **LiteLLM Gateway** | Proxy LLM unificado | :4000 | Todos os modelos (DeepSeek + Ollama) |
| **PicoClaw** | Adaptador secundrio (driven) | :18790 | Core  Agentes |
| **OpenCode** | Runtime dos agentes T1 | :45132/:32879 | Executa tasks do PicoClaw |
| **DeepSeek** | LLM executor | via :4000 | LiteLLM roteia |
| **Ollama (Qwen)** | Worker pool braçal | :11434 | LiteLLM roteia |
| **Pixel Agents** | Adaptador secundrio (observer) | :8767 | Core  Visual |
| **neocortex_hud.py** | Dashboard local | GUI Tkinter | Read-only monitor |

### Regra de ouro
> T0 (Antigravity) **pensa e decide**. OpenCode/DeepSeek **executam**. PicoClaw **despacha**. Nunca inverter.  
> O Core **no sabe** que Mission Control ou Pixel Agents existem  DDD hexagonal.

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
| `@SSOT` | `DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md` | Naming + mapa + changelog |
| `@ROADMAP` | `DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md` | Roadmap unificado (FR + DS) |
| `@LOCKS` | `DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml` | Arquivos protegidos DENY |
| `@POLICY` | `DIR-DOC-FR-001-docs-main/NC-CFG-FR-002-rules-policy.yaml` | Regras machine-readable |
| `@GOVERNANCE` | `DIR-DOC-FR-001-docs-main/NC-GOV-FR-003-ia-governance-rules.yaml` | 20 regras de governana de IA + auditoria |
| `@BOOT` | `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md` | **Este arquivo** |
| `@SOP` | `DIR-DOC-FR-001-docs-main/NC-SOP-FR-001-session-startup.md` | SOP de sesso |
| `@POPULATE` | `scripts/NC-SCR-FR-001-populate-lobes-ssot.py` | Popula lobos |
| `@APPENDIX` | `DIR-DOC-FR-001-docs-main/NC-APP-FR-001-technical-appendix.md` | Tools, libs, LLMs |
| `@ULQ` | `DIR-DOC-FR-001-docs-main/NC-DOC-FR-001-ubiquitous-language-dictionary.md` | Dicionrio @$% |
| `@PROMPT` | `NC-PROMPT-FR-001-master-context.md` (raiz) | Contexto master v8 |

---

## 6. FRENTES OPERACIONAIS ATIVAS (2026-04-20)

** FRENTE ATIVA:** Correes Crticas NeoCortex (Orquestrao T0)

1. **Tester  Correo testes VectorEngine (async/API)**
   - Handoff: NC-DS-048  COMPLETED
   - Resultado: Aplicação massiva de metadados de frontmatter (domain, layer, type, tags, hash) em todos os arquivos complementares (Testes, Templates, Scripts base, configurações raiz) conforme especificado no ticket.

1. **Outros  Tarefas diversas**
   - Handoff: NC-DS-121  COMPLETED

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
| **SOTA Industrialization** | **PHASE-4-MVP** | ✅ **DONE** | **Python Core Industrializado: Zero-Trust, mmap IPC, LanceDB, Thermal Decay.** |
| .gitignore | — | ✅ DONE | +10 entradas: node_modules, *.archived, logs, reports/ |

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

CRITÉRIO DE ENCERRAMENTO DA FASE PR-MCP:
  Antigravity chama tool MCP → Core recebe → PicoClaw despacha → OpenCode executa → resultado retorna
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
