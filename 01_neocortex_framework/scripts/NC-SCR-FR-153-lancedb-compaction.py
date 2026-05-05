#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""---
NC-SCR-FR-153-lancedb-compaction.py
---
"""

"""---
NC-SCR-FR-153-lancedb-compaction.py
---
"""

"""
NC-SCR-FR-153-lancedb-compaction.py
Phase 2.2: LanceDB Optimization and Compaction
"""

import os
import shutil
import datetime
from pathlib import Path

try:
    import lancedb
    HAS_LANCEDB = True
except ImportError:
    HAS_LANCEDB = False

ROOT_DIR = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42")
FW_DIR = ROOT_DIR / "01_neocortex_framework"
DB_PATH = FW_DIR / "data" / "vector_db"
BACKUP_DIR = FW_DIR / "DIR-BAK-FR-001-backup-main" / f"lancedb_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

def optimize():
    print("=== LanceDB Compaction Pipeline ===")
    
    if not DB_PATH.exists():
        print(f"[ERROR] Vector DB path {DB_PATH} not found.")
        return

    # 1. Inspect storage footprint before
    db_size_before = sum(f.stat().st_size for f in DB_PATH.rglob('*') if f.is_file())
    transactions_count = len(list((DB_PATH / "neocortex_kgs.lance" / "_transactions").glob("*"))) if (DB_PATH / "neocortex_kgs.lance" / "_transactions").exists() else 0
    versions_count = len(list((DB_PATH / "neocortex_kgs.lance" / "_versions").glob("*"))) if (DB_PATH / "neocortex_kgs.lance" / "_versions").exists() else 0
    
    print(f"[INFO] Initial Size: {db_size_before / (1024**2):.2f} MB")
    print(f"[INFO] Transactions Fragments: {transactions_count}")
    print(f"[INFO] Version Fragments: {versions_count}")

    # 2. Perform Secure Backup
    print(f"[INFO] Creating secure backup at: {BACKUP_DIR.name}...")
    shutil.copytree(str(DB_PATH), str(BACKUP_DIR))
    print("[SUCCESS] Backup completed explicitly.")

    # 3. Compaction
    if not HAS_LANCEDB:
        print("[WARNING] `lancedb` package not locally installed in this env instance, unable to run `compact_files()`.")
        print("[WARNING] However, backup and analysis is complete. Pruning requires the python dependencies loaded.")
        return

    print("[INFO] Connecting to LanceDB engine...")
    try:
        db = lancedb.connect(str(DB_PATH))
        table_names = db.table_names()
        
        for name in table_names:
            print(f"[INFO] Optimizing table: {name}...")
            table = db.open_table(name)
            
            # Compaction
            if hasattr(table, 'compact_files'):
                table.compact_files()
                print("       -> Files compacted.")
            
            # Cleanup old operations
            if hasattr(table, 'cleanup_old_versions'):
                table.cleanup_old_versions()
                print("       -> Old versions pruned.")
                
        print(f"[SUCCESS] Optimization complete for {len(table_names)} tables.")
        
    except Exception as e:
        print(f"[ERROR] LanceDB optimization failed: {e}")

    # 4. Storage Footprint After
    db_size_after = sum(f.stat().st_size for f in DB_PATH.rglob('*') if f.is_file())
    print(f"[RESULT] Final Size: {db_size_after / (1024**2):.2f} MB (Diff: {(db_size_after - db_size_before) / (1024**2):.2f} MB)")

if __name__ == "__main__":
    optimize()
