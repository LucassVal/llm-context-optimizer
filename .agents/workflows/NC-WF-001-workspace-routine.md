---
description: NeoCortex Workspace Routine Standards (Os 4 Ciclos) — v4.0 | 2026-04-18
version: "4.0"
hash: "NC-WF-001-v4.0-20260418"
governance_law: true
governance_links:
  lei_mestra:         ".agents/workflows/NC-WF-001-workspace-routine.md"
  ciclos:             "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CYC-FR-001-4-cycle-validation.md"
  ticket_lifecycle:   "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-002-ticket-lifecycle.yaml"
  ia_rules:           "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-003-ia-governance-rules.yaml"
  artifacts_registry: "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-004-fr-artifacts-registry.yaml"
  template_central:   "01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TPL-FR-001-template-central-index.yaml"
  handoff_template:   "DIR-DS-001-tickets/NC-DS-HANDOFF-TEMPLATE.yaml"
  governance_ecosystem: "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-005-governance-ecosystem.yaml"
  atomic_locks:       "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml"
  write_zones:        "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-FR-002-rules-policy.yaml"
  ssot_names:         "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md"
  boot_manifest:      "DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md"
  catalog:            "DIR-DOC-FR-001-docs-main/artifact_catalog.json"
  user_consciousness: "01_neocortex_framework/lobes/NC-LBE-USR-001-user-consciousness.mdc"
  user_profile:       "01_neocortex_framework/DIR-PRF-FR-001-profiles-main/users/lucas_valerio/NC-PRF-USR-001-profile.json"
  wal_service:        "01_neocortex_framework/neocortex/core/services/NC-SVC-FR-016-wal-service.py"
  wal_db:             "DIR-DS-003-wal/neocortex_wal.db"
  tag_normalizer:     "01_neocortex_framework/neocortex/core/services/NC-SVC-FR-018-tag-normalizer.py"
  crypto_hub:         "01_neocortex_framework/neocortex/core/services/NC-SVC-FR-017-crypto-hub.py"
  orchestration_tool: "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-023-orchestration.py"
  picoclaw_tool:      "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-036-picoclaw.py"
  litellm_gateway:      "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-043-litellm.py"
  litellm_startup:      "01_neocortex_framework/scripts/NC-SCR-FR-110-litellm-startup.ps1"
  litellm_lobe:         "02_memory_lobes/NC-LBE-FR-LITELLM-001.mdc"
  litellm_config:       "config.yaml"
lobes_ativos:
  user_consciousness: "01_neocortex_framework/lobes/NC-LBE-USR-001-user-consciousness.mdc"
  picoclaw:           "01_neocortex_framework/lobes/NC-LBE-INT-001-picoclaw-architecture.mdc"
  opencode:           "01_neocortex_framework/lobes/NC-LBE-INT-002-opencode-architecture.mdc"
  antigravity:        "01_neocortex_framework/lobes/NC-LBE-INT-003-antigravity-integration.mdc"
  mission_control:    "02_memory_lobes/NC-LBE-INT-004-mission-control.mdc"
  pixel_agents:       "02_memory_lobes/NC-LBE-INT-005-pixel-agents.mdc"
  worker_patterns:    "01_neocortex_framework/lobes/NC-LBE-DS-003-worker-patterns.mdc"
  quality_env:        "01_neocortex_framework/lobes/NC-LBE-FR-QUALITY-001-env-quality.mdc"
  quality_compaction: "01_neocortex_framework/lobes/NC-LBE-FR-QUALITY-002-context-compaction.mdc"
antigravity_config:   "DIR-DS-000-agent-config/antigravity_neocortex_config.json"
sprint_atual:
  fase: "PRÉ-MCP"
  # Estado real → ler NC-BOOT-FR-001-system-manifest.md (seções 6, 7, 8, 9)
  # Tickets → DIR-DS-001-tickets/
  # Handoffs → DIR-DS-002-audit-logs/
---

# Fluxo de Trabalho NeoCortex — Os 4 Ciclos
> **Fase atual:** SPRINT-ACELERADO — LiteLLM+PicoClaw+Ollama driving | sem MC/Pixel por ora  
> **Raiz:** `C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\`  
> **Shell:** PowerShell 7.x (todos os comandos abaixo são pwsh)  
> **T0 (orquestrador):** Antigravity — pensa e decide. OpenCode/DeepSeek executam. PicoClaw despacha.

---

## ⛔ REGRA DE OURO (antes de qualquer coisa)

```
Handoff sem ticket  = ERRO CRÍTICO  → criar ticket retrospectivo imediatamente.
Ticket sem handoff  = INCOMPLETO    → não iniciar nova tarefa antes de fechar.
Violar atomic_lock  = BLOQUEIO T0   → abortar imediatamente, notificar T0.
```

---

## 🗺️ MAPA DE GOVERNANÇA

> **NC-WF-001 é a lei mestra.** Todos os arquivos abaixo são referenciados por ela.  
> Qualquer IA (Antigravity, OpenCode, Claude, DeepSeek) obedece esta hierarquia.

```
NC-WF-001 (lei mestra — este arquivo)
│
├── CICLOS & PROTOCOLO
│   ├── NC-CYC-FR-001   → define os 4 ciclos (machine-readable)
│   └── NC-GOV-FR-002   → ciclo de vida do ticket (STAGE-05: handoff obrigatório)
│
├── REGRAS & SEGURANÇA
│   ├── NC-GOV-FR-003   → 20 regras de governança de IA
│   │   ├── R09 → Modo Mentor (instruções impositivas)     [STEP 0 / AGENT-203]
│   │   ├── R10 → Validação pré-ação                       [STEP 0 / Regression Check]
│   │   ├── R11 → Rollback em falha                        [STEP +1 / SAVE-003]
│   │   └── R21 → Zero suposições — verificar ambiente real
│   ├── NC-SEC-FR-001   → atomic locks (IMUTÁVEIS: server.py, sub_server.py, NC-NAM-FR-001, neocortex_config.yaml)
│   │   └── LockGuard / DENY-by-default                    [SEC-401 / PRE-2]
│   └── NC-CFG-FR-002   → write zones por role (PolicyLoader)  [PRE-1]
│
├── TEMPLATES (R22)
│   └── NC-TPL-FR-001   → índice da Template Central (catálogo por tipo)
│       └── Dir: 01_neocortex_framework/DIR-TMP-FR-001-templates-main/
│
├── SSOT & ARTEFATOS
│   ├── NC-NAM-FR-001   → naming convention NC-<TIPO>-<SIGLA>-<NUM> (enforcement SEC-402)
│   │   ├── Compact Encoding / Dedup (@$%)                 [GOV-006]
│   │   └── Vocabulário Ubíquo                             [NC-DOC-FR-001]
│   ├── NC-GOV-FR-004   → registro de artefatos FR (SSOT de scripts + Tool Manifest FR-021a)
│   │   ├── PulseScheduler / scripts de manutenção         [OPT-010]
│   │   ├── Logs estruturados JSON                         [OBS-001 — IN_PROGRESS]
│   │   └── TTL de Logs                                    [TTL-002 — PENDING]
│   └── NC-GOV-FR-005   → ecossistema de governança (visão macro + MetricsStore METR-106)
│
├── ESTADO DO SISTEMA
│   └── NC-BOOT-FR-001  → boot manifest (estado real: frentes, tickets críticos, fase)
│       ├── Observabilidade / MetricsStore                  [METR-106]
│       └── HUD / neocortex_hud.py                         [HUD-001]
│
└── LOBES DE REFERÊNCIA (ver seção abaixo)
    ├── NC-LBE-INT-001  → PicoClaw (arquitetura, :18790)
    ├── NC-LBE-INT-004  → Mission Control (dashboard, :3000)
    └── NC-LBE-INT-005  → Pixel Agents (observer, :8767)
```

### Componentes com cobertura implícita (tornada explícita aqui)

| Componente | Status | Cobertura | Arquivo |
|---|---|---|---|
| Fallback Chain LLM | ✅ LLM-006 | NC-LBE-INT-001 + NC-CFG-DS-001 | picoclaw config |
| PulseScheduler (heartbeat) | ✅ OPT-010 | NC-GOV-FR-004 (scripts manutenção) | artifact registry |
| Compact Encoding / Dedup | ✅ | NC-NAM-FR-001 + NC-DOC-FR-001 | naming + ubiq language |
| MetricsStore | ✅ METR-106 | NC-GOV-FR-005 + NC-BOOT-FR-001 | ecossistema + boot |
| HUD | ✅ HUD-001 | NC-LBE-INT-004 (Mission Control) | lobe mission control |
| Logs estruturados JSON | 🟡 OBS-001 | NC-GOV-FR-004 | PENDING ticket |
| Health Check /health | 🟡 AGENT-206 | CICLO 0 (verificação MCP) | ver abaixo |
| TTL de Logs | 🟡 TTL-002 | NC-GOV-FR-004 | PENDING ticket |
| Audit Trail WAL | 🟡 parcial | NC-GOV-FR-002 (handoff) | PENDING WAL |
| Fila SQLite | 🟡 migração | NC-GOV-FR-002 (STAGE-05) | IN_PROGRESS |
| SAVE-002 (Save Point) | ✅ | NC-CYC-FR-001 + NC-GOV-FR-003 | ciclos + regras |

---

## 🧠 LOBES DE REFERÊNCIA

> Antes de trabalhar com qualquer componente de integração, ler o lobe correspondente.

| Lobe | Componente | Porta | Path |
|---|---|---|---|
| NC-LBE-FR-LITELLM-001 | LiteLLM Gateway (proxy unificado :4000) | :4000 | `02_memory_lobes/NC-LBE-FR-LITELLM-001.mdc` |
| NC-LBE-USR-001 | User Consciousness (perfil cognitivo T0) | — | `01_neocortex_framework/lobes/NC-LBE-USR-001-user-consciousness.mdc` |
| NC-LBE-INT-001 | PicoClaw (gateway A2A, DeepSeek executor) | :18790 | `01_neocortex_framework/lobes/NC-LBE-INT-001-picoclaw-architecture.mdc` |
| NC-LBE-INT-002 | OpenCode (runtime agentes T1, DeepSeek) | :45132/:32879 | `01_neocortex_framework/lobes/NC-LBE-INT-002-opencode-architecture.mdc` |
| NC-LBE-INT-003 | Antigravity (T0 adapter, 38 tools MCP) | stdio/SSE | `01_neocortex_framework/lobes/NC-LBE-INT-003-antigravity-integration.mdc` |
| NC-LBE-INT-004 | Mission Control (dashboard, kanban, SSE) | :3000 | `02_memory_lobes/NC-LBE-INT-004-mission-control.mdc` |
| NC-LBE-INT-005 | Pixel Agents (observer pixel-art, JSONL) | :8767 | `02_memory_lobes/NC-LBE-INT-005-pixel-agents.mdc` |
| NC-LBE-DS-003 | Worker Patterns (B1–B6, claim protocol) | — | `01_neocortex_framework/lobes/NC-LBE-DS-003-worker-patterns.mdc` |
| NC-LBE-FR-QUALITY-001 | Env Quality (ambiente isolado, checks) | — | `01_neocortex_framework/lobes/NC-LBE-FR-QUALITY-001-env-quality.mdc` |
| NC-LBE-FR-QUALITY-002 | Context Compaction (dedup, compactação) | — | `01_neocortex_framework/lobes/NC-LBE-FR-QUALITY-002-context-compaction.mdc` |

---

## 🔌 CICLO 0 — VERIFICAÇÃO MCP (antes de iniciar sessão)
> Objetivo: (1) Carregar consciência do usuário. (2) Verificar se o stack MCP está rodando. Se não, iniciar na ordem correta.

### PASSO 0: Carregar User Consciousness (OBRIGATÓRIO — antes de qualquer ação)

```bash
# Ler o lobe de consciência do usuário antes de agir:
# Arquivo: 01_neocortex_framework/lobes/NC-LBE-USR-001-user-consciousness.mdc
# Leitura define: tom de resposta, formato, prioridades, projetos ativos, firewall emocional.
head -80 "01_neocortex_framework/lobes/NC-LBE-USR-001-user-consciousness.mdc"
```

**Checklist consciência:**
- [ ] Lobe NC-LBE-USR-001 lido
- [ ] Projetos ativos identificados (`current_sprint`, `blockers`)
- [ ] Formato de resposta calibrado (tabelas > parágrafos, pt-BR)
- [ ] Firewall emocional carregado (Joaquin / Antônio / Helena = CRITICAL)

```powershell
# 0. Verificar LiteLLM gateway :4000 (DEVE estar UP antes do MCP)
$portas = @(4000, 8766, 3000, 18790, 11434)
foreach ($p in $portas) {
    $conn = Test-NetConnection -ComputerName localhost -Port $p -WarningAction SilentlyContinue
    $status = if ($conn.TcpTestSucceeded) { "UP" } else { "DOWN" }
    Write-Host "$p`: $status $(switch($p){4000{'(LiteLLM)'}; 8766{'(MCP)'}; 3000{'(MC)'}; 18790{'(PicoClaw)'}; 11434{'(Ollama)'}})"
}

# Se LiteLLM DOWN — iniciar:
# .\01_neocortex_framework\scripts\NC-SCR-FR-110-litellm-startup.ps1 -Start
# OU registrar no Task Scheduler (run as Admin):
# .\01_neocortex_framework\scripts\NC-SCR-FR-110-litellm-startup.ps1 -Register

# LiteLLM health via MCP (após MCP iniciar):
# neocortex_litellm.gateway.health

# 1. Verificar portas ativas (MCP health wrapper :8766, MC :3000, PicoClaw :18790)

# 2. Health check MCP via wrapper (NC-SCR-FR-098, porta 8766)
#    Se 8766 UP → JSON com status/uptime
#    Se 8766 DOWN → iniciar wrapper primeiro (PASSO 0.5)
if ((Test-NetConnection -ComputerName localhost -Port 8766 -WA 0).TcpTestSucceeded) {
    try { (Invoke-WebRequest http://localhost:8766/health -UseBasicParsing).Content } catch {}
} else {
    Write-Host "Health wrapper DOWN — executar PASSO 0.5 para iniciar"
}

# 3. Se DOWN — iniciar na ordem:
# PASSO 1: MCP Core
#   cd 01_neocortex_framework
#   python -m neocortex.mcp.server   # stdio (Antigravity conecta aqui)

# PASSO 0.5: Health Wrapper (NC-SCR-FR-098) — iniciar ANTES do MCP se não estiver UP
#   Start-Process python -ArgumentList "01_neocortex_framework\scripts\NC-SCR-FR-098-health-wrapper.py","--port","8766" -NoNewWindow
#   # Aguardar ~2s e verificar: (Invoke-WebRequest http://localhost:8766/health).Content
#   # GET /health → JSON {status, uptime, pid, tools_count, timestamp}
#   # GET /ready  → 200 (MCP OK) | 503 (MCP não responde)

# PASSO 2: Mission Control
#   cd DIR-RES-CC-001-claude-leak-workzone\external-refs\mission-control
#   pnpm dev   # → :3000

# PASSO 3: Registrar NeoCortex no Mission Control
#   python 01_neocortex_framework\neocortex\core\adapters\NC-ADP-FR-001-mission-control.py

# PASSO 4: PicoClaw (DeepSeek API executor)
#   01_neocortex_framework\scripts\NC-SCR-PIC-001-picoclaw-watchdog.bat
#   # Configs: DIR-DS-000-agent-config\NC-CFG-PIC-001-picoclaw-config.json

# PASSO 5: Pixel Agents — instalar extensão VS Code
#   code --install-extension pablodelucca.pixel-agents
#   # Observer passivo em :8767
```

**Checklist Ciclo 0:**
- [ ] LiteLLM Gateway (:4000) UP — `NC-SCR-FR-110-litellm-startup.ps1 -Start`
- [ ] MCP Core (NeoCortex server.py) — stdio conectado ao Antigravity
- [ ] **Health Wrapper (:8766) UP** — `GET /health` retorna JSON válido ← NOVO (AGENT-206 ✅)
- [ ] **`/ready` = 200** — MCP stdio respondendo confirmado
- [ ] Mission Control (:3000) — dashboard acessível
- [ ] PicoClaw (:18790) — gateway A2A ativo, DeepSeek API configurada
- [ ] Pixel Agents (:8767) — extensão VS Code instalada (observer)
- [ ] NC-ADP-FR-001 — NeoCortex registrado no Mission Control

---

## 🔄 CICLO 1 — INÍCIO DE SESSÃO
> Objetivo: Estabelecer baseline, verificar conformidade, identificar bloqueantes.

```powershell
# 1. Ler boot manifesto (primeiros 80 linhas)
Get-Content "DIR-BOOT-FR-001-bootup-main\NC-BOOT-FR-001-system-manifest.md" -Head 80

# 2. Verificar idade do catálogo semântico
#    NOTA: catálogo em DIR-DOC-FR-001-docs-main\ (raiz), não em 01_neocortex_framework\
python -c "
import json, datetime
try:
    with open('DIR-DOC-FR-001-docs-main/artifact_catalog.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    gen = datetime.datetime.fromisoformat(data['metadata']['generated'])
    age = (datetime.datetime.now() - gen).total_seconds() / 3600
    py_count = len(data.get('python_files', []))
    yaml_count = len(data.get('yaml_files', []))
    print(f'Catalogo gerado ha {age:.1f}h | py={py_count} yaml={yaml_count}')
    print('AVISO: >24h — regenerar no Ciclo 3' if age > 24 else 'OK: catalogo recente')
except Exception as e:
    print(f'ERRO: {e}')
"

# 3. ⛔ BLOQUEANTE — Auditar tickets sem handoff correspondente
python -c "
import glob, re
tickets  = {re.search(r'(NC-DS-\d+)', f).group(1) for f in glob.glob('DIR-DS-001-tickets/*.yaml')  if re.search(r'NC-DS-\d+', f)}
handoffs = {re.search(r'(NC-DS-\d+)', f).group(1) for f in glob.glob('DIR-DS-002-audit-logs/*.yaml') if re.search(r'NC-DS-\d+', f)}
orphan_t = tickets - handoffs
orphan_h = handoffs - tickets
print(f'Tickets: {len(tickets)} | Handoffs: {len(handoffs)}')
if orphan_t: print(f'ERRO: {len(orphan_t)} tickets SEM handoff: {sorted(orphan_t)}')
if orphan_h: print(f'ERRO: {len(orphan_h)} handoffs SEM ticket formal: {sorted(orphan_h)}')
if not orphan_t and not orphan_h: print('OK: todos os tickets tem handoff correspondente')
"

# 4. Validar YAMLs de governança (dupla mordaça)
python "01_neocortex_framework\scripts\NC-SCR-FR-009-sanitize-all-yamls.py" --check-only

# 5. Verificar tickets críticos (seção 9 do bootup)
Select-String -Path "DIR-BOOT-FR-001-bootup-main\NC-BOOT-FR-001-system-manifest.md" -Pattern "## 9\."
```

**Checklist Ciclo 1:**
- [ ] Catálogo < 24h (senão: Ciclo 3 primeiro)
- [ ] Bootup lido — frentes ativas e fase identificadas
- [ ] YAMLs de governança válidos (hash)
- [ ] ⛔ BLOQUEANTE: 0 tickets ativos sem handoff
- [ ] ⛔ BLOQUEANTE: 0 handoffs sem ticket formal → criar retrospectivo se houver
- [ ] Nenhum ticket crítico bloqueante (seção 9 do bootup)

### 📡 ACESSO AOS COMPONENTES NEOcORTEX (Orquestrador Unitário)

> **IMPORTANTE:** O NeoCortex opera como orquestrador unitário gerenciando 16 portas (8 serviços + 8 A2A). Acesse cada componente conforme abaixo:

| Componente | Porta | URL / Comando | Descrição |
|------------|-------|---------------|-----------|
| **MCP Server (core)** | `8765` | `ws://localhost:8765` | Servidor WebSocket/SSE principal. Verificar: `netstat -an | findstr 8765` |
| **Health wrapper** | `8766` | `http://localhost:8766/health` | Endpoint de saúde. Testar: `curl http://localhost:8766/health` |
| **Pixel Agents HTTP** | `8767` | `http://localhost:8767` | Servidor de hooks para extensão VS Code (recebe eventos Claude Code) |
| **A2A Gateway** | `8768` | `ws://localhost:8768` | Comunicação entre agentes (Agent-to-Agent) |
| **Courier service** | `8769` | `http://localhost:8769` | Entrega de mensagens entre componentes |
| **Engineer service** | `8770` | `http://localhost:8770` | Execução de tasks de engenharia |
| **FastAPI Web** | `8771` | `http://localhost:8771` | Interface administrativa web |
| **Webhook receiver** | `8772` | `http://localhost:8772` | Recebe webhooks externos |
| **A2A Channel 1** | `8773` | `ws://localhost:8773` | Canal A2A reservado 1 |
| **A2A Channel 2-8** | `8774-8780` | `ws://localhost:8774` etc. | Canais A2A adicionais |
| **Mission Control** | `3000` | `http://localhost:3000` | Dashboard React com kanban e SSE |
| **PicoClaw gateway** | `18790` | `http://localhost:18790` | Gateway A2A para despacho de tasks |
| **OpenCode agentes** | `59520` `44624` `32763` | `http://localhost:59520` etc. | Runtime dos agentes T1 (DeepSeek executor) |

**Procedimentos de verificação (Ciclo 0 obrigatório):**
1. **MCP Server**: `curl http://localhost:8766/ready` deve retornar 200 (MCP stdio respondendo)
2. **Health wrapper**: `curl http://localhost:8766/health` retorna JSON com status
3. **Mission Control**: Acessar `http://localhost:3000` no navegador
4. **Pixel Agents**: Verificar extensão VS Code instalada e configurada para porta 8767
5. **PicoClaw**: `netstat -an | findstr 18790` para gateway ativo

**Conflitos resolvidos:** Pixel Agents movido da porta 8765 para 8767 para liberar MCP Server.

---

---

## 🔄 CICLO 2 — DURANTE A SESSÃO
> Objetivo: Executar tickets com validação contínua, gerar handoff ao concluir cada um.

### ⛔ PROTOCOLO OBRIGATÓRIO PARA AGENTES T1 (R21 + R22 + R23)

> **Este protocolo é lei.** Qualquer agente que receber um ticket DEVE seguir estas etapas ANTES de escrever uma linha de código.

**STEP 0 — Ler antes de agir (obrigatório):**

| Recurso | Por quê ler |
|---------|-------------|
| `DIR-DS-001-tickets/NC-DS-HANDOFF-TEMPLATE.yaml` | Template oficial do handoff que VOCÊ deve gerar ao concluir |
| `01_neocortex_framework/DIR-TMP-FR-001-templates-main/` | Central de templates — use NC-TPL-FR-001-template-central-index.yaml |
| `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-003-ia-governance-rules.yaml` | 23 regras de governança — obrigatório seguir |
| `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml` | Arquivos que NUNCA podem ser tocados |

**REGRA DA DÚVIDA (R21 — Zero Suposições):**
```
EM CASO DE QUALQUER DÚVIDA → PARAR IMEDIATAMENTE e retornar ao T0.
NÃO assumir. NÃO adivinhar. NÃO improvisar.

Retornar com:
  (1) O que foi feito até agora
  (2) Qual é a dúvida exata
  (3) Quais são as opções que você vê

T0 decide. Você continua apenas após confirmação.
```

Exemplos de quando parar:
- Arquivo mencionado no ticket não encontrado
- API/estrutura do serviço é diferente do descrito
- A mudança necessária toca um arquivo @LOCKS
- Dois caminhos possíveis sem critério claro de escolha
- Script/template referenciado não existe

**HANDOFF OBRIGATÓRIO (R23) — ao concluir:**
```
Destino: DIR-DS-002-audit-logs/NC-DS-{TICKET_ID}-handoff-{YYYYMMDDTHHMMSS}.yaml
Template: DIR-DS-001-tickets/NC-DS-HANDOFF-TEMPLATE.yaml
Status válidos: APPROVED | PARTIALLY_COMPLETED | FAILED | ESCALATED
```
> Falhou ou ficou bloqueado? Gerar handoff com `status: FAILED` ou `ESCALATED`.
> NUNCA silenciar o erro. NUNCA encerrar sem handoff.

---

### Protocolo por ticket

**Antes de editar — consultar catálogo:**
```powershell
python -c "
import json
with open('DIR-DOC-FR-001-docs-main/artifact_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)
search = 'vector_engine.py'  # substituir pelo arquivo alvo
for item in catalog.get('python_files', []) + catalog.get('yaml_files', []):
    if search in item.get('file_path', ''):
        print(f'{item[\"file_path\"]}: {item.get(\"purpose\",\"\")[:120]}')
        break
"
```

**Após concluir o ticket — gerar handoff obrigatório:**
```yaml
# Salvar em: DIR-DS-002-audit-logs/NC-DS-XXX-handoff-YYYYMMDDTHHMMSS.yaml
ticket_id: "NC-DS-XXX"
status: "APPROVED"          # APPROVED | PARTIALLY_COMPLETED | FAILED | CANCELLED
timestamp: "2026-04-15T00:00:00-03:00"
agent: "T0-Antigravity"
summary: |
  Resumo do trabalho realizado...
files_modified: []
files_created: []
checklist_r20:
  naming_convention: true
  no_print_statements: true
  ssot_updated: true
  no_locked_files_modified: true
  handoff_yaml_complete: true
```

**Regras obrigatórias:**
- ✅ **ANTES de despachar agente T1** → criar dispatch YAML (R24) usando [NC-TPL-FR-002](01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TPL-FR-002-agent-dispatch.yaml)
- ✅ Destino do dispatch: `DIR-DS-001-tickets/NC-DS-AGT-{ID}-dispatch-{tickets}.yaml`
- ✅ Validar dispatch YAML com `yaml.safe_load` antes de enviar ao agente
- ✅ Atualizar SSOT (`NC-NAM-FR-001`) se criar/renomear artefato
- ✅ Respeitar `write_zones` em `NC-CFG-FR-002-rules-policy.yaml`
- ✅ NUNCA violar `NC-SEC-FR-001-atomic-locks.yaml`
- ✅ Gerar handoff para **cada** ticket concluído — sem exceção
- ✅ Ticket sem ticket formal correspondente = criar ticket retrospectivo

---

### ⚠️ PROTOCOLO T0 — AUDITORIA DE HANDOFF RECEBIDO (NC-DS-116)

> **LEI:** `%DONE` no @ROADMAP é **PROIBIDO** sem `t0_review` completamente preenchido.
> Origem: falha 2026-04-16 — tickets 103/104 marcados sem validação real.

**A cada handoff recebido de agente T1, T0 DEVE executar na ordem:**

| # | Ação | Comando / Verificação |
|---|------|-----------------------|
| 1 | Ler handoff YAML | Verificar `status`, `locks_violated: []`, `files_created`, `files_modified` |
| 2 | Para cada `.py` no diff | `py -m py_compile <arquivo>` → deve retornar OK |
| 3 | Ruff em cada `.py` | `py -m ruff check <arquivo>` → deve retornar `All checks passed!` |
| 4 | Zero print() | `grep -n "print(" <arquivo>` → deve retornar vazio |
| 5 | Se `files_created` não vazio | Verificar se cada artefato novo está em NC-NAM-FR-001. Se não → criar ticket SSOT |
| 6 | Preencher `t0_review` | `compile_ok`, `naming_ok`, `ssot_updated`, `locks_clean`, `roadmap_done` — todos non-null |
| 7 | Marcar `%DONE` no @ROADMAP | **Somente após os 6 passos acima concluídos** |

**Se qualquer check falhar:**
```
1. NÃO marcar %DONE
2. Alterar status do handoff para REJECTED
3. Preencher rejection.reason com o erro exato
4. Criar novo ticket de correção (rejection.next_ticket)
5. Notificar agente com o ticket de correção
```

**Handoff com `files_modified: []` e `files_created: []` (diff vazio):**
```
Válido APENAS se o agente documentou explicitamente por que não houve mudança.
T0 deve ler o arquivo alvo e confirmar que os critérios do ticket já estavam satisfeitos.
Marcar t0_review.compile_ok: true somente após confirmar o arquivo.
```

---

## 🔄 CICLO 3 — FIM DE SESSÃO
> Objetivo: Consolidar contexto, atualizar catálogo e bootup.
> ⚠️ WAL: após NC-DS-089, os passos 1-3 logam automaticamente via NC-SVC-FR-016.

```powershell
# Descobrir python disponível (Windows — py.exe launcher ou venv)
$py = if (Test-Path "/c/Windows/py.exe") { "/c/Windows/py.exe" } `
      elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" } `
      else { "python3" }

# 1. Atualizar catálogo semântico (se >24h ou mudanças significativas)
#    Saída: DIR-DOC-FR-001-docs-main/artifact_catalog.json (raiz)
& $py "01_neocortex_framework/scripts/NC-SCR-FR-064-artifact-catalog.py"

# 2. Sincronizar bootup com handoffs recentes
& $py "01_neocortex_framework/scripts/NC-SCR-FR-066-bootup-sync.py"

# 3. Sanitizar YAMLs de rotina
& $py "01_neocortex_framework/scripts/NC-SCR-FR-009-sanitize-all-yamls.py"

# 4. Pruning WAL (entradas >30 dias) — TTL-002
& $py "01_neocortex_framework/neocortex/core/services/NC-SVC-FR-016-wal-service.py" prune 30

# 5. Verificar baseline tickets/handoffs
& $py -c @"
import glob, re
t = {re.search(r'(NC-DS-\d+)',f).group(1) for f in glob.glob('DIR-DS-001-tickets/*.yaml') if re.search(r'NC-DS-\d+',f)}
h = {re.search(r'(NC-DS-\d+)',f).group(1) for f in glob.glob('DIR-DS-002-audit-logs/*.yaml') if re.search(r'NC-DS-\d+',f)}
print(f'Tickets:{len(t)} Handoffs:{len(h)} Orfaos:{sorted(t-h)}')
"@
```

**Checklist Ciclo 3:**
- [ ] Catálogo atualizado (timestamp recente, python_files > 0, yaml_files > 0)
- [ ] Bootup sincronizado com frentes ativas reais
- [ ] YAMLs sanitizados (0 issues críticas)
- [ ] WAL pruning executado (sem erros)
- [ ] Baseline 0 órfãos (tickets sem handoff = apenas tickets OPEN ativos)
- [ ] Nenhum `.db-wal`/`.db-shm`/`__pycache__` commitado
- [ ] **[AUTO-MEMORY]** `neocortex_session(action="session.summarize")` executado
- [ ] **[AUTO-MEMORY]** `neocortex_memory_auto(action="catalog.now")` → atualiza memory/hot-context.md

---

## 🔄 CICLO 4 — LIMPEZA SEMANAL (sexta-feira ou a cada 5–7 dias)
> Objetivo: Manter baseline limpa, auditar governança, arquivar tickets antigos.

```powershell
# 1. Auditoria completa de governança (20 regras) — meta: compliance >80%
python "01_neocortex_framework\scripts\NC-SCR-FR-080-governance-auditor.py"

# 2. Verificar dupla mordaça em YAMLs de governança (NC-SEC-FR-001 LockGuard)
python -c "
import yaml, os
gov_yamls = [
    'NC-SEC-FR-001-atomic-locks.yaml',
    'NC-CFG-FR-002-rules-policy.yaml',
    'NC-GOV-FR-002-ticket-lifecycle.yaml',
    'NC-GOV-FR-003-ia-governance-rules.yaml',
]
base = '01_neocortex_framework/DIR-DOC-FR-001-docs-main'
for yf in gov_yamls:
    path = f'{base}/{yf}'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        h = data.get('meta', {}).get('hash', 'MISSING')
        md_ok = 'OK' if os.path.exists(path.replace('.yaml','.md')) else 'FALTANDO'
        print(f'{yf}: hash={h} | md={md_ok}')
    else:
        print(f'MISS: {path}')
"

# 3. Arquivar handoffs antigos (>7 dias) — NC-GOV-FR-004 (TTL-002 PENDING)
New-Item -ItemType Directory -Force -Path "DIR-ARC-FR-001-archive-main" | Out-Null
Get-ChildItem "DIR-DS-002-audit-logs\" -Filter "*.yaml" |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |
  Move-Item -Destination "DIR-ARC-FR-001-archive-main\"

# 4. Mover tickets órfãos >30 dias para arquivo
New-Item -ItemType Directory -Force -Path "DIR-DS-004-archived-tickets" | Out-Null
Get-ChildItem "DIR-DS-001-tickets\" -Filter "*.yaml" |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) -and $_.Name -notmatch "TEMPLATE" } |
  Move-Item -Destination "DIR-DS-004-archived-tickets\"

# 5. Validar conformidade de nomenclatura NC-  (enforcement SEC-402)
python -c "
import os, re
pattern = r'^NC-[A-Z]+-[A-Z]+-[0-9]{3}-.+\..+'
non_conform = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['.git','__pycache__','.venv','node_modules']]
    for file in files:
        if file.endswith(('.py','.md','.yaml','.json')) and not re.match(pattern, file):
            non_conform.append(os.path.join(root, file))
total = sum(len(f) for _,_,f in os.walk('.'))
print(f'Nao conformes: {len(non_conform)} arquivos')
for p in non_conform[:10]:
    print(f'  - {p}')
"

# 6. Atualizar lobes se SSOT alterado (NC-SCR-FR-001 → populate lobes)
python "01_neocortex_framework\scripts\NC-SCR-FR-001-populate-lobes-ssot.py"
```

**Checklist Ciclo 4:**
- [ ] Auditoria de governança (NC-SCR-FR-080) executada — compliance >80%
- [ ] Hash de YAMLs de governança válidos (dupla mordaça / LockGuard)
- [ ] Handoffs antigos >7 dias arquivados em `DIR-ARC-FR-001-archive-main/`
- [ ] Tickets órfãos >30 dias movidos para `DIR-DS-004-archived-tickets/`
- [ ] Conformidade NC-: meta 100%
- [ ] Lobes atualizados (`NC-SCR-FR-001-populate-lobes-ssot.py`)
- [ ] Relatório em `DIR-DS-002-audit-logs/`

---

## 🎯 COMANDOS RÁPIDOS

| Ação | Comando |
|------|---------|
| LiteLLM health | `Invoke-RestMethod http://localhost:4000/health -Headers @{Authorization='Bearer sk-my-master-key-123'}` |
| LiteLLM iniciar | `.\01_neocortex_framework\scripts\NC-SCR-FR-110-litellm-startup.ps1 -Start` |
| LiteLLM registrar | `.\01_neocortex_framework\scripts\NC-SCR-FR-110-litellm-startup.ps1 -Register` (Admin) |
| LiteLLM via MCP | `neocortex_litellm.gateway.health` / `neocortex_litellm.route.call` |
| Workers Qwen | `neocortex_litellm.workers.spawn` (n_workers=3) |
| Ver bootup | `Get-Content "DIR-BOOT-FR-001-bootup-main\NC-BOOT-FR-001-system-manifest.md" -Head 100` |
| Ver SSOT | `Get-Content "01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-NAM-FR-001-naming-convention.md" -Head 50` |
| Listar tickets | `Get-ChildItem "DIR-DS-001-tickets\" -Filter "*.yaml" \| Select Name, LastWriteTime` |
| Listar handoffs | `Get-ChildItem "DIR-DS-002-audit-logs\" -Filter "*.yaml" \| Select Name, LastWriteTime` |
| Atualizar catálogo | `python "01_neocortex_framework\scripts\NC-SCR-FR-064-artifact-catalog.py"` |
| Sincronizar bootup | `python "01_neocortex_framework\scripts\NC-SCR-FR-066-bootup-sync.py"` |
| Auditoria governança | `python "01_neocortex_framework\scripts\NC-SCR-FR-080-governance-auditor.py"` |
| Validar YAMLs | `python "01_neocortex_framework\scripts\NC-SCR-FR-009-sanitize-all-yamls.py"` |
| Orquestrar agentes | `powershell -File "01_neocortex_framework\scripts\NC-SCR-FR-064-orchestration-agent-fixes.ps1" -DryRun` |
| Rodar testes | `Set-Location "01_neocortex_framework"; pytest tests/ -v` |
| Lint | `Set-Location "01_neocortex_framework"; python -m ruff check .` |
| Status portas MCP | `@(8766,3000,18790) \| % { "$_`: $(if((Test-NetConnection localhost -Port $_ -WA 0).TcpTestSucceeded){'UP'}else{'DOWN'})" }` |
| MCP alive check | `(Invoke-WebRequest http://localhost:8766/health -UseBasicParsing).Content` |
| MCP ready check | `(Invoke-WebRequest http://localhost:8766/ready -UseBasicParsing).StatusCode` |
| Iniciar health wrapper | `Start-Process python -ArgumentList "01_neocortex_framework\scripts\NC-SCR-FR-098-health-wrapper.py","--port","8766" -NoNewWindow` |
| Registrar no MC | `python "01_neocortex_framework\neocortex\core\adapters\NC-ADP-FR-001-mission-control.py"` |

---

## 📚 DOCUMENTAÇÃO DE REFERÊNCIA COMPLETA

| Arquivo | Propósito | Tier |
|---------|-----------|------|
| `NC-WF-001-workspace-routine.md` | **Este arquivo** — lei mestra dos 4 ciclos | LEI |
| `NC-BOOT-FR-001-system-manifest.md` | Boot universal — ler PRIMEIRO em toda sessão | BOOT |
| `NC-CYC-FR-001-4-cycle-validation.md` | Protocolo de 4 ciclos machine-readable | CICLOS |
| `NC-GOV-FR-002-ticket-lifecycle.yaml` | Ciclo de vida do ticket (STAGE-05: handoff) | GOV |
| `NC-GOV-FR-003-ia-governance-rules.yaml` | 20 regras de governança de IA + regras MCP | GOV |
| `NC-GOV-FR-004-fr-artifacts-registry.yaml` | Registro de artefatos FR — SSOT de scripts | GOV |
| `NC-GOV-FR-005-governance-ecosystem.yaml` | Ecossistema de governança — visão macro | GOV |
| `NC-SEC-FR-001-atomic-locks.yaml` | Arquivos imutáveis — NUNCA modificar sem T0 | SEC |
| `NC-SEC-FR-002-entry-lock-protocol.md` | Protocolo de entrada em zonas de lock | SEC |
| `NC-CFG-FR-002-rules-policy.yaml` | Write zones por role (PolicyLoader PRE-1) | CFG |
| `NC-NAM-FR-001-naming-convention.md` | SSOT — mapa de artefatos + compact encoding | SSOT |
| `artifact_catalog.json` | Catálogo semântico (`DIR-DOC-FR-001-docs-main/`) | SSOT |
| `NC-LBE-INT-001-picoclaw-architecture.mdc` | PicoClaw — gateway A2A :18790 | LOBE |
| `NC-LBE-INT-002-opencode-architecture.mdc` | OpenCode — runtime agentes T1 :45132 | LOBE |
| `NC-LBE-INT-003-antigravity-integration.mdc` | Antigravity — T0 adapter, 38 tools MCP | LOBE |
| `NC-LBE-INT-004-mission-control.mdc` | Mission Control — dashboard :3000 | LOBE |
| `NC-LBE-INT-005-pixel-agents.mdc` | Pixel Agents — observer :8767 | LOBE |
| `NC-LBE-DS-003-worker-patterns.mdc` | Worker Patterns — B1–B6, claim protocol | LOBE |
| `NC-DOC-FR-001-ubiquitous-language-dictionary.md` | Dicionário Ubíquo @/$/% — SSOT símbolos | SSOT |
| `NC-ADP-FR-001-mission-control.py` | Adapter NeoCortex → Mission Control | ADAPTER |
| `NC-TOOL-FR-023-orchestration.py` | Tool MCP orquestração + task.dispatch ORCH-301 | TOOL |
| `NC-TOOL-FR-036-picoclaw.py` | Tool MCP PicoClaw + task.status ORCH-302 | TOOL |
| `NC-CFG-PIC-001-picoclaw-config.json` | Config PicoClaw (DeepSeek API, porta 18790) | CFG |
| `antigravity_neocortex_config.json` | Config Antigravity → NeoCortex MCP (DIR-DS-000-agent-config/) | CFG |

---

## ⚠️ LEMBRETES CRÍTICOS

1. **SEMPRE** ler boot manifest no início da sessão (CICLO 0 → CICLO 1)
2. **SEMPRE** consultar catálogo antes de editar artefato desconhecido
3. **NUNCA** modificar arquivos em `atomic_locks` sem autorização T0
4. **SEMPRE** gerar handoff para ticket concluído — sem exceção
5. **NUNCA** deletar — arquivar em `DIR-ARC-FR-001-archive-main/`
6. **SEMPRE** seguir naming convention `NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext`
7. **Handoff sem ticket** → criar ticket retrospectivo (`status: RETROSPECTIVE`) imediatamente
8. **Ticket sem handoff >30 dias** → mover para `DIR-DS-004-archived-tickets/`
9. **Shell correto**: PowerShell 7.x — usar `Get-Content`, `Get-ChildItem`, `Select-String`
10. **T0 orquestra. OpenCode/DeepSeek executam. PicoClaw despacha. Nunca inverter. (R17)**
11. **SEMPRE** commitar alterações após aprovação de handoff YAML ou conclusão de to-do — manter histórico versionado.

---

## 🆘 SOLUÇÃO DE PROBLEMAS

| Sintoma | Solução |
|---------|---------|
| Catálogo vazio (0 artefatos) | Verificar chaves: usar `python_files` e `yaml_files`, não `artifacts` |
| Catálogo path errado | Path correto: `DIR-DOC-FR-001-docs-main\artifact_catalog.json` (raiz do projeto) |
| Encoding Unicode | `python -c "import sys; sys.stdout.reconfigure(encoding='utf-8')"` |
| Handoff sem ticket | Criar ticket retrospectivo em `DIR-DS-001-tickets/` com `status: RETROSPECTIVE` |
| Ticket sem handoff | Gerar handoff `CANCELLED` ou `APPROVED` retroativo antes de prosseguir |
| Ticket OPEN com handoff APPROVED | Fechar ticket: atualizar `status: "OPEN"` → `"DONE"` |
| Ticket órfão >30 dias | Mover para `DIR-DS-004-archived-tickets/` via Ciclo 4 |
| Regex seção 9 bootup falha | Verificar separadores `---` — usar `(?:---\n)+\n` (NC-DS-072 corrigiu) |
| Violação de lock | Verificar `NC-SEC-FR-001-atomic-locks.yaml` e **abortar imediatamente** |
| Mission Control DOWN | `pnpm dev` em `DIR-RES-CC-001-claude-leak-workzone\external-refs\mission-control\` |
| PicoClaw DOWN | `NC-SCR-PIC-001-picoclaw-watchdog.bat` + verificar `NC-CFG-PIC-001-picoclaw-config.json` |
| MCP server DOWN | `python -m neocortex.mcp.server` em `01_neocortex_framework\` |

---

**Hash**: `NC-WF-001-v4.0-20260418`  
**Atualizado**: 2026-04-18  
**Versão**: 4.0  
**Fase**: SPRINT-ACELERADO (sem MC/Pixel)  
_"Rotinas inertes matam produtividade. Handoffs são evidência. Bootup é verdade. Governança é lei."_

