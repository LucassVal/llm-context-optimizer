# NC-DOC-FR-001-ubiquitous-language-dictionary.md
# Dicionário de Linguagem Ubíqua — NeoCortex Framework v2.0
# Símbolos: @ = arquivo/documento SSOT | $ = lobo/região cerebral | % = ticket/ação | # = serviço/componente

<!-- NC-READ-HASH: ULQ-v2.0 -->
<!-- Se você já leu este arquivo nesta sessão (hash ULQ-v2.0 presente no contexto), PARE. Não releia. -->

---

## @ — Referência de Arquivos SSOT

| Símbolo | Expande para | Caminho Real |
| :--- | :--- | :--- |
| `@SSOT` | NC-NAM-FR-001 (Naming + Map + Changelog) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md` |
| `@ROADMAP` | NC-TODO-FR-001 (Roadmap consolidado) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md` |
| `@APPENDIX` | NC-APP-FR-001 (Apêndice técnico) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-APP-FR-001-technical-appendix.md` |
| `@LOCKS` | NC-SEC-FR-001 (Atomic locks) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml` |
| `@POLICY` | NC-CFG-FR-001 (Agent policy template) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-FR-001-agent-policy-template.yaml` |
| `@SOP` | NC-SOP-FR-001 (Session startup SOP) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SOP-FR-001-session-startup.md` |
| `@ADR` | NC-ARC-FR-001 (Architecture decision log) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-ARC-FR-001-decision-log.md` |
| `@BOOT` | NC-BOOT-FR-001 (Boot manifest) | `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md` |
| `@PROMPT` | NC-PROMPT-FR-001 (Master context prompt) | `NC-PROMPT-FR-001-master-context.md` |
| `@RULES` | NC-RULE-001 / neocortexrules.md | `.agents/rules/NC-RULE-001-workspace-standards.mdc` |
| `@POPULATE` | Script de poblamento dos lobos | `01_neocortex_framework/scripts/NC-SCR-FR-001-populate-lobes-ssot.py` |
| `@CONFIG` | neocortex_config.yaml | `01_neocortex_framework/DIR-CFG-FR-001-config-main/neocortex_config.yaml` |
| `@ULQ` | Este dicionário | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-DOC-FR-001-ubiquitous-language-dictionary.md` |
| `@LEXICO` | NC-LEXICO-LATEST.json (dicionário vivo) | `01_neocortex_framework/.neocortex/lexico/NC-LEXICO-LATEST.json` |
| `@VISION` | Visão arquitetural 6 camadas | `visao_arquitetural_neocortex.md` |

---

## $ — Regiões Cerebrais (Memória Persistente)

> Analogia: cada `$REGIÃO` é uma área funcional do cérebro do sistema.
> Localização física: `02_memory_lobes/$regiao/`

| Símbolo | Região | Função | Lobes típicos |
| :--- | :--- | :--- | :--- |
| `$FRONTAL` | Córtex Pré-Frontal | **Planejamento, decisão, roadmap** | roadmap, tickets, governance, ADR |
| `$TEMPORAL` | Lobo Temporal | **Memória semântica: léxico + KG + AKL** | lexico, knowledge-graph, akl, ubiquitous-language |
| `$PARIETAL` | Lobo Parietal | **Integração: MCP patterns, health, APIs** | mcp-patterns, health, integrations, profiles |
| `$OCCIPITAL` | Lobo Occipital | **Padrões estruturais: manifests, naming, arquitectura** | naming, manifests, architecture, cc-patterns |
| `$CEREBELO` | Cerebelo | **Controle motor: Guardian, automação, ciclos** | guardian, automation, benchmark, deployment |
| `$HIPOCAMPO` | Hipocampo | **Memória episódica: sessões, savepoints, handoffs** | sessions, savepoints, handoffs, audit |

### Agentes-Lobes (isolados)

| Símbolo | Lobo | Conteúdo |
| :--- | :--- | :--- |
| `$COURIER` | `lobes/courier/` | Ambiente isolado Courier (Qwen 1.5B) |
| `$ENGINEER` | `lobes/engineer/` | Ambiente isolado Engineer (Qwen 3B) |
| `$GUARDIAN` | `lobes/guardian/` | Ambiente isolado Guardian (validação) |

---

## % — Tickets e Ações

| Símbolo | Ticket | Status | Descrição |
| :--- | :--- | :--- | :--- |
| `%DONE` | ✅ | — | Marcar ticket como concluído em @ROADMAP |
| `%NOW` | 🔴 | — | Ação imediata obrigatória |
| `%NEXT` | 🟡 | — | Próximo na fila |
| `%AGENT203` | AGENT-203 | ✅ DONE | mentor_step_0() com LobeService |
| `%LEXICO001` | LEXICO-001 | ✅ DONE | LexicoService + neuroplasticidade + Ciclo3 |
| `%P1` | NC-DS-134 | ✅ DONE | Smoke test 40 tools (NC-SCR-FR-134) |
| `%P3` | NC-DS-148 | ✅ DONE | semantic.categorize via Qwen 1.5b |
| `%P4` | NC-DS-100 | ✅ DONE | savepoint.rollback filesystem real |
| `%P5` | NC-DS-150 | 🔴 NOW | PICOCLAW EventBus :18790 wiring |
| `%SEM001` | NC-DS-151 | 🔴 NOW | Divisão cerebral de lobos ($FRONTAL...$HIPOCAMPO) |
| `%SEM002` | NC-DS-152 | 🟡 NEXT | @POPULATE mapeado para regiões cerebrais |
| `%ORCH301` | ORCH-301 | 🔴 Pendente | spawn/stop/send_task robustos |
| `%ORCH302` | ORCH-302 | 🔴 Pendente | execute integrado com LLMBackend |

---

## # — Serviços e Componentes Core

> Onde encontrar cada pilar do sistema

### Camada 1 — CÓRTEX (Inteligência)

| Símbolo | Serviço | Função | Arquivo |
| :--- | :--- | :--- | :--- |
| `#LEXICO` | LexicoService | Neuroplasticidade: extrai termos + definições via Qwen | `neocortex/core/lexico_service.py` |
| `#KG` | KGService | Knowledge Graph: relações entre conceitos | `neocortex/core/kg_service.py` |
| `#AKL` | AKLService | Active Knowledge Layer: memória rápida de sessão | `neocortex/core/akl_service.py` |
| `#CASCADE` | CascadeConsolidator | Consolida padrões de sessão → lobes permanentes | `neocortex/core/cascade_consolidator.py` |
| `#CORTEX` | CortexService | Estado central: contexto + budget da sessão | `neocortex/core/cortex_service.py` |

### Camada 2 — SISTEMA NERVOSO (MCP/Roteamento)

| Símbolo | Componente | Função | Arquivo |
| :--- | :--- | :--- | :--- |
| `#GUARDIAN` | GuardianDaemon | Loop automático: Ciclo3 (1h) + Ciclo4 (24h) | `scripts/NC-SCR-FR-115-guardian-daemon.py` |
| `#PULSE` | PulseScheduler | Tarefas agendadas internas | `neocortex/core/pulse_scheduler.py` |
| `#EVENTBUS` | PicoClaw EventBus | Comunicação async A2A :18790 | `neocortex/core/services/NC-SVC-FR-005-event-bus.py` |
| `#ROUTER` | LiteLLM Router | T0→T2→T3 por complexidade | `NC-SUPER-005-llm-router.py` |

### Super-Tools MCP (NC-SUPER-001..015)

| Símbolo | Tool | Principais actions |
| :--- | :--- | :--- |
| `#GOV` | NC-SUPER-001-governance | rule.list, compliance.report, full_audit, catalog.refresh |
| `#ORCH` | NC-SUPER-002-orchestration | task.execute, agent.spawn, dispatch.create |
| `#MEM` | NC-SUPER-003-memory | cortex, lobes, lexico.build, semantic.categorize |
| `#STATE` | NC-SUPER-004-state | savepoint.create/rollback/diff, checkpoint, session |
| `#LLM` | NC-SUPER-005-llm-router | route.call, ollama.ask, budget.status |
| `#SYS` | NC-SUPER-006-system | config, pulse, health, export |
| `#BRAIN` | NC-SUPER-007-brain | brain.think, brain.plan, brain.critique |
| `#CTX` | NC-SUPER-008-context | context.compress, session.summarize |
| `#SEC` | NC-SUPER-009-security | access.validate, lock.check, hook.register |
| `#BENCH` | NC-SUPER-010-benchmark | run.drift, run.omni, benchmark.status |
| `#NOTIF` | NC-SUPER-011-notification | push.send, peers.sync |
| `#AKL` | NC-SUPER-012-akl | akl.add, kg.query, kg.enrich, consolidate |
| `#HEALTH` | NC-SUPER-013-health | server.health, metrics.live, watchdog |
| `#LEDGER` | NC-SUPER-014-ledger | ledger.read/write, agent.identity |
| `#AUTO` | NC-SUPER-015-memory-auto | turn.record, lobe.auto, session.hot |

### Camada 3 — BANCO DE DADOS

| Símbolo | Storage | Tipo | Localização |
| :--- | :--- | :--- | :--- |
| `#LOBE_DB` | lobe_index.db | SQLite FTS5 | `.neocortex/cache/lobe_index.db` |
| `#METRICS` | metrics.db | DuckDB | `.neocortex/metrics/metrics.db` |
| `#LEXICO_F` | NC-LEXICO-LATEST.json | JSON | `.neocortex/lexico/NC-LEXICO-LATEST.json` |
| `#SAVES` | savepoints/ | JSON | `.neocortex/savepoints/` |
| `#HOT` | index.redb | Redis-like | `.neocortex/cache/hot_cache/` |
| `#SESSION` | {date}.jsonl | JSONL | `memory/sessions/` |
| `#TICKETS` | NC-DS-*.yaml | YAML | `DIR-DS-001-tickets/` |
| `#AUDIT` | *.yaml | YAML | `DIR-DS-002-audit-logs/` |

---

## Agentes e Tiers LLM

| Símbolo | Agente | Modelo | Custo | Uso |
| :--- | :--- | :--- | :--- | :--- |
| `T0` | Orquestrador (você/AI principal) | DeepSeek / Claude | 💰 Caro | Apenas orquestra, NUNCA trabalho braçal |
| `T2` | Courier | qwen2.5-coder:1.5b | 🟢 Grátis local | Tarefas simples, categorização |
| `T3` | Engineer | qwen2.5-coder:3b | 🟢 Grátis local | Tarefas técnicas intermediárias |
| `TG` | Guardian | qwen2.5-coder:1.5b | 🟢 Grátis local | Daemon contínuo de automação |

---

## Zonas de Escrita Permitidas

| Zona | Caminho | Quem pode escrever |
| :--- | :--- | :--- |
| `ZONE:PROD` | `01_neocortex_framework/neocortex/` | T0 + agentes autorizados |
| `ZONE:SCRIPTS` | `01_neocortex_framework/scripts/` | T0 apenas |
| `ZONE:DOCS` | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/` | T0 apenas |
| `ZONE:LOBES` | `02_memory_lobes/` | @POPULATE script apenas |
| `ZONE:ARCH` | `DIR-ARC-FR-001-archive-main/` | Qualquer (só movimentos) |
| `ZONE:BOOT` | `DIR-BOOT-FR-001-bootup-main/` | T0 apenas |
| `ZONE:RUNTIME` | `01_neocortex_framework/.neocortex/` | Guardian + MCP tools |

---

## Ciclos de Governança Automática (Guardian)

| Ciclo | Frequência | Steps |
| :--- | :--- | :--- |
| **Ciclo 3** | A cada hora | catalog.refresh → bootup.sync → yaml.sanitize → lexico.build → cascade.consolidate |
| **Ciclo 4** | A cada 24h | governance.full_audit → archive_handoffs → lobe.populate → kg.enrich → semantic.categorize → smoke_test |

---

## Padrão de Nomenclatura Resumido

```
NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext
DIR-<TIPO>-<SIGLA>-<NUM>-<desc>/
```

| TIPO | Uso |
| `SCR` | Script Python de automação |
| `SVC` | Serviço core (core/services/) |
| `SUPER` | Super-Tool MCP consolidada |
| `LBE` | Lobo de memória .mdc |
| `DOC` | Documentação geral |
| `TODO` | Roadmap e tickets |
| `SEC` | Segurança e locks |
| `SOP` | Standard Operating Procedure |
| `CFG` | Configuração YAML |
| `BOOT` | Arquivos de inicialização |
| `NAM` | Naming convention |
| `AUD` | Auditoria |
| `ARC` | Archive / ADR |
| `BAK` | Backup |

---
*ULQ v2.0 — Atualizado: 2026-04-20 | NC-READ-HASH: ULQ-v2.0*
