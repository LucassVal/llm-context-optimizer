# NC-ANA-CC-001  Claude Code Leak: Python Engine (clawcode) Analysis

**Data source:** `clawcode/src/` (183 arquivos Python + Rust)  
**Key files:** `main.py`, `runtime.py`, `query_engine.py`, `parity_audit.py`, `test_porting_workspace.py`  
**Analysis date:** 2026-04-12  
**Analyst:** T1 (DeepSeek)  
**Ticket:** NC-DS-008 / CC-001-A  

---

## 1. Viso Geral do Projeto `clawcode`

### 1.1 Objetivo
- **Porting workspace** para reescrever o Claude Code de TypeScript para Python.
- **Espelha** o snapshot do archive TypeScript (`archive/claw_code_ts_snapshot/src/`) em mdulos Python.
- **Fornece** ferramentas de auditoria (`parityaudit`), roteamento de prompts, execuo simulada de comandos/tools.

### 1.2 Arquitetura de Mdulos
```
clawcode/src/
 reference_data/          # Snapshots dos mdulos TypeScript
    commands_snapshot.json
    tools_snapshot.json
    archive_surface_snapshot.json
 commands.py              # Registry de comandos portados (PORTED_COMMANDS)
 tools.py                 # Registry de tools portadas (PORTED_TOOLS)
 runtime.py               # Runtime simulada (PortRuntime, RuntimeSession)
 query_engine.py          # Motor de queries (QueryEnginePort, TurnResult)
 parity_audit.py          # Auditoria de cobertura TypeScript  Python
 main.py                  # CLI principal (23 subcomandos)
 tests/test_porting_workspace.py
```

---

## 2. Componentes Principais

### 2.1 CLI (`main.py`)
- **23 subcomandos** para explorar o workspace de porting:
  - `summary`  renderiza resumo Markdown do workspace.
  - `manifest`  imprime o manifest atual.
  - `parityaudit`  compara Python vs TypeScript archive.
  - `commands` / `tools`  lista mdulos espelhados.
  - `route`  roteia um prompt pelo inventrio de commands/tools.
  - `bootstrap`  constri relatrio de sesso no estilo runtime.
  - `turnloop`  executa loop de turnos stateful.
  - `execcommand` / `exectool`  executa shims de command/tool por nome.
  - `remotemode`, `sshmode`, `teleportmode`  simula branching de runtime.

### 2.2 Runtime Simulada (`runtime.py`)
- **PortRuntime**  roteia prompts por tokens, coletando matches de commands/tools.
- **RuntimeSession**  contm prompt, context, setup, history, routed matches, turn result.
- **Mtodo `route_prompt`**  tokeniza o prompt, busca matches em `PORTED_COMMANDS` e `PORTED_TOOLS`.
- **Session como Markdown**  mtodo `as_markdown()` produz relatrio estruturado.

### 2.3 Query Engine (`query_engine.py`)
- **QueryEnginePort**  gerencia sesses de turnos com oramento de tokens.
- **TurnResult**  resultado de um turno (prompt, output, matched commands/tools, permission denials, usage).
- **Configurao**  `max_turns`, `max_budget_tokens`, `structured_output`.
- **Persistncia**  salva/restaura sesses via `session_store`.

### 2.4 Parity Audit (`parity_audit.py`)
- **Compara** o workspace Python com o archive TypeScript local.
- **Mapeamentos** prdefinidos de arquivos raiz (`ARCHIVE_ROOT_FILES`) e diretrios (`ARCHIVE_DIR_MAPPINGS`).
- **Clculo de cobertura**  root file coverage, directory coverage, command/tool entry ratio.
- **Resultado**  `ParityAuditResult` com mtricas e missing targets.

---

## 3. Modelos de Dados

### 3.1 PortManifest (`port_manifest.py`)
- Inventrio completo dos mdulos Python portados.

### 3.2 PortContext (`context.py`)
- Contexto de execuo (workspace, platform, python version, test command).

### 3.3 HistoryLog (`history.py`)
- Log de mensagens da sesso.

### 3.4 PermissionDenial (`models.py`)
- Registro de negaes de permisso.

### 3.5 UsageSummary (`models.py`)
- Contagem de tokens input/output.

---

## 4. Insights sobre a Engenharia da Anthropic

### 4.1 Abordagem de Porting
- **Snapshotbased**  arquivos `commands_snapshot.json` e `tools_snapshot.json` so a fonte de verdade.
- **Shims de execuo**  `execcommand` e `exectool` executam mdulos espelhados (no a implementao real).
- **Auditoria rigorosa**  `parity_audit` garante que no haja gaps de cobertura.

### 4.2 Padres de Design
- **Separao clara** entre registry (commands/tools), runtime, query engine.
- **Sesses stateful** com persistncia e histrico.
- **Roteamento por matching de tokens**  simples porm eficaz para prototype.

### 4.3 Comparao com NeoCortex
| Conceito `clawcode` | Equivalente NeoCortex | Diferenas |
|----------------------|-----------------------|------------|
| `PortRuntime` | `NCTOOLFR023orchestration.py` | NeoCortex tem orchestration mais avanada (MCP + A2A + Gateway). |
| `QueryEnginePort` | `NCTOOLFR026intelligence.py` | NeoCortex tem budget tracking por fase, no por turno. |
| `parity_audit` | `NCTOOLFR029health.py` (validation) | NeoCortex valida naming, locks, compile; Anthropic valida cobertura de porting. |
| `commands/tools registry` | `NCTOOLFR020categories.py` (wrapper) | Anthropic tem 1000+ comandos, 900+ tools; ns temos 10 tools consolidadas. |

---

## 5. Lacunas e Perguntas Abertas

### 5.1 Ausncia de Implementao Real
- `clawcode`  **apenas um workspace de porting**, no a engine de produo.
- **Shims** no executam a lgica real dos commands/tools.
- **A engine real** est em TypeScript (`freecode/src/`).

### 5.2 Onde Est a Lgica de Memria/Orchestration?
- **Memria**  implementada em `freecode/src/memdir/` (TypeScript).
- **Orchestration**  possivelmente em `freecode/src/coordinator/`, `freecode/src/services/`.
- **AutoDream**  mencionado no ticket; precisa ser buscado em `freecode/src/services/`.

### 5.3 Prximos Passos (Fase 2)
1. Analisar `freecode/src/memdir/` (j iniciado).
2. Extrair schemas de `agentMemory.ts`, `agentMemorySnapshot.ts`.
3. Investigar `freecode/src/coordinator/` e `freecode/src/services/`.
4. Buscar triggers do `autoDream` (3 portas).

---

## 6. Referncias

- `clawcode/src/main.py` (213 linhas)  entrypoint CLI.
- `clawcode/src/runtime.py` (192 linhas)  runtime simulada.
- `clawcode/src/query_engine.py` (193 linhas)  motor de queries.
- `clawcode/src/parity_audit.py` (138 linhas)  auditoria de cobertura.
- `clawcode/src/tests/test_porting_workspace.py` (10.9KB)  testes de porting.

---

**Status:** Anlise do engine Python concluda. O foco agora deve migrar para a implementao TypeScript real (`freecode/src/`).