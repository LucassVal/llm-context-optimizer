#  Sumario do Conhecimento - TURBOQUANT v5.0-CORTEX / NeoCortex

##  Visao Geral
Framework de engenharia de contexto para agentes de IA, baseado em arquitetura fractal (Cortex + Lobos), memoria hierarquica (quente/fria/arquivo) e protocolo de evolucao autonoma. Operacao whitelabel (apenas Markdown/JSON) integrada via MCP a IDEs.

##  Elementos Principais (Aliases)

| Alias | Elemento | Descricao Compacta |
|-------|----------|-------------------|
| `$CTX` | Cortex (.mdc) | Regras universais, vocabulario, workflows, STEP 0, encoding. |
| `$LBE` | Lobo (.mdc) | Contexto de fase/modulo, checkpoint tree, regression local. |
| `$LDG` | Ledger (JSON) | Estado volatil: metricas, timeline, action queue, atomic locks. |
| `$MF` | Manifesto | Indice leve de um lobo/cortex (metadados, resumo simbolico). |
| `$MCP` | Servidor MCP | 10 ferramentas multiacao que expoem $TQ para IDEs. |
| `$ST0` | STEP 0 | Regression check obrigatorio antes de qualquer acao. |
| `$ENC` | Compact Encoding | Simbolos $ @ ! ? (uso obrigatorio). |
| `$RGR` | Regression Buffer | Historico de falhas para evitar repeticao. |
| `$AKL` | Adaptive Knowledge Lifecycle | Ciclo de vida adaptativo (importancia, maturidade, decaimento). |
| `$KG` | Mini Knowledge Graph | Grafo semantico local (evolucao do $ENC). |
| `$CSL` | Consolidacao Semantica | Transforma experiencia efemera em regras permanentes. |
| `$AGEF` | Agente Efemero | Subagente com lobo temporario, gerenciado pelo T0. |
| `$T0` | Cortex Executor | Agente principal que orquestra, consolida e evolui. |
| `$BENCH` | Benchmark Suite | Drift Exhaustion, OmniReasoning, Titanomachy. |

##  Modelos de Linguagem e Referencias Academicas

| Fonte | Sigla | Conceitos Relevantes |
|-------|-------|---------------------|
| MemGPT (Letta) | `?memgpt` | Memoria hierarquica RAM/Disk, paging de contexto. |
| ReAct (Google DeepMind) | `?react` | Loop ThoughtActionObservation, scratchpad isolado. |
| Acon Framework | `?acon` | Context Compaction, summarizacao progressiva. |
| Cursor Rules | `?cursor` | Regras modulares, alwaysApply, globs. |
| Anthropic CLAUDE.md | `?claude` | Hierarquia GlobalProjetoLocal, fewshot examples. |
| ByteRover (China) | `?byterover` | Arquitetura invertida, Context Tree, Zero Dependencias. |
| TiMem (China) | `?timem` | Temporal Memory Tree, consolidacao guiada por semantica. |
| GAM (China) | `?gam` | DualAgent (escritor/leitor), principio JIT. |
| MemOS (China) | `?memos` | Memoria como SO, MemCube (metadados). |
| CoM / LightMem (China) | `?lightmem` | ChainofMemory, 3 estagios (38x reducao). |
| AGENTiGraph (Japao) | `?agentigraph` | Integracao LLM + Knowledge Graph. |
| REMIND (Taiwan) | `?remind` | Framework modular STM + LTM. |
| MCP (Anthropic) | `?mcp` | Model Context Protocol, ferramentas via stdio. |

##  Principais Secoes do Documento

1. **Visao Geral** - O que e o TurboQuant/NeoCortex
2. **Elementos Principais** - Aliases e componentes
3. **Referencias Academicas** - Base teorica
4. **Conceitos-Chave** - Terminologia compactada
5. **Benchmark Suite** - Testes e metricas
6. **Workflows** - Explore-Plan-Act, Debug, Wrap Up
7. **Arquitetura** - Cortex, Lobos, JSON Ledger
8. **MCP Server** - Integracao com IDEs
9. **Agentes Efemeros** - Multi-agente, orquestracao
10. **Evolucao Autonoma** - Ciclo de aprendizado
11. **Persistencia AntiDesistencia** - Garantias de aderencia
12. **Empacotamento** - Distribuicao PyPI, CLI

##  Estrutura de Arquivos

```
[PROJECT]/
 memory_turboquant_[PROJECT].json    STATE LEDGER
 .agents/
    rules/
       00-cortex.mdc               GLOBAL INSTRUCTIONS
       phase-[N]-[name].mdc        Lobes por fase/modulo
       local.mdc                   Notas pessoais (gitignore)
       CHANGELOG.md                Ultimas 5 mudancas estruturais
       archive/                    Lobes completados (com auto-sumario)
    workflows/                      Comandos Slash opcionais
 memory_lobes/                       Estado detalhado dos lobos ativos
 archive/                            Auto-sumarios markdown de fases completadas
 backup/                             Backups timestamped (!backup)
```

##  Proximos Passos

1. Renomear projeto para **NeoCortex**
2. Criar estrutura white label
3. Implementar framework no sistema opencode
4. Destrinchar arquivo completo em componentes estruturados
5. Criar documentacao de referencia completa