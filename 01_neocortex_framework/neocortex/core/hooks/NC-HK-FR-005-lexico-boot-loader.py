#!/usr/bin/env python3
"""
NC-HK-FR-005-lexico-boot-loader.py
LEXICO-005 — Boot Loader para hooks lexicais.

Objetivo: Carregar e inicializar hooks lexicais durante o boot do framework.
Suporta carregamento síncrono e assíncrono de hooks com prioridades.

Funcionalidades:
1. Carregamento automático de hooks de diretórios configurados
2. Priorização baseada em metadados YAML
3. Integração com neocortex_system para inicialização
4. Suporte a hooks síncronos e assíncronos
5. Registro automático no HookRegistry global
"""

import importlib.util
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from ruamel.yaml import YAML

logger = logging.getLogger(__name__)


class HookPriority(int, Enum):
    """Prioridades para hooks lexicais."""
    CRITICAL = 1000
    HIGH = 500
    MEDIUM = 250
    LOW = 100
    BACKGROUND = 10


class HookLoadMode(str, Enum):
    """Modos de carregamento de hooks."""
    SYNC = "sync"      # Carregamento síncrono durante boot
    ASYNC = "async"    # Carregamento assíncrono em background
    LAZY = "lazy"      # Carregamento sob demanda


@dataclass
class LexicoHookMetadata:
    """Metadados de um hook lexical."""
    name: str
    priority: HookPriority = HookPriority.MEDIUM
    load_mode: HookLoadMode = HookLoadMode.SYNC
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: float = 5.0
    enabled: bool = True
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)


class LexicoBootLoader:
    """Boot loader para hooks lexicais.
    
    Responsável por:
    1. Escanear diretórios em busca de hooks YAML/Python
    2. Carregar hooks com base em prioridade e dependências
    3. Registrar hooks no HookRegistry global
    4. Gerenciar inicialização síncrona/assíncrona
    5. Fornecer status e métricas de carregamento
    """
    
    def __init__(
        self,
        hook_dirs: Optional[List[Path]] = None,
        max_workers: int = 4,
        auto_discover: bool = True
    ):
        self.hook_dirs = hook_dirs or []
        self.max_workers = max_workers
        self.auto_discover = auto_discover
        
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._yaml = YAML()
        self._lock = threading.Lock()
        
        # Estado interno
        self._loaded_hooks: Dict[str, LexicoHookMetadata] = {}
        self._hook_handlers: Dict[str, Callable] = {}
        self._dependency_graph: Dict[str, Set[str]] = {}
        self._load_stats: Dict[str, Any] = {
            "total_scanned": 0,
            "loaded": 0,
            "failed": 0,
            "skipped": 0,
            "start_time": None,
            "end_time": None
        }
        
        # Integração com sistemas externos
        self._hook_registry = None
        self._system_service = None
        
    def discover_hook_dirs(self) -> List[Path]:
        """Descobre automaticamente diretórios de hooks."""
        base_dirs = []
        
        # Diretório padrão de hooks
        hooks_dir = Path(__file__).parent
        if hooks_dir.exists():
            base_dirs.append(hooks_dir)
        
        # Diretório de configuração de hooks
        config_dir = hooks_dir.parent.parent / "DIR-CFG-FR-001-config-main" / "hooks"
        if config_dir.exists():
            base_dirs.append(config_dir)
        
        # Diretório de templates
        templates_dir = hooks_dir.parent.parent / "DIR-TMP-FR-001-templates-main" / "hooks"
        if templates_dir.exists():
            base_dirs.append(templates_dir)
        
        # Diretórios de lobes (para hooks automáticos)
        lobes_dir = hooks_dir.parent.parent / "lobes"
        if lobes_dir.exists():
            for lobe_dir in lobes_dir.iterdir():
                if lobe_dir.is_dir():
                    lobe_hooks = lobe_dir / "hooks"
                    if lobe_hooks.exists():
                        base_dirs.append(lobe_hooks)
        
        return base_dirs
    
    def load_hooks(self, sync: bool = True) -> Dict[str, Any]:
        """Carrega todos os hooks disponíveis.
        
        Args:
            sync: Se True, carrega síncronamente. Se False, inicia carregamento assíncrono.
            
        Returns:
            Dicionário com estatísticas de carregamento.
        """
        self._load_stats["start_time"] = datetime.now()
        
        if self.auto_discover and not self.hook_dirs:
            self.hook_dirs = self.discover_hook_dirs()
        
        logger.info(f"Iniciando carregamento de hooks de {len(self.hook_dirs)} diretórios")
        
        if sync:
            return self._load_hooks_sync()
        else:
            # Inicia carregamento assíncrono em background
            future = self._executor.submit(self._load_hooks_sync)
            future.add_done_callback(self._on_async_load_complete)
            return {"status": "async_started", "future": future}
    
    def _load_hooks_sync(self) -> Dict[str, Any]:
        """Carregamento síncrono de hooks."""
        all_hooks = []
        
        # Fase 1: Coletar todos os hooks
        for hook_dir in self.hook_dirs:
            hooks = self._scan_directory(hook_dir)
            all_hooks.extend(hooks)
        
        self._load_stats["total_scanned"] = len(all_hooks)
        
        # Fase 2: Ordenar por prioridade e resolver dependências
        sorted_hooks = self._sort_hooks_by_priority(all_hooks)
        
        # Fase 3: Carregar hooks na ordem correta
        for hook_meta in sorted_hooks:
            try:
                self._load_single_hook(hook_meta)
                self._load_stats["loaded"] += 1
            except Exception as e:
                logger.error(f"Falha ao carregar hook {hook_meta.name}: {e}")
                self._load_stats["failed"] += 1
        
        self._load_stats["end_time"] = datetime.now()
        self._load_stats["duration"] = (
            self._load_stats["end_time"] - self._load_stats["start_time"]
        ).total_seconds()
        
        # Fase 4: Registrar hooks no HookRegistry global
        self._register_hooks_to_registry()
        
        logger.info(
            f"Carregamento concluído: {self._load_stats['loaded']} loaded, "
            f"{self._load_stats['failed']} failed, {self._load_stats['skipped']} skipped"
        )
        
        return self._load_stats.copy()
    
    def _scan_directory(self, directory: Path) -> List[LexicoHookMetadata]:
        """Escaneia diretório em busca de hooks YAML."""
        hooks = []
        
        if not directory.exists():
            logger.warning(f"Diretório não encontrado: {directory}")
            return hooks
        
        # Procurar arquivos YAML de hooks
        yaml_patterns = ["*.yaml", "*.yml"]
        for pattern in yaml_patterns:
            for yaml_file in directory.glob(pattern):
                if yaml_file.name.startswith("NC-HK-") or "hook" in yaml_file.name.lower():
                    hook_meta = self._parse_hook_yaml(yaml_file)
                    if hook_meta:
                        hooks.append(hook_meta)
        
        # Procurar scripts Python de hooks
        for py_file in directory.glob("*.py"):
            if py_file.name.startswith("NC-HK-") or "hook" in py_file.name.lower():
                hook_meta = self._parse_hook_python(py_file)
                if hook_meta:
                    hooks.append(hook_meta)
        
        return hooks
    
    def _parse_hook_yaml(self, yaml_path: Path) -> Optional[LexicoHookMetadata]:
        """Analisa arquivo YAML de hook."""
        try:
            data = self._yaml.load(yaml_path)
            
            # Verificar se é um arquivo de hook
            if "hook" not in data and "hooks" not in data:
                return None
            
            hook_data = data.get("hook", {})
            if not hook_data and "hooks" in data:
                # Arquivo com múltiplos hooks
                hooks_list = data["hooks"]
                if hooks_list:
                    hook_data = hooks_list[0]  # Pegar primeiro hook
            
            name = hook_data.get("name", yaml_path.stem)
            priority_str = hook_data.get("priority", "MEDIUM").upper()
            priority = getattr(HookPriority, priority_str, HookPriority.MEDIUM)
            
            load_mode_str = hook_data.get("load_mode", "SYNC").upper()
            load_mode = getattr(HookLoadMode, load_mode_str, HookLoadMode.SYNC)
            
            metadata = LexicoHookMetadata(
                name=name,
                priority=priority,
                load_mode=load_mode,
                dependencies=hook_data.get("dependencies", []),
                timeout_seconds=hook_data.get("timeout_seconds", 5.0),
                enabled=hook_data.get("enabled", True),
                description=hook_data.get("description", ""),
                version=hook_data.get("version", "1.0.0"),
                author=hook_data.get("author", ""),
                created=datetime.fromisoformat(hook_data.get("created", datetime.now().isoformat())),
                updated=datetime.fromisoformat(hook_data.get("updated", datetime.now().isoformat()))
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Erro ao analisar YAML {yaml_path}: {e}")
            return None
    
    def _parse_hook_python(self, py_path: Path) -> Optional[LexicoHookMetadata]:
        """Analisa script Python de hook para extrair metadados."""
        try:
            # Tentar extrair metadados do docstring
            spec = importlib.util.spec_from_file_location(py_path.stem, py_path)
            if spec is None:
                return None
            
            # Executar apenas para extrair variáveis de metadados
            exec_globals = {}
            with open(py_path, 'r', encoding='utf-8') as f:
                exec(f.read(), exec_globals)
            
            # Extrair metadados
            name = exec_globals.get("HOOK_NAME", py_path.stem)
            priority_str = exec_globals.get("HOOK_PRIORITY", "MEDIUM").upper()
            priority = getattr(HookPriority, priority_str, HookPriority.MEDIUM)
            
            metadata = LexicoHookMetadata(
                name=name,
                priority=priority,
                load_mode=HookLoadMode.SYNC,
                description=exec_globals.get("HOOK_DESCRIPTION", ""),
                version=exec_globals.get("HOOK_VERSION", "1.0.0"),
                author=exec_globals.get("HOOK_AUTHOR", "")
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Erro ao analisar Python hook {py_path}: {e}")
            return None
    
    def _sort_hooks_by_priority(self, hooks: List[LexicoHookMetadata]) -> List[LexicoHookMetadata]:
        """Ordena hooks por prioridade e resolve dependências."""
        # Construir grafo de dependências
        self._dependency_graph = {}
        hook_map = {hook.name: hook for hook in hooks}
        
        for hook in hooks:
            self._dependency_graph[hook.name] = set(hook.dependencies)
        
        # Ordenação topológica
        sorted_hooks = []
        visited = set()
        temp_visited = set()
        
        def visit(hook_name: str):
            if hook_name in temp_visited:
                raise ValueError(f"Dependência circular detectada envolvendo {hook_name}")
            if hook_name in visited:
                return
            
            temp_visited.add(hook_name)
            
            for dep in self._dependency_graph.get(hook_name, []):
                if dep in hook_map:
                    visit(dep)
            
            temp_visited.remove(hook_name)
            visited.add(hook_name)
            
            if hook_name in hook_map:
                sorted_hooks.append(hook_map[hook_name])
        
        # Visitar todos os hooks
        for hook in hooks:
            if hook.name not in visited:
                visit(hook.name)
        
        # Ordenar por prioridade dentro do mesmo nível
        priority_groups = {}
        for hook in sorted_hooks:
            priority_groups.setdefault(hook.priority, []).append(hook)
        
        # Reconstruir lista ordenada por prioridade (maior primeiro)
        final_sorted = []
        for priority in sorted(HookPriority, reverse=True):
            if priority in priority_groups:
                final_sorted.extend(priority_groups[priority])
        
        return final_sorted
    
    def _load_single_hook(self, hook_meta: LexicoHookMetadata) -> bool:
        """Carrega um único hook."""
        if not hook_meta.enabled:
            logger.debug(f"Hook {hook_meta.name} desabilitado, pulando")
            self._load_stats["skipped"] += 1
            return False
        
        logger.info(f"Carregando hook: {hook_meta.name} (priority: {hook_meta.priority.name})")
        
        # Aqui seria implementada a lógica específica de carregamento
        # Por enquanto, apenas registra o metadado
        with self._lock:
            self._loaded_hooks[hook_meta.name] = hook_meta
        
        return True
    
    def _register_hooks_to_registry(self):
        """Registra hooks carregados no HookRegistry global."""
        try:
            # Importar HookRegistry usando importlib devido ao hífen no nome
            import importlib.util
            hook_registry_path = Path(__file__).parent / "NC-HK-FR-001-hook-registry.py"
            spec = importlib.util.spec_from_file_location("hook_registry", hook_registry_path)
            if spec is None:
                logger.warning("Não foi possível importar HookRegistry")
                return
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # registry = module.get_hook_registry()  # Não usado no momento
            
            # Aqui seria implementado o registro real dos handlers
            # Por enquanto, apenas loga
            logger.info(f"Preparando para registrar {len(self._loaded_hooks)} hooks no registry")
            
        except ImportError:
            logger.warning("HookRegistry não disponível, pulando registro")
    
    def _on_async_load_complete(self, future):
        """Callback para carregamento assíncrono completo."""
        try:
            stats = future.result()
            logger.info(f"Carregamento assíncrono completo: {stats}")
        except Exception as e:
            logger.error(f"Erro no carregamento assíncrono: {e}")
    
    def get_loaded_hooks(self) -> List[Dict[str, Any]]:
        """Retorna lista de hooks carregados."""
        with self._lock:
            return [
                {
                    "name": meta.name,
                    "priority": meta.priority.name,
                    "load_mode": meta.load_mode.value,
                    "enabled": meta.enabled,
                    "description": meta.description,
                    "version": meta.version
                }
                for meta in self._loaded_hooks.values()
            ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de carregamento."""
        return self._load_stats.copy()
    
    def shutdown(self):
        """Desliga o boot loader e libera recursos."""
        self._executor.shutdown(wait=False)
        logger.info("LexicoBootLoader desligado")


# ── Integração com neocortex_system ───────────────────────────────────────────

def register_to_system():
    """Registra o boot loader no neocortex_system."""
    try:
        from neocortex.core import system_service
        
        boot_loader = LexicoBootLoader()
        
        # Registrar como serviço de inicialização
        system_service.register_boot_service(
            name="lexico_hook_boot_loader",
            service=boot_loader,
            priority=500  # Prioridade média
        )
        
        logger.info("LexicoBootLoader registrado no neocortex_system")
        return boot_loader
        
    except ImportError:
        logger.warning("neocortex_system não disponível, registro manual necessário")
        return LexicoBootLoader()


# ── Singleton global ─────────────────────────────────────────────────────────

_boot_loader_instance: Optional[LexicoBootLoader] = None


def get_boot_loader() -> LexicoBootLoader:
    """Singleton do LexicoBootLoader."""
    global _boot_loader_instance
    if _boot_loader_instance is None:
        _boot_loader_instance = register_to_system()
    return _boot_loader_instance


# ── Funções de conveniência ─────────────────────────────────────────────────

def load_hooks_sync() -> Dict[str, Any]:
    """Carrega hooks síncronamente (conveniência)."""
    loader = get_boot_loader()
    return loader.load_hooks(sync=True)


async def load_hooks_async() -> Dict[str, Any]:
    """Carrega hooks assíncronamente (conveniência)."""
    from concurrent.futures import ThreadPoolExecutor
    
    loader = get_boot_loader()
    
    import asyncio
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        future = loop.run_in_executor(executor, loader.load_hooks, False)
        return await future


if __name__ == "__main__":
    # Teste básico
    import sys
    logging.basicConfig(level=logging.INFO)
    
    loader = LexicoBootLoader()
    stats = loader.load_hooks()
    
    print(f"Carregamento concluído: {stats}")
    print(f"Hooks carregados: {loader.get_loaded_hooks()}")
    
    loader.shutdown()
    sys.exit(0 if stats['failed'] == 0 else 1)