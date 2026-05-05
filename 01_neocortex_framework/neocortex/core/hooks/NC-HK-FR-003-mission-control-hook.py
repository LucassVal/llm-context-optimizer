#!/usr/bin/env python3
"""---
NC-HK-FR-003-mission-control-hook.py
---
"""

"""---
NC-HK-FR-003-mission-control-hook.py
---
"""

"""
NC-HK-FR-003-mission-control-hook.py

Hook para enviar eventos de tool calls para o Mission Control activity feed.
Registra-se no HookRegistry e, para cada tool call, envia um report assíncrono.

Uso:
    O hook é registrado automaticamente ao importar este módulo.
    Ou pode ser registrado manualmente via HookRegistry.

Interface:
    on_before(tool_name, args) → report 'tool_call'
    on_after(tool_name, result, duration_ms) → report 'tool_result'
    on_error(tool_name, error) → report 'tool_error'
"""

import importlib.util
import logging
import threading
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Importação dinâmica do adapter Mission Control (R09)
# -----------------------------------------------------------------------------


def load_adapter():
    """Carrega NC-ADP-FR-001-mission-control.py via importlib.util."""
    adapter_path = (
        Path(__file__).parent.parent.parent
        / "core"
        / "adapters"
        / "NC-ADP-FR-001-mission-control.py"
    )
    if not adapter_path.exists():
        logger.error("Adapter não encontrado em %s", adapter_path)
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            "mission_control_adapter", adapter_path
        )
        if spec is None or spec.loader is None:
            logger.error("Falha ao criar spec para adapter")
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        logger.info("Adapter carregado com sucesso para MissionControlHook")
        return module
    except Exception as e:
        logger.error("Erro ao carregar adapter: %s", e, exc_info=True)
        return None


# -----------------------------------------------------------------------------
# MissionControlHook
# -----------------------------------------------------------------------------


class MissionControlHook:
    """Hook que reporta tool calls para o Mission Control."""

    def __init__(self, adapter_module=None):
        """
        Inicializa o hook.

        Args:
            adapter_module: Módulo do adapter Mission Control (opcional).
                Se None, carrega automaticamente.
        """
        self.adapter_module = adapter_module or load_adapter()
        self.adapter = None
        self._lock = threading.Lock()

    def _get_adapter(self):
        """Retorna uma instância do adapter (singleton por hook)."""
        with self._lock:
            if self.adapter is None and self.adapter_module is not None:
                try:
                    config = self.adapter_module.MissionControlConfig(
                        base_url="http://localhost:3000",
                        api_endpoint="/api/adapters",
                        agent_id="neocortex-hook",
                        name="neocortex-hook",
                        role="hook",
                        capabilities=["audit"],
                        metadata={"hook_version": "1.0"},
                        timeout_sec=3,
                    )
                    self.adapter = self.adapter_module.MissionControlAdapter(config)
                    # Registrar o agente? O hook não precisa registrar, apenas reportar.
                    # O registro é feito pelo startup hook.
                except Exception as e:
                    logger.error("Falha ao criar adapter: %s", e)
            return self.adapter

    def on_before(self, tool_name: str, args: Dict[str, Any], **kwargs: Any) -> None:
        """
        Chamado antes da execução da tool.
        Envia evento 'tool_call' para o Mission Control.
        """
        adapter = self._get_adapter()
        if adapter is None:
            logger.debug("Adapter não disponível, skip tool_call report")
            return
        try:
            # Sumarizar args (evitar dados grandes)
            args_summary = {k: type(v).__name__ for k, v in args.items()}
            # Usar o método report fire-and-forget
            adapter.report(
                "tool_call",
                {
                    "tool": tool_name,
                    "args_summary": args_summary,
                    "args_keys": list(args.keys()),
                },
            )
        except Exception as e:
            logger.debug("Falha ao report tool_call: %s", e)

    def on_after(
        self, tool_name: str, result: Any, elapsed_ms: float = 0.0, **kwargs: Any
    ) -> None:
        """
        Chamado após a execução bem-sucedida da tool.
        Envia evento 'tool_result' para o Mission Control.
        """
        adapter = self._get_adapter()
        if adapter is None:
            logger.debug("Adapter não disponível, skip tool_result report")
            return
        try:
            result_type = type(result).__name__
            adapter.report(
                "tool_result",
                {
                    "tool": tool_name,
                    "result_type": result_type,
                    "elapsed_ms": elapsed_ms,
                    "success": True,
                },
            )
        except Exception as e:
            logger.debug("Falha ao report tool_result: %s", e)

    def on_error(self, tool_name: str, error: Exception, **kwargs: Any) -> None:
        """
        Chamado quando a tool levanta uma exceção.
        Envia evento 'tool_error' para o Mission Control.
        """
        adapter = self._get_adapter()
        if adapter is None:
            logger.debug("Adapter não disponível, skip tool_error report")
            return
        try:
            adapter.report(
                "tool_error",
                {
                    "tool": tool_name,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                },
            )
        except Exception as e:
            logger.debug("Falha ao report tool_error: %s", e)


# -----------------------------------------------------------------------------
# Auto-registro no HookRegistry (opcional)
# -----------------------------------------------------------------------------


def register_hook():
    """Registra MissionControlHook no HookRegistry singleton."""
    try:
        # Carregar HookRegistry
        hooks_dir = Path(__file__).parent
        registry_path = hooks_dir / "NC-HK-FR-001-hook-registry.py"
        if not registry_path.exists():
            logger.warning("HookRegistry não encontrado, skip auto-registro")
            return False
        spec = importlib.util.spec_from_file_location("hook_registry", registry_path)
        if spec is None or spec.loader is None:
            logger.error("Falha ao criar spec para HookRegistry")
            return False
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        registry = module.get_hook_registry()
        hook = MissionControlHook()
        # Registrar para os três eventos padrão
        registry.register(
            "mission_control_before",
            module.HookEvent.PRE_TOOL_USE,
            hook.on_before,
        )
        registry.register(
            "mission_control_after",
            module.HookEvent.POST_TOOL_USE,
            hook.on_after,
        )
        registry.register(
            "mission_control_error",
            module.HookEvent.TOOL_ERROR,
            hook.on_error,
        )
        logger.info("MissionControlHook registrado no HookRegistry")
        return True
    except Exception as e:
        logger.error("Falha ao registrar MissionControlHook: %s", e, exc_info=True)
        return False


# Auto-registro ao importar (compatibilidade com NC-HK-FR-002)
if __name__ != "__main__":
    # Registro automático pode ser desabilitado por variável de ambiente
    import os

    if os.getenv("NEOCORTEX_AUTO_REGISTER_HOOKS", "true").lower() == "true":
        register_hook()

# -----------------------------------------------------------------------------
# Teste standalone
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Testando MissionControlHook...")
    hook = MissionControlHook()
    if hook.adapter_module:
        logger.info("Adapter carregado: %s", hook.adapter_module.__file__)
    else:
        logger.error("Adapter não carregado")
    # Teste de registro automático
    success = register_hook()
    logger.info("Auto-registro: %s", success)
    logger.info("Teste concluído.")
