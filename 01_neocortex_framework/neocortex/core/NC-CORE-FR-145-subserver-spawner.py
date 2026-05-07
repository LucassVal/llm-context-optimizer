# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
import json
import logging
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

BASE_PORT = 8766

class SubServerSpawner:
    """Gerencia sub-servers MCP para children forked."""

    def __init__(self, root: Path | None = None):
        import os
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.registry_file = self.root / ".neocortex" / "subservers.json"
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.servers: dict[str, dict[str, Any]] = self._load()

    def spawn(self, child_id: str, child_dir: str) -> dict[str, Any]:
        """Iniciar MCP server no child fork."""
        port = self._next_port()
        child_path = Path(child_dir)

        # Verificar se child existe
        if not child_path.exists():
            return {"success": False, "error": f"Child {child_id} não encontrado em {child_dir}"}

        # Iniciar sub-server
        try:
            proc = subprocess.Popen(
                [sys.executable, "-m", "neocortex.mcp.server",
                 "--transport", "sse", "--port", str(port)],
                cwd=str(child_path),
                env={**__import__("os").environ,
                     "PYTHONPATH": str(child_path),
                     "NC_ROOT": str(child_path),
                     "NEOCORTEX_LOG_LEVEL": "ERROR"},
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(3)  # Aguardar startup

            # Verificar se está rodando
            if self._check_port(port):
                self.servers[child_id] = {
                    "child_id": child_id,
                    "port": port,
                    "pid": proc.pid,
                    "started_at": datetime.now().isoformat(),
                    "status": "running",
                    "url": f"http://localhost:{port}/sse",
                }
                self._save()
                logger.info(f"[SubServer] {child_id} started on :{port}")
                return {"success": True, "child_id": child_id, "port": port,
                        "url": f"http://localhost:{port}/sse"}
            else:
                return {"success": False, "error": f"Port {port} não respondeu"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop(self, child_id: str) -> dict[str, Any]:
        """Parar sub-server."""
        if child_id not in self.servers:
            return {"success": False, "error": f"Sub-server {child_id} não encontrado"}
        try:
            import os as _os
            _os.kill(self.servers[child_id]["pid"], 9)
            self.servers[child_id]["status"] = "stopped"
            self._save()
            return {"success": True, "child_id": child_id, "status": "stopped"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_servers(self) -> list[dict[str, Any]]:
        return list(self.servers.values())

    def _next_port(self) -> int:
        used = {s["port"] for s in self.servers.values()}
        port = BASE_PORT + 100
        while port in used:
            port += 100
        return port

    def _check_port(self, port: int) -> bool:
        try:
            s = socket.create_connection(("localhost", port), timeout=2)
            s.close()
            return True
        except: return False

    def _load(self) -> dict:
        if self.registry_file.exists():
            try: return json.loads(self.registry_file.read_text(encoding="utf-8"))
            except: pass
        return {}

    def _save(self):
        self.registry_file.write_text(json.dumps(self.servers, indent=2, ensure_ascii=False), encoding="utf-8")

_spawner: SubServerSpawner | None = None
def get_spawner() -> SubServerSpawner:
    global _spawner
    if _spawner is None: _spawner = SubServerSpawner()
    return _spawner
