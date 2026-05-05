# Catlogo de Artefatos

*Gerado em: 2026-05-04T13:45:10.508438*

## Estatsticas
- Arquivos Python: 723
- Arquivos YAML: 820

## Arquivos Python
| Arquivo | Propsito | Importaes |
|---------|-----------|-------------|
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\NC-CORE-FR-136-auto-amendment-engine.py` | ---
NC-CORE-FR-136-auto-amendment-engine.py — Motor de Auto-Emenda Constitucional
STEP 0 + Govern... | hashlib, json, logging, collections.Counter, datetime.datetime ... (+7 mais) |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\mcp_server_legacy\NC-MCP-FR-001-mcp-server.py` | ---
alwaysApply: true
description: "Central Cortex  {project_name}. NeoCortex v4.2-Cortex."
--- | asyncio, os, sys, json, logging ... (+9 mais) |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\add_root_sanitize_event.py` | ---
Add root sanitization event to ledger.
--- | json, datetime |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_antigravity_confirmation.py` | ---
Update ledger and cortex with Antigravity MCP confirmation.
--- | json, datetime, os |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_ledger_status.py` | ---
Update ledger status after PHASE 2 completion.
--- | json, datetime, sys, os |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_phase3_progress.py` | ---
Update ledger and cortex with PHASE 3 progress.
--- | json, datetime |
| `01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\verify_mcp.py` | ---
Verify MCP server startup and tool registration.
--- | subprocess, sys, os, json, time ... (+3 mais) |
| `01_neocortex_framework\DIR-CORE-FR-001-core-central\NC-CORE-FR-099-update-ledger.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.057249'
  injected_by: NC-SCR-FR-075-genealog... | datetime, json |
| `01_neocortex_framework\DIR-CORE-FR-001-core-central\NC-SEC-FR-001-security-utils.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.050252'
  injected_by: NC-SCR-FR-075-genealog... | json, pathlib.Path, typing.Any, typing.Dict, typing.Optional ... (+1 mais) |
| `01_neocortex_framework\DIR-CORE-FR-001-core-central\NC-TEST-FR-002-security-integration.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.054253'
  injected_by: NC-SCR-FR-075-genealog... | os, sys, NC_SEC_FR_001_security_utils.can_access, NC_SEC_FR_001_security_utils.load_profile, traceback |
| `01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-102-deepseek-gateway.py` | ---
NC-SVC-FR-102 - DeepSeek Gateway
--- | http.server, json, os, sys, time ... (+4 mais) |
| `01_neocortex_framework\DIR-PRF-FR-001-profiles-main\NC-PRF-FR-003-profile-loader.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.100946'
  injected_by: NC-SCR-FR-075-genealog... | json, os, sys, datetime.datetime, pathlib.Path ... (+5 mais) |
| `01_neocortex_framework\DIR-PRF-FR-001-profiles-main\NC-PRF-FR-004-profile-manager.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.926071'
  injected_by: NC-SCR-FR-075-genealog... | json, os, datetime.datetime, pathlib.Path, typing.Any ... (+4 mais) |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\NC-TEST-FR-001-fire-test.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.110028'
  injected_by: NC-SCR-FR-075-genealog... | json, sys, time, pathlib.Path, neocortex.mcp.tools.subserver ... (+2 mais) |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\NC-TEST-FR-003-config-reload.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.115042'
  injected_by: NC-SCR-FR-075-genealog... | os, sys, neocortex.config.get_config |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\NC-TEST-FR-004-mcp-responsive.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.119047'
  injected_by: NC-SCR-FR-075-genealog... | os, sys, neocortex.mcp.server.FAST_MCP_AVAILABLE, neocortex.mcp.server.create_mcp_server |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\NC-TEST-FR-005-modular-server.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.122629'
  injected_by: NC-SCR-FR-075-genealog... | os, sys, neocortex.mcp.server.main, neocortex.mcp.server.mcp, io ... (+3 mais) |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\NC-TEST-FR-006-sanity.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.126663'
  injected_by: NC-SCR-FR-075-genealog... | shutil, sys, tempfile, datetime.datetime, pathlib.Path ... (+23 mais) |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\NC-TEST-FR-007-task.py` | ---
_genealogy:
  injected_at: '2026-04-16T00:23:57.131177'
  injected_by: NC-SCR-FR-075-genealog... | sys, traceback, json, neocortex.mcp.tools.task._execute_task |
| `01_neocortex_framework\DIR-TEST-FR-001-tests-main\NC-TEST-FR-008-tools.py` | ---
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
| `01_neocortex_framework\neocortex\config.py` |  | importlib.util, sys, pathlib |
| `01_neocortex_framework\neocortex\NC-CFG-FR-002-config.py` | ---
@Module  mcp _genealogy:   injected_at: '2026-04-16T00:24:01.83
--- | json, logging, os, pathlib.Path, typing.Any ... (+4 mais) |
| `01_neocortex_framework\neocortex\__init__.py` | ---
@Module  mcp _genealogy:   injected_at: '2026-04-16T00:24:01.85
--- |  |
| `01_neocortex_framework\neocortex\agent\NC-AGENT-FR-001-executor.py` | ---
@Module  mcp _genealogy:   injected_at: '2026-04-16T00:23:57.23
--- | logging, dataclasses.dataclass, dataclasses.field, datetime.datetime, typing.Any ... (+11 mais) |
| `01_neocortex_framework\neocortex\cli\NC-CLI-FR-001-main.py` | ---
@Module  mcp _genealogy:   injected_at: '2026-04-16T00:23:57.27
--- | argparse, sys, pathlib.Path, neocortex.mcp.server.FAST_MCP_AVAILABLE, neocortex.mcp.server.create_mcp_server ... (+5 mais) |
| `01_neocortex_framework\neocortex\cli\__init__.py` | ---
@Module  mcp domain: "cli" layer: "core" type: "cli" tags: ["in
--- |  |
| `01_neocortex_framework\neocortex\core\NC-CFG-FR-001-logging-config.py` | ---
@Module NC-CFG-FR-001-logging-config mcp domain: "core" layer: "core" type: "file" tags: ["
--- | logging, pathlib.Path, services.NC_SVC_FR_001_logging_service.NeoCortexLogger, services.NC_SVC_FR_001_logging_service.get_neocortex_logger, neocortex.config.get_config |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-014-lock-guard.py` | ---
@Module NC-CORE-FR-014-lock-guard mcp _genealogy:   injected_at: '2026-04-16T00:23:57.81
--- | fnmatch, logging, time, datetime.datetime, pathlib.Path ... (+6 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-016-kg-service.py` | ---
domain: "core"
layer: "core"
type: "file"
tags: ["service"]
hash: "auto-generated"
--- | typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository, infra.ledger_store.LedgerStore |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-017-policy-loader.py` | ---
@Module NC-CORE-FR-017-policy-loader mcp _genealogy:   injected_at: '2026-04-16T00:23:57.84
--- | logging, time, pathlib.Path, typing.Any, typing.Dict ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-022-save-point-service.py` | ---
@Module NC-CORE-FR-022-save-point-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57... | logging, threading, time, uuid, datetime.datetime ... (+7 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-101-agent-policy-enforcer.py` | ---
NC-CORE-FR-101-agent-policy-enforcer.py — AGENT-001
Carrega e valida policies de agentes loca... | __future__.annotations, logging, pathlib.Path, typing.Any, typing.Dict ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-102-agent-service.py` | ---
@Module NC-CORE-FR-102-agent-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.31
--- | typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository, neocortex.repositories.LedgerRepository ... (+2 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-103-akl-service.py` | ---
@Module NC-CORE-FR-103-akl-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.34
--- | typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository, datetime.datetime ... (+1 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-104-benchmark-service.py` | ---
@Module NC-CORE-FR-104-benchmark-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.... | subprocess, sys, pathlib.Path, typing.Any, typing.Dict |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-105-cascade-consolidator.py` | ---
NC-CORE-FR-105-cascade-consolidator.py — CASC-001
"Sono REM" do NeoCortex: consolida handoffs... | __future__.annotations, json, logging, os, urllib.request ... (+11 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-106-checkpoint-service.py` | ---
@Module NC-CORE-FR-106-checkpoint-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57... | datetime.datetime, typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-107-circuit-breaker.py` | ---
NC-CORE-FR-107-circuit-breaker.py — SEC-403
Circuit Breaker para agentes locais (Qwen 1.5b/3b... | __future__.annotations, hashlib, logging, time, collections.deque ... (+6 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-108-config-service.py` | ---
@Module NC-CORE-FR-108-config-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.45
--- | datetime.datetime, typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository ... (+1 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-109-consolidation-service.py` | ---
@Module NC-CORE-FR-109-consolidation-service mcp _genealogy:   injected_at: '2026-04-16T00:23... | typing.Any, typing.Dict, typing.Optional, repositories.CortexRepository, repositories.LedgerRepository ... (+2 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-110-cortex-service.py` | ---
@Module NC-CORE-FR-110-cortex-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.51
--- | re, typing.Any, typing.Dict, typing.List, typing.Optional ... (+2 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-111-export-service.py` | ---
@Module NC-CORE-FR-111-export-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.55
--- | json, datetime.datetime, typing.Any, typing.Dict, typing.List ... (+8 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-112-file-utils.py` | ---
@Module NC-CORE-FR-112-file-utils mcp _genealogy:   injected_at: '2026-04-16T00:23:57.59
--- | json, logging, pathlib.Path, typing.Any, typing.Dict ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-113-init-service.py` | ---
@Module NC-CORE-FR-113-init-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.62
--- | os, datetime.datetime, pathlib.Path, typing.Any, typing.Dict ... (+6 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-114-kg-service.py` | ---
@Module NC-CORE-FR-114-kg-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.66
--- | typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository, infra.ledger_store.LedgerStore |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-115-ledger-service.py` | ---
@Module NC-CORE-FR-115-ledger-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.70
--- | json, datetime.datetime, typing.Any, typing.Dict, typing.Optional ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-116-lexico-service.py` | ---
NC-CORE-FR-116-lexico-service.py — LEXICO-001
"Neuroplasticidade" do NeoCortex: dicionário se... | __future__.annotations, json, logging, os, re ... (+8 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-117-lobe-service.py` | ---
@Module NC-CORE-FR-117-lobe-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.73
--- | re, typing.Any, typing.Dict, typing.List, typing.Optional ... (+9 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-118-manifest-service.py` | ---
@Module NC-CORE-FR-118-manifest-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.7... | json, logging, os, re, datetime.datetime ... (+15 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-119-peers-service.py` | ---
@Module NC-CORE-FR-119-peers-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.92
--- | typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository, infra.ledger_store.LedgerStore |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-120-profile-manager.py` | ---
domain: "core"
layer: "core"
type: "file"
tags: ["profile", "manager"]
hash: "auto-generated"... | json, os, datetime.datetime, pathlib.Path, typing.Any ... (+5 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-121-profile-service.py` | ---
@Module NC-CORE-FR-121-profile-service mcp _genealogy:   injected_at: '2026-04-16T00:23:57.96... | json, typing.Any, typing.Dict, typing.List, typing.Optional ... (+6 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-122-pulse-scheduler.py` | ---
@Module NC-CORE-FR-122-pulse-scheduler mcp _genealogy:   injected_at: '2026-04-16T00:23:57.99... | logging, threading, time, datetime.datetime, datetime.timedelta ... (+8 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-123-regression-service.py` | ---
@Module NC-CORE-FR-123-regression-service mcp _genealogy:   injected_at: '2026-04-16T00:23:58... | datetime.datetime, typing.Any, typing.Dict, typing.Optional, repositories.LedgerRepository ... (+1 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-124-security-service.py` | ---
@Guard NC-CORE-FR-124-security-service mcp _genealogy:   injected_at: '2026-04-16T00:23:58.07... | importlib, datetime.datetime, typing.Any, typing.Dict, typing.Optional ... (+5 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-125-tool-guard.py` | ---
@Tool NC-CORE-FR-125-tool-guard mcp NC-CORE-FR-125-tool-guard.py — STEP 0 + LockGuard
--- | logging, datetime.datetime, pathlib.Path, typing.Any, typing.Dict ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-126-search-service.py` | ---
@Service NC-CORE-FR-126-search-service mcp NC-CORE-FR-126-search-service.py — SearchService (... | logging, pathlib.Path, typing.Any, typing.Dict, typing.Optional ... (+1 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-127-knowledge-service.py` | ---
@Service NC-CORE-FR-127-knowledge-service mcp NC-CORE-FR-127-knowledge-service.py — Knowledge... | logging, pathlib.Path, typing.Any, typing.Dict, typing.Optional ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-128-session-memory-writer.py` | ---
NC-CORE-FR-128-session-memory-writer.py — SessionMemoryWriter (real, substitui stub)
--- | json, logging, datetime.datetime, pathlib.Path, typing.Any ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-129-sandbox.py` | ---
@Gateway NC-CORE-FR-129-shared-kernel-gateway mcp NC-CORE-FR-129-shared-kernel-gateway.py — T... | logging, datetime.datetime, pathlib.Path, typing.Any, typing.Dict ... (+27 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-129-shared-kernel-gateway.py` | ---
@Gateway NC-CORE-FR-129-shared-kernel-gateway mcp NC-CORE-FR-129-shared-kernel-gateway.py — T... | logging, datetime.datetime, pathlib.Path, typing.Any, typing.Dict ... (+26 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-130-genome-replicator.py` | ---
@Replicator NC-CORE-FR-130-genome-replicator mcp NC-CORE-FR-130-genome-replicator.py — DNA/RN... | hashlib, json, logging, shutil, time ... (+8 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-131-federative-pact.py` | ---
@Pact NC-CORE-FR-131-federative-pact mcp NC-CORE-FR-131-federative-pact.py — Pacto Federati
--- | logging, enum.Enum, pathlib.Path, typing.Any, typing.Dict ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-132-civil-procedure-code.py` | ---
@Code NC-CORE-FR-132-civil-procedure-code mcp NC-CORE-FR-132-civil-procedure-code.py — CPC Di... | hashlib, json, logging, datetime.datetime, enum.Enum ... (+12 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-133-regulatory-agencies.py` | ---
@Service NC-CORE-FR-133-regulatory-agencies mcp NC-CORE-FR-133-regulatory-agencies.py — Agênc... | logging, threading, time, collections.defaultdict, datetime.datetime ... (+10 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-134-legislative-process.py` | ---
@Module NC-CORE-FR-134-legislative-process mcp NC-CORE-FR-134-legislative-process.py — Proces... | logging, datetime.datetime, datetime.timedelta, enum.Enum, pathlib.Path ... (+5 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-135-criminal-procedure-code.py` | ---
@Code NC-CORE-FR-135-criminal-procedure-code mcp NC-CORE-FR-135-criminal-procedure-code.py — ... | json, logging, datetime.datetime, datetime.timedelta, enum.Enum ... (+7 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-137-vigilant-cycle.py` | ---
@Module NC-CORE-FR-137-vigilant-cycle mcp NC-CORE-FR-137-vigilant-cycle.py — CICLO 0 Vigilan
--- | json, logging, datetime.datetime, pathlib.Path, typing.Any ... (+5 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-138-judicial-organs.py` | ---
@Audit NC-CORE-FR-138-judicial-organs mcp NC-CORE-FR-138-judicial-organs.py — Órgãos Judicia
--- | logging, datetime.datetime, pathlib.Path, typing.Any, typing.Dict ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-139-orbital-bridge.py` | ---
@Tool NC-CORE-FR-139-orbital-bridge mcp NC-CORE-FR-139-orbital-bridge.py — Ponte Orbital p
--- | importlib.util, datetime.datetime, pathlib.Path, typing.Any, typing.Dict ... (+2 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-140-hierarchy-protocol.py` | ---
@Pact NC-CORE-FR-140-hierarchy-protocol mcp NC-CORE-FR-140-hierarchy-protocol.py — Protocolo ... | json, logging, datetime.datetime, enum.Enum, pathlib.Path ... (+8 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-141-secretariats.py` | ---
@Module NC-CORE-FR-141-secretariats mcp NC-CORE-FR-141-secretariats.py — Secretarias do Po
--- | logging, datetime.datetime, pathlib.Path, typing.Any, typing.Dict ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-142-pulse-scheduler-orbital.py` | ---
@Scheduler NC-CORE-FR-142-pulse-scheduler-orbital mcp NC-CORE-FR-142-pulse-scheduler-orbital.... | json, logging, threading, time, datetime.datetime ... (+19 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-143-deletion-guard.py` | ---
@Guard NC-CORE-FR-143-deletion-guard mcp NC-CORE-FR-143-deletion-guard.py — R05 Enforcement
--- | logging, re, typing.Tuple |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-144-bash-guard.py` | ---
@Guard NC-CORE-FR-144-bash-guard mcp NC-CORE-FR-144-bash-guard.py — Bash Command Guard
--- | json, logging, re, datetime.datetime, pathlib.Path ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-145-lightweight-instances.py` | ---
@Gateway NC-CORE-FR-145-lightweight-instances mcp NC-CORE-FR-145-lightweight-instances.py — I... | json, logging, datetime.datetime, pathlib.Path, typing.Any ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-145-subserver-spawner.py` | ---
@Module NC-CORE-FR-145-subserver-spawner mcp NC-CORE-FR-145-subserver-spawner.py — Sub-Server... | json, logging, socket, subprocess, sys ... (+9 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-146-central-watcher.py` | ---
@Gateway NC-CORE-FR-146-central-watcher mcp NC-CORE-FR-146-central-watcher.py — Vigia Central... | json, logging, threading, collections.defaultdict, datetime.datetime ... (+9 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-147-root-cause-engine.py` | ---
@Engine NC-CORE-FR-147-root-cause-engine mcp NC-CORE-FR-147-root-cause-engine.py — Motor de 5... | json, logging, datetime.datetime, pathlib.Path, typing.Any ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-148-submission-pipeline.py` | ---
@Tool NC-CORE-FR-148-submission-pipeline mcp NC-CORE-FR-148-submission-pipeline.py — Pipeline... | logging, re, subprocess, sys, datetime.datetime ... (+12 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-149-full-system-audit.py` | ---
---
--- | json, logging, sys, datetime.datetime, pathlib.Path ... (+14 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-150-techniques-audit.py` | ---
@Audit NC-CORE-FR-150-techniques-audit mcp NC-CORE-FR-150-techniques-audit.py — Auditoria REA... | os, re, datetime.datetime, pathlib.Path, typing.Dict |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-151-missing-techniques.py` | ---
@Module NC-CORE-FR-151-missing-techniques mcp NC-CORE-FR-151-missing-techniques.py — Motores ... | json, os, re, datetime.datetime, pathlib.Path ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-152-eisenhower-real.py` | ---
@Engine NC-CORE-FR-152-eisenhower-real mcp NC-CORE-FR-152-eisenhower-real.py — Conecta Eisenh... | os, pathlib, datetime.datetime, typing.Dict, typing.List ... (+1 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-153-pareto-real.py` | ---
@Engine NC-CORE-FR-153-pareto-real mcp NC-CORE-FR-153-pareto-real.py — Conecta ParetoEngi
--- | os, pathlib, sqlite3, datetime.datetime, typing.Dict ... (+1 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-154-corporate-engines.py` | ---
@Engine NC-CORE-FR-154-corporate-engines mcp NC-CORE-FR-154-corporate-engines.py — Motores Co... | json, os, pathlib, sqlite3, datetime.datetime ... (+8 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-155-resiliency-engine.py` | ---
@Engine NC-CORE-FR-155-resiliency-engine mcp NC-CORE-FR-155-resiliency-engine.py — Bloco 4: I... | json, os, pathlib, threading, time ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-156-ai-governance.py` | ---
@Audit NC-CORE-FR-156-ai-governance mcp NC-CORE-FR-156-ai-governance.py — Bloco 5: Governa
--- | hashlib, json, os, pathlib, re ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-157-bsc-swot.py` | ---
@Module NC-CORE-FR-157-bsc-swot mcp NC-CORE-FR-157-bsc-swot.py — Bloco 3: BSC + SWOT (
--- | os, pathlib, sqlite3, subprocess, sys ... (+3 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-158-system-integrity.py` | ---
@Audit NC-CORE-FR-158-system-integrity mcp NC-CORE-FR-158-system-integrity.py — 4 Checks de I... | os, pathlib, re, datetime.datetime, typing.Dict ... (+1 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-159-crypto-integrity.py` | ---
@Module NC-CORE-FR-159-crypto-integrity mcp NC-CORE-FR-159-crypto-integrity.py — Central de C... | hashlib, json, os, pathlib, datetime.datetime ... (+1 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-160-advanced-resilience.py` | ---
@Module NC-CORE-FR-160-advanced-resilience mcp NC-CORE-FR-160-advanced-resilience.py — Bloco ... | os, pathlib, datetime.datetime, typing.Dict, sqlite3 |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-161-regulatory-compliance.py` | ---
---
--- | os, pathlib, datetime.datetime, typing.Dict |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-162-strangler-fig.py` | ---
@Code NC-CORE-FR-162-strangler-fig mcp NC-CORE-FR-162-strangler-fig.py — R68 Strangler Fi
--- | json, os, pathlib, datetime.datetime, typing.Dict |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-163-ssot-reporter.py` | ---
@Reporter NC-CORE-FR-163-ssot-reporter mcp NC-CORE-FR-163-ssot-reporter.py — R117: SSOT Statu... | json, os, pathlib, re, socket ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-164-claim-validator.py` | ---
@Validator NC-CORE-FR-164-claim-validator mcp NC-CORE-FR-164-claim-validator.py — R21 Enforce... | json, os, pathlib, re, typing.Dict ... (+5 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-165-semantic-router.py` | ---
@Router NC-CORE-FR-165-semantic-router mcp NC-CORE-FR-165-semantic-router.py — Semantic Route... | json, os, pathlib, re, typing.Any ... (+4 mais) |
| `01_neocortex_framework\neocortex\core\NC-CORE-FR-166-domain-routers.py` | ---
@Router NC-CORE-FR-166-domain-routers mcp NC-CORE-FR-166-domain-routers.py — Domain Routers
--- | os, pathlib, re, datetime.datetime, typing.Any ... (+4 mais) |

*... e mais 623 arquivos Python.*


## Arquivos YAML
| Arquivo | Propsito | Referncias |
|---------|-----------|-------------|
| `01_neocortex_framework\DIR-CFG-FR-001-config-main\neocortex_config.yaml` | ── 3 W's (Auto de Infração) ── |  |
| `01_neocortex_framework\DIR-CFG-FR-001-config-main\neocortex_config_dev.yaml` | ── 3 W's (Auto de Infração) ── |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-ANALYSIS-FR-001-renaming-plan-review.yaml` | NC-ANALYSIS-FR-001-renaming-plan-review.yaml | DIR-DOC-FR-001-docs-main/renaming_plan.yaml, neocortex/core/security_service.py, neocortex/core/NC-CORE-FR-025-security-service.py ... (+28 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-ARC-FR-002-architecture-blueprint.yaml` | ── 3 W's (Auto de Infração) ── |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CAT-FR-001-research-catalog.yaml` |  | $temporal/research/NC-ANA-INT-001-synthesis-t0.md, $temporal/research/NC-GOV-CC-001-governance-mcp-insights.yaml, $temporal/research/NC-RES-CC-001-validation-hooks-worker-review.md ... (+3 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CFG-FR-001-agent-policy-template.yaml` | ── 3 W's (Auto de Infração) ── |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CFG-FR-002-rules-policy.yaml` | ── 3 W's (Auto de Infração) ── | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-DOC-FR-001-ubiquitous-language-dictionary.md, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-FR-002-rules-policy.md, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md ... (+10 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CFG-OP-001-operation-profiles.yaml` | ── 3 W's (Auto de Infração) ── |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CHG-FR-001-changelog.yaml` | NC-CHG-FR-001 — Changelog Unificado + Kaizen v1.0 | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-002-ticket-lifecycle.yaml` | ── 3 W's (Auto de Infração) ── | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-002-ticket-lifecycle.md, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md ... (+5 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-003-ia-governance-rules.yaml` | ── 3 W's (Auto de Infração) ── | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-003-ia-governance-rules.md, reports/governance/2026-04-22/compliance_report.md, Verificar existencia e hash dos arquivos .md/.yaml ... (+1 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-004-fr-artifacts-registry.yaml` | ── 3 W's (Auto de Infração) ── | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-004-fr-artifacts-registry.md, 01_neocortex_framework/scripts/NC-SCR-FR-001-populate-lobes-ssot.py, 01_neocortex_framework/scripts/NC-SCR-FR-004-governance-validator.py ... (+67 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-005-governance-ecosystem.yaml` | ── 3 W's (Auto de Infração) ── | neocortex/infra/metrics_store.py, DIR-RES-CC-001-claude-leak-workzone/NC-GOV-CC-001-governance-mcp-insights.yaml, Migrar neocortex_config.yaml → .nc/config.yaml ... (+4 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-006-agent-rights.yaml` | ── 3 W's (Auto de Infração) ── |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-008-lobe-taxonomy.yaml` | ── 3 W's (Auto de Infração) ── |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-MAP-FR-001-structural-maps.yaml` | NC-MAP-FR-001 — Mapas Estruturais Consolidados v1.0 | DIR-DS-002-audit-logs/NC-DS-SESS-*.yaml, DIR-DS-002-audit-logs/NC-DS-*-handoff-*.yaml, DIR-DOC-FR-001-docs-main/artifact_catalog.json |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-SEC-FR-001-atomic-locks.yaml` | ── 3 W's (Auto de Infração) ── |  |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_analysis_summary.yaml` |  | neocortex/NC-CORE-FR-001-config.py, neocortex/config.py, neocortex/mcp/NC-CORE-FR-026-server.py ... (+266 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan.yaml` |  | neocortex/agent/NC-AGENT-FR-001-executor.py, neocortex/agent/executor.py, neocortex/cli/NC-CLI-FR-001-main.py ... (+171 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan_v2.yaml` |  | neocortex/agent/NC-AGENT-FR-001-executor.py, neocortex/agent/executor.py, neocortex/cli/NC-CLI-FR-001-main.py ... (+345 mais) |
| `01_neocortex_framework\DIR-DOC-FR-001-docs-main\renaming_plan_v2_dedup.yaml` |  | neocortex/agent/NC-AGENT-FR-001-executor.py, neocortex/agent/executor.py, neocortex/cli/NC-CLI-FR-001-main.py ... (+171 mais) |
| `01_neocortex_framework\DIR-DS-002-handoffs\NC-HOFF-FR-002-ciclo2-ciclo3-handoff.yaml` | NC-HOFF-FR-002: Handoff Formal CICLO_2 -> CICLO_3 |  |
| `01_neocortex_framework\DIR-DS-002-handoffs\NC-HOFF-FR-002-summary.yaml` | NC-HOFF-FR-002-SUMMARY: Handoff CICLO_2 -> CICLO_3 (Resumo) |  |
| `01_neocortex_framework\DIR-DS-003-entry-locks\active-zones.yaml` | Active Write Zones Registry |  |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-GOV-TPL-000-root-template.yaml` | NC-GOV-TPL-000-root-template.yaml |  |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-GOV-TPL-001-agent-courier.yaml` | NC-GOV-TPL-001-agent-courier.yaml |  |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TPL-FR-001-template-central-index.yaml` | ── 3 W's (Auto de Infração) ── | 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-GOV-TPL-000-root-template.yaml, 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-GOV-TPL-001-agent-courier.yaml, 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TPL-FR-002-agent-dispatch.yaml ... (+4 mais) |
| `01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TPL-FR-002-agent-dispatch.yaml` | ── 3 W's (Auto de Infração) ── | DIR-DS-001-tickets/NC-DS-HANDOFF-TEMPLATE.yaml, 01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TPL-FR-001-template-central-index.yaml, 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-GOV-FR-003-ia-governance-rules.yaml ... (+3 mais) |
| `01_neocortex_framework\governance\rules\NC-GOV-RULES-v0.3-20260422.yaml` | ── 3 W's (Auto de Infração) ── |  |
| `01_neocortex_framework\neocortex\core\config\NC-CFG-FR-004-project-config-schema.yaml` | ── 3 W's (Auto de Infração) ── |  |
| `01_neocortex_framework\neocortex\core\hooks\NC-CFG-HK-001-hooks.yaml` | ── 3 W's (Auto de Infração) ── | ../hooks/NC-HK-FR-004-lexico-step0-hook.py |
| `01_neocortex_framework\neocortex\core\hooks\NC-CFG-HK-002-lexico-hooks.yaml` | NC-CFG-HK-002-lexico-hooks.yaml | ../hooks/NC-HK-FR-004-lexico-step0-hook.py, ../hooks/NC-HK-FR-004-lexico-step0-hook.py |
| `01_neocortex_framework\neocortex\mcp\NC-CFG-FR-005-tool-autoload.yaml` | ── 3 W's (Auto de Infração) ── | neocortex/mcp/tools/NC-SUPER-016-picoclaw.py |
| `02_memory_lobes\_INDEX.yaml` |  |  |
| `02_memory_lobes\lobes\courier\neocortex_config.yaml` | Courier-specific configuration |  |
| `02_memory_lobes\lobes\engineer\neocortex_config.yaml` | Engineer-specific configuration |  |
| `03_external_integrations\openclaude\.github\ISSUE_TEMPLATE\config.yml` |  |  |
| `03_external_integrations\openclaude\.github\workflows\pr-checks.yml` |  | python/requirements.txt, python -m pip install -r python/requirements.txt |
| `03_external_integrations\openclaude\.github\workflows\release.yml` |  |  |
| `DIR-ARC-FR-001-archive-main\LOBE-INT-001-handoff-20260413-153000.yaml` | Salvar em: DIR-DS-002-audit-logs/LOBE-INT-001-handoff-{YYYYMMDD-HHMMSS}.yaml |  |
| `DIR-ARC-FR-001-archive-main\LOBE-INT-003-handoff-20260413T153711.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-CFG-DS-001-agent-policy-from-docs.yaml` | NC-CFG-DS-001-agent-policy.yaml | DIR-DS-001-tickets/NC-DS-HANDOFF-TEMPLATE.yaml |
| `DIR-ARC-FR-001-archive-main\NC-DS-001-handoff-20260413-195155.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-DS-002-handoff-20260413-194024.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-DS-003-handoff-20260413-203500.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-DS-004-handoff-20260413-203500.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-DS-005-handoff-20260413-214100.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-DS-006-handoff-20260413-214100.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-DS-007-handoff-20260414-004610.yaml` |  |  |
| `DIR-ARC-FR-001-archive-main\NC-DS-008-handoff-20260414-004024.yaml` |  |  |

*... e mais 770 arquivos YAML.*

## Metadados Completos
Os dados completos esto disponveis em formato JSON:
`DIR-DOC-FR-001-docs-main\artifact_catalog.json`
