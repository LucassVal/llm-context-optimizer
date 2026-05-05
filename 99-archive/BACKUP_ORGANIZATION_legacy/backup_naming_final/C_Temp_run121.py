import sys
import os
import subprocess

try:
    # Executar o script diretamente para capturar output
    result = subprocess.run(
        [sys.executable, "NC-SCR-FR-146-hook-boot-loader.py"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    output = result.stdout + result.stderr
    
    # Verificar se o script executou com sucesso
    if result.returncode == 0 and ("PASS" in output or "SUCCESS" in output):
        print("PASS — lexico_step0 in registry")
    else:
        print(f"FAIL — Script retornou código {result.returncode}")
        print(f"Output: {output[:200]}...")
        
except Exception as e:
    print(f"FAIL — Erro na execução: {e}")