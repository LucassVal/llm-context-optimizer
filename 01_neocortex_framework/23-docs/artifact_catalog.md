# Catlogo de Artefatos

*Gerado em: 2026-04-27T18:08:28.324964*

## Estatsticas
- Arquivos Python: 655
- Arquivos YAML: 544

## Arquivos Python
| Arquivo | Propsito | Importaes |
|---------|-----------|-------------|
| `audit_system.py` | System-wide YAML/JSON audit + template coverage check.
Output: audit_results.txt | os, sys, yaml, json, glob ... (+1 mais) |
| `NC-SCR-FR-120-batch-rename-fix.py` | NC-SCR-FR-120 — Batch Rename Fix for SSOT Compliance
Script para corrigir nomes de arquivos que n... | os, re, shutil, json, argparse ... (+2 mais) |
| `NC-SCR-FR-121-update-references.py` | NC-SCR-FR-121 — Update File References After SSOT Rename
Script para atualizar referencias a arqu... | os, re, argparse, datetime.datetime, pathlib.Path ... (+1 mais) |
| `NC-SCR-FR-122-white-label-anonymizer.py` | NC-SCR-FR-122 — White Label Anonymizer for Open Source Release
Script para criar versão anônima d... | os, re, shutil, json, argparse ... (+2 mais) |
| `NC-SCR-FR-162-tray-monitor.py` | NeoCortex MCP Tray Monitor — shows MCP status in system tray. | subprocess, sys, time, threading, os ... (+3 mais) |
| `NC-TEST-FR-201-health-tool-test.py` | NC-TEST-FR-201 — Health Tool Test Script
Test the NC-SUPER-013-health.py tool directly | sys, os, pathlib.Path, neocortex.mcp.tools.NC_SUPER_013_health.neocortex_health, traceback |
| `run_mcp_daemon.py` | Daemon para manter MCP server vivo.
Workaround para bug atexit que fecha servidor. | sys, os, time, signal, threading ... (+4 mais) |
| `start_mcp_server.py` | Start NeoCortex MCP Server with SSE transport

This script starts the MCP server using FastMCP wi... | sys, os, pathlib.Path, neocortex.mcp.server |
| `validate_gov.py` |  | yaml, sys, traceback |
| `_test_lock.py` | Test MCP tool call via SSE | requests, json |
| `_test_mcp.py` |  | sys, json |
| `_test_opencode_mcp.py` | Simulate OpenCode MCP client connection to diagnose Connection closed. | subprocess, json, sys, os, time |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\mcp_server_legacy\NC-MCP-FR-001-mcp-server.py` | NeoCortex MCP Server

Servidor MCP (Model Context Protocol) que expoe as 10 ferramentas multi-aca... | asyncio, os, sys, json, logging ... (+9 mais) |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\add_root_sanitize_event.py` | Add root sanitization event to ledger. | json, datetime |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_antigravity_confirmation.py` | Update ledger and cortex with Antigravity MCP confirmation. | json, datetime, os |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_ledger_status.py` | Update ledger status after PHASE 2 completion. | json, datetime, sys, os |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_phase3_progress.py` | Update ledger and cortex with PHASE 3 progress. | json, datetime |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\verify_mcp.py` | Verify MCP server startup and tool registration. | subprocess, sys, os, json, time ... (+3 mais) |
| `01_neocortex_framework\DIR-CORE-FR-001-core-central\NC_SEC_FR_001_security_utils.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.050252'
  injected_by: NC-SCR-FR-075-genealog... | json, pathlib.Path, typing.Any, typing.Dict, typing.Optional ... (+1 mais) |
| `01_neocortex_framework\DIR-CORE-FR-001-core-central\test_security_integration.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.054253'
  injected_by: NC-SCR-FR-075-genealog... | os, sys, NC_SEC_FR_001_security_utils.can_access, NC_SEC_FR_001_security_utils.load_profile, traceback |
| `01_neocortex_framework\DIR-CORE-FR-001-core-central\update_ledger.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.057249'
  injected_by: NC-SCR-FR-075-genealog... | datetime, json |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-102-deepseek-gateway.py` | NC-SVC-FR-102 - DeepSeek Gateway
Proxy para DeepSeek API com whitelist de modelos.
Porta 4001, AP... | http.server, json, os, sys, time ... (+4 mais) |
| `01_neocortex_framework\DIR-PRF-FR-001-profiles-main\NC-PRF-FR-003-profile-loader.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.100946'
  injected_by: NC-SCR-FR-075-genealog... | json, os, sys, datetime.datetime, pathlib.Path ... (+5 mais) |
| `01_neocortex_framework\DIR-PRF-FR-001-profiles-main\profile_manager.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.926071'
  injected_by: NC-SCR-FR-075-genealog... | json, os, datetime.datetime, pathlib.Path, typing.Any ... (+4 mais) |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\fire_test.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.110028'
  injected_by: NC-SCR-FR-075-genealog... | json, sys, time, pathlib.Path, neocortex.mcp.tools.subserver ... (+2 mais) |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_config_reload.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.115042'
  injected_by: NC-SCR-FR-075-genealog... | os, sys, neocortex.config.get_config |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_mcp_responsive.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.119047'
  injected_by: NC-SCR-FR-075-genealog... | os, sys, neocortex.mcp.server.FAST_MCP_AVAILABLE, neocortex.mcp.server.create_mcp_server |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_modular_server.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.122629'
  injected_by: NC-SCR-FR-075-genealog... | os, sys, neocortex.mcp.server.main, neocortex.mcp.server.mcp, io ... (+3 mais) |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_sanity.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.126663'
  injected_by: NC-SCR-FR-075-genealog... | shutil, sys, tempfile, datetime.datetime, pathlib.Path ... (+23 mais) |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_task.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.131177'
  injected_by: NC-SCR-FR-075-genealog... | sys, traceback, json, neocortex.mcp.tools.task._execute_task |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_tools.py` | ---
domain: "testing"
layer: "test"
type: "TST"
tags: ['testing', 'unit', 'test']
hash: "auto-gen... | os, sys, neocortex.mcp.server.mcp |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TOOL-FR-TEMPLATE\hooks\NC-HK-FR-001-example.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.162874'
  injected_by: NC-SCR-FR-075-genealog... | logging, typing.Dict |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TOOL-FR-TEMPLATE\tests\test_example.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.192714'
  injected_by: NC-SCR-FR-075-genealog... | sys, pathlib.Path, pytest, json, hooks.NC_HK_EXAMPLE.example_pre_tool_use |
| `01_neocortex_framework\hooks\NC-HOOK-PRE-COMMIT-v0.1-20260422.py` | NC-HOOK-PRE-COMMIT-v0.1-20260422.py
Hook de Pré-Commit para Validação Automática

Validações exec... | argparse, json, logging, os, re ... (+13 mais) |
| `01_neocortex_framework\neocortex\config.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:24:01.835250'
  injected_by: NC-SCR-FR-075-genealog... | json, logging, os, pathlib.Path, typing.Any ... (+4 mais) |
| `01_neocortex_framework\neocortex\__init__.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:24:01.856891'
  injected_by: NC-SCR-FR-075-genealog... |  |
| `01_neocortex_framework\neocortex\agent\executor.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.237249'
  injected_by: NC-SCR-FR-075-genealog... | logging, dataclasses.dataclass, dataclasses.field, datetime.datetime, typing.Any ... (+11 mais) |
| `01_neocortex_framework\neocortex\cli\main.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.272695'
  injected_by: NC-SCR-FR-075-genealog... | argparse, sys, pathlib.Path, neocortex.mcp.server.FAST_MCP_AVAILABLE, neocortex.mcp.server.create_mcp_server ... (+5 mais) |
| `01_neocortex_framework\neocortex\cli\__init__.py` | ---
domain: "cli"
layer: "core"
type: "cli"
tags: ["init"]
hash: "auto-generated"
--- |  |
| `01_neocortex_framework\neocortex\core\agent_policy_enforcer.py` | agent_policy_enforcer.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-101-agent-policy-enforc... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\agent_service.py` | agent_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-102-agent-service.py
Preserved ... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\akl_service.py` | akl_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-103-akl-service.py
Preserved for ... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\benchmark_service.py` | benchmark_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-104-benchmark-service.py
Pr... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\cascade_consolidator.py` | cascade_consolidator.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-105-cascade-consolidator... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\checkpoint_service.py` | checkpoint_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-106-checkpoint-service.py
... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\circuit_breaker.py` | circuit_breaker.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-107-circuit-breaker.py
Preser... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\config_service.py` | config_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-108-config-service.py
Preserve... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\consolidation_service.py` | consolidation_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-109-consolidation-servi... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\cortex_service.py` | cortex_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-110-cortex-service.py
Preserve... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\export_service.py` | export_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-111-export-service.py
Preserve... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\file_utils.py` | file_utils.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-112-file-utils.py
Preserved for ba... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\init_service.py` | init_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-113-init-service.py
Preserved fo... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\kg_service.py` | kg_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-114-kg-service.py
Preserved for ba... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\ledger_service.py` | ledger_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-115-ledger-service.py
Preserve... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\lexico_service.py` | lexico_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-116-lexico-service.py
Preserve... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\lobe_service.py` | lobe_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-117-lobe-service.py
Preserved fo... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\logging_config.py` | ---
domain: "core"
layer: "core"
type: "file"
tags: ["logging", "config"]
hash: "auto-generated"
--- | logging, logging.handlers, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\manifest_service.py` | manifest_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-118-manifest-service.py
Pres... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\NC-CFG-FR-001-logging-config.py` | ---
domain: "core"
layer: "core"
type: "file"
tags: ["cfg", "001", "logging", "config"]
hash: "au... | logging, pathlib.Path, services.NC_SVC_FR_001_logging_service.NeoCortexLogger, services.NC_SVC_FR_001_logging_service.get_neocortex_logger, neocortex.config.get_config |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-014-lock-guard.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.812864'
  injected_by: NC-SCR-FR-075-genealog... | fnmatch, logging, time, datetime.datetime, pathlib.Path ... (+6 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-016-kg-service.py` | ---
domain: "core"
layer: "core"
type: "file"
tags: ["service"]
hash: "auto-generated"
--- | typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository, infra.ledger_store.LedgerStore |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-017-policy-loader.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.849342'
  injected_by: NC-SCR-FR-075-genealog... | logging, time, pathlib.Path, typing.Any, typing.Dict ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-022-save-point-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.886808'
  injected_by: NC-SCR-FR-075-genealog... | logging, threading, time, uuid, datetime.datetime ... (+7 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-101-agent-policy-enforcer.py` | NC-CORE-FR-021-agent-policy-enforcer.py — AGENT-001
Carrega e valida policies de agentes locais.
... | __future__.annotations, logging, pathlib.Path, typing.Any, typing.Dict ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-102-agent-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.314170'
  injected_by: NC-SCR-FR-075-genealog... | typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository, neocortex.repositories.LedgerRepository ... (+2 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-103-akl-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.346984'
  injected_by: NC-SCR-FR-075-genealog... | typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository, datetime.datetime ... (+1 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-104-benchmark-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.381741'
  injected_by: NC-SCR-FR-075-genealog... | subprocess, sys, pathlib.Path, typing.Any, typing.Dict |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-105-cascade-consolidator.py` | NC-CORE-FR-022-cascade-consolidator.py — CASC-001
"Sono REM" do NeoCortex: consolida handoffs e l... | __future__.annotations, json, logging, os, urllib.request ... (+12 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-106-checkpoint-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.415422'
  injected_by: NC-SCR-FR-075-genealog... | datetime.datetime, typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-107-circuit-breaker.py` | NC-CORE-FR-020-circuit-breaker.py — SEC-403
Circuit Breaker para agentes locais (Qwen 1.5b/3b).

... | __future__.annotations, hashlib, logging, time, collections.deque ... (+7 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-108-config-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.450283'
  injected_by: NC-SCR-FR-075-genealog... | datetime.datetime, typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository ... (+1 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-109-consolidation-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.485178'
  injected_by: NC-SCR-FR-075-genealog... | typing.Any, typing.Dict, typing.Optional, repositories.CortexRepository, repositories.LedgerRepository ... (+2 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-110-cortex-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.519155'
  injected_by: NC-SCR-FR-075-genealog... | re, typing.Any, typing.Dict, typing.List, typing.Optional ... (+2 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-111-export-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.553027'
  injected_by: NC-SCR-FR-075-genealog... | json, datetime.datetime, typing.Any, typing.Dict, typing.List ... (+8 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-112-file-utils.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.591727'
  injected_by: NC-SCR-FR-075-genealog... | json, logging, pathlib.Path, typing.Any, typing.Dict ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-113-init-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.629720'
  injected_by: NC-SCR-FR-075-genealog... | os, datetime.datetime, pathlib.Path, typing.Any, typing.Dict ... (+6 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-114-kg-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.663790'
  injected_by: NC-SCR-FR-075-genealog... | typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository, infra.ledger_store.LedgerStore |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-115-ledger-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.700591'
  injected_by: NC-SCR-FR-075-genealog... | json, datetime.datetime, typing.Any, typing.Dict, typing.Optional ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-116-lexico-service.py` | NC-CORE-FR-023-lexico-service.py — LEXICO-001
"Neuroplasticidade" do NeoCortex: dicionário semânt... | __future__.annotations, json, logging, os, re ... (+9 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-117-lobe-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.736775'
  injected_by: NC-SCR-FR-075-genealog... | re, typing.Any, typing.Dict, typing.List, typing.Optional ... (+8 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-118-manifest-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.774267'
  injected_by: NC-SCR-FR-075-genealog... | json, logging, os, re, datetime.datetime ... (+15 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-119-peers-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.922343'
  injected_by: NC-SCR-FR-075-genealog... | typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository, infra.ledger_store.LedgerStore |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-120-profile-manager.py` | ---
domain: "core"
layer: "core"
type: "file"
tags: ["profile", "manager"]
hash: "auto-generated"... | json, os, datetime.datetime, pathlib.Path, typing.Any ... (+5 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-121-profile-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.961474'
  injected_by: NC-SCR-FR-075-genealog... | json, typing.Any, typing.Dict, typing.List, typing.Optional ... (+6 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-122-pulse-scheduler.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.998783'
  injected_by: NC-SCR-FR-075-genealog... | logging, threading, time, datetime.datetime, datetime.timedelta ... (+8 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-123-regression-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:58.035114'
  injected_by: NC-SCR-FR-075-genealog... | datetime.datetime, typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository ... (+1 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-124-security-service.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:58.073883'
  injected_by: NC-SCR-FR-075-genealog... | importlib, datetime.datetime, typing.Any, typing.Dict, typing.Optional ... (+5 mais) |
| `01_neocortex_framework\neocortex\core\peers_service.py` | peers_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-119-peers-service.py
Preserved ... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\profile_manager.py` | profile_manager.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-120-profile-manager.py
Preser... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\profile_service.py` | profile_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-121-profile-service.py
Preser... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\pulse_scheduler.py` | pulse_scheduler.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-122-pulse-scheduler.py
Preser... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\regression_service.py` | regression_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-123-regression-service.py
... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\security_service.py` | security_service.py — ALIAS SHIM (DEPRECATED)
Replaced by NC-CORE-FR-124-security-service.py
Pres... | importlib.util, sys, pathlib.Path |
| `01_neocortex_framework\neocortex\core\__init__.py` | ---
domain: "core"
layer: "core"
type: "file"
tags: ["init"]
hash: "auto-generated"
--- | importlib, agent_service.AgentService, agent_service.get_agent_service, akl_service.AKLService, akl_service.get_akl_service ... (+53 mais) |
| `01_neocortex_framework\neocortex\core\adapters\NC-ADP-FR-001-mission-control.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:58.134720'
  injected_by: NC-SCR-FR-075-genealog... | concurrent.futures, json, logging, threading, time ... (+7 mais) |
| `01_neocortex_framework\neocortex\core\adapters\__init__.py` | ---
domain: "core"
layer: "core"
type: "file"
tags: ["init"]
hash: "auto-generated"
--- | importlib |
| `01_neocortex_framework\neocortex\core\config\NC-CFG-FR-002-feature-flags.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:58.184436'
  injected_by: NC-SCR-FR-075-genealog... | logging, os, pathlib.Path, typing.Any, typing.Dict ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\config\NC-CFG-FR-004-project-config.py` | ---
domain: "core"
layer: "core"
type: "file"
tags: ["cfg", "004", "project", "config"]
hash: "au... | json, logging, os, pathlib.Path, typing.Any ... (+6 mais) |
| `01_neocortex_framework\neocortex\core\config\NC-CFG-FR-004-project-loader.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:58.232866'
  injected_by: NC-SCR-FR-075-genealog... | logging, os, pathlib.Path, typing.Any, typing.Dict ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\hooks\NC-HK-FR-001-hook-registry.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:24:02.151220'
  injected_by: NC-SCR-FR-075-genealog... | concurrent.futures, importlib.util, logging, threading, dataclasses.dataclass ... (+11 mais) |

*... e mais 555 arquivos Python.*


## Arquivos YAML
| Arquivo | Propsito | Referncias |
|---------|-----------|-------------|
| `config.yaml` | ── Tier STF/STJ: Raciocínio profundo ── |  |
| `01_neocortex_framework\alerting\NC-ALERT-FR-001-proactive_alerts.yaml` | NEOCORTEX PROACTIVE ALERTING v0.1 |  |
| `01_neocortex_framework\automation\NC-AUTO-FR-001-compliance_enhanced.yaml` | NEOCORTEX COMPLIANCE AUTOMATION ENHANCED v0.4 |  |
| `01_neocortex_framework\automation\NC-AUTO-FR-002-compliance_basic.yaml` | NEOCORTEX COMPLIANCE AUTOMATION v0.3 |  |
| `01_neocortex_framework\constitution\NC-CONST-FR-001-v0.3-20260422.yaml` |  |  |
| `01_neocortex_framework\constitution\NC-CONST-FR-002-evolution_process.yaml` | NEOCORTEX CONSTITUTIONAL EVOLUTION PROCESS v0.1 |  |
| `01_neocortex_framework\DIR-CFG-FR-001-config-main\neocortex_config.yaml` | NeoCortex Configuration |  |
| `01_neocortex_framework\DIR-CFG-FR-001-config-main\neocortex_config_dev.yaml` |  |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-ANALYSIS-FR-001-renaming-plan-review.yaml` | NC-ANALYSIS-FR-001-renaming-plan-review.yaml | DIR-DOC-FR-001-docs-main/renaming_plan.yaml, neocortex/core/security_service.py, neocortex/core/NC-CORE-FR-025-security-service.py ... (+28 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CAT-FR-001-research-catalog.yaml` |  | $temporal/research/NC-ANA-INT-001-synthesis-t0.md, $temporal/research/NC-GOV-CC-001-governance-mcp-insights.yaml, $temporal/research/NC-RES-CC-001-validation-hooks-worker-review.md ... (+3 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CFG-FR-001-agent-policy-template.yaml` | NC-CFG-FR-001 — Template de Política de Agente NeoCortex |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CFG-FR-002-rules-policy.yaml` | NC-CFG-FR-002-rules-policy.yaml | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-DOC-FR-001-ubiquitous-language-dictionary.md, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-FR-002-rules-policy.md, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md ... (+10 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CFG-OP-001-operation-profiles.yaml` | NC-CFG-OP-001 — Perfis de Operação NeoCortex v4 |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-002-ticket-lifecycle.yaml` | NC-GOV-FR-002-ticket-lifecycle.yaml | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-002-ticket-lifecycle.md, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md ... (+5 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-003-ia-governance-rules.yaml` | NC-GOV-FR-003 — Regras de Governança de IA para NeoCortex | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-003-ia-governance-rules.md, reports/governance/2026-04-22/compliance_report.md, Verificar existencia e hash dos arquivos .md/.yaml ... (+1 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-004-fr-artifacts-registry.yaml` |  | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-004-fr-artifacts-registry.md, 01_neocortex_framework/scripts/NC-SCR-FR-001-populate-lobes-ssot.py, 01_neocortex_framework/scripts/NC-SCR-FR-004-governance-validator.py ... (+67 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-005-governance-ecosystem.yaml` | NC-GOV-FR-005 — Mapa do Ecossistema de Governança NeoCortex | neocortex/infra/metrics_store.py, DIR-RES-CC-001-claude-leak-workzone/NC-GOV-CC-001-governance-mcp-insights.yaml, Migrar neocortex_config.yaml → .nc/config.yaml ... (+4 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-006-agent-rights.yaml` | NC-GOV-FR-006 — Agent Rights and Duties |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-008-lobe-taxonomy.yaml` | NC-GOV-FR-008 — Lobe Taxonomy (Memória Institucional) |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-SEC-FR-001-atomic-locks.yaml` | NC-SEC-FR-001 — Atomic Locks: Arquivos Protegidos do NeoCortex |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_analysis_summary.yaml` |  | neocortex/NC-CORE-FR-001-config.py, neocortex/config.py, neocortex/mcp/NC-CORE-FR-026-server.py ... (+266 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan.yaml` |  | neocortex/agent/NC-AGENT-FR-001-executor.py, neocortex/agent/executor.py, neocortex/cli/NC-CLI-FR-001-main.py ... (+171 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan_v2.yaml` |  | neocortex/agent/NC-AGENT-FR-001-executor.py, neocortex/agent/executor.py, neocortex/cli/NC-CLI-FR-001-main.py ... (+345 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan_v2_dedup.yaml` |  | neocortex/agent/NC-AGENT-FR-001-executor.py, neocortex/agent/executor.py, neocortex/cli/NC-CLI-FR-001-main.py ... (+171 mais) |
| `01_neocortex_framework\DIR-DS-001-tickets\NC-DS-FR-118-fix-f841-metrics-store.yaml` |  | 01_neocortex_framework/neocortex/infra/metrics_store.py, DIR-DS-002-audit-logs/NC-DS-FR-118-completion.yaml |
| `01_neocortex_framework\DIR-DS-001-tickets\NC-DS-FR-119-picoclaw-integration-test.yaml` |  | 01_neocortex_framework/05_examples/NC-TEST-FR-119-picoclaw-integration.py, DIR-DS-002-audit-logs/NC-DS-FR-119-completion.yaml |
| `01_neocortex_framework\DIR-DS-001-tickets\NC-DS-FR-120-picoclaw-tool-autoloader.yaml` |  | DIR-DS-002-audit-logs/NC-DS-FR-120-completion.yaml |
| `01_neocortex_framework\DIR-DS-001-tickets\NC-DS-FR-121-lexico-hook-boot-loader.yaml` |  | DIR-DS-002-audit-logs/NC-DS-FR-121-completion.yaml |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-DS-153-handoff-20260420T235000.yaml` | NC-DS-HANDOFF-TEMPLATE.yaml | DIR-DS-002-audit-logs/NC-DS-FR-153-diff.txt, scripts/NC-SCR-FR-148-wal-ttl-pruner.py, 05_examples/NC-TEST-FR-153-ttl-wal-prune.py ... (+2 mais) |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-DS-154-handoff-20260420T205300.yaml` | NC-DS-HANDOFF-TEMPLATE.yaml | 01_neocortex_framework/05_examples/NC-TEST-FR-154-ssot-cross-audit.py, 01_neocortex_framework/05_examples/NC-RPT-FR-154-ssot-cross-audit.json, DIR-DS-002-audit-logs/NC-DS-FR-154-diff.txt |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-DS-FR-118-completion.yaml` |  | 01_neocortex_framework/neocortex/infra/metrics_store.py |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-DS-FR-120-completion.yaml` |  | 01_neocortex_framework/scripts/NC-SCR-FR-145-tool-autoloader.py, 01_neocortex_framework/neocortex/mcp/NC-CFG-FR-005-tool-autoload.yaml, neocortex/mcp/tools/NC-SUPER-016-picoclaw.py |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-DS-FR-121-completion.yaml` |  | 01_neocortex_framework/scripts/NC-SCR-FR-146-hook-boot-loader.py, 01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-005-lexico-boot-loader.py, 01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-006-lexico-hook-chain.py ... (+5 mais) |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-DS-FR-150-completion.yaml` |  | 05_examples/NC-RPT-FR-150-smoke-test-report.json, 05_examples/NC-RPT-FR-150-coverage-gaps.md, scripts/NC-SCR-FR-150-smoke-test.py |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-HANDOFF-FR-021-phase-4-python-mvp.yaml` |  |  |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-HANDOFF-FR-022-status-real.yaml` |  |  |
| `01_neocortex_framework\DIR-DS-002-handoffs\NC-HOFF-FR-002-ciclo2-ciclo3-handoff.yaml` | NC-HOFF-FR-002: Handoff Formal CICLO_2 -> CICLO_3 |  |
| `01_neocortex_framework\DIR-DS-002-handoffs\NC-HOFF-FR-002-summary.yaml` | NC-HOFF-FR-002-SUMMARY: Handoff CICLO_2 -> CICLO_3 (Resumo) |  |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-GOV-TPL-000-root-template.yaml` | NC-GOV-TPL-000-root-template.yaml |  |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-GOV-TPL-001-agent-courier.yaml` | NC-GOV-TPL-001-agent-courier.yaml |  |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TPL-FR-001-template-central-index.yaml` | NC-TPL-FR-001 — Template Central Index | 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-GOV-TPL-000-root-template.yaml, 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-GOV-TPL-001-agent-courier.yaml, 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TPL-FR-002-agent-dispatch.yaml ... (+4 mais) |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TPL-FR-002-agent-dispatch.yaml` | NC-TPL-FR-002-agent-dispatch.yaml | DIR-DS-001-tickets/NC-DS-HANDOFF-TEMPLATE.yaml, 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TPL-FR-001-template-central-index.yaml, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-003-ia-governance-rules.yaml ... (+3 mais) |
| `01_neocortex_framework\governance\rules\NC-GOV-RULES-v0.3-20260422.yaml` | NEOCORTEX GOVERNANCE RULES v0.3 |  |
| `01_neocortex_framework\integration\NC-INT-MEMORY-STATE-LEDGER-v0.3-20260422.yaml` |  |  |
| `01_neocortex_framework\metrics\NC-METRICS-KPIS-v0.1-20260422.yaml` | NEOCORTEX GOVERNANCE METRICS & KPIS v0.1 |  |
| `01_neocortex_framework\monitoring\NC-MON-REAL-TIME-v0.1-20260422.yaml` |  |  |
| `01_neocortex_framework\neocortex\core\config\NC-CFG-FR-004-project-config-schema.yaml` | NC-CFG-FR-004-project-config-schema.yaml |  |
| `01_neocortex_framework\neocortex\core\hooks\NC-CFG-HK-001-hooks.yaml` | NC-CFG-HK-001-hooks.yaml | ../hooks/NC-HK-FR-004-lexico-step0-hook.py |
| `01_neocortex_framework\neocortex\core\hooks\NC-CFG-HK-002-lexico-hooks.yaml` | NC-CFG-HK-002-lexico-hooks.yaml | ../hooks/NC-HK-FR-004-lexico-step0-hook.py, ../hooks/NC-HK-FR-004-lexico-step0-hook.py |
| `01_neocortex_framework\neocortex\mcp\NC-CFG-FR-005-tool-autoload.yaml` | NC-CFG-FR-005: Configuração de auto-loader de ferramentas extras | neocortex/mcp/tools/NC-SUPER-016-picoclaw.py |

*... e mais 494 arquivos YAML.*

## Metadados Completos
Os dados completos esto disponveis em formato JSON:
`DIR-DOC-FR-001-docs-main\artifact_catalog.json`
