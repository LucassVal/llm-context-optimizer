# NC-APP-FR-001 - Apndice Tcnico: Detalhamento de Implementao NeoCortex

> **Complemento obrigatrio do roadmap consolidado.** Este documento contm os detalhes tcnicos de implementao que no cabem no roadmap de alto nvel: aes de ferramentas MCP, bibliotecas, modelos LLM, polticas de roteamento, fluxos de orquestrao e status de cada mecanismo de segurana/governana.
>
> **Data Referncia:** 2026-04-11 | **Status Geral:**  Em Estabilizao

---

##  Status dos Mecanismos Centrais

| Regra / Mecanismo | Arquivo Principal | Status | Validao Rpida |
| :--- | :--- | :---: | :--- |
| STEP 0 (Regression Check) | `neocortex/mcp/tools/NC-TOOL-FR-012-regression.py` |  | `neocortex_regression.check(task)` |
| Modo Mentor (`mentor_step_0`) | `neocortex/mcp/sub_server.py` |  AGENT-203 | Funo `mentor_step_0()` existe? |
| Atomic Locks | `SecurityService` + `config.yaml` |  | `neocortex_security.validate_access` |
| Visibilidade Hierrquica | `neocortex_hierarchy` (planejado) |  HIER-001 | Ferramenta no existe |
| Polticas de Uso (Token Budget) | `sub_server.py` + `config.yaml` |  SEC-403 | Chaves `limits.*` no config do agente? |
| Fallback Chain LLM | `LLMBackendFactory` |  | `config.yaml` contm `fallback_chain`? |
| Roteamento Inteligente | `NC-TOOL-FR-000-brain.py` |  | Ferramenta `brain.think` ativa? |
| PulseScheduler (Heartbeat) | `neocortex/core/pulse_scheduler.py` |  | Logs `[Pulse] ...` no servidor |
| Audit Trail | `LedgerService` |  | Seo `audit_trail` no `$LDG`? |
| Consolidao / AKL | `ConsolidationService` / `AKLService` |  | Agendado no PulseScheduler |

---

##  Ferramentas MCP: Aes Completas

### Ferramentas Existentes (Aes No Documentadas no Roadmap)

| Ferramenta | Aes em Falta / Stubs |
| :--- | :--- |
| `neocortex_cortex` | `get_workflows`, `validate_alias` |
| `neocortex_lobes` | `search` (implementada, no documentada) |
| `neocortex_ledger` | `prune_context`, `get_dependency_graph` |
| `neocortex_agent` | `heartbeat`, `consume`, `list_ephemeral` |
| `neocortex_export` | `to_graph` (stub) |
| `neocortex_peers` | `discover`, `sync_state`, `resolve_conflict` |
| `neocortex_security` | `encrypt_sensitive` (stub) |

### Ferramentas Planejadas (No Existem Ainda)

| Ferramenta | Aes | Ticket |
| :--- | :--- | :--- |
| `neocortex_mentor` | `supervise`, `inject_instruction`, `validate_risk` | AGENT-203 |
| `neocortex_guardian` | `validate_tool_call`, `audit_execution`, `enforce_constraints` | SEC-401 |
| `neocortex_failsafe` | `detect_failure`, `rollback`, `switch_backend` | SEC-402 |
| `neocortex_hierarchy` | `create_child_lobe`, `grant_lateral_access`, `get_ancestors` | HIER-001 |
| `neocortex_visibility` | `get_policy`, `set_policy` | HIER-002 |
| `neocortex_scheduler` | `schedule_task`, `prioritize`, `load_balance` | Planejado |
| `neocortex_semantic_search` | `search_similar` | OPT-012 |

---

##  Bibliotecas e Dependncias

| Categoria | Biblioteca | Propsito | Status |
| :--- | :--- | :--- | :---: |
| Armazenamento | `pyspeedb` | LedgerStore, ManifestStore |  |
| Serializao | `msgspec` | Validao e serializao JSON |  |
| ndice Relacional | `sqlite3` (built-in) | LobeIndex, FTS5 |  |
| Cache Voltil | `diskcache-rs` | HotCache |  |
| Analytics | `duckdb` | MetricsStore |  |
| Busca Textual | `xapian-bindings` ou `tantivy` | SearchEngine (fallback FTS5) |  |
| Cache Distribudo | `redis` | CacheBackend (stub) |  OPT-011 |
| Busca Vetorial | `infinity-sdk`, `lancedb` | VectorStore |  OPT-012 |
| Descoberta de Rede | `zeroconf` | mDNS |  CONN-001 |
| Comunicao gRPC | `grpcio`, `grpcio-tools` | Sub-servers alta performance |  CONN-002 |
| Gateway MCP | `traefik`, `gravitee` | Roteamento e autenticao |  CONN-004 |

---

##  Modelos LLM Configurados

| Modelo | Backend | Caso de Uso |
| :--- | :--- | :--- |
| `qwen2.5-coder:1.5b-instruct` | Ollama | Agente Courier (tarefas braais 24/7) |
| `qwen2.5-coder:3b-instruct` | Ollama | Agente Engineer (desenvolvimento) |
| `deepseek-reasoner` | DeepSeek API | Raciocnio complexo, T0 principal |
| `deepseek-chat` | DeepSeek API | Tarefas transacionais, respostas rpidas |

### Polticas de Roteamento (A Implementar)

| Poltica | Regra | Ticket |
| :--- | :--- | :--- |
| Por Complexidade | `< 500 tokens  qwen:1.5b`; `> 2000 tokens  deepseek-reasoner` | neocortex_brain |
| Por Custo | Se `daily_cost > $1.00`, rotear para locais | SEC-403 |
| Por Latncia | `timeout < 2s  local` | neocortex_brain |
| Fallback Chain | `ollama  deepseek-chat  deepseek-reasoner` |  LLM-006 |
| Por Role | `guardian  qwen:1.5b`; `engineer  qwen:3b` | sub_server.py |

---

##  Fluxo Completo de Orquestrao de Agente

```
1. USURIO (IDE)  "Antigravity, pede ao Courier para indexar os arquivos."
2. T0 (DeepSeek/Claude)  neocortex_subserver.spawn(role="courier", lobe="documentacao")
3. SERVIDOR MCP PRINCIPAL  Spawna: python -m neocortex.mcp.sub_server --role courier --port 11435
4. SUB-SERVER (Courier)  Inicia, registra no $LDG, carrega Lobo isolado.
5. T0  neocortex_subserver.send_task(agent_id="courier", task="indexar")
6. SUB-SERVER  Recebe tarefa via neocortex_task.execute
   - [AGENT-203] Aplica mentor_step_0() (validao pr-ao)
   - Envia prompt para LLMBackend (Qwen 1.5B)
   - Executa indexao (FTS5)
   - Atualiza $LDG com status "completed"
7. T0 (ou PulseScheduler)  Monitora $LDG. Detecta concluso.
   - [SEC-401] Opcional: Spawna guardian para auditar resultado.
8. T0  Reporta ao usurio.
```

### Componentes Pendentes para Fluxo Funcionar 100%

| Componente | Arquivo | Ticket |
| :--- | :--- | :--- |
| `spawn` e `send_task` robustos | `NC-TOOL-FR-016-subserver.py` | ORCH-301 |
| `neocortex_task.execute` integrado | `NC-TOOL-FR-017-task.py` | ORCH-302 |
| `mentor_step_0()` | `sub_server.py` | AGENT-203 |
| Validao `allowed_tools` por role | `sub_server.py` | AGENT-204 |
| Guardian ps-tarefa | `NC-TOOL-FR-(novo)-guardian.py` | SEC-401 |

---

##  Aes Imediatas Crticas (Desbloqueadores)

1. **AGENT-203**  Implementar `mentor_step_0()` em `sub_server.py`  sem isso, agentes locais allucinam livremente.
2. **ORCH-301**  Tornar `spawn`, `stop`, `send_task` funcionais  sem isso, o T0 no consegue orquestrar nada.
3. **ORCH-302**  Integrar `execute` no sub-server com `LLMBackend`  sem isso, o agente no executa tarefas.
4. **SEC-401**  Implementar `neocortex_guardian`  camada de auditoria ps-execuo.
5. **SEC-403**  Adicionar limites de token/custo ao `config.yaml` de cada agente.

---

##  Inventrio Completo de Tecnologias do Ecossistema

### 1. Bancos de Dados e Armazenamento Persistente

| Ferramenta | Tipo | Funo no NeoCortex | Status |
| :--- | :--- | :--- | :---: |
| **RocksDB** (via `pyspeedb`) | Key-Value Store | `LedgerStore` e `ManifestStore`. ACID, alta performance. |  |
| **SQLite + FTS5** | Banco Relacional | `LobeIndex`: metadados de Lobos + busca textual completa. |  |
| **DuckDB** | Banco OLAP | `MetricsStore`: analytics de tokens, custos, eficincia. |  |
| **Infinity** | AI-Native DB | `VectorStore`: busca hbrida vetorial + texto. |  OPT-012 |
| **LanceDB** | Banco Vetorial | Alternativa open-source ao Infinity para busca vetorial. |  OPT-012 |

> **Nota:** `pyspeedb` foi escolhido sobre `RocksDB` puro para evitar latncias de compactao.

---

### 2. Cache e Serializao de Alta Performance

| Ferramenta | Tipo | Funo no NeoCortex | Status |
| :--- | :--- | :--- | :---: |
| **diskcache-rs** | Cache em Disco (Rust) | `HotCache`: cache voltil para `hot_context` do PulseScheduler. |  |
| **msgspec** | Serializao/Validao | Substitui `json` padro. Validao com type hints. |  |
| **Redis** | Cache Distribudo | `CacheBackend`: escala horizontal multi-tenant. |  OPT-011 |

---

### 3. Motores de Busca e ndices

| Ferramenta | Tipo | Funo no NeoCortex | Status |
| :--- | :--- | :--- | :---: |
| **SQLite FTS5** | Busca Textual | Backend primrio do `SearchEngine`. |  |
| **Xapian** (`xapian-bindings`) | Motor C++ | Alternativa robusta ao FTS5 p/ grandes volumes. |  OPT-004 |
| **Tantivy** | Motor Rust | Alta performance, alternativa ao Xapian. |  Opcional |

> **Nota:** FTS5 do SQLite atende bem  escala atual. Xapian/Tantivy so para futuro scale-out.

---

### 4. Modelos LLM e Backends

| Ferramenta | Tipo | Funo no NeoCortex | Status |
| :--- | :--- | :--- | :---: |
| **Ollama** | Servidor Local | Backend para modelos locais. |  |
| **DeepSeek API** | API Cloud | T0 principal  raciocnio e desenvolvimento. |  |
| **OpenAI API** | API Cloud | Fallback estratgico e compatibilidade. |  |
| **Anthropic API (Claude)** | API Cloud | Planejado para T0 alternativo (auditoria e orquestrao). |  |
| **Qwen2.5-Coder 1.5B** | Modelo Local | Agente Courier (tarefas braais 24/7). |  |
| **Qwen2.5-Coder 3B** | Modelo Local | Agente Engineer (desenvolvimento). |  |

---

### 5. Orquestrao e Conectividade

| Ferramenta | Tipo | Funo no NeoCortex | Status |
| :--- | :--- | :--- | :---: |
| **FastMCP** | Framework MCP | Servidor MCP principal. |  |
| **WebSocket** (`uvicorn`) | Protocolo | Conexo IDE  servidor MCP. |  |
| **gRPC** (`grpcio`) | Protocolo | Comunicao entre Sub-MCP Servers de alta performance. |  CONN-002 |
| **Zeroconf** | Descoberta | mDNS para descoberta de agentes na LAN. |  CONN-001 |
| **Tailscale / ZeroTier** | VPN Mesh | Conectividade segura entre agentes remotos. |  CONN-003 |

---

### 6. Ferramentas de Desenvolvimento e Distribuio

| Ferramenta | Tipo | Funo no NeoCortex | Status |
| :--- | :--- | :--- | :---: |
| **pytest** | Testes | Testes unitrios e de integrao. |  T0-005 |
| **GitHub Actions** | CI/CD | Pipeline de integrao contnua. |  T0-006 |
| **PyInstaller** | Empacotador | Gerao de `.exe` nico para distribuio. |  Planejado |
| **Tkinter** | GUI | HUD (painel de controle visual). |  Planejado |
| **pystray** | System Tray | Minimizao do HUD para bandeja do sistema. |  Planejado |

---

### 7. Bibliotecas Auxiliares

| Biblioteca | Funo |
| :--- | :--- |
| `pyyaml` | Leitura de arquivos `config.yaml` |
| `requests` / `httpx` | Chamadas HTTP para APIs externas |
| `asyncio` | Operaes assncronas (servidor MCP, PulseScheduler) |
| `watchdog` | Monitoramento de sistema de arquivos (auto-indexao) |
| `matplotlib` | Gerao de grficos para relatrios e HUD |

---

###  Resumo de Status por Ferramenta

| Status | Qtd | Ferramentas |
| :--- | :---: | :--- |
| ** Implementado** | 12 | RocksDB, SQLite+FTS5, DuckDB, diskcache-rs, msgspec, Ollama, DeepSeek API, OpenAI API, Qwen 1.5B, Qwen 3B, FastMCP, WebSocket |
| ** Stub / Parcial** | 9 | Infinity, LanceDB, Redis, Xapian, Tantivy, gRPC, Zeroconf, Tailscale, Anthropic API |
| ** Planejado** | 6 | PyInstaller, pytest, GitHub Actions, Tkinter, pystray, watchdog |
