# NC-TODO-DS-001  Roadmap PR-MCP (Sprint Imediato)
<!-- Temporrio: vigora at MCP-WQUEUE estar operacional -->
<!-- Gerado: 2026-04-12 | Atualizado: 2026-04-13 | Base: NC-STR-CC-001 + NC-ANA-INT-001 -->
<!-- SSOT: Este arquivo  a fonte de verdade do sprint pr-MCP -->

## Changelog
- [2026-04-13] NC-ANA-INT-001 aprovado: 6 checkpoints, 17 ajustes, faseamento completo
- [2026-04-13] NC-DS-042B APPROVED: NC-RES-CC-002 agora 191L (platformdirs adicionado)
- [2026-04-13] NC-DS-032: adicionar `platformdirs` + XDG cross-platform Windows
- [2026-04-13] NC-DS-031: renomear eventos para PreToolUse/PostToolUse/ToolError (padro MCP)
- [2026-04-13] Dependncias Fase 1 aprovadas: cachetools, ruamel.yaml, rich, platformdirs, filelock, notifypy
- [2026-04-12] Roadmap criado com 12 tickets NC-DS-029040
- [2026-04-14] NC-DOC-DS-005-topological-taxonomy.md criado  Bblia Topolgica do NeoCortex (30 tags vetoriais, frontmatter Ruamel obrigatrio)
- [2026-04-14] NC-DS-053 COMPLETED: Merge Cruzado e Unificao Definitiva do Tool Manifest  SSOT NC-TLM-FR-001-tool-manifest.json consolidado, scripts redundantes removidos

## Arquivos de Referncia Globais

| Smbolo | Path absoluto |
|---------|---------------|
| `@ROADMAP` | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md` |
| `@SSOT` | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md` |
| `@LOCKS` | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml` |
| `@BOOT` | `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md` |
| `$WORKER_PATTERNS` | `01_neocortex_framework/lobes/NC-LBE-DS-003-worker-patterns.mdc` |
| `@STRATEGY` | `DIR-RES-CC-001-claude-leak-workzone/NC-STR-CC-001-master-strategy.md` |
| `@COMPETITIVE` | `DIR-RES-CC-001-claude-leak-workzone/analysis-session-b/NC-ANA-CC-004-competitive-intel.md` |
| `@PLUGINS` | `DIR-RES-CC-001-claude-leak-workzone/analysis-session-b/NC-ANA-CC-005-plugins-deep.md` |
| `@KAIROS` | `DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-ANA-CC-005-kairos-deep.md` |
| `@IMPL_PLAN` | `[artifact] cc_leak_implementation_plan.md` |
| `@SYNTHESIS` | `DIR-RES-CC-001-claude-leak-workzone/NC-ANA-INT-001-synthesis-t0.md` |
| `@RES001` | `DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-001-validation-hooks-worker-review.md` |
| `@RES002` | `DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-002-validation-buddy-config-plugin.md` |
| `@RES003` | `DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-003-validation-scheduling-ttl-flags.md` |

---

## Estado Atual
```
Fila: AVAILABLE=0 | DONE=22 (19 formais + 3 lobes fora da fila)
Barreira: MCP-WQUEUE no implementado
Dispatch: Individual (1 agent = 1 task)
```

 **NC-DS-036 MANUAL (41L)**  TTLManager foi entregue como stub (41L). Ticket volta para AVAILABLE  precisa re-entrega com 80L.

## Dependncias Python Aprovadas (Fase 1)  @SYNTHESIS CP-002

| Lib | Verso | Para | Instalar? |
|---|---|---|---|
| `cachetools` | >=5.0 | FeatureFlagService, TTLManager | `pip install cachetools` |
| `ruamel.yaml` | >=0.18 | ProjectConfigLoader | `pip install ruamel.yaml` |
| `rich` | >=13.0 | SessionMate display | `pip install rich` |
| `platformdirs` | >=4.0 | XDG cross-platform Windows | `pip install platformdirs` |
| `filelock` | >=3.0 | Locks atmicos de arquivo | `pip install filelock` |
| `notifypy` | >=0.5 | PushNotification (opcional) | `pip install notify-py` |

---

## Ajustes Confirmados pela Pesquisa Internet  @SYNTHESIS CP-003

| Ticket | Ajuste | Impacto |
|---|---|---|
| NC-DS-029 | + backoff exponencial 102040s | Worker mais resiliente |
| NC-DS-029 | + classe PersistentWorker com start/stop/pause | API limpa |
| NC-DS-030 | + `rich` para display + `.nc/session_stats.json` | Histrico entre sesses |
| NC-DS-030 | + conquistas (3-5 badges iniciais) | Gamificao leve |
| NC-DS-031 | + timeout 2s por hook | Evitar bloqueio |
| NC-DS-031 | renomear: PreToolUse/PostToolUse/ToolError (padro MCP) | Interoperabilidade |
| NC-DS-032 | + `ruamel.yaml` + XDG + `NEOCORTEX_CONFIG_DIR` | Config robusta |
| NC-DS-032 | + `platformdirs` para XDG Windows-first | Compat Windows |
| NC-DS-033 | + campo `neocortex_min_version` no plugin.json | Versioning |
| NC-DS-034 | + `radon` como validador opcional (complexidade) | Qualidade extra |
| NC-DS-035 | cdigo base em @RES003 linhas 121-148 (PulseDaemon) | No partir do zero |
| NC-DS-036 | cdigo base em @RES003 linhas 150-179 (TTLManager) | No partir do zero |
| NC-DS-037 | + `cachetools.TTLCache` (no manual) | Cache maduro |
| NC-DS-038 | + exportar EXIT_CODE_PERMANENT=42 | Constante compartilhada |
| NC-DS-040 | + notifypy com ImportError fallback | Graceful degradation |

---

## Novos Lobes CC-Leak Criados (2026-04-13)
```
01_neocortex_framework/lobes/cc-leak/
  NC-LBE-CC-002-hooks-system.mdc         302L  (MentorHooks/GuardHooks)
  NC-LBE-CC-003-persistent-worker.mdc    290L  (PersistentWorker)
  NC-LBE-CC-004-confidence-review.mdc    312L  (ConfidenceReviewService)
  NC-LBE-CC-005-session-mate.mdc         230L  (SessionMate)
  NC-LBE-CC-006-project-config.mdc       318L  (.nc/ ProjectConfigLoader)
  NC-LBE-CC-007-plugin-template.mdc      347L  (NC-TOOL-FR-TEMPLATE)
  NC-LBE-CC-008-pulse-daemon.mdc         205L  (PulseDaemon/TickEngine)
  NC-LBE-CC-009-ttl-session-manager.mdc  206L  (TTLManager+IDValidator)
  NC-LBE-CC-010-feature-flags-channels.mdc 204L  (FeatureFlagService+ChannelNotifier)
```

## Novos Lobes de Integrao (2026-04-14)
```
02_memory_lobes/
  NC-LBE-INT-004-mission-control.mdc      (Mission Control Generic Adapter)
  NC-LBE-INT-005-pixel-agents.mdc         (Pixel Agents JSONL Bridge)
```

**Cruzamento com o que j existe:**
| Lobe Novo | Cruza com existente | Gap |  
|---|---|---|
| CC-002 hooks | NC-SEC-FR-001 @LOCKS | Falta interceptao ps-ao |
| CC-003 worker | NC-PROMPT-FR-002 checklist | Falta loop contnuo |
| CC-004 review | NC-SCR-FR-005 auto-approve | Substituir por score 0-100 |
| CC-005 session | NC-SVC-FR-006 metrics  | Adicionar camada de display |
| CC-006 config | neocortex_config.yaml  | Adicionar override local |
| CC-007 plugin | DIR-TMP-FR-001-templates  | Falta scaffolding padronizado |
| CC-008 daemon | pulse_scheduler.py  | Refatorar para event-driven |
| CC-009 TTL | NC-SVC-FR-004 cache  | Generalizar para entidades |
| CC-010 flags | neocortex_config.yaml  | Adicionar cache + rollout |
| INT-004 MissionCtrl | neocortex_gateway | Setup do Generic Adapter pendente |
| INT-005 PixelAgents | NC-SCR-FR-016 | Implementao da bridge pendente |


---

## Sprint Pr-MCP  Tickets com Cross-References

### NC-DS-029  Worker Persistente (Ralph-Wiggum)
```
ttulo:       WORKER-001  Worker persistente em loop contnuo
prioridade:    IMEDIATO
esforo:      ~150L
write_zone:   DIR-DS-000-agent-config/
arquivo:      DIR-DS-000-agent-config/NC-PROMPT-DS-003-persistent-worker.md
source:       @PLUGINS seo "11. ralph-wiggum" (linha 155-162)
              @STRATEGY seo D.1 (linhas 153-164)
reference:    @PLUGINS, @KAIROS, $WORKER_PATTERNS
              NC-PROMPT-FR-002-pre-mcp-manual-checklist.md
depende:      nenhuma
no modificar: server.py, sub_server.py (@LOCKS)
```

### NC-DS-030  Buddy Light (Session Stats)
```
ttulo:       BUDDY-001  Stats de sesso (gamificao leve)
prioridade:    IMEDIATO
esforo:      ~80L
write_zone:   01_neocortex_framework/neocortex/core/services/
arquivo:      NC-SVC-FR-009-session-buddy.py
source:       @COMPETITIVE seo 1.6 "Buddy" (linha 53-57)
              @STRATEGY seo D.2 (linhas 166-177)
reference:    NC-SVC-FR-006-metrics-collector.py (j existe, leia antes)
              @COMPETITIVE para entender escopo Buddy
depende:      NC-SVC-FR-006 (j existe em disco )
```

### NC-DS-031  Hookify-like (HookRegistry YAML+Python)
```
ttulo:       HOOK-001  Sistema de hooks reativos ps-ao
prioridade:    IMEDIATO
esforo:      ~250L
write_zone:   01_neocortex_framework/neocortex/core/hooks/
arquivos:
  - NC-HK-FR-001-hook-registry.py
  - NC-HK-FR-002-example-hook.py
  - examples/.nc/hooks/ssot-guard.yaml
source:       @PLUGINS seo 1 "security-guidance" (linhas 45-61)
              @COMPETITIVE seo 1.2 "Hookify" (linhas 29-33)
              @STRATEGY seo D.3 (linhas 179-193)
              DIR-RES-CC-001-claude-leak-workzone/analysis-session-b/NC-ANA-CC-003-plugin-patterns.md
reference:    @PLUGINS para padro de hooks.json + Python externo
              NC-SEC-FR-001-atomic-locks.yaml (para criar guard de SSOT)
depende:      nenhuma
```

### NC-DS-032  Config por Projeto (`.nc/`)
```
ttulo:       CONFIG-001  ProjectConfigLoader local
prioridade:    IMEDIATO
esforo:      ~150L
write_zone:   01_neocortex_framework/neocortex/core/config/
arquivos:
  - NC-CFG-FR-004-project-loader.py
  - examples/.nc/config.yaml
source:       @COMPETITIVE seo 1.8 ".claude/ per-project" (linhas 64-67)
              @STRATEGY seo D.4 (linhas 195-207)
reference:    01_neocortex_framework/neocortex/neocortex_config.yaml (config global)
              @PLUGINS seo C.4 "Configurao por Projeto" (linhas 193-195)
depende:      NC-CFG-FR-001 (config global)
```

### NC-DS-033  Template NC-TOOL-FR-* (Plugin System)
```
ttulo:       PLUGIN-001  Template padronizado de plugin/tool
prioridade:    IMEDIATO
esforo:      ~300L (10 arquivos template)
write_zone:   01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TOOL-FR-TEMPLATE/
arquivos:
  - NC-TOOL-FR-TEMPLATE/NC-CFG-FR-001-plugin.json
  - NC-TOOL-FR-TEMPLATE/commands/NC-CMD-EXAMPLE.md
  - NC-TOOL-FR-TEMPLATE/hooks/NC-HK-EXAMPLE.py
  - NC-TOOL-FR-TEMPLATE/README.md
  - scripts/NC-SCR-FR-012-new-tool.py (scaffolding script)
source:       @PLUGINS seo 9 "plugin-dev" (linhas 141-146)
              @PLUGINS seo A "Estrutura de Plugin" (linhas 168-181)
              @STRATEGY seo D.5 (linhas 209-224)
reference:    @PLUGINS para estrutura completa .claude-plugin/
              @SSOT para nomear arquivos do template
depende:      nenhuma
```

### NC-DS-034  Confidence Review Score (0-100)
```
ttulo:       REVIEW-001  Validao de handoffs com confidence score
prioridade:    NEXT
esforo:      ~400L
write_zone:   01_neocortex_framework/neocortex/core/review/
arquivos:
  - NC-REV-FR-001-confidence-review.py
  - validators/NC-VAL-FR-001-naming-validator.py
  - validators/NC-VAL-FR-002-compile-validator.py
  - validators/NC-VAL-FR-003-locks-validator.py
  - validators/NC-VAL-FR-004-ssot-validator.py
source:       @PLUGINS seo 3 "code-review" (linhas 81-91)
              @COMPETITIVE seo 3.1 "Auto-review" (linhas 108-111)
              @STRATEGY seo D.6 (linhas 226-239)
reference:    NC-SCR-FR-005-auto-approve.py (substituir)
              batch_approve.py (referncia de lgica atual)
              @LOCKS para lista de arquivos proibidos
depende:      NC-SCR-FR-005 (substituir)
```

### NC-DS-035  KairosService (Event-driven Pulse)
```
ttulo:       SCHED-001  Refatorao pulse_scheduler  event-driven
prioridade:    NEXT
esforo:      ~200L
write_zone:   01_neocortex_framework/neocortex/core/services/
arquivo:      NC-SVC-FR-010-kairos-service.py
source:       @KAIROS seo 4 "Analogia NeoCortex" (linhas 86-122)
              @COMPETITIVE seo 1.5 "KAIROS" (linhas 47-51)
              @STRATEGY seo D.7 e B.1 flags KAIROS_* (linhas 241-253)
reference:    @KAIROS (leia inteiro antes de implementar)
              01_neocortex_framework/neocortex/core/pulse_scheduler.py (refatorar)
              DIR-RES-CC-001-claude-leak-workzone/kairos_snippets.txt (padres raw)
              DIR-RES-CC-001-claude-leak-workzone/scheduler_files.txt
depende:      pulse_scheduler.py (atual, manter compatibilidade)
```

### NC-DS-036  TTLManager
```
ttulo:       TTL-001  Gesto granular de expirao por entidade
prioridade:    NEXT
esforo:      ~150L
write_zone:   01_neocortex_framework/neocortex/core/services/
arquivo:      NC-SVC-FR-011-ttl-manager.py
source:       @STRATEGY seo B.4 constantes (linhas 77-87): 3h55m, 5min, ~5h, sessionTimeoutMs
              @STRATEGY seo D.8 (linhas 255-266)
              DIR-RES-CC-001-claude-leak-workzone/timer_files.txt (valores reais)
reference:    @KAIROS (integrar com KairosService)
              NC-SVC-FR-004-cache-service.py (modelo de TTL existente)
depende:      NC-DS-035 (KairosService)
```

### NC-DS-037  Feature Flags com Cache
```
ttulo:       FLAG-001  FeatureFlagService com TTL 1h
prioridade:    Complementar
esforo:      ~120L
write_zone:   01_neocortex_framework/neocortex/core/config/
arquivo:      NC-CFG-FR-002-feature-flags.py
source:       @COMPETITIVE seo 1.7 "Growthbook" (linhas 59-62)
              @STRATEGY seo B.5 "Growthbook (cache 1h)" (linhas 93-94)
              @STRATEGY seo D.9 (linhas 268-285)
reference:    01_neocortex_framework/neocortex/neocortex_config.yaml
              (adicionar seo feature_flags a este arquivo)
depende:      nenhuma
```

### NC-DS-038  ID Validator
```
ttulo:       UTIL-004  Validador de IDs (tickets, sesses, agents)
prioridade:    Complementar
esforo:      ~80L
write_zone:   01_neocortex_framework/neocortex/core/utils/
arquivo:      NC-UTL-FR-004-id-validator.py
source:       @STRATEGY seo B.3 "validateBridgeId" (linha 73)
              @STRATEGY seo D.10 (linhas 287-300)
reference:    NC-UTL-FR-002-hash-utils.py (checksum)
              NC-UTL-FR-001-yaml-safe-parser.py (modelo)
depende:      nenhuma
```

### NC-DS-039  Channel Notifier
```
ttulo:       CHANNEL-001  Notificaes push MCP (KAIROS_CHANNELS)
prioridade:    Complementar
esforo:      ~150L
write_zone:   01_neocortex_framework/neocortex/core/services/
arquivo:      NC-SVC-FR-012-channel-notifier.py
source:       @STRATEGY seo B.1 flag KAIROS_CHANNELS (linhas 54-55)
              @STRATEGY seo D.11 (linhas 302-315)
              DIR-RES-CC-001-claude-leak-workzone/kairos_snippets.txt (grep KAIROS_CHANNELS)
reference:    NC-SVC-FR-005-event-bus.py (integrar, j existe )
depende:      NC-SVC-FR-005 (EventBus, j existe )
```

### NC-DS-040  Push Notification Tool
```
ttulo:       TOOL-030  PushNotificationTool MCP
prioridade:    Complementar
esforo:      ~100L
write_zone:   01_neocortex_framework/neocortex/mcp/tools/
arquivo:      NC-TOOL-FR-030-push-notification.py
source:       @STRATEGY seo B.1 flag KAIROS_PUSH_NOTIFICATION (linhas 55-56)
              @STRATEGY seo D.12 (linhas 317-329)
reference:    NC-SVC-FR-005-event-bus.py (integrar)
              01_neocortex_framework/neocortex/mcp/ (estrutura existente)
              NC-TOOL-FR-030 (naming convention @SSOT)
depende:      NC-SVC-FR-005 (EventBus ), NC-DS-039 (Channel Notifier)
```

---

## Regras Sprint

- Dispatch: 1 agent = 1 ticket = prompt direto
- Proibido: server.py, sub_server.py, NC-NAM-FR-001 (@LOCKS)
- Handoff: `DIR-DS-002-audit-logs/NC-DS-{NUM}-handoff-{YYYYMMDD-HHMMSS}.yaml`
- Aprovao: `batch_approve.py` (80L  APPROVED)
- Contexto: Ler `$WORKER_PATTERNS` + `@BOOT` + **`@SYNTHESIS`** no incio de CADA sesso
- Dependncias: Instalar libs Fase 1 antes de iniciar implementao

## Relacionamentos de Arquivos (destes tickets)

```
NC-DS-029  l: @SYNTHESIS, @RES001-p7, $WORKER_PATTERNS
            gera: NC-PROMPT-DS-003-persistent-worker.md
NC-DS-030  l: @SYNTHESIS, @RES002-p6, NC-SVC-FR-006
            gera: NC-SVC-FR-009-session-buddy.py + .nc/session_stats.json
NC-DS-031  l: @SYNTHESIS, @RES001-p1, @RES001-p2, NC-SEC-FR-001
            gera: NC-HK-FR-001/002 + examples/.nc/hooks/ssot-guard.yaml
NC-DS-032  l: @SYNTHESIS, @RES002-p2/7/10, neocortex_config.yaml
            gera: NC-CFG-FR-004-project-loader.py + examples/.nc/config.yaml
NC-DS-033  l: @SYNTHESIS, @RES002-p8, @SSOT
            gera: NC-TOOL-FR-TEMPLATE/ + NC-SCR-FR-012-new-tool.py
NC-DS-034  l: @SYNTHESIS, @RES001-p10, batch_approve.py
            gera: NC-REV-FR-001 + validators/NC-VAL-FR-001/002/003
NC-DS-035  l: @SYNTHESIS, @RES003-p1, @RES003 linhas 121-148
            gera: NC-SVC-FR-010-kairos-service.py (base: cdigo de @RES003)
NC-DS-036  l: @SYNTHESIS, @RES003-p7, @RES003 linhas 150-179
            gera: NC-SVC-FR-011-ttl-manager.py (base: cdigo de @RES003)
NC-DS-037  l: @SYNTHESIS, @RES003-p7, neocortex_config.yaml
            gera: NC-CFG-FR-002-feature-flags.py
NC-DS-038  l: @SYNTHESIS, @RES003-p10, NC-UTL-FR-002
            gera: NC-UTL-FR-004-id-validator.py
NC-DS-039  l: @SYNTHESIS, @RES003-p9, NC-SVC-FR-005
            gera: NC-SVC-FR-012-channel-notifier.py
NC-DS-040  l: @SYNTHESIS, @RES003-p9, NC-SVC-FR-005
            gera: NC-TOOL-FR-030-push-notification.py
### NC-DS-047  Saneamento Massivo de Arquivos (Fase 1/2)
```
ttulo:       SANE-001  Aplicao Regra 007 (Arquivos Core)
prioridade:    IMEDIATO
esforo:      Massivo (vrios arquivos)
write_zone:   01_neocortex_framework/neocortex/
referncia:   .agents/rules/NC-RULE-007-tagging-system.mdc
depende:      Nenhuma
```

### NC-DS-048  Saneamento de Lobos e SSOT (Fase 2/2)
```
ttulo:       SANE-002  Aplicao Regra 007 (Lobos e Docs)
prioridade:    IMEDIATO
esforo:      Massivo (vrios arquivos)
write_zone:   02_memory_lobes/ e DIR-DOC-FR-001-docs-main/
referncia:   .agents/rules/NC-RULE-007-tagging-system.mdc
depende:      NC-DS-047
```

### NC-DS-049  Auditoria Estrutural e Graph Builder
```
ttulo:       AUDIT-001  Otimizao de Tokens, Expargo da Raiz e Manifest Factory
prioridade:    IMEDIATO
esforo:      ~200L
write_zone:   Raiz e 01_neocortex_framework/scripts/
arquivo:      NC-SCR-FR-003-manifest-factory.py (subir para Knowledge Graph Builder)
depende:      NC-DS-047, NC-DS-048
```

### NC-DS-050  Validao Estrita do Mission Control
```
ttulo:       VAL-001  Refatorao Assncrona e Anti-Corruption Layer
prioridade:    IMEDIATO
esforo:      ~150L
write_zone:   01_neocortex_framework/neocortex/core/adapters/
arquivo:      NC-ADP-FR-001-mission-control.py
depende:      Nenhuma (Pode rodar em paralelo)
```

### NC-DS-051  VectorDB Connection Engine
```
ttulo:       VCT-001  Base Engine setup para LanceDB/Chroma
prioridade:    IMEDIATO (Agente 1)
esforo:      ~200L
write_zone:   01_neocortex_framework/neocortex/core/services/
arquivo:      NC-SVC-FR-013-vector-orchestrator.py
depende:      Nenhuma
```

### NC-DS-052  Knowledge Graph Vector Builder
```
ttulo:       VCT-002  Refatorao do Manifest Factory para Vector Embedder
prioridade:    IMEDIATO (Agente 2)
esforo:      ~250L
write_zone:   01_neocortex_framework/scripts/
arquivo:      NC-SCR-FR-003-knowledge-graph-builder.py
depende:      NC-DS-051
```

### NC-DS-053  MCP Dormant Tools Audit & Revival
```
ttulo:       MCP-001  Merge Cruzado e Unificao Definitiva do Tool Manifest
prioridade:    IMEDIATO (Agente 3)
esforo:      ~550L (Auditoria, Merge via Cross-Reference, Update AST/Dependncias, Validao)
write_zone:   01_neocortex_framework/neocortex/mcp/tools/ e DIR-CORE-FR-001-core-central/
arquivo:      NC-TLM-FR-001-tool-manifest.json
depende:      Nenhuma
status:        COMPLETED (2026-04-14)
```

### NC-DS-054  Thread-Safe Async Validations
```
ttulo:       VAL-002  Envelopamento Async da Anti-Corruption Layer para VectorDB
prioridade:    IMEDIATO (Agente 4)
esforo:      ~150L
write_zone:   01_neocortex_framework/neocortex/core/review/
arquivo:      NC-VAL-FR-005-async-thread-validator.py
depende:      Nenhuma
```
```
