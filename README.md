# LLM Context Optimizer (TurboQuant v4.2)

![Version](https://img.shields.io/badge/Version-v4.2-brightgreen.svg)
![Framework](https://img.shields.io/badge/Framework-Agnostic-blue.svg)
![Context](https://img.shields.io/badge/Context-Engineering-orange.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

> **Industrial-grade context engineering framework with fractal memory architecture for stateful LLM agents.**

Reduce token overhead by 40% and eliminate agent drift with a unified ledger system inspired by MemGPT, ReAct, Acon, Cursor Rules, Anthropic, and Google Context Engineering.

---

## 📁 Kit Structure

```
TURBOQUANT_V42/
├── README.md                          ← This file
├── turboquant_memory_prompt.md        ← Complete white-label template (v4.2)
│
├── templates/
│   ├── 00-cortex-STARTER.mdc          ← Minimal cortex (first 3-5 sessions)
│   ├── 00-cortex-FULL.mdc             ← Complete cortex (when project scales)
│   ├── phase-lobe-TEMPLATE.mdc        ← Phase/module lobe template
│   └── memory-ledger-TEMPLATE.json    ← State JSON (ledger)
│
├── .agents/
│   ├── rules/
│   │   ├── 00-cortex.mdc              ← Active cortex of the TQ project itself
│   │   └── CHANGELOG.md               ← Change history
│   └── workflows/
│       └── restart-session.md         ← Session resumption workflow
│
├── memory_lobes/                      ← Active lobes
├── archive/                           ← Completed phases
└── backup/                            ← Timestamped backups
```

---

## 🚀 Gradual Deployment Guide (Recommended)

### Week 1 — Starter (3-5 sessions)
Copy only `templates/00-cortex-STARTER.mdc` to `.agents/rules/` of your project.
Contains only: STEP 0 · 5-10 essential aliases · commands · wrapping up.

### Week 2 — Expansion
If you feel limitations, migrate to `00-cortex-FULL.mdc`.
Add aliases dynamically as suggested by the AI.

### Week 3+ — Lobes
When the cortex exceeds ~150 lines, create phased lobes using `phase-lobe-TEMPLATE.mdc`.

### Optional — JSON Ledger
Only add `memory-ledger-TEMPLATE.json` if you need fine-grained tracking of metrics and checkpoints.

---

## ⚡ Trigger Cheat Sheet

| Say this... | The AI will... |
| :--- | :--- |
| `"wrap up"` / `"that's it for today"` | Wrap Workflow (saves everything + !backup) |
| `"resume"` / `"where did we stop"` | Resume Workflow (reads current checkpoint) |
| `"create"` / `"implement"` | Explore-Plan-Act (read-only → proposes → waits OK) |
| `"error"` / `"bug"` | Debug Workflow (STEP 0 → hypothesis → confirm) |
| `"optimize"` | Genetic Algorithm + GetFitness (context specific) |
| `!token-check` | Checks JSON memory token size |
| `!backup` | Timestamped copy of the ledger |

---

## 📊 Estimated Savings (10 Sessions — Medium Project)

| Metric | Without TurboQuant | v4.2 | Gain |
| :--- | :--- | :--- | :--- |
| Total Tokens | ~370,000 | ~230,000 | **-38%** |
| Errors from lack of context | 3-5/session | 0-1/session | **-80%** |
| Premature changes | 2-3/session | 0-1/session | **-70%** |
| Dynamic alias savings | — | +15% additional | **New v4.2** |
| Completely saved sessions | ~60% | 100% | **+67%** |

---

## 💰 Cortex Token Cost

| File | Approx. Size | Tokens (Estimate) |
| :--- | :--- | :--- |
| `00-cortex-STARTER.mdc` | ~80 lines | ~600 tokens |
| `00-cortex-FULL.mdc` | ~200 lines | ~1,500 tokens |
| Active Lobe | ~60 lines | ~450 tokens |
| JSON ledger | ~400 lines | ~2,500 tokens |
| **STARTER total** | | **~600 tokens** |
| **FULL total (no JSON)** | | **~2,000 tokens** |
| **FULL + JSON + Lobe** | | **~4,500 tokens** |

> 💡 Even with 4,500 tokens of "overhead", the system saves 10-15x more in avoided mistakes.

---

## 🔑 Core Principles of v4.2

1. **STEP 0** — Regression Check before any action
2. **Compact Encoding** — Mandatory `$alias`, never use full paths
3. **Scratchpad** — Isolated `<thinking>` before answering
4. **Explore-Plan-Act** — Never write without exploring (read-only) first
5. **Negative Constraints** — Explicit list of what to NEVER do
6. **Wrapping Up** — Persist state at the end of every session
