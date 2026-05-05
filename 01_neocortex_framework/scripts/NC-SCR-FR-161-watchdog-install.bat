@echo off
:: NC-SCR-FR-161-watchdog-install.bat
:: Instala o Stack Watchdog Unificado no Task Scheduler
:: Rode como ADMINISTRADOR uma vez.
::
:: Cria:
::   NeoCortex-Stack-Watchdog  (a cada 5 min, verifica :8765 :4001 :4000 :18790)
:: Desabilita:
::   NeoCortex-PicoClaw-Watchdog  (redundante)

setlocal
set "SCRIPT_DIR=%~dp0"
set "WATCHDOG_PS1=%SCRIPT_DIR%NC-SCR-FR-161-stack-watchdog.ps1"

echo ============================================
echo  NeoCortex Stack Watchdog - Installer
echo ============================================
echo.

:: Verificar se é admin
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [!] Este script precisa ser executado como ADMINISTRADOR.
    echo     Clique com botao direito ^> "Executar como administrador"
    pause
    exit /b 1
)

echo [1/3] Removendo task antiga (NeoCortex-PicoClaw-Watchdog)...
schtasks /end /tn "NeoCortex-PicoClaw-Watchdog" >nul 2>&1
schtasks /delete /tn "NeoCortex-PicoClaw-Watchdog" /f >nul 2>&1
echo   OK - removida ou ja inexistente

echo [2/3] Desabilitando NeoCortex-PicoClaw-Startup (redundante)...
schtasks /change /tn "NeoCortex-PicoClaw-Startup" /disable >nul 2>&1
echo   OK

echo [3/3] Criando NeoCortex-Stack-Watchdog (a cada 5 min)...
schtasks /create /tn "NeoCortex-Stack-Watchdog" /sc MINUTE /mo 5 ^
  /tr "powershell.exe -ExecutionPolicy Bypass -File \"%WATCHDOG_PS1%\"" /f
if %ERRORLEVEL% equ 0 (
    echo   OK - task criada
) else (
    echo   [!] Erro ao criar task (codigo: %ERRORLEVEL%)
    echo   Tente criar manualmente no Task Scheduler:
    echo     Nome: NeoCortex-Stack-Watchdog
    echo     Trigger: A cada 5 minutos
    echo     Acao: powershell.exe -ExecutionPolicy Bypass -File "%WATCHDOG_PS1%"
)

echo.
echo ============================================
echo  Instalacao concluida.
echo  Verifique no Task Scheduler: NeoCortex-Stack-Watchdog
echo ============================================
pause
