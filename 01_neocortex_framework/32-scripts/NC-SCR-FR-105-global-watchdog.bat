@echo off
:: NC-SCR-FR-105-global-watchdog.bat
:: NeoCortex Global Watchdog v1.0 — 2026-04-17
:: Verifica e reinicia todos os servicos do stack NeoCortex.
:: Regra de governanca: qualquer servico deve subir em <= 120s. Senao = ERRO.
:: Uso: Scheduled Task a cada 30min OU manualmente.

setlocal EnableDelayedExpansion

:: ============================================================
:: CONFIG
:: ============================================================
set ROOT=%~dp0..\..
set FW=%ROOT%\01_neocortex_framework
set MC_DIR=%ROOT%\DIR-RES-CC-001-claude-leak-workzone\external-refs\mission-control
set PYTHON=C:\Program Files\Python312\python.exe
set LOG_DIR=%ROOT%\DIR-DS-002-audit-logs
set LOG_FILE=%LOG_DIR%\NC-LOG-FR-105-global-watchdog.log
set MAX_LOG_KB=1024
set TIMEOUT_SEC=120
set OK=0
set FAIL=1

:: ============================================================
:: TIMESTAMP
:: ============================================================
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set DT=%%I
set DT=%DT:~0,4%-%DT:~4,2%-%DT:~6,2%T%DT:~8,2%:%DT:~10,2%:%DT:~12,2%

:: ============================================================
:: ROTATE LOG > 1MB
:: ============================================================
if exist "%LOG_FILE%" (
    for %%F in ("%LOG_FILE%") do set /a SZ_KB=%%~zF / 1024
    if !SZ_KB! gtr %MAX_LOG_KB% (
        move /y "%LOG_FILE%" "%LOG_DIR%\NC-LOG-FR-105-watchdog.bak" >nul 2>&1
        echo [%DT%] [INFO] Log rotacionado ^(!SZ_KB!KB^) >> "%LOG_FILE%"
    )
)

echo [%DT%] [START] ===== Watchdog Global NeoCortex ===== >> "%LOG_FILE%"
echo [%DT%] [START] ===== Watchdog Global NeoCortex =====

:: ============================================================
:: FUNCAO DE VERIFICAÇÃO DE PORTA (via netstat)
:: Uso: call :CHECK_PORT <porta> <nome> <resultado_var>
:: ============================================================

:: ============================================================
:: 1. MCP SERVER :8765
:: ============================================================
call :CHECK_PORT 8765 "MCP-Server" MCP_ALIVE
if "!MCP_ALIVE!"=="1" (
    echo [%DT%] [OK]   MCP Server ativo ^(:8765^) >> "%LOG_FILE%"
    echo [OK]   MCP Server :8765
) else (
    echo [%DT%] [WARN] MCP Server DOWN — iniciando ^(stdio via Antigravity^) >> "%LOG_FILE%"
    echo [WARN] MCP Server :8765 DOWN — sera iniciado pelo Antigravity ^(stdio^)
    :: Nota: em modo stdio o Antigravity spawna automaticamente. Nao reiniciar aqui.
)

:: ============================================================
:: 2. HEALTH WRAPPER :8766
:: ============================================================
call :CHECK_PORT 8766 "Health-Wrapper" HW_ALIVE
if "!HW_ALIVE!"=="1" (
    echo [%DT%] [OK]   Health Wrapper ativo ^(:8766^) >> "%LOG_FILE%"
    echo [OK]   Health Wrapper :8766
) else (
    echo [%DT%] [INFO] Health Wrapper :8766 OFF >> "%LOG_FILE%"
    echo [INFO] Health Wrapper :8766 OFF ^(nao critico^)
)

:: ============================================================
:: 3. MISSION CONTROL :3000
:: ============================================================
call :CHECK_PORT 3000 "Mission-Control" MC_ALIVE
if "!MC_ALIVE!"=="1" (
    echo [%DT%] [OK]   Mission Control ativo ^(:3000^) >> "%LOG_FILE%"
    echo [OK]   Mission Control :3000
) else (
    echo [%DT%] [WARN] Mission Control DOWN — iniciando pnpm dev... >> "%LOG_FILE%"
    echo [WARN] Mission Control :3000 DOWN — iniciando...
    if exist "%MC_DIR%\package.json" (
        start "MC-WD" /min cmd /c "cd /d "%MC_DIR%" && pnpm dev >"%LOG_DIR%\NC-LOG-MC-001-mc-dev.log" 2>&1"
        call :WAIT_PORT 3000 "Mission-Control" MC_RESULT
        if "!MC_RESULT!"=="1" (
            echo [%DT%] [OK]   Mission Control iniciado ^(:3000^) >> "%LOG_FILE%"
            echo [OK]   Mission Control :3000 INICIADO
        ) else (
            echo [%DT%] [ERROR] Mission Control NAO subiu em %TIMEOUT_SEC%s >> "%LOG_FILE%"
            echo [ERROR] Mission Control NAO subiu em %TIMEOUT_SEC%s — verificar log:
            echo         %LOG_DIR%\NC-LOG-MC-001-mc-dev.log
        )
    ) else (
        echo [%DT%] [ERROR] MC_DIR nao encontrado: %MC_DIR% >> "%LOG_FILE%"
        echo [ERROR] Diretorio Mission Control nao encontrado
    )
)

:: ============================================================
:: 4. PICOCLAW :18790
:: ============================================================
call :CHECK_PORT_HTTP 18790 "/health" "PicoClaw" PC_ALIVE
if "!PC_ALIVE!"=="1" (
    echo [%DT%] [OK]   PicoClaw gateway ativo ^(:18790^) >> "%LOG_FILE%"
    echo [OK]   PicoClaw :18790
) else (
    echo [%DT%] [WARN] PicoClaw DOWN — iniciando... >> "%LOG_FILE%"
    echo [WARN] PicoClaw :18790 DOWN — iniciando...
    start /min "PicoClaw-WD" picoclaw --port 18790 2>nul
    call :WAIT_PORT 18790 "PicoClaw" PC_RESULT
    if "!PC_RESULT!"=="1" (
        echo [%DT%] [OK]   PicoClaw reiniciado >> "%LOG_FILE%"
        echo [OK]   PicoClaw :18790 REINICIADO
    ) else (
        echo [%DT%] [ERROR] PicoClaw NAO subiu em %TIMEOUT_SEC%s >> "%LOG_FILE%"
        echo [ERROR] PicoClaw NAO subiu em %TIMEOUT_SEC%s
    )
)

echo [%DT%] [END]   ===== Watchdog concluido ===== >> "%LOG_FILE%"
echo.
echo ============================================================
echo    Watchdog concluido. Log: %LOG_FILE%
echo ============================================================
goto :EOF

:: ============================================================
:: SUBROUTINE: :CHECK_PORT <porta> <nome> <var_resultado>
:: Verifica se a porta esta LISTEN via netstat
:: ============================================================
:CHECK_PORT
set _P=%1& set _N=%2& set %3=0
netstat -ano 2>nul | findstr ":%~1 " | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 set %3=1
goto :EOF

:: ============================================================
:: SUBROUTINE: :CHECK_PORT_HTTP <porta> <path> <nome> <var>
:: Verifica via HTTP GET (timeout 5s)
:: ============================================================
:CHECK_PORT_HTTP
set _P=%1& set _PATH=%2& set _N=%3& set %4=0
for /f "tokens=*" %%R in ('powershell -NoProfile -NonInteractive -Command "try{$r=Invoke-WebRequest http://127.0.0.1:%~1%~2 -TimeoutSec 5 -UseBasicParsing -EA Stop;$r.StatusCode}catch{0}" 2^>nul') do (
    if "%%R"=="200" set %4=1
)
goto :EOF

:: ============================================================
:: SUBROUTINE: :WAIT_PORT <porta> <nome> <var_resultado>
:: Aguarda ate TIMEOUT_SEC segundos pela porta ficar LISTEN
:: Retorna 1 se subiu, 0 se timeout
:: ============================================================
:WAIT_PORT
set _WP=%1& set _WN=%2& set %3=0
set /a MAX=%TIMEOUT_SEC% / 3
set /a CNT=0
:WAIT_LOOP
    netstat -ano 2>nul | findstr ":%~1 " | findstr "LISTENING" >nul 2>&1
    if %errorlevel%==0 (
        set %3=1
        goto :EOF
    )
    set /a CNT+=1
    if !CNT! geq !MAX! goto :EOF
    echo    [WAIT] %~2 ::%~1 aguardando... ^(!CNT!/%MAX%^)
    timeout /t 3 /nobreak >nul
goto :WAIT_LOOP
