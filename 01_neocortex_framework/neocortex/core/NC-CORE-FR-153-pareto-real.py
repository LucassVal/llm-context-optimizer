"""---
@Engine NC-CORE-FR-153-pareto-real mcp NC-CORE-FR-153-pareto-real.py — Conecta ParetoEngi
---
"""


import os
import pathlib
import sqlite3
from datetime import datetime
from typing import Dict


class ParetoReal:
    """Pareto conectado ao neocortex_wal.db (SQLite)."""

    def __init__(self, root: Optional[pathlib.Path] = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self.wal_path = self.root / "DIR-DS-003-wal" / "neocortex_wal.db"

    def analyze_from_db(self) -> Dict:
        if not self.wal_path.exists():
            return {"error": "wal_db_not_found", "path": str(self.wal_path)}

        conn = sqlite3.connect(str(self.wal_path))
        try:
            # Query: rollbacks por modulo (extrai NC- do file_path)
            cursor = conn.execute("""
                SELECT file_path, COUNT(*) as rollback_count
                FROM wal_log
                WHERE rollback_ref IS NOT NULL
                GROUP BY file_path
                ORDER BY rollback_count DESC
            """)
            rows = cursor.fetchall()

            total_errors = sum(r[1] for r in rows)
            if total_errors == 0:
                return {
                    "total_modules_with_errors": 0,
                    "total_errors": 0,
                    "pareto_holds": False,
                    "message": "Nenhum rollback encontrado — sistema sadio",
                    "timestamp": datetime.now().isoformat(),
                }

            # Extract module from file_path pattern
            mod_errors = {}
            for file_path, count in rows:
                mod = self._extract_module(file_path)
                mod_errors[mod] = mod_errors.get(mod, 0) + count

            sorted_mods = sorted(mod_errors.items(), key=lambda x: x[1], reverse=True)
            top_n = max(1, len(sorted_mods) // 5)
            top_offenders = sorted_mods[:top_n]
            top_errors = sum(v for _, v in top_offenders)
            pct = round(top_errors / total_errors * 100, 1)

            # Most common operations
            cursor2 = conn.execute("""
                SELECT operation, COUNT(*) as cnt
                FROM wal_log
                WHERE rollback_ref IS NOT NULL
                GROUP BY operation
                ORDER BY cnt DESC
                LIMIT 10
            """)
            ops = [(op, cnt) for op, cnt in cursor2.fetchall()]

            return {
                "total_files_with_rollbacks": len(rows),
                "total_rollbacks": total_errors,
                "top_20pct_count": top_n,
                "top_20pct_rollbacks": top_errors,
                "top_20pct_rollback_pct": pct,
                "pareto_holds": pct >= 70,
                "top_offenders": [{"module": m, "count": c} for m, c in top_offenders[:10]],
                "most_rolled_back_ops": ops,
                "foco_fiscalizatorio": {
                    "deve_focar": [m for m, _ in top_offenders[:min(5, len(top_offenders))]],
                    "conceito": "20% dos arquivos geram 80% dos rollbacks",
                    "recomendacao": "Focar Gateway + tests nos top offenders",
                },
                "timestamp": datetime.now().isoformat(),
            }
        finally:
            conn.close()

    @staticmethod
    def _extract_module(file_path: str) -> str:
        import re
        if not file_path:
            return "unknown"
        # Try NC- pattern
        m = re.search(r'NC-[A-Z]+-[A-Z]+-\d+', file_path)
        if m:
            return m.group()
        # Fallback: directory-based module
        parts = file_path.replace("\\", "/").split("/")
        if len(parts) >= 2:
            return "/".join(parts[-2:])
        return file_path

    def check_wal_schema(self) -> Dict:
        if not self.wal_path.exists():
            return {"error": "wal_db_not_found"}
        conn = sqlite3.connect(str(self.wal_path))
        try:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cursor.fetchall()]
            schema = {}
            for t in tables:
                cursor2 = conn.execute(f"PRAGMA table_info('{t}')")
                schema[t] = [{"name": r[1], "type": r[2]} for r in cursor2.fetchall()]
            return {"tables": tables, "schema": schema, "path": str(self.wal_path)}
        finally:
            conn.close()


_pareto = None
def get_pareto():
    global _pareto
    if _pareto is None:
        _pareto = ParetoReal()
    return _pareto
