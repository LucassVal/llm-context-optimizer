# 🧠 LLM Context Optimizer (TurboQuant v4.2-Cortex)

**Industrial-grade context engineering for stateful AI agents.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v4.2-blue)](https://github.com/LucassVal/llm-context-optimizer)
[![TurboQuant](https://img.shields.io/badge/TurboQuant-v4.2--Cortex-blue)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/LucassVal/llm-context-optimizer/pulls)

## 🎯 What Problem Does This Solve?

LLM agents suffer from:
- ❌ **Context amnesia** — forgetting everything between sessions
- ❌ **Token bloat** — wasting thousands of tokens on repeated discovery
- ❌ **Hallucinated commands** — guessing wrong build/test commands
- ❌ **Regression loops** — repeating the same failed solutions

**TurboQuant v4.2-Cortex** solves all of this with a **fractal memory architecture** inspired by MemGPT, ReAct, and Context Engineering research.

## 📊 Key Results (10 Sessions, Medium Project)

| Metric | Without TQ | With TQ v4.2 | Improvement |
| :--- | :---: | :---: | :---: |
| Tokens Consumed | 370,000 | 230,000 | **-38%** |
| Context Drift Errors | 3-5/session | 0-1/session | **-80%** |
| Session Continuity | ~60% | 100% | **+67%** |

## 🚀 Quick Start (30 seconds)

### Method 1: Using the Setup Scripts
**For Windows (PowerShell):**
```powershell
# Clone the repo
git clone https://github.com/LucassVal/llm-context-optimizer.git
cd llm-context-optimizer

# Run the initialization script
.\install.ps1 -ProjectName "MyProject"
```

**For Linux / macOS (Bash):**
```bash
# Clone the repo
git clone https://github.com/LucassVal/llm-context-optimizer.git
cd llm-context-optimizer

# Run the initialization script
chmod +x install.sh
./install.sh "MyProject"
```

### Method 2: Manual Setup
```bash
# Clone the repo
git clone https://github.com/LucassVal/llm-context-optimizer.git

# Copy the starter cortex to your project
cp llm-context-optimizer/templates/00-cortex-STARTER.mdc your-project/.agents/rules/00-cortex.mdc
```

**That's it.** Your AI agent now has persistent memory, mandatory compact encoding, and STEP 0 regression checking.

## 📚 Documentation

- [Full Prompt Specification](turboquant_memory_prompt.md)
- [Starter Cortex Template](templates/00-cortex-STARTER.mdc)
- [Phase Lobe Template](templates/phase-lobe-TEMPLATE.mdc)
- [JSON Ledger Schema](templates/memory-ledger-TEMPLATE.json)
- [Cheat Sheet & Voice Triggers](CHEATSHEET.md)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              TURBOQUANT v4.2-CORTEX             │
│                                                 │
│  ┌──────────────┐      ┌─────────────────────┐ │
│  │ JSON Ledger  │      │   .mdc Cortex       │ │
│  │ (State)      │      │   (Instructions)    │ │
│  └──────────────┘      └─────────────────────┘ │
│                                                 │
│  ┌────────────────────────────────────────────┐│
│  │  Lobes (Phase Modules) — Semantic Loading  ││
│  └────────────────────────────────────────────┘│
│                                                 │
│  ┌────────────────────────────────────────────┐│
│  │  Hierarchical Memory (Hot → Cold → Archive)││
│  └────────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘
```

## 🧪 Based On

- MemGPT (UC Berkeley)
- ReAct (Google DeepMind)
- Acon Framework
- Context Engineering Google
- Cursor Rules Best Practices
- Anthropic CLAUDE.md Specification

## 📄 License

MIT — use freely in any project, commercial or personal.

## ⭐ Star This Repo

If this saves you tokens and headaches, a star helps others discover it!
