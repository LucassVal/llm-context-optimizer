@echo off
:: NC-SCR-FR-116 — Guardian Daemon Service Installer
:: Instala o Guardian Daemon (COG-001) como tarefa agendada do Windows.
:: Uso: executar como Administrador
:: Gerado: 2026-04-19 | AGENT-001 COG-001

setlocal EnableDelayedExpansion

set "FW=C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework"
set "SCRIPT=%FW%\scripts\NC-SCR-FR-115-guardian-daemon.py"
set "TASK_NAME=NeoCortex-GuardianDaemon"
set "LOG=%FW%\.neocortex\guardian_service.log"
set "INTERVAL=60"

echo.
echo  =====================================
echo   NeoCortex Guardian Daemon Installer
echo   COG-001 / NC-SCR-FR-116
echo  =====================================
echo.

:: Verificar se Python existe
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH.
    pause & exit /b 1
)

:: Verificar se o script existe
if not exist "%SCRIPT%" (
    echo [ERRO] Script nao encontrado: %SCRIPT%
    pause & exit /b 1
)

:: Perguntar acao
echo Escolha uma opcao:
echo   1. Instalar / Atualizar tarefa agendada
echo   2. Remover tarefa agendada
echo   3. Iniciar agora (uma vez, em background)
echo   4. Ver status da tarefa
echo   5. Ver ultimo log
echo.
set /p "OPCAO=Opcao [1-5]: "

if "%OPCAO%"=="1" goto :instalar
if "%OPCAO%"=="2" goto :remover
if "%OPCAO%"=="3" goto :iniciar_agora
if "%OPCAO%"=="4" goto :status
if "%OPCAO%"=="5" goto :logs
goto :fim

:instalar
echo.
echo [*] Instalando tarefa: %TASK_NAME%

:: Deletar existente (sem erro se nao existir)
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

:: Criar wrapper .vbs para rodar Python sem janela
set "VBS=%FW%\scripts\NC-SCR-FR-116-guardian-runner.vbs"
(
echo Set WshShell = CreateObject("WScript.Shell"^)
echo Set env = WshShell.Environment("Process"^)
echo env("PYTHONIOENCODING"^) = "utf-8"
echo env("PYTHONUTF8"^) = "1"
echo env("NC_GUARDIAN_INTERVAL"^) = "%INTERVAL%"
echo env("PYTHONPATH"^) = "%FW%"
echo WshShell.Run "python -u ""%SCRIPT%"" >> ""%LOG%"" 2>&1", 0, False
) > "%VBS%"

:: Criar a tarefa agendada
:: Boot delay de 60s para esperar Ollama subir
schtasks /Create /TN "%TASK_NAME%" /TR "wscript.exe ""%VBS%""" /SC ONLOGON /DELAY 0001:00 /RL HIGHEST /F

if errorlevel 1 (
    echo [ERRO] Falha ao criar tarefa agendada.
    echo Dica: Execute este .bat como Administrador.
    pause & exit /b 1
)

echo.
echo [OK] Tarefa instalada com sucesso!
echo      Nome:     %TASK_NAME%
echo      Trigger:  Ao fazer login (delay 60s)
echo      Script:   %SCRIPT%
echo      Log:      %LOG%
echo      Intervalo: %INTERVAL% segundos
echo.
echo [*] Iniciando agora para teste...
schtasks /Run /TN "%TASK_NAME%"
timeout /t 3 >nul
echo [OK] Daemon rodando em background.
goto :fim

:remover
echo.
echo [*] Removendo tarefa: %TASK_NAME%
schtasks /Delete /TN "%TASK_NAME%" /F
:: Matar processo python do guardian se rodando
taskkill /FI "IMAGENAME eq pythonw.exe" /F >nul 2>&1
for /f "tokens=1" %%P in ('wmic process where "commandline like '%%NC-SCR-FR-115%%'" get processid /value 2^>nul ^| findstr ProcessId') do (
    taskkill /PID %%P /F >nul 2>&1
)
echo [OK] Tarefa removida.
goto :fim

:iniciar_agora
echo.
echo [*] Iniciando Guardian em background (processo isolado)...
set "VBS_TMP=%TEMP%\nc_guardian_run.vbs"
(
echo Set WshShell = CreateObject("WScript.Shell"^)
echo Set env = WshShell.Environment("Process"^)
echo env("PYTHONIOENCODING"^) = "utf-8"
echo env("PYTHONUTF8"^) = "1"
echo env("NC_GUARDIAN_INTERVAL"^) = "%INTERVAL%"
echo env("PYTHONPATH"^) = "%FW%"
echo WshShell.Run "python -u ""%SCRIPT%"" >> ""%LOG%"" 2>&1", 0, False
) > "%VBS_TMP%"
wscript.exe "%VBS_TMP%"
timeout /t 3 >nul
echo [OK] Guardian iniciado! Log em: %LOG%
echo      Para ver: type "%LOG%"
goto :fim

:status
echo.
schtasks /Query /TN "%TASK_NAME%" /FO LIST 2>nul || echo [INFO] Tarefa nao instalada.
echo.
echo Processos Python ativos:
wmic process where "name='python.exe'" get CommandLine,ProcessId /format:list 2>nul | findstr "NC-SCR-FR-115"
goto :fim

:logs
echo.
echo === Ultimo log do Guardian ===
if exist "%LOG%" (
    :: Mostrar ultimas 40 linhas
    powershell -Command "Get-Content '%LOG%' -Tail 40"
) else (
    echo [INFO] Log nao encontrado: %LOG%
    echo        Execute a opcao 3 para iniciar o daemon primeiro.
)
goto :fim

:fim
echo.
pause
endlocal
