# Stub — NC-INFRA ledger_store replacement (T0 2026-05-04)
import json
from pathlib import Path


class LedgerStore:
    def __init__(self, *a, **kw):
        self._path = kw.get('path', Path('data/ledger.json'))
    def record(self, *a, **kw): pass
    def query(self, *a, **kw): return []
    def read_ledger(self):
        try: return json.loads(self._path.read_text())
        except: return {}
    def write_ledger(self, data):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, indent=2))
    def close(self): pass
