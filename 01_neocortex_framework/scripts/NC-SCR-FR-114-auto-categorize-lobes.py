#!/usr/bin/env python3
"""---
NC-SCR-FR-114 — NC-DS-148: Auto-Categorização de Lobes com Qwen 1.5b
---
"""

"""---
NC-SCR-FR-114 — NC-DS-148: Auto-Categorização de Lobes com Qwen 1.5b
---
"""

"""
NC-SCR-FR-114 — NC-DS-148: Auto-Categorização de Lobes com Qwen 1.5b
Usa Ollama local para categorizar e enriquecer metadados dos arquivos .mdc.

Saída por arquivo:
  - category (taxonomy NeoCortex)
  - tags sugeridas
  - resumo 1 linha
  - priority_score (0-10)

Resultado salvo em: NC-CAT-{lobe_stem}.json (junto ao .mdc)
"""
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

# Config
OLLAMA_URLS = [
    "http://localhost:11435",  # iGPU (preferencial)
    "http://localhost:11434",  # CUDA (fallback)
]
import sys
from pathlib import Path

MODEL = "qwen2.5-coder:1.5b-instruct"
ROOT  = Path(__file__).resolve().parents[2]

# Add framework to path for neocortex imports
sys.path.append(str(ROOT / "01_neocortex_framework"))
from neocortex.core.file_utils import get_lobes_path

LOBES_DIR = get_lobes_path()

# Taxonomia NeoCortex
CATEGORIES = [
    "01_architecture",     # ADRs, design, estrutura
    "02_security",         # Segurança, locks, policies
    "03_orchestration",    # Agentes, tarefas, workflows
    "04_cc_patterns",      # Padrões de código, boas práticas
    "05_machine_learning", # LLMs, modelos, inferência
    "06_infrastructure",   # MCP, litellm, serviços
    "07_governance",       # Roadmap, SSOT, regras
    "08_integration",      # APIs, picoclaw, external
    "09_documentation",    # Docs, templates, guias
    "10_experimental",     # Experimentos, PoCs
]


def _ollama_url() -> str:
    """Retorna o primeiro Ollama respondendo."""
    for base in OLLAMA_URLS:
        try:
            req = urllib.request.Request(f"{base}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2):
                return base
        except Exception:
            continue
    raise RuntimeError("Nenhum Ollama disponível em :11434/:11435")


def _ask_qwen(prompt: str, ollama_base: str, max_tokens: int = 200) -> str:
    """Chama Qwen 1.5b via Ollama REST API."""
    body = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0.1},
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{ollama_base}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except Exception as e:
        return f"ERROR: {e}"


def categorize_lobe(mdc_path: Path, ollama_base: str) -> dict:
    """Categoriza um .mdc usando Qwen 1.5b."""
    text = mdc_path.read_text("utf-8", errors="replace")
    # Truncar para economizar tokens
    excerpt = text[:800]

    categories_str = "\n".join(f"  - {c}" for c in CATEGORIES)

    prompt = f"""You are a classifier for a software framework documentation system.
Given the following file content, respond with ONLY a JSON object (no explanation):

File: {mdc_path.name}
Content excerpt:
---
{excerpt}
---

Categories available:
{categories_str}

Respond with ONLY this JSON (no markdown, no explanation):
{{"category": "<one of the categories above>", "tags": ["tag1", "tag2", "tag3"], "summary": "<one sentence in Portuguese>", "priority_score": <0-10>}}"""

    response = _ask_qwen(prompt, ollama_base, max_tokens=150)

    # Extrair JSON da resposta
    try:
        # Tentar extrair JSON diretamente
        match = re.search(r'\{[^{}]+\}', response, re.DOTALL)
        if match:
            result = json.loads(match.group())
            # Validar campos
            if result.get("category") not in CATEGORIES:
                result["category"] = _fallback_category(mdc_path.name, text)
            return result
    except Exception:
        pass

    # Fallback: categorização por keywords
    return {
        "category": _fallback_category(mdc_path.name, text),
        "tags": _extract_tags(mdc_path.name),
        "summary": f"Lobe {mdc_path.stem} — categorizado por fallback",
        "priority_score": 5,
    }


def _fallback_category(filename: str, content: str) -> str:
    """Categorização por keywords sem LLM."""
    fn = filename.lower() + content[:300].lower()
    if any(k in fn for k in ["security", "lock", "policy", "guardian", "sec-"]):
        return "02_security"
    if any(k in fn for k in ["llm", "qwen", "ollama", "model", "inference", "benchmark"]):
        return "05_machine_learning"
    if any(k in fn for k in ["mcp", "litellm", "server", "infra", "picoclaw"]):
        return "06_infrastructure"
    if any(k in fn for k in ["orchestrat", "agent", "task", "courier", "engineer"]):
        return "03_orchestration"
    if any(k in fn for k in ["arch", "design", "adr", "structure"]):
        return "01_architecture"
    if any(k in fn for k in ["governance", "roadmap", "ssot", "naming", "rule"]):
        return "07_governance"
    if any(k in fn for k in ["igpu", "ipex", "integration", "api"]):
        return "08_integration"
    if any(k in fn for k in ["pattern", "practice", "guideline", "karpathy"]):
        return "04_cc_patterns"
    return "09_documentation"


def _extract_tags(filename: str) -> list:
    parts = re.split(r'[-_]', filename.lower().replace(".mdc", ""))
    return [p for p in parts if len(p) > 2 and p not in ("nc", "lbe", "fr", "int", "001", "002")][:4]


def main():
    print("NC-DS-148: Auto-Categorização com Qwen 1.5b")
    print(f"Root: {ROOT}")

    # Descobrir Ollama disponível
    try:
        ollama_base = _ollama_url()
        print(f"Ollama: {ollama_base}")
    except RuntimeError as e:
        print(f"ERRO: {e} — usando fallback sem LLM")
        ollama_base = None

    # Listar todos os .mdc
    mdc_files = sorted(LOBES_DIR.rglob("*.mdc"))
    print(f"Arquivos .mdc: {len(mdc_files)}\n")

    results = []
    errors  = 0

    for i, mdc in enumerate(mdc_files, 1):
        try:
            if ollama_base:
                cat_data = categorize_lobe(mdc, ollama_base)
            else:
                text = mdc.read_text("utf-8", errors="replace")
                cat_data = {
                    "category": _fallback_category(mdc.name, text),
                    "tags": _extract_tags(mdc.name),
                    "summary": f"Lobe {mdc.stem} — fallback",
                    "priority_score": 5,
                }

            # Salvar resultado junto ao .mdc
            cat_data["file"]      = mdc.name
            cat_data["lobe_id"]   = mdc.stem
            cat_data["classified"] = datetime.now().isoformat(timespec="seconds")

            out_file = mdc.parent / f"NC-CAT-{mdc.stem}.json"
            out_file.write_text(
                json.dumps(cat_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            score_bar = "█" * int(cat_data.get("priority_score", 5))
            print(f"  [{i:02d}/{len(mdc_files)}] {mdc.name[:45]:<46} → {cat_data['category']} [{score_bar}]")
            results.append(cat_data)

            # Pequena pausa para não saturar iGPU
            if ollama_base and i % 5 == 0:
                time.sleep(0.5)

        except Exception as ex:
            print(f"  [{i:02d}] ERRO {mdc.name}: {ex}")
            errors += 1

    # Resumo
    print(f"\n{'='*60}")
    print(f"Processados: {len(results)} | Erros: {errors}")

    # Distribuição por categoria
    from collections import Counter
    dist = Counter(r["category"] for r in results)
    print("\nDistribuição por categoria:")
    for cat, cnt in sorted(dist.items(), key=lambda x: -x[1]):
        print(f"  {cnt:2d}x {cat}")

    # Salvar índice global
    index = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "model": MODEL if ollama_base else "fallback",
        "total": len(results),
        "distribution": dict(dist),
        "lobes": results,
    }
    index_path = LOBES_DIR / "NC-CAT-INDEX-001.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ Índice salvo: {index_path}")


if __name__ == "__main__":
    main()
