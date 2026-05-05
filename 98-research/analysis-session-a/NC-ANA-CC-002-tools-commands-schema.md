# NC-ANA-CC-002  Claude Code Leak: Tools & Commands Schema Analysis

**Data source:** `claw-code/src/reference_data/commands_snapshot.json` (41KB, 1037 entries)  
**Data source:** `claw-code/src/reference_data/tools_snapshot.json` (37KB, 922 entries)  
**Analysis date:** 2026-04-12  
**Analyst:** T1 (DeepSeek)  
**Ticket:** NC-DS-008 / CC-001-A  

---

## 1. Schema dos Snapshots

### 1.1 commands_snapshot.json
- **Formato:** Array de objetos JSON (1037 elementos).
- **Campos por objeto:**
  - `name` (string): Nome do comando (ex: "adddir", "validation", "advisor").
  - `source_hint` (string): Caminho TypeScript original no archive (ex: "commands/adddir/adddir.tsx").
  - `responsibility` (string): Descrio fixa: "Command module mirrored from archived TypeScript path ".

### 1.2 tools_snapshot.json
- **Formato:** Array de objetos JSON (922 elementos).
- **Campos por objeto:**
  - `name` (string): Nome da tool (ex: "AgentTool", "UI", "agentMemory", "agentMemorySnapshot").
  - `source_hint` (string): Caminho TypeScript original (ex: "tools/AgentTool/AgentTool.tsx").
  - `responsibility` (string): Descrio fixa: "Tool module mirrored from archived TypeScript path ".

---

## 2. Insights sobre a Estrutura Interna da Anthropic

### 2.1 Organizao de Mdulos
- Os snapshots so **inventrios de porting**, no definies de API.
- Cada entrada representa um **mdulo TypeScript** que foi espelhado para Python no projeto `clawcode`.
- O campo `source_hint` revela a organizao de diretrios do cdigofonte original:
  - `commands/`  comandos CLI/internos.
  - `tools/`  ferramentas do agente (AgentTool, UI, agentMemory, etc.).
  - Subdiretrios por funcionalidade (AgentTool/, REPLTool/, GrepTool/).

### 2.2 Categorias de Tools (amostra)
- **AgentTool/**  UI, agentColorManager, agentDisplay, agentMemory, agentMemorySnapshot, agentToolUtils.
- **builtin/**  clawCodeGuideAgent, exploreAgent, generalPurposeAgent.
- **REPLTool/**  constants, prompt.
- **GrepTool/**  prompt.
- **SearchTool/**  prompt.
- **FileTool/**  prompt.
- **EditTool/**  prompt.
- **TaskTool/**  prompt.

### 2.3 Categorias de Commands (amostra)
- **adddir/**  adddir, validation.
- **agents/**  agents.
- **anttrace/**  anttrace.
- **autofixpr/**  autofixpr.
- **backfillsessions/**  backfillsessions.
- **branch/**  branch.
-  (mais de 1000 comandos).

---

## 3. Mapeamento para o NeoCortex

### 3.1 Correspondncias de Conceitos
| Conceito Anthropic | Equivalente NeoCortex | Observaes |
|-------------------|-----------------------|-------------|
| `agentMemory` | `NCTOOLFR021memory.py` (lobe.*) | Ambos gerenciam memria de agente, mas a implementao Anthropic  TypeScript com indexao por tpicos. |
| `agentMemorySnapshot` | `NCTOOLFR021memory.py` (cortex.*) | Snapshots do estado do agente vs nosso cortex central. |
| `commands` (CLI) | `NCTOOLFR020categories.py` (wrapper) | A Anthropic tem >1000 comandos; ns temos 10 tools consolidadas. |
| `tools` (agente) | `NCTOOLFR021030` | A Anthropic tem 922 tools espelhadas; ns temos 130 aes por domnio. |

### 3.2 Lacunas Identificadas
- **Ausncia de schema de tool definition**  os snapshots no contm parmetros, tipos, descries. Apenas metadados de porting.
- **Parity audit** (`parity_audit.py`) mostra cobertura de arquivos TypeScript  Python, no a semntica das tools.
- **A definio real da API** deve estar nos arquivos TypeScript originais (no fornecidos no leak).

---

## 4. Concluses para o NeoCortex

1. **O leak atual no expe a API interna da Anthropic**  apenas a lista de mdulos portados.
2. **A estrutura de memria** (`agentMemory`, `agentMemorySnapshot`)  similar em conceito ao nosso lobe/cortex, mas a implementao  TypeScript com indexao por tpicos (MEMORY.md).
3. **A escala da Anthropic**  maior (1000+ comandos, 900+ tools) vs nossa consolidao em 10 tools com 130 aes.
4. **Recomendao:** Investigar os arquivos TypeScript originais em `freecode/src/` para extrair os schemas reais de tool/command definition.

---

## 5. Referncias Cruzadas

- `clawcode/src/parity_audit.py`  mapeamento de diretrios TypeScript  Python.
- `clawcode/src/reference_data/archive_surface_snapshot.json`  superfcie do archive.
- `freecode/src/memdir/`  implementao real de memria (MEMORY.md, memoryTypes.ts, findRelevantMemories.ts).
- `freecode/src/tools/`  implementao das tools (agentMemory.ts, agentMemorySnapshot.ts, etc.).

---

**Status:** Anlise preliminar concluda. Prximo passo: analisar `parity_audit.py` e `freecode/src/memdir/` para detalhes de arquitetura de memria.