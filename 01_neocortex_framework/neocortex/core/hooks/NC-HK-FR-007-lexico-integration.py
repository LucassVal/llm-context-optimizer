#!/usr/bin/env python3
"""---
NC-HK-FR-007-lexico-integration.py
---
"""

"""---
NC-HK-FR-007-lexico-integration.py
---
"""

"""
NC-HK-FR-007-lexico-integration.py
LEXICO-007 — Integração simplificada do sistema de hooks lexicais.

Versão simplificada que evita problemas de importação com nomes contendo hífen.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class LexicoIntegrationService:
    """Serviço de integração simplificado."""

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path
        self._initialized = False

    def initialize(self) -> bool:
        """Inicializa o serviço de integração."""
        if self._initialized:
            logger.warning("Serviço já inicializado")
            return True

        try:
            # Carregar script de boot loader
            self._load_boot_loader()
            self._initialized = True
            logger.info("Serviço de integração lexical inicializado")
            return True

        except Exception as e:
            logger.error(f"Falha na inicialização: {e}")
            return False

    def _load_boot_loader(self):
        """Carrega o boot loader de hooks."""
        try:
            # Usar o script NC-SCR-FR-146 que já foi criado
            script_path = Path(__file__).parent.parent.parent / "scripts" / "NC-SCR-FR-146-hook-boot-loader.py"

            if not script_path.exists():
                raise FileNotFoundError(f"Script não encontrado: {script_path}")

            # Importar dinamicamente
            import importlib.util
            spec = importlib.util.spec_from_file_location("boot_loader", script_path)
            if spec is None:
                raise ImportError(f"Não foi possível criar spec para {script_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Executar função main para carregar hooks
            if hasattr(module, "main"):
                hooks = module.main()
                logger.info(f"Hooks carregados: {hooks}")
            else:
                logger.warning("Função main não encontrada no script")

        except Exception as e:
            logger.error(f"Erro ao carregar boot loader: {e}")
            raise

    def get_status(self) -> dict:
        """Retorna status do serviço."""
        return {
            "initialized": self._initialized,
            "config_path": str(self.config_path) if self.config_path else None
        }

    def shutdown(self):
        """Desliga o serviço."""
        self._initialized = False
        logger.info("Serviço de integração lexical desligado")


# Singleton
_integration_service = None

def get_integration_service(config_path: Path | None = None):
    """Singleton do serviço de integração."""
    global _integration_service
    if _integration_service is None:
        _integration_service = LexicoIntegrationService(config_path)
    return _integration_service


if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(level=logging.INFO)

    service = LexicoIntegrationService()
    if service.initialize():
        print("✅ Serviço inicializado com sucesso")
        print(f"Status: {service.get_status()}")
        service.shutdown()
    else:
        print("❌ Falha na inicialização")
