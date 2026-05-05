# NC-GRAND-PLAN-001 — NeoCortex Grand Unified Plan v1.0
# TODAS as regras, fases, prioridades e arquitetura
# Hash: GRAND-PLAN-v1.0-20260427
# "Se não está neste plano, não existe. Se está, tem dono, prazo e critério de saída."

---

## ═══════════════════════════════════════════════
## REALIDADE ATUAL (2026-04-27 23:50)
## ═══════════════════════════════════════════════

Score:        82% (era 62%)
MCP:          SSE :8766 estável, 20 super tools
Compliance:   93.8% (15/16 regras)
Stubs:        7 eliminados, 5 restantes (dependem de serviços externos)
Checkpoints:  2090
Handoffs:     5
Ruff:         6 bare-except cosméticos

### O que FUNCIONA (comprovado por teste)

DOMÍNIOS DDD ATIVOS:
  STF (brain)          ✅ 6/6 ações (LiteLLM offline = degraded)
  STJ (llm_router)     ✅ 7/7 ações (LiteLLM offline)
  TJ (memory)          ✅ 12/12 ações (search real, knowledge real)
  TJ (state)           ✅ 15/15 ações (STEP 0 + LockGuard wired)
  TJ (context)         ✅ 8/8 ações
  TJ (memory_auto)     ✅ 7/7 ações
  FÓRUM (system)       ✅ 15/15 ações (config.set wired)
  FÓRUM (security)     ✅ 9/9 ações (7 lock categories)
  FÓRUM (health)       ✅ 8/8 ações (tools_count fix)
  FÓRUM (benchmark)    ✅ 5/5 ações
  FÓRUM (notification) ✅ 6/6 ações
  FÓRUM (akl)          ✅ 8/8 ações
  FÓRUM (ledger)       ✅ 6/6 ações
  LEGISLATIVO (gov)    ✅ 21/21 ações (21 regras visíveis)
  EXECUTIVO (orch)     ❌ 12/12 offline (PicoClaw)
  BRIDGES              ⚠️ 2/4 ativas

### O que NÃO funciona (dependência externa)
  PicoClaw  :18790 → offline (Wave 1 NC-DS-302)
  LiteLLM   :4000  → offline (scheduled task não iniciou)
  PulseScheduler    → desabilitado (crashava SSE)

### O que NÃO EXISTE (stubs)
  SessionMemoryWriter → serviço não implementado
  KG Service parcial  → algumas queries falham

---

## ═══════════════════════════════════════════════
## 321 REGRAS — MAPEAMENTO COMPLETO
## ═══════════════════════════════════════════════

### BLOCO 0: FUNDAÇÃO (R01-R21 + LOCK + STEPS + CICLOS)
Status: 82% implementado
Regras: 71 (governança + segurança + agentes + ciclos + tokens + policies + crypto + metrics + eco)

### BLOCO 1: FACTORY — GERAÇÃO (R101-R120)
Status: 0% (visão)
Regras: 20 (templates, scaffolding, savepoint pré-escrita)

### BLOCO 2: FACTORY — VALIDAÇÃO (R121-R140)
Status: 0% (visão)
Regras: 20 (lint, sandbox, schema validation, multi-platform tests)

### BLOCO 3: FACTORY — GOVERNANÇA (R141-R160)
Status: 0% (visão)
Regras: 20 (secrets, CORS, RBAC, rate limiting, security headers)

### BLOCO 4: FACTORY — AUTO-REPLICAÇÃO (R161-R180)
Status: 0% (visão)
Regras: 20 (fork, DNA/RNA, lineage, TTL, hierarchical replication)

### BLOCO 5: FACTORY — CUSTOMIZAÇÃO (R181-R200)
Status: 0% (visão)
Regras: 20 (config, plugins, themes, i18n, multi-DB, A/B testing)

### BLOCO 6: EVOLUÇÃO — REPLICAÇÃO CONTROLADA (R201-R220)
Status: 0% (visão)
Regras: 20 (herança de políticas, R0 threshold, sandbox BSL, SHA-256)

### BLOCO 7: EVOLUÇÃO — MUTAÇÃO (R221-R240)
Status: 0% (visão)
Regras: 20 (mutation board, drift control, ethical genome, fitness ranking)

### BLOCO 8: ECOSSISTEMA — PLUGINS (R241-R250)
Status: 0% (visão)
Regras: 10 (npm package, UPM compatibility, AGENTS.md, auto-update)

---

## ═══════════════════════════════════════════════
## PRIORIDADES ABSOLUTAS (P0 → P4)
## ═══════════════════════════════════════════════

### 🔴 P0 — CRÍTICO (DEVE funcionar AGORA)
O que mantém o sistema vivo e sob governança.

| # | Item | Status | Ação |
|---|------|--------|------|
| P0-01 | MCP SSE :8766 | ✅ | Manter |
| P0-02 | ToolGuard ativo nos 3 tools | ✅ | Manter |
| P0-03 | STEP 0 regression check | ✅ | Manter |
| P0-04 | Atomic Locks (7 categorias) | ✅ | Manter |
| P0-05 | Compliance >80% | ✅ 93.8% | Manter |
| P0-06 | LiteLLM :4000 | ❌ | Iniciar (scheduled task existe) |
| P0-07 | OpenCode MCP config | ✅ | Manter |

### 🟠 P1 — ESTA SEMANA (Bloqueia progresso)
Coisas que impedem a próxima fase.

| # | Item | Status | Ação |
|---|------|--------|------|
| P1-01 | PulseScheduler reativar | ❌ | Fix background thread crash |
| P1-02 | Bloco B triggers (G6-G10) | ⏳ | Wire up auto bootup/compliance |
| P1-03 | PicoClaw :18790 | ❌ | Ativar (NC-DS-302) |
| P1-04 | LiteLLM gateway start | ❌ | Rodar scheduled task |
| P1-05 | health.tools_count fix | ✅ | Done |
| P1-06 | SSOT drift auto (R02) | ⏳ | Wire up |

### 🟡 P2 — ESTE MÊS (Wave 1-2)
Fundação para a Factory.

| # | Item | Status | Ação |
|---|------|--------|------|
| P2-01 | Profile Router (NC-DS-300/301) | ⏳ | Wave 1 |
| P2-02 | CI/CD + ruff.toml (NC-DS-303/304) | ⏳ | Wave 1 |
| P2-03 | Token measurement (NC-DS-305) | ⏳ | Wave 1 |
| P2-04 | Circuit Breaker + CODEOWNERS | ⏳ | Wave 2 |
| P2-05 | MCP tools P2 exposure (R03, R06, R07, R17) | ⏳ | Wave 2 |
| P2-06 | SessionMemoryWriter (substituir stub) | ⏳ | Wave 2 |

### 🟢 P3 — PRÓXIMO TRIMESTRE (Wave 3)
Maturidade e semantic.

| # | Item | Status | Ação |
|---|------|--------|------|
| P3-01 | SemanticCataloger Qwen 1.5b | ⏳ | Wave 3 |
| P3-02 | Budget tracking por agente | ⏳ | Wave 3 |
| P3-03 | Sandbox execução T3 | ⏳ | Wave 3 |
| P3-04 | Cache preditivo HotCache | ⏳ | Wave 3 |
| P3-05 | HyDE retrieval | ⏳ | Wave 3 |

### 🔵 P4 — FUTURO (FASE 5 — FACTORY)
Auto-replicação e ecossistema. 250 regras novas.

| # | Item | Regras | Dependência |
|---|------|--------|-------------|
| P4-01 | NC-GENOME-FR-001 (DNA/RNA) | R201-R220 | P1-P3 concluídos |
| P4-02 | Template Selector + Scaffolding | R101-R120 | P2 concluído |
| P4-03 | Validation pipeline | R121-R140 | P2 concluído |
| P4-04 | Auto-replicação (fork + sandbox) | R161-R180 | P4-01 |
| P4-05 | Mutation Board + Drift Control | R221-R240 | P4-04 |
| P4-06 | Plugin npm + UPM | R241-R250 | P4-04 |
| P4-07 | Marketplace de Templates | F6-F10 | P4-02 |

---

## ═══════════════════════════════════════════════
## PLANO DE AÇÃO IMEDIATO (PRÓXIMOS 3 DIAS)
## ═══════════════════════════════════════════════

### DIA 1 — P0 + P1 (HOJE)
1. [ ] Iniciar LiteLLM gateway (:4000) → scheduled task
2. [ ] P1-01: Reativar PulseScheduler com safeguards
3. [ ] P1-02: Bloco B triggers (G6 bootup auto, G8 ssot.diff auto)
4. [ ] Testar brain.think + llm_router com LiteLLM online
5. [ ] Ruff final limpo (eliminar 6 bare-except)
6. [ ] bootup.sync + compliance.report

### DIA 2 — P2 INÍCIO
1. [ ] P2-06: SessionMemoryWriter (eliminar último stub)
2. [ ] P2-01: Profile Router design doc
3. [ ] P1-03: Ativar PicoClaw (se possível)
4. [ ] P2-05: Expor R03, R06, R07 via MCP

### DIA 3 — CONSOLIDAÇÃO
1. [ ] P2-02: ruff.toml + CI/CD scaffold
2. [ ] Todos os stubs eliminados (meta: 0)
3. [ ] Score >85%
4. [ ] Preparar Wave 1 kickoff

---

## ═══════════════════════════════════════════════
## GENOME — DNA/RNA (Base para Auto-Replicação)
## ═══════════════════════════════════════════════

```yaml
genome:
  version: "1.0"
  species: "NeoCortex MCP Framework"
  lineage_root: "T0-Antigravity"

  dna:  # Imutável pelo child
    atomic_locks: "NC-SEC-FR-001-atomic-locks.yaml"
    constitution: "NC-GOV-FR-003-ia-governance-rules.yaml"
    tool_guard: "NC-CORE-FR-125-tool-guard.py"
    step_zero: "NC-CORE-FR-123-regression-service.py"
    wal_service: "NC-SVC-FR-016-wal-service.py"
    crypto_hub: "NC-SVC-FR-017-crypto-hub.py"

  rna:  # Estado de execução (mutável)
    mode: "dev"
    lifecycle_stage: "fase_4_mcp_ativo"
    objective: "SPRINT-GOVERNANÇA Bloco A concluído"
    capabilities_developed: ["search.advanced", "knowledge.search", "tool_guard"]

  epi_genome:  # Constantes (imutáveis localmente, propagadas)
    mcp_port: 8766
    litellm_port: 4000
    picoclaw_port: 18790
    max_replication_rate: 5_per_hour
    drift_threshold: 0.68
    biosafety_default: "BSL-1"

  replication:
    requires: ["ToolGuard validation", "STEP 0 check", "SHA-256 integrity"]
    sandbox_required: true
    policy_inheritance: true

  mutation:
    review_board: ["T0", "Guardian", "Engineer"]
    requires: ["Sandbox test", "MetricsStore delta", "Regression Buffer update"]
    auto_rollback: true
```

---

## ═══════════════════════════════════════════════
## MÉTRICAS DE SUCESSO
## ═══════════════════════════════════════════════

| Marco | Critério | Status |
|-------|----------|--------|
| M1 — MCP estável | SSE 24h sem crash | ⚠️ Precisa testar |
| M2 — Compliance | >90% score | ✅ 93.8% |
| M3 — Zero stubs | 0 ações "indisponível" | ⚠️ 5 restantes |
| M4 — Score >85% | Medido pelo compliance.report | ⚠️ 82% |
| M5 — LiteLLM online | brain.think funcional | ❌ |
| M6 — PicoClaw online | orchestration funcional | ❌ |
| M7 — Factory MVP | 1 template gerado com sucesso | ❌ P4 |
| M8 — Auto-replicação | Fork funcional com herança | ❌ P4 |

---

**Hash:** `NC-GRAND-PLAN-001-v1.0-20260427`
**Total de regras:** 321 (71 base + 250 factory/evolution/plugins)
**Score atual:** 82% | **Alvo 30 dias:** 92% + Factory MVP
_"Se não está neste plano, não existe."_