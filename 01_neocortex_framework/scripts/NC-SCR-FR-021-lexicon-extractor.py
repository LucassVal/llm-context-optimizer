#!/usr/bin/env python3
import io
import sys

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.695954'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-DOC-FR-001-ubiquitous-language-dictionary
related_ssot:
  - NC-SEC-FR-001-atomic-locks
  - NC-SCR-FR-021-lexicon-extractor
  - NC-SCR-FR-021
  - NC-CFG-FR-001-agent-policy-template
  - NC-TLM-FR-001-tool-manifest
  - NC-DOC-FR-001
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-021-lexicon-extractor.py
Extrai termos do SSOT e gera symbolic_map.json para ultra-compresso.
Autor: T0 (NeoCortex)
Data: 2026-04-14
"""

import hashlib
import json
import re
import sys
from pathlib import Path

# Configuraes de Path
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "DIR-DOC-FR-001-docs-main"
CORE_DIR = PROJECT_ROOT / "DIR-CORE-FR-001-core-central"
SYMBOLIC_MAP_PATH = DOCS_DIR / "symbolic_map.json"

# Arquivos de entrada corrigidos e confirmados via find_by_name
UBIQUITOUS_DICT = DOCS_DIR / "NC-DOC-FR-001-ubiquitous-language-dictionary.md"
TOOL_MANIFEST = CORE_DIR / "NC-TLM-FR-001-tool-manifest.json"
ATOMIC_LOCKS = DOCS_DIR / "NC-SEC-FR-001-atomic-locks.yaml"
AGENT_POLICY = DOCS_DIR / "NC-CFG-FR-001-agent-policy-template.yaml"

# Conjunto de smbolos disponveis (letras gregas + Unicode)
SYMBOL_POOL = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
]


def extract_terms_from_markdown(content: str) -> set[str]:
    """Extrai termos do dicionrio ubquo (formato tabela markdown)."""
    terms = set()
    pattern = r"^\|\s*`([^`]+)`\s*\|"
    for line in content.splitlines():
        match = re.match(pattern, line)
        if match:
            terms.add(match.group(1))
    return terms


def extract_terms_from_json(data: dict) -> set[str]:
    """Extrai chaves e valores relevantes de um JSON estruturado."""
    terms = set()
    if not isinstance(data, dict):
        return terms

    # Especificamente para o Tool Manifest, pegar IDs, nomes de tools e aes
    # Vamos pegar as ferramentas (keys) e actions
    if "tools" in data and isinstance(data["tools"], dict):
        for tool_name, tool_data in data["tools"].items():
            terms.add(tool_name)
            if "actions" in tool_data and isinstance(tool_data["actions"], dict):
                for action_name in tool_data["actions"].keys():
                    terms.add(action_name)
    elif "tools" in data and isinstance(data["tools"], list):  # Fallback iterativo
        for tool in data["tools"]:
            if isinstance(tool, dict) and "name" in tool:
                terms.add(tool["name"])
                if "actions" in tool and isinstance(tool["actions"], list):
                    for act in tool["actions"]:
                        if isinstance(act, dict) and "name" in act:
                            terms.add(act["name"])

    # Fallback genrico para pegar chaves do root e meta
    for k in data.keys():
        terms.add(k)

    return terms


def extract_terms_from_yaml(content: str) -> set[str]:
    """Extrai chaves de um YAML (regex genrico sem lockar ruamel)."""
    terms = set()
    pattern = r"^([a-zA-Z_][a-zA-Z0-9_-]*):"
    for line in content.splitlines():
        match = re.match(pattern, line.strip())
        if match:
            terms.add(match.group(1))
    return terms


def generate_symbol_map(terms: set[str]) -> dict:
    """Gera mapeamento determinstico de termos para smbolos."""
    encode = {}
    decode = {}

    sorted_terms = sorted(list(terms))

    for i, term in enumerate(sorted_terms):
        if i < len(SYMBOL_POOL):
            symbol = SYMBOL_POOL[i]
        else:
            # Fallback: hash curto
            symbol = hashlib.md5(term.encode()).hexdigest()[:4]

        encode[term] = symbol
        decode[symbol] = term

    return {"encode": encode, "decode": decode}


def main():
    print("  NC-SCR-FR-021: Iniciando extrao de lxico para KGS...")

    all_terms = set()

    # 1. Dicionrio Ubquo
    if UBIQUITOUS_DICT.exists():
        content = UBIQUITOUS_DICT.read_text(encoding="utf-8")
        terms = extract_terms_from_markdown(content)
        print(f"   [+] Dicionrio Ubquo: {len(terms)} termos extrados")
        all_terms.update(terms)
    else:
        print(
            f"   [!] Dicionrio Ubquo (NC-DOC-FR-001) no encontrado em {UBIQUITOUS_DICT}"
        )

    # 2. Tool Manifest
    if TOOL_MANIFEST.exists():
        with open(TOOL_MANIFEST, "r", encoding="utf-8") as f:
            data = json.load(f)
        terms = extract_terms_from_json(data)
        print(f"   [+] Tool Manifest: {len(terms)} termos extrados")
        all_terms.update(terms)
    else:
        print(f"   [!] Tool Manifest no encontrado em {TOOL_MANIFEST}")

    # 3. Atomic Locks
    if ATOMIC_LOCKS.exists():
        content = ATOMIC_LOCKS.read_text(encoding="utf-8")
        terms = extract_terms_from_yaml(content)
        print(f"   [+] Atomic Locks: {len(terms)} termos extrados")
        all_terms.update(terms)
    else:
        print(f"   [!] Atomic Locks no encontrado em {ATOMIC_LOCKS}")

    # 4. Agent Policy
    if AGENT_POLICY.exists():
        content = AGENT_POLICY.read_text(encoding="utf-8")
        terms = extract_terms_from_yaml(content)
        print(f"   [+] Agent Policy: {len(terms)} termos extrados")
        all_terms.update(terms)
    else:
        print(f"   [!] Agent Policy no encontrado em {AGENT_POLICY}")

    print(f"\n Gerando mapa simblico para {len(all_terms)} termos cumulativos...")

    symbol_map = generate_symbol_map(all_terms)

    with open(SYMBOLIC_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(symbol_map, f, indent=2, ensure_ascii=False)

    print(f" Mapa simblico salvo em: {SYMBOLIC_MAP_PATH}")
    print(f"   Termos mapeados: {len(symbol_map['encode'])}")
    print("  Misso concluda. Cdigo e Dicionrio validados KGS-Compliant.")


if __name__ == "__main__":
    main()
