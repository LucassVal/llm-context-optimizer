# NC-NAM-FR-001d  Registry Prompts & Tickets

> Sub-registro extrado de NC-NAM-FR-001-naming-convention.md (categoria: NC-PROMPT-*, NC-BOOT-*, NC-DS-*).  
> Mantido automaticamente via script NC-SCR-FR-004-governance-validator.py.

| Nome | Descrio | Local | Palavras Chaves |
|---|---|---|---|
| NC-PROMPT-DS-001-deepseek-subordinate.md | Prompt mestre T1: ciclo 6 fases, 9 regras, protocolo handoff YAML PENDING_REVIEW [2026-04-12] | \NC-PROMPT-DS-001-deepseek-subordinate.md | deepseek, t1, subordinate, prompt, handoff |
| NC-DS-HANDOFF-TEMPLATE.yaml | Template correspondencia T1T0: status PENDING_REVIEW/APPROVED/REJECTED/ESCALATED [2026-04-12] | \DIR-DS-001-tickets\NC-DS-HANDOFF-TEMPLATE.yaml | handoff, template, correspondence, t1-t0 |
| NC-DS-FR-001-fr025-system.yaml | Ticket NC-DS-001: FR-025 neocortex_system 8 acoes [2026-04-12] | \DIR-DS-001-tickets\NC-DS-FR-001-fr025-system.yaml | ticket, fr-025, system, t1 |
| NC-PROMPT-DS-000-launcher.md | Launcher T1: 4 linhas  cole no OpenCode e DeepSeek le tudo sozinho [2026-04-12] | \NC-PROMPT-DS-000-launcher.md | launcher, deepseek, opencode, t1 |
| NC-DOC-DS-001-prompt-template-sample.md | **TEMPLATE CANONICO** de prompt para agentes T1: Brockman v1 (GOAL/RETURN FORMAT/WARNINGS/CONTEXT DUMP) + STEP-0 v2 + protocolo entrega YAML + checklist revisao T0. Base para qualquer NC-PROMPT-DS-* [2026-04-13] | \DIR-DS-000-agent-config\NC-DOC-DS-001-prompt-template-sample.md | template, brockman, step0, canonical, t1, prompt |
| NC-PROMPT-DS-004-kairos-channel.md | Prompt Agente DS-A: NC-DS-035 (KairosService) + NC-DS-039 (ChannelNotifier). Template Brockman v1 + STEP-0 v2 [2026-04-13] | \DIR-DS-000-agent-config\NC-PROMPT-DS-004-kairos-channel.md | ds-a, kairos, channel, brockman |
| NC-PROMPT-DS-005-pathresolver-eventbus.md | Prompt Agente DS-B: NC-DS-026 (PathResolver) + NC-DS-021 (EventBus upgrade). Template Brockman v1 + STEP-0 v2 [2026-04-13] | \DIR-DS-000-agent-config\NC-PROMPT-DS-005-pathresolver-eventbus.md | ds-b, pathresolver, eventbus, brockman |
| NC-PROMPT-DS-006-metrics-statemachine.md | Prompt Agente DS-C v2: NC-DS-022 (MetricsCollector) + NC-DS-023 (FSM). Template Brockman v1 + STEP-0 v2. Interfaces completas [2026-04-13] | \DIR-DS-000-agent-config\NC-PROMPT-DS-006-metrics-statemachine.md | ds-c, metrics, fsm, brockman |
| NC-PROMPT-FR-001-master-context.md | Prompt T0 universal v4: R21 no topo, 9 SSOTs mapeados, Brockman integrado, Sprint-002 frentes, toolchain, flag MCP offline [2026-04-13] | \NC-PROMPT-FR-001-master-context.md | t0, master, context, brockman, r21 |
| NC-PROMPT-DS-015-picoclaw-research.md | Prompt pesquisa profunda PicoClaw: Agente A (59520), ticket LOBE-INT-001. 10 fontes obrigatrias, 10 sees, config NeoCortex, handoff YAML [2026-04-13] | \DIR-DS-000-agent-config\NC-PROMPT-DS-015-picoclaw-research.md | prompt, agente-a, picoclaw, research, lobe-int-001 |
| NC-PROMPT-DS-016-opencode-research.md | Prompt pesquisa profunda OpenCode: Agente B (44624), ticket LOBE-INT-002. REST API, TUI, headless, MCP OAuth, config completo [2026-04-13] | \DIR-DS-000-agent-config\NC-PROMPT-DS-016-opencode-research.md | prompt, agente-b, opencode, research, lobe-int-002 |
| NC-PROMPT-DS-017-antigravity-research.md | Prompt pesquisa profunda Antigravity/T0: Agente C (32763), ticket LOBE-INT-003. Hierarquia T0T3, 34 tools MCP, protocolos delegao [2026-04-13] | \DIR-DS-000-agent-config\NC-PROMPT-DS-017-antigravity-research.md | prompt, agente-c, antigravity, t0, research, lobe-int-003 |

---

### Servios e Tools Criados  2026-04-13

| Nome | Descrio | Local |
|---|---|---|
| NC-SVC-FR-014-dry-run-preview.py | SAVE-005: servio preview dry-run antes de escrita (183L, py=OK, ruff=0V) | 01_neocortex_framework\neocortex\core\services\ |
| NC-SVC-FR-015-task-broker.py | ORCH-301: TaskBroker persistente com polling, retry (3x backoff 248s), tracking (queued/running/done/failed) (220L) | 01_neocortex_framework\neocortex\core\services\ |
| NC-TOOL-FR-035-task.py | ORCH-302: MCP tool neocortex_task  execute/poll/cancel/list_queued, HTTP real, fallback registry (315L) | 01_neocortex_framework\neocortex\mcp\tools\ |

---

## Changelog

- [2026-04-12T16:48:00] Criado por T1 DS-B  extrao automtica de NC-NAM-FR-001-naming-convention.md (4 entradas NC-PROMPT-* / NC-DS-*).
- [2026-04-13T12:12:00] T0 Antigravity  Adicionados 5 novos registros: NC-DOC-DS-001, NC-PROMPT-DS-004/005/006, NC-PROMPT-FR-001 v4.
- [2026-04-13T15:53:00] T0 Antigravity  NC-PROMPT-DS-015/016/017 (lobes INT) + NC-SVC-FR-014/015 + NC-TOOL-FR-035 registrados.