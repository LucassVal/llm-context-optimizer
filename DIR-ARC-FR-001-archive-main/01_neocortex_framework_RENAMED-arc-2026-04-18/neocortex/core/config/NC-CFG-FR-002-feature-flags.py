"""---
domain: "core"
layer: "core"
type: "file"
tags: ["cfg", "002", "feature", "flags"]
hash: "auto-generated"
---"""
"""
NC-CFG-FR-002-feature-flags.py
FR-CFG-002  FeatureFlagService: Flags de funcionalidade com cache TTL 1h.

L flags de neocortex_config.yaml (seo feature_flags).
Cache TTL 1h usando cachetools.TTLCache.
Suporta feature flags via env var (NEOCORTEX_FF_<FLAG>=true).
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict

import platformdirs
from cachetools import TTLCache
from ruamel.yaml import YAML

logger = logging.getLogger(__name__)


class FeatureFlagService:
    """Gerencia feature flags com cache TTL 1h.

    Interface pblica:
      is_enabled(flag_name: str) -> bool
      get_flag(flag_name: str, default=None) -> Any
      reload() -> None
      list_flags() -> Dict[str, Any]

    Flags padro do sistema (conforme @STRATEGY):
      - kairos_channels: bool (KAIROS_CHANNELS env var)
      - kairos_push_notification: bool
      - mentor_step0: bool (default True)
      - rate_limit_enabled: bool (default True)
    """

    # Flags padro (fallback se config no existir)
    _DEFAULTS: Dict[str, Any] = {
        "kairos_channels": False,
        "kairos_push_notification": False,
        "mentor_step0": True,
        "rate_limit_enabled": True,
    }

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FeatureFlagService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._cache = TTLCache(maxsize=1, ttl=3600)  # cache do arquivo de config
        self._config_path = self._get_global_config_path()
        self._flags: Dict[str, Any] = {}
        self._yaml = YAML()
        self._yaml.preserve_quotes = True
        self.reload()
        self._initialized = True

    def is_enabled(self, flag_name: str) -> bool:
        """Retorna True se a flag est ativa (config ou env var)."""
        value = self.get_flag(flag_name, False)
        return bool(value)

    def get_flag(self, flag_name: str, default: Any = None) -> Any:
        """Retorna valor da flag (qualquer tipo)."""
        # Verifica env var primeiro (precedncia)
        env_var = f"NEOCORTEX_FF_{flag_name.upper()}"
        env_value = os.getenv(env_var)
        if env_value is not None:
            # Converte strings booleanas comuns
            if env_value.lower() in ("true", "1", "yes", "on"):
                return True
            elif env_value.lower() in ("false", "0", "no", "off"):
                return False
            # Caso contrrio, retorna a string original
            return env_value

        # Verifica cache do arquivo de config
        if "config" in self._cache:
            flags = self._cache["config"]
        else:
            flags = self._load_config()
            self._cache["config"] = flags

        # Retorna valor da config ou default
        return flags.get(flag_name, default)

    def reload(self) -> None:
        """Invalida cache e fora re-leitura."""
        self._cache.clear()
        self._flags = self._load_config()
        logger.info(f"Feature flags recarregadas, {len(self._flags)} flags")

    def list_flags(self) -> Dict[str, Any]:
        """Retorna todas as flags com seus valores atuais."""
        result = {}
        for flag_name in set(self._flags.keys()) | set(self._DEFAULTS.keys()):
            result[flag_name] = self.get_flag(flag_name, self._DEFAULTS.get(flag_name))
        return result

    def _load_config(self) -> Dict[str, Any]:
        """Carrega flags do arquivo de configurao YAML."""
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                config = self._yaml.load(f) or {}
        except FileNotFoundError:
            logger.warning(
                f"Config no encontrada em {self._config_path}, usando defaults"
            )
            config = {}
        except Exception as e:
            logger.error(f"Erro ao carregar config {self._config_path}: {e}")
            config = {}

        feature_flags = config.get("feature_flags", {})
        # Garante que todas as flags padro existam
        merged = self._DEFAULTS.copy()
        merged.update(feature_flags)
        return merged

    def _get_global_config_path(self) -> Path:
        """Determina o caminho para neocortex_config.yaml."""
        env_path = os.environ.get("NEOCORTEX_CONFIG_DIR")
        if env_path:
            env_path = Path(env_path)
            if env_path.is_dir():
                config_file = env_path / "neocortex_config.yaml"
                if config_file.is_file():
                    return config_file
                return config_file

        config_dir = platformdirs.user_config_dir("neocortex")
        return Path(config_dir) / "neocortex_config.yaml"


def get_feature_flags() -> FeatureFlagService:
    """Singleton do FeatureFlagService."""
    return FeatureFlagService()
