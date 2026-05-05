@echo off
echo [%date% %time%] Executando validação YAML/JSON...
"C:\Program Files\Python312\python.exe" "C:\Users\Lucas Valério\.gemini\antigravity\brain\validate_yaml.py"
if %errorlevel% neq 0 (
    echo VALIDAÇÃO FALHOU - Verificar logs
    exit 1
) else (
    echo Validação concluída com sucesso
)
