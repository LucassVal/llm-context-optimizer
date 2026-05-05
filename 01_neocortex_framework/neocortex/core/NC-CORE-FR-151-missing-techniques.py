"""---
@Module NC-CORE-FR-151-missing-techniques mcp NC-CORE-FR-151-missing-techniques.py — Motores das
---
"""


import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# ═══════════════════════════════════════════════════════════════
# 1. 3 W's — Auto-Contexto (What / Why / Where)
# ═══════════════════════════════════════════════════════════════

class ThreeWEngine:
    """Gera What/Why/Where automaticamente para qualquer módulo NC-."""

    def __init__(self, root: Path = None):
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))

    def analyze_module(self, file_path: Path) -> Dict:
        """Analisa um módulo e extrai seu contexto em 3 W's."""
        if not file_path.exists():
            return {"error": "not_found", "what": "", "why": "", "where": ""}
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        name = file_path.stem.replace("-", " ")

        # What: extrai da classe principal ou docstring
        what = self._extract_what(content, name)
        # Why: extrai de comentários """--- ou de RCA logs
        why = self._extract_why(content, file_path)
        # Where: determina o domínio/orbital
        where = self._extract_where(file_path)

        return {"module": file_path.name, "what": what, "why": why, "where": where, "scanned_at": datetime.now().isoformat()}

    def _extract_what(self, content: str, name: str) -> str:
        # Busca descrição no cabeçalho """
        m = re.search(r'\"\"\"---\n(.+?)\n---', content, re.DOTALL)
        if m:
            return m.group(1).strip()
        # Fallback: nome do arquivo
        return f"Modulo: {name}"

    def _extract_why(self, content: str, file_path: Path) -> str:
        # Busca "adicionado para" ou "porque" em comentários
        m = re.search(r'# (?:porque|adicionado para|fixes|resolve)[\s:]*(.+)', content, re.IGNORECASE)
        if m:
            return m.group(1).strip()[:120]
        # Fallback: data de criação
        return f"Criado em {datetime.fromtimestamp(file_path.stat().st_ctime).strftime('%Y-%m-%d')}"

    def _extract_where(self, file_path: Path) -> str:
        rel = file_path.relative_to(self.root) if self.root in file_path.parents else file_path
        parts = rel.parts
        if "neocortex" in parts:
            idx = parts.index("neocortex")
            return "/".join(parts[idx:idx+3])
        return "/".join(parts[:3])

    def generate_welcome_doc(self) -> str:
        """Gera doc de boas-vindas para novo dev."""
        lobes = list((self.root / "02_memory_lobes").rglob("*.mdc"))[:5]
        tools = list((self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools").glob("NC-SUPER-*.py"))[:5]
        modules = [self.analyze_module(m) for m in tools]

        doc = f"""---
NC-DOC-FR-003-developer-onboarding.md — 3 W's Auto-Generated
Gerado: {datetime.now().isoformat()}
---

# Bem-vindo ao NeoCortex — O QUE, POR QUE e ONDE

## O QUE é o NeoCortex?
Sistema de governança DDD orbital com Gateway, PulseScheduler, RCA Engine e 18 Super Tools MCP.

## POR QUE foi criado?
Para governar automaticamente código, lobos de memória e deploys com enforcement de 4 camadas (HOOK/CHECKPOINT/SCHEDULE/USER).

## ONDE estão as coisas?

### Domínios de Memória
"""
        for l in lobes:
            doc += f"- `{l.relative_to(self.root)}`\n"

        doc += "\n### Módulos Core\n"
        for m in modules:
            doc += f"- **{m['module']}**: {m['what']}\n"
            doc += f"  - Por que: {m['why']}\n"
            doc += f"  - Onde: {m['where']}\n"

        doc += "\n---\n*Gerado automaticamente pelo 3-W's Engine (NC-CORE-FR-151)*\n"
        return doc


# ═══════════════════════════════════════════════════════════════
# 2. Eisenhower Matrix — Priorização de Tickets
# ═══════════════════════════════════════════════════════════════

class EisenhowerEngine:
    """Classifica tickets por Urgência x Importância."""

    URGENT_IMPORTANT = "DO_NOW"
    IMPORTANT_NOT_URGENT = "SCHEDULE"
    URGENT_NOT_IMPORTANT = "DELEGATE"
    NOT_URGENT_NOT_IMPORTANT = "DELETE"

    def classify(self, ticket: Dict) -> str:
        urgency = self._score_urgency(ticket)
        importance = self._score_importance(ticket)

        if urgency >= 7 and importance >= 7:
            return self.URGENT_IMPORTANT
        elif urgency >= 7 and importance < 7:
            return self.URGENT_NOT_IMPORTANT
        elif urgency < 7 and importance >= 7:
            return self.IMPORTANT_NOT_URGENT
        else:
            return self.NOT_URGENT_NOT_IMPORTANT

    def _score_urgency(self, t: Dict) -> int:
        score = 0
        # Bloqueante = urgente
        if t.get("status") == "BLOCKED": score += 4
        # Regras L1 violadas = urgente
        if t.get("violation_level") == "L1": score += 3
        # Há < 1h = urgente
        if t.get("age_hours", 999) < 1: score += 2
        return min(score, 10)

    def _score_importance(self, t: Dict) -> int:
        score = 0
        # Core module = importante
        if t.get("module", "").startswith("NC-CORE"): score += 3
        # Compliance impact = importante
        if t.get("compliance_impact"): score += 3
        # RCA gerado = importante
        if t.get("has_rca"): score += 2
        return min(score, 10)

    def prioritize_tickets(self, tickets: List[Dict]) -> List[Dict]:
        for t in tickets:
            t["eisenhower_quadrant"] = self.classify(t)
        # Order: DO_NOW first, DELETE last
        order = [self.URGENT_IMPORTANT, self.IMPORTANT_NOT_URGENT, self.URGENT_NOT_IMPORTANT, self.NOT_URGENT_NOT_IMPORTANT]
        return sorted(tickets, key=lambda t: order.index(t["eisenhower_quadrant"]))


# ═══════════════════════════════════════════════════════════════
# 3. Pareto 80/20 — Error Distribution Analytics
# ═══════════════════════════════════════════════════════════════

class ParetoEngine:
    """Analisa quais 20% dos módulos causam 80% dos erros."""

    def __init__(self, root: Path = None):
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))

    def analyze(self) -> Dict:
        log_dir = self.root / "DIR-DS-002-audit-logs"
        errors_by_module: Dict[str, int] = {}

        if log_dir.exists():
            for f in log_dir.glob("*.yaml"):
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    # Extract module names from error logs
                    mods = set(re.findall(r'NC-(?:CORE|SUPER|LBE|DS|ARC|DOC|SEC|NAM|SCR|SOP|TODO)-\w+-\d+', content))
                    for m in mods:
                        errors_by_module[m] = errors_by_module.get(m, 0) + 1
                except: pass

        # Sort by error count descending
        sorted_modules = sorted(errors_by_module.items(), key=lambda x: x[1], reverse=True)
        total_errors = sum(errors_by_module.values())
        top_20pct_count = max(1, len(sorted_modules) // 5)  # 20%
        top_20pct = sorted_modules[:top_20pct_count]
        top_errors = sum(v for _, v in top_20pct)

        pct_of_errors = round(top_errors / total_errors * 100, 1) if total_errors > 0 else 0
        pareto_holds = pct_of_errors >= 70  # True if 80/20 rule holds

        return {
            "total_modules_with_errors": len(sorted_modules),
            "total_errors": total_errors,
            "top_20pct_count": top_20pct_count,
            "top_20pct_errors": top_errors,
            "top_20pct_error_pct": pct_of_errors,
            "pareto_holds": pareto_holds,
            "top_offenders": [(m, c) for m, c in top_20pct[:10]],
            "recommendation": "FOCUS on top 20%" if pareto_holds else "Errors are well distributed"
        }


# ═══════════════════════════════════════════════════════════════
# 4. OKRs — Objectives & Key Results Tracker
# ═══════════════════════════════════════════════════════════════

class OKREngine:
    """Track Objectives and Key Results no roadmap."""

    def __init__(self, root: Path = None):
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.okr_lobe = self.root / "02_memory_lobes" / "06_governance" / "NC-LBE-FR-OKR-001.md"

    def get_current_okrs(self) -> Dict:
        if self.okr_lobe.exists():
            return {"objective": "NeoCortex Production-Ready", "key_results": self._parse_krs(self.okr_lobe.read_text(encoding="utf-8"))}
        return self._default_okrs()

    def _parse_krs(self, text: str) -> List[Dict]:
        krs = []
        for m in re.finditer(r'KR(\d+):\s*(.+?)(?=\n\n|\nKR|\Z)', text, re.DOTALL):
            krs.append({"id": f"KR{m.group(1)}", "description": m.group(2).strip().replace("\n", " ")})
        return krs

    def _default_okrs(self) -> Dict:
        return {
            "objective": "Sermos os mais competitivos com governança autônoma",
            "key_results": [
                {"id": "KR1", "description": "100% dos módulos NC- com Gateway enforcement (8/18 -> 18/18)", "progress_pct": 44},
                {"id": "KR2", "description": "Score de auditoria >= 90% (atual 72.3%)", "progress_pct": 72},
                {"id": "KR3", "description": "0 ruff errors nos 18 tools (2/10 -> 18/18)", "progress_pct": 20},
                {"id": "KR4", "description": "15/15 técnicas implementadas (5/15 -> 15/15)", "progress_pct": 33},
                {"id": "KR5", "description": "4/4 enforcement layers ativas (H/C/S/U)", "progress_pct": 100},
            ],
            "updated_at": datetime.now().isoformat()
        }

    def generate_okr_report(self) -> str:
        okrs = self.get_current_okrs()
        lines = [f"# OKR: {okrs['objective']}", ""]
        for kr in okrs["key_results"]:
            bar = "█" * (kr.get("progress_pct", 0) // 5) + "░" * (20 - kr.get("progress_pct", 0) // 5)
            lines.append(f"**{kr['id']}**: {kr['description']}")
            lines.append(f"  [{bar}] {kr.get('progress_pct', 0)}%")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# 5. Idempotency Guard — Savepoint/WAL Guardian
# ═══════════════════════════════════════════════════════════════

class IdempotencyGuard:
    """Garante que operações em savepoints/WAL sejam idempotentes."""

    def __init__(self, root: Path = None):
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.state_dir = self.root / ".neocortex" / "state"

    def is_duplicate(self, key: str, content_hash: str) -> bool:
        """Check se uma operação já foi registrada."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        dedup_file = self.state_dir / "NC-STATE-IDEMPOTENCY_LOG.jsonl"

        if dedup_file.exists():
            for line in dedup_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        entry = json.loads(line)
                        if entry.get("key") == key and entry.get("hash") == content_hash:
                            return True
                    except: pass
        return False

    def record(self, key: str, content_hash: str, action: str = "savepoint") -> bool:
        """Registra operação se não for duplicata. Retorna True se nova, False se duplicata."""
        if self.is_duplicate(key, content_hash):
            return False

        dedup_file = self.state_dir / "NC-STATE-IDEMPOTENCY_LOG.jsonl"
        entry = json.dumps({
            "key": key, "hash": content_hash, "action": action,
            "timestamp": datetime.now().isoformat()
        })
        with open(dedup_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        return True

    def check_savepoint(self, savepoint_name: str, data: str) -> bool:
        """Wrapper: check se savepoint é duplicado."""
        import hashlib
        h = hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]
        return self.record(f"sp:{savepoint_name}", h, "savepoint")

    def check_wal_duplicate(self, entry_key: str, payload: str) -> bool:
        """Wrapper: check se entry WAL já existe."""
        import hashlib
        h = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
        return self.record(f"wal:{entry_key}", h, "wal")


# ═══════════════════════════════════════════════════════════════
# Combined Engine
# ═══════════════════════════════════════════════════════════════

class TechniquesEngine:
    """Motor combinado das 5 técnicas faltantes."""

    def __init__(self, root: Path = None):
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.three_w = ThreeWEngine(root=self.root)
        self.eisenhower = EisenhowerEngine()
        self.pareto = ParetoEngine(root=self.root)
        self.okr = OKREngine(root=self.root)
        self.idempotency = IdempotencyGuard(root=self.root)

    def full_analysis(self) -> Dict:
        return {
            "3ws_onboarding": self.three_w.generate_welcome_doc()[:500],
            "eisenhower_sample": self.eisenhower.prioritize_tickets([
                {"id": "T1", "status": "OPEN", "violation_level": "L1", "module": "NC-CORE-FR-147", "has_rca": True},
                {"id": "T2", "status": "OPEN", "module": "NC-SCRIPT-FR-999", "age_hours": 100},
            ]),
            "pareto": self.pareto.analyze(),
            "okrs": self.okr.get_current_okrs(),
            "idempotency_test": self.idempotency.check_savepoint("test", "data123")  # True = new
        }


_engine = None
def get_techniques_engine() -> TechniquesEngine:
    global _engine
    if _engine is None: _engine = TechniquesEngine()
    return _engine
