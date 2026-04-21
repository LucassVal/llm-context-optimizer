#  NeoCortex  Industrial AI Orchestration Framework

> **Formerly:** LLM Context Optimizer / TurboQuant v4.2-Cortex  
> **GitHub:** [LucassVal/llm-context-optimizer](https://github.com/LucassVal/llm-context-optimizer)  
> **Author:** Lucas Valrio  
> **Status:** Active Development  Phase 1 (Foundation) 80% complete

---

##  O que o NeoCortex resolve?

Agentes LLM sofrem de problemas estruturais graves:

-  **Context amnesia**  esquecem tudo entre sesses
-  **Token bloat**  gastam milhares de tokens redescobindo o que j sabem  
-  **Hallucinated commands**  chutam comandos errados por falta de contexto
-  **Regression loops**  repetem as mesmas solues erradas

O NeoCortex resolve isso com uma **arquitetura de memria fractal** executada localmente via MCP (Model Context Protocol), inspirada em MemGPT, ReAct e pesquisas de Context Engineering.

---

##  Resultados Comprovados

>  Escalabilidade para 1 Milho de Tokens: veja os [Benchmarks](https://github.com/LucassVal/llm-context-optimizer/blob/main/BENCHMARKS.md)  
> Crescimento O(1) de contexto enquanto agentes padro sofrem exploso O(N).

| Mtrica | Agente Padro | NeoCortex |
| :--- | :---: | :---: |
| Custo por sesso (20 turnos) | 100% | **~30%** |
| Memria cross-session |  |  FTS5 + RocksDB |
| Drift cognitivo (11 turnos) | Falha |  Isolado |
| Industrial Stress (100 turnos) | Colapso |  Sobrevive |

---

##  Arquitetura

```

                      NEOCORTEX v5.0                       
                                                           
       
   LedgerStore     LobeService      MCP Server     
   (RocksDB)      (FTS5+SQLite)    30 tools/114+   
           actions      
                                       
   
             Lobes  Memria Semntica Persistente      
    $ARCH  $SEC  $DEV  $COURIER  $ENGINEER  $GUARDIAN   
   
   
     Hierarchical Memory: Hot Cache  Cold  Archive    
   
   
     Multi-Agent: T0 (Orquestrador)  A2A Gateway      
      Courier (Qwen 1.5B) + Engineer (Qwen 3B)         
   

```

---

##  Quick Start (30 segundos)

```bash
git clone https://github.com/LucassVal/llm-context-optimizer.git
cd llm-context-optimizer

# Instalar dependncias
pip install -r 01_neocortex_framework/requirements.txt

# Iniciar MCP Server
python 01_neocortex_framework/neocortex/mcp/server.py

# Verificar ferramentas disponveis (20 ferramentas, ~70 aes)
python 01_neocortex_framework/neocortex/mcp/server.py --list-tools
```

---

##  Benchmark Suite

```bash
# Suite completa de testes (TurboQuant v4.2-Cortex)
python examples/ollama-benchmark/benchmark_master_suite.py

# Modelos suportados:
# - qwen2.5-coder (local, grtis)
# - llama3.1 (local, grtis)
# - deepseek (API)
# - openai (API)
```

4 pilares de teste:
1. **Empirical Token Optimization** (20 turnos)  prova reduo O(1)
2. **Industrial Stress Test** (100 turnos)  colapso KV-Cache 2048
3. **Cognitive Drift** (11 turnos)  prova isolamento de memria
4. **Turbulent Dev Simulator**  amnsia cross-session, Nuclear Locks, merge conflicts

---

##  Casos de Uso

###  Desenvolvedores Individuais
Conecte seu editor (Cursor, OpenCode) ao NeoCortex MCP e ganhe memria persistente automtica  sem copiar contexto manualmente.

###  Times de Engenharia
Compartilhe lobos de memria entre agentes. Courier e Engineer trabalham em paralelo, cada um com seu domnio isolado.

###  Empresas
Gateway centralizado com OAuth 2.1, rate limiting, audit trail e 30 ferramentas especializadas na Fase 2.

---

##  Documentao

| Documento | Contedo |
| :--- | :--- |
| [SSOT & Naming](01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md) | Convenes + changelog |
| [Roadmap](01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md) | Tickets e prioridades |
| [Technical Appendix](01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-APP-FR-001-technical-appendix.md) | 30+ ferramentas, stores, DBs |
| [Ubiquitous Language](01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-DOC-FR-001-ubiquitous-language-dictionary.md) | Dicionrio @$% |
| [Boot Manifest](DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md) | Boot para qualquer IA |
| [Benchmarks](https://github.com/LucassVal/llm-context-optimizer/blob/main/BENCHMARKS.md) | Resultados empricos |

---

##  Stack Tcnico

| Camada | Tecnologia |
| :--- | :--- |
| MCP Framework | FastMCP (Python) |
| State / Ledger | RocksDB via pyspeedb |
| Lobe Index | SQLite FTS5 |
| Metrics / Analytics | DuckDB |
| Hot Cache | diskcache-rs |
| LLM Local | Ollama (Qwen 2.5, Llama 3) |
| LLM Cloud | DeepSeek, OpenAI (API) |
| Embedding | sentence-transformers |

---

##  Baseado Em

- [MemGPT](https://arxiv.org/abs/2310.08560)  Memria hierrquica para LLMs
- [ReAct](https://arxiv.org/abs/2210.03629)  Reasoning + Acting unificados
- [Model Context Protocol](https://modelcontextprotocol.io)  Anthropic MCP spec
- [Google A2A Protocol](https://google.github.io/A2A)  Agent-to-Agent (Fase 2)

---

##  Licena

MIT  Livre para uso pessoal e comercial.

---

##  Contribuiu?

Se o NeoCortex economizou seus tokens ou melhorou seu workflow, considere dar uma  no GitHub.

> *"O objetivo no  uma IA mais inteligente.  uma IA que se lembra."*

