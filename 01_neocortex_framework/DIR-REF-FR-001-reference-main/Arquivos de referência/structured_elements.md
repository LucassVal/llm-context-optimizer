#  Elementos Estruturados - NeoCortex v5.0-CORTEX

Extracao e estruturacao do conhecimento contido no arquivo "Sem titulo.txt".

##  Secoes Principais Identificadas

### 1.  Visao Geral e Elementos Principais
- Framework de engenharia de contexto para agentes de IA
- Arquitetura fractal (Cortex + Lobos)
- Memoria hierarquica (quente/fria/arquivo)
- Protocolo de evolucao autonoma
- White-label (apenas Markdown/JSON)
- Integracao via MCP a IDEs (VS Code, Antigravity, Cursor)

### 2.  Sistema de Aliases (Simbolos Obrigatorios)
| Alias | Elemento | Descricao |
|-------|----------|-----------|
| `$CTX` | Cortex (.mdc) | Regras universais, vocabulario, workflows, STEP 0, encoding |
| `$LBE` | Lobo (.mdc) | Contexto de fase/modulo, checkpoint tree, regression local |
| `$LDG` | Ledger (JSON) | Estado volatil: metricas, timeline, action queue, atomic locks |
| `$MF` | Manifesto | Indice leve de um lobo/cortex (metadados, resumo simbolico) |
| `$MCP` | Servidor MCP | 10 ferramentas multiacao que expoem $TQ para IDEs |
| `$ST0` | STEP 0 | Regression check obrigatorio antes de qualquer acao |
| `$ENC` | Compact Encoding | Simbolos $ @ ! ? (uso obrigatorio) |
| `$RGR` | Regression Buffer | Historico de falhas para evitar repeticao |
| `$AKL` | Adaptive Knowledge Lifecycle | Ciclo de vida adaptativo (importancia, maturidade, decaimento) |
| `$KG` | Mini Knowledge Graph | Grafo semantico local (evolucao do $ENC) |
| `$CSL` | Consolidacao Semantica | Transforma experiencia efemera em regras permanentes |
| `$AGEF` | Agente Efemero | Subagente com lobo temporario, gerenciado pelo T0 |
| `$T0` | Cortex Executor | Agente principal que orquestra, consolida e evolui |
| `$BENCH` | Benchmark Suite | Drift Exhaustion, OmniReasoning, Titanomachy |

### 3.  Modelos de Referencia Academica
| Fonte | Sigla | Conceitos Incorporados |
|-------|-------|-----------------------|
| MemGPT (Letta) | `?memgpt` | Memoria hierarquica RAM/Disk, paging de contexto |
| ReAct (Google DeepMind) | `?react` | Loop ThoughtActionObservation, scratchpad isolado |
| Acon Framework | `?acon` | Context Compaction, summarizacao progressiva |
| Cursor Rules | `?cursor` | Regras modulares, alwaysApply, globs |
| Anthropic CLAUDE.md | `?claude` | Hierarquia GlobalProjetoLocal, fewshot examples |
| ByteRover (China) | `?byterover` | Arquitetura invertida, Context Tree, Zero Dependencias |
| TiMem (China) | `?timem` | Temporal Memory Tree, consolidacao guiada por semantica |
| GAM (China) | `?gam` | DualAgent (escritor/leitor), principio JIT |
| MemOS (China) | `?memos` | Memoria como SO, MemCube (metadados) |
| CoM / LightMem (China) | `?lightmem` | ChainofMemory, 3 estagios (38x reducao) |
| AGENTiGraph (Japao) | `?agentigraph` | Integracao LLM + Knowledge Graph |
| REMIND (Taiwan) | `?remind` | Framework modular STM + LTM |
| MCP (Anthropic) | `?mcp` | Model Context Protocol, ferramentas via stdio |

### 4.  Workflows Principais

#### Explore-Plan-Act (Para features complexas)
1. **STEP 0**  OBRIGATORIO
2. **Explore** (somente leitura): mapear arquivos, identificar dependencias
3. **Plan**: `<thinking>` + propor plano em 2-3 pontos  AGUARDAR CONFIRMACAO
4. **Act**: executar em diffs minimos
5. **Observe**: `!lint` + `!test`  validar contra objetivo
6. **Persist**: atualizar estado + `!backup`

#### Debug
1. **STEP 0**  OBRIGATORIO
2. Reproduzir  Hipotese Unica  Confirmar  Aplicar  Documentar no Regression Buffer

#### Wrap Up Session (SEMPRE ao terminar)
**Triggers:** "wrap up", "see you later", "that's it for today", tarefa concluida
1. Atualizar "Current State" + proximos passos
2. Marcar checkpoint no lobe ativo
3. Adicionar session_timeline no JSON
4. action_queue: in_progress  completed/pending
5. Compactar hot_context se > 5 entradas
6. `!backup`
7. Atualizar CHANGELOG: registrar 1 linha de mudanca estrutural
8. "Session saved. Next resumes at [CHECKPOINT]."

### 5.  Arquitetura de Arquivos
```
[PROJECT]/
 memory_neocortex_[PROJECT].json    STATE LEDGER
 .agents/
    rules/
       00-cortex.mdc               GLOBAL INSTRUCTIONS (alwaysApply: true)
       phase-[N]-[name].mdc        Lobes por fase/modulo
       local.mdc                   Notas pessoais (gitignore)
       CHANGELOG.md                Ultimas 5 mudancas estruturais
       archive/                    Lobes completados (com auto-sumario)
    workflows/                      Comandos Slash opcionais
 memory_lobes/                       Estado detalhado dos lobos ativos
 archive/                            Auto-sumarios markdown de fases completadas
 backup/                             Backups timestamped (!backup)
```

### 6.  Sistema MCP (Model Context Protocol)

#### 10 Ferramentas MultiAcao
| # | Nome da Ferramenta | Acoes (`action`) | Descricao |
|---|-------------------|------------------|-----------|
| **1** | `neocortex_cortex` | `get_full`, `get_section`, `get_aliases`, `get_workflows`, `validate_alias` | Acesso ao cortex central |
| **2** | `neocortex_lobes` | `list_active`, `get_content`, `get_checkpoint_tree`, `activate`, `deactivate` | Gerenciamento de lobos |
| **3** | `neocortex_checkpoint` | `get_current`, `set_current`, `complete_task`, `list_history` | Controle de checkpoints |
| **4** | `neocortex_regression` | `check`, `add_entry`, `list_all` | STEP 0 e buffer de regressao |
| **5** | `neocortex_ledger` | `get_metrics`, `get_atomic_locks`, `get_dependency_graph`, `prune_context` | Acesso ao ledger JSON |
| **6** | `neocortex_benchmark` | `run_drift`, `run_titanomachy`, `get_last_report` | Execucao de benchmarks |
| **7** | `neocortex_agent` | `spawn`, `heartbeat`, `consume`, `list_ephemeral` | Orquestracao de agentes efemeros |
| **8** | `neocortex_init` | `scan_project`, `generate_cortex`, `generate_lobe` | Inicializacao de projetos |
| **9** | `neocortex_config` | `get_config`, `set_model`, `list_models` | Configuracao do sistema |
| **10** | `neocortex_export` | `to_markdown`, `to_json`, `to_graph` | Exportacao de dados |

### 7.  Benchmark Suite

#### Testes Principais
1. **Drift Exhaustion (Gauntlet)** - Testa resistencia ao drift de contexto
2. **OmniReasoning** - Avaliacao de raciocinio multi-dominio
3. **Titanomachy** - Simulacao massiva (100+ tarefas)
4. **Red Team (Adversarial)** - Testes de seguranca e prompt injection
5. **Chaos Environment** - Conflitos de merge, rollbacks, ambientes turbulentos

#### Metricas Coletadas
- Tokens consumidos (Stateless vs NeoCortex)
- Acuracia em manter regras
- Context drift errors
- Session continuity
- ROI financeiro (projecao de custos em nuvem)

### 8.  Agentes Efemeros e Orquestracao

#### Conceito de "Micro Quants"
- Agentes criados para tarefas especificas
- Excluidos ou arquivados apos conclusao
- Conhecimento persistido em logs consultaveis pelo T0
- Ciclo de vida gerenciado pelo cortex executor

#### Estrutura no JSON Ledger
```json
"memory_cortex": {
  "active_agents": [
    {
      "agent_id": "ag-001",
      "role": "code_reviewer",
      "status": "running",
      "created_at": "2026-04-09T10:00:00Z",
      "lobe_ref": "ephemeral/ag-001-code-review.mdc",
      "parent_task": "Implementar endpoint /login"
    }
  ],
  "agent_archive": {
    "completed": [],
    "failed": []
  }
}
```

### 9.  Ciclo de Evolucao Autonoma

#### Componentes Habilitadores
1. **Adaptive Knowledge Lifecycle ($AKL)** - Importancia, maturidade, decaimento
2. **Semantic Consolidation ($CSL)** - Transforma experiencia em regras permanentes
3. **Mini Knowledge Graph ($KG)** - Evolucao do compact encoding para grafo semantico
4. **Regression Buffer ($RGR)** - Aprendizado com falhas passadas
5. **Audit Trail** - Rastreabilidade completa de acoes

#### Fluxo de Evolucao
1. Agente executa tarefas  gera experiencia
2. T0 (cortex executor) analisa resultados
3. Identifica padroes de sucesso/falha
4. Consolida em regras semanticas
5. Atualiza cortex e lobos
6. Arquiva conhecimento obsoleto

### 10.  Persistencia AntiDesistencia

#### Mecanismos para Prevenir "Desistencia" das Regras
| Mecanismo | Como Funciona |
|-----------|---------------|
| **STEP 0 (Regression Check)** | Reafirmacao obrigatoria a cada acao |
| **Compact Encoding Obrigatorio** | Reduz carga cognitiva com simbolos curtos |
| **Workflow de Finalizacao Explicito** | Encerramento formal com salvamento de estado |
| **Atomic Locks no JSON Ledger** | Protecao fisica contra modificacoes nao autorizadas |
| **Lobos Isolados** | Contexto sob demanda mantem o foco |
| **Injecao via MCP** | Informacoes forcadas via tool calls |

##  Proximas Etapas de Implementacao

1.  Criar estrutura basica do NeoCortex Framework
2.  Criar template white label
3.  Implementar servidor MCP com 10 ferramentas
4.  Desenvolver benchmark suite completa
5.  Implementar orquestracao de agentes efemeros
6.  Criar sistema de evolucao autonoma
7.  Documentar todos os componentes
8.  Empacotar para PyPI como `neocortex-framework`