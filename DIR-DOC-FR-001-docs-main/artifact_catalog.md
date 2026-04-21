# Catlogo de Artefatos

*Gerado em: 2026-04-21T20:17:46.443545*

## Estatsticas
- Arquivos Python: 631
- Arquivos YAML: 489

## Arquivos Python
| Arquivo | Propsito | Importaes |
|---------|-----------|-------------|
| `NC-SCR-FR-070-genealogy-builder.py` | NC-SCR-FR-070-genealogy-builder.py
Genealogy Builder - Constri grafo de relaes (imports, ferramen... | os, re, json, logging, datetime ... (+5 mais) |
| `test_lexico.py` | Teste simplificado do LexicoService | sys, os, importlib.util, json, traceback |
| `test_mcp_simple.py` | Teste simples do MCP server | sys, os, neocortex.mcp.server.create_mcp_server, traceback |
| `01_neocortex_framework\fix_shims.py` |  | os, re |
| `01_neocortex_framework\fix_trailing_whitespace.py` | Fix trailing whitespace in metrics_store.py | re |
| `01_neocortex_framework\test_import.py` |  | traceback, neocortex.core.agent_service |
| `01_neocortex_framework\test_vector_scan.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.046729'
  injected_by: NC-SCR-FR-075-genealog... | sys, os, neocortex.core.manifest_service.ManifestService |
| `01_neocortex_framework\05_examples\NC-RPT-117-core-audit.py` | NC-RPT-117-core-audit.py
Audit core/ raiz — classificar 31 arquivos sem prefixo NC

Ticket: NC-DS... | json, re, sys, pathlib.Path, typing.Dict ... (+4 mais) |
| `01_neocortex_framework\05_examples\NC-TEST-119-picoclaw-integration-fixed.py` | NC-TEST-119-picoclaw-integration.py
Teste de integração PICOCLAW — loop dispatch→poll via :18790
... | importlib.util, json, sys, time, urllib.error ... (+7 mais) |
| `01_neocortex_framework\05_examples\NC-TEST-119-picoclaw-integration.py` | NC-TEST-119-picoclaw-integration.py
Teste de integração PICOCLAW — loop dispatch→poll via :18790
... | importlib.util, json, sys, time, urllib.error ... (+9 mais) |
| `01_neocortex_framework\05_examples\NC-TEST-152-savepoint-wal-integration.py` | NC-TEST-152-savepoint-wal-integration.py
Integration test for SavePoint-WAL Bridge (NC-SVC-FR-025... | json, sys, time, pathlib.Path, io ... (+2 mais) |
| `01_neocortex_framework\05_examples\NC-TEST-153-ttl-wal-prune.py` | NC-TEST-153-ttl-wal-prune.py
Teste de integração para NC-SCR-FR-148-wal-ttl-pruner.py

Ticket: NC... | json, subprocess, sys, tempfile, datetime.datetime ... (+7 mais) |
| `01_neocortex_framework\05_examples\NC-TEST-154-ssot-cross-audit.py` | NC-TEST-154-ssot-cross-audit.py
SSOT Cross-Audit Script for NC-DS-154 Compliance Audit.

Objetivo... | json, logging, re, sys, datetime.datetime ... (+7 mais) |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\clean_security.py` | Clean security.py tool module. | pathlib.Path |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\extract_all_tools.py` | Extract all MCP tools from monolithic server file to individual modules. | re, pathlib.Path |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\extract_tools_final.py` | Final extraction of MCP tools with correct indentation. | re, pathlib.Path |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\extract_tools_robust.py` | Robust extraction of MCP tools from monolithic server file. | re, pathlib.Path |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\fix_indentation.py` | Fix indentation for tool modules. | re, pathlib.Path |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\mcp_server_legacy\NC-MCP-FR-001-mcp-server.py` | NeoCortex MCP Server

Servidor MCP (Model Context Protocol) que expoe as 10 ferramentas multi-aca... | asyncio, os, sys, json, logging ... (+9 mais) |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\add_root_sanitize_event.py` | Add root sanitization event to ledger. | json, datetime |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_antigravity_confirmation.py` | Update ledger and cortex with Antigravity MCP confirmation. | json, datetime, os |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_ledger_status.py` | Update ledger status after PHASE 2 completion. | json, datetime, sys, os |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_phase3_progress.py` | Update ledger and cortex with PHASE 3 progress. | json, datetime |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\verify_mcp.py` | Verify MCP server startup and tool registration. | subprocess, sys, os, json, time ... (+3 mais) |
| `01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\add_root_sanitize_event.py` | Add root sanitization event to ledger. | datetime, json |
| `01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\update_antigravity_confirmation.py` | Update ledger and cortex with Antigravity MCP confirmation. | datetime, json |
| `01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\update_ledger_status.py` | Update ledger status after PHASE 2 completion. | datetime, json |
| `01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\verify_mcp.py` | Verify MCP server startup and tool registration. | json, os, subprocess, sys, time ... (+3 mais) |
| `01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\benchmarks_archive\benchmark_fractal_gauntlet.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:24:01.919897'
  injected_by: NC-SCR-FR-075-genealog... | sys, json, requests |
| `01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\benchmarks_archive\benchmark_master_suite.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:24:01.945238'
  injected_by: NC-SCR-FR-075-genealog... | json, os, random, sys, dataclasses.dataclass ... (+1 mais) |
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
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\clean_utf0.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.061527'
  injected_by: NC-SCR-FR-075-genealog... | pathlib.Path |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\extract_tools.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.065541'
  injected_by: NC-SCR-FR-075-genealog... | re, pathlib.Path |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\list_tools.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.068545'
  injected_by: NC-SCR-FR-075-genealog... | os, sys |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\list_tools_simple.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.072559'
  injected_by: NC-SCR-FR-075-genealog... | sys |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\litellm_simple_gateway.py` | LiteLLM Simple Gateway - Proxy simples para Ollama
Porta 4000, compatível com Neocortex | socket, threading, json, time, sys ... (+3 mais) |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\mcp_service_100.py` | MCP SERVICE 100% - NeoCortex Model Context Protocol Server
Servidor standalone com 17 ferramentas... | socket, threading, json, time, sys ... (+1 mais) |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-BOOT-FR-001-mcp-startup.py` | NC-BOOT-FR-001 - MCP Services Startup Script
Inicia todos os serviços MCP com naming convention NC- | subprocess, sys, time, threading, os ... (+1 mais) |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-HUB-FR-001-mcp-hub.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.076586'
  injected_by: NC-SCR-FR-075-genealog... | asyncio, logging, sys, time, uuid ... (+5 mais) |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-100-mcp-server.py` | NC-SVC-FR-100-mcp-server.py - VERSÃO CORRIGIDA

CORREÇÃO: NC-SCR-FR-157
DATA: 2026-04-21
STATUS: ... | sys, json, logging, pathlib.Path |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-101-litellm-gateway.py` | NC-SVC-FR-101 - LiteLLM Gateway Service
Proxy simples para Ollama, porta 4000
Conforme NC-NAM-FR-... | socket, threading, json, time, sys ... (+4 mais) |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\neocortex_mcp.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.080113'
  injected_by: NC-SCR-FR-075-genealog... | asyncio, json, logging, sys, pathlib.Path ... (+8 mais) |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\test_mcp_simple.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.084666'
  injected_by: NC-SCR-FR-075-genealog... | os, sys, neocortex_mcp, traceback |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\test_server_start.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.086671'
  injected_by: NC-SCR-FR-075-genealog... | subprocess, sys, time, traceback |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\test_tools.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.134686'
  injected_by: NC-SCR-FR-075-genealog... | os, sys |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\test_tools_simple.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.096940'
  injected_by: NC-SCR-FR-075-genealog... | os, sys, mcp.server, re, NC_MCP_FR_001_mcp_server ... (+1 mais) |
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
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TOOL-FR-TEMPLATE\hooks\NC-HK-EXAMPLE.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.162874'
  injected_by: NC-SCR-FR-075-genealog... | logging, typing.Dict |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TOOL-FR-TEMPLATE\tests\test_example.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.192714'
  injected_by: NC-SCR-FR-075-genealog... | sys, pathlib.Path, pytest, json, hooks.NC_HK_EXAMPLE.example_pre_tool_use |
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
  injected_by: NC-SCR-FR-075-genealog... | typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository, infra.ledger_store.LedgerStore |
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

*... e mais 531 arquivos Python.*


## Arquivos YAML
| Arquivo | Propsito | Referncias |
|---------|-----------|-------------|
| `.pre-commit-config.yaml` |  |  |
| `config.yaml` | ── Tier STF/STJ: Raciocínio profundo ── |  |
| `NC-DS-115-execution-summary.yaml` |  |  |
| `01_neocortex_framework\DIR-CFG-FR-001-config-main\neocortex_config.yaml` | NeoCortex Configuration |  |
| `01_neocortex_framework\DIR-CFG-FR-001-config-main\neocortex_config_dev.yaml` |  |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-ANALYSIS-FR-001-renaming-plan-review.yaml` | NC-ANALYSIS-FR-001-renaming-plan-review.yaml | DIR-DOC-FR-001-docs-main/renaming_plan.yaml, neocortex/core/security_service.py, neocortex/core/NC-CORE-FR-025-security-service.py ... (+28 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CAT-FR-001-research-catalog.yaml` |  | $temporal/research/NC-ANA-INT-001-synthesis-t0.md, $temporal/research/NC-GOV-CC-001-governance-mcp-insights.yaml, $temporal/research/NC-RES-CC-001-validation-hooks-worker-review.md ... (+3 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CFG-FR-001-agent-policy-template.yaml` |  |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CFG-FR-002-rules-policy.yaml` | NC-CFG-FR-002-rules-policy.yaml | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-DOC-FR-001-ubiquitous-language-dictionary.md, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-FR-002-rules-policy.md, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md ... (+10 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-002-ticket-lifecycle.yaml` | NC-GOV-FR-002-ticket-lifecycle.yaml | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-002-ticket-lifecycle.md, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md ... (+5 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-003-ia-governance-rules.yaml` | NC-GOV-FR-003 — Regras de Governança de IA para NeoCortex | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-003-ia-governance-rules.md, Verificar existência e hash dos arquivos .md/.yaml, 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TPL-FR-002-agent-dispatch.yaml |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-004-fr-artifacts-registry.yaml` |  | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-004-fr-artifacts-registry.md, 01_neocortex_framework/scripts/NC-SCR-FR-001-populate-lobes-ssot.py, 01_neocortex_framework/scripts/NC-SCR-FR-004-governance-validator.py ... (+67 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-005-governance-ecosystem.yaml` |  |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-006-agent-rights.yaml` | NC-GOV-FR-006 — Agent Rights and Duties |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-008-lobe-taxonomy.yaml` | NC-GOV-FR-008 — Lobe Taxonomy (Memória Institucional) |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-SEC-FR-001-atomic-locks.yaml` | NC-SEC-FR-001 — Atomic Locks: Arquivos Protegidos do NeoCortex |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_analysis_summary.yaml` |  | neocortex/NC-CORE-FR-001-config.py, neocortex/config.py, neocortex/mcp/NC-CORE-FR-026-server.py ... (+266 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan.yaml` |  | neocortex/agent/NC-AGENT-FR-001-executor.py, neocortex/agent/executor.py, neocortex/cli/NC-CLI-FR-001-main.py ... (+171 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan_v2.yaml` |  | neocortex/agent/NC-AGENT-FR-001-executor.py, neocortex/agent/executor.py, neocortex/cli/NC-CLI-FR-001-main.py ... (+345 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan_v2_dedup.yaml` |  | neocortex/agent/NC-AGENT-FR-001-executor.py, neocortex/agent/executor.py, neocortex/cli/NC-CLI-FR-001-main.py ... (+171 mais) |
| `01_neocortex_framework\DIR-DS-001-tickets\NC-DS-118-fix-f841-metrics-store.yaml` |  | 01_neocortex_framework/neocortex/infra/metrics_store.py, DIR-DS-002-audit-logs/NC-DS-118-completion.yaml |
| `01_neocortex_framework\DIR-DS-001-tickets\NC-DS-119-picoclaw-integration-test.yaml` |  | 01_neocortex_framework/05_examples/NC-TEST-119-picoclaw-integration.py, DIR-DS-002-audit-logs/NC-DS-119-completion.yaml |
| `01_neocortex_framework\DIR-DS-001-tickets\NC-DS-120-picoclaw-tool-autoloader.yaml` |  | DIR-DS-002-audit-logs/NC-DS-120-completion.yaml |
| `01_neocortex_framework\DIR-DS-001-tickets\NC-DS-121-lexico-hook-boot-loader.yaml` |  | DIR-DS-002-audit-logs/NC-DS-121-completion.yaml |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-DS-120-completion.yaml` |  | 01_neocortex_framework/scripts/NC-SCR-FR-145-tool-autoloader.py, 01_neocortex_framework/neocortex/mcp/NC-CFG-FR-005-tool-autoload.yaml, neocortex/mcp/tools/NC-SUPER-016-picoclaw.py |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-DS-121-completion.yaml` |  | 01_neocortex_framework/scripts/NC-SCR-FR-146-hook-boot-loader.py, 01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-005-lexico-boot-loader.py, 01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-006-lexico-hook-chain.py ... (+5 mais) |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-DS-150-completion.yaml` |  | 05_examples/NC-RPT-150-smoke-test-report.json, 05_examples/NC-RPT-150-coverage-gaps.md, scripts/NC-SCR-FR-150-smoke-test.py |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-DS-153-handoff-20260420T235000.yaml` | NC-DS-HANDOFF-TEMPLATE.yaml | DIR-DS-002-audit-logs/NC-DS-153-diff.txt, scripts/NC-SCR-FR-148-wal-ttl-pruner.py, 05_examples/NC-TEST-153-ttl-wal-prune.py ... (+2 mais) |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-DS-154-handoff-20260420T205300.yaml` | NC-DS-HANDOFF-TEMPLATE.yaml | 01_neocortex_framework/05_examples/NC-TEST-154-ssot-cross-audit.py, 01_neocortex_framework/05_examples/NC-RPT-154-ssot-cross-audit.json, DIR-DS-002-audit-logs/NC-DS-154-diff.txt |
| `01_neocortex_framework\DIR-DS-002-audit-logs\NC-HANDOFF-FR-021-phase-4-python-mvp.yaml` |  |  |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-GOV-TPL-000-root-template.yaml` | NC-GOV-TPL-000-root-template.yaml |  |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-GOV-TPL-001-agent-courier.yaml` | NC-GOV-TPL-001-agent-courier.yaml |  |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TPL-FR-001-template-central-index.yaml` | NC-TPL-FR-001 — Template Central Index | 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-GOV-TPL-000-root-template.yaml, 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-GOV-TPL-001-agent-courier.yaml, 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TPL-FR-002-agent-dispatch.yaml ... (+4 mais) |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TPL-FR-002-agent-dispatch.yaml` | NC-TPL-FR-002-agent-dispatch.yaml | DIR-DS-001-tickets/NC-DS-HANDOFF-TEMPLATE.yaml, 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TPL-FR-001-template-central-index.yaml, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-003-ia-governance-rules.yaml ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\config\NC-CFG-FR-004-project-config-schema.yaml` | NC-CFG-FR-004-project-config-schema.yaml |  |
| `01_neocortex_framework\neocortex\core\hooks\NC-CFG-HK-001-hooks.yaml` | NC-CFG-HK-001-hooks.yaml | ../hooks/NC-HK-FR-004-lexico-step0-hook.py |
| `01_neocortex_framework\neocortex\core\hooks\NC-CFG-HK-002-lexico-hooks.yaml` | NC-CFG-HK-002-lexico-hooks.yaml | ../hooks/NC-HK-FR-004-lexico-step0-hook.py, ../hooks/NC-HK-FR-004-lexico-step0-hook.py |
| `01_neocortex_framework\neocortex\mcp\NC-CFG-FR-005-tool-autoload.yaml` | NC-CFG-FR-005: Configuração de auto-loader de ferramentas extras | neocortex/mcp/tools/NC-SUPER-016-picoclaw.py |
| `02_memory_lobes\$temporal\research\NC-GOV-CC-001-governance-mcp-insights.yaml` |  |  |
| `02_memory_lobes\lobes\courier\neocortex_config.yaml` | Courier-specific configuration |  |
| `02_memory_lobes\lobes\engineer\neocortex_config.yaml` | Engineer-specific configuration |  |
| `DIR-ARC-FR-001-archive-main\LOBE-INT-001-handoff-20260413-153000.yaml` | Salvar em: DIR-DS-002-audit-logs/LOBE-INT-001-handoff-{YYYYMMDD-HHMMSS}.yaml |  |
| `DIR-ARC-FR-001-archive-main\LOBE-INT-003-handoff-20260413T153711.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-CFG-DS-001-agent-policy-from-docs.yaml` | NC-CFG-DS-001-agent-policy.yaml | DIR-DS-001-tickets/NC-DS-HANDOFF-TEMPLATE.yaml |
| `DIR-ARC-FR-001-archive-main\NC-DS-001-handoff-20260413-195155.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-DS-002-handoff-20260413-194024.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-DS-003-handoff-20260413-203500.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-DS-004-handoff-20260413-203500.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-DS-005-handoff-20260413-214100.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-DS-006-handoff-20260413-214100.yaml` |  |  |

*... e mais 439 arquivos YAML.*

## Metadados Completos
Os dados completos esto disponveis em formato JSON:
`DIR-DOC-FR-001-docs-main\artifact_catalog.json`
