# TURBOQUANT MEMORY PROMPT v4.2-CORTEX
## Industrial Context Management System for AI Agents
### Fractal Architecture · Compact Encoding · STEP 0 · 30+ Global Improvements

> **White-Label Prompt** — replace `[PROJECT_NAME]` and placeholders with your project.
> Based on global research: MemGPT, ReAct, Acon Framework, Cursor Rules, Anthropic CLAUDE.md,
> Context Engineering (Google DeepMind), LangChain Agent Patterns and academic literature 2024-2026.

---

## PRE-CONVERSATION INSTRUCTION — TURBOQUANT CORTEX

```
[BEFORE STARTING ANY TASK - COPY AND PASTE THIS BLOCK]

INIT TURBOQUANT FOR: [PROJECT_NAME]
CONTEXT: [BRIEF_DESCRIPTION_OF_CURRENT_CONTEXT]
OBJECTIVE: [WHAT_YOU_WANT_TO_ACHIEVE_THIS_SESSION]
PREVIOUS_MEMORY: [CORTEX AND ACTIVE LOBE OR "None"]
MODE: single_agent
```

---

## THE 30+ IMPLEMENTED PRINCIPLES (Improvement Index)

| # | Name | Source | Status |
|---|---|---|---|
| 01 | STEP 0 Regression Check | TurboQuant v4.1 | ✅ Core |
| 02 | JSON ↔ MDC Separation | TurboQuant v4.1 | ✅ Core |
| 03 | Mandatory Compact Encoding | TurboQuant v4.1 | ✅ Core |
| 04 | Lobe by Semantic Intention | TurboQuant v4.1 | ✅ Core |
| 05 | Session Wrap-up Workflow | TurboQuant v4.1 | ✅ Core |
| 06 | Automatic Backup | TurboQuant v4.1 | ✅ Core |
| 07 | ReAct Loop (Thought-Action-Observation) | DeepMind/Yao et al. | 🆕 v4.2 |
| 08 | Structured Scratchpad (isolated reasoning) | ReAct 2026 | 🆕 v4.2 |
| 09 | Plan-and-Execute before acting | Agno/LangChain | 🆕 v4.2 |
| 10 | Rule Modularity (< 500 lines/file) | Cursor Rules | 🆕 v4.2 |
| 11 | Hierarchy Global → Project → Local | Anthropic CLAUDE.md | 🆕 v4.2 |
| 12 | JIT References (Just-In-Time) | Cursor/Anthropic | 🆕 v4.2 |
| 13 | Few-Shot Examples in workflows | Anthropic | 🆕 v4.2 |
| 14 | Hierarchical Memory RAM/Disk (MemGPT) | MemGPT | 🆕 v4.2 |
| 15 | Cognitive Triage (future value of info) | MemGPT | 🆕 v4.2 |
| 16 | Context Compaction + Summarization | Acon Framework | 🆕 v4.2 |
| 17 | "Scale by Subtraction" (less is more) | Augment Code | 🆕 v4.2 |
| 18 | Token Budget Monitor (active metric) | OpenAI/Augment | 🆕 v4.2 |
| 19 | Scoped Tasking (explicit scope) | Agent Drift Prevention | 🆕 v4.2 |
| 20 | Goal Persistence (goal reinforcement) | Context Rot Research | 🆕 v4.2 |
| 21 | Explore-Plan-Act (read-only before write) | Codegen.com | 🆕 v4.2 |
| 22 | Self-Validation (lint + test before finish) | Cursor/Anthropic | 🆕 v4.2 |
| 23 | Negative Constraints (what NOT to do) | Anthropic | 🆕 v4.2 |
| 24 | Role-Based Namespacing (scope by role) | Galileo AI | 🆕 v4.2 |
| 25 | Episodic vs Semantic Memory (MemGPT layers) | MemGPT/MemGPT2 | 🆕 v4.2 |
| 26 | Context Pollution Prevention (isolated sub-agents) | LangChain | 🆕 v4.2 |
| 27 | Progressive Disclosure (on-demand info) | Anthropic/Cursor | 🆕 v4.2 |
| 28 | Rule Version Control (.agents in Git) | Cursor Best Practices | 🆕 v4.2 |
| 29 | Structured Audit Trail (WHO did WHAT) | Observability Research | 🆕 v4.2 |
| 30 | Reset Discipline (short sessions + clean state) | Context Rot Research | 🆕 v4.2 |
| 31 | Vocabulary as Law (Ubiquitous Language) | DDD/Evans | ✅ Reinforced |
| 32 | Atomic Locks SSOT | TurboQuant | ✅ Reinforced |
| 33 | XML Tags for critical sections | Anthropic | 🆕 v4.2 |
| 34 | Learning Feedback Loop (rule-from-mistake) | Cursor Best Practices | 🆕 v4.2 |
| 35 | Cortex CHANGELOG (last N changes) | DevOps Best Practices | 🆕 v4.2 |

---

## v4.2-CORTEX ARCHITECTURE (OVERVIEW)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TURBOQUANT v4.2-CORTEX                          │
│                                                                     │
│  ┌──────────────────┐    ┌─────────────────────────────────────┐   │
│  │   LEDGER (JSON)  │    │     INSTRUCTIONS (.mdc alwaysApply) │   │
│  │                  │    │                                     │   │
│  │ · Checkpoints    │    │ · STEP 0 Regression Check           │   │
│  │ · Metrics        │    │ · Compact Encoding (mandatory)      │   │
│  │ · Action Queue   │    │ · Ubiquitous Vocabulary             │   │
│  │ · Session Log    │    │ · Workflows (ReAct + Plan-Exec)     │   │
│  │ · Atomic Locks   │    │ · Structured Scratchpad             │   │
│  └──────────────────┘    └─────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    LOBES (by glob OR semantics)                │ │
│  │  phase-N.mdc: checkpoint tree · local regression · encoding   │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │            HIERARCHICAL MEMORY (MemGPT-inspired)               │ │
│  │  HOT (5 interactions) → COLD (archival) → VECTOR (future)     │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## SYSTEM COMMANDS — 6 LAYERS + 30 IMPROVEMENTS

```
[FULL PROTOCOL v4.2]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 — REGRESSION + GOAL CHECK  (Improvement #01, #20)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEFORE ANY ACTION:
   1. Read Regression Buffer from Cortex AND Active Lobe
   2. If task bears resemblance to previous error → WARN before proceeding
   3. Reaffirm session GOAL explicitly (anti-drift)
   4. Confirm scope: "I will work on [FILE/MODULE] only" (Improvement #19)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — EXPLORE (read-only)  (Improvement #21)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEFORE WRITING ANY CODE:
   1. Map relevant files (without modifying anything)
   2. Identify 1st and 2nd degree dependencies
   3. Check atomic_locks (SSOT — do not modify)
   4. Propose plan in 2-3 points and AWAIT CONFIRMATION

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — PLAN (explicit reasoning)  (Improvement #07, #08, #09)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USE INTERNAL SCRATCHPAD (ReAct):
   <thinking>
     Thought: [What I know and what I need]
     Plan: [Sequence of steps]
     Risks: [What could go wrong]
     Regression: [Does any pattern from the buffer apply?]
   </thinking>
   → Visible result to user: reasoning conclusion only

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — ACT (implementation)  (Improvement #12, #13, #23)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTION RULES:
   · Access information only when needed — JIT (Just-In-Time) (#12)
   · Minimal diffs — do not rewrite entire files
   · Show concrete example before implementing (#13)
   · Respect NEGATIVE constraints (what NOT to do) (#23)
   · Use ONLY terms from the Ubiquitous Vocabulary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4 — OBSERVE + VALIDATE  (Improvement #22, #07)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEFORE DECLARING TASK COMPLETED:
   · Run !lint and !test
   · Verify if output resolves the original goal (anti-drift #20)
   · If it fails: return to STEP 2 with a new hypothesis (ReAct loop)
   · Document result in the Audit Trail (#29)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 5 — PERSIST (memory + cleanup)  (Improvement #05, #06, #16, #30)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHEN FINISHING ANY TASK:
   1. Update "Current State" in .mdc (phase, checkpoint, next steps)
   2. Mark checkpoint in active lobe
   3. Update session_timeline in JSON
   4. Move action_queue: in_progress → completed/pending
   5. Apply Context Compaction if hot_context > 5 (#16)
   6. Run !backup (#06)
   7. Update cortex CHANGELOG (#35)
   8. Advise: "Session saved. Next session resumes at [CHECKPOINT]."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTEXT AND TOKEN MANAGEMENT  (Improvements #14, #15, #17, #18, #25)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HIERARCHICAL MEMORY (MemGPT-inspired):
   HOT  (RAM)   → hot_context: last 5 active interactions
   COLD (Disk)  → cold_storage: access via consult_cold_storage
   ARCHIVAL     → archive/: completed lobes + auto-summary

TOKEN BUDGET:
   · JSON > 6000 tokens → WARNING: run pruning
   · JSON > 8000 tokens → BLOCK: pruning mandatory before continuing
   · COGNITIVE TRIAGE: when moving to cold, evaluate "future value" of info
   · SCALE BY SUBTRACTION: periodically remove obsolete rules
   · Active metric: report token estimate when starting a long session

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY ENCODING  (Improvement #03)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROHIBITED to write full paths when an alias is defined.
✅ "$alias section X" | ❌ "full/path/file.txt section X"
Automatically create new alias if reference repeats > 2x.

CONVENTION:
   $ = file         @ = directory
   ! = command      ? = code pattern

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LOBES — SEMANTIC ACTIVATION  (Improvement #04, #24)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Lobes load by GLOB (open file) OR SEMANTIC INTENTION.
If the topic mentions the lobe's domain → apply its patterns.
Each lobe has an isolated namespace to avoid context pollution (#26).
```

---

## JSON ANTI-HALLUCINATION PROTOCOL

```
WHEN UPDATING THE MEMORY FILE:
  1. Read current JSON BEFORE writing (never infer structure)
  2. Use only allowed schema keys
  3. No trailing commas, no duplicate keys
  4. Minimal diffs — never rewrite the whole file
  5. Validate JSON before saving
  6. Log structural changes in cortex CHANGELOG
```

---

## VALIDATION SCHEMA — ALLOWED KEYS v4.2

```json
{
  "$schema": "turboquant-v4.2-cortex",
  "separation_rule": "JSON = LEDGER. MDC = INSTRUCTIONS. Never duplicate.",
  "required_top_level_keys": [
    "turboquant_version", "system_type", "architecture",
    "system_constraints", "granular_state_management",
    "pointers_and_hashes", "hierarchical_validation",
    "memory_temperature", "ubiquitous_language",
    "agent_session", "project_identity", "session_timeline",
    "problem_solution_map", "knowledge_base",
    "action_queue", "validation_checkpoints",
    "session_metrics", "memory_cortex"
  ],
  "new_in_v4.2": [
    "session_metrics.token_budget_warnings",
    "hierarchical_validation.audit_trail",
    "hierarchical_validation.changelog",
    "memory_temperature.compaction_log",
    "agent_session.scratchpad_enabled"
  ],
  "max_json_size_tokens": 8000,
  "warning_threshold_tokens": 6000,
  "pruning_trigger": "> 20 entries in session_timeline → move to history_archive_[DATE].json",
  "lobe_archiving": "Lobe completed → archive/ with auto-summary + timestamp",
  "backup_rule": "!backup mandatory when wrapping up any session",
  "changelog_rule": "Register last 5 cortex structural changes in .agents/CHANGELOG.md"
}
```

---

## TURBOQUANT CORTEX JSON STRUCTURE v4.2 (MAIN TEMPLATE)

```json
{
  "turboquant_version": "4.2-cortex",
  "system_type": "[erp | web | api | desktop | cli]",
  "architecture": "6_layer_conceptual_fractal",
  "system_constraints": {
    "max_context_depth": 3,
    "enforce_ssot": true,
    "token_optimization": true,
    "hot_context_limit": 5,
    "context_pruning_days": 3,
    "max_json_size_tokens": 8000,
    "warning_threshold_tokens": 6000,
    "dependency_graph_depth": "1st_and_2nd_degree_only",
    "scratchpad_enabled": true,
    "react_loop_enabled": true
  },
  "granular_state_management": {
    "atomic_locks": {
      "_comment": "SSOT. Do not modify without explicit unlock.",
      "locked_modules": []
    },
    "dependency_graph": {
      "_comment": "1st and 2nd degree only. Never serialize full graph.",
      "active_module": "",
      "first_degree": [],
      "second_degree": []
    },
    "feature_flag_sync": { "draft": [], "test": [], "prod": [] },
    "state_transitions": [],
    "session_scope": {
      "_comment": "Scoped Tasking: explicit scope for anti-drift.",
      "current_focus_module": "",
      "allowed_write_paths": [],
      "readonly_paths": []
    }
  },
  "pointers_and_hashes": {
    "source_map_ref": {
      "_comment": "Aliases MANDATORY. Prohibited to write full path.",
      "aliases": {}
    },
    "logic_checksums": { "_comment": "Hash of critical files.", "files": {} },
    "context_pruning": {
      "last_pruning": "",
      "pruned_sessions": [],
      "compaction_log": []
    }
  },
  "hierarchical_validation": {
    "blueprint_compliance": { "status": "ok | warning | violation", "last_checked": "" },
    "gatekeeper_metrics": { "current_checkpoint": "", "pass_criteria": [], "last_result": "" },
    "regression_buffer": {
      "_comment": "STEP 0: ALWAYS CONSULT. Do not repeat failures.",
      "failed_attempts": []
    },
    "checkpoint_validation": [],
    "audit_trail": {
      "_comment": "Who did what and when. Automatically maintained.",
      "entries": []
    },
    "changelog": {
      "_comment": "Last 5 structural changes of the cortex.",
      "entries": []
    }
  },
  "memory_temperature": {
    "hot_context": {
      "_comment": "RAM: max 5 interactions. Excess → cold_storage.",
      "interactions": []
    },
    "cold_storage": {
      "_comment": "Disk: access via consult_cold_storage.",
      "archived_interactions": []
    },
    "context_switching": { "active_module": "", "switch_log": [] },
    "compaction_log": {
      "_comment": "Log of executed context compactions.",
      "entries": []
    }
  },
  "ubiquitous_language": {
    "domain_vocabulary": {
      "_comment": "Synonyms prohibited. ALWAYS employ the official term.",
      "terms": {}
    },
    "term_consistency": { "last_validated": "", "violations": [] },
    "vocabulary_checksum": "",
    "compact_encoding": {
      "_comment": "$ file | @ dir | ! cmd | ? pattern. MANDATORY USE.",
      "files": {},
      "directories": {},
      "commands": {},
      "patterns": {}
    }
  },
  "agent_session": {
    "model_id": "[model_name]",
    "session_start": "",
    "environment": "[opencode | cursor | antigravity | api]",
    "platform": "[win32 | linux | darwin]",
    "update_mechanism": "ai_self_write",
    "mode": "single_agent",
    "scratchpad_enabled": true,
    "token_budget_warnings": []
  },
  "project_identity": {
    "name": "[PROJECT_NAME]",
    "path": "[ABSOLUTE_PATH]",
    "type": "[web | api | desktop | cli | erp]",
    "tech_stack": [],
    "created": "",
    "last_modified": ""
  },
  "session_timeline": [],
  "problem_solution_map": {
    "active_problems": [],
    "resolved_problems": [],
    "solution_patterns": [],
    "workarounds": [],
    "failed_attempts": []
  },
  "knowledge_base": {
    "project_structure": {},
    "dependencies": {},
    "configurations": {},
    "constraints": {
      "negative_constraints": []
    },
    "conventions": {},
    "patterns": {},
    "agent_guidance": {
      "commands": { "build": "", "test_single": "", "test_all": "", "lint": "", "typecheck": "", "dev_server": "" },
      "architecture_notes": [],
      "workflow_order": [],
      "quirks_and_gotchas": [],
      "testing_conventions": [],
      "entrypoints": {},
      "monorepo_boundaries": {},
      "few_shot_examples": []
    }
  },
  "action_queue": {
    "pending": [], "in_progress": [], "completed": [], "blocked": []
  },
  "validation_checkpoints": [],
  "session_metrics": {
    "total_interactions": 0,
    "files_created": 0,
    "files_modified": 0,
    "problems_solved": 0,
    "decisions_made": 0,
    "context_prunes_executed": 0,
    "compactions_executed": 0,
    "protocol_violations": 0,
    "token_budget_warnings": 0
  },
  "memory_cortex": {
    "_comment": "Fractal architecture. Lobes by glob OR semantic intent.",
    "active_lobes": [],
    "synapses": { "current_context": { "lobe_id": "", "checkpoint_id": "" } },
    "global_checkpoint_index": { "checkpoints": [] },
    "cortex_vocabulary": { "core_modules": [] }
  }
}
```

---

## FULL CORTEX `.mdc` TEMPLATE (v4.2)

```markdown
---
alwaysApply: true
description: "Central Cortex – universal rules. TurboQuant v4.2-Cortex."
---

# 🧠 Cortex: [PROJECT_NAME]
<!-- v4.2-Cortex | INSTRUCTIONS file — do not duplicate data from JSON -->

## 🚨 STEP 0 — REGRESSION + GOAL CHECK (NON-NEGOTIABLE)
> 1. Read Regression Buffer (cortex + active lobe)
> 2. If similar to an error → ADVISE before proceeding  
> 3. Reaffirm goal: "[SESSION_GOAL]"
> 4. Confirm scope: "I will work on [MODULE/FILE] only"

## 🧪 SCRATCHPAD (Isolated Reasoning — ReAct)
> Use `<thinking>` internally before any complex response.
> Scratchpad content DOES NOT appear in the final response.
> Structure: Thought → Plan → Risks → Regression Check

## 📍 Workspace Map
| File/Dir | Alias | Purpose |
| :--- | :--- | :--- |
| `[PATH]` | `$alias` | [Description] |

## ⚡ Compact Encoding (MANDATORY — NO EXCEPTIONS)
> ✅ `$alias` | ❌ `full/path.ext`
> Automatically create alias if reference repeats > 2×

| $ = file | @ = directory | ! = command | ? = pattern |
| :--- | :--- | :--- | :--- |
| `$alias` | `@dir` | `!cmd` | `?pattern` |

## ⚙️ Stack & Commands
| Alias | Real Command | Description |
| :--- | :--- | :--- |
| `!build` | `[CMD]` | Build |
| `!test` | `[CMD]` | Tests |
| `!lint` | `[CMD]` | Lint |
| `!backup` | `[CMD_BACKUP_WITH_TIMESTAMP]` | Backup |

## 📖 Ubiquitous Language (NO SYNONYMS)
| Term | Definition | ❌ Prohibited |
| :--- | :--- | :--- |
| `[TERM]` | [DEF] | `[SYN1]` |

## 🚫 Negative Constraints (What to NEVER do)
- ❌ Rewrite entire files — minimal diffs only
- ❌ Modify $SSOT_FILE without explicit unlock
- ❌ Use synonyms from the ubiquitous language
- ❌ Write full path if there is an alias
- ❌ [PROJECT_SPECIFIC_CONSTRAINT]

## 🔒 Atomic Locks (SSOT — Do Not Modify)
- `$alias` — Reason: [EXPLANATION]

## 🗺️ Workflows

### 🔁 Active Lobe (Semantic)
> Even without an open file: if the subject mentions [LOBE_DOMAIN],
> apply patterns from the lobe `[FILE].mdc`.

### 🔍 Workflow: Explore-Plan-Act (For complex features)
1. **STEP 0** ← MANDATORY
2. **Explore** (read-only): map files, identify deps
3. **Plan**: `<thinking>` + propose plan in 2-3 points → AWAIT OK
4. **Act**: execute in minimal diffs
5. **Observe**: `!lint` + `!test` → validate against goal
6. **Persist**: update state + `!backup`

**Example (few-shot):**
> User: "Add validation to /login endpoint"
> AI: Explore → reads auth.ts + validators/ → Plan: [1. Add Zod schema, 2. Update handler, 3. Add test] → Awaits OK → Act

### 🐛 Workflow: Debug
1. **STEP 0** ← MANDATORY
2. Reproduce → Single Hypothesis → Confirm → Apply → Document in Regression Buffer

### 📈 Workflow: [SPECIFIC_NAME]
**Triggers:** "[WORD]", "[WORD]"
1. **STEP 0** ← MANDATORY
2. [STEPS]
N. Update state + `!backup`

### 🏁 Workflow: Wrap Up Session (ALWAYS when finishing)
**Triggers:** "wrap up", "see you later", "that's it for today", task completed
1. Update Current State + next steps
2. Check off checkpoint in active lobe
3. Add session_timeline in JSON
4. action_queue: in_progress → completed/pending
5. Compact hot_context if > 5 entries
6. `!backup`
7. Update CHANGELOG: record 1 line of structural change
8. "Session saved. Next resumes at [CHECKPOINT]."

## 📉 Regression Buffer (CHECK IN STEP 0)
| Error | Failed Attempt | Lesson |
| :--- | :--- | :--- |
| [ERROR] | [ATTEMPT] | [LESSON] |

## 🎯 Current State (Checkpoint)
<!-- UPDATE in Wrap Up Session Workflow -->
- **Version:** TurboQuant v4.2-Cortex
- **Active Phase:** [PHASE]
- **Active Lobe:** `.agents/rules/[FILE].mdc`
- **Token Budget:** ~[N] tokens (update when starting long session)
- **Last Checkpoint:** [ID] — [DESCRIPTION] ✅
- **Next Steps:**
  - [ ] [TASK_1]
  - [ ] [TASK_2]
```

---

## LOBE TEMPLATE (v4.2)

```markdown
---
alwaysApply: false
description: "Lobe: [PHASE_NAME]. TurboQuant v4.2."
globs: ["[PATH_PATTERN]"]
---

# 🧩 Lobe: [PHASE_NAME]
<!-- Activated by glob OR semantic mention to domain -->
<!-- Isolated namespace: do not share variables with other lobes -->

## 🚨 STEP 0 — REGRESSION CHECK (MANDATORY)
> Read table below. Similarity → advise before proceeding.

## 📍 Checkpoint Tree
- [x] **CP-001:** [Completed]
- [ ] **CP-002:** [In progress] ← **CURRENT**
  - [ ] Sub-task 2.1 — Few-shot: "[EXAMPLE]"
- [ ] **CP-003:** [Pending]

## 🚫 Negative Phase Constraints
- ❌ [WHAT_NOT_TO_DO_IN_THIS_PHASE]

## 📉 Regression Buffer — Specific
| Error | Attempt | Lesson |
| :--- | :--- | :--- |
| [ERROR] | [ATTEMPT] | [LESSON] |

## 🏷️ Local Compact Encoding
| Symbol | Meaning |
| :--- | :--- |
| `$[alias]` | `[PATH]` |

## 📊 Phase Metrics
> Update via Wrap Up Session Workflow.

| Metric | Value |
| :--- | :--- |
| Interactions | 0 |
| Files created | 0 |
| Problems solved | 0 |
| Token budget warnings | 0 |
```

---

## FILE HIERARCHY (Anthropic-inspired — Improvement #11)

```
GLOBAL   → ~/.config/turboquant/global-cortex.mdc   (permanent personal preferences)
PROJECT  → .agents/rules/00-cortex.mdc              (repo architecture and conventions)
PHASE    → .agents/rules/phase-N-name.mdc           (module-specific context)
LOCAL    → .agents/rules/local.mdc (gitignore)      (personal notes, local dev URLs)
```

---

## DIRECTORY STRUCTURE (v4.2)

```
[PROJECT]/
├── memory_turboquant_[PROJECT].json   ← STATE LEDGER
├── .agents/
│   ├── rules/
│   │   ├── 00-cortex.mdc              ← GLOBAL INSTRUCTIONS (alwaysApply: true)
│   │   ├── phase-[N]-[name].mdc       ← Lobes by phase/module
│   │   ├── local.mdc                  ← Personal notes (gitignore)
│   │   ├── CHANGELOG.md               ← Last 5 structural changes
│   │   └── archive/                   ← Completed lobes (with auto-summary)
│   └── workflows/                     ← Optional Slash commands
├── memory_lobes/                      ← Detailed state of active lobes
├── archive/                           ← Markdown auto-summaries of completed phases
└── backup/                            ← Timestamped backups (!backup)
```

---

## COMPLETE INDUSTRIAL WORKFLOW (SINGLE-AGENT v4.2)

```
PHASE 0  → STEP 0: Regression Check + Goal Reaffirmation
PHASE 1  → Explore (read-only) → Identify files, deps, locks
PHASE 2  → Plan: <thinking> → propose plan → await confirmation
PHASE 3  → Act: minimal diffs · JIT · mandatory encoding · official vocab
PHASE 4  → Observe: !lint + !test → validate goal → ReAct if fails
PHASE 5  → Persist: state · checkpoint · compaction · !backup · CHANGELOG
PHASE 6  → (if focus shift) → Finish current lobe → Load new lobe
```

---

## UTILITY COMMANDS (PowerShell)

```powershell
# Check JSON health
$json = Get-Content memory_turboquant_*.json -Raw
$tokens = [math]::Round($json.Length / 4)
Write-Host "Estimated tokens: $tokens"
if ($tokens -gt 7000) { Write-Warning "⚠ Nearing limit — execute pruning" }
if ($tokens -gt 8000) { Write-Error "🚨 BLOCK — mandatory pruning!" }

# Timestamped backup
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
Copy-Item memory_turboquant_*.json "backup\cortex_$ts.json"

# Archive completed lobe
$lobe = "phase-1-name"; $ts = Get-Date -Format 'yyyyMMdd'
Move-Item ".agents\rules\$lobe.mdc" ".agents\rules\archive\$lobe`_$ts.mdc"

# Check for encoding violations (paths without alias)
Select-String -Path ".agents\rules\*.mdc" -Pattern "docs/|src/|lib/" |
  Where-Object { $_ -notmatch "^\s*#" -and $_ -notmatch "^\s*\|" }
```

---

## USAGE EXAMPLES (Few-Shot — Improvement #13)

```
▸ NEW SESSION
  INIT TURBOQUANT FOR: my_api
  CONTEXT: Implement JWT authentication
  OBJECTIVE: Create /refresh endpoint with token blacklist
  PREVIOUS_MEMORY: None
  MODE: single_agent

▸ RESUME SESSION (with active lobe)
  INIT TURBOQUANT FOR: my_api
  CONTEXT: Continuing CP-DEV-003 — /refresh endpoint
  OBJECTIVE: Finish unit tests for auth module
  PREVIOUS_MEMORY: cortex v4.2 + lobe phase-2-auth (checkpoint CP-003)
  MODE: single_agent

▸ USING COMPACT ENCODING
  INIT TURBOQUANT FOR: my_api
  CONTEXT: Refactor $auth-svc and @middlewares to use ?validation-schema
  OBJECTIVE: Apply Zod in all protected routes
  PREVIOUS_MEMORY: cortex v4.2 + lobe phase-2-auth
  MODE: single_agent
```

---

**VERSION:** TurboQuant v4.2-Cortex (Single-Agent)  
**DATE:** 2026-04-09  
**IMPROVEMENTS:** 35 implemented principles (see index above)  
**SOURCES:** MemGPT · ReAct · Acon Framework · Cursor Rules · Anthropic CLAUDE.md · Context Engineering (Google DeepMind) · LangChain · DDD (Evans) · Augment Code · Galileo AI