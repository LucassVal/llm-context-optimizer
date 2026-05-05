"""---
NC-SVC-FR-016-wal-service.py
---
"""



import hashlib
import sqlite3
import threading
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
_SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS wal_sessions (
    session_id   TEXT PRIMARY KEY,
    agent        TEXT    NOT NULL,
    ticket_id    TEXT,
    started_at   TEXT    NOT NULL,
    committed_at TEXT,
    status       TEXT    NOT NULL DEFAULT 'OPEN'
    -- status: OPEN | COMMITTED | ROLLED_BACK
);

CREATE TABLE IF NOT EXISTS wal_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   TEXT    NOT NULL REFERENCES wal_sessions(session_id),
    timestamp    TEXT    NOT NULL,
    operation    TEXT    NOT NULL,  -- CREATE | MODIFY | DELETE | MOVE
    file_path    TEXT    NOT NULL,
    ticket_id    TEXT,
    before_hash  TEXT,              -- sha256 antes da operação (NULL se CREATE)
    after_hash   TEXT,              -- sha256 após a operação (NULL se DELETE)
    rollback_ref INTEGER            -- id da entrada que reverteu esta
);

CREATE INDEX IF NOT EXISTS idx_wal_session ON wal_log(session_id);
CREATE INDEX IF NOT EXISTS idx_wal_path    ON wal_log(file_path);
CREATE INDEX IF NOT EXISTS idx_wal_time    ON wal_log(timestamp);
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256(path: Path) -> str | None:
    """Retorna sha256 do arquivo ou None se não existir."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except (FileNotFoundError, PermissionError):
        return None


def _now() -> str:
    return datetime.now(UTC).isoformat()


# ---------------------------------------------------------------------------
# WALService
# ---------------------------------------------------------------------------

class WALService:
    """
    Serviço de Write-Ahead Log para operações de filesystem do NeoCortex.

    Uso básico:
        wal = WALService()
        with wal.transaction("session-abc", "T0-Antigravity", ticket_id="NC-DS-090") as txn:
            before = txn.before_write("path/to/file.yaml")
            # ... modifica o arquivo ...
            txn.after_write("path/to/file.yaml", before)

        wal.commit_session("session-abc")

    Rollback:
        wal.rollback_session("session-abc")  # lista operações reversíveis
    """

    _instances: "dict[str, WALService]" = {}
    _lock = threading.Lock()

    def __new__(cls, db_path: Path | None = None) -> "WALService":
        key = str(db_path or "default")
        with cls._lock:
            if key not in cls._instances:
                instance = object.__new__(cls)
                object.__setattr__(instance, "_initialized", False)
                cls._instances[key] = instance
            return cls._instances[key]

    def __init__(self, db_path: Path | None = None) -> None:
        if object.__getattribute__(self, "_initialized"):
            return
        self._db_path: Path = db_path or self._default_db_path()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local: threading.local = threading.local()
        self._init_db()
        object.__setattr__(self, "_initialized", True)

    @staticmethod
    def _default_db_path() -> Path:
        """Resolve project_root pelo marcador .git (único na raiz do repo)."""
        here = Path(__file__).resolve()
        for parent in here.parents:
            if (parent / ".git").exists():
                return parent / "DIR-DS-003-wal" / "neocortex_wal.db"
        # fallback: relativo ao CWD (quando rodado diretamente)
        return Path("DIR-DS-003-wal") / "neocortex_wal.db"

    def _get_conn(self) -> sqlite3.Connection:
        conn: sqlite3.Connection | None = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._local.conn = conn  # type: ignore[attr-defined]
        return conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        conn.executescript(_SCHEMA)
        conn.commit()

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def open_session(self, session_id: str, agent: str, ticket_id: str | None = None) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT OR IGNORE INTO wal_sessions (session_id, agent, ticket_id, started_at, status)"
            " VALUES (?, ?, ?, ?, 'OPEN')",
            (session_id, agent, ticket_id, _now()),
        )
        conn.commit()

    def commit_session(self, session_id: str) -> None:
        conn = self._get_conn()
        conn.execute(
            "UPDATE wal_sessions SET status='COMMITTED', committed_at=? WHERE session_id=?",
            (_now(), session_id),
        )
        conn.commit()

    def rollback_session(self, session_id: str) -> list[dict]:
        """
        Marca a sessão como ROLLED_BACK e retorna a lista de operações
        que precisam ser revertidas manualmente (WAL não desfaz arquivos
        automaticamente — fornece o mapa para rollback manual ou script externo).
        """
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM wal_log WHERE session_id=? ORDER BY id DESC",
            (session_id,),
        ).fetchall()

        conn.execute(
            "UPDATE wal_sessions SET status='ROLLED_BACK', committed_at=? WHERE session_id=?",
            (_now(), session_id),
        )
        conn.execute(
            "UPDATE wal_log SET rollback_ref=-1 WHERE session_id=?",
            (session_id,),
        )
        conn.commit()

        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # File operation logging
    # ------------------------------------------------------------------

    def log_operation(
        self,
        session_id: str,
        operation: str,
        file_path: str,
        ticket_id: str | None = None,
        before_hash: str | None = None,
        after_hash: str | None = None,
    ) -> int:
        """Registra uma operação no WAL. Retorna o id da entrada."""
        conn = self._get_conn()
        cur = conn.execute(
            "INSERT INTO wal_log (session_id, timestamp, operation, file_path, ticket_id, before_hash, after_hash)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, _now(), operation, file_path, ticket_id, before_hash, after_hash),
        )
        conn.commit()
        return cur.lastrowid or 0

    def capture_before(self, path) -> str | None:
        """Captura hash antes de modificar um arquivo. Retorna o hash ou None."""
        return _sha256(Path(path))

    def capture_after(self, path) -> str | None:
        """Captura hash após modificar um arquivo. Retorna o hash ou None."""
        return _sha256(Path(path))

    # ------------------------------------------------------------------
    # Context manager: WALTransaction
    # ------------------------------------------------------------------

    @contextmanager
    def transaction(
        self,
        session_id: str,
        agent: str,
        ticket_id: str | None = None,
    ) -> Generator["_WALTransaction", None, None]:
        """
        Context manager para agrupar operações numa sessão WAL.

        with wal.transaction("s-001", "T0-Antigravity", "NC-DS-090") as txn:
            bh = txn.before_write("arquivo.yaml")
            # ... modifica ...
            txn.after_write("arquivo.yaml", bh)
        # commit automático ao sair sem exceção
        # rollback_session() marcado em caso de exceção
        """
        self.open_session(session_id, agent, ticket_id)
        txn = _WALTransaction(self, session_id, ticket_id)
        try:
            yield txn
            self.commit_session(session_id)
        except Exception:
            self.rollback_session(session_id)
            raise

    # ------------------------------------------------------------------
    # Query / audit
    # ------------------------------------------------------------------

    def get_session_summary(self, session_id: str) -> dict:
        conn = self._get_conn()
        session = conn.execute(
            "SELECT * FROM wal_sessions WHERE session_id=?", (session_id,)
        ).fetchone()
        entries = conn.execute(
            "SELECT * FROM wal_log WHERE session_id=? ORDER BY id",
            (session_id,),
        ).fetchall()
        return {
            "session": dict(session) if session else {},
            "entries": [dict(e) for e in entries],
            "total_ops": len(entries),
        }

    def get_file_history(self, file_path: str, limit: int = 20) -> list[dict]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT l.*, s.agent, s.status as session_status"
            " FROM wal_log l JOIN wal_sessions s ON l.session_id=s.session_id"
            " WHERE l.file_path=? ORDER BY l.id DESC LIMIT ?",
            (file_path, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_open_sessions(self) -> list[dict]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM wal_sessions WHERE status='OPEN' ORDER BY started_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def stats(self) -> dict:
        conn = self._get_conn()
        total_entries = conn.execute("SELECT COUNT(*) FROM wal_log").fetchone()[0]
        sessions = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM wal_sessions GROUP BY status"
        ).fetchall()
        return {
            "total_log_entries": total_entries,
            "sessions": {r["status"]: r["cnt"] for r in sessions},
            "db_path": str(self._db_path),
            "db_size_kb": (self._db_path.stat().st_size / 1024) if self._db_path.exists() else 0.0,
        }

    # ------------------------------------------------------------------
    # TTL pruning (resolve TTL-002)
    # ------------------------------------------------------------------

    def prune_old_entries(self, days: int = 30) -> int:
        """
        Remove entradas COMMITTED com mais de `days` dias.
        Entradas OPEN ou ROLLED_BACK são preservadas independente da idade.
        Retorna quantidade de entradas removidas.
        """
        cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()
        conn = self._get_conn()

        # IDs de sessões COMMITTED antigas
        old_sessions = conn.execute(
            "SELECT session_id FROM wal_sessions"
            " WHERE status='COMMITTED' AND committed_at < ?",
            (cutoff,),
        ).fetchall()

        if not old_sessions:
            return 0

        ids = [r["session_id"] for r in old_sessions]
        placeholders = ",".join("?" * len(ids))

        cur = conn.execute(
            f"DELETE FROM wal_log WHERE session_id IN ({placeholders})", ids
        )
        conn.execute(
            f"DELETE FROM wal_sessions WHERE session_id IN ({placeholders})", ids
        )
        conn.commit()
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        return cur.rowcount


# ---------------------------------------------------------------------------
# _WALTransaction (helper interno ao context manager)
# ---------------------------------------------------------------------------

class _WALTransaction:
    """Helper para uso dentro do context manager `wal.transaction()`."""

    def __init__(self, service: WALService, session_id: str, ticket_id: str | None):
        self._svc = service
        self.session_id = session_id
        self.ticket_id = ticket_id

    def before_write(self, path) -> str | None:
        """Captura hash antes de modificar. Retorna hash para passar ao after_write."""
        return self._svc.capture_before(path)

    def after_write(self, path, before_hash: str | None = None) -> int:
        after_hash = self._svc.capture_after(path)
        op = "CREATE" if before_hash is None else "MODIFY"
        return self._svc.log_operation(
            self.session_id, op, str(path),
            ticket_id=self.ticket_id,
            before_hash=before_hash,
            after_hash=after_hash,
        )

    def log_delete(self, path, before_hash: str | None = None) -> int:
        bh = before_hash or self._svc.capture_before(path)
        return self._svc.log_operation(
            self.session_id, "DELETE", str(path),
            ticket_id=self.ticket_id,
            before_hash=bh,
            after_hash=None,
        )

    def log_move(self, src: str, dst: str) -> int:
        return self._svc.log_operation(
            self.session_id, "MOVE", f"{src} -> {dst}",
            ticket_id=self.ticket_id,
        )


# ---------------------------------------------------------------------------
# CLI — uso direto
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import sys

    wal = WALService()

    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"

    if cmd == "stats":
        print(json.dumps(wal.stats(), indent=2))

    elif cmd == "sessions":
        rows = wal.get_open_sessions()
        print(f"Sessões OPEN: {len(rows)}")
        for r in rows:
            print(f"  {r['session_id']} | {r['agent']} | {r['started_at']}")

    elif cmd == "history" and len(sys.argv) > 2:
        rows = wal.get_file_history(sys.argv[2])
        print(json.dumps(rows, indent=2))

    elif cmd == "prune":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        removed = wal.prune_old_entries(days=days)
        print(f"Entradas removidas (>{days}d): {removed}")

    elif cmd == "rollback" and len(sys.argv) > 2:
        ops = wal.rollback_session(sys.argv[2])
        print("Sessão marcada como ROLLED_BACK. Operações para reverter manualmente:")
        for op in ops:
            print(f"  [{op['operation']}] {op['file_path']}")
            if op.get("before_hash"):
                print(f"    before: {op['before_hash'][:16]}...")

    else:
        print("Uso: NC-SVC-FR-016-wal-service.py [stats|sessions|history <path>|prune [days]|rollback <session_id>]")
