@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
set PYTHON_PATH="C:\Program Files\Python312\python.exe"
set PYTHONPATH=%~dp0
set PYTHONUTF8=1

echo.
echo  =========================================================
echo   NEOCORTEX HUD  v2.1  ^|  2026-04-13  [ + PicoClaw Gateway ]
echo   Sistema de Memoria Hierarquico - Status ao Vivo
echo  =========================================================
echo.

REM ── SPRINT STATUS ─────────────────────────────────────────
echo  [ SPRINT-001 STATUS ]
echo  ─────────────────────────────────────────────────────────
echo  DS-A  Frente A ^| Ticktes: NC-DS-006 (ativo)  =^> NC-DS-008
echo  DS-B  Frente B ^| Tickets: NC-DS-007 (ativo)  =^> NC-DS-009
echo.

REM ── HANDOFFS PENDING ──────────────────────────────────────
echo  [ HANDOFFS PENDING_REVIEW ]
set FOUND_PENDING=0
for %%f in ("%~dp0DIR-DS-002-audit-logs\*.yaml") do (
    findstr /i "PENDING_REVIEW" "%%f" >nul 2>&1
    if not errorlevel 1 (
        echo    [!] %%~nxf
        set FOUND_PENDING=1
    )
)
if !FOUND_PENDING!==0 echo    [OK] Nenhum handoff pendente

echo.

REM ── LOBES ATIVOS ────────────────────────────────────────
echo  [ LOBES DE MEMORIA ]
echo  Use o HUD GUI (NeoCortex_HUD_launcher.bat) para status ao vivo.
echo  Lobes canônicos: NC-LBE-FR-ARCHITECTURE-001, NC-LBE-FR-SECURITY-001
echo.
REM ── TICKETS T1 ATIVOS ─────────────────────────────────────
echo  [ TICKETS T1 ATIVOS (ver NC-TODO-FR-001) ]
echo  PIC-001/002/003: DONE  ^|  PIC-004: pendente  ^|  SEC-403: pendente

echo.
echo  ─────────────────────────────────────────────────────────
echo  Lobes CC (Claude Leak): NC-LBE-CC-001 ativo ^| CC-002..005 pending DS-A/B
echo  HUD-004 (dashboard web interativo): pos-MCP Fase 1
echo  ─────────────────────────────────────────────────────────
echo.

REM ── PICOCLAW GATEWAY ──────────────────────────────────────
echo  [ PICOCLAW GATEWAY :18790 ]
echo  ─────────────────────────────────────────────────────────
for /f "tokens=*" %%i in ('powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri http://127.0.0.1:18790/health -TimeoutSec 2 -UseBasicParsing -EA Stop; Write-Host $r.StatusCode } catch { Write-Host 0 }"') do set PIC_STATUS=%%i
if "%PIC_STATUS%"=="200" (
    echo   [ON ] Gateway ativo em http://127.0.0.1:18790
) else (
    echo   [---] Gateway offline. Iniciando...
    set PICOCLAW_CFG=%~dp0DIR-DS-000-agent-config\NC-CFG-PIC-001-picoclaw-config.json
    if exist "!PICOCLAW_CFG!" (
        start /min "PicoClaw-Gateway" picoclaw --port 18790 --config "!PICOCLAW_CFG!"
    ) else (
        start /min "PicoClaw-Gateway" picoclaw --port 18790
    )
    timeout /t 3 /nobreak >nul
    echo   [OK ] PicoClaw iniciado
)
echo.

echo  Pressione qualquer tecla para iniciar servidor MCP...
echo  (ou feche esta janela para apenas visualizar o HUD)
echo.
pause >nul

cd /d "%~dp001_neocortex_framework"
set PYTHONPATH=%~dp001_neocortex_framework
"C:\Program Files\Python312\python.exe" -m neocortex.mcp.server --transport websocket --host 127.0.0.1 --port 8765
pause
