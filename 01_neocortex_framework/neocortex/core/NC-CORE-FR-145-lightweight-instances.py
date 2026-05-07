# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
"""---
@Gateway NC-CORE-FR-145-lightweight-instances mcp NC-CORE-FR-145-lightweight-instances.py — Instânci
---
"""


import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

class LightweightInstance:
    """Instância virtual — estado isolado, MCP compartilhado."""

    def __init__(self, child_id: str, child_dir: str):
        self.id = child_id
        self.dir = Path(child_dir)
        self.active = True
        self.tasks_completed = 0
        self.errors = 0
        self.created_at = datetime.now().isoformat()

    def get_dna(self) -> dict[str, Any]:
        dna_file = self.dir / "DNA.json"
        if dna_file.exists():
            return json.loads(dna_file.read_text(encoding="utf-8"))
        return {}

    def get_rna(self) -> dict[str, Any]:
        rna_file = self.dir / "RNA.json"
        if rna_file.exists():
            return json.loads(rna_file.read_text(encoding="utf-8"))
        return {}

    def update_rna(self, updates: dict[str, Any]):
        rna = self.get_rna()
        rna.update(updates)
        (self.dir / "RNA.json").write_text(json.dumps(rna, indent=2, ensure_ascii=False), encoding="utf-8")

    def status(self) -> dict[str, Any]:
        return {"id": self.id, "active": self.active,
                "tasks": self.tasks_completed, "errors": self.errors,
                "created": self.created_at.isoformat()}


class InstanceManager:
    """Gerencia instâncias virtuais (children ativos)."""

    def __init__(self, root: Path | None = None):
        import os
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.instances: dict[str, LightweightInstance] = {}
        self.current: LightweightInstance | None = None
        self._load_existing()

    def _load_existing(self):
        sandbox = self.root / ".neocortex" / "sandbox"
        if not sandbox.exists(): return
        for d in sandbox.iterdir():
            if d.is_dir() and d.name.startswith("nc-child-"):
                self.instances[d.name] = LightweightInstance(d.name, str(d))

    def switch(self, child_id: str) -> dict[str, Any]:
        """Alternar contexto para child — agentes operam como child."""
        if child_id not in self.instances:
            return {"success": False, "error": f"Child {child_id} não encontrado"}
        self.current = self.instances[child_id]
        return {"success": True, "current": child_id,
                "dna": self.current.get_dna().get("instance_name", ""),
                "bsl": "BSL-1"}

    def execute(self, action: str, **kwargs) -> dict[str, Any]:
        """Executar ação no contexto do child atual."""
        if not self.current:
            return {"success": False, "error": "Nenhum child ativo. Use instance.switch primeiro."}
        self.current.tasks_completed += 1
        return {"success": True, "instance": self.current.id, "action": action}

    def list_instances(self) -> list[dict[str, Any]]:
        return [i.status() for i in self.instances.values()]

    def get_current(self) -> dict[str, Any] | None:
        if self.current:
            return self.current.status()
        return None

_mgr: InstanceManager | None = None
def get_instance_manager() -> InstanceManager:
    global _mgr
    if _mgr is None: _mgr = InstanceManager()
    return _mgr
