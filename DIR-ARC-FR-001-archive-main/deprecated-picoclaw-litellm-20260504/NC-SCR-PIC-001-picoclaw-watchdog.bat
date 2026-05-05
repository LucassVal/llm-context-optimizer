@echo off
:: NC-SCR-PIC-001-picoclaw-watchdog.bat
:: NeoCortex PicoClaw Watchdog v1.0 — 2026-04-13
:: Garante que o gateway PicoClaw esta rodando na porta 18790.
:: Usado tanto no startup quanto pelo Scheduled Task (a cada 30 min).

setlocal EnableDelayedExpansion

:: ============================================================
:: CONFIG
:: ============================================================
set PICOCLAW_EXE=picoclaw
set PICOCLAW_PORT=18790
set PICOCLAW_CONFIG=%~dp0..\..\..\DIR-DS-000-agent-config\NC-CFG-PIC-001-picoclaw-config.json
set LOG_DIR=%~dp0..\..\..\DIR-DS-002-audit-logs
set LOG_FILE=%LOG_DIR%\NC-LOG-PIC-001-watchdog.log
set MAX_LOG_KB=512

:: ============================================================
:: TIMESTAMP
:: ============================================================
for /f "tokens=1-6 delims=/:. " %%a in ("%date% %time%") do (
    set DT=%%c-%%b-%%a %%d:%%e:%%f
)

:: ============================================================
:: ROTATE LOG SE > 512KB
:: ============================================================
if exist "%LOG_FILE%" (
    for %%F in ("%LOG_FILE%") do (
        set SZ=%%~zF
        set /a SZ_KB=!SZ! / 1024
        if !SZ_KB! gtr %MAX_LOG_KB% (
            copy /y "%LOG_FILE%" "%LOG_DIR%\NC-LOG-PIC-001-watchdog.bak" >nul 2>&1
            del /f /q "%LOG_FILE%" >nul 2>&1
            echo [%DT%] LOG rotacionado (era !SZ_KB!KB) >> "%LOG_FILE%"
        )
    )
)

:: ============================================================
:: VERIFICA SE GATEWAY ESTA RESPONDENDO NA PORTA 18790
:: ============================================================
set ALIVE=0
for /f "tokens=*" %%i in ('powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri http://127.0.0.1:%PICOCLAW_PORT%/health -TimeoutSec 3 -UseBasicParsing -EA Stop; Write-Host $r.StatusCode } catch { Write-Host 0 }"') do (
    set HTTP_STATUS=%%i
    if "%%i"=="200" set ALIVE=1
)

:: ============================================================
:: GATEWAY VIVO — NAO FAZ NADA
:: ============================================================
if "%ALIVE%"=="1" (
    echo [%DT%] [OK] PicoClaw gateway ativo (HTTP 200 em :%PICOCLAW_PORT%) >> "%LOG_FILE%"
    goto :EOF
)

:: ============================================================
:: GATEWAY MORTO — (RE)INICIA
:: ============================================================
echo [%DT%] [WARN] Gateway offline — iniciando PicoClaw... >> "%LOG_FILE%"

:: Mata residuos se existir
taskkill /f /im picoclaw.exe >nul 2>&1

:: Aguarda 1s
timeout /t 1 /nobreak >nul

:: Inicia gateway em background (janela minimizada, separada)
if exist "%PICOCLAW_CONFIG%" (
    start /min "PicoClaw-Gateway" %PICOCLAW_EXE% --port %PICOCLAW_PORT% --config "%PICOCLAW_CONFIG%"
) else (
    start /min "PicoClaw-Gateway" %PICOCLAW_EXE% --port %PICOCLAW_PORT%
)

:: Aguarda 5s e verifica se subiu
timeout /t 5 /nobreak >nul

set ALIVE2=0
for /f "tokens=*" %%i in ('powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri http://127.0.0.1:%PICOCLAW_PORT%/health -TimeoutSec 4 -UseBasicParsing -EA Stop; Write-Host $r.StatusCode } catch { Write-Host 0 }"') do (
    if "%%i"=="200" set ALIVE2=1
)

if "%ALIVE2%"=="1" (
    echo [%DT%] [RESTART_OK] Gateway reiniciado com sucesso em :%PICOCLAW_PORT% >> "%LOG_FILE%"
) else (
    echo [%DT%] [ERROR] Falha ao reiniciar gateway! Verificar config em NC-CFG-PIC-001 >> "%LOG_FILE%"
)

endlocal
