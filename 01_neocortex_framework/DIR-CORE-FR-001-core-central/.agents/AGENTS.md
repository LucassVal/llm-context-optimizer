# 🤖 AGENTS.md – NeoCortex Integration Guide for OpenCode

> **Single Source of Truth** for how OpenCode should interact with the NeoCortex framework.

---

## 🧠 Core Philosophy

OpenCode **is** the primary agent (`$T0`) that orchestrates the NeoCortex framework. You must:

1. **Always apply** the rules from `$ctx` (`.agents/rules/00-cortex.mdc`)
2. **Maintain state** in `$ldg` (`memory_neocortex_framework.json`)
3. **Enforce** STEP 0, Compact Encoding, Ubiquitous Language, and Regression Buffer

---

## 📦 Project Structure (Aliases)

| Alias | Path | Description |
|-------|------|-------------|
| `$ctx` | `neocortex_framework/.agents/rules/NC-CTX-FR-001-cortex-central.mdc` | Central cortex rules |
| `$ldg` | `neocortex_framework/NC-LED-FR-001-framework-ledger.json` | State ledger (JSON) |
| `@neocortex` | `neocortex_framework/` | Core framework directory |
| `@white` | `white_label/` | White‑label templates |
| `@ref` | `neocortex_framework/DIR-REF-FR-001-reference-main/` | Extracted knowledge base |
| `@ex` | `examples/` | Example projects and benchmarks |
| `@tpl` | `neocortex_framework/DIR-TMP-FR-001-templates-main/` | Template files |
| `$mcp` | `neocortex_framework/DIR-MCP-FR-001-mcp-server/NC-MCP-FR-001-mcp-server.py` | MCP server |
| `$roadmap` | `neocortex_framework/NC-TODO-FR-001-project-roadmap.md` | Project roadmap |

---

## ⚙️ Commands (OpenCode Internal)

| Alias | Command | Description |
|-------|---------|-------------|
| `!init-neocortex` | Read `$ctx` and `$ldg` | Load NeoCortex framework into session |
| `!step0` | Perform regression check | Mandatory before any action |
| `!update-ldg` | Edit `$ldg` with minimal diffs | Update state after each milestone |
| `!backup-ldg` | Copy `$ldg` to `backup/` with timestamp | Create backup |
| `!compact` | If hot_context > 5, move oldest to cold_storage | Context compaction |

---

## 🔁 Workflows (OpenCode‑Specific)

### Starting a NeoCortex Session
1. Run `!init-neocortex`
2. Execute **STEP 0** (`!step0`)
3. Report current checkpoint + next steps from `$ctx`
4. Await user confirmation

### Implementing a Feature
1. **STEP 0** (mandatory)
2. **Explore** – read‑only mapping of relevant files
3. **Plan** – `<thinking>` scratchpad, propose 2‑3 points
4. **Act** – minimal diffs, JIT references, compact encoding
5. **Observe** – validate with lint/test if available
6. **Persist** – update `$ldg`, `!backup-ldg`, update `$ctx` checkpoint

### Wrapping Up a Session
**Triggers:** “wrap up”, “that's it for today”, task completed
1. Update `$ctx` Current State + next steps
2. Move action_queue items (in_progress → completed)
3. Add entry to `$ldg` session_timeline
4. Compact hot_context if >5 entries
5. `!backup-ldg`
6. Update CHANGELOG (one line)
7. Message: “Session saved. Next resumes at [CHECKPOINT].”

---

## 🚫 Negative Constraints (OpenCode)

- ❌ **Never** write full paths when an alias exists
- ❌ **Never** modify `$ctx` or `$ldg` without reading first
- ❌ **Never** skip STEP 0 regression check
- ❌ **Never** use synonyms from the Ubiquitous Language
- ❌ **Never** rewrite entire files – minimal diffs only

---

## 📖 Ubiquitous Language (Enforced)

| Term | Definition | ❌ Prohibited |
|------|------------|---------------|
| Cortex | Central rule set (.mdc file) | rules, instructions, config |
| Lobe | Phase/module‑specific context | module, phase, context |
| Ledger | JSON state file | state, memory, database |
| STEP 0 | Mandatory regression check | pre‑check, validation |
| Compact Encoding | Symbolic references ($ @ ! ?) | aliases, shortcuts, symbols |
| Regression Buffer | History of failures to avoid repetition | error log, mistake list |

---

## 🧪 Example Session

```
User: “Add a new validation rule to the auth module”

OpenCode:
1. !init-neocortex
2. !step0 → “No regression warnings. Goal: add validation rule to auth module.”
3. Explore – reads $ctx, @neocortex structure, locates auth‑related files
4. Plan – <thinking>…</thinking> → “Proposal: 1) Update $auth‑svc, 2) Add ?validation‑schema, 3) Extend tests. Await OK.”
5. User: “OK”
6. Act – applies minimal diffs using $auth‑svc alias
7. Observe – runs !lint (if defined)
8. Persist – updates $ldg, !backup‑ldg, updates $ctx checkpoint
```

---

## 🔗 Integration with MCP (READY)

✅ **MCP Server está pronto e funcional!**

**Como conectar:**

1. **Modo WebSocket (Recomendado)**:
   ```bash
   # Na área de trabalho, execute:
   .\start_neocortex_mcp.ps1
   # Ou: .\start_neocortex_mcp.bat
   ```
   - Servidor: `ws://localhost:8765`
   - 22 ferramentas, 73+ ações
   - Métricas automáticas (DuckDB + relatórios)

2. **Modo stdio (IDE integration)**:
   - Configure no Antigravity: `python -m neocortex.mcp.server --transport stdio`
   - Config exemplo: `antigravity_neocortex_config.json`

**Ferramentas principais para OpenCode:**

1. `neocortex_cortex` - Query `$ctx` sections (get_full, get_section, get_aliases)
2. `neocortex_ledger` - Read/update `$ldg` state (read, write, update_section)
3. `neocortex_report` - Relatórios de métricas (daily_summary, cost_report, agent_report)
4. `neocortex_subserver` - Orquestração de agentes (spawn, stop, list, send_task)
5. `neocortex_task` - Execução em sub-servers (execute com mentor mode)
6. `neocortex_checkpoint` - Checkpoints e restauração (get_current, create, restore)
7. `neocortex_config` - Configuração do sistema (get, set, validate)
8. `neocortex_search` - Busca semântica no conhecimento (semantic, keyword)
9. `neocortex_agent` - Execução de agentes LLM (execute com backend override)
10. `neocortex_pulse` - Agendamento automático (status, force_consolidation)

**Exemplo de uso no OpenCode:**
```python
# Query cortex
ctx_data = neocortex_cortex(action="get_full")

# Update ledger
neocortex_ledger(action="update_section", section="session_timeline", data={...})

# Generate report
report = neocortex_report(action="generate_daily_summary")
```

---

## 📈 Metrics to Track

| Metric | How to Measure |
|--------|----------------|
| Token savings | Compare stateless vs NeoCortex token counts |
| Context drift errors | Count of times STEP 0 prevented regression |
| Rule adherence | % of actions that follow compact encoding & vocabulary |
| Session continuity | Ability to resume exactly from last checkpoint |

---

**Version:** NeoCortex v4.2‑Cortex (OpenCode Integration)  
**Date:** 2026‑04‑09  
**Maintainer:** OpenCode (T0 cortex executor)