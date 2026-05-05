"""---
@Engine NC-CORE-FR-152-eisenhower-real mcp NC-CORE-FR-152-eisenhower-real.py — Conecta Eisenh
---
"""


import os
import pathlib
from datetime import datetime

import yaml as _yaml


class EisenhowerReal:
    """Eisenhower conectado aos tickets reais de DIR-DS-001-tickets."""

    URGENT_IMPORTANT = "DO_NOW"
    IMPORTANT_NOT_URGENT = "SCHEDULE"
    URGENT_NOT_IMPORTANT = "DELEGATE"
    NOT_URGENT_NOT_IMPORTANT = "DELETE"

    def __init__(self, root: Optional[pathlib.Path] = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self.ticket_dir = self.root / "DIR-DS-001-tickets"

    def load_all_tickets(self) -> list[dict]:
        tickets = []
        if not self.ticket_dir.exists():
            return tickets
        for f in sorted(self.ticket_dir.glob("NC-DS-*.yaml")):
            try:
                data = _yaml.safe_load(f.read_text(encoding="utf-8", errors="ignore"))
                if isinstance(data, dict):
                    data["_file"] = f.name
                    # Default urgency/impact if missing
                    if "urgency" not in data:
                        data["urgency"] = self._infer_urgency(data)
                    if "impact" not in data:
                        data["impact"] = self._infer_impact(data)
                    tickets.append(data)
            except Exception:
                pass
        return tickets

    def _infer_urgency(self, ticket: dict) -> int:
        status = str(ticket.get("status", "")).upper()
        priority = str(ticket.get("priority", "")).upper()
        if status == "BLOCKED":
            return 5
        if status == "OPEN" and priority == "HIGH":
            return 4
        if status == "OPEN":
            return 3
        if status in ("IN_PROGRESS", "IN-PROGRESS"):
            return 2
        return 1

    def _infer_impact(self, ticket: dict) -> int:
        title = str(ticket.get("title", ticket.get("summary", "")))
        module = str(ticket.get("module", ""))
        if "L1" in title or "L1" in module or "CRITICAL" in title:
            return 5
        if "core" in title.lower() or module.startswith("NC-CORE"):
            return 4
        if "governance" in title.lower() or "security" in title.lower():
            return 3
        return 2

    def classify(self, ticket: dict) -> str:
        urgency = int(ticket.get("urgency", 3))
        impact = int(ticket.get("impact", 2))

        if urgency >= 4 and impact >= 4:
            return self.URGENT_IMPORTANT
        elif urgency >= 4 and impact < 4:
            return self.URGENT_NOT_IMPORTANT
        elif urgency < 4 and impact >= 4:
            return self.IMPORTANT_NOT_URGENT
        else:
            return self.NOT_URGENT_NOT_IMPORTANT

    def full_analysis(self) -> dict:
        tickets = self.load_all_tickets()
        for t in tickets:
            t["_quadrant"] = self.classify(t)

        order = [self.URGENT_IMPORTANT, self.IMPORTANT_NOT_URGENT, self.URGENT_NOT_IMPORTANT, self.NOT_URGENT_NOT_IMPORTANT]
        sorted_tickets = sorted(tickets, key=lambda t: order.index(t["_quadrant"]))

        by_quadrant = {}
        for q in order:
            by_quadrant[q] = [t["_file"] for t in sorted_tickets if t["_quadrant"] == q]

        return {
            "total": len(tickets),
            "by_quadrant": {q: len(items) for q, items in by_quadrant.items()},
            "top_5_do_now": [t["_file"] for t in sorted_tickets if t["_quadrant"] == self.URGENT_IMPORTANT][:5],
            "paute_de_julgamento": {
                self.URGENT_IMPORTANT: {
                    "label": "URGENTE + IMPORTANTE (Julgar agora)",
                    "conceito": "Precatórios, Habeas Corpus, Liminares",
                    "count": by_quadrant.get(self.URGENT_IMPORTANT, [])
                },
                self.IMPORTANT_NOT_URGENT: {
                    "label": "IMPORTANTE NAO URGENTE (Agendar)",
                    "conceito": "Recursos, Apelações, Ações Civis",
                },
                self.URGENT_NOT_IMPORTANT: {
                    "label": "URGENTE NAO IMPORTANTE (Delegar)",
                    "conceito": "Mandados, Citações, Diligências",
                },
                self.NOT_URGENT_NOT_IMPORTANT: {
                    "label": "NEM URGENTE NEM IMPORTANTE (Arquivar)",
                    "conceito": "Processos prescritos, Incidentes menores",
                },
            },
            "timestamp": datetime.now().isoformat(),
        }

    def inject_urgency_impact(self, dry_run: bool = True) -> dict:
        """Adiciona urgency/impact aos tickets que nao tem."""
        tickets = self.load_all_tickets()
        updated = 0
        for t in tickets:
            fname = t.get("_file", "")
            if not fname:
                continue
            fp = self.ticket_dir / fname
            if not fp.exists():
                continue
            content = fp.read_text(encoding="utf-8", errors="ignore")
            modified = False
            if "urgency:" not in content:
                urg = self._infer_urgency(t)
                content = content.rstrip() + f"\nurgency: {urg}\n"
                modified = True
            if "impact:" not in content:
                imp = self._infer_impact(t)
                content = content.rstrip() + f"\nimpact: {imp}\n"
                modified = True
            if modified and not dry_run:
                fp.write_text(content, encoding="utf-8")
            if modified:
                updated += 1

        return {"updated": updated, "dry_run": dry_run, "total": len(tickets)}


_eisenhower = None
def get_eisenhower():
    global _eisenhower
    if _eisenhower is None:
        _eisenhower = EisenhowerReal()
    return _eisenhower
