#!/usr/bin/env python3
"""
NC-SCR-FR-154 - Atualizar SSOT após alpha testing
Atualiza o SSOT com os novos arquivos criados durante o alpha testing.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def main():
    """Atualizar SSOT com novos arquivos."""
    project_root = Path(__file__).parent.parent
    ssot_path = project_root / "NC-REF-UPDATE-REPORT-20260421_232200.json"
    
    if not ssot_path.exists():
        print(f"SSOT não encontrado: {ssot_path}")
        return False
    
    print(f"Carregando SSOT: {ssot_path}")
    with open(ssot_path, 'r', encoding='utf-8') as f:
        ssot = json.load(f)
    
    # Novos arquivos criados durante alpha testing
    new_files = [
        # Open-source prep
        "LICENSE",
        ".gitignore",
        "README.md",
        "NC-SCR-FR-122-white-label-anonymizer.py",
        "NC-PAPER-FR-001-fractal-memory-architecture.md",
        
        # Testing
        "05_examples/NC-TEST-FR-150-smoke-test-40-tools.py",
        "05_examples/NC-RPT-150-smoke-test-results.json",
        
        # Memory hooks
        "01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-004-conversation-hook.py",
        "01_neocortex_framework/scripts/NC-SCR-FR-152-activate-memory-hook.py",
        "01_neocortex_framework/scripts/NC-BOOT-FR-002-memory-hook.py",
        
        # Checkpoint
        "05_examples/NC-SCR-FR-153-checkpoint-alpha.py",
        
        # Este script
        "05_examples/NC-SCR-FR-154-update-ssot.py",
    ]
    
    # Verificar quais existem
    existing_files = []
    for file in new_files:
        full_path = project_root / file
        if full_path.exists():
            existing_files.append(file)
            print(f"  [ADD] {file}")
        else:
            print(f"  [MISS] {file}")
    
    # Atualizar SSOT
    if "files" not in ssot:
        ssot["files"] = []
    
    # Adicionar novos arquivos (se não existirem)
    current_files = {f["path"] for f in ssot["files"]}
    added_count = 0
    
    for file in existing_files:
        if file not in current_files:
            ssot["files"].append({
                "path": file,
                "type": "file",
                "added": datetime.now().isoformat(),
                "source": "alpha_testing_2026-04-22",
                "description": f"Criado durante alpha testing do NeoCortex"
            })
            added_count += 1
    
    # Atualizar metadata
    ssot["last_updated"] = datetime.now().isoformat()
    ssot["update_reason"] = "Alpha testing completion - new files added"
    ssot["total_files"] = len(ssot["files"])
    
    # Salvar SSOT atualizado
    new_ssot_path = project_root / f"NC-REF-UPDATE-REPORT-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(new_ssot_path, 'w', encoding='utf-8') as f:
        json.dump(ssot, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] SSOT atualizado!")
    print(f"   Arquivos adicionados: {added_count}")
    print(f"   Total arquivos no SSOT: {ssot['total_files']}")
    print(f"   Novo SSOT salvo em: {new_ssot_path.name}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)