# PROMPT AGENT 3  Sub-lobes KAIROS/Scheduling + Pesquisa (TTL / Flags / Utils)
# Cole este prompt em uma JANELA LIMPA (nova sesso sem contexto anterior)
# Data: 2026-04-12 | Leia este arquivo inteiro antes de comear

---

## CONTEXTO OBRIGATRIO  Leia estes arquivos ANTES de qualquer ao

1. `01_neocortex_framework/lobes/NC-LBE-DS-003-worker-patterns.mdc`  estado atual
2. `DIR-RES-CC-001-claude-leak-workzone/NC-STR-CC-001-master-strategy.md`  sees B.1-B.5, D.5D.12
3. `DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-ANA-CC-005-kairos-deep.md`  KAIROS completo
4. `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-004-cache-service.py`  TTL existente
5. `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-005-event-bus.py`  EventBus existente

---

## PARTE 1  Criar Sub-Lobes CC Leak (conhecimento fixado em pedra)

Crie os seguintes arquivos em `01_neocortex_framework/lobes/cc-leak/`:

### 3A. NC-LBE-CC-008-pulse-daemon.mdc
Documente extensivamente (mnimo 200 linhas):
- Arquitetura completa do KAIROS no CC (evento, tick, TTL, subsistemas)
- Hooks por subsistema: AFK hook, bridge hook, voice hook, channel hook
- Flags: KAIROS_CHANNELS, KAIROS_PUSH_NOTIFICATION, PROACTIVE
- Eventos: worker_idle, queue_empty, session_timeout, token_refresh
- Constantes TTL reais extradas do cdigo:
  - Session lease: ~5h (SESSION_LEASE_TTL = 18000s)
  - Token refresh: 5min antes de expirar
  - Heartbeat interval: 1min
  - Feature flag cache Growthbook: 1h
- Deciso de design NeoCortex: KAIROS  PulseDaemon / TickEngine
- Mapping: `NC-SVC-FR-010-kairos-service.py`
- Diferena vs pulse_scheduler.py atual (intervalo fixo  event-driven)
- API proposta: register_hook(event, callback), start(), stop(), fire(event)
- Como integrar TTLManager (NC-DS-036) com o PulseDaemon

### 3B. NC-LBE-CC-009-ttl-session-manager.mdc
Documente extensivamente (mnimo 120 linhas):
- Como sessionTimers, tokenRefresh funcionam no CC (bridgeMain.ts)
- sessionIngressTokens: gesto de tokens de autenticao por sesso
- Padro de refresh proativo (5min antes): evitar expirao em uso
- BridgeHeadlessPermanentError: EXIT_CODE_PERMANENT = 42 (no-retentvel)
- validateBridgeId(): formato e checksum de IDs de sesso/bridge
- Deciso de design NeoCortex:  TTLManager + IDValidator
- Mapping: `NC-SVC-FR-011-ttl-manager.py` + `NC-UTL-FR-004-id-validator.py`
- Tabela de TTLs adotados no NeoCortex (com justificativa)

### 3C. NC-LBE-CC-010-feature-flags-channels.mdc
Documente extensivamente (mnimo 100 linhas):
- Feature flags do CC: checkGate, checkGate_CACHED_OR_BLOCKING, Growthbook
- KAIROS_CHANNELS: como funciona channel notification push MCP
- KAIROS_PUSH_NOTIFICATION: PushNotificationTool, como  ativado
- Integrao Growthbook: cache de 1h, rollout percentual
- Deciso de design NeoCortex:  FeatureFlagService + ChannelNotifier
- Mapping: `NC-CFG-FR-002-feature-flags.py` + `NC-SVC-FR-012-channel-notifier.py`
- Exemplo de config YAML para feature_flags no neocortex_config.yaml

---

## PARTE 2  Pesquisa Internet (validao e alternativas)

Para cada palavra-chave, pesquise na internet e traga 3 pontos.
Formato obrigatrio:
```
### [PALAVRA-CHAVE]
Fonte: [URL ou referncia]
 Faz sentido? [nossa abordagem vs mercado]
 Alternativa melhor? [lib, padro, framework, com link]
 Como melhorar? [mudana especfica no nosso design]
```

SOBRE O QUE J TEMOS:
- "python event-driven scheduler hooks callbacks"
- "python in-memory TTL cache expiration callback"
- "python SQLite atomic task queue workers"
- "python YAML safe loader concurrent access"
- "python SHA256 file integrity verification"

SOBRE O QUE QUEREMOS IMPLEMENTAR (NC-DS-035/036/037/038/039/040):
- "event-driven pulse scheduler python alternatives APScheduler"
- "TTL manager entity expiration python implementation"
- "feature flag service python open source Unleash Flagsmith"
- "MCP push notification server tool implementation"
- "python ID validator UUID format checksum"
- "agent heartbeat protocol distributed workers python"

Compile em:
`DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-003-validation-scheduling-ttl-flags.md`
(mnimo 200 linhas)

---

## PARTE 3  Atualizar NC-ANA-CC-005-kairos-deep com Nomes NeoCortex

Leia: `DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-ANA-CC-005-kairos-deep.md`

Adicione uma seo no FINAL:
```
## Seo F  Deciso de Design NeoCortex

### Renomeao Oficial
KAIROS  PulseDaemon (nome interno definitivo no NeoCortex)

### Constantes TTL Adotadas
| Constante | Valor | Fonte CC | Para uso em |
|---|---|---|---|
| SESSION_LEASE_TTL | 18000s (~5h) | bridgeMain.ts:60 | Sesses de worker |
| TOKEN_REFRESH_BEFORE | 300s (5min) | bridgeMain.ts:53 | Auth tokens |
| FEATURE_FLAG_CACHE_TTL | 3600s (1h) | Growthbook cache | FeatureFlagService |
| HEARTBEAT_INTERVAL | 60s | bridgeMain.ts | Workers  Gateway |
| EXIT_CODE_PERMANENT | 42 | bridgeMain.ts:2798 | PersistentWorker stop |

### Mapeamento de Implementao
| KAIROS subsystem | PulseDaemon NeoCortex | Ticket |
|---|---|---|
| AFK hook | idle_hook via register_hook() | NC-DS-035 |
| Session timeout | TTLManager.set_ttl() | NC-DS-036 |
| Channel notifications | ChannelNotifier | NC-DS-039 |
| Push notifications | PushNotificationTool | NC-DS-040 |
| Feature flag cache | FeatureFlagService TTL | NC-DS-037 |
```

NO modifique o restante do documento.

---

## ENTREGA

Gere handoff: `DIR-DS-002-audit-logs/NC-DS-043-handoff-{YYYYMMDD-HHMMSS}.yaml`
```yaml
ticket_id: NC-DS-043
status: PENDING_REVIEW
lines_added: [total real das 3 partes]
files_created:
  - 01_neocortex_framework/lobes/cc-leak/NC-LBE-CC-008-pulse-daemon.mdc
  - 01_neocortex_framework/lobes/cc-leak/NC-LBE-CC-009-ttl-session-manager.mdc
  - 01_neocortex_framework/lobes/cc-leak/NC-LBE-CC-010-feature-flags-channels.mdc
  - DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-003-validation-scheduling-ttl-flags.md
files_modified:
  - DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-ANA-CC-005-kairos-deep.md
```

## REGRAS
- NO toque em: server.py, sub_server.py, NC-NAM-FR-001 (@LOCKS)
- NO crie arquivos .py  apenas .mdc e .md
- Janela 100k: se contexto ficar pesado, salve o handoff antes de compactar
