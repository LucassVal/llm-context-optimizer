# NC-PROMPT-FR-001 — NeoCortex Master Context Prompt (v2)

> **Propósito:** Prompt padrão para qualquer sessão de trabalho com qualquer AI (Antigravity, OpenCode, Cursor).
> Cole no início do chat **ou** adicione como `.agents/AGENTS.md` para ingestão automática.
> **Versão:** 2.0 | **Data:** 2026-04-11

---

## 🧠 Leia antes de qualquer ação

Você opera no projeto **NeoCortex MCP Framework**:
```
C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\
```

**Objetivo central do NeoCortex:**
> Reduzir custo de API e latência reutilizando memória contextual local via servidor MCP ativo (`neocortex.mcp.server`), substituindo tokens caros de cloud por tokens baratos de modelos locais (Qwen 1.5B/3B).

**Antes de qualquer trabalho, consulte obrigatoriamente:**

| Prioridade | Arquivo | Propósito |
| :---: | :--- | :--- |
| 1 | `NC-NAM-FR-001-naming-convention.md` | SSOT: Mapa do projeto + Nomenclatura + Changelog |
| 2 | `NC-TODO-FR-001-project-roadmap-consolidated.md` | Roadmap único e oficial (todos os tickets) |
| 3 | `NC-APP-FR-001-technical-appendix.md` | Detalhes técnicos: tools, libs, LLMs, mecanismos |
| 4 | Lobo do contexto ativo (`neocortex_lobes.get`) | Estado atual persistido nos lobos |

---

## 📂 Estrutura de Pastas Raiz

```
TURBOQUANT_V42/
├── 01_neocortex_framework/       ← NÚCLEO (único lugar para edição de código)
├── 02_memory_lobes/              ← Dados vivos de persistência (NÃO editar)
├── 03_white_label_templates/     ← Templates para instâncias white-label
├── 04_user_docs/                 ← Documentos de referência do usuário
├── 05_examples/                  ← Exemplos e benchmarks
├── .agents/
│   ├── rules/NC-RULE-001-workspace-standards.mdc   ← REGRAS ATIVAS (MDC)
│   └── workflows/NC-WF-001-workspace-routine.md    ← FLUXO PADRÃO
├── .gitignore
└── NC-PROMPT-FR-001-master-context.md               ← ESTE ARQUIVO
```

### Dentro de `01_neocortex_framework/`

```
neocortex/
├── mcp/
│   ├── server.py          ← Host principal WebSocket :8765
│   ├── sub_server.py      ← Orquestrador de agentes isolados
│   └── tools/             ← NC-TOOL-FR-000 a NC-TOOL-FR-020
├── core/                  ← Serviços (LedgerService, LobeService, PulseScheduler...)
└── infra/                 ← Repositórios e stores (LedgerStore, HotCache, MetricsStore)
DIR-DOC-FR-001-docs-main/  ← Documentação e SSOT
DIR-CFG-FR-001-config-main/
scripts/
└── NC-SCR-FR-001-populate-lobes-ssot.py  ← Povoa lobos com SSOT
```

---

## 🧠 Arquitetura de Lobos (Memória Persistente)

Os **Lobos** são a memória de longo prazo do NeoCortex. Cada lobo é um arquivo `.mdc` que o servidor indexa via FTS5 e disponibiliza para busca semântica sem nova chamada de API.

### Lobos Existentes

| Lobo (`.mdc`) | Papel do Agente | Conteúdo |
| :--- | :--- | :--- |
| `NC-LBE-FR-ARCHITECTURE-001` | Arquitetura | Roadmap, Naming Convention, Apêndice Técnico |
| `NC-LBE-FR-DEVELOPMENT-001` | Development | Auditorias, alinhamentos, MCP docs |
| `NC-LBE-FR-SECURITY-001` | Guardian | Checklist de sanitização, atomic locks |
| `NC-LBE-FR-PROFILES-001` | Profiles | Schemas de developer/team |
| `NC-LBE-FR-WHITELABEL-001` | Indexer | Templates white-label |
| `NC-LBE-FR-BENCHMARKS-001` | Backend Dev | Resultados de benchmark |
| `lobes/courier/` | Courier | Ambiente isolado para Qwen 1.5B |
| `lobes/engineer/` | Engineer | Ambiente isolado para Qwen 3B |
| `lobes/guardian/` | Guardian | Ambiente isolado para validação |

### Como Povoar / Atualizar Lobos

```bash
cd 01_neocortex_framework

# Ver o que seria feito (sem gravar):
python scripts/NC-SCR-FR-001-populate-lobes-ssot.py --dry-run

# Gravar (popula/atualiza todos os lobos mapeados):
python scripts/NC-SCR-FR-001-populate-lobes-ssot.py
```

### Como Buscar nos Lobos (via MCP)

```
# Busca textual em todos os lobos indexados:
neocortex_lobes.search(query="AGENT-203 mentor_step_0")

# Busca avançada com filtros:
neocortex_search.advanced(query="fallback_chain", tags=["architecture"])

# Ver lobo específico:
neocortex_lobes.get(lobe_name="NC-LBE-FR-ARCHITECTURE-001")
```

---

## 🏷️ Regras de Nomenclatura (NUNCA violar)

**Arquivo:** `NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext`
**Pasta:**   `DIR-<TIPO>-<SIGLA>-<NUM>-<desc>/`

| TIPO | Uso |
| :--- | :--- |
| `TOOL` | Ferramenta MCP em `/mcp/tools/` |
| `SCR` | Scripts em `/scripts/` |
| `DOC` | Documentação em `/docs-main/` |
| `TODO` | Roadmaps e tickets |
| `APP` | Apêndices técnicos |
| `LBE` | Lobos de memória (`.mdc`) |
| `PRF` | Profiles de usuário/agente |
| `ARC` | Obsoletos → mover para `DIR-ARC-FR` |
| `BAK` | Backups → mover para `DIR-BAK-FR` |

---

## 🚀 Iniciar o Servidor MCP

```powershell
# Batch (drag & drop):
start_neocortex_mcp.bat

# PowerShell:
.\start_neocortex_mcp.ps1

# Manual:
cd 01_neocortex_framework
python -m neocortex.mcp.server --transport websocket --host 127.0.0.1 --port 8765
```

**Verificar se está ativo:** `ws://127.0.0.1:8765`
**Config Antigravity MCP:** `C:\Users\Lucas Valério\.gemini\antigravity\mcp_config.json`
- `PYTHONPATH`: `C:/Users/Lucas Valério/Desktop/TURBOQUANT_V42/01_neocortex_framework`

---

## 🤖 Tiers de LLM e Roteamento

| Tier | Modelo | Backend | Uso |
| :--- | :--- | :--- | :--- |
| T0 (você) | `deepseek-reasoner` | DeepSeek API | Raciocínio, orquestração, auditorias |
| Courier | `qwen2.5-coder:1.5b` | Ollama local | Tarefas braçais 24/7, indexação |
| Engineer | `qwen2.5-coder:3b` | Ollama local | Geração de código, testes |
| Fallback | Chain: ollama → deepseek-chat → deepseek-reasoner | LLMFactory | Auto |

**Princípio de economia:** Toda tarefa repetitiva ou de indexação deve ir para o Courier (Qwen local). O T0 orquestra, não executa trabalho bruto.

---

## 🎯 Tickets Críticos Pendentes (Desbloqueadores)

| Ticket | Descrição | Impacto |
| :--- | :--- | :--- |
| **AGENT-203** | `mentor_step_0()` em `sub_server.py` | Sem isso, agentes locais allucinam |
| **ORCH-301** | `spawn`, `stop`, `send_task` robustos | Sem isso, T0 não orquestra agentes |
| **ORCH-302** | `execute` integrado com `LLMBackend` | Sem isso, agente não executa tarefas |
| **SEC-401** | `neocortex_guardian` | Auditoria pós-execução |
| **SEC-403** | `limits.*` no `config.yaml` de cada agente | Rate limiting de tokens/custo |

---

## 🛑 Proibições Absolutas

1. **Nunca deletar arquivos** — mova para `DIR-ARC-FR-001-archive-main/`
2. **Nunca criar arquivo sem nome no padrão NC-** — consulte o SSOT `NC-NAM-FR-001`
3. **Nunca hardcodar paths** — use `ConfigProvider` / `get_config()`
4. **Nunca fazer import direto de módulo com hífen** — use `importlib.import_module()`
5. **Nunca editar fora de `01_neocortex_framework/`** sem autorização explícita
6. **Nunca commitar** `*.db`, `*.wal`, `__pycache__/`, `.venv/`, `.neocortex/metrics/`

---

## ✅ Checklist de Início de Sessão

- [ ] Servidor MCP ativo em `ws://127.0.0.1:8765`?
- [ ] Lobos populados com SSOT atual? (`python scripts/NC-SCR-FR-001-populate-lobes-ssot.py`)
- [ ] Li o `NC-TODO-FR-001` (roadmap) para saber o que está aberto?
- [ ] Li o `NC-APP-FR-001` (apêndice técnico) para detalhes de implementação?
- [ ] Novo arquivo segue a convenção `NC-<TIPO>-<SIGLA>-<NUM>`?
- [ ] Cataloguei o novo arquivo na tabela SSOT do `NC-NAM-FR-001`?
