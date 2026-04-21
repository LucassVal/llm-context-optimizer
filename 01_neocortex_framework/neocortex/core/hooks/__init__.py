"""---
_genealogy:
  injected_at: '2026-04-16T00:24:02.159278'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-HK-FR-002-simple-hook
related_ssot:
  - NC-HK-FR-001-hook-registry
tags:
  - neocortex-other
  - level-0
  - python
---"""
"""
neocortex/core/hooks/__init__.py
Exporta HookRegistry e hooks pr-fabricados.
"""

import importlib.util
import sys
from pathlib import Path

_hooks_dir = Path(__file__).parent


def _load(filename):
    stem = filename.replace(".py", "")
    file_path = _hooks_dir / filename
    spec = importlib.util.spec_from_file_location(stem, file_path)
    if spec is None:
        raise ImportError(f"Could not load spec for {file_path}")
    if spec.loader is None:
        raise ImportError(f"Loader is None for {file_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[stem] = mod
    spec.loader.exec_module(mod)
    return mod


_reg = _load("NC-HK-FR-001-hook-registry.py")
_smpl = _load("NC-HK-FR-002-simple-hook.py")

HookRegistry = _reg.HookRegistry

# Constants for hook events (matching HookRegistry internal keys)
HOOK_BEFORE_TOOL_CALL = "before_tool_call"
HOOK_AFTER_TOOL_CALL = "after_tool_call"
HOOK_ON_ERROR = "on_error"
HOOK_ON_SESSION_START = "session_start"
HOOK_ON_SESSION_END = "session_end"
HOOK_ON_CHECKPOINT = "on_checkpoint"

LoggingHook = _smpl.LoggingHook
TimingHook = _smpl.TimingHook
RateLimitHook = _smpl.RateLimitHook
AuditHook = _smpl.AuditHook

__all__ = [
    "HookRegistry",
    "HOOK_BEFORE_TOOL_CALL",
    "HOOK_AFTER_TOOL_CALL",
    "HOOK_ON_ERROR",
    "HOOK_ON_SESSION_START",
    "HOOK_ON_SESSION_END",
    "HOOK_ON_CHECKPOINT",
    "LoggingHook",
    "TimingHook",
    "RateLimitHook",
    "AuditHook",
]
