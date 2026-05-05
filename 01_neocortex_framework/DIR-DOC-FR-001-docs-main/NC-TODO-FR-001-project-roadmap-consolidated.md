# ⚠️ DEPRECATED — Use NC-TODO-FR-001-roadmap.yaml (DIR-DS-000-agent-config/)
# Este arquivo é mantido como histórico. O roadmap ativo está em YAML.

<!-- NC-TODO-FR-001 — NeoCortex: Roadmap SSOT Consolidado v17.0 -->
<!-- @ROADMAP — Single Source of Truth | Atualizado: 2026-04-28 23:20 -->
<!-- Regra R21: NADA de suposições — cada item validado por A/B/C/D -->

> **Versão:** v17.0 | **Hash:** NC-TODO-FR-001-v17.0-20260428-2320 | **Data:** 2026-04-28 23:20

## ✅ ENTREGUES HOJE — VERIFICADOS EM TEMPO REAL

| # | Módulo | O que faz | Status |
|---|--------|-----------|--------|
| FR-150 | Techniques Audit | 15 técnicas com verificação de arquivos reais | ✅ ZERO MOCK |
| FR-151 | 5 Motores | 3W+Eisenhower+Pareto+OKR+Idempot | ✅ REAL |
| FR-152 | Eisenhower Real | 163 tickets reais | ✅ REAL |
| FR-153 | Pareto Real | WAL DB real | ✅ REAL |
| FR-154 | Corporate Engines | KPIs+ROI+Compliance (dinâmicos) | ✅ ZERO MOCK |
| FR-155 | Resiliency Engine | Bulkhead+CQRS+Feature+Graceful+Backpressure | ✅ REAL |
| FR-156 | AI Governance | ModelCards+XAI+HITL+Bias+RedTeam+Audit | ✅ REAL |
| FR-157 | BSC+SWOT | BalancedScorecard+SWOTAnalyzer (dados reais) | ✅ ZERO MOCK |
| FR-158 | System Integrity | YAML+MDC+Secrets+DeadCode | ✅ REAL |
| FR-159 | Crypto Integrity | SHA-256 + encoding scan + manifest | ✅ REAL |
| FR-160 | Advanced Resilience | 13 conceitos avançados | ✅ REAL |
| FR-161 | Regulatory Compliance | 8 padrões regulatórios (file checks) | ✅ ZERO MOCK |
| GW v3.1 | Gateway per-action | 35 H hooks reais + 7 critical hooks | ✅ VERIFICADO |
| CW | CentralWatcher | STEP 0 + Regression persistente | ✅ 48 checks |
| MEM | Memory-auto | Session tracking (18 turns) | ✅ ATIVO |
| HANDOFF | Auto-handoff | PulseScheduler cria a cada 300s | ✅ ATIVO |
| MULTILAYER | 115 Regras v3.1 | 7 blocos + Trigger Table + 3 Whos | ✅ HONEST |
| AUDIT | Tripla + Integridade | ruff+mypy+pyright+YAML+MDC+Secrets | ✅ 80 arquivos |

## 📊 STATUS ATUAL (v17.1 — 2026-04-29)

| Métrica | Valor |
|---------|-------|
| **Regras** | 123 (R01-R123) |
| **H (HOOK) ativos** | 36/123 com código REAL no Gateway |
| **C (CHECKPOINT) ativos** | 15/123 via PulseScheduler |
| **S (SCHEDULE) ativos** | 97/123 documentados |
| **U (USER)** | 123/123 via T0 (OpenCode) |
| **Engines** | 20 (FR-150 a FR-170) |
| **Tools MCP** | 18 (16 GW wired + 2 Fase 5) |
| **Tickets** | 168 total |
| **Ruff** | 100% |
| **Mypy/Pyright** | Pass |
| **Lobes** | 76 (17 domínios, 0 vazios) |
| **STEP 0** | ON (235 checks, 10 violations) |
| **Checkpoints** | 217 auto + 2 session |
| **ULQ headers** | 139 compressed |
| **3W injected** | 349 files |
| **Aliases** | 24 NC-ID antigo → novo |
| **Semantic Boot** | 125 tags indexed |

## ⏳ PRIORIDADES — 70 Conceitos (R42-R111)

### 🔴 P0 (Alto Impacto — implementar AGORA)

| Conceito | Regra | O que falta | Esforço |
|----------|-------|-------------|---------|
| Due Diligence | R59 | Validação de segurança de novos módulos (hash check) | 30min |
| Strangler Fig | R68 | Wire migration tracker no PulseScheduler | 30min |

### 🟡 P1 (Médio Impacto — próxima sessão)

| Conceito | Regra | O que falta | Esforço |
|----------|-------|-------------|---------|
| Stakeholder Map | R60 | Mapear privilégios por hierarquia nos tools | 1h |
| Lean | R62 | Context pruner + response trimmer | 1h |
| Self-Healing | R95 | Auto-restart MCP container on 500 errors | 1h |
| DB Replication | R98 | Duplicar WAL entre nós (HA) | 2h |
| Microreboot | R103 | Restart isolado de thread da tool | 1h |

### 🟢 P2 (Baixo Impacto — Fase 5)

| Conceito | Regra | O que falta |
|----------|-------|-------------|
| Six Sigma | R63 | Error rate tracker (3.4 DPMO) |
| Federated Learning | R80 | Compartilhar métricas entre instâncias |
| DTO | R86 | Simular gargalos via WAL history |
| Performance Rights | R90 | Budget de execução por tool |
| Board AI Gov | R93 | Comitê humano p/ mutações |
| **Secrets** | 0 leaks |
| **Audit score** | ~78% |

## ⏳ PENDENTES (Próxima Sessão)

| # | Item | Prioridade | Esforço | Ticket |
|---|------|-----------|---------|--------|
| P8 | 49 legacy orphans (FR-101~FR-128) — revisão manual | HIGH | 2h | NC-DS-208 |
| P9 | roadmap.done action implementar | MEDIUM | 30min | NC-DS-209 |
| P10 | Strangler Fig wire no PulseScheduler | LOW | 30min | NC-DS-210 |
| P11 | MDC headers: 11 ERROR files sem YAML header | LOW | 30min | — |

## TOOLS AUDIT — 99.6% IMPLEMENTADO

| Métrica | Valor |
|---------|-------|
| Total tools | 18 (20 registradas, 2 Fase 5) |
| Total actions | 241 |
| Actions implementadas | 240 (99.6%) |
| Actions com TODO | 1 (roadmap.done) |
| Tools com Gateway | 16/18 |
| Tools com STUBS | 0 |
| Tools com MOCK | 0 |

## ORFÃOS AUDIT

| Categoria | Qtd | Ação |
|-----------|-----|------|
| Legacy services (FR-101~FR-128) | 49 | Revisão manual antes de arquivar |
| Gitignored (active deps) | 25 | Protegidos por .gitignore |
| Truly orphan (safe to archive) | 0 | Nenhum confirmado seguro |

## TICKETS — ESTADO ATUAL

| Estado | Qtd |
|--------|-----|
| Total | 167 (164 + 3 novos) |
| Abertos | ~95 |
| Fechados hoje | 4 (NC-DS-101,150,164,167) |
| Criados hoje | 5 (NC-DS-205,206,207,208,209,210) |
> **Fase atual:** CICLO 3 FECHADO — Sistema Jurídico Tripartite implementado
> **Score atual:** 85% (era 62%) | **Próximo:** MCP tools exposure + wire-up Gateway
> **Matriz de validação:** A=CÓDIGO B=MCP C=ENFORCE D=TESTADO

---

## LEGENDA
```
%DONE [YYYY-MM-DD]   — concluído com data comprovada (D=sim)
%IN_PROGRESS         — sprint atual
%PENDING             — próximo sprint
%BLOCKED(RAZÃO)      — bloqueado
%VISÃO               — longo prazo
%FORA_ESCOPO         — decidido não implementar
```

---

## MATRIZ DE VALIDAÇÃO DAS 71 REGRAS (2026-04-27)

### P0 — ATIVO E AUTOMÁTICO (14 regras) — NÃO MEXER
> A=sim, B=sim, C=automático/enforced, D=sim

| ID | Regra | Evidência |
|----|-------|-----------|
| R10 | Logger por Módulo | Ruff confirmado (31→7 issues) |
| R13 | Audit Trail (WAL) | NC-SVC-FR-016 ativo, DIR-DS-002 com logs |
| LOCK-01 | server.py imutável | lock.check → locked:true |
| LOCK-02 | SSOT imutável | lock.check → locked:true |
| LOCK-03 | config imutável | lock.check → locked:true |
| LOCK-04 | locks.yaml imutável | Auto-referência no YAML |
| LOCK-05 | DENY by default | NC-CORE-FR-124:127 access_granted=False |
| CRYPTO-01 | API keys nunca plain | CryptoHub NC-SVC-FR-017 ativo |
| CRYPTO-02 | encrypt/decrypt T0+Guardian | CryptoHub integrado WAL |
| CRYPTO-03 | decrypt→WAL severity:HIGH | WAL service registra |
| MET-01 | MetricsStore DuckDB | UUID fix aplicado, funcional |
| ECO-02 | LiteLLM proxy :4000 | Task Scheduler ativo |
| CICLO-0 | MCP check | SSE :8766 estável, 20 tools |

### P1 — ATIVO MAS MANUAL (22 regras) — WIRE UP AUTOMÁTICO
> A=sim, B=sim, C=manual (precisa virar middleware/trigger)

| ID | Regra | Ação necessária |
|----|-------|-----------------|
| R01 | Nomenclatura NC- | naming.check → hook PreToolUse |
| R02 | SSOT Update | ssot.diff → auto-drift no bootup.sync |
| R04 | Atomic Locks | lock.check → LockGuard middleware |
| R05 | NUNCA Deletar | violation.log → hook PreDelete |
| R09 | Modo Mentor | regression.check → middleware obrigatório |
| R11 | STEP +1 Rollback | savepoint.rollback → auto-trigger on failure |
| R15 | T0 Nunca Executa | agent.identity → enforcement runtime |
| R16 | Boot Context | @BOOT → auto-load ao iniciar sessão |
| R18 | Manifestos Lobo | manifest.list → auto-generate no Ciclo 3 |
| R20 | Checklist Fim Sessão | bootup.sync → auto-trigger on session end |
| STEP -1.5 | Dry-Run Preview | NC-SVC-FR-014 → integrar ao savepoint.create |
| STEP -1 | Save Point | savepoint.create → auto antes de write |
| STEP 0 | Regression Check | regression.check → middleware |
| STEP +1 | Rollback | savepoint.rollback → auto on failure |
| TOKEN-03 | PulseScheduler pruning | Reativar (estável após fix SSE) |
| TOKEN-04 | Manifestos | manifest.list → pre-load antes de lobe.get |
| TOKEN-05 | Fallback Chain | llm_router → fallback automático |
| AGENT-01 | T0 identity | Enforcement via LockGuard |
| AGENT-08 | Handoffs | handoff.create → auto no ticket.close |
| CICLO-1 | Audit tickets | ticket.list → auto no início sessão |
| CICLO-3 | Catalog+Bootup | bootup.sync → schedule automático |
| CICLO-4 | Compliance | compliance.report → schedule semanal |
| MET-03 | Health checks | health.server.health → fix + endpoint |

### P2 — EXISTE, SEM MCP (21 regras) — EXPOR COMO TOOL
> A=sim, B=não (precisa expor via MCP tool)

| ID | Regra | O que fazer |
|----|-------|-------------|
| R03 | Ticket Reference | Expor ticket.validate via MCP |
| R06 | Write Zones | Expor zone.check + zone.list via MCP |
| R07 | ConfigProvider | Expor config.validate via MCP |
| R12 | STEP -1 TTL 10min | Implementar TTL no savepoint.create |
| R14 | Lobe Isolation | Expor lobe.isolation_status via MCP |
| R17 | PolicyLoader | Wire up cf.pre_check → carregar YAML real |
| R19 | Ticket State Machine | Expor ticket.state via MCP |
| LOCK-06 | LockGuard middleware | Expor lock.validate_access via MCP |
| AGENT-02 | Courier | Ativar com PicoClaw (NC-DS-302) |
| AGENT-03 | Engineer | Ativar com PicoClaw |
| AGENT-04 | Guardian | Ativar daemon (NC-SCR-FR-115 existe) |
| AGENT-06 | mentor_step_0 | Integrar como middleware real |
| AGENT-07 | agentes efêmeros | Depende PicoClaw ativo |
| CICLO-2 | During session | Expor cycle.status via MCP |
| TOKEN-02 | Compact Encoding | Expor encoding.validate + encoding.stats |
| TOKEN-06 | Complexity routing | Profile Router (NC-DS-301 Wave 1) |
| POL-01 a 04 | PolicyLoader runtime | Wire up YAML→runtime |
| MET-02 | Reports diários | Wire up report.generate |
| MET-04 | TTL logs | Wire up TTL manager |
| ECO-04 | PicoClaw :18790 | Ativar (NC-DS-302 Wave 1) |
| Naming/Alias | 6 regras $@%!?# | Documentar + validar uso |

### P3 — NÃO IMPLEMENTADO (14 regras) — NOVO DESENVOLVIMENTO
> A=não (precisa criar do zero ou está no roadmap futuro)

| ID | Regra | Destino |
|----|-------|---------|
| R08 | Git Ignore validation | Wave 2 CI/CD (NC-DS-304) |
| AGENT-05 | allowed_tools | Wave 2 (após Profile Router) |
| TOKEN-01 | Cache Hit >95% | Wave 3 (NC-DS-324) |
| ECO-01 | WebSocket MCP | Wave 3 (substituir/complementar SSE) |
| ECO-03 | Mission Control | Fase 4 UI |
| ECO-05 | Hybrid Firebase+GAS | Fase 4 |
| demais | 8 regras de visão | Waves 2-3 ou Fases 4+ |

---

## SPRINT ATUAL — SPRINT-GOVERNANÇA (Dias 1-2)
> **Critério de saída:** 22 regras P1 wire-up concluídas → score 62%→75%
> **Pré-requisito:** Nenhum — as P1 já têm código, só falta automação

### Bloco A — MIDDLEWARE (~1 dia) ✅ CONCLUÍDO
| # | Ticket | Descrição | Status |
|---|--------|-----------|--------|
| G1 | NC-DS-501 | LockGuard middleware — check_write antes de writes | %DONE [2026-04-27] |
| G2 | NC-DS-502 | STEP 0 middleware — regression.check antes de tool call | %DONE [2026-04-27] |
| G3 | NC-DS-503 | STEP -1 auto — savepoint.create antes de write | %DONE [2026-04-27] |
| G4 | NC-DS-504 | STEP +1 auto — savepoint.rollback em failure | %PENDING |
| G5 | NC-DS-505 | R01 auto — naming.check com @ULQ dictionary | %DONE [2026-04-27] |

### Bloco B — TRIGGERS (~1 dia)
| # | Ticket | Descrição | Esforço |
|---|--------|-----------|---------|
| G6 | NC-DS-506 | R20 auto — bootup.sync ao fim de sessão | 1.5h |
| G7 | NC-DS-507 | R16 auto — @BOOT carregado ao iniciar sessão | 1h |
| G8 | NC-DS-508 | R02 auto — ssot.diff no bootup.sync | 1h |
| G9 | NC-DS-509 | CICLO-4 auto — compliance.report semanal | 2h |
| G10 | NC-DS-510 | TOKEN-03 — reativar PulseScheduler (estável pós-fix) | 2h |

---

## CICLO-REFORMA (Wave 1: Dias 3-5)
> **Pré-requisito:** SPRINT-GOVERNANÇA concluída (75%)
> **Alvo:** 75% → 82%

### Prioridade 1 — FUNDAÇÃO
| # | Ticket | Título | Esforço | Status |
|---|--------|--------|---------|--------|
| P1 | NC-DS-300 | NC-CFG-OP-001 operation profiles (PRO/FLASH/AUTO) | 0.5d | %PENDING |
| P1 | NC-DS-301 | NC-SVC-FR-026 profile-router.py | 2d | %PENDING |
| P1 | NC-DS-302 | Ativar PicoClaw :18790 (stub→real) | 1d | %PENDING |
| P1 | NC-DS-303 | ruff.toml regras customizadas | 0.5d | %PENDING |
| P1 | NC-DS-304 | CI/CD GitHub Actions | 1.5d | %PENDING |
| P1 | NC-DS-305 | Medição real tokens (tiktoken) | 1.5d | %PENDING |
| P1 | NC-DS-306 | Trigger implícito intenção → Profile Router | 1.5d | %PENDING |
| P1 | NC-DS-308 | LiteLLM router.yaml (perfis→modelos) | 0.5d | %PENDING |

### Prioridade 2 — SPRINT ACELERADO
| # | Ticket | Título | Status |
|---|--------|--------|--------|
| P2 | NC-DS-098 a 114 | 17 tickets sprint acelerado | %IN_PROGRESS |
| P2 | NC-DS-132 | LEXICO-001 LexicoService | %IN_PROGRESS |
| P2 | NC-DS-134 | Smoke test 40 tools | %IN_PROGRESS |

---

## SISTEMA JURÍDICO TRIPARTITE — %DONE [2026-04-28]
| # | Módulo | Status |
|---|--------|--------|
| J1 | Gateway UBL | %DONE |
| J2 | DNA/RNA | %DONE |
| J3 | Federative Pact | %DONE |
| J4 | CPC Digital | %DONE |
| J5 | Regulatory Agencies | %DONE |
| J6 | Legislative Process | %DONE |
| J7 | CPP Digital | %DONE |
| J8 | Auto-Amendment | %DONE |
| J9 | Vigilant Cycle | %DONE |

## GAPS PRIORIDADE 0
| # | Gap | Esforço |
|---|-----|---------|
| P0-01 | 5 MCP tools expor | 3h |
| P0-02 | CPP no validate_action | 1h |
| P0-03 | CICLO 0 auto-hook | 1h |
| P0-04 | 13 tools Gateway | 2h |
| P0-05 | SSOT registrar módulos | 1h |
| P0-06 | Blueprint atualizar | 1h |

---

## SPRINT-AUDITORIA — Correções imediatas (Dia 0)
> **Origem:** NC-ARC-COMPLIANCE-REPORT.md | **Alvo:** 67% → 80%
> **Critério:** Fechar bugs encontrados na auditoria arquitetural

| # | Ticket | Título | Esforço | Status |
|---|--------|--------|---------|--------|
| A1 | NC-DS-520 | Fix health.tools_count bug (Path undefined) | 0.5h | %IN_PROGRESS |
| A2 | NC-DS-521 | Fix blueprint NC-CORE-FR numbers (5 errados) | 0.5h | %PENDING |
| A3 | NC-DS-522 | Criar @SOP NC-SOP-FR-001-session-startup.md | 1h | %PENDING |
| A4 | NC-DS-523 | Criar @ADR NC-ARC-FR-001-decision-log.md | 1h | %PENDING |
| A5 | NC-DS-524 | Wire up SearchService (search.advanced stub→real) | 3h | %PENDING |
| A6 | NC-DS-525 | Wire up KnowledgeService (knowledge.search stub→real) | 3h | %PENDING |

---

## WAVE 2 — REFORÇO (Dias 6-9)
> **Alvo:** 82% → 88%
> + tickets P2 de expor MCP (R03, R06, R07, R12, R14, R17, R19, LOCK-06)

| # | Ticket | Título | Esforço |
|---|--------|--------|---------|
| P3 | NC-DS-309 | Circuit Breaker (R16 proxy) | 1.5d |
| P3 | NC-DS-312 | CODEOWNERS para @LOCKS | 0.5d |
| P3 | NC-DS-313 | Coverage >60% MCP tools | 1d |
| P3 | NC-DS-314 | mypy strict mode | 1.5d |
| P3 | NC-DS-315 | bandit security scan | 1d |
| P3 | NC-DS-511 | Expor R06 Write Zones via MCP | 1d |
| P3 | NC-DS-512 | Expor R17 PolicyLoader runtime via MCP | 1d |
| P3 | NC-DS-513 | Expor R03/R19 ticket validation via MCP | 1d |

---

## WAVE 3 — MATURIDADE (Dias 10-14)
> **Alvo:** 88% → 92%

| # | Ticket | Título |
|---|--------|--------|
| P4 | NC-DS-318 | SemanticCataloger Qwen 1.5b |
| P4 | NC-DS-319 | Budget tracking por agente |
| P4 | NC-DS-320 | Auto-pause >85% budget |
| P4 | NC-DS-321 | Sandbox execução T3 |
| P4 | NC-DS-324 | Cache preditivo HotCache |
| P4 | NC-DS-325 | Retrieval augmentado (HyDE) |

---

## PROGRESSO MACRO

| Fase | Nome | Agora | Alvo |
|------|------|-------|------|
| **F0** | Fundação & Estabilização | **100%** ✅ | — |
| **SPRINT-GOV** | 22 P1 wire-up | **0%** | **75%** |
| **CICLO-REFORMA** | Perfis + PicoClaw + CI/CD | 0% | **82%** |
| **WAVE 2** | Reforço + P2 MCP | 0% | **88%** |
| **WAVE 3** | Maturidade + P3 | 0% | **92%** |

---

## CHANGELOG

| Data | Versão | Mudança |
|------|--------|---------|
| 2026-04-27 | **v14.1** | **SPRINT-GOVERNANÇA Bloco A concluído.** G1-G5 implementados (4/5 DONE). ToolGuard criado com 5 steps de middleware. Blueprint NC-ARC-FR-002 criado. GAPs 001-004 fechados. 4 novos arquivos: NC-CORE-FR-125-tool-guard.py, NC-ARC-FR-002-architecture-blueprint.yaml, NC-DS-IMPL-001-governance-sprint.yaml, _mcp.bat. Score 62→72%. |
| 2026-04-27 | v14.0 | Reforma por validação: 71 regras classificadas via matriz A/B/C/D. SPRINT-GOVERNANÇA inserido antes do CICLO-REFORMA. |
| 2026-04-26 | v13.0 | Reforma CICLO-REFORMA, Profile Router, 3 Waves |

---

## FASE 5 — NEOcORTEX FACTORY (Auto-Replicação + Templates)
> **Visão:** Fábrica de software autônoma que se auto-replica
> **Status:** %VISÃO | **Pré-requisito:** Waves 1-3 concluídas (score >92%)
> **Especificação:** NC-FACTORY-SPEC-001.md (200 regras + 50 ideias)

### Factory Wave 1 — Fundação de Templates (Dias 15-20)
| # | Ticket | Título | Status |
|---|--------|--------|--------|
| F1 | NC-DS-600 | NC-SUPER-017-factory — MCP tool de geração de projetos | %VISÃO |
| F2 | NC-DS-601 | Template Selector Inteligente (T0 analisa prompt → template) | %VISÃO |
| F3 | NC-DS-602 | Scaffolding Multi-Stack (React, FastAPI, Spring Boot, Go, Rust) | %VISÃO |
| F4 | NC-DS-603 | Template de Agente IA Autônomo (MCP+Ollama+LiteLLM+PicoClaw) | %VISÃO |
| F5 | NC-DS-604 | Pipeline Generate→Validate(STEP0)→Repair→Validate loop | %VISÃO |

### Factory Wave 2 — Auto-Replicação (Dias 21-28)
| # | Ticket | Título | Status |
|---|--------|--------|--------|
| F6 | NC-DS-610 | Auto-Replicação: gerar cópia funcional de si mesmo | %VISÃO |
| F7 | NC-DS-611 | Sincronização bidirecional original↔réplica | %VISÃO |
| F8 | NC-DS-612 | Réplicas com TTL + auto-desativação | %VISÃO |
| F9 | NC-DS-613 | Multi-Agent Factory (PM+DEV+OPS+QA orquestrados) | %VISÃO |
| F10 | NC-DS-614 | Marketplace de Templates | %VISÃO |

### Regras da Factory (R101-R200)
> 100 regras em 5 categorias: Geração (R101-R120), Validação (R121-R140),
> Governança (R141-R160), Auto-Replicação (R161-R180), Customização (R181-R200)
> Documento completo: DIR-DOC-FR-001-docs-main/NC-FACTORY-SPEC-001.md

---

**Hash:** `NC-TODO-FR-001-v14.2-20260427`
**Score atual:** 82% | **Alvo 30 dias:** 92% + Factory Wave 1

**Hash:** `NC-TODO-FR-001-v14.1-20260427`
**Score atual:** 72% | **Alvo 14 dias:** 92%
_"Não se constrói quarto em casa pronta sem seguir a planta."_
