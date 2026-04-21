"""---
domain: "core"
layer: "core"
type: "file"
tags: ["cfg", "004", "project", "config"]
hash: "auto-generated"
---"""
#!/usr/bin/env python3
"""
NC-CFG-FR-004-project-config.py
FR-004  ProjectConfig: Configurao por projeto/workspace.

Permite que cada projeto/workspace tenha configuraes prprias que sobrescrevem
o neocortex_config.yaml global (sem modific-lo).

Arquivo de persistncia: {project_root}/.neocortex/project.yaml
Formato YAML  usa ruamel.yaml com fallback para PyYAML com fallback para json.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

# YAML loading utilities
_yaml_loader = None
_yaml_dumper = None

try:
    from ruamel.yaml import YAML

    _yaml = YAML()
    _yaml_loader = _yaml.load
    _yaml_dumper = _yaml.dump
    _yaml_lib = "ruamel"
except ImportError:
    try:
        import yaml

        _yaml_loader = yaml.safe_load

        def _pyyaml_dumper(data, stream):
            yaml.dump(data, stream, default_flow_style=False, indent=2)

        _yaml_dumper = _pyyaml_dumper
        _yaml_lib = "pyyaml"
    except ImportError:
        _yaml_lib = None

logger = logging.getLogger(__name__)


class ProjectConfig:
    """
    Configurao por projeto/workspace.

    Interface obrigatria:
        __init__(project_root: Path | str) -> None
        load() -> dict
        save(data: dict) -> None
        get(key: str, default=None)
        set(key: str, value) -> None
        merge_with_global() -> dict
        reset() -> None
    """

    def __init__(self, project_root: Union[Path, str]) -> None:
        """
        Inicializa config para o projeto especificado.

        Args:
            project_root: Diretrio raiz do projeto.
        """
        if isinstance(project_root, str):
            self.project_root = Path(project_root).resolve()
        else:
            self.project_root = project_root.resolve()

        self.config_dir = self.project_root / ".neocortex"
        self.config_file = self.config_dir / "project.yaml"
        self._config: Dict[str, Any] = {}
        self._global_config: Optional[Dict[str, Any]] = None

        if _yaml_lib is None:
            logger.warning(
                "Nem ruamel.yaml nem PyYAML encontrados. Usando JSON como fallback."
            )

    def load(self) -> Dict[str, Any]:
        """
        Carrega .neocortex/project.yaml se existir.

        Returns:
            Dicionrio com configurao do projeto (vazio se no existir).
        """
        if not self.config_file.exists():
            logger.debug(
                f"Arquivo de configurao do projeto no encontrado: {self.config_file}"
            )
            self._config = {}
            return {}

        try:
            content = self.config_file.read_text(encoding="utf-8")
            if _yaml_loader is not None:
                config = _yaml_loader(content) or {}
            else:
                config = json.loads(content)
        except Exception as e:
            logger.error(f"Erro ao carregar configurao do projeto: {e}")
            config = {}

        self._config = config
        logger.debug(f"Configurao do projeto carregada: {len(config)} chaves")
        return config

    def save(self, data: Dict[str, Any]) -> None:
        """
        Persiste dicionrio em .neocortex/project.yaml.

        Args:
            data: Dicionrio de configurao a ser salvo.
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)

        try:
            if _yaml_dumper is not None:
                with open(self.config_file, "w", encoding="utf-8") as f:
                    _yaml_dumper(data, f)
            else:
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar configurao do projeto: {e}")
            raise

        self._config = data
        logger.info(f"Configurao do projeto salva em {self.config_file}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Leitura com fallback para global config.

        Args:
            key: Chave de configurao (dot-notation suportada).
            default: Valor padro se chave no existir.

        Returns:
            Valor da configurao ou default.
        """
        # Primeiro tenta configurao do projeto
        if not self._config:
            self.load()

        # Suporte a dot notation
        parts = key.split(".")
        value = self._config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                # No encontrado no projeto, tenta global
                return self._get_global_key(key, default)

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Escreve e persiste imediatamente.

        Args:
            key: Chave de configurao (dot-notation suportada).
            value: Valor a ser definido.
        """
        if not self._config:
            self.load()

        # Suporte a dot notation: atualiza dicionrio aninhado
        parts = key.split(".")
        config = self._config
        for _, part in enumerate(parts[:-1]):
            if part not in config or not isinstance(config[part], dict):
                config[part] = {}
            config = config[part]
        config[parts[-1]] = value

        # Persiste
        self.save(self._config)

    def merge_with_global(self) -> Dict[str, Any]:
        """
        Retorna dict merged: global + project (project wins).

        Returns:
            Dicionrio mesclado com precedncia do projeto.
        """
        global_config = self._load_global_config()
        merged = self._deep_merge(global_config.copy(), self._config)
        return merged

    def reset(self) -> None:
        """Apaga .neocortex/project.yaml."""
        if self.config_file.exists():
            self.config_file.unlink()
            logger.info(f"Configurao do projeto resetada: {self.config_file}")
        self._config = {}

    def _get_global_key(self, key: str, default: Any = None) -> Any:
        """
        Obtm chave da configurao global.

        Args:
            key: Chave (dot-notation).
            default: Valor padro.

        Returns:
            Valor da configurao global ou default.
        """
        global_config = self._load_global_config()
        parts = key.split(".")
        value = global_config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        return value

    def _load_global_config(self) -> Dict[str, Any]:
        """
        Carrega configurao global (neocortex_config.yaml).

        Returns:
            Dicionrio com configurao global.
        """
        if self._global_config is not None:
            return self._global_config

        # Tenta encontrar neocortex_config.yaml usando a mesma lgica do FeatureFlagService
        config_path = self._get_global_config_path()
        if not config_path.exists():
            logger.debug(
                f"Arquivo de configurao global no encontrado: {config_path}"
            )
            self._global_config = {}
            return {}

        try:
            content = config_path.read_text(encoding="utf-8")
            if _yaml_loader is not None:
                config = _yaml_loader(content) or {}
            else:
                config = json.loads(content)
        except Exception as e:
            logger.error(f"Erro ao carregar configurao global: {e}")
            config = {}

        self._global_config = config
        return config

    def _get_global_config_path(self) -> Path:
        """
        Determina caminho para neocortex_config.yaml.

        Segue a mesma lgica do FeatureFlagService.
        """
        env_path = os.environ.get("NEOCORTEX_CONFIG_DIR")
        if env_path:
            env_path = Path(env_path)
            if env_path.is_dir():
                config_file = env_path / "neocortex_config.yaml"
                if config_file.is_file():
                    return config_file
                return config_file

        # Usa platformdirs para XDG/APPDATA
        try:
            from platformdirs import user_config_dir

            config_dir = user_config_dir("neocortex")
            return Path(config_dir) / "neocortex_config.yaml"
        except ImportError:
            # Fallback para diretrio padro
            return Path.home() / ".config" / "neocortex" / "neocortex_config.yaml"

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge recursivo de dicionrios (override sobrescreve base).

        Args:
            base: Dicionrio base.
            override: Dicionrio com sobreposies.

        Returns:
            Dicionrio mesclado.
        """
        result = base.copy()
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result


# Singleton convenience
_default_project_config: Optional[ProjectConfig] = None


def get_project_config(
    project_root: Optional[Union[Path, str]] = None,
) -> ProjectConfig:
    """
    Singleton do ProjectConfig.

    Args:
        project_root: Diretrio raiz do projeto. Se None, usa diretrio atual.

    Returns:
        Instncia de ProjectConfig.
    """
    global _default_project_config

    if project_root is None:
        project_root = Path.cwd()

    if _default_project_config is None:
        _default_project_config = ProjectConfig(project_root)
    elif _default_project_config.project_root != Path(project_root).resolve():
        logger.warning(
            f"Singleton j instanciado com projeto {_default_project_config.project_root}. "
            f"Ignorando novo project_root: {project_root}"
        )

    return _default_project_config
