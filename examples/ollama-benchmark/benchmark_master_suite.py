import sys
import subprocess
import os

sys.stdout.reconfigure(encoding='utf-8')

# Ensure we are executing relative to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    clear_screen()
    print("="*80)
    print(" 🚀 TURBOQUANT V4.2 - MASTER BENCHMARK SUITE")
    print("="*80)
    print(" Select an empirical benchmark to execute locally against your LLM:\n")
    print(" [1] EMPIRICAL TOKEN OPTIMIZATION (20 TURNS)")
    print("     Evaluates O(N) context ballooning vs O(1) stateful JSON lobing over 4 phases.\n")
    print(" [2] INDUSTRIAL STRESS TEST (100 TURNS)")
    print("     Massive 10-phase scale token saturation test (forces 2048 KV Cache limit).\n")
    print(" [3] COGNITIVE DRIFT & HALLUCINATION TEST (11 TURNS)")
    print("     Evaluates rule-forgetting after the standard LLM's context window truncates.\n")
    print(" [4] THE TURBULENT DEVELOPMENT SIMULATOR (ADVERSARIAL RED TEAMING)")
    print("     A/B Testing: Dependency Rollback, Compliance Locks, & Git Conflicts.\n")
    print(" [0] EXIT COMMAND CENTER")
    print("="*80)

def run_script(filename):
    script_path = os.path.join(SCRIPT_DIR, filename)
    if not os.path.exists(script_path):
        print(f"\n[ERROR] Could not find {filename} in {SCRIPT_DIR}.")
        input("\nPress Enter to continue...")
        return
        
    print(f"\n🚀 Launching {filename}...\n")
    try:
        subprocess.run([sys.executable, script_path])
    except KeyboardInterrupt:
        print("\n[!] Execution aborted by user.")
    print("\n" + "-"*80)
    input("Execution completed. Press Enter to return to the Main Menu...")

def main():
    while True:
        print_menu()
        choice = input("\nEnter your choice [0-4]: ").strip()
        
        if choice == '1':
            run_script("benchmark_20_turns_stress.py")
        elif choice == '2':
            run_script("benchmark_100_turns_stress.py")
        elif choice == '3':
            run_script("benchmark_cognitive_drift.py")
        elif choice == '4':
            run_script("benchmark_turbulent_simulator.py")
        elif choice == '0':
            print("\nExiting TurboQuant Benchmark Suite. Goodbye!")
            break
        else:
            print("\n[!] Invalid choice. Please enter a number between 0 and 4.")
            time.sleep(1)

if __name__ == "__main__":
    main()
