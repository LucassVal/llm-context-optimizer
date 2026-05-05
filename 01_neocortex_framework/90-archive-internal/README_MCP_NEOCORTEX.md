#  NeoCortex MCP Server - Host para OpenCode + Antigravity

> **Servidor MCP pronto para produo** - 22 ferramentas, 73+ aes, mtricas automticas, WebSocket/stdio

---

##  **Status: PRONTO & FUNCIONAL**

 **MCP Server atualizado** com suporte a WebSocket + stdio  
 **22 ferramentas** registradas com mtricas automticas  
 **DuckDB MetricsStore** + relatrios em Markdown/CSV/JSON  
 **Agent Isolation** (courier/engineer) com mentor mode (parcial)  
 **Scripts de startup** para Windows (PowerShell + Batch)  
 **Configurao para Antigravity** includa

---

##  **Como Iniciar (30 segundos)**

### **Opo 1: PowerShell (Recomendado)**
```powershell
cd "C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42"
.\start_neocortex_mcp.ps1
```

### **Opo 2: Batch File**
```cmd
cd "C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42"
start_neocortex_mcp.bat
```

### **Opo 3: Manual (Python)**
```bash
cd neocortex_framework
python -m neocortex.mcp.server --transport websocket --host localhost --port 8765 --log-level INFO
```

**Sada esperada:**
```
[INFO] Iniciando NeoCortex MCP Server v4.2-cortex (Host Mode)
[INFO] Transporte: websocket
[INFO] Endereo: ws://localhost:8765
[INFO] Heartbeat: a cada 30 segundos
 Servidor WebSocket pronto em ws://localhost:8765
 Aguardando conexes do OpenCode/Antigravity...
```

---

##  **Conectar no Antigravity**

### **Configurao Rpida:**
1. **Copie** `antigravity_neocortex_config.json` para:
   - `%APPDATA%\antigravity\mcp-servers.json` (Windows)
   - `~/.config/antigravity/mcp-servers.json` (Mac/Linux)

2. **OU adicione ao seu arquivo existente**

3. **No Antigravity**, use:
   - **WebSocket**: `neocortex-websocket` (ws://localhost:8765)
   - **Stdio**: `neocortex` (inicia automaticamente)

### **Verifique a conexo:**
- Abra o Antigravity
- Verifique se as ferramentas `neocortex_*` aparecem
- Teste: `neocortex_cortex` com ao `get_full`

---

##  **Ferramentas Disponveis (22)**

| Categoria | Ferramenta | Aes Principais | Status |
|-----------|------------|------------------|--------|
| **Core** | `neocortex_cortex` | get_full, get_section, get_aliases |  |
| **State** | `neocortex_ledger` | read, write, update_section |  |
| **Reporting** | `neocortex_report` | generate_daily_summary, cost_report, agent_report |  |
| **Orchestration** | `neocortex_subserver` | spawn, stop, list, send_task |  |
| **Execution** | `neocortex_task` | execute (com mentor mode) |  |
| **Checkpoints** | `neocortex_checkpoint` | get_current, create, restore |  |
| **Configuration** | `neocortex_config` | get, set, validate |  |
| **Lobes** | `neocortex_lobes` | list, get, create |  |
| **Search** | `neocortex_search` | semantic, keyword |  |
| **Agents** | `neocortex_agent` | execute (backend override) |  |
| **Pulse** | `neocortex_pulse` | status, force_consolidation |  |
| **Metrics** | (automtico) | DuckDB + relatrios |  |

**Total: 73+ aes operacionais**

---

##  **Mtricas & Relatrios Automticos**

O servidor inclui **MetricsStore com DuckDB** que registra:

1. **Token Economy**: Uso dirio de tokens por modelo/agente
2. **Cost Tracking**: Custos reais vs estimados, ROI
3. **Agent Activity**: Spawns, tarefas, falhas
4. **Pulse Health**: Consolidao, pruning, checkpoints

**Relatrios disponveis via `neocortex_report`:**
- `generate_daily_summary`: Resumo dirio (Markdown)
- `generate_cost_report`: Anlise de custos (CSV/JSON)
- `generate_agent_report`: Atividade dos agentes

---

##  **Agent Isolation (Phase 2 - Parcial)**

**Ambientes criados:**
- `lobes/courier/`: Agente 1.5B (Qwen) - leitura apenas
- `lobes/engineer/`: Agente 3B (Qwen) - leitura/escrita

**Configurao por role:**
- `neocortex_config.yaml` com `allowed_tools` especficos
- Sub-server com filtragem automtica de ferramentas
- `--role` parameter para identificao

**Pendente:** `mentor_step_0()` (AGENT-203)

---

##  **Comandos Avanados**

### **Modos de Transporte:**
```bash
# WebSocket (host mode)
python -m neocortex.mcp.server --transport websocket --port 9999

# Stdio (IDE integration)
python -m neocortex.mcp.server --transport stdio

# Debug mode
python -m neocortex.mcp.server --transport websocket --log-level DEBUG
```

### **Parmetros:**
- `--transport`: `websocket` (padro) ou `stdio`
- `--host`: Hostname (padro: localhost)
- `--port`: Porta (padro: 8765)
- `--log-level`: DEBUG, INFO, WARNING, ERROR
- `--heartbeat-interval`: Segundos entre heartbeats

---

##  **Soluo de Problemas**

### **1. "FastMCP no encontrado"**
```bash
pip install mcp
```

### **2. "Porta j em uso"**
```bash
# Use porta diferente
python -m neocortex.mcp.server --port 9999

# Ou encontre processo usando a porta
netstat -ano | findstr :8765
```

### **3. "Python no encontrado"**
- Instale Python 3.8+
- Adicione ao PATH durante instalao
- Reinicie o terminal

### **4. "Conexo recusada" (Antigravity)**
1. Verifique se servidor est rodando
2. Confirme porta correta
3. Teste com: `python -m neocortex.mcp.server --transport websocket --port 8765`

---

##  **Roadmap Atual (v7.0)**

** COMPLETADO:**
- Phase 1: Core Infrastructure
- Phase 1.5: Metrics & Reporting

** EM PROGRESSO:**
- Phase 2: Agent Isolation & Mentor Mode (70%)
  -  AGENT-201: Ambientes isolados criados
  -  AGENT-202: Sub-server com role config
  -  AGENT-203: mentor_step_0() (pendente)
  -  AGENT-204: Tool allow/deny lists
  -  AGENT-205: Testes de isolamento

** PRXIMOS:**
- Phase 3: Manual Orchestration Basics
- Phase 4: Stabilization & Security Policies
- Phase 5: Testing & Documentation

---

##  **Suporte**

### **Arquivos criados:**
1. `start_neocortex_mcp.ps1` - Script PowerShell
2. `start_neocortex_mcp.bat` - Script Batch
3. `antigravity_neocortex_config.json` - Config Antigravity
4. `README_MCP_NEOCORTEX.md` - Este guia

### **Logs:**
- Console output em tempo real
- Logs em `neocortex_framework/.neocortex/logs/`
- Mtricas em DuckDB: `.neocortex/metrics.db`

### **Para desenvolvedores:**
- Cdigo: `neocortex_framework/neocortex/mcp/server.py`
- Ferramentas: `neocortex_framework/neocortex/mcp/tools/`
- Testes: `test_sanity.py` (11/11 passando)

---

** Pronto para uso!** O NeoCortex MCP Server est funcional e pode se conectar ao OpenCode (voc) e ao Antigravity simultaneamente.

**Prximo passo:** Testar conexo e comear a usar as ferramentas `neocortex_*` no Antigravity!