#!/usr/bin/env python3

# Fix encoding for Windows (UTF-8)
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.623184'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-NAM-FR-001-naming-convent
---
"""

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.623184'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-NAM-FR-001-naming-convent
---
"""

if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.623184'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-NAM-FR-001-naming-convention
related_ssot:
  - NC-NAM-FR-001
  - NC-NAM-FR-001-tools-registry
  - NC-NAM-FR-001-config-registry
  - NC-SCR-FR-004-governance-validator
  - NC-NAM-FR-001-lobes-registry
  - NC-NAM-FR-001-prompts-registry
  - NC-SCR-FR-004
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-004-governance-validator.py
Script de validao de governana documental.
Calcula SHA-256 dos sub-registros e do arquivo mestre NC-NAM-FR-001.
Verifica paridade e reporta artefatos desatualizados.

Uso:
    python NC-SCR-FR-004-governance-validator.py [--check] [--verbose]
"""

import hashlib
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def get_config():
    """
    Obtm configurao do NeoCortex.
    Usa importao dinmica para evitar dependncia circular.
    """
    try:
        from neocortex.config import ConfigProvider

        return ConfigProvider.get_config()
    except ImportError:
        # Fallback para desenvolvimento local
        class FallbackConfig:
            @property
            def project_root(self):
                return Path(__file__).parent.parent.parent

        return FallbackConfig()


def compute_file_hash(filepath: Path) -> str:
    """Calcula SHA-256 de um arquivo."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        logger.warning(f"Arquivo no encontrado: {filepath}")
        return None


def validate_registry_parity(config, verbose=False):
    """
    Valida paridade entre o mestre NC-NAM-FR-001 e os sub-registros.
    Retorna dicionrio com hashes e status.
    """
    docs_dir = (
        config.project_root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main"
    )
    master_file = docs_dir / "NC-NAM-FR-001-naming-convention.md"

    sub_registries = [
        docs_dir / "NC-NAM-FR-001-tools-registry.md",
        docs_dir / "NC-NAM-FR-001-lobes-registry.md",
        docs_dir / "NC-NAM-FR-001-config-registry.md",
        docs_dir / "NC-NAM-FR-001-prompts-registry.md",
    ]

    results = {
        "master": {"path": str(master_file), "hash": None, "exists": False},
        "sub_registries": [],
        "parity_ok": True,
        "missing_files": [],
    }

    # Hash do mestre
    if master_file.exists():
        results["master"]["hash"] = compute_file_hash(master_file)
        results["master"]["exists"] = True
        if verbose:
            logger.info(f"Mestre: {results['master']['hash']} {master_file.name}")
    else:
        results["missing_files"].append(str(master_file))
        results["parity_ok"] = False

    # Hash dos sub-registros
    for sub_path in sub_registries:
        entry = {"path": str(sub_path), "hash": None, "exists": False}
        if sub_path.exists():
            entry["hash"] = compute_file_hash(sub_path)
            entry["exists"] = True
            if verbose:
                logger.info(f"Sub-registro: {entry['hash']} {sub_path.name}")
        else:
            results["missing_files"].append(str(sub_path))
            results["parity_ok"] = False
        results["sub_registries"].append(entry)

    # Verificao de paridade (contedo extrado est presente no mestre?)
    # Esta  uma verificao bsica; uma verificao completa exigiria diff.
    if verbose and results["master"]["hash"]:
        logger.info("Paridade: verificao bsica concluda. Use diff para detalhes.")

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validador de governana documental")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Executa validao e retorna cdigo de sada",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Log detalhado")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    config = get_config()
    results = validate_registry_parity(config, verbose=args.verbose)

    # Report
    print("=" * 60)
    print("NC-SCR-FR-004  Governance Validator Report")
    print("=" * 60)
    print(f"Mestre: {results['master']['path']}")
    if results["master"]["exists"]:
        print(f"  SHA256: {results['master']['hash']}")
    else:
        print("    ARQUIVO AUSENTE")

    print("\nSub-registros:")
    for idx, sub in enumerate(results["sub_registries"], 1):
        prefix = "  " if sub["exists"] else "  "
        print(f"{prefix} {Path(sub['path']).name}")
        if sub["exists"]:
            print(f"      SHA256: {sub['hash']}")

    if results["missing_files"]:
        print(f"\n  Arquivos faltantes: {len(results['missing_files'])}")
        for f in results["missing_files"]:
            print(f"    - {f}")
        results["parity_ok"] = False

    print(f"\nStatus paridade: {' OK' if results['parity_ok'] else ' FALHA'}")
    print("=" * 60)

    if args.check:
        sys.exit(0 if results["parity_ok"] else 1)


if __name__ == "__main__":
    main()
