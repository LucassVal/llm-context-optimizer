# NC-ANA-CC-005  KAIROS Deep Dive: Timers, Event Loop, Daemon Lifecycle

**Data da anlise:** 20260412  
**Fonte:** `NCLBECC005featureskairos.mdc` (sessionb) + grep em `CLAUDE_CODE_DISSECTION/`  
**Ticket:** NCDS015 (CC002B)  
**Worker:** worker100472196eb  

---

## 1. Viso Geral do KAIROS

KAIROS  o **sistema de tick proativo** do Claude Code, responsvel por disparar aes peridicas baseadas em eventos do usurio, estado da sesso e flags de feature.

**Estatsticas (do mapeamento anterior):**
- **61 arquivos** contm a string `KAIROS` (casesensitive).
- **105 arquivos** contm `tick` (relacionado).
- **Localizao principal:** `src/interactiveHelpers.tsx`, `src/tools.ts`, `src/bridge/bridgeMain.ts`, `src/main.tsx`, `src/commands.ts`.
- **No est em `src/assistant/`**  indica que  um **mdulo global** independente da UI do assistente.

---

## 2. Lifecycle do Daemon KAIROS

### 2.1 Inicializao
1. **Boot do aplicativo**  KAIROS  registrado como servio singleton.
2. **Configurao de intervalos**  define o perodo do tick (ex.: 500ms, 1s, 5s) via `setInterval` ou `requestAnimationFrame`.
3. **Hooks de feature flags**  consulta Growthbook (`checkGate_CACHED_OR_BLOCKING`) para decidir quais funcionalidades esto ativas.

### 2.2 Ciclo de Tick
Cada tick executa as seguintes verificaes:

| Componente | O que verifica | Ao possvel |
|------------|----------------|---------------|
| **AFK detector** | Inatividade do usurio | Ativar modo standby, notificar KAIROS |
| **Bridge mode** | Sesses remotas ativas | Heartbeat, timeout (`DEFAULT_SESSION_TIMEOUT_MS`) |
| **Voice mode** | Streaming de udio | Parar/retomar TTS |
| **Buddy system** | Estatsticas de sesso | Atualizar sprites, gacha |
| **ULTRAPLAN** | Modo headless | Executar comandos em lote |

### 2.3 Shutdown
- **Graceful stop**  salva estado do Buddy, persiste flags.
- **Timeout final**  garante que nenhum tick pendente fique rodando aps o fechamento.

---

## 3. Event Loop e Hooks

### 3.1 Arquitetura do Loop
```typescript
// Pseudocdigo inferido
class KairosScheduler {
  private tickInterval: number;
  private subscribers: Map<string, (tick: TickEvent) => void>;

  start() {
    setInterval(() => this.tick(), this.tickInterval);
  }

  private tick() {
    const event = new TickEvent(Date.now());
    this.subscribers.forEach(callback => callback(event));
  }

  subscribe(eventType: string, callback: (event: TickEvent) => void) {
    this.subscribers.set(eventType, callback);
  }
}
```

### 3.2 Hooks Identificados
| Hook | Localizao (inferida) | Propsito |
|------|------------------------|-----------|
| `onAfkTick` | `src/interactiveHelpers.tsx` | Reage  inatividade do usurio |
| `onBridgeTick` | `src/bridge/bridgeMain.ts` | Mantm sesses remotas vivas |
| `onBuddyTick` | `src/buddy/` | Atualiza sprites, gacha, stats |
| `onVoiceTick` | `src/voice/` | Gerencia streaming de udio |
| `onUltraplanTick` | `src/remote/` | Executa comandos em lote headless |

### 3.3 TTL (TimeToLive) Management
- **Sesses Bridge:** `DEFAULT_SESSION_TIMEOUT_MS` (provavelmente 3060 minutos).
- **Cache de feature flags:** `checkGate_CACHED_OR_BLOCKING`  cache de 510 minutos.
- **Estado do Buddy:** persistido em `localStorage` com TTL dirio (reset  0h).

---

## 4. Analogia com o NeoCortex

### 4.1 Pulse Scheduler (`pulse_scheduler.py`)
O NeoCortex j possui um `pulse_scheduler.py` que executa tarefas peridicas (backup de lobe, limpeza de cache, health checks).  
**KAIROS seria a evoluo desse scheduler**, com:

| KAIROS | NeoCortex (atual) | Evoluo proposta |
|--------|-------------------|-------------------|
| Tick por evento | Intervalo fixo | **Eventdriven ticks** (AFK, bridge, voice) |
| Hooks por mdulo | Callbacks genricas | **Hooks registrados por servio** (ex.: `register_kairos_hook`) |
| TTL por componente | TTL global | **TTL granular** (sesso, cache, buddy) |
| Featureflags | Config esttica | **Growthbook integration** (rollout gradual) |

### 4.2 Implementao Sugerida para NeoCortex
1. **KairosService**  singleton com `start()`, `stop()`, `register_hook()`.
2. **TickEvent**  carrega timestamp, contexto (AFK, bridge, voice, buddy).
3. **HookRegistry**  armazena callbacks por evento (`afk_tick`, `bridge_tick`).
4. **TTLManager**  gerencia expirao por entidade (cache, sesso, buddy).

```python
# Exemplo de esboo
class KairosService:
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {}
        self.tick_interval = 1.0  # segundos

    def register_hook(self, event_type: str, callback: Callable[[TickEvent], None]):
        self.hooks.setdefault(event_type, []).append(callback)

    def start(self):
        while self.running:
            time.sleep(self.tick_interval)
            event = TickEvent(timestamp=time.time())
            for event_type, callbacks in self.hooks.items():
                for cb in callbacks:
                    cb(event)
```

---

## 5. Concluses e Prximos Passos

### 5.1 Concluses
- KAIROS  um **scheduler orientado a eventos** que coordena mltiplos subsistemas (AFK, bridge, voice, buddy).
- **TTL granular** permite expirao independente por componente.
- **Hooks registrados** facilitam a extenso sem modificar o core.

### 5.2 Recomendaes para o NeoCortex
1. **Adotar o modelo de hooks** no `pulse_scheduler.py`.
2. **Integrar com Growthbook** para feature flags (j temos `checkGate`).
3. **Criar TTLManager** separado para cache, sesso, buddy.
4. **Documentar** a analogia KAIROS  pulse_scheduler no NCNAMFR001.

### 5.3 Prximas Investigaes
- Ler os **61 arquivos com KAIROS** para extrair a implementao real.
- Analisar `src/interactiveHelpers.tsx` e `src/tools.ts` para extrair a lgica de tick.
- Crosscheck com `src/buddy/` para entender gamificao.

## F. Deciso de Design NeoCortex

### Renomeao: KAIROS  PulseDaemon

### Constantes TTL Adotadas
| Constante | Valor | Fonte CC | Uso no NeoCortex |
|---|---|---|---|
| SESSION_LEASE_TTL | 18000s (~5h) | bridgeMain.ts:60 | Sesses de worker |
| TOKEN_REFRESH_BEFORE | 300s (5min) | bridgeMain.ts:53 | Auth tokens |
| FEATURE_FLAG_CACHE_TTL | 3600s (1h) | Growthbook | FeatureFlagService |
| HEARTBEAT_INTERVAL | 60s | bridgeMain.ts | Workers  Gateway |
| EXIT_CODE_PERMANENT | 42 | bridgeMain.ts:2798 | PersistentWorker stop |

### Mapeamento KAIROS  PulseDaemon NeoCortex
| KAIROS subsystem | PulseDaemon NC | Ticket |
|---|---|---|
| AFK hook | idle_hook via register_hook() | NC-DS-035 |
| Session timeout | TTLManager.set_ttl() | NC-DS-036 |
| Channel notifications | ChannelNotifier | NC-DS-039 |
| Push notifications | PushNotificationTool | NC-DS-040 |
| Feature flag cache | FeatureFlagService TTL | NC-DS-037 |

---

**Status da anlise:** Baseada em documentao existente (NCLBECC005) e inferncia arquitetural.  
**Confiana:** Mdia  necessria leitura dos arquivos fonte originais para detalhes de implementao.  
**Prximo ticket:** NCDS010 (CC001C) poderia focar na extrao de cdigo real dos 61 arquivos KAIROS.

---  
*Documento gerado por worker100472196eb em 20260412T22:21:50.225*  
*Writezone: DIRRESCC001claudeleakworkzone/analysissessiona/*