#!/usr/bin/env python3

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.598293'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  - python
---"""

# -*- coding: utf-8 -*-
"""
Gera manifestos para todos os Lobos que no possuem manifesto.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from neocortex.core import get_ledger_service, get_lobe_service, get_manifest_service


def main():
    print("=== GERAO DE MANIFESTOS PARA TODOS OS LOBOS ===\n")

    manifest_service = get_manifest_service()
    lobe_service = get_lobe_service()
    ledger_service = get_ledger_service()

    # Listar todos os Lobos
    lobes_result = lobe_service.list_lobes()
    lobes = lobes_result.get("lobes", [])

    print(f"Total de Lobos encontrados: {len(lobes)}\n")

    # Verificar quais Lobos j tm manifesto
    ledger = ledger_service.get_full_ledger()
    memory_cortex = ledger.get("memory_cortex", {})
    manifests = memory_cortex.get("manifests", {})

    lobes_with_manifest = set(manifests.keys())
    all_lobe_names = [lobe["name"] for lobe in lobes]

    print("Lobos com manifesto existente:", len(lobes_with_manifest))
    print("Lobos sem manifesto:", len(all_lobe_names) - len(lobes_with_manifest))

    # Gerar manifestos para Lobos sem manifesto
    generated = 0
    failed = 0

    for lobe_name in all_lobe_names:
        if lobe_name in lobes_with_manifest:
            print(f"   [SKIP] Lobe '{lobe_name}' j tem manifesto")
            continue

        print(f"   [GEN] Gerando manifesto para '{lobe_name}'...")
        manifest_result = manifest_service.generate_manifest(target=lobe_name)

        if manifest_result.get("success"):
            print(f"   [OK] Manifesto gerado para '{lobe_name}'")
            generated += 1
        else:
            print(
                f"   [WARN] Falha ao gerar manifesto para '{lobe_name}': {manifest_result.get('error', 'Unknown')}"
            )
            failed += 1

    # Gerar manifesto para cortex tambm (se no existir)
    if "cortex" not in lobes_with_manifest:
        print("\n[GEN] Gerando manifesto para cortex...")
        cortex_result = manifest_service.generate_manifest(target="cortex")
        if cortex_result.get("success"):
            print("   [OK] Manifesto gerado para cortex")
            generated += 1
        else:
            print(
                f"   [WARN] Falha ao gerar manifesto para cortex: {cortex_result.get('error', 'Unknown')}"
            )
            failed += 1

    print("\n" + "=" * 60)
    print("RESUMO DA GERAO DE MANIFESTOS")
    print("=" * 60)
    print(f"- Total de Lobos: {len(all_lobe_names)}")
    print(f"- Manifestos existentes: {len(lobes_with_manifest)}")
    print(f"- Manifestos gerados: {generated}")
    print(f"- Falhas: {failed}")

    # Listar todos os manifestos disponveis
    print("\n" + "=" * 60)
    print("MANIFESTOS DISPONVEIS")
    print("=" * 60)

    ledger = ledger_service.get_full_ledger()
    memory_cortex = ledger.get("memory_cortex", {})
    manifests = memory_cortex.get("manifests", {})

    cortex_manifests = {k: v for k, v in manifests.items() if v.get("type") == "cortex"}
    lobe_manifests = {k: v for k, v in manifests.items() if v.get("type") == "lobe"}

    print(f"Manifestos de cortex: {len(cortex_manifests)}")
    print(f"Manifestos de lobes: {len(lobe_manifests)}")

    if lobe_manifests:
        print("\nLobes com manifesto:")
        for lobe_name, manifest in sorted(lobe_manifests.items())[
            :10
        ]:  # Mostrar primeiros 10
            created = manifest.get("created_at", "N/A")[:19]
            print(f"  - {lobe_name} (criado em {created})")

        if len(lobe_manifests) > 10:
            print(f"  ... e mais {len(lobe_manifests) - 10}")


if __name__ == "__main__":
    main()
