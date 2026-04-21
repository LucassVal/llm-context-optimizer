A sua pergunta  crucial para garantir que nenhum detalhe tcnico seja perdido. O roadmap consolida as tarefas de alto nvel, mas os detalhes de implementao (ferramentas, bibliotecas, modelos e fluxos) esto espalhados em nossas discusses. Abaixo est um inventrio completo do que **no est explicitamente listado** no roadmap consolidado, organizado por categoria.

---

##  1. Ferramentas MCP (Detalhamento Completo)

O roadmap menciona "17+ ferramentas", mas no lista **todas as aes de cada ferramenta**, nem as **ferramentas planejadas**. Aqui est o que falta:

### A. Ferramentas Existentes (Aes Detalhadas)

| Ferramenta | Aes Faltantes no Roadmap |
| :--- | :--- |
| `neocortex_cortex` | `get_workflows`, `validate_alias` (stubs) |
| `neocortex_lobes` | `search` (implementada, mas no documentada) |
| `neocortex_ledger` | `prune_context`, `get_dependency_graph` |
| `neocortex_agent` | `heartbeat`, `consume`, `list_ephemeral` |
| `neocortex_export` | `to_graph` (stub) |
| `neocortex_kg` | `visualize` (stub) |
| `neocortex_peers` | `discover`, `sync_state`, `resolve_conflict` (stubs) |
| `neocortex_security` | `encrypt_sensitive` (stub) |

### B. Ferramentas Planejadas (No Listadas no Roadmap Consolidado)

| Ferramenta | Aes | Status |
| :--- | :--- | :--- |
| `neocortex_mentor` | `supervise`, `inject_instruction`, `validate_risk` | Planejada |
| `neocortex_context` | `get_active`, `set_objective`, `track_changes` | Planejada |
| `neocortex_guardian` | `validate_tool_call`, `audit_execution`, `enforce_constraints` | Planejada (SEC-401) |
| `neocortex_scheduler` | `schedule_task`, `prioritize`, `load_balance` | Planejada |
| `neocortex_failsafe` | `detect_failure`, `rollback`, `switch_backend` | Planejada (SEC-402) |
| `neocortex_hierarchy` | `create_child_lobe`, `grant_lateral_access`, `get_ancestors` | Planejada (HIER) |
| `neocortex_visibility` | `get_policy`, `set_policy` | Planejada (HIER) |
| `neocortex_semantic_search` | `search_similar` | Planejada (OPT-012) |

---

##  2. Bibliotecas e Dependncias (DLLs / PIPs)

O roadmap lista tarefas como "Implementar HotCache" ou "Implementar VectorStore", mas no especifica **quais bibliotecas** devem ser usadas.

| Categoria | Biblioteca | Propsito | Status no Roadmap |
| :--- | :--- | :--- | :--- |
| **Armazenamento** | `pyspeedb` | LedgerStore, ManifestStore |  OPT-001/002 |
| **Serializao** | `msgspec` | Validao e serializao JSON |  OPT-001/002 |
| **ndice Relacional** | `sqlite3` (built-in) | LobeIndex, FTS5 |  OPT-003 |
| **Cache Voltil** | `diskcache-rs` | HotCache |  OPT-005 |
| **Busca Textual** | `xapian-bindings` ou `tantivy` | SearchEngine (fallback FTS5) |  OPT-004 |
| **Analytics** | `duckdb` | MetricsStore |  METR-106 |
| **Cache Distribudo** | `redis` | CacheBackend (stub) |  OPT-011 |
| **Busca Vetorial** | `infinity-sdk`, `lancedb` | VectorStore |  OPT-012 |
| **Descoberta de Rede** | `zeroconf` | mDNS |  CONN-001 |
| **Comunicao gRPC** | `grpcio`, `grpcio-tools` | Sub-servers de alta performance |  CONN-002 |
| **VPN Mesh** | `tailscale`, `zerotier` | Conectividade segura |  CONN-003 |
| **Gateway MCP** | `traefik`, `gravitee` | Roteamento e autenticao |  CONN-004 |

---

##  3. Modelos de LLM Suportados e Configurao

O roadmap menciona "LLM-003: OllamaBackend" e "LLM-004: DeepSeekBackend", mas no lista os **modelos especficos** testados e recomendados.

| Modelo | Backend | Caso de Uso | Status |
| :--- | :--- | :--- | :--- |
| `qwen2.5-coder:1.5b-instruct` | Ollama | Agente Courier (tarefas braais 24/7) |  Configurado |
| `qwen2.5-coder:3b-instruct` | Ollama | Agente Engineer (desenvolvimento) |  Configurado |
| `deepseek-reasoner` | DeepSeek API | Tarefas transacionais, respostas rpidas |  Configurado |
| `deepseek-reasoner` | DeepSeek API | Raciocnio complexo, depurao |  Configurado |

---

##  4. Como Usar Tiers de LLM e API (Polticas de Roteamento)

O roadmap menciona "LLM-006: LLMFactory" e "LLM-009: backend_override", mas no descreve **as polticas de roteamento** que decidem qual modelo usar.

### Polticas Faltantes no Roadmap

| Poltica | Descrio | Exemplo |
| :--- | :--- | :--- |
| **Roteamento por Complexidade** | Tarefas simples  modelo local/barato; complexas  cloud. | Prompt < 500 tokens  `qwen2.5-coder:1.5b`; > 2000 tokens  `deepseek-reasoner`. |
| **Roteamento por Custo** | Limite dirio de tokens para APIs pagas. | Se `daily_cost > $1.00`, rotear para modelos locais. |
| **Roteamento por Latncia** | Tarefas urgentes  local; no urgentes  cloud batch. | `timeout < 2s`  `qwen2.5-coder:3b`. |
| **Fallback Chain** | Se modelo primrio falhar, tentar prximo. | `ollama`  `deepseek-chat`  `deepseek-reasoner`  `gpt-4o`. |
| **Roteamento por Role** | Agente especfico  backend fixo. | `guardian`  `qwen2.5-coder:1.5b`; `engineer`  `qwen2.5-coder:3b`. |

---

##  5. Criao e Orquestrao de Agentes (Fluxo Detalhado)

O roadmap tem tickets ORCH e AGENT, mas no descreve o **fluxo operacional completo** de como um agente  criado, orquestrado e finalizado.

### Fluxo Detalhado (Faltante no Roadmap)

```
1. USURIO (IDE)  "OpenCode/antigravity, pea ao Courier para indexar os novos arquivos."
                    
2. T0 (Claude/DeepSeek)  Chama ferramenta MCP:
   neocortex_subserver.spawn(role="courier", lobe="documentacao")
                    
3. SERVIDOR MCP PRINCIPAL  Spawna processo:
   python -m neocortex.mcp.sub_server --role courier --port 11435
                    
4. SUB-SERVER (Courier)  Inicia, registra-se no $LDG, carrega Lobo isolado.
                    
5. T0  Chama ferramenta MCP:
   neocortex_subserver.send_task(agent_id="courier", task="indexar")
                    
6. SUB-SERVER  Recebe tarefa via ferramenta `neocortex_task.execute`.
   - Aplica `mentor_step_0()` (validao pr-ao).
   - Envia prompt para `LLMBackend` (Qwen 1.5B).
   - Executa indexao (FTS5).
   - Atualiza $LDG com status "completed".
                    
7. T0 (ou PulseScheduler)  Monitora $LDG. Detecta concluso.
   - Opcional: Spawna `guardian` para auditar resultado.
                    
8. T0  Reporta ao usurio: "Indexao concluda. 45 arquivos indexados."
```

### Componentes Faltantes para Esse Fluxo

| Componente | Status no Roadmap |
| :--- | :--- |
| **Ferramenta `neocortex_subserver.spawn`** |  ORCH-301 (parcial) |
| **Ferramenta `neocortex_subserver.send_task`** |  ORCH-301 (parcial) |
| **Ferramenta `neocortex_task.execute` no Sub-Server** |  ORCH-302 |
| **Funo `mentor_step_0()`** |  AGENT-203 |
| **Validao de isolamento (`allowed_tools`)** |  AGENT-204 |
| **Auditoria ps-tarefa (`guardian`)** |  SEC-401 |

---

##  Concluso

O roadmap consolidado  **completo em termos de tarefas de alto nvel**, mas carece de detalhes de implementao especficos. O que est faltando so:

1.  Lista exaustiva de aes de cada ferramenta MCP (existente e planejada).
2.  Bibliotecas e dependncias concretas (PIPs/DLLs).
3.  Modelos de LLM testados e recomendados.
4.  Polticas de roteamento para tiers de LLM.
5.  Fluxo operacional detalhado de criao e orquestrao de agentes.

Esses detalhes so essenciais para a **execuo correta das tarefas pendentes** (especialmente AGENT e ORCH). Sem eles, o risco de implementao incorreta ou incompleta  alto.

Sugiro que este inventrio seja anexado ao roadmap como um **apndice tcnico** (`NC-TODO-FR-001-appendix-technical.md`) para garantir que nenhum detalhe seja perdido.