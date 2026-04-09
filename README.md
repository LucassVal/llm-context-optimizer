# 🧠 LLM Context Optimizer (TurboQuant v4.2-Cortex)

**Industrial-grade context engineering for stateful AI agents.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-4.2.0-blue.svg)](https://github.com/LucassVal/llm-context-optimizer)
[![TurboQuant](https://img.shields.io/badge/Framework-TurboQuant_Cortex-blueviolet.svg)](#)
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

> 📈 **Scaling to 1 Million Tokens:** Working on massive monorepos? Check out our [Extrapolated Scalability Benchmarks](BENCHMARKS.md) to see how TurboQuant achieves O(1) context growth while standard agents suffer from linear O(N) token explosion.

## 🧪 Live Master Benchmark Suite

We've built an **Empirical Interactive A/B Testing Lab** (`examples/ollama-benchmark/benchmark_master_suite.py`) that you can run locally against your own models (like `qwen2.5` or `llama3.1`). It proves the difference between a Stateless standard agent versus our TurboQuant architecture across 4 massive stress tests:

1. **Empirical Token Optimization (20 Turns):** Proves O(1) cost reduction.
2. **Industrial Stress Test (100 Turns):** Forces the model to hit the 2048 KV-Cache limit and watches standard agents collapse while TQ survives.
3. **Cognitive Drift (11 Turns):** Proves standard models forget core passwords after 10 turns of code noise, whereas TQ isolates and recalls it continuously.
4. **The Turbulent Development Simulator (Red Teaming):** Evaluates Cross-Session Amnesia, compliance constraints (Nuclear Locks), and exact architectural merge conflict resolutions.

Read the [Benchmark Lab Documentation](examples/ollama-benchmark/README.md) for deeper instructions!

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

## 💡 Real-World Example

Check out the [`examples/demo-api`](examples/demo-api) directory.
It contains a simple Node.js Express server to demonstrate the framework in action. By reading the internal `.agents/rules/00-cortex.mdc` of that demo, you can see how the instructions prevent the agent from wandering aimlessly, ensuring it knows exactly where the entry points and rules are.

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
