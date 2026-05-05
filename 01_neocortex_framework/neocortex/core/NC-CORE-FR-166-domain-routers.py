"""---
@Router NC-CORE-FR-166-domain-routers mcp NC-CORE-FR-166-domain-routers.py — Domain Routers
---
"""

import os
import pathlib
import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class DomainRouter:
    """Router de 1 dominio DDD. Sabe todos os modulos do seu bounded context."""

    def __init__(self, domain_name: str, root: pathlib.Path = None):
        self.domain = domain_name
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._index: Dict[str, Dict] = {}
        self._build_index()

    def _build_index(self):
        """Indexa todos os modulos do dominio."""
        fw = self.root / "01_neocortex_framework" / "neocortex"
        # Core engines
        core = fw / "core"
        for f in sorted(core.glob("NC-CORE-FR-*.py")):
            nc_id = re.search(r'(NC-CORE-FR-\d+[\w-]*)', f.name)
            if nc_id:
                self._index[nc_id.group(1)] = {"path": str(f.relative_to(self.root)), "type": "engine", "domain": self.domain}

        # MCP tools
        tools = fw / "mcp" / "tools"
        for f in sorted(tools.glob("NC-SUPER-*.py")):
            self._index[f.stem] = {"path": str(f.relative_to(self.root)), "type": "tool", "domain": self.domain}

        # Lobes in this domain
        lobes = self.root / "02_memory_lobes" / self.domain
        if lobes.exists():
            for f in sorted(lobes.glob("*.mdc")):
                self._index[f.stem] = {"path": str(f.relative_to(self.root)), "type": "lobe", "domain": self.domain}

    def resolve(self, query: str) -> Optional[Dict]:
        """Busca exata primeiro, depois parcial."""
        # 1. Exata por NC-ID
        for key, data in self._index.items():
            if key == query or key.upper() == query.upper():
                data["match"] = key
                data["match_type"] = "exact"
                return data
        # 2. Contem query
        for key, data in self._index.items():
            if query.upper() in key.upper():
                data["match"] = key
                data["match_type"] = "contains"
                return data
        # 3. Query contida na key
        for key, data in self._index.items():
            if key.upper() in query.upper():
                data["match"] = key
                data["match_type"] = "contained"
                return data
        return None

    def list_all(self) -> List[str]:
        return sorted(self._index.keys())

    def count(self) -> int:
        return len(self._index)


class CentralSemanticIndex:
    """Indice central — sabe qual dominio tem o que. Nao executa, so indexa."""

    def __init__(self, root: pathlib.Path = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._domain_routers: Dict[str, DomainRouter] = {}
        self._init_routers()

    def _init_routers(self):
        domains = ["06_governance", "04_cc_patterns", "$frontal", "$cerebelo",
                   "01_framework", "01_architecture", "02_integrations", "05_machine_memory"]
        for d in domains:
            self._domain_routers[d] = DomainRouter(d, root=self.root)

    def resolve(self, query: str) -> Dict:
        """Central index: pergunta a cada domain router. Retorna o 1o match."""
        results = []
        for _domain, router in self._domain_routers.items():
            match = router.resolve(query)
            if match:
                results.append(match)
        return {
            "query": query,
            "found": len(results) > 0,
            "matches": results[:5],
            "best": results[0] if results else None,
            "domains_searched": len(self._domain_routers),
            "timestamp": datetime.now().isoformat(),
        }

    def route_to_module(self, nc_id: str) -> Optional[Any]:
        """Carrega modulo via domain router + importlib."""
        import importlib.util
        result = self.resolve(nc_id)
        if not result["best"]:
            return None
        best = result["best"]
        fp = self.root / best["path"]
        if not fp.exists():
            return None
        spec = importlib.util.spec_from_file_location(nc_id.replace("-", "_"), str(fp))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def status(self) -> Dict:
        return {
            "total_domains": len(self._domain_routers),
            "total_indexed": sum(r.count() for r in self._domain_routers.values()),
            "per_domain": {d: r.count() for d, r in self._domain_routers.items()},
            "architecture": "2-level: CentralIndex -> DomainRouters -> Modules/Lobes",
            "ddd_compliant": "Shared Kernel — all domains can query",
            "timestamp": datetime.now().isoformat(),
        }


_index_instance = None


def get_central_index():
    global _index_instance
    if _index_instance is None:
        _index_instance = CentralSemanticIndex()
    return _index_instance
