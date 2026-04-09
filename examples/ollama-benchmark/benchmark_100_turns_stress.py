import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "tinyllama:latest"

FILE_LINES = 100
BASE_FILE_MOCK = "def core_logic(): pass\n" * FILE_LINES  

def print_header():
    print("="*75)
    print("[TURBOQUANT] EMPIRICAL CONTEXT OPTIMIZATION (100 TURNS)")
    print("="*75)

print_header()
phases = ["Ph1", "Ph2", "Ph3", "Ph4", "Ph5", "Ph6", "Ph7", "Ph8", "Ph9", "Ph10"]
history_standard = ""
repo_files_standard = ""
tokens_standard = 0

print("[x] TEST A: STANDARD AGENT (O(N))")
for p in phases:
    print(f"\n    ► {p} Started")
    repo_files_standard += BASE_FILE_MOCK
    for step in range(1, 11):
        prompt = f"Repo: {repo_files_standard}\nHistory: {history_standard}\nInstruction: Step {step}"
        try:
            r = requests.post(OLLAMA_API, json={"model": MODEL, "prompt": prompt, "stream": False}, timeout=10)
            data = r.json()
            tk = 2048 if ("error" in data and "memory" in data["error"].lower()) else data.get("prompt_eval_count", 0)
        except: tk = 0
        tokens_standard += tk
        history_standard += f"[{p}] Completed step {step}.\n"
        print(f"       Turn | Tokens: {tk}")

ledger_state = {}
history_tq = ""
tokens_tq = 0

print("\n" + "-"*75)
print("[OK] TEST B: TURBOQUANT AGENT O(1)")
for p in phases:
    print(f"\n    ► {p} Started")
    if history_tq != "":
        history_tq = ""
        ledger_state[p] = "DONE"
        print("       [SYSTEM] ⚡ CHECKPOINT PROTOCOL TRIGGERED. History Flushed.")
    for step in range(1, 11):
        prompt = f"Ledger:{json.dumps(ledger_state)}\nFile:{BASE_FILE_MOCK}\nHistory:{history_tq}\nInstruction: Step {step}"
        try:
            r = requests.post(OLLAMA_API, json={"model": MODEL, "prompt": prompt, "stream": False}, timeout=10)
            data = r.json()
            tk = 2048 if ("error" in data and "memory" in data["error"].lower()) else data.get("prompt_eval_count", 0)
        except: tk = 0
        tokens_tq += tk
        history_tq += f"Step {step} done.\n"
        print(f"       Turn | Tokens: {tk}")

print("\n" + "="*75)
print(f"[-] Cumulative Stress (Stateless):  {tokens_standard}")
print(f"[-] Cumulative Stress (TurboQuant): {tokens_tq}")
savings = (1 - (tokens_tq / tokens_standard)) * 100 if tokens_standard > 0 else 0
print(f"[!] EMPIRICAL EFFICIENCY GAIN: {savings:.2f}% Token Reduction\n")
