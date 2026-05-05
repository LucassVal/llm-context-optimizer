"""---
domain: "core"
layer: "core"
type: "file"
tags: ["init"]
hash: "auto-generated"
---"""
#!/usr/bin/env python3
"""
NeoCortex Core Module

Business logic and core utilities for the NeoCortex framework.
"""

#  Camada 3  NC- named modules (R09: importlib obrigatrio para hyphens)
import importlib as _il

from .agent_service import AgentService, get_agent_service
from .akl_service import AKLService, get_akl_service
from .benchmark_service import BenchmarkService, get_benchmark_service
from .checkpoint_service import CheckpointService, get_checkpoint_service
from .config_service import ConfigService, get_config_service
from .consolidation_service import ConsolidationService, get_consolidation_service
from .cortex_service import CortexService, get_cortex_service
from .export_service import ExportService, get_export_service
from .file_utils import (
    CORTEX_PATH,
    LEDGER_PATH,
    PROJECT_ROOT,
    find_lobes,
    get_lobe_content,
    get_project_root,
    path_exists,
    read_cortex,
    read_json_file,
    read_ledger,
    write_cortex,
    write_json_file,
    write_ledger,
)
from .init_service import InitService, get_init_service
from .kg_service import KGService, get_kg_service
from .ledger_service import LedgerService, get_ledger_service
from .lobe_service import LobeService, get_lobe_service
from .manifest_service import ManifestService, get_manifest_service
from .peers_service import PeersService, get_peers_service
from .profile_manager import (
    check_hierarchical_access,
    create_profile,
    get_timestamp,
    load_json_file,
    load_profile,
    profile_exists,
    save_json_file,
    save_profile,
    validate_profile,
)
from .profile_service import ProfileService, get_profile_service
from .regression_service import RegressionService, get_regression_service
from .security_service import SecurityService, get_security_service

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
    "DryRunPreviewService",
    "get_dry_run_preview_service",
]
