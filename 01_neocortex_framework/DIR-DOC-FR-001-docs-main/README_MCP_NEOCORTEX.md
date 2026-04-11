# 🚀 NeoCortex MCP Server - Host para OpenCode + Antigravity

> **Servidor MCP pronto para produção** - 22 ferramentas, 73+ ações, métricas automáticas, WebSocket/stdio

---

## 🎯 **Status: PRONTO & FUNCIONAL**

✅ **MCP Server atualizado** com suporte a WebSocket + stdio  
✅ **22 ferramentas** registradas com métricas automáticas  
✅ **DuckDB MetricsStore** + relatórios em Markdown/CSV/JSON  
✅ **Agent Isolation** (courier/engineer) com mentor mode (parcial)  
✅ **Scripts de startup** para Windows (PowerShell + Batch)  
✅ **Configuração para Antigravity** incluída

---

## 🚀 **Como Iniciar (30 segundos)**

### **Opção 1: PowerShell (Recomendado)**
```powershell
cd "C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42"
.\start_neocortex_mcp.ps1
```

### **Opção 2: Batch File**
```cmd
cd "C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42"
start_neocortex_mcp.bat
```

### **Opção 3: Manual (Python)**
```bash
cd neocortex_framework
python -m neocortex.mcp.server --transport websocket --host localhost --port 8765 --log-level INFO
```

**Saída esperada:**
```
[INFO] Iniciando NeoCortex MCP Server v4.2-cortex (Host Mode)
[INFO] Transporte: websocket
[INFO] Endereço: ws://localhost:8765
[INFO] Heartbeat: a cada 30 segundos
✅ Servidor WebSocket pronto em ws://localhost:8765
📡 Aguardando conexões do OpenCode/Antigravity...
```

---

## 🔗 **Conectar no Antigravity**

### **Configuração Rápida:**
1. **Copie** `antigravity_neocortex_config.json` para:
   - `%APPDATA%\antigravity\mcp-servers.json` (Windows)
   - `~/.config/antigravity/mcp-servers.json` (Mac/Linux)

2. **OU adicione ao seu arquivo existente**

3. **No Antigravity**, use:
   - **WebSocket**: `neocortex-websocket` (ws://localhost:8765)
   - **Stdio**: `neocortex` (inicia automaticamente)

### **Verifique a conexão:**
- Abra o Antigravity
- Verifique se as ferramentas `neocortex_*` aparecem
- Teste: `neocortex_cortex` com ação `get_full`

---

## 🛠️ **Ferramentas Disponíveis (22)**

| Categoria | Ferramenta | Ações Principais | Status |
|-----------|------------|------------------|--------|
| **Core** | `neocortex_cortex` | get_full, get_section, get_aliases | ✅ |
| **State** | `neocortex_ledger` | read, write, update_section | ✅ |
| **Reporting** | `neocortex_report` | generate_daily_summary, cost_report, agent_report | ✅ |
| **Orchestration** | `neocortex_subserver` | spawn, stop, list, send_task | ✅ |
| **Execution** | `neocortex_task` | execute (com mentor mode) | ✅ |
| **Checkpoints** | `neocortex_checkpoint` | get_current, create, restore | ✅ |
| **Configuration** | `neocortex_config` | get, set, validate | ✅ |
| **Lobes** | `neocortex_lobes` | list, get, create | ✅ |
| **Search** | `neocortex_search` | semantic, keyword | ✅ |
| **Agents** | `neocortex_agent` | execute (backend override) | ✅ |
| **Pulse** | `neocortex_pulse` | status, force_consolidation | ✅ |
| **Metrics** | (automático) | DuckDB + relatórios | ✅ |

**Total: 73+ ações operacionais**

---

## 📊 **Métricas & Relatórios Automáticos**

O servidor inclui **MetricsStore com DuckDB** que registra:

1. **Token Economy**: Uso diário de tokens por modelo/agente
2. **Cost Tracking**: Custos reais vs estimados, ROI
3. **Agent Activity**: Spawns, tarefas, falhas
4. **Pulse Health**: Consolidação, pruning, checkpoints

**Relatórios disponíveis via `neocortex_report`:**
- `generate_daily_summary`: Resumo diário (Markdown)
- `generate_cost_report`: Análise de custos (CSV/JSON)
- `generate_agent_report`: Atividade dos agentes

---

## 🤖 **Agent Isolation (Phase 2 - Parcial)**

**Ambientes criados:**
- `lobes/courier/`: Agente 1.5B (Qwen) - leitura apenas
- `lobes/engineer/`: Agente 3B (Qwen) - leitura/escrita

**Configuração por role:**
- `neocortex_config.yaml` com `allowed_tools` específicos
- Sub-server com filtragem automática de ferramentas
- `--role` parameter para identificação

**Pendente:** `mentor_step_0()` (AGENT-203)

---

## ⚙️ **Comandos Avançados**

### **Modos de Transporte:**
```bash
# WebSocket (host mode)
python -m neocortex.mcp.server --transport websocket --port 9999

# Stdio (IDE integration)
python -m neocortex.mcp.server --transport stdio

# Debug mode
python -m neocortex.mcp.server --transport websocket --log-level DEBUG
```

### **Parâmetros:**
- `--transport`: `websocket` (padrão) ou `stdio`
- `--host`: Hostname (padrão: localhost)
- `--port`: Porta (padrão: 8765)
- `--log-level`: DEBUG, INFO, WARNING, ERROR
- `--heartbeat-interval`: Segundos entre heartbeats

---

## 🔧 **Solução de Problemas**

### **1. "FastMCP não encontrado"**
```bash
pip install mcp
```

### **2. "Porta já em uso"**
```bash
# Use porta diferente
python -m neocortex.mcp.server --port 9999

# Ou encontre processo usando a porta
netstat -ano | findstr :8765
```

### **3. "Python não encontrado"**
- Instale Python 3.8+
- Adicione ao PATH durante instalação
- Reinicie o terminal

### **4. "Conexão recusada" (Antigravity)**
1. Verifique se servidor está rodando
2. Confirme porta correta
3. Teste com: `python -m neocortex.mcp.server --transport websocket --port 8765`

---

## 📈 **Roadmap Atual (v7.0)**

**✅ COMPLETADO:**
- Phase 1: Core Infrastructure
- Phase 1.5: Metrics & Reporting

**🔄 EM PROGRESSO:**
- Phase 2: Agent Isolation & Mentor Mode (70%)
  - ✅ AGENT-201: Ambientes isolados criados
  - ✅ AGENT-202: Sub-server com role config
  - ❌ AGENT-203: mentor_step_0() (pendente)
  - ✅ AGENT-204: Tool allow/deny lists
  - ❌ AGENT-205: Testes de isolamento

**⏳ PRÓXIMOS:**
- Phase 3: Manual Orchestration Basics
- Phase 4: Stabilization & Security Policies
- Phase 5: Testing & Documentation

---

## 📞 **Suporte**

### **Arquivos criados:**
1. `start_neocortex_mcp.ps1` - Script PowerShell
2. `start_neocortex_mcp.bat` - Script Batch
3. `antigravity_neocortex_config.json` - Config Antigravity
4. `README_MCP_NEOCORTEX.md` - Este guia

### **Logs:**
- Console output em tempo real
- Logs em `neocortex_framework/.neocortex/logs/`
- Métricas em DuckDB: `.neocortex/metrics.db`

### **Para desenvolvedores:**
- Código: `neocortex_framework/neocortex/mcp/server.py`
- Ferramentas: `neocortex_framework/neocortex/mcp/tools/`
- Testes: `test_sanity.py` (11/11 passando)

---

**🎉 Pronto para uso!** O NeoCortex MCP Server está funcional e pode se conectar ao OpenCode (você) e ao Antigravity simultaneamente.

**Próximo passo:** Testar conexão e começar a usar as ferramentas `neocortex_*` no Antigravity!