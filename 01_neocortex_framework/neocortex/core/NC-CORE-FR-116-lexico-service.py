#!/usr/bin/env python3
"""---
NC-CORE-FR-116-lexico-service.py — LEXICO-001
"Neuroplasticidade" do NeoCortex: dicionário semântico evolutivo.

Analogia neuro: Re-wiring sináptico baseado em experiência —
o sistema aprende novos termos e relações com o uso, sem intervenção manual.

Responsabilidades:
  1. Extrair termos técnicos únicos dos lobes .mdc
  2. Construir glossário com definições via Qwen 1.5b
  3. Detectar drift semântico (termos novos vs histórico)
  4. Exportar LEXICO.json para consumo por outros serviços

Storage: .neocortex/lexico/NC-LEXICO-{version}.json
---"""
from __future__ import annotations

import json
import logging
import os
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT      = Path(os.environ.get("NC_ROOT", "")).resolve() if os.environ.get("NC_ROOT") \
            else Path(__file__).resolve().parents[2]
FW_DIR    = ROOT / "01_neocortex_framework"
LEX_DIR   = FW_DIR / ".neocortex" / "lexico"
LEX_DIR.mkdir(parents=True, exist_ok=True)
LOBES_DIR = ROOT / "02_memory_lobes"

OLLAMA_BASE = os.environ.get("NC_OLLAMA", "http://localhost:11434")
MODEL       = "qwen2.5-coder:1.5b-instruct"

# Termos muito comuns a ignorar (stop-words técnicas)
STOP_TERMS = {
    "the", "and", "for", "with", "from", "that", "this", "are", "not",
    "will", "can", "may", "all", "any", "use", "used", "using", "each",
    "true", "false", "none", "null", "self", "args", "kwargs", "def",
    "class", "import", "return", "yield", "async", "await",
}


# ── LLM helper ────────────────────────────────────────────────────────────────

def _ask_qwen(prompt: str, max_tok: int = 80) -> str:
    body = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tok, "temperature": 0.1},
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())["response"].strip()
    except Exception as e:
        logger.debug(f"[LEXICO] LLM falhou: {e}")
        return ""


# ── Extração ───────────────────────────────────────────────────────────────────

def _extract_terms(text: str) -> set[str]:
    """Extrai termos técnicos candidatos de um texto."""
    # Palavras compostas NC-style: NC-TIPO-SIGLA ou camelCase
    compound = set(re.findall(r'NC-[A-Z]{2,}-[A-Z]{2,}-\d+', text))

    # Siglas (2+ maiúsculas) como MCP, AKL, KG, LLM
    acronyms = set(re.findall(r'\b[A-Z]{2,}\b', text))

    # CamelCase: CircuitBreaker, GuardianDaemon, etc.
    camel = set(re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', text))

    # Snake_case técnico (funções/variáveis de módulo)
    snake = {w for w in re.findall(r'\b[a-z][a-z_]{4,}\b', text)
                if '_' in w and w.lower() not in STOP_TERMS}

    all_terms = compound | acronyms | camel | snake
    # Filtrar stop-words e termos muito curtos
    return {t for t in all_terms if len(t) >= 3 and t.lower() not in STOP_TERMS}


def _gather_terms_from_lobes() -> dict[str, list[str]]:
    """Varre todos os .mdc e extrai termos por categoria."""
    term_sources: dict[str, list[str]] = {}  # termo → [fontes]
    for mdc in sorted(LOBES_DIR.rglob("*.mdc")):
        try:
            text = mdc.read_text("utf-8", errors="replace")
            terms = _extract_terms(text)
            for t in terms:
                term_sources.setdefault(t, [])
                if mdc.stem not in term_sources[t]:
                    term_sources[t].append(mdc.stem)
        except Exception:
            pass

    return term_sources


# ── Definições via LLM ─────────────────────────────────────────────────────────

def _define_term(term: str, contexts: list[str]) -> str:
    """Gera definição curta via Qwen 1.5b."""
    ctx = ", ".join(contexts[:3])
    prompt = (
        f"In a Python AI agent framework, define this term in ONE sentence in Portuguese:\n"
        f"Term: {term}\n"
        f"Context files: {ctx}\n"
        f"Reply with ONLY the definition (no quotes, no 'Term:', max 20 words):"
    )
    resp = _ask_qwen(prompt, max_tok=40)
    return resp if resp and len(resp) < 200 else f"Termo técnico do NeoCortex ({ctx[:50]})"


# ── Drift detection ────────────────────────────────────────────────────────────

def _detect_drift(current: dict[str, Any], previous: dict[str, Any] | None) -> dict[str, Any]:
    """Detecta termos novos, removidos e alterados entre versões."""
    if not previous:
        return {"new": list(current.keys()), "removed": [], "changed": []}

    prev_terms = set(previous.get("terms", {}).keys())
    curr_terms = set(current.keys())

    return {
        "new":     list(curr_terms - prev_terms),
        "removed": list(prev_terms - curr_terms),
        "changed": [],  # Futuro: comparar definições
        "drift_score": len(curr_terms - prev_terms) / max(len(prev_terms), 1),
    }


# ── LexicoService ─────────────────────────────────────────────────────────────

class LexicoService:
    """
    Serviço principal do LEXICO-001.

    Usage:
        lex = LexicoService()
        result = lex.build()
        print(result["total_terms"], result["lexico_path"])

        # Busca
        hits = lex.search("circuit")
    """

    def __init__(self):
        self.version  = datetime.now().strftime("%Y%m%d-%H%M%S")
        self._lexico: dict[str, Any] = {}

    def _load_previous(self) -> dict | None:
        """Carrega versão anterior do lexico (se existir)."""
        existing = sorted(LEX_DIR.glob("NC-LEXICO-*.json"))
        if not existing:
            return None
        try:
            return json.loads(existing[-1].read_text("utf-8"))
        except Exception:
            return None

    def build(self, with_definitions: bool = True, max_defs: int = 30) -> dict[str, Any]:
        """Constrói o lexico completo."""
        logger.info(f"[LEXICO] Iniciando build v{self.version}")

        # 1. Coletar termos
        term_sources = _gather_terms_from_lobes()
        logger.info(f"[LEXICO] {len(term_sources)} termos candidatos extraídos")

        # 2. Rankear por frequência (ocorre em mais lobes = mais importante)
        ranked = sorted(term_sources.items(), key=lambda x: len(x[1]), reverse=True)

        # 3. Gerar definições (limitado para economizar tokens)
        terms_dict: dict[str, Any] = {}
        previous = self._load_previous()
        prev_terms = previous.get("terms", {}) if previous else {}

        def_count = 0
        for term, sources in ranked:
            entry: dict[str, Any] = {
                "sources":   sources,
                "frequency": len(sources),
            }

            # Definição: reusar da versão anterior se termo já existe
            if term in prev_terms and prev_terms[term].get("definition"):
                entry["definition"] = prev_terms[term]["definition"]
                entry["reused"]     = True
            elif with_definitions and def_count < max_defs:
                entry["definition"] = _define_term(term, sources)
                def_count += 1
            else:
                entry["definition"] = None

            terms_dict[term] = entry

        # 4. Drift analysis
        drift = _detect_drift(terms_dict, previous)
        logger.info(f"[LEXICO] Drift: {len(drift['new'])} novos, {len(drift['removed'])} removidos "
                    f"(score={drift.get('drift_score', 0):.2f})")

        # 5. Construir lexico completo
        lexico = {
            "version":     self.version,
            "generated":   datetime.now().isoformat(timespec="seconds"),
            "model":       MODEL if with_definitions else "none",
            "total_terms": len(terms_dict),
            "terms":       terms_dict,
            "drift":       drift,
            "stats": {
                "new_terms":     len(drift["new"]),
                "removed_terms": len(drift["removed"]),
                "definitions":   sum(1 for v in terms_dict.values() if v.get("definition")),
                "top_10":        [(t, len(sources)) for t, sources in ranked[:10]],
            }
        }

        # 6. Persistir
        out_path = LEX_DIR / f"NC-LEXICO-{self.version}.json"
        out_path.write_text(json.dumps(lexico, ensure_ascii=False, indent=2), encoding="utf-8")

        # Symlink/cópia para "latest"
        latest = LEX_DIR / "NC-LEXICO-LATEST.json"
        latest.write_text(json.dumps(lexico, ensure_ascii=False, indent=2), encoding="utf-8")

        self._lexico = lexico
        logger.info(f"[LEXICO] Salvo: {out_path} | {len(terms_dict)} termos")

        return {
            "version":      self.version,
            "total_terms":  len(terms_dict),
            "new_terms":    len(drift["new"]),
            "drift_score":  drift.get("drift_score", 0),
            "definitions":  lexico["stats"]["definitions"],
            "lexico_path":  str(out_path),
            "top_10":       lexico["stats"]["top_10"],
            "timestamp":    lexico["generated"],
        }

    def search(self, query: str) -> list[dict[str, Any]]:
        """Busca termos no lexico pelo nome ou definição."""
        if not self._lexico:
            latest = LEX_DIR / "NC-LEXICO-LATEST.json"
            if latest.exists():
                self._lexico = json.loads(latest.read_text("utf-8"))
            else:
                return []
        q = query.lower()
        results = []
        for term, entry in self._lexico.get("terms", {}).items():
            score = 0
            if q in term.lower():
                score += 10
            defi = entry.get("definition", "") or ""
            if q in defi.lower():
                score += 5
            if score:
                results.append({
                    "term":       term,
                    "definition": defi,
                    "frequency":  entry.get("frequency", 0),
                    "sources":    entry.get("sources", []),
                    "score":      score,
                })
        return sorted(results, key=lambda x: (-x["score"], -x["frequency"]))[:20]

    def latest_stats(self) -> dict[str, Any]:
        latest = LEX_DIR / "NC-LEXICO-LATEST.json"
        if not latest.exists():
            return {"status": "not_built", "timestamp": datetime.now().isoformat(timespec="seconds")}
        try:
            data = json.loads(latest.read_text("utf-8"))
            return {
                "version":    data["version"],
                "total_terms":data["total_terms"],
                "drift":      data["drift"],
                "stats":      data["stats"],
                "generated":  data["generated"],
            }
        except Exception as e:
            return {"error": str(e)}


# ── Singleton ──────────────────────────────────────────────────────────────────

_service: LexicoService | None = None


def get_lexico_service() -> LexicoService:
    global _service
    if _service is None:
        _service = LexicoService()
    return _service


def run_lexico_build(with_defs: bool = True, max_defs: int = 30) -> dict[str, Any]:
    return get_lexico_service().build(with_definitions=with_defs, max_defs=max_defs)


# ── Standalone ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    max_defs = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    result = run_lexico_build(with_defs=True, max_defs=max_defs)
    print(json.dumps(result, ensure_ascii=False, indent=2))
