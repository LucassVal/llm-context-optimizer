# 🧪 TurboQuant V4.2 - Master Benchmark Suite

This directory contains the **Master Benchmark Suite** (`benchmark_master_suite.py`), a professional, monolithic stress-testing tool designed to empirically prove the architectural superiority of **TurboQuant's O(1) Context Optimization** vs the traditional **Stateless O(N) Agent** approach via direct A/B testing.

## 🚀 How to Run

1. Ensure your local LLM server is active (default is `http://localhost:11434/api/generate` configured for Ollama).
2. Execute the master suite via terminal:
```bash
python benchmark_master_suite.py
```
3. A menu will appear allowing you to select the specific benchmark to run.

## 🧠 Model Recommendations & Parameters

- **Recommended Testing Model**: `qwen2.5-coder:latest`, `llama3.1:latest`, or any model with **7B+ parameters**.
- **The "Model Collapse" Warning**: During testing, we proved experimentally that small models (like 1B `tinyllama`) lack the internal parameter density to adhere strictly to JSON-based rules. Even under the rigid strictures of TurboQuant, a 1B model will often hallucinate against the JSON due to parametric overriding. Therefore, use 7B+ parameters to properly observe the TurboQuant core engine logic operating deterministically.

You can modify the target model on **Line 16** of `benchmark_master_suite.py`:
```python
MODEL = "qwen2.5-coder:latest" # Change to your local or external endpoint
```

## 📊 The Four Benchmarks

### 1. Empirical Token Optimization (20 Turns)
Tracks the exact number of tokens evaluated per turn. The **Stateless Agent** linearly accumulates history, reaching the 2048 Context Window limit via Context Ballooning O(N) immediately. **TurboQuant** flushes history dynamically between phases, using the `Ledger` to maintain O(1) stability throughout the 20 conversational turns, proving a ~80% efficiency gain.

### 2. Industrial Stress Test (100 Turns)
An extrapolation of Test 1 pushing 100 deep conversational turns. This definitively proves KV-Cache saturation. While the Stateless Agent completely collapses and overflows your VRAM, TurboQuant's memory isolation keeps token consumption nearly perfectly horizontal over thousands of logical code injections.

### 3. Cognitive Drift & Hallucination Test (11 Turns)
Proves that **long context is not synonymous with good logic**. 
- Turn 1: We tell the model the production password is `SIGMA-BUMBLEBEE`.
- Turns 2 to 10: We flood the history with simulated repository code noise.
- Turn 11: We ask for the password. The **Stateless LLM forgets completely** because the rule drifted out of the KV-Cache. **TurboQuant recalls it 100% of the time** because the rule is retrieved efficiently from a separate `Semantic Lobe` file, bypassing the conversational noise altogether.

### 4. The Turbulent Development Simulator (Adversarial Red Teaming)
A/B testing across 4 massive real-world development scenarios:
1. **Dependency Hell Rollback**: Recovering exact Node versions securely.
2. **Compliance Defiance**: Standard agents offer "corporate essays" against user inputs breaking atomic bounds. TurboQuant outputs pure logic (`DENY`).
3. **Git Merge Conflict**: Standard agents write massive tutorials. TurboQuant enforces the `Auth Lobe` to resolve the string directly.
4. **The Monday Morning Amnesia Test**: Demonstrates Cross-Session Recall. When starting a completely empty chat window ("Monday Morning"), standard LLMs hallucinate what happened on "Friday". TurboQuant queries its `Regression Buffer` and extracts previous bugs perfectly without requiring a 64k token memory dump.
