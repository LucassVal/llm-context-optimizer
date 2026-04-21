import importlib.util
import sys
from pathlib import Path


def _import_module(file_name: str, module_name: str):
    file_path = Path(__file__).parent / file_name
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not load module from {file_path}")
    if spec.loader is None:
        raise ImportError(f"Loader is None for module {module_name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


try:
    hook_registry_module = _import_module(
        "NC-HK-FR-001-hook-registry.py", "neocortex.core.hooks.hook_registry"
    )
    HookRegistry = hook_registry_module.HookRegistry
    Hook = hook_registry_module.Hook
except Exception as e:
    print(f"Warning: Could not import HookRegistry: {e}")
    HookRegistry = None
    Hook = None

try:
    simple_hooks_module = _import_module(
        "NC-HK-FR-002-simple-hook.py", "neocortex.core.hooks.simple_hooks"
    )
    LoggingHook = simple_hooks_module.LoggingHook
    TimingHook = simple_hooks_module.TimingHook
    RateLimitHook = simple_hooks_module.RateLimitHook
    AuditHook = simple_hooks_module.AuditHook
except Exception as e:
    print(f"Warning: Could not import simple hooks: {e}")
    LoggingHook = None
    TimingHook = None
    RateLimitHook = None
    AuditHook = None


__all__ = [
    "HookRegistry",
    "Hook",
    "LoggingHook",
    "TimingHook",
    "RateLimitHook",
    "AuditHook",
]
