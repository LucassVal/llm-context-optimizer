# NC-ANA-CC-004  O que a Anthropic tem que ns no temos?

**Data da anlise:** 20260412  
**Escopo:** Claude Code vazado (freecode + officialclaudecode)  
**Ticket:** NCDS009 (CC001B)

---

## Resumo Executivo

A Anthropic construiu um **ecossistema maduro** com 13 plugins oficiais, sistema de hooks leve, telemetria abrangente, feature flags, bridge para sesses remotas, e um modelo de tick proativo (KAIROS). **Nosso NeoCortex est mais enxuto e seguro** (atomic locks, mentor mode, policy loader), mas falta a **extensibilidade padronizada** e a **gamificao** (Buddy) que aumentam a adoo.

**Prioridade de incorporao:**
1. **Sistema de hooks estilo hookify** (baixo esforo, alto retorno).
2. **Plugin marketplace** interno (mdio esforo).
3. **Feature flags com Growthbook** (j temos parcial).
4. **Modo Buddy** (gamificao para devs).

---

## 1. FORAS DA ANTHROPIC (que ns NO temos)

### 1.1 Plugin Marketplace (13 plugins oficiais)
- **Extensibilidade padronizada**  qualquer dev pode criar plugin.
- **Autodiscovery**  `cc --plugindir` detecta automaticamente.
- **Documentao rica**  cada plugin tem README detalhado.
- **Ns temos:** apenas tools MCP, sem sistema de plugins.

### 1.2 Hookify  Governana Leve
- **Regras em Markdown+YAML** (legvel para nodevs).
- **Ativao imediata** (sem restart).
- **Eventos granulares** (bash, file, stop, prompt).
- **Ns temos:** atomic locks (bloqueio proativo), mas no hooks reativos.

### 1.3 Telemetria Abrangente
- **85 arquivos** com `telemetry`.
- **Integrao com Datadog, firstparty logging, Growthbook.**
- **Mtricas por sesso, comando, erro.**
- **Ns temos:** logging bsico, sem telemetria de produo.

### 1.4 Bridge Mode  Sandbox Remota
- **31 arquivos** em `src/bridge/`.
- **Sesses isoladas** em infraestrutura remota.
- **Timeout, capacity management, token refresh.**
- **Ns temos:** isolamento via lobe local, sem sandbox remota.

### 1.5 KAIROS  Tick Proativo
- **61 arquivos** com `KAIROS`.
- **Sistema de deciso agir vs ficar quieto.**
- **Possivelmente MLdriven.**
- **Ns temos:** scheduler de heartbeat (PulseScheduler), mas no proativo.

### 1.6 Buddy  Gamificao
- **6 arquivos** em `src/buddy/`.
- **Tamagotchi com stats, gacha, sprites ASCII.**
- **Engaja usurios com recompensas.**
- **Ns temos:** nenhum elemento de gamificao.

### 1.7 Growthbook  Feature Flags
- **`checkGate_CACHED_OR_BLOCKING`**.
- **Rollout progressivo, A/B testing.**
- **Ns temos:** `checkGate` bsico, sem cache nem rollout.

### 1.8 Configurao por Projeto (`.claude/`)
- **Diretrio `.claude/`** na raiz armazena configs de todos os plugins.
- **Exemplos em `examples/settings/`.**
- **Ns temos:** configurao global (`neocortex_config.yaml`), no por projeto.

---

## 2. FORAS DO NEOCORTEX (que eles NO tm)

### 2.1 Atomic Locks
- **Bloqueio proativo** de arquivos protegidos (@LOCKS).
- **Impede corrupo de SSOT** antes de acontecer.
- **Eles tm:** apenas hooks reativos (psao).

### 2.2 Mentor Mode
- **Filtro prexecuo** que injeta contexto + regras antes do LLM.
- **Cobre subservers** (20 tools).
- **Eles tm:** hooks apenas para tools especficas.

### 2.3 Policy Loader + Rate Limiting
- **Limites de tokens/budget/timeout por role.**
- **Antirunaway** na raiz.
- **Eles tm:** rate limit apenas no nvel da API?

### 2.4 Lobe Isolation
- **Cada agente em diretrio separado** (lobe).
- **Crosslobe write blocking.**
- **Eles tm:** bridge para sesses remotas, mas no isolamento local.

### 2.5 SSOT Ubquo
- **NCNAMFR001** como fonte nica de naming.
- **Roadmap centralizado** (NCTODOFR001).
- **Eles tm:** documentao fragmentada nos plugins.

### 2.6 Save Points (futuro)
- **Snapshot diff antes de escrita** (SAVE002 pendente).
- **Rollback automtico** (SAVE003 pendente).
- **Eles tm:** no identificado.

---

## 3. OPORTUNIDADES DE MELHORIA (incorporar do Claude Code)

### 3.1 Prioridade Alta
| Item | Descrio | Esforo |
|------|-----------|---------|
| **Hookifylike** | Regras Markdown+YAML em `.claude/` | Baixo |
| **Plugin system** | Estrutura para NCTOOLFR* como plugins | Mdio |
| **Buddy light** | Stats simples de sesso (comandos, acertos) | Baixo |
| **Projectlevel config** | `.claude/` na raiz do projeto | Baixo |

### 3.2 Prioridade Mdia
| Item | Descrio | Esforo |
|------|-----------|---------|
| **Growthbook completo** | Cache + rollout progressivo | Mdio |
| **Bridge mode light** | Sandbox remota para tools perigosas | Alto |
| **KAIROS tick** | Heartbeat proativo para manuteno | Mdio |
| **Telemetria no intrusiva** | Mtricas annimas de uso | Mdio |

### 3.3 Prioridade Baixa
| Item | Descrio | Esforo |
|------|-----------|---------|
| **Voice mode** | Interface por voz | Alto |
| **ULTRAPLAN** | Modo headless | Mdio |
| **Gacha system** | Recompensas aleatrias | Baixo |

---

## 4. RISCOS DE COPIAR (o que NO devemos copiar)

### 4.1 Telemetria Intrusiva
- **85 arquivos de telemetry**  viola privacidade.
- **Manter** nosso princpio de zero telemetria por padro.

### 4.2 Complexidade do Bridge
- **31 arquivos**  overkill para nosso caso.
- **Manter** isolamento via lobe local.

### 4.3 DRM (que morreu em 24h)
- **No encontrado**  provavelmente removido.
- **Ignorar** completamente.

---

## 5. PRXIMOS PASSOS CONCRETOS (T0)

### 5.1 Ticket NCDS010 (CC001C)
- **Ler os 61 arquivos com KAIROS** para extrair lgica de tick.
- **Ler README dos 11 plugins restantes.**
- **Analisar `src/constants/license.ts`** (subscription model).

### 5.2 Ticket NCDS011 (CC001D)
- **Implementar hookifylike** (NCTOOLFR022).
- **Criar diretrio `.claude/`** com exemplo de regra.

### 5.3 Ticket NCDS012 (CC001E)
- **Scaffold de plugin** baseado em `agentsdkdev`.
- **Comando `/newplugin`** para gerar NCTOOLFR*.

---

## 6. CONCLUSO

**O Claude Code vazado  uma mina de ouro de padres de extensibilidade.** No precisamos copiar a complexidade inteira, mas **devemos absorver a filosofia de hooks leves e plugins modulares**.

**Nosso diferencial (atomic locks, mentor mode) deve ser mantido e expandido** com a flexibilidade que eles criaram.

**Prxima ao imediata:** T0 revisar este handoff e priorizar os tickets de implementao.

---

**Status:** Anlise competitiva preliminar.  
**Confiana:** Mdia (baseada em grep e leitura de 2/13 READMEs).  
**Prximo ticket:** NCDS010 (CC001C) para anlise mais profunda.

## G. Mapeamento de Nomes CC  NeoCortex

| Nome Original (CC) | Nome NeoCortex | Arquivo Mapping |
|---|---|---|
| KAIROS | PulseDaemon / TickEngine | NCSVCFR010kairosservice.py |
| ralphwiggum | PersistentWorker | NCPROMPTDS003persistentworker.md |
| hookify / securityguidance | MentorHooks / GuardHooks | NCHKFR001hookregistry.py |
| Buddy | SessionMate | NCSVCFR009sessionbuddy.py |
| Bridge Mode | A2AGateway | NCSVCFR011a2agateway.py |
| ULTRAPLAN | BatchOrchestrator | futuro psMCP |
| plugindev / marketplace | NCTOOLFRTEMPLATE | NCSCRFR012newtool.py |
| .claude/ | .nc/ | NCCFGFR004projectloader.py |
| codereview plugin | ConfidenceReviewService | NCREVFR001confidencereview.py |