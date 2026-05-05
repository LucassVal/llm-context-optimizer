#!/usr/bin/env python3
"""---
NC-SCR-FR-112 — Gerador de .manifest.json por Lobe (NC-DS-142)
---
"""

"""---
NC-SCR-FR-112 — Gerador de .manifest.json por Lobe (NC-DS-142)
---
"""

"""
NC-SCR-FR-112 — Gerador de .manifest.json por Lobe (NC-DS-142)
Dual-Representation: cria/atualiza NC-MANIFEST-*.json para cada lobe .mdc
"""
import json
import re
from datetime import datetime
import sys
from pathlib import Path

# Add framework to path for neocortex imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "01_neocortex_framework"))

from neocortex.core.file_utils import get_lobes_path

LOBES   = get_lobes_path() / "lobes"
CREATED = 0

def extract_frontmatter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta

for mdc in sorted(LOBES.rglob("*.mdc")):
    text = mdc.read_text("utf-8", errors="replace")
    fm   = extract_frontmatter(text)
    manifest = {
        "lobe_id":     fm.get("lobe_id", mdc.stem),
        "name":        fm.get("name", mdc.stem),
        "category":    fm.get("category", "uncategorized"),
        "description": fm.get("description", ""),
        "tags":        [t.strip("[] ") for t in fm.get("tags", "").split(",") if t.strip()],
        "status":      fm.get("status", "active"),
        "file":        str(mdc.relative_to(ROOT)),
        "size_bytes":  mdc.stat().st_size,
        "generated":   datetime.now().isoformat(timespec="seconds"),
    }
    out = mdc.parent / f"NC-MANIFEST-{mdc.stem}.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    CREATED += 1

print(f"✅ NC-DS-142: {CREATED} manifests .json gerados em {LOBES}")
