# @UBL @UBL @HK-FR | LEXICO: #SYSTEM
#!/usr/bin/env python3
"""---
NC-HK-FR-004 — Conversation Hook
---
"""

"""---
NC-HK-FR-004 — Conversation Hook
---
"""

"""
NC-HK-FR-004 — Conversation Hook
Hook para captura automática de turns de conversação (on_response → turn.record)

Objetivo: interceptar cada resposta MCP e registrar turno automaticamente
Integração: SessionMemoryWriter (NC-SVC-FR-021) + memory_auto tool (NC-TOOL-FR-044)
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Configuração padrão
DEFAULT_CONFIG = {
    "enabled": True,
    "compression": True,
    "max_turns_per_session": 1000,
    "hot_buffer_size": 10,
    "exclude_patterns": ["health", "status", "ping"],  # Patterns para excluir
}

class ConversationHook:
    """Hook para captura automática de turns de conversação."""

    def __init__(self, config: dict | None = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self._session_memory = None
        self._turn_count = 0
        self._last_turn_time = None
        logger.info("ConversationHook inicializado (enabled=%s)", self.config["enabled"])

    def _get_session_memory(self):
        """Obtém instância do SessionMemoryWriter."""
        if self._session_memory is None:
            try:
                # Tentar importar via módulo core
                import importlib
                mod = importlib.import_module(
                    "neocortex.core.services.NC-SVC-FR-021-session-memory-writer"
                )
                self._session_memory = mod.get_session_memory()
            except ImportError:
                # Fallback: importar direto do arquivo
                import importlib.util
                import sys

                # Encontrar caminho do SessionMemoryWriter
                hook_dir = Path(__file__).parent
                svc_path = (
                    hook_dir.parents[1]  # neocortex/
                    / "core" / "services"
                    / "NC-SVC-FR-021-session-memory-writer.py"
                )

                if svc_path.exists():
                    spec = importlib.util.spec_from_file_location("session_memory_writer", svc_path)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        sys.modules["session_memory_writer"] = mod
                        spec.loader.exec_module(mod)
                        self._session_memory = mod.get_session_memory()
                else:
                    logger.warning("SessionMemoryWriter não encontrado em %s", svc_path)

        return self._session_memory

    def _should_record_turn(self, user_message: str, ai_response: str) -> bool:
        """Determina se deve registrar o turno."""
        if not self.config["enabled"]:
            return False

        # Verificar padrões de exclusão
        user_lower = user_message.lower()
        for pattern in self.config["exclude_patterns"]:
            if pattern.lower() in user_lower:
                logger.debug("Turno excluído por pattern: %s", pattern)
                return False

        # Verificar se é muito curto (provavelmente comando, não conversação)
        if len(user_message.strip()) < 5 or len(ai_response.strip()) < 10:
            logger.debug("Turno muito curto, ignorando")
            return False

        return True

    async def on_response(self, context: dict) -> dict:
        """
        Hook chamado após cada resposta do MCP (POST_TOOL_USE).

        Args:
            context: Contexto do evento MCP com user_message, result, etc.

        Returns:
            Dict com resultado do registro
        """
        # Extrair informações do contexto
        user_message = context.get("user_message", "")
        ai_response = context.get("result", {}).get("content", "") if isinstance(context.get("result"), dict) else str(context.get("result", ""))
        {
            "tool": context.get("tool_name", ""),
            "timestamp": context.get("timestamp", datetime.now().isoformat()),
            "session_id": context.get("session_id", ""),
        }
        """
        Hook chamado após cada resposta do MCP.

        Args:
            user_message: Mensagem do usuário
            ai_response: Resposta do AI/MCP
            metadata: Metadados adicionais (tool usado, timestamp, etc.)

        Returns:
            Dict com resultado do registro
        """
        if not self._should_record_turn(user_message, ai_response):
            return {"recorded": False, "reason": "filtered"}

        try:
            smw = self._get_session_memory()
            if not smw:
                return {"recorded": False, "reason": "session_memory_unavailable"}

            # Registrar turno
            entry = smw.turn_record(user_message, ai_response)
            self._turn_count += 1
            self._last_turn_time = datetime.now()

            # Aplicar compressão se configurado
            if self.config["compression"]:
                await self._apply_compression(entry)

            logger.debug("Turno registrado: #%d", self._turn_count)

            # Gerar hot summary periódico (a cada 5 turns)
            if self._turn_count % 5 == 0:
                hot_summary = smw.get_hot_summary_text()
                logger.info("Hot summary (turns %d-%d): %s",
                           self._turn_count - 4, self._turn_count,
                           hot_summary[:100] + "..." if len(hot_summary) > 100 else hot_summary)

            return {
                "recorded": True,
                "turn_number": self._turn_count,
                "entry": entry,
                "hot_buffer_size": len(smw.get_hot_summary()),
            }

        except Exception as e:
            logger.error("Erro ao registrar turno: %s", e, exc_info=True)
            return {"recorded": False, "error": str(e)}

    async def _apply_compression(self, entry: dict) -> None:
        """Aplica compressão via LexicoService se disponível."""
        try:
            # Tentar importar LexicoService
            import importlib
            lexico_mod = importlib.import_module("neocortex.core.lexico_service")
            lexico_service = lexico_mod.get_lexico_service()

            if hasattr(lexico_service, "compress_text"):
                # Comprimir previews
                user_preview = entry.get("user_preview", "")
                ai_summary = entry.get("ai_summary", "")

                if user_preview:
                    compressed_user = lexico_service.compress_text(user_preview, ratio=0.5)
                    entry["user_preview_compressed"] = compressed_user

                if ai_summary:
                    compressed_ai = lexico_service.compress_text(ai_summary, ratio=0.5)
                    entry["ai_summary_compressed"] = compressed_ai

                logger.debug("Compressão aplicada ao turno %d", entry.get("turn"))

        except ImportError:
            # LexicoService não disponível, continuar sem compressão
            pass
        except Exception as e:
            logger.warning("Erro na compressão: %s", e)

    def get_stats(self) -> dict:
        """Retorna estatísticas do hook."""
        smw = self._get_session_memory()
        hot_size = len(smw.get_hot_summary()) if smw else 0

        return {
            "enabled": self.config["enabled"],
            "turns_recorded": self._turn_count,
            "last_turn_time": self._last_turn_time.isoformat() if self._last_turn_time else None,
            "hot_buffer_size": hot_size,
            "compression_enabled": self.config["compression"],
        }

    def update_config(self, new_config: dict) -> dict:
        """Atualiza configuração do hook."""
        old_config = self.config.copy()
        self.config.update(new_config)
        logger.info("Configuração atualizada: %s", new_config)
        return {"old_config": old_config, "new_config": self.config}

# Singleton
_hook_instance: ConversationHook | None = None

def get_conversation_hook(config: dict | None = None) -> ConversationHook:
    """Retorna instância singleton do ConversationHook."""
    global _hook_instance
    if _hook_instance is None:
        _hook_instance = ConversationHook(config)
    return _hook_instance

def register_hook(hook_registry_path: Path | None = None) -> bool:
    """
    Registra o hook no HookRegistry.

    Args:
        hook_registry_path: Caminho para NC-HK-FR-001-hook-registry.py

    Returns:
        True se registro bem-sucedido
    """
    try:
        # Encontrar HookRegistry
        if hook_registry_path is None:
            hook_dir = Path(__file__).parent
            hook_registry_path = hook_dir / "NC-HK-FR-001-hook-registry.py"

        if not hook_registry_path.exists():
            logger.warning("HookRegistry não encontrado em %s", hook_registry_path)
            return False

        # Importar HookRegistry
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("hook_registry", hook_registry_path)
        if not spec or not spec.loader:
            logger.error("Não foi possível carregar HookRegistry")
            return False

        mod = importlib.util.module_from_spec(spec)
        sys.modules["hook_registry"] = mod
        spec.loader.exec_module(mod)

        # Registrar hook
        hook = get_conversation_hook()

        # Verificar se HookRegistry tem método register
        if hasattr(mod, "HookRegistry") and hasattr(mod, "HookEvent"):
            registry = mod.HookRegistry()
            # Usar POST_TOOL_USE como evento mais próximo de "on_response"
            registry.register(
                name="conversation_hook",
                event=mod.HookEvent.POST_TOOL_USE,
                handler=hook.on_response,
                timeout_seconds=5.0,
                enabled=True
            )
            logger.info("ConversationHook registrado no HookRegistry (POST_TOOL_USE)")
            return True
        else:
            logger.error("HookRegistry não tem classes/métodos esperados")
            return False

    except Exception as e:
        logger.error("Erro ao registrar hook: %s", e, exc_info=True)
        return False

# Função de inicialização para ser chamada no boot
def initialize() -> dict:
    """Inicializa e registra o hook."""
    hook = get_conversation_hook()
    registered = register_hook()

    return {
        "hook_initialized": True,
        "hook_registered": registered,
        "config": hook.config,
        "stats": hook.get_stats(),
    }

if __name__ == "__main__":
    # Teste básico (apenas para desenvolvimento)
    import asyncio

    logging.basicConfig(level=logging.INFO)

    async def test():
        hook = get_conversation_hook()
        logger.info("Configuração: %s", hook.config)

        # Testar registro de turno
        result = await hook.on_response({
            "user_message": "Teste de conversação",
            "result": {"content": "Esta é uma resposta de teste para verificar o hook de conversação."},
            "tool_name": "test_tool",
            "timestamp": datetime.now().isoformat(),
            "session_id": "test_session"
        })
        logger.info("Resultado do registro: %s", result)

        # Mostrar estatísticas
        logger.info("Estatísticas: %s", hook.get_stats())

    asyncio.run(test())
