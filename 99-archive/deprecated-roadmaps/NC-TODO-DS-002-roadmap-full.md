# DEPRECATED — Superseded by NC-TODO-FR-001-project-roadmap-consolidated.md (v9.0)
# Movido para archive em 2026-04-15. NÃO USE ESTE ARQUIVO.

# NC-TODO-DS-002  Roadmap TOTAL NeoCortex
<!-- Todas as fases: Pr-MCP  MCP-WQUEUE  Ps-MCP  V2 -->
<!-- Gerado: 2026-04-12 | Atualizado: 2026-04-13 | Base: NC-STR-CC-001 + NC-ANA-INT-001 -->

## Changelog
- [2026-04-13] NC-ANA-INT-001 aprovado: 6 checkpoints, backlog faseado, antecipaes ps-MCP
- [2026-04-13] CP-005 Backlog Faseado: nada descartado, cada lib tem fase certa
- [2026-04-13] CP-006: Savepoint/Rollback real  Fase 1.5; Rate Limit + A2A spec  Fase 2 early
- [2026-04-13] Dependncias Fase 1: cachetools, ruamel.yaml, rich, platformdirs, filelock, notifypy
- [2026-04-12] Roadmap criado com 4 fases de industrializao

---

## Viso Geral

```
FASE 0 (DONE)     Fundao: logging, health, cache, state, utils
FASE 1 (AGORA)    Extensibilidade: hooks, plugins, worker persistente
FASE 2 (MCP)      Infraestrutura: SQLite queue, A2A Gateway
FASE 3 (PS-MCP)  Integrao: KairosService, auto-review, telemetria
FASE 4 (V2)       Escala: multi-tenant, SDK, distribuio
```

---

## FASE 0  Fundao (DONE )

> Sesses 2026-04-08 a 2026-04-12 | 18 tickets DONE | ~3.200L entregues

| Categoria | Entregveis |
|-----------|------------|
| **Servios** | logging, health, savepoint, cache, event-bus, metrics, state-machine, config-validator |
| **Utils** | yaml-safe-parser, hash-utils, path-resolver |
| **Scripts** | populate-lobes, manifest-factory, auto-approve, ticket-validator, queue-monitor, queue-repair, sync-status, sanitize |
| **Anlise CC** | NC-ANA-CC-004 (competitive intel), NC-ANA-CC-005 (11 plugins), kairos-deep, NC-STR-CC-001 (master strategy) |
| **Docs** | nworker-protocol, timestamp-audit, boot-manifest |

---

## FASE 1  Extensibilidade Pr-MCP (NC-DS-029040)

> **Estado:** Em execuo | Lobes de referncia criados  | Pesquisa internet concluda 

### 1.0 Lobes de Referncia Criados (base para implementao)

| Lobe | Path | Cruza com existente |
|------|------|---------------------|
| NC-LBE-CC-002 302L | `lobes/cc-leak/NC-LBE-CC-002-hooks-system.mdc` | NC-SEC-FR-001 @LOCKS |
| NC-LBE-CC-003 290L | `lobes/cc-leak/NC-LBE-CC-003-persistent-worker.mdc` | NC-PROMPT-FR-002 |
| NC-LBE-CC-004 312L | `lobes/cc-leak/NC-LBE-CC-004-confidence-review.mdc` | NC-SCR-FR-005 |
| NC-LBE-CC-005 230L | `lobes/cc-leak/NC-LBE-CC-005-session-mate.mdc` | NC-SVC-FR-006  |
| NC-LBE-CC-006 318L | `lobes/cc-leak/NC-LBE-CC-006-project-config.mdc` | neocortex_config.yaml |
| NC-LBE-CC-007 347L | `lobes/cc-leak/NC-LBE-CC-007-plugin-template.mdc` | DIR-TMP-FR-001 |
| NC-LBE-CC-008 205L | `lobes/cc-leak/NC-LBE-CC-008-pulse-daemon.mdc` | pulse_scheduler.py |
| NC-LBE-CC-009 206L | `lobes/cc-leak/NC-LBE-CC-009-ttl-session-manager.mdc` | NC-SVC-FR-004 |
| NC-LBE-CC-010 204L | `lobes/cc-leak/NC-LBE-CC-010-feature-flags-channels.mdc` | neocortex_config.yaml |

### 1.1 Worker & Scheduling

| Ticket | Entregvel | Status | Agent |
|--------|-----------|--------|-------|
| **NC-DS-029** | `NC-PROMPT-DS-003-persistent-worker.md` |  DISPONVEL | Agent 1 |
| **NC-DS-035** | `NC-SVC-FR-010-kairos-service.py` |  Aps NC-DS-029 |  |
| **NC-DS-036** | `NC-SVC-FR-011-ttl-manager.py` |  Re-entrega (41L stub) |  |

### 1.2 Observabilidade

| Ticket | Entregvel | Status | Agent |
|--------|-----------|--------|-------|
| **NC-DS-030** | `NC-SVC-FR-009-session-buddy.py` |  DISPONVEL | Agent 2 |
| **NC-DS-037** | `NC-CFG-FR-002-feature-flags.py` |  DISPONVEL | Agent 2 |
| **NC-DS-039** | `NC-SVC-FR-012-channel-notifier.py` |  Aps EventBus  |  |
| **NC-DS-040** | `NC-TOOL-FR-030-push-notification.py` |  DISPONVEL | Agent 3 |

### 1.3 Extensibilidade

| Ticket | Entregvel | Status | Agent |
|--------|-----------|--------|-------|
| **NC-DS-031** | `NC-HK-FR-001-hook-registry.py` |  DISPONVEL | Agent 1 |
| **NC-DS-032** | `NC-CFG-FR-004-project-loader.py` |  DISPONVEL | Agent 2 |
| **NC-DS-033** | `NC-TOOL-FR-TEMPLATE/` + scaffolding |  DISPONVEL | Agent 1 |

### 1.4 Qualidade

| Ticket | Entregvel | Status | Agent |
|--------|-----------|--------|-------|
| **NC-DS-034** | `NC-REV-FR-001-confidence-review.py` |  DISPONVEL | Agent 3 |
| **NC-DS-038** | `NC-UTL-FR-004-id-validator.py` |  DISPONVEL | Agent 3 |

### Distribuio Batch Atual (3 tasks  3 agents)

| Agent | Task A | Task B | Task C |
|-------|--------|--------|--------|
| **Agent 1** | NC-DS-029 PersistentWorker | NC-DS-031 HookRegistry | NC-DS-033 PluginTemplate |
| **Agent 2** | NC-DS-030 SessionMate | NC-DS-032 ProjectConfig | NC-DS-037 FeatureFlags |
| **Agent 3** | NC-DS-034 ConfidenceReview | NC-DS-038 IDValidator | NC-DS-040 PushNotification |

### 1.1 Worker & Scheduling
| Ticket | Entregvel | Prioridade |
|--------|-----------|-----------|
| **NC-DS-029** | `NC-PROMPT-DS-003-persistent-worker.md`  Worker loop contnuo |  Imediato |
| **NC-DS-035** | `NC-SVC-FR-010-kairos-service.py`  Event-driven pulse |  Next |
| **NC-DS-036** | `NC-SVC-FR-011-ttl-manager.py`  TTL granular por entidade |  Next |

### 1.2 Observabilidade
| Ticket | Entregvel | Prioridade |
|--------|-----------|-----------|
| **NC-DS-030** | `NC-SVC-FR-009-session-buddy.py`  Stats de sesso |  Imediato |
| **NC-DS-037** | `NC-CFG-FR-002-feature-flags.py`  Feature flags com cache |  Complementar |
| **NC-DS-039** | `NC-SVC-FR-012-channel-notifier.py`  Push MCP |  Complementar |
| **NC-DS-040** | `NC-TOOL-FR-030-push-notification.py`  Push tool |  Complementar |

### 1.3 Extensibilidade
| Ticket | Entregvel | Prioridade |
|--------|-----------|-----------|
| **NC-DS-031** | `NC-HK-FR-001-hook-registry.py`  Hookify-like |  Imediato |
| **NC-DS-032** | `NC-CFG-FR-004-project-loader.py`  Config `.nc/` |  Imediato |
| **NC-DS-033** | `NC-TOOL-FR-TEMPLATE/` + `NC-SCR-FR-012-new-tool.py` |  Imediato |

### 1.4 Qualidade

| Ticket | Entregvel | Status | Agent |
|--------|-----------|----|-------|
| **NC-DS-034** | `NC-REV-FR-001-confidence-review.py` |  DISPONVEL | Agent 3 |
| **NC-DS-038** | `NC-UTL-FR-004-id-validator.py` |  DISPONVEL | Agent 3 |

### 1.5 Dependncias Python Aprovadas (Fase 1)  @SYNTHESIS CP-002

| Lib | Fase | Para |
|---|---|---|
| `cachetools >=5.0` | Fase 1 | FeatureFlagService, TTLManager |
| `ruamel.yaml >=0.18` | Fase 1 | ProjectConfigLoader |
| `rich >=13.0` | Fase 1 | SessionMate display |
| `platformdirs >=4.0` | Fase 1 | XDG cross-platform Windows |
| `filelock >=3.0` | Fase 1 | Locks atmicos de arquivo |
| `notifypy >=0.5` | Fase 1 | PushNotification (opcional) |
| `APScheduler >=3.0` | Fase 2 | PulseDaemon com triggers cron |
| `asciimatics >=1.15` | Fase 3 | SessionMate display avanado |
| `pluggy >=1.0` | Fase 3 | Framework de plugins maduro |
| `cookiecutter >=2.0` | Fase 3 | Scaffolding avanado Jinja2 |
| `reviewdog >=0.17` | Fase 3 | CI/CD para ConfidenceReview |
| `celery >=5.0` | Fase 4 | Task queue distribuda |
| `redis >=5.0` | Fase 4 | Cache distribudo + lock |
| `Unleash/Flagsmith SDK` | Fase 4 | Feature flags servidor dedicado |
| `ZooKeeper` | Fase 5 | Coordenao cluster |

---

## FASE 1.5  Savepoint/Rollback Real (antes de MCP-WQUEUE)

> Antecipado de Fase 3 por risco: falha sem rollback = estado corrompido.

| Componente | Ticket | Estado atual | Entregvel |
|---|---|---|---|
| **Savepoint completo** | SAVE-002 | NC-SVC-FR-003  stub | NC-SVC-FR-003 completo com SHA-256 + rollback |

> Fase 1.5 ocorre aps Fase 1 estar estvel e antes de implementar MCP-WQUEUE.

---

## FASE 2  MCP-WQUEUE (Barreira Principal)

> **Desbloqueador:** elimina race conditions YAML, habilita N-workers real

| Componente | Ticket | Descrio |
|-----------|--------|-----------|
| **SQLite Queue** | MCP-WQUEUE | `task_queue.db` com claim atmico ACID |
| **MCP Tool** | NC-TOOL-FR-030 | `claim_task`, `release_task`, `list_queue`, `get_task` |
| **Migrao YAMLSQL** | NC-SCR-FR-013 | Script de migrao fila YAML  SQLite |

**Pr-requisitos:** NC-DS-027 (TicketValidator) , NC-DS-028 (QueueMonitor) 

**Impacto esperado:** throughput de ~2 tasks/h  10-15 tasks/h com N workers

---

## FASE 3  Ps-MCP (Integrao)

> Depende de MCP-WQUEUE + @LOCKS liberados
> Antecipaes confirmadas por @SYNTHESIS CP-006:

| Ticket | Entregvel | Antecipado? | Depende |
|--------|-----------|----|----|
| **GATEWAY-001** | A2A Gateway (spec Fase 1, impl Fase 2 early) |  Spec Fase 1 | LOCKS |
| **SCHED-002** | KairosService integrado ao MCP dispatch |  Fase 3 ok | NC-DS-035 |
| **REVIEW-002** | ConfidenceReview no server.py |  NC-DS-034 j na Fase 1 | LOCKS |
| **RATE-001** | Rate Limit por Tool (budget guard) |  Fase 2 early | MCP-WQUEUE |
| **TELEM-001** | Prometheus/Grafana (metrics export HTTP) |  Export Fase 2 early | MCP estvel |
| **FLAG-002** | Growthbook SDK (rollout percentual) |  Fase 3 ok | MCP estvel |
| **SEC-403** | Rate Limit por Tool |  Fase 2 early | MCP-WQUEUE |

### Arquitetura A2A Gateway (Ps-MCP)
```
[T0 Antigravity]
       dispatch via MCP-WQUEUE (SQLite ACID)
      
[A2A Gateway :8766]
     POST /register   worker registra capabilities
     GET  /claim      worker solicita task
     POST /heartbeat  worker sinaliza alive (TTL: 5min)
     POST /complete   worker entrega handoff
     Worker A :25993
     Worker B :53109
     Worker C :58184
          
    SQLite (task_queue.db)
```

**TTL do Claude Code adaptados:**
- Session lease: 5h (`SESSION_LEASE_TTL = 18000s`)
- Token refresh: 5min antes do vencimento
- Heartbeat interval: 1min
- `EXIT_CODE_PERMANENT = 42` para erros no-retentveis

---

## FASE 4  V2 / Escala (Longo Prazo)

> Referncia: NC-TODO-FR-001 v9.0

| Milestone | Descrio | Status |
|-----------|-----------|--------|
| **SDK Pblico** | FastAPI wrapper + .exe distribuvel | Planejado |
| **Multi-tenant** | Workspaces isolados por projeto | Planejado |
| **Docker compose** | Stack completo 1-comando | Planejado |
| **Buddy V2** | Sprint rewards + achievements textuais | Planejado |
| **Prompt Versioning** | NC-SCR-FR-011-prompt-migrate.py | Planejado |
| **Dashboard Web** | Interface HTML para fila + agentes | Planejado |

---

## Mapa de Dependncias Global

```
FASE 0   DONE
    
    
FASE 1 (Pr-MCP)  Todos paralelos
    029 Worker   031 HookRegistry  033 PluginTemplate
    030 Session  032 ProjectConfig  037 FeatureFlags
    034 Review   038 IDValidator    040 PushNotif
    035 Pulse    036 TTLManager     039 Channel
    
    
FASE 1.5  Savepoint/Rollback real (SAVE-002)
    
    
FASE 2 (MCP-WQUEUE)  BARREIRA PRINCIPAL
    + RATE-001 Rate Limit por Tool
    + TELEM-001 Metrics HTTP export
    + A2A Gateway spec/impl
    
    
FASE 3 (Ps-MCP)
    GATEWAY-001 impl  SCHED-002  REVIEW-002 (sequencial)
    FLAG-002, TELEM-001 full, APScheduler (paralelos)
    
    
FASE 4 (V2 / Escala)
    SDK pblico  celery  redis  Unleash/Flagsmith
    asciimatics, pluggy, cookiecutter, reviewdog
    
    
FASE 5 (Cluster)
    ZooKeeper  multi-host  distribuio global
```

---

## KPIs por Fase

| Fase | Mtrica-chave | Meta |
|------|---------------|------|
| Fase 1 | DONE count | 30 tickets |
| Fase 2 | Throughput workers | 10+ tasks/h sem superviso |
| Fase 3 | N workers estveis | 5+ workers sem race condition |
| Fase 4 | Deploy time | < 5 min end-to-end |

---

## Custo Estimado

| Fase | Tokens | Custo estimado |
|------|--------|---------------|
| Fase 0 (realizado) | ~400M | ~$18 |
| Fase 1 | ~100M | ~$4-6 |
| Fase 2 | ~50M | ~$2-3 |
| Fase 3 | ~80M | ~$3-4 |
| **Total** | **~630M** | **~$27-31** |

> Fase 0 custou ~$18 em 5 dias (08/04-12/04). Com Ralph-Wiggum worker (loop persistente), estimativa Fase 1 em 1-2 dias.
