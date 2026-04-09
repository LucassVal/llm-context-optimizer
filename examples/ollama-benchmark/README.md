# Ollama Benchmark Tool

This folder contains a Python script that empowers you to **empirically prove** the token savings of the TurboQuant architecture using your own local LLMs.

## How does it work?
The script tests two scenarios using the Ollama API's native `prompt_eval_count` telemetry (which tracks exact tokens evaluated by the model):

1. **Standard Stateless Agent:** Feeds a large dummy codebase over 5 conversation turns. As history builds, the agent processes larger and larger chunks of data just to understand the conversation state.
2. **TurboQuant Stateful Agent:** Feeds only a compact JSON Ledger string alongside the conversation state, simulating precise file targeting instead of mass reading.

## Requirements
- Python 3.x
- `requests` library (`pip install requests`)
- Ollama installed locally with the `llama3` model (or edit the script to point to your model, e.g., `mistral`, `deepseek-coder`).

## Execution
```bash
python run_benchmark.py
```
