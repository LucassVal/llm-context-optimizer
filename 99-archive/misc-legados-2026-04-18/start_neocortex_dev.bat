@echo off
REM NC-TOOL SAND-002 — Launcher NeoCortex DEV Sandbox
REM Instancia dev isolada na porta 8766
REM Nao interfere com a instancia de producao (porta 8765)

SET PYTHONUTF8=1
SET PYTHONPATH=C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework
SET NC_CONFIG=DIR-CFG-FR-001-config-main\neocortex_config_dev.yaml
SET NC_ENV=development

echo [NeoCortex DEV] Iniciando instancia sandbox (porta 8766)...
echo [NeoCortex DEV] Config: %NC_CONFIG%
echo [NeoCortex DEV] Lobe dir: .neocortex_dev

"C:\Program Files\Python312\python.exe" -X utf8 -m neocortex.mcp.server ^
  --config "%NC_CONFIG%" ^
  --transport stdio ^
  2>> "C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\NC-LOG-FR-001-hud-audit\neocortex_dev_err.log"
