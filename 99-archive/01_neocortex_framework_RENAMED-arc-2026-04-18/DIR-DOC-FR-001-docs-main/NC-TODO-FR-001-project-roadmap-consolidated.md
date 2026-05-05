# NC-TODO-FR-001  NeoCortex: Roadmap SSOT Completo v9.0
<!-- @ROADMAP  Single Source of Truth | Atualizado: 2026-04-11 -->
<!-- MACRO  MICRO  TICKET: De A a Z, do incio ao fim -->

> **Filosofia:** MCP = vertical (agente  ferramentas). A2A = horizontal (agente  agente). Gateway = plano de controle.
> **Regra:** Toda implementao referencia um ticket aqui. Aps concluir  `%DONE` com data [YYYY-MM-DD].

---

##  O EDIFCIO  Lgica de Construo

> *Um edifcio no coloca janelas antes de ter paredes. O NeoCortex segue a mesma lgica.*

```
FUNDAO (Fase 0)         Infraestrutura, stores, backends LLM       [ DONE]
  
ESTRUTURA (Fase 1-2)     MCP ativo, HTTP IPC, Mentor Mode             [ DONE]
  
   LINHA PR-MCP/PS-MCP 
  

> Esta tabela mapeia **cada padro de arquitetura**  sua fase correta de implementao, com a razo tcnica.
> **Critrio de corte:** O padro  PR-MCP se a ausncia dele permite que o sistema **corrompa estado, gaste sem limite ou burle regras** quando rodar autnomo.

###  PADRES ALTOS (Crticos  bloqueiam operao autnoma segura)

| Padro | O QUE | POR QU agora | ONDE no Roadmap | Status |
|---|---|---|---|---|
| **STEP 0 (Mentor)** | Filtro pr-execuo: injeta contexto + regras antes do LLM | Sem isso, modelos 1.5B alucinam e violam polticas | Fase 1-2 (AGENT-203 / PRE-1) |  DONE |
| **Atomic Locks** | DENY-by-default: bloqueia escrita em paths protegidos | Sem isso, agente pode sobrescrever SSOT, config e ledger | Fase 4 (SEC-401) |  DONE |
| **Polticas de Uso** | Limites de tokens/budget/timeout por role | Sem isso, agente gasta todo o credit da API em uma tarefa | Fase 4 (PRE-1 + SEC-403) |  Parcial (PolicyLoader   rate limit runtime = SEC-403 pendente) |
| **Modo Mentor (global)** | Middleware no server.py principal, no s sub-servers | Cobre as 20 tools do MCP principal | Fase 4 (SEC-401 extenso) |  Sub-servers   server.py pendente |
| **STEP -1 (Save Point)** | Snapshot diff ANTES de qualquer escrita | Sem isso, falha = estado corrompido sem volta | Fase 4b (SAVE-002) |  Pendente |
| **STEP +1 (Rollback)** | Reverso automtica se ao falhar | Par obrigatrio do STEP -1: sem ele, o save point  intil | Fase 4b (SAVE-003) |  Pendente |
| **Audit Trail imtvel** | WAL append-only com hash encadeado | Log mutvel no  audit trail real  agente pode apagar rastro | Fase 4b (SAVE-004 + FR-026) |  Parcial (log mutvel   WAL = futuro) |

###  PADRES MDIOS (Importantes  no bloqueiam mas degradam resilincia)

| Padro | O QUE | POR QU | ONDE | Status |
|---|---|---|---|---|
| **Fallback Chain** | Troca automtica de backend LLM se um cair | Resilincia do sistema: sem fallback, MCP para se Ollama cair | Fase 0 (LLM-004) |  DONE |
| **PulseScheduler** | Heartbeat peridico: pruning, consolidation, backup | Mantm stores saudveis sem interveno manual | Fase 0 (OPT-010) |  DONE |
| **Manifestos de Lobo** | ndice leve do contedo de cada lobo | Agentes sem manifesto = sem contexto = alucinao | Fase 0-1 |  DONE |
| **Vocabulary Ubquo** | Dicionrio de termos $@% oficiais | Sem ele, IAs diferentes chamam o mesmo conceito de nomes distintos | Fase 0 (GOV-006) |  DONE |
| **Tool Manifest auto** | Manifest gerado dinamicamente no startup: NC-SCR-FR-003 + NC-TOOL-FR-019 | Fase 3 |  DONE [2026-04-11] |
| **Rate Limit por Tool** | Limites diferentes por tipo de ao (no s por agente) | ledger.update  task.execute em termos de risco | Fase 4 (SEC-403) |  Pendente |
| **Context Budget** | Rastrear tokens por sesso em tempo real | Sem isso, budget dirio  aproximao, no limite real | Fase 4b (FR-026) |  Pendente |

###  PADRES BAIXOS (Ps-MCP  polimento, observabilidade, distribuio)

| Padro | O QUE | ONDE | Status |
|---|---|---|---|
| **Nomenclatura NC- (enforcement)** | Pre-commit hook rejeita nomes sem prefixo | Fase 4 (SEC-402) |  DONE [2026-04-11] |
| **Mtricas / Observabilidade** | Latencia, custos, erros por agente em DuckDB | Fase 5 (FR-026) |  Parcial (MetricsStore , API balance = pendente) |
| **HUD / Painel** | Interface visual com compliance heartbeat real | Fase 0-HUD (HUD-001) |  DONE |
| **Logs Estruturados (JSON)** | `python-json-logger` em server.py, sub_server.py, pulse_scheduler.py | Fase 5 (OBS-001) |  Parcial  logging wrapper criado, import em @LOCKS = ticket futuro [2026-04-12]  PENDING T0 REVIEW [2026-04-12] |
| **Documentao White-Label** | Guias para novos usurios do framework | Fase 6 (DOC-503) |  Pendente |
| **JWT / OAuth 2.1** | Auth real para transports HTTP | Fase 5 (FR-027 + SEC-405) |  Pendente |
| **YAML Config (existe)** | Todos configs em YAML legivel | Fase 0 |  DONE |
| **Tool Categories Hub** | NC-TOOL-FR-020: wrapper temporrio  ser substitudo pelas 10 tools consolidadas (Fase 3) | Fase 3 (FR-021030) |  Wrapper ativo, refatorao pendente |
| **Manifest Factory** | NC-SCR-FR-003: scan completo, system_profile (tools+lobes+governance), boot_context | Fase 3 (FR-021a) |  DONE [2026-04-11] |
| **HUD Fix + stderr log** | NeoCortex_HUD.bat v5: fix PYTHONUTF8, stderrNC-LOG-FR-001 | Fase 0-HUD (HUD-002) |  DONE [2026-04-11] |
| **Health Check /health endpoint** | HTTP /health nos sub-servers com estado interno (last_task, tokens) | Fase 5 (AGENT-206) |  DONE [2026-04-12] |
| **TTL de Logs** | PulseScheduler: apagar JSONL mais antigos que 7 dias | Fase 5 (TTL-002) |  Pendente |

---

## CAMADAS E STATUS

| Camada | O que | Padres Associados | Status |
|---|---|---|---|
| L0 | Infraestrutura (MCP server, backends LLM, stores) | Fallback Chain   PulseScheduler   YAML Config  |  Completo |
| L1 | Core MCP ativo com 20 tools/~70 aes | Vocabulrio Ubquo   Manifestos de Lobo  |  Funcional |
| L2 | Orquestrao real (spawn/task IPC) | Mentor Mode   Policy YAML   Atomic Locks  |  Ativo |
| L3 | Security Hard Enforcement | STEP -1   Rollback   SEC-402   Rate Limit  |  EM FOCO |
| L4 | 10 tools refatoradas (FR-021030)  130 aes por domnio | Tool Refactor   lobe.fragment   hierarchy T0T3  |  Planejado |
| L5 | SDK + Distribuio  FastAPI, .exe, docker-compose | ORCH-301   SDK-001   7 portas   Rust daemon  |  Futuro |

---

##  PR-REQUISITOS POR FASE (Dependncia Tcnica)

```
Fase 4 (Security) requer:
   Fase 0-2 completa (LLM backends + HTTP IPC + AGENT-203)  

Fase 4b (Save Points) requer:
   SEC-401 (LockGuard)   DONE hoje
   PolicyLoader (PRE-1)   DONE hoje
   SAVE-002 (Save Point Middleware)   NEXT

Fase 3 (Refatorao 10 tools) requer:
   Fase 0-4 funcional (MCP ativo + locks)
   FR-024 (governance tool) requer autorizao T0 (@LOCKS override)
   FR-029/030 (health + context)  novos, sem dependncia  iniciar primeiro

Fase 5 (A2A + Gateway + SDK Rust) requer:
   Fase 3 completa (10 tools refatoradas + ORCH-301)
   SAVE-005 (audit trail imutvel)
   FR-027 (auth JWT) + FR-029 (discovery)

Fase 6 (Distribuio: PyPI + .exe) requer:
   Fase 5 completa (Gateway estvel)
   Tool refactor concludo (NC-TOOL-FR-021030)
   CI/CD validado (GitHub Actions)
```

> **ADR-SDK-001 [2026-04-11]:** Core Python permanece ABERTO e white-label (no encapsulado).
> SDK Rust encapsula APENAS o Gateway/A2A. Distribuio em 2 fases:
> - Fase 6: `pip install neocortex-mcp` (core Python, curto prazo)
> - Fase 5/end: GitHub Release `.exe` (Rust daemon, aps Fase 5 estvel)

---

##  FASE 0  CONCLUDO (Fundao)

### Infrastructure & Stores
- [x] **OPT-001** `LedgerStore` storage otimizado (DuckDB)
- [x] **OPT-002** `ManifestStore` para tool manifests
- [x] **OPT-003** `LobeIndex` para metadados de lobos
- [x] **OPT-004** `SearchEngine` busca hbrida (FTS5 + semntica)
- [x] **OPT-005** `HotCache` (diskcache)
- [x] **OPT-006** `LobeIndex` integrado ao `LobeService`
- [x] **OPT-007** MCP search tool
- [x] **OPT-008** Script de migrao
- [x] **OPT-009** `ConfigProvider` global
- [x] **OPT-010** `PulseScheduler` heartbeat

### LLM Backends
- [x] **LLM-001** Design hybrid LLM mode
- [x] **LLM-002** `LLMBackend` ABC
- [x] **LLM-003** `OllamaBackend` (Qwen local)
- [x] **LLM-004** `DeepSeekBackend` (API + streaming + fallback)
- [x] **LLM-005** `OpenAIBackend`
- [x] **LLM-006** `LLMFactory`
- [x] **LLM-007** `AgentExecutor`
- [x] **LLM-008/009/010/011/012** Config, override, docs, testes, benchmarks

### MCP Base
- [x] **ORCH-001** Script de startup do sub-MCP server
- [x] **ORCH-002** Ferramenta `neocortex_subserver` (base)
- [x] **ORCH-003** Ferramenta `neocortex_task` (base)
- [x] **ORCH-004** Lobos isolados por agente

### Estabilizao (v6)
- [x] **STAB-101** ConfigProvider Integration completo
- [x] **STAB-102** Audit Factories & Singletons
- [x] **STAB-103** Sanity Test Suite
- [x] **STAB-104** LLM Factory Config Handling
- [x] **STAB-105** HotCache com diskcache robusto
- [x] **METR-106** MetricsStore  Domain Tables
- [x] **METR-107** MetricsStore integrado aos core components
- [x] **METR-108** MCP Report Tool
- [x] **METR-109** Validation & Sanity Integration
- [x] **AGENT-202** Sub-Server com Role Configuration
- [x] **AGENT-204** Tool Allow/Deny Lists

### Governana & NeoCortex Brand (2026-04-11)
- [x] **GOV-001** Rebrand: llm-context-optimizer  NeoCortex
- [x] **GOV-002** Estrutura numbered zones (01_ a 05_)
- [x] **GOV-003** 4 MDC rules modulares (NC-RULE-001 a 004)
- [x] **GOV-004** NC-CFG-FR-002 (policy-as-code YAML)
- [x] **GOV-005** NC-SEC-FR-001 (atomic locks  6 categorias)
- [x] **GOV-006** NC-DOC-FR-001 (ubiquitous language @$%)
- [x] **GOV-007** @BOOT manifest auto-suficiente
- [x] **GOV-008** R20  @BOOT atualizado no checklist de fim de sesso
- [x] **GOV-009** DeepSeek como T0 default (config + backend verificado)
- [x] **GOV-010** $DEEPSEEK lobe criado (referncia completa da API)
- [x] **GOV-011** NC-PROMPT-FR-002 (pre-MCP manual checklist)
- [ ] **GOV-012** Biblioteca Documental Hierrquica  subdividir NC-NAM-FR-001 em sub-registros (tools/lobes/config/prompts) + manifesto-mestre SHA-256 + script de validao  **NC-DS-007-REVISED** | DS-B | `[2026-04-12]`  PENDING T0 REVIEW [2026-04-12]
- [x] **GOV-013** Timestamp padronizado ISO 8601 HH:MM:SS em todo o sistema  changelogs, handoffs, SSOT, lobes, @BOOT  T0 agora | `[2026-04-12]`  DONE [2026-04-12]
- [ ] **GOV-014** Protocolo T0/T1 (NC-CFG-DS-003, lobes DS-000/001/002, frentes paralelas DS-A/DS-B)   infra DONE, formalizar apenas  | `[2026-04-12]`
- [x] **AGENT-203** `mentor_step_0()`  Mentor Mode completo  DONE [2026-04-11]

---

##  FASE 1  PR-MCP (25 min)  PRXIMO AGORA

### Objetivo: Policy automtica + agentes identificados

- [ ] **PRE-1** `mentor_step_0` l `NC-CFG-FR-002.yaml` em vez de dict hardcoded
  - Micro: substituir `policy_rules = {"R01": ...}` por `yaml.safe_load(policy_path)`
  - Arquivo: `01_neocortex_framework/neocortex/mcp/sub_server.py`
  - ~20 linhas | Desbloqueador: nenhum

- [ ] **PRE-2** `--role` no argparse do sub_server
  - Micro: `parser.add_argument("--role", choices=["courier","engineer","guardian"], default="courier")`
  - Arquivo: `sub_server.py` | ~15 linhas

---

##  FASE 2  ORCH-301/302 (~2h)  DESBLOQUEADOR MCP

### Objetivo: MCP 100% funcional + DeepSeek Reasoner ativo end-to-end

- [x] **ORCH-301a** `_send_task()` real via HTTP IPC  DONE [2026-04-11]
  - Micro: Substituir stub por `urllib.request.urlopen POST /task`
  - Arquivo: `neocortex/mcp/tools/NC-TOOL-FR-016-subserver.py`

- [x] **ORCH-301b** `role` + `agent_id` no spawn  DONE [2026-04-11]
  - Micro: Passar `--role {role}` e `--http-port {port}` no subprocess.Popen do spawn
  - Arquivo: NC-TOOL-FR-016

- [x] **ORCH-302** `neocortex_task` via HTTP no sub_server  DONE [2026-04-11]
  - Micro: `BaseHTTPRequestHandler` com `POST /task` + `GET /health`
  - `start_http_server()` daemon thread antes do `server.run(transport="stdio")`
  - Arquivo: `sub_server.py`

- [x] **ORCH-304** Validao: `py_compile` ambos os arquivos OK  DONE [2026-04-11]
  - `sub_server.py OK` | `NC-TOOL-FR-016-subserver.py OK`
  - HTTP layer tested: GET /health + POST /task funcionais (sem LLM = prompt_ready)
  - Criterio: DeepSeek retorna resposta via tool call  aguarda Ollama ativo

** Aps ORCH-304: 20 ferramentas + ~70 aes em produo real.**

---

##  FASE 3  REFATORAO: 22  10 TOOLS CONSOLIDADAS (+ 130 AES)

> **ADR [2026-04-11]:** As 22 tools atuais so consolidadas em 10 tools por domnio lgico.
> Cada nova tool absorve 2-4 tools existentes (arquivadas em DIR-ARC-FR-001) e expande aes.
> **Deve ser feita ANTES de adicionar novas capacidades (A2A, gateway, etc.).**
> Detalhe completo de aes: `[Antigravity brain]/implementation_plan.md`

### Ordem de implementao (risco crescente)

| Ticket | Nova Tool | Absorve (arquivar) | Aes novas-chave | Status |
|---|---|---|---|---|
| **FR-021** | `neocortex_memory` | 001-cortex, 009-lobes, 014-search, 013-report, 007-init | `lobe.list_active`, `lobe.get_content`, `lobe.activate`, `lobe.deactivate`, `lobe.search`, `lobe.list_all`, `lobe.get_checkpoint_tree`, `cortex.get_full`, `cortex.get_section`, `cortex.get_aliases`, `cortex.get_workflows`, `cortex.validate_alias`, `manifest.generate`, `manifest.update`, `manifest.query`, `manifest.list`, `manifest.generate_all`, `search.advanced` |  PENDING T0 REVIEW [2026-04-12] |
| **CC-001-A** | `Claude Code Leak Analysis` | (pesquisa externa) | `memory.arch`, `orchestration.coordinator`, `python.engine`, `tools.schema` |  PENDING T0 REVIEW [2026-04-12] |
| **CC-001-B** | `Claude Code Leak Analysis B` | (pesquisa externa) | `memory.arch`, `orchestration.coordinator`, `python.engine`, `tools.schema` |  PENDING T0 REVIEW [2026-04-12] |
| **FR-022** | `neocortex_session` | 004-checkpoint, 031-savepoint, 012-regression | `atomic.begin/commit/rollback` |  PENDING T0 REVIEW [2026-04-12] |
| **FR-023** | `neocortex_orchestration` | 002-agent, 016-subserver, 017-task, 010-peers | `hierarchy.delegate`, `pipeline.dag`, `broadcast.by_role` |  PENDING T0 REVIEW [2026-04-12] |
| **FR-024** | `neocortex_governance` | 015-security, 008-ledger | `policy.check`, `audit.replay`, `compliance.report`, `lock.validate`, `rule.list`, `session.contracts`, `violation.log`, `ssot.diff` |  DONE [2026-04-12] |
| **FR-025** | `neocortex_system` | 005-config, 011-pulse | `pulse.schedule_custom`, `config.diff`, `system.diagnostics` |  DONE [2026-04-12] |
| **FR-026** | `neocortex_intelligence` | 000-brain, 003-benchmark, 013-report | `brain.critique`, `cost.estimate`, `analytics.efficiency` |  PENDING T0 REVIEW [2026-04-12] |
| **FR-027** | `neocortex_knowledge` | 019-manifest, 007-init, 018-manifest-lobe | `project.boot_context`, `docs.generate_readme` |  PENDING T0 REVIEW [2026-04-12] |
| **FR-028** | `neocortex_export` | 006-export | `export.docker_compose`, `export.obsidian`, `export.readme` |  DONE [2026-04-12] |
| **FR-029** | `neocortex_health` | *(novo  OBS-001 + AGENT-206)* | `log.tail`, `metrics.live`, `alert.set` |  DONE [2026-04-11] |
| **FR-030** | `neocortex_context` | *(novo  token economy)* | `context.budget_status`, `session.handoff`, `cache.warm` |  DONE [2026-04-11] |
| **BOOT-001** | `System Manifest Update` | (nenhum) | `manifest.update`, `lobe.integrate` |  PENDING T0 REVIEW [2026-04-12] |

**Resultado esperado:** 22 tools  10 tools no handshake MCP | ~80 aes  ~130 aes com lgica de domnio

**Micro tasks por tool (padro):**
1. Criar `NC-TOOL-FR-0XX-nome.py` com `register_tool(mcp)` e todas as aes
2. Testar cada ao individualmente via MCP call
3. Arquivar as tools absorvidas em `DIR-ARC-FR-001-archive-main/tools_legacy/`
4. Atualizar `@SSOT` (NC-NAM-FR-001) com changelog
5. Rodar `NC-SCR-FR-003` para regenerar o manifesto

> **NOTA:** FR-029/030 (`health` e `context`) so novas  sem migrao, iniciar primeiro.
> FR-024 (`governance`) toca arquivos em @LOCKS  requer autorizao T0 explcita.
> FR-026 (`intelligence`) inclui `brain.critique`  **auto-learning loop** (captura outcomes  retroalimenta lobes).

### Sandbox Modular (paralelo  Fase 3)
- [] **SAND-001** `neocortex_config_dev.yaml`  instncia dev isolada (porta 8766, lobe_dir separado)  DONE [2026-04-12]
- [] **SAND-002** `start_neocortex_dev.bat`  launcher da instncia dev  DONE [2026-04-12]
- [ ] **SAND-003** White-label templates em `DIR-TMP-FR-001-templates-main/`
  - `README_template.md`, `neocortex_config_template.yaml` (sem API keys), `onboarding_checklist.md`
- [x] **HUD-003** `NeoCortex_HUD.bat` v2  display ASCII hierrquico (TIER-04) de lobes, handoffs PENDING_REVIEW automtico, tickets T1 ativos via NC-CFG-DS-003  DONE [2026-04-12T16:45:00]
- [ ] **HUD-004** Dashboard web interativo de lobes (Opo B)  checkboxes de ativao/desativao, tree hierrquico clicvel | **ps-MCP Fase 1** | depende ORCH-301

---



##  FASE 4  SECURITY HARD ENFORCEMENT (~6h)

### Objetivo: Enforcement automtico  sem depender de IA seguir regras

- [x] **SEC-401** `neocortex_guardian`  Runtime interceptor  [2026-04-11]
  - `lock_guard.py` criado: l `NC-SEC-FR-001-atomic-locks.yaml`, DENY-by-default, hot-reload 60s, violation log
  - `SecurityService.validate_access()` fallback corrigido: `access_granted=True`  `False` (brecha eliminada)
  - Mtodos `check_path_write()` e `check_tool_allowed()` adicionados ao SecurityService

- [x] **SEC-402** `.git/hooks/pre-commit`  R01 naming + R08 db/wal/cache bloqueados  [2026-04-11]
  - `.git/hooks/pre-commit` que rejeita commit se arquivo no tem prefixo `NC-`

- [ ] **SEC-403** Rate limiting por agente no guardian
  - Consumes `NC-CFG-FR-001-agent-policy-template.yaml`  aplica `limits.*` por role

- [ ] **SEC-404** Auto-repair dos stores
  - Heartbeat que detecta corrupo em DuckDB/diskcache e faz rollback automtico

- [ ] **SEC-405** JWT/OAuth 2.1 para transports HTTP
  - Integra com `neocortex_auth` (FR-027)

---

##  FASE 4b  STEP -1: SAVE POINTS & ROLLBACK (~4h)

### Objetivo: Camada de segurana transacional  agentes autnomos sem medo de corromper estado

| Mecanismo | Quando | Funo |
|---|---|---|
| **STEP -1 (Save Point)** | ANTES de qualquer escrita | Snapshot diff do estado atual |
| **STEP 0 (Mentor/Validao)** | ANTES da execuo | Valida locks + policy (j implementado) |
| **STEP +1 (Rollback)** | APS falha ou exceo | Reverte para o save point |

**O que j temos:**
- `PulseScheduler`  checkpoints peridicos (5min)  NO  pr-ao
- `CheckpointService.force_checkpoint()`  snapshot completo  NO faz diff
- `LedgerStore` (DuckDB ACID)  suporta snapshots  NO usado para rollback

- [x] **SAVE-001** `capture_diff()` no `LedgerService` e `LobeService`  PRE-1 via PolicyLoader  [2026-04-11]
  - PolicyLoader (`policy_loader.py`) criado: l `NC-CFG-FR-001` em runtime, hot-reload 120s
  - `mentor_step_0` agora consome `policy.get_limits(role)` + `get_mentor_prefix(role)` + `record_token_usage()`
  - Token truncation automtico quando prompt > `max_tokens_per_task`
  - HUD: painel Compliance Heartbeat adicionado (real checks, sem mock, 5s refresh)
    - 7 padres de governana com status verde/mbar/vermelho
    - 3 agent heartbeats via TCP (courier:11435, engineer:11436, guardian:11437)

- [x] **SAVE-002** `save_point_service.py`  STEP -1 capture + STEP +1 rollback  [2026-04-11]
  - Micro: Wrapper antes de cada tool call de escrita (create/update/delete/spawn/execute)
  - Detecta `is_write_action()`  captura snapshot  armazena com TTL 10min
  - Arquivo: `neocortex/mcp/server.py` | ~60 linhas

- [x] **SAVE-003** `handle_task` integrado  rollback automtico no except  [2026-04-11]
  - Micro: Em `except Exception:` no handle_task  aciona rollback automtico
  - Arquivo: `sub_server.py` + middleware | ~30 linhas

- [x] **SAVE-004** `NC-TOOL-FR-031-savepoint.py`  4 aes MCP (list_active, rollback, discard, get_status)  [2026-04-11]
  - Aes: `list_active`, `rollback`, `discard`, `get_diff`
  - Arquivo: `neocortex/mcp/tools/NC-TOOL-FR-031-savepoint.py` | ~80 linhas

- [x] **SAVE-005** Validao ps-execuo configurvel  DONE [2026-04-13]
  - `NC-SVC-FR-014-dry-run-preview.py` (183L, py=OK, ruff=0V)
  - Preview dry-run antes de qualquer escrita, integrado com guardian

**J feito (itens que aceleram SAVE):**
- [x] **HUD-001** `neocortex_hud.py`  painel de controle tkinter com bandeja  [2026-04-11]
  - Desktop launcher: `NeoCortex_HUD.bat` na rea de Trabalho
  - Atalho `.lnk` na rea de Trabalho
  - Fix: `PROJECT_ROOT` corrigido para apontar para `01_neocortex_framework`



---

##  SPRINT PICOCLAW  FASE PIC-001 (Prximos 3 tickets)

> **Objetivo:** Conectar T0 (Antigravity) ao ecossistema PicoClaw sem lock-in. Governana permanece 100% no NeoCortex.
> **Princpio:** PicoClaw = adapter descartvel. Se falhar, troca-se sem reescrever nada.
> **Decises gravadas em:** NC-LBE-INT-001/002/003 (lobes permanentes)

### Lobes de Documentao (Concludo 2026-04-13)
- [x] **LOBE-INT-001** NC-LBE-INT-001-picoclaw-architecture.mdc  DONE [2026-04-13]  605L, Agente A (59520)
- [x] **LOBE-INT-002** NC-LBE-INT-002-opencode-architecture.mdc  DONE [2026-04-13]  501L+, Agente B (44624)
- [x] **LOBE-INT-003** NC-LBE-INT-003-antigravity-integration.mdc  DONE [2026-04-13]  249L+, Agente C (32763)

### Prximos Tickets (Sprint Atual)
- [x] **PIC-001** Instalar PicoClaw no Windows  DONE [2026-04-13]
  - v0.2.6 via `winget install Sipeed.PicoClaw`  TUI funcional
  - `WARNING:` binrio no no PATH automtico  use caminho completo ou reinicie shell
  - Gateway ativar via TUI menu `g`  Gateway Management

- [x] **PIC-002** `config.json` PicoClaw com NeoCortex MCP + DeepSeek + exec  DONE [2026-04-13]
  - `NC-CFG-PIC-001-picoclaw-config.json`  66L, JSON vlido
  - DeepSeek-v3 com API key real, NeoCortex MCP stdio, exec + DuckDuckGo
  - T0 completou: Agente B havia entregue verso mnima (8L  66L)

- [x] **PIC-003** `NC-TOOL-FR-036-picoclaw.py`  bridge T0  PicoClaw gateway  DONE [2026-04-13]
  - 267L | `py_compile` OK | `ruff` 0 violations | 0 `print()`
  - 3 aes: `task.send`, `gateway.health`, `gateway.status`
  - HTTP via `urllib` stdlib  zero deps externas

---

##  FASE 5  A2A + GATEWAY + SDK RUST (Futuro  requer Fase 3+4b completas)

> **Pr-req:** ORCH-301 funcional + SAVE-005 + FR-027 (auth) + Tool Refactor (10 tools) concludo.
> **ADR-SDK-001:** O SDK Rust encapsula APENAS o Gateway. Core Python permanece aberto.

### Hierarquia e Rede
- [ ] **HIER-001** Hierarquia multi-nvel: T0T1T2T3 com `hierarchy.delegate`
- [ ] **HIER-002** Peer discovery automtico (mDNS / registry)
- [ ] **HIER-003** Load balancing entre instncias
- [ ] **CONN-001** gRPC stubs para comunicao inter-node
- [ ] **CONN-002** Tailscale/mTLS para segurana de rede
- [ ] **CONN-003** MCP Gateway com Traefik
- [ ] **INFRA-001** Redis para PubSub real (substitui in-process)
- [ ] **INFRA-002** Docker Compose com 7 portas pr-configuradas
  - Porta 8765: MCP Server principal  8766: A2A Gateway  8767: Courier  8768: Engineer  8769: FastAPI Web  8770: Webhook

### Capacidades Avanadas (requer Fase 3 concluda  antes eram FR-021030 legado)
> Estas capacidades foram movidas da Fase 3 antiga. Dependem das 10 tools refatoradas estarem estveis.

- [ ] **A2A-001** `neocortex_gateway`  register, deregister, list, route, stats
- [ ] **A2A-002** `neocortex_a2a`  publish_card, discover, delegate, status, negotiate
- [ ] **A2A-003** `neocortex_workflow`  create, execute_step, pause, resume, status, cancel
- [ ] **A2A-004** `neocortex_vector`  embed, upsert, search, delete (OPT-012)
- [ ] **A2A-005** `neocortex_pubsub`  publish, subscribe, get_pending, replay
- [ ] **A2A-006** `neocortex_auth`  issue_token, validate, revoke, list_sessions (SEC-405)
- [ ] **A2A-007** `neocortex_cache`  set, get, invalidate, stats (OPT-011)
- [ ] **A2A-008** `neocortex_discovery`  register, discover, deregister, health_all
- [ ] **A2A-009** `neocortex_observability`  log_chain, get_trace, export_audit, metrics

### SDK Rust Gateway (somente aps Fase 5 estabilizada)
- [ ] **SDK-001** Rust daemon: Gateway + A2A protocol (binrio nico)
- [ ] **SDK-002** Rust embeds FastAPI Web Panel como HUD web
- [ ] **SDK-003** GitHub Release: `.exe` porttil  "baixa e roda"
- [ ] **SDK-004** CI/CD GitHub Actions: build Rust + test + release

---

##  FASE 6  DISTRIBUIO & PyPI (Curto/Mdio Prazo  requer Fase 3 concluda)

> **ADR-SDK-001:** PyPI distribui o core Python. `.exe` Rust  Fase 5. Ordem: PyPI primeiro.

### Core Python  PyPI
- [ ] **SDK-010** `pyproject.toml` com `[project]` e `[tool.setuptools]` para PyPI
- [ ] **SDK-011** `pip install neocortex-mcp`  `neocortex-server` CLI entry point
- [ ] **SDK-012** GitHub Actions: auto-publish to PyPI em tag `v*`
- [ ] **SDK-013** PyInstaller `.exe` para Windows (sem Rust  MVP rpido)
  - Zero dependncia Python para usurio final, ~2h de trabalho

### Documentao e White-Label
- [ ] **T1-002** CLI client para uso local
- [ ] **TEST-501** Integration Test Suite completo
- [ ] **TEST-502** Stress Test Hybrid (Titanomachy)
- [ ] **DOC-503** White-Label Documentation
- [ ] **DOC-504** Final ROI Report
  - Inclui: tabela pr/ps-MCP, custo por sesso, KV cache hit rate

---

##  CONTAGEM TOTAL

| Fase | Tools | Aes | Status |
|---|---|---|---|
| Hoje (L0+L1) | 20 | ~70 |  |
| + Fase 1+2 | 20 | ~70 |  ~2.5h |
| + Fase 3 completa | **30** | **~114** |  ~23h |
| + Fase 4 SEC | **32** | **~125+** |  ~6h |
| + Fases 5+6 | N/A | N/A |  Futuro |

---

##  SANITIZAO CONCLUDA [2026-04-11]

### Arquivados em DIR-ARC-FR-001-archive-main (auditado 2026-04-11)
- `NC-TODO-FR-001-project-roadmap.md` (verso antiga)
- [x] `NC-TODO-FR-001-project-roadmap-v6-stability.md`
- [x] `NC-TODO-FR-001-project-roadmap-v7-combined.md`
- [x] `NC-TKT-FR-001-tickets.md`
- [x] `CHECKPOINT_AUDIT_2026-04-10.md`
- [x] `NC-SES-FR-001-session-status-2026-04-10.md`
- [x] `NC-AUD-FR-001-audit-findings-2026-04-10.md`
- [x] `SANITIZATION_CHECKLIST.md`
- [x] `STATUS.md`
- [x] `README_MCP_NEOCORTEX.md`
- [x] `DEEPSEEK_API_SUMMARY.md`
- [x] `BENCHMARKS.md` + `BENCHMARKS_HYBRID.md`
- [x] `NC-DOC-FR-003-turboquant-prompt.md`
- [x] `NC-PLN-FR-001-optimization-plan.mdc`

### Pendente  Renomear (R01 conflict)
- [ ] **SEC-402-prep** `NC-RULE-001-workspace-standards.mdc`  `NC-RULE-005-workspace-standards.mdc`

---

##  CHECKLIST FIM DE SESSO  R20 (sempre)

```
 @SSOT (NC-NAM-FR-001) atualizado + changelog [YYYY-MM-DD]
 %DONE neste @ROADMAP para cada ticket concludo
 @POPULATE rodado (se algum lobe foi criado/alterado)
 @BOOT atualizado (tickets + lobos + agentes)
 Nenhum *.db / *.wal / __pycache__ / neocortex_config.yaml commitado
```

---

##  Fase Ps-MCP  Tickets adicionados [2026-04-12]

> Executar APS concluso das 10 tools MCP e estabilizao da fila N-workers.

### LOBE-INT-003  Lobe de Integrao Antigravity
**Prioridade:** ALTO | **Status:**  DONE [2026-04-13]
**Objetivo:** Documentar o papel de T0 (Antigravity) como orquestrador central, hierarquia de agentes, 34 ferramentas MCP, protocolos de delegao e integrao com PicoClaw/OpenCode.
**Entregas:**
- `01_neocortex_framework/lobes/NC-LBE-INT-003-antigravity-integration.mdc`  Lobe completo com 12 sees obrigatrias

### INT-004  Lobe de Integrao Mission Control
**Prioridade:** ALTO | **Status:**  DONE [2026-04-14]
**Objetivo:** Documentar a integrao com o painel Kanban, webhook e adaptadores genricos para o Mission Control.
**Entregas:**
- `02_memory_lobes/NC-LBE-INT-004-mission-control.mdc`  Lobe de integrao

### INT-005  Lobe de Integrao Pixel Agents
**Prioridade:** ALTO | **Status:**  DONE [2026-04-14]
**Objetivo:** Especificar e documentar a bridge JSONL e o gerenciamento de logs visuais do ecossistema Pixel Agents no OpenCode.
**Entregas:**
- `02_memory_lobes/NC-LBE-INT-005-pixel-agents.mdc`  Lobe de integrao

### DOC-001  Documentao Humana (Remover "ar de Frankenstein")
**Prioridade:** MDIO | **Bloqueado por:** MCP completo
**Objetivo:** Qualquer dev/parceiro que clona o repo entende em <5 min o que  o NeoCortex e como usar.
**Entregas:**
- `README.md` principal: diagrama ASCII da arquitetura + 3 casos de uso
- `QUICKSTART.md`: do zero ao MCP rodando em 10 passos
- `DIR-DOC-FR-001-docs-main/NC-DOC-FR-002-human-guide.md`: guia completo sem jargo tcnico interno
- Nomenclatura NS-* em ingls ou PT explicada nos headers

### MCP-WQUEUE  NC-TOOL-FR-030-worker-queue.py (Worker Queue como MCP Tool)
**Prioridade:** ALTO | **Bloqueado por:** NC-DS-027 (TicketValidator concludo)
**Objetivo:** O sistema atual de fila YAML (NC-CFG-DS-004) se torna uma MCP tool nativa  atmica, sem race conditions, qualquer IA/ferramenta acessa via protocolo padro.
**Aes MCP planejadas:**
- `claim_task(worker_id, task_id)`  claim atmico com lock de arquivo
- `release_task(worker_id, status, lines_added, files_created)`  finaliza + gera handoff
- `list_queue()`  snapshot AVAILABLE/CLAIMED/DONE
- `get_task(task_id)`  l ticket YAML + valida integrity_hash
- `check_regression(error_description)`  consulta regression buffer antes de executar
- `register_zone(worker_id, write_zone)` / `release_zone(worker_id)`  write-zone registry
**Por que  uma tool e no s YAML?**: Atomicidade real (file lock vs. 5s wait), rastreabilidade via MCP, reutilizvel por Pico Claw, outros LLMs, CI/CD.

### DOC-002  Manifest Review e Expanso de Lobos
**Prioridade:** MDIO | **Bloqueado por:** MCP-WQUEUE
**Objetivo:** Qualquer IA que entra no projeto via @BOOT chega a 100% de contexto em <10 tokens de leitura.
**Entregas:**
- Revisar e consolidar NC-MAN-FR-001 (JSON/MD) com novos arquivos DS e core/services
- Criar lobe `$WORKER_PATTERNS` capturando prompts, IDs port-based, gates, regression
- Criar lobe `$INDUSTRIALIZATION` documentando N-workers, claim protocol, entry locks
- Atualizar @BOOT com referncia aos novos lobos
