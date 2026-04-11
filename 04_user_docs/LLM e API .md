A sua pergunta é crucial para garantir que nenhum detalhe técnico seja perdido. O roadmap consolida as tarefas de alto nível, mas os detalhes de implementação (ferramentas, bibliotecas, modelos e fluxos) estão espalhados em nossas discussões. Abaixo está um inventário completo do que **não está explicitamente listado** no roadmap consolidado, organizado por categoria.

---

## 🧰 1. Ferramentas MCP (Detalhamento Completo)

O roadmap menciona "17+ ferramentas", mas não lista **todas as ações de cada ferramenta**, nem as **ferramentas planejadas**. Aqui está o que falta:

### A. Ferramentas Existentes (Ações Detalhadas)

| Ferramenta | Ações Faltantes no Roadmap |
| :--- | :--- |
| `neocortex_cortex` | `get_workflows`, `validate_alias` (stubs) |
| `neocortex_lobes` | `search` (implementada, mas não documentada) |
| `neocortex_ledger` | `prune_context`, `get_dependency_graph` |
| `neocortex_agent` | `heartbeat`, `consume`, `list_ephemeral` |
| `neocortex_export` | `to_graph` (stub) |
| `neocortex_kg` | `visualize` (stub) |
| `neocortex_peers` | `discover`, `sync_state`, `resolve_conflict` (stubs) |
| `neocortex_security` | `encrypt_sensitive` (stub) |

### B. Ferramentas Planejadas (Não Listadas no Roadmap Consolidado)

| Ferramenta | Ações | Status |
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

## 📦 2. Bibliotecas e Dependências (DLLs / PIPs)

O roadmap lista tarefas como "Implementar HotCache" ou "Implementar VectorStore", mas não especifica **quais bibliotecas** devem ser usadas.

| Categoria | Biblioteca | Propósito | Status no Roadmap |
| :--- | :--- | :--- | :--- |
| **Armazenamento** | `pyspeedb` | LedgerStore, ManifestStore | ✅ OPT-001/002 |
| **Serialização** | `msgspec` | Validação e serialização JSON | ✅ OPT-001/002 |
| **Índice Relacional** | `sqlite3` (built-in) | LobeIndex, FTS5 | ✅ OPT-003 |
| **Cache Volátil** | `diskcache-rs` | HotCache | ✅ OPT-005 |
| **Busca Textual** | `xapian-bindings` ou `tantivy` | SearchEngine (fallback FTS5) | 🟡 OPT-004 |
| **Analytics** | `duckdb` | MetricsStore | ✅ METR-106 |
| **Cache Distribuído** | `redis` | CacheBackend (stub) | 🟡 OPT-011 |
| **Busca Vetorial** | `infinity-sdk`, `lancedb` | VectorStore | 🟡 OPT-012 |
| **Descoberta de Rede** | `zeroconf` | mDNS | 🟡 CONN-001 |
| **Comunicação gRPC** | `grpcio`, `grpcio-tools` | Sub-servers de alta performance | 🟡 CONN-002 |
| **VPN Mesh** | `tailscale`, `zerotier` | Conectividade segura | 🟡 CONN-003 |
| **Gateway MCP** | `traefik`, `gravitee` | Roteamento e autenticação | 🟡 CONN-004 |

---

## 🤖 3. Modelos de LLM Suportados e Configuração

O roadmap menciona "LLM-003: OllamaBackend" e "LLM-004: DeepSeekBackend", mas não lista os **modelos específicos** testados e recomendados.

| Modelo | Backend | Caso de Uso | Status |
| :--- | :--- | :--- | :--- |
| `qwen2.5-coder:1.5b-instruct` | Ollama | Agente Courier (tarefas braçais 24/7) | ✅ Configurado |
| `qwen2.5-coder:3b-instruct` | Ollama | Agente Engineer (desenvolvimento) | ✅ Configurado |
| `deepseek-reasoner` | DeepSeek API | Tarefas transacionais, respostas rápidas | ✅ Configurado |
| `deepseek-reasoner` | DeepSeek API | Raciocínio complexo, depuração | ✅ Configurado |

---

## 🔄 4. Como Usar Tiers de LLM e API (Políticas de Roteamento)

O roadmap menciona "LLM-006: LLMFactory" e "LLM-009: backend_override", mas não descreve **as políticas de roteamento** que decidem qual modelo usar.

### Políticas Faltantes no Roadmap

| Política | Descrição | Exemplo |
| :--- | :--- | :--- |
| **Roteamento por Complexidade** | Tarefas simples → modelo local/barato; complexas → cloud. | Prompt < 500 tokens → `qwen2.5-coder:1.5b`; > 2000 tokens → `deepseek-reasoner`. |
| **Roteamento por Custo** | Limite diário de tokens para APIs pagas. | Se `daily_cost > $1.00`, rotear para modelos locais. |
| **Roteamento por Latência** | Tarefas urgentes → local; não urgentes → cloud batch. | `timeout < 2s` → `qwen2.5-coder:3b`. |
| **Fallback Chain** | Se modelo primário falhar, tentar próximo. | `ollama` → `deepseek-chat` → `deepseek-reasoner` → `gpt-4o`. |
| **Roteamento por Role** | Agente específico → backend fixo. | `guardian` → `qwen2.5-coder:1.5b`; `engineer` → `qwen2.5-coder:3b`. |

---

## 🧑‍💼 5. Criação e Orquestração de Agentes (Fluxo Detalhado)

O roadmap tem tickets ORCH e AGENT, mas não descreve o **fluxo operacional completo** de como um agente é criado, orquestrado e finalizado.

### Fluxo Detalhado (Faltante no Roadmap)

```
1. USUÁRIO (IDE) → "OpenCode/antigravity, peça ao Courier para indexar os novos arquivos."
                    │
2. T0 (Claude/DeepSeek) → Chama ferramenta MCP:
   neocortex_subserver.spawn(role="courier", lobe="documentacao")
                    │
3. SERVIDOR MCP PRINCIPAL → Spawna processo:
   python -m neocortex.mcp.sub_server --role courier --port 11435
                    │
4. SUB-SERVER (Courier) → Inicia, registra-se no $LDG, carrega Lobo isolado.
                    │
5. T0 → Chama ferramenta MCP:
   neocortex_subserver.send_task(agent_id="courier", task="indexar")
                    │
6. SUB-SERVER → Recebe tarefa via ferramenta `neocortex_task.execute`.
   - Aplica `mentor_step_0()` (validação pré-ação).
   - Envia prompt para `LLMBackend` (Qwen 1.5B).
   - Executa indexação (FTS5).
   - Atualiza $LDG com status "completed".
                    │
7. T0 (ou PulseScheduler) → Monitora $LDG. Detecta conclusão.
   - Opcional: Spawna `guardian` para auditar resultado.
                    │
8. T0 → Reporta ao usuário: "Indexação concluída. 45 arquivos indexados."
```

### Componentes Faltantes para Esse Fluxo

| Componente | Status no Roadmap |
| :--- | :--- |
| **Ferramenta `neocortex_subserver.spawn`** | 🟡 ORCH-301 (parcial) |
| **Ferramenta `neocortex_subserver.send_task`** | 🟡 ORCH-301 (parcial) |
| **Ferramenta `neocortex_task.execute` no Sub-Server** | 🟡 ORCH-302 |
| **Função `mentor_step_0()`** | 🟡 AGENT-203 |
| **Validação de isolamento (`allowed_tools`)** | 🟡 AGENT-204 |
| **Auditoria pós-tarefa (`guardian`)** | 🔴 SEC-401 |

---

## 🏁 Conclusão

O roadmap consolidado é **completo em termos de tarefas de alto nível**, mas carece de detalhes de implementação específicos. O que está faltando são:

1.  Lista exaustiva de ações de cada ferramenta MCP (existente e planejada).
2.  Bibliotecas e dependências concretas (PIPs/DLLs).
3.  Modelos de LLM testados e recomendados.
4.  Políticas de roteamento para tiers de LLM.
5.  Fluxo operacional detalhado de criação e orquestração de agentes.

Esses detalhes são essenciais para a **execução correta das tarefas pendentes** (especialmente AGENT e ORCH). Sem eles, o risco de implementação incorreta ou incompleta é alto.

Sugiro que este inventário seja anexado ao roadmap como um **apêndice técnico** (`NC-TODO-FR-001-appendix-technical.md`) para garantir que nenhum detalhe seja perdido.