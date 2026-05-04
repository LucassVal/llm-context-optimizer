"""---
@Module  mcp domain: "core" layer: "core" type: "file" tags: ["
---
"""


#!/usr/bin/env python3
"""
NeoCortex Core Module

Business logic and core utilities for the NeoCortex framework.
"""

# ── LENIENT IMPORTS (T0-fixed 2026-05-04) ──────────────────
# Cada serviço carregado via importlib direto do NC-CORE-FR-* 
# Falha em um serviço NÃO bloqueia o boot do sistema.
import importlib as _il_mcp
import logging as _log_mcp
_log_mcp.basicConfig(level=_log_mcp.WARNING)
_log = _log_mcp.getLogger("neocortex.core.boot")

def _try_load(pkg_name: str, exports: list):
    """Load NC-CORE-FR-* module via importlib. Returns dict of exported names or {}."""
    try:
        mod = _il_mcp.import_module(pkg_name, package="neocortex.core")
        result = {}
        for name in exports:
            if hasattr(mod, name):
                result[name] = getattr(mod, name)
        return result
    except Exception as e:
        _log.warning(f"Service {pkg_name} unavailable: {e}")
        return {}

# Core services — loaded in dependency order
_agents = _try_load(".NC-CORE-FR-102-agent-service", ["AgentService", "get_agent_service"])
globals().update(_agents)

_akl = _try_load(".NC-CORE-FR-103-akl-service", ["AKLService", "get_akl_service"])
globals().update(_akl)

_bench = _try_load(".NC-CORE-FR-104-benchmark-service", ["BenchmarkService", "get_benchmark_service"])
globals().update(_bench)

_ckpt = _try_load(".NC-CORE-FR-106-checkpoint-service", ["CheckpointService", "get_checkpoint_service"])
globals().update(_ckpt)

_cfg = _try_load(".NC-CORE-FR-108-config-service", ["ConfigService", "get_config_service"])
globals().update(_cfg)

try:
    from ..config import get_config
except Exception:
    def get_config(key=None, default=None):
        return default

_cons = _try_load(".NC-CORE-FR-109-consolidation-service", ["ConsolidationService", "get_consolidation_service"])
globals().update(_cons)

_cortex = _try_load(".NC-CORE-FR-110-cortex-service", ["CortexService", "get_cortex_service"])
globals().update(_cortex)

_exp = _try_load(".NC-CORE-FR-111-export-service", ["ExportService", "get_export_service"])
globals().update(_exp)

_fu = _try_load(".NC-CORE-FR-112-file-utils", ["CORTEX_PATH","LEDGER_PATH","PROJECT_ROOT","find_lobes","get_lobe_content","get_project_root","path_exists","read_cortex","read_json_file","read_ledger","write_cortex","write_json_file","write_ledger"])
globals().update(_fu)

_init = _try_load(".NC-CORE-FR-113-init-service", ["InitService", "get_init_service"])
globals().update(_init)

_kg = _try_load(".NC-CORE-FR-114-kg-service", ["KGService", "get_kg_service"])
globals().update(_kg)

_ledger = _try_load(".NC-CORE-FR-115-ledger-service", ["LedgerService", "get_ledger_service"])
globals().update(_ledger)

_lobe = _try_load(".NC-CORE-FR-117-lobe-service", ["LobeService", "get_lobe_service"])
globals().update(_lobe)

_man = _try_load(".NC-CORE-FR-118-manifest-service", ["ManifestService", "get_manifest_service"])
globals().update(_man)

_peers = _try_load(".NC-CORE-FR-119-peers-service", ["PeersService", "get_peers_service"])
globals().update(_peers)

_pm = _try_load(".NC-CORE-FR-120-profile-manager", ["check_hierarchical_access","create_profile","get_timestamp","load_json_file","load_profile","profile_exists","save_json_file","save_profile","validate_profile"])
globals().update(_pm)

_prof = _try_load(".NC-CORE-FR-121-profile-service", ["ProfileService", "get_profile_service"])
globals().update(_prof)

_reg = _try_load(".NC-CORE-FR-123-regression-service", ["RegressionService", "get_regression_service"])
globals().update(_reg)

_sec = _try_load(".NC-CORE-FR-124-security-service", ["SecurityService", "get_security_service"])
globals().update(_sec)

_il = _il_mcp  # backward compat alias
_search_mod = _il.import_module(".NC-CORE-FR-126-search-service", package="neocortex.core")
get_search_service = _search_mod.get_search_service
SearchService = _search_mod.SearchService

# GAP-005: KnowledgeService (real, substitui stub)
_know_mod = _il.import_module(".NC-CORE-FR-127-knowledge-service", package="neocortex.core")
get_knowledge_service = _know_mod.get_knowledge_service
KnowledgeService = _know_mod.KnowledgeService

# SessionMemoryWriter (real, substitui stub)
_session_mod = _il.import_module(".NC-CORE-FR-128-session-memory-writer", package="neocortex.core")
get_session_memory_writer = _session_mod.get_session_memory_writer
SessionMemoryWriter = _session_mod.SessionMemoryWriter

# DDD Shared Kernel Gateway (T0→T1 entry point)
_gateway_mod = _il.import_module(".NC-CORE-FR-129-shared-kernel-gateway", package="neocortex.core")
get_gateway = _gateway_mod.get_gateway
validate_action = _gateway_mod.validate_action
ConstitutionGateway = _gateway_mod.ConstitutionGateway

# E1: DNA/RNA Genome Replicator
_genome_mod = _il.import_module(".NC-CORE-FR-130-genome-replicator", package="neocortex.core")
get_genome = _genome_mod.get_genome
GenomeReplicator = _genome_mod.GenomeReplicator

# E1b: Federative Pact (CF/88 Art. 1-30)
_pact_mod = _il.import_module(".NC-CORE-FR-131-federative-pact", package="neocortex.core")
get_federative_pact = _pact_mod.get_federative_pact
FederativePact = _pact_mod.FederativePact

# CPC Digital (Lei 13.105/15)
_cpc_mod = _il.import_module(".NC-CORE-FR-132-civil-procedure-code", package="neocortex.core")
get_cpc = _cpc_mod.get_cpc
CivilProcedureCode = _cpc_mod.CivilProcedureCode

_lck = _il.import_module(".NC-CORE-FR-014-lock-guard", package="neocortex.core")
_pol = _il.import_module(".NC-CORE-FR-017-policy-loader", package="neocortex.core")
_sav = _il.import_module(".NC-CORE-FR-022-save-point-service", package="neocortex.core")
_dry = _il.import_module(
    ".services.NC-SVC-FR-014-dry-run-preview", package="neocortex.core"
)

get_lock_guard = _lck.get_lock_guard
get_policy_loader = _pol.get_policy_loader
get_save_point_service = _sav.get_save_point_service
get_dry_run_preview_service = _dry.get_dry_run_preview_service


__all__ = [
    # File utilities
    "read_cortex",
    "write_cortex",
    "read_ledger",
    "write_ledger",
    "find_lobes",
    "get_lobe_content",
    "get_project_root",
    "path_exists",
    "read_json_file",
    "write_json_file",
    "PROJECT_ROOT",
    "CORTEX_PATH",
    "LEDGER_PATH",
    # Profile manager functions
    "load_json_file",
    "save_json_file",
    "get_timestamp",
    "load_profile",
    "save_profile",
    "create_profile",
    "profile_exists",
    "check_hierarchical_access",
    "validate_profile",
    # Services
    "CortexService",
    "get_cortex_service",
    "LedgerService",
    "get_ledger_service",
    "LobeService",
    "get_lobe_service",
    "ProfileService",
    "get_profile_service",
    "RegressionService",
    "get_regression_service",
    "CheckpointService",
    "get_checkpoint_service",
    "ConfigService",
    "get_config_service",
    "InitService",
    "get_init_service",
    "ExportService",
    "get_export_service",
    "ManifestService",
    "get_manifest_service",
    "SecurityService",
    "get_security_service",
    "KGService",
    "get_kg_service",
    "ConsolidationService",
    "get_consolidation_service",
    "AKLService",
    "get_akl_service",
    "AgentService",
    "get_agent_service",
    "BenchmarkService",
    "get_benchmark_service",
    "PeersService",
    "get_peers_service",
    "get_config",
    "DryRunPreviewService",
    "get_dry_run_preview_service",
    "get_search_service",
    "SearchService",
]
