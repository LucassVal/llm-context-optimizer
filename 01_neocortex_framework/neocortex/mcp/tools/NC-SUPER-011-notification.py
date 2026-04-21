#!/usr/bin/env python3
"""
NC-SUPER-011 — neocortex_notification
FÓRUM — Notificações e Peers

Funde: notification (028), peers (012).

Actions:
  push.send, push.list, push.clear
  peers.discover, peers.sync, peers.list, peers.heartbeat
"""
import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_notification"

_NOTIFICATIONS: List[Dict] = []
_PEERS: Dict[str, Dict] = {}


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_notification(
        action: str,
        message: str = "",
        level: str = "INFO",
        channel: str = "system",
        peer_id: str = "",
        peer_url: str = "",
        limit: int = 20,
    ) -> Dict[str, Any]:
        """FÓRUM — Notificações e Peers.
        Funde: notification (028) + peers (012).
        Actions: push.send, push.list, push.clear,
                 peers.discover, peers.sync, peers.list, peers.heartbeat
        """
        ts = _ts()

        if action == "push.send":
            if not message:
                return {"success": False, "error": "message obrigatória", "timestamp": ts}
            notif = {"id": f"N{len(_NOTIFICATIONS)+1:04d}", "message": message,
                     "level": level, "channel": channel, "timestamp": ts}
            _NOTIFICATIONS.append(notif)
            return {"success": True, "action": action, "notification": notif, "timestamp": ts}

        elif action == "push.list":
            channel_filter = [n for n in _NOTIFICATIONS if not channel or n["channel"] == channel]
            return {"success": True, "action": action,
                    "notifications": channel_filter[-limit:],
                    "count": len(channel_filter), "timestamp": ts}

        elif action == "push.clear":
            _NOTIFICATIONS.clear()
            return {"success": True, "action": action, "cleared": True, "timestamp": ts}

        elif action == "peers.discover":
            known_ports = [3000, 8765, 8767, 11434, 18790, 4000]
            discovered = []
            try:
                import requests
                for port in known_ports:
                    try:
                        r = requests.get(f"http://localhost:{port}/health", timeout=1)
                        discovered.append({"port": port, "reachable": r.ok, "status": "up" if r.ok else "down"})
                    except Exception:
                        discovered.append({"port": port, "reachable": False, "status": "down"})
            except ImportError:
                pass
            for peer in discovered:
                _PEERS[str(peer["port"])] = peer
            return {"success": True, "action": action, "discovered": discovered,
                    "online": sum(1 for p in discovered if p["reachable"]), "timestamp": ts}

        elif action == "peers.list":
            return {"success": True, "action": action,
                    "peers": list(_PEERS.values()), "count": len(_PEERS), "timestamp": ts}

        elif action == "peers.sync":
            if not peer_id or not peer_url:
                return {"success": False, "error": "peer_id e peer_url obrigatórios", "timestamp": ts}
            _PEERS[peer_id] = {"peer_id": peer_id, "url": peer_url, "synced": ts}
            return {"success": True, "action": action, "peer_id": peer_id, "timestamp": ts}

        elif action == "peers.heartbeat":
            try:
                import requests
                alive = {}
                for pid, peer in _PEERS.items():
                    url = peer.get("url", f"http://localhost/{pid}")
                    try:
                        r = requests.get(url, timeout=2)
                        alive[pid] = r.ok
                    except Exception:
                        alive[pid] = False
                return {"success": True, "action": action, "heartbeat": alive, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}


        elif action == "push.status":
            try:
                from neocortex.core import get_ledger_service
                svc = get_ledger_service(); ledger = svc.read_ledger() if hasattr(svc,"read_ledger") else {}
                notifs = ledger.get("notifications", [])
                return {"success": True, "action": action, "pending": len(notifs), "notifications": notifs[-10:], "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}
        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["push.send", "push.list", "push.clear",
                                  "peers.discover", "peers.sync", "peers.list", "peers.heartbeat"],
                    "timestamp": ts}
