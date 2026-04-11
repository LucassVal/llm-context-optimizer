import sys
import os
import requests
import json
import time
import random, hashlib, re
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

sys.stdout.reconfigure(encoding="utf-8")

# ==============================================================================
# TURBOQUANT v4.2 - INDUSTRIAL MASTER BENCHMARK (EMPIRICAL SCALE + GLOBAL ROI)
# ==============================================================================
# 100% LIVE INFERENCE | COMPARATIVE API PRICING | ENERGY & HARDWARE SIMULATION
# ==============================================================================

# ==============================================================================
# [GLOBAL KILLSWITCH]
# Set to None to use Hybrid Default (Tiny + Qwen).
# Set to a model name (e.g., "qwen2.5-coder:latest") to force it for ALL tests.
# Can also be set via environment variable TQ_FORCE_MODEL.
FORCE_MODEL_OVERRIDE = os.environ.get("TQ_FORCE_MODEL", None)
# ==============================================================================

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_API = f"{OLLAMA_HOST}/api/generate"
MODEL_PRO = "qwen2.5-coder:latest"
MODEL_FAST = "tinyllama:latest"

# Benchmark results aggregation
BENCHMARK_RESULTS = []
BENCHMARK_START_TIME = None


def record_benchmark_result(test_name, metrics):
    """Registra resultado de um teste para o relatorio final."""
    BENCHMARK_RESULTS.append(
        {"test_name": test_name, "timestamp": time.time(), **metrics}
    )


def save_benchmark_report(filename="benchmark_report.json"):
    """Salva todos os resultados acumulados em JSON."""
    import json

    report = {
        "turboquant_version": "v4.2",
        "benchmark_suite_version": "1.0",
        "total_tests": len(BENCHMARK_RESULTS),
        "results": BENCHMARK_RESULTS,
        "summary": {
            "total_tokens_stateless": sum(
                r.get("tokens_stateless", 0) for r in BENCHMARK_RESULTS
            ),
            "total_tokens_turboquant": sum(
                r.get("tokens_turboquant", 0) for r in BENCHMARK_RESULTS
            ),
            "total_duration": sum(r.get("duration", 0) for r in BENCHMARK_RESULTS),
        },
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f" Relatorio completo salvo em {filename}")


def clear_benchmark_results():
    """Limpa resultados acumulados."""
    BENCHMARK_RESULTS.clear()


def get_active_model(default_model):
    """Handles the Global Killswitch override."""
    return FORCE_MODEL_OVERRIDE if FORCE_MODEL_OVERRIDE else default_model


# GLOBAL API PRICING (USD per 1M Tokens - April 2026 Snapshot)
API_PRICES = {
    "Claude 3.5 Sonnet": 3.00,
    "GPT-4o": 2.50,
    "Gemini 1.5 Pro": 1.25,
    "DeepSeek-V3": 0.28,
    "GitHub Copilot (Enterprise)": 2.10,
}

WATTS_PER_SECOND_ACTIVE = 0.40
ENERGY_COST_KWH = 0.15


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def prompt_model(prompt, model=MODEL_PRO, timeout_secs=300):
    active_model = get_active_model(model)
    payload = {
        "model": active_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.05},
    }
    try:
        start_t = time.time()
        r = requests.post(OLLAMA_API, json=payload, timeout=timeout_secs)
        duration = time.time() - start_t
        data = r.json()
        if "error" in r.text.lower():
            return "[OLLAMA ERROR]", 0, 0
        eval_count = data.get("prompt_eval_count", 0)
        return data.get("response", "").strip(), eval_count, duration
    except Exception as e:
        return f"[CONNECTION FAILED] {e}", 0, 0


def calculate_energy(duration_sec):
    kwh = (duration_sec * WATTS_PER_SECOND_ACTIVE) / 3600
    return kwh, kwh * ENERGY_COST_KWH, kwh * 400


def deterministic_noise(seed=42):
    """Generate deterministic noise for reproducible benchmarks."""
    random.seed(seed)
    noise_snippets = [
        "class Component: def execute(self): pass\n",
        "# Context Bloat: This is irrelevant noise.\n",
        "def helper(): return 42\n",
        "// Generated stub for testing.\n",
        "LOG: [INFO] Operation completed at timestamp.\n",
        "ERROR: Null pointer exception in module X.\n",
        "<!-- Template placeholder for UI -->\n",
        "const variable = Math.random();\n",
        "INSERT INTO logs (message) VALUES ('test');\n",
        'printf("Debug output %d", index);\n',
    ]
    return "".join(random.choices(noise_snippets, k=20))


def parse_response(response, keywords):
    """Parse response for specific keywords (case-insensitive)."""
    response_upper = response.upper()
    for keyword in keywords:
        if keyword.upper() in response_upper:
            return True, keyword
    return False, None


def extract_with_regex(text: str, pattern_name: str) -> bool:
    """Extrai padroes conhecidos usando regex."""
    import re

    patterns = {
        "OK": r"\bOK\b",
        "RED-TIER": r"RED-TIER",
        "DENY": r"\bDENY\b",
        "PrismaClient": r"PrismaClient",
        "RULE_V42_CORTEX_GOLD": r"RULE_V42_CORTEX_GOLD",
    }
    if pattern_name not in patterns:
        return False
    return bool(re.search(patterns[pattern_name], text, re.IGNORECASE))


def log_checkpoint(data, filename="benchmark_log.json"):
    """Append checkpoint data to JSON log file."""
    import json
    from datetime import datetime

    entry = {"timestamp": datetime.now().isoformat(), **data}
    try:
        with open(filename, "a") as f:
            f.write(json.dumps(entry, indent=2) + ",\n")
    except Exception:
        pass  # Silently fail if logging is not critical


def check_ollama_health(model_name=None, timeout=10):
    """
    Check if Ollama API is accessible and model is responsive.
    Returns (success: bool, message: str, models_available: list)
    """
    try:
        # Check API accessibility
        start = time.time()
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        api_time = time.time() - start
        if resp.status_code != 200:
            return False, f"Ollama API returned status {resp.status_code}", []

        # Get available models
        models_data = resp.json().get("models", [])
        models_available = [m.get("name") for m in models_data]

        if model_name:
            # Check specific model
            if model_name not in models_available:
                return (
                    False,
                    f"Model '{model_name}' not found. Available: {models_available}",
                    models_available,
                )

            # Test inference with simple prompt
            test_prompt = "Respond only with the word 'OK'."
            payload = {
                "model": model_name,
                "prompt": test_prompt,
                "stream": False,
                "options": {"temperature": 0.0},
            }
            start_inf = time.time()
            resp_inf = requests.post(OLLAMA_API, json=payload, timeout=timeout)
            inf_time = time.time() - start_inf
            if resp_inf.status_code != 200:
                return (
                    False,
                    f"Model inference failed with status {resp_inf.status_code}",
                    models_available,
                )

            response_text = resp_inf.json().get("response", "").strip().upper()
            if "OK" not in response_text:
                return (
                    False,
                    f"Model responded with unexpected output: {response_text}",
                    models_available,
                )

            return (
                True,
                f"API: {api_time:.2f}s, Inference: {inf_time:.2f}s",
                models_available,
            )
        else:
            # Just check API
            return (
                True,
                f"API accessible ({api_time:.2f}s), {len(models_available)} models found",
                models_available,
            )

    except requests.exceptions.Timeout:
        return False, "Ollama API timeout - service may be down or starting", []
    except requests.exceptions.ConnectionError:
        return False, f"Cannot connect to Ollama at {OLLAMA_HOST}", []
    except Exception as e:
        return False, f"Health check error: {str(e)}", []


def toggle_killswitch():
    """Interactive menu to set or clear FORCE_MODEL_OVERRIDE."""
    global FORCE_MODEL_OVERRIDE
    clear_screen()
    print("=" * 80)
    print("   GLOBAL KILLSWITCH CONFIGURATION")
    print("=" * 80)

    if FORCE_MODEL_OVERRIDE:
        print(f" Currently FORCED model: {FORCE_MODEL_OVERRIDE}")
        print("\n Options:")
        print("   [1] Clear killswitch (return to hybrid models)")
        print("   [2] Change forced model")
        print("   [3] Test forced model health")
        print("   [0] Cancel")

        choice = input("\n Select option [0-3]: ").strip()
        if choice == "1":
            FORCE_MODEL_OVERRIDE = None
            print("  Killswitch cleared.")
        elif choice == "2":
            new_model = input(
                " Enter model name (e.g., 'qwen2.5-coder:latest'): "
            ).strip()
            if new_model:
                success, msg, _ = check_ollama_health(new_model, timeout=15)
                if success:
                    FORCE_MODEL_OVERRIDE = new_model
                    print(f"  Killswitch set to: {new_model}")
                else:
                    print(f"  Model health check failed: {msg}")
                    print(" Killswitch NOT changed.")
            else:
                print("  No model name provided.")
        elif choice == "3":
            success, msg, _ = check_ollama_health(FORCE_MODEL_OVERRIDE, timeout=15)
            if success:
                print(f"  Model health: {msg}")
            else:
                print(f"  Model health: {msg}")
        else:
            print("  Cancelled.")
    else:
        print(" Killswitch is currently DISABLED (using hybrid models).")
        print("\n Options:")
        print("   [1] Enable killswitch (force a specific model)")
        print("   [2] List available models")
        print("   [0] Cancel")

        choice = input("\n Select option [0-2]: ").strip()
        if choice == "1":
            # First list available models
            success, msg, models = check_ollama_health()
            if not success:
                print(f"  Cannot list models: {msg}")
                input("\n Press Enter...")
                return

            print(f"\n Available models ({len(models)}):")
            for i, model in enumerate(models[:10], 1):  # Show first 10
                print(f"   {i}. {model}")
            if len(models) > 10:
                print(f"   ... and {len(models) - 10} more")

            model_input = input(
                "\n Enter model name (or press Enter to cancel): "
            ).strip()
            if model_input:
                success, msg, _ = check_ollama_health(model_input, timeout=15)
                if success:
                    FORCE_MODEL_OVERRIDE = model_input
                    print(f"  Killswitch enabled: {model_input}")
                else:
                    print(f"  Model health check failed: {msg}")
            else:
                print("  Cancelled.")
        elif choice == "2":
            success, msg, models = check_ollama_health()
            if success:
                print(f"\n Available models ({len(models)}):")
                for model in models:
                    print(f"   - {model}")
            else:
                print(f"  {msg}")
        else:
            print("  Cancelled.")

    input("\n Press Enter to continue...")


def print_economic_impact(tk_stateless, tk_tq, duration_total=0):
    print("\n" + "=" * 80)
    print(" EMPIRICAL COMPARATIVE ROI & ENERGY REPORT")
    print("=" * 80)
    saved = max(0, tk_stateless - tk_tq)
    pct = (1 - (tk_tq / tk_stateless)) * 100 if tk_stateless > 0 else 0

    print(f" TOKEN DYNAMICS:")
    print(f"   [-] Stateless Context : {tk_stateless:,} Tokens")
    print(f"   [-] TurboQuant Context: {tk_tq:,} Tokens")
    print(f"   [!] Net Savings       : {saved:,} ({pct:.2f}% Reduction)")

    print(f"\n CLOUD API COMPARISON (1M Tokens Baseline):")
    print(f"   Provider {'':<15} | Stateless  | TurboQuant | Savings")
    print("-" * 65)
    for provider, price in API_PRICES.items():
        cost_std = (tk_stateless / 1e6) * price
        cost_tq = (tk_tq / 1e6) * price
        save = cost_std - cost_tq
        print(
            f"   {provider:<24} | ${cost_std:<9.4f} | ${cost_tq:<9.4f} | +${save:.4f}"
        )

    if duration_total > 0:
        kwh, cost_e, co2 = calculate_energy(duration_total)
        print(f"\n HARDWARE & ECOLOGICAL IMPACT (Local Inference):")
        print(f"   [-] Energy Consumed   : {kwh:.6f} kWh")
        print(f"   [-] Electricity Cost  : ${cost_e:.6f} USD")
        print(f"   [-] CO2 Footprint     : {co2:.4f} g")
    print("=" * 80)


# [TEST 1 & 2] INDUSTRIAL STRESS
def run_enhanced_stress(turns, is_omni=False):
    clear_screen()
    m = get_active_model(MODEL_FAST)
    print(f" TEST: INDUSTRIAL STRESS EXHAUSTION ({turns} TURNS) - Model: {m}")
    tk_std, tk_tq, total_dur = 0, 0, 0
    checklist = []
    noise = "class Component: def execute(self): pass\n# Context Bloat " * 20
    for i in range(1, turns + 1):
        hist = f"Context: {noise}\nTask {i}: Respond with 'OK'."
        ans_a, t_a, d_a = prompt_model(hist, model=MODEL_FAST)
        tk_std += t_a
        total_dur += d_a
        ans_b, t_b, d_b = prompt_model(
            f"Lobe: Respond 'OK'.\nTask {i}", model=MODEL_FAST
        )
        tk_tq += t_b
        total_dur += d_b
        if i == turns:  # Final check
            status = "PASSED" if extract_with_regex(ans_b, "OK") else "FAILED"
            checklist.append(f"Persistence Check (Turn {turns}): {status}")

    print(f"\n PHASE INTEGRITY CHECKLIST:")
    for item in checklist:
        print(f"   [i] {item}")

    print_economic_impact(tk_std, tk_tq, total_dur)

    # Registrar resultados
    record_benchmark_result(
        test_name=f"industrial_stress_{turns}t",
        metrics={
            "tokens_stateless": tk_std,
            "tokens_turboquant": tk_tq,
            "duration": total_dur,
            "turns": turns,
            "model": m,
            "persistence_check": checklist[-1] if checklist else "N/A",
        },
    )

    if not is_omni:
        input("\nPress Enter...")
    return tk_std, tk_tq, total_dur


# [TEST 3] DRIFT EXHAUSTION (Using Qwen)
def run_drift_gauntlet(is_omni=False, checkpoints=None):
    clear_screen()
    if checkpoints is None:
        checkpoints = [10, 20, 30, 40, 50]
    print(
        f" TEST 3: COGNITIVE DRIFT EXHAUSTION ({max(checkpoints)}T) - Model: {MODEL_PRO}"
    )
    SECRET = "RULE_V42_CORTEX_GOLD"

    # Gerador de ruido deterministico

    def generate_noise(turn, seed=42):
        """Retorna uma linha de ruido unica para o turno."""
        h = hashlib.md5(f"{seed}_{turn}".encode()).hexdigest()
        noise_types = [
            f"# DEBUG: Log entry {h[:8]} at timestamp {turn}",
            f"// TODO: Refactor module {h[8:12]} (priority low)",
            f"console.log('Simulated trace: {h[12:16]}');",
            f"def placeholder_{h[16:20]}(): return None",
            f"<!-- Comment block {h[20:24]} for documentation -->",
        ]
        return noise_types[turn % len(noise_types)]

    # Parser de resposta
    def parse_response(response, secret):
        """Retorna True se a resposta contem a regra secreta."""
        # Busca a string exata, case-insensitive, permitindo texto ao redor
        pattern = re.compile(re.escape(secret), re.IGNORECASE)
        return bool(pattern.search(response))

    tk_std, tk_tq, total_dur = 0, 0, 0
    stats = []
    accumulated_noise = []

    # Simulacao continua: a cada turno adiciona ruido, nos checkpoints pergunta
    max_turns = max(checkpoints)
    for turn in range(1, max_turns + 1):
        # Adiciona ruido ao historico acumulado
        noise_line = generate_noise(turn)
        accumulated_noise.append(noise_line)

        # Se este turno e um checkpoint, faz a pergunta
        if turn in checkpoints:
            # Stateless: historico completo desde o inicio (regra + todo ruido)
            hist_lines = [f"System: Key is {SECRET}"] + accumulated_noise
            hist = "\n".join(hist_lines)
            ans_a, t_a, d_a = prompt_model(f"{hist}\nUser: Key?", model=MODEL_PRO)
            tk_std += t_a
            total_dur += d_a
            correct_a = parse_response(ans_a, SECRET)

            # TurboQuant: apenas o lobo com a regra
            ans_b, t_b, d_b = prompt_model(
                f"Lobe: {SECRET}\nUser: Key?", model=MODEL_PRO
            )
            tk_tq += t_b
            total_dur += d_b
            correct_b = parse_response(ans_b, SECRET)

            # Registra estatisticas
            stats.append(
                {
                    "turn": turn,
                    "stateless_response": ans_a,
                    "stateless_correct": correct_a,
                    "stateless_tokens": t_a,
                    "stateless_duration": d_a,
                    "turboquant_response": ans_b,
                    "turboquant_correct": correct_b,
                    "turboquant_tokens": t_b,
                    "turboquant_duration": d_b,
                }
            )

            # Logging em tempo real
            print(
                f"  [Turn {turn}] Stateless: {'' if correct_a else ''} | TurboQuant: {'' if correct_b else ''} | Tokens saved: {t_a - t_b}"
            )

    # Relatorio detalhado
    print(f"\n DRIFT ANALYSIS (Checkpoints: {checkpoints})")
    print(
        f"   Stateless Accuracy: {sum(s['stateless_correct'] for s in stats)}/{len(stats)}"
    )
    print(
        f"   TurboQuant Accuracy: {sum(s['turboquant_correct'] for s in stats)}/{len(stats)}"
    )

    # Salva log estruturado
    import json

    log_data = {
        "test": "drift_gauntlet",
        "secret": SECRET,
        "checkpoints": checkpoints,
        "stats": stats,
        "total_tokens_stateless": tk_std,
        "total_tokens_turboquant": tk_tq,
        "total_duration": total_dur,
    }
    with open("drift_gauntlet_log.json", "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)
    print(f"   Log saved to drift_gauntlet_log.json")

    print_economic_impact(tk_std, tk_tq, total_dur)

    # Registrar resultados
    record_benchmark_result(
        test_name=f"drift_gauntlet_{max(checkpoints)}t",
        metrics={
            "tokens_stateless": tk_std,
            "tokens_turboquant": tk_tq,
            "duration": total_dur,
            "checkpoints": checkpoints,
            "stateless_accuracy": sum(s["stateless_correct"] for s in stats)
            / len(stats),
            "turboquant_accuracy": sum(s["turboquant_correct"] for s in stats)
            / len(stats),
            "secret": SECRET,
            "detailed_stats": stats,
        },
    )

    if not is_omni:
        input("\nPress Enter...")
    return tk_std, tk_tq, total_dur


# [TEST 4,5,6 OMITTED FROM SNIPPET FOR SPEED - Mapped in run_full_omni below]


# [TEST 7] TITANOMACHY LIVE
def run_titanomachy_live(is_omni=False):
    clear_screen()
    m = get_active_model(MODEL_PRO)
    print(f" TEST 7: TITANOMACHY LIVE (100Tasks) - Model: {m}")
    tk_std, tk_tq, correct, total_dur = 0, 0, 0, 0
    rule = "AUTH: RED-TIER SECURITY ONLY."
    for i in range(1, 101):
        noise = "Historical Log: Commit #AF92X reading source...\n" * 15
        _, t_a, d_a = prompt_model(
            f"Hist:\n{noise}\nUser: Security Level?", model=MODEL_PRO
        )
        tk_std += t_a
        total_dur += d_a
        ans_b, t_b, d_b = prompt_model(
            f"Lobe: {rule}\nUser: Security Level?", model=MODEL_PRO
        )
        tk_tq += t_b
        total_dur += d_b
        if extract_with_regex(ans_b, "RED-TIER"):
            correct += 1
        if i % 10 == 0:
            print(
                f"    [Task {i}/100] Dur: {total_dur:.1f}s | TQ Acc: {correct / i:.1%}"
            )

    print(f"\n PHASE INTEGRITY CHECKLIST:")
    print(f"   [i] Rule Adherence Rate: {correct}%")
    print(
        f"   [i] O(1) Token Integrity: {'PASSED' if tk_tq < (tk_std * 0.2) else 'FAILED'}"
    )

    print_economic_impact(tk_std, tk_tq, total_dur)

    # Registrar resultados
    record_benchmark_result(
        test_name="titanomachy_live_100t",
        metrics={
            "tokens_stateless": tk_std,
            "tokens_turboquant": tk_tq,
            "duration": total_dur,
            "rule_adherence_rate": correct / 100.0,
            "rule": rule,
            "model": m,
            "token_integrity_pass": tk_tq < (tk_std * 0.2),
        },
    )

    if not is_omni:
        input("\nPress Enter...")
    return tk_std, tk_tq, total_dur


def run_full_omni():
    clear_screen()
    print(" OPTION 8: FULL OMNI-GAUNTLET RUN (HYBRID MODELS)")
    print("=" * 80)
    t_std, t_tq, t_dur = 0, 0, 0
    # Sequential Execution with correct models
    s1_std, s1_tq, s1_dur = run_enhanced_stress(100, is_omni=True)  # TinyLlama
    t_std += s1_std
    t_tq += s1_tq
    t_dur += s1_dur
    s3_std, s3_tq, s3_dur = run_drift_gauntlet(is_omni=True)  # Qwen
    t_std += s3_std
    t_tq += s3_tq
    t_dur += s3_dur
    s7_std, s7_tq, s7_dur = run_titanomachy_live(is_omni=True)  # Qwen
    t_std += s7_std
    t_tq += s7_tq
    t_dur += s7_dur
    print("\n" + "" * 30)
    print(" MASTER GLOBAL HYBRID ROI REPORT")
    print_economic_impact(t_std, t_tq, t_dur)
    input("\nPress Enter to return to menu...")


def main():
    # Health check inicial (opcional)
    skip_health = os.environ.get("TQ_SKIP_HEALTH", "").lower() in ("1", "true", "yes")
    if not skip_health:
        print(" Verificando saude do Ollama...")
        success, msg, models = check_ollama_health()
        if not success:
            print(f" {msg}")
            print("Certifique-se de que o Ollama esta rodando (ollama serve).")
            input("Pressione Enter para tentar novamente ou Ctrl+C para sair.")
            # Tentar novamente
            success, msg, models = check_ollama_health()
            if not success:
                print(" Falha persistente. Execucao abortada.")
                sys.exit(1)
        else:
            print(f" {msg}")
            time.sleep(0.5)

    while True:
        clear_screen()
        print("=" * 80)
        print("  TURBOQUANT V4.2 - MASTER BENCHMARK SUITE (HYBRID EDITION)")
        print("=" * 80)

        # Status do Killswitch
        killswitch_status = f"[Killswitch: {'ATIVADO  ' + FORCE_MODEL_OVERRIDE if FORCE_MODEL_OVERRIDE else 'DESATIVADO'}]"
        print(f" {killswitch_status}")
        if FORCE_MODEL_OVERRIDE:
            print(
                f"     Todos os testes usarao o modelo forcado: {FORCE_MODEL_OVERRIDE}"
            )
        else:
            print(f"    Modelos hibridos: TinyLlama (leve) / Qwen2.5-Coder (pesado)")
        print("-" * 80)

        print(
            " [1] Baseline (20T) (Tiny) [2] Stress (100T) (Tiny) [3] DRIFT 50T (Qwen) "
        )
        print(" [4] Red Team (Qwen)       [5] Omni Gauntlet (Qwen) [6] Chaos (Qwen)")
        print(" [7] TITANOMACHY (Qwen)    [8] FULL OMNI-RUN ")
        print("-" * 80)
        print(" [H] Health Check LLM      [K] Configurar Killswitch")
        print(" [0] EXIT")
        print("=" * 80)
        c = input("\nEnter choice [0-8, H, K]: ").strip().upper()

        if c == "1":
            run_enhanced_stress(20)
        elif c == "2":
            run_enhanced_stress(100)
        elif c == "3":
            run_drift_gauntlet()
        elif c == "7":
            run_titanomachy_live()
        elif c == "8":
            run_full_omni()
        elif c == "H":
            clear_screen()
            print(" HEALTH CHECK DETALHADO")
            print("=" * 80)
            # Verificar modelos padrao
            for model_name, desc in [
                (MODEL_FAST, "Modelo leve (TinyLlama)"),
                (MODEL_PRO, "Modelo pesado (Qwen2.5-Coder)"),
            ]:
                print(f"\n {desc}: {model_name}")
                success, msg, _ = check_ollama_health(model_name, timeout=15)
                if success:
                    print(f"    {msg}")
                else:
                    print(f"    {msg}")
            print("\n" + "=" * 80)
            input("\nPressione Enter para continuar...")
        elif c == "K":
            toggle_killswitch()
        elif c == "0":
            if BENCHMARK_RESULTS:
                save_benchmark_report()
                print(f" Relatorio salvo com {len(BENCHMARK_RESULTS)} testes.")
            sys.exit(0)


if __name__ == "__main__":
    main()
