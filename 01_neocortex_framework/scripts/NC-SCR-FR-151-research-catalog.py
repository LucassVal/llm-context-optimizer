#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""---
NC-SCR-FR-151-research-catalog.py
---
"""

"""---
NC-SCR-FR-151-research-catalog.py
---
"""

"""
NC-SCR-FR-151-research-catalog.py

Phase 1 Consolidation: Scans DIR-RES-CC-001-claude-leak-workzone, 
generates a catalog YAML, and moves syntheses to $temporal/research.
"""

import os
import shutil
import sys
import datetime
from pathlib import Path

# Add framework to path for neocortex imports
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR / "01_neocortex_framework"))

from neocortex.core.file_utils import get_lobes_path

# Try to use ruamel.yaml if available, else standard yaml
try:
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.default_flow_style = False
    has_ruamel = True
except ImportError:
    import yaml
    has_ruamel = False

SOURCE_DIR = ROOT_DIR / "DIR-RES-CC-001-claude-leak-workzone"
TEMPORAL_RESEARCH_DIR = get_lobes_path() / "$temporal" / "research"
CATALOG_PATH = ROOT_DIR / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-CAT-FR-001-research-catalog.yaml"

def build_catalog():
    if not SOURCE_DIR.exists():
        print(f"[ERROR] Source directory not found: {SOURCE_DIR}")
        return

    TEMPORAL_RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    catalog = {
        "metadata": {
            "name": "Research Catalog",
            "version": "1.0",
            "last_updated": datetime.datetime.now().isoformat(),
            "description": "Consolidated catalog of legacy and loose research analyses."
        },
        "entries": []
    }

    print(f"[INFO] Scanning {SOURCE_DIR}...")
    for file_path in SOURCE_DIR.glob("*.*"):
        if not file_path.is_file():
            continue
            
        ext = file_path.suffix.lower()
        if ext not in [".md", ".yaml"]:
            continue
            
        # Extract basic metadata from filename
        filename = file_path.name
        
        # Deduce topic and type
        topic = "general"
        doc_type = "synthesis"
        if "gov" in filename.lower(): topic = "governance"
        elif "res" in filename.lower(): topic = "research"
        elif "ana" in filename.lower(): topic = "analysis"
        elif "str" in filename.lower(): topic = "strategy"
        
        entry = {
            "id": filename.replace(ext, ""),
            "original_filename": filename,
            "type": doc_type,
            "topic": topic,
            "tags": ["legacy", "consolidation", topic],
            "cataloged_date": datetime.datetime.now().isoformat(),
            "new_location": f"$temporal/research/{filename}"
        }
        catalog["entries"].append(entry)
        
        # Move the file
        dest_path = TEMPORAL_RESEARCH_DIR / filename
        shutil.move(str(file_path), str(dest_path))
        print(f"[MOVED] {filename} -> {dest_path}")

    # Write YAML catalog
    if has_ruamel:
        with open(CATALOG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(catalog, f)
    else:
        with open(CATALOG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(catalog, f, default_flow_style=False, sort_keys=False)

    print(f"[SUCCESS] Catalog written to {CATALOG_PATH}")
    print(f"[SUCCESS] Total entries cataloged: {len(catalog['entries'])}")

if __name__ == "__main__":
    build_catalog()
