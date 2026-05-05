#!/usr/bin/env python3
"""---
NC-SCR-FR-113 — NC-DS-143: Popular Knowledge Graph com lobes existentes
---
"""

"""---
NC-SCR-FR-113 — NC-DS-143: Popular Knowledge Graph com lobes existentes
---
"""

"""
NC-SCR-FR-113 — NC-DS-143: Popular Knowledge Graph com lobes existentes
Usa Path(__file__) para evitar problemas com caminhos Unicode (ex: acentos).
"""
import re
import sys
from pathlib import Path

# Derivar ROOT a partir da localização do script (sem hardcode)
SCRIPT_DIR = Path(__file__).resolve().parent          # scripts/
FW_DIR     = SCRIPT_DIR.parent                        # 01_neocortex_framework/
ROOT       = FW_DIR.parent                             # TURBOQUANT_V42/

from neocortex.core.file_utils import get_lobes_path
from neocortex.core.kg_service import KGService

kg    = KGService()
LOBES = get_lobes_path() / "lobes"

if not LOBES.exists():
    print(f"ERRO: diretório de lobes não encontrado: {LOBES}")
    sys.exit(1)

# Garantir entidade base
kg.add_entity("memory_lobe", "concept")

added, skipped = 0, 0

for mdc in sorted(LOBES.rglob("*.mdc")):
    try:
        lobe_id = mdc.stem
        kg.add_entity(lobe_id, "lobe")

        try:
            kg.add_relation(lobe_id, "is_a", "memory_lobe")
        except Exception:
            pass  # relação já existe

        text = mdc.read_text("utf-8", errors="replace")

        # Extrair category do frontmatter
        m = re.search(r"category:\s*(.+)", text)
        if m:
            cat = m.group(1).strip()
            kg.add_entity(cat, "concept")
            try:
                kg.add_relation(lobe_id, "category", cat)
            except Exception:
                pass

        # Extrair tags
        t = re.search(r"tags:\s*\[(.+?)\]", text)
        if t:
            for tag in t.group(1).split(","):
                tag = tag.strip().strip("\"'")
                if tag:
                    kg.add_entity(tag, "concept")
                    try:
                        kg.add_relation(lobe_id, "has_tag", tag)
                    except Exception:
                        pass

        added += 1
    except Exception as ex:
        print(f"  skip {mdc.name}: {ex}")
        skipped += 1

stats = kg.get_stats()
print(f"NC-DS-143 OK: {added} lobes processados, {skipped} ignorados")
print(f"KG: {stats.get('total_entities')} entidades | {stats.get('total_relations')} relações")
print(f"Distribuição tipos: {stats.get('entity_type_distribution')}")
