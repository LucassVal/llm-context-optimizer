#!/usr/bin/env python3
"""---
NC-CORE-FR-105-cascade-consolidator.py — CASC-001
"Sono REM" do NeoCortex: consolida handoffs e logs de sessão em padrões
persistidos nos lobes de memória.

Analogia neuro: Hipocampo → Córtex (consolidação de curto→longo prazo)

Fluxo:
  1. Lê arquivos recentes de handoff/audit-log
  2. Usa Qwen 1.5b para extrair padrões e insights
  3. Persiste padrões no AKL (machine_memory lobe)
  4. Atualiza KG com relações extraídas
  5. Gera NC-CASC-REPORT-{ts}.md com resumo

Trigado por:
  - GuardianDaemon (ciclo noturno)
  - MCP action cascade.run
  - Manualmente via script
---"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT    = Path(os.environ.get("NC_ROOT", "")).resolve() if os.environ.get("NC_ROOT") \
          else Path(__file__).resolve().parents[2]
FW_DIR  = ROOT / "01_neocortex_framework"
LOG_DIR = ROOT / "DIR-DS-002-audit-logs"
HND_DIR = ROOT / "DIR-DS-001-handoffs-queue"
OUT_DIR = FW_DIR / ".neocortex" / "cascade"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OLLAMA_BASE = os.environ.get("NC_OLLAMA", "http://localhost:11434")
MODEL       = "qwen2.5-coder:1.5b-instruct"

# ── LLM helper ────────────────────────────────────────────────────────────────

def _ask_qwen(prompt: str, max_tok: int = 200) -> str:
    body = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tok, "temperature": 0.15},
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read())["response"].strip()
    except Exception as e:
        logger.warning(f"[CASCADE] LLM falhou: {e}")
        return ""


# ── Leitura de fontes ─────────────────────────────────────────────────────────

def _recent_files(directory: Path, hours: int = 24, extensions=(".yaml", ".json", ".md", ".log")) -> list[Path]:
    """Arquivos modificados nas últimas N horas."""
    if not directory.exists():
        return []
    cutoff = datetime.now() - timedelta(hours=hours)
    files = []
    for f in directory.rglob("*"):
        if f.is_file() and f.suffix in extensions:
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime > cutoff:
                    files.append(f)
            except Exception:
                pass
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)


def _read_excerpt(path: Path, max_chars: int = 500) -> str:
    try:
        return path.read_text("utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


# ── Extração de padrões ───────────────────────────────────────────────────────

def _extract_pattern(content: str, source: str) -> dict[str, Any] | None:
    """Usa Qwen 1.5b para extrair padrão relevante de um trecho."""
    prompt = (
        f"Analyze this log/handoff excerpt from a software framework.\n"
        f"Source: {source}\n"
        f"Content:\n{content[:400]}\n\n"
        f"Extract ONE important pattern or lesson. Reply ONLY with JSON:\n"
        f'{{\"pattern\":\"<description>\",\"category\":\"<error|success|warning|insight>\",\"tags\":[\"t1\",\"t2\"]}}'
    )
    resp = _ask_qwen(prompt, max_tok=120)
    try:
        import re
        m = re.search(r'\{[^{}]+\}', resp, re.DOTALL)
        if m:
            data = json.loads(m.group())
            if data.get("pattern"):
                return data
    except Exception:
        pass
    return None


# ── Persistência ───────────────────────────────────────────────────────────────

def _save_to_akl(patterns: list[dict], session_id: str) -> int:
    """Persiste padrões no AKL (machine_memory lobe)."""
    try:
        import sys
        sys.path.insert(0, str(FW_DIR))
        from neocortex.core.NC_CORE_FR_103_akl_service import get_akl_service
        akl = get_akl_service()
        saved = 0
        for i, p in enumerate(patterns):
            key = f"cascade-{session_id}-{i:03d}"
            akl.add(
                key=key,
                content=p["pattern"],
                tag=f"cascade_{p.get('category','insight')}",
                session_id=session_id,
            )
            saved += 1
        return saved
    except Exception as e:
        logger.warning(f"[CASCADE] AKL save falhou: {e}")
        return 0


def _save_to_kg(patterns: list[dict]) -> int:
    """Adiciona entidades/relações ao KG."""
    try:
        from neocortex.core.NC_CORE_FR_114_kg_service import get_kg_service
        kg = get_kg_service()
        added = 0
        for p in patterns:
            cat = p.get("category", "insight")
            kg.add_entity(f"cascade:{cat}", "concept")
            for tag in p.get("tags", []):
                try:
                    kg.add_entity(tag, "concept")
                    kg.add_relation(f"cascade:{cat}", "has_tag", tag)
                    added += 1
                except Exception:
                    pass
        return added
    except Exception as e:
        logger.warning(f"[CASCADE] KG update falhou: {e}")
        return 0


# ── Report ────────────────────────────────────────────────────────────────────

def _generate_report(patterns: list[dict], sources: int, session_id: str, akl_saved: int, kg_added: int) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = OUT_DIR / f"NC-CASC-REPORT-{ts}.md"

    lines = [
        f"# NC-CASC-REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"\n**Session:** `{session_id}`",
        f"**Fontes processadas:** {sources} arquivos",
        f"**Padrões extraídos:** {len(patterns)}",
        f"**AKL salvo:** {akl_saved} | **KG entidades:** {kg_added}",
        "\n---\n\n## Padrões Consolidados\n",
    ]

    by_cat: dict[str, list] = {}
    for p in patterns:
        cat = p.get("category", "insight")
        by_cat.setdefault(cat, []).append(p)

    cat_emoji = {"error": "🔴", "warning": "🟡", "success": "🟢", "insight": "💡"}
    for cat, items in sorted(by_cat.items()):
        lines.append(f"### {cat_emoji.get(cat, '•')} {cat.title()} ({len(items)})\n")
        for item in items:
            tags = " ".join(f"`{t}`" for t in item.get("tags", []))
            lines.append(f"- {item['pattern']}  \n  {tags}\n")

    lines.append(f"\n---\n*Gerado por CASC-001 Guardian Daemon | Modelo: {MODEL}*\n")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


# ── CascadeConsolidator ────────────────────────────────────────────────────────

class CascadeConsolidator:
    """
    Coração do CASC-001: coleta, analisa e consolida conhecimento de sessão.

    Usage:
        cc = CascadeConsolidator()
        result = cc.run(hours=24)
        print(result["patterns_found"], result["report"])
    """

    def __init__(self, hours: int = 24):
        self.hours      = hours
        self.session_id = f"casc-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def run(self) -> dict[str, Any]:
        logger.info(f"[CASCADE] Iniciando consolidação | session={self.session_id} | janela={self.hours}h")

        # 1. Coletar fontes
        sources: list[Path] = []
        for d in [LOG_DIR, HND_DIR]:
            sources.extend(_recent_files(d, hours=self.hours))

        # Também pegar guardian_state e AKL
        guardian_state = FW_DIR / ".neocortex" / "guardian_state.json"
        if guardian_state.exists():
            sources.append(guardian_state)

        logger.info(f"[CASCADE] {len(sources)} fontes encontradas")

        # 2. Extrair padrões
        patterns: list[dict] = []
        processed = 0
        for src in sources[:20]:  # Limite de 20 fontes por ciclo
            excerpt = _read_excerpt(src, max_chars=400)
            if not excerpt.strip():
                continue
            pattern = _extract_pattern(excerpt, src.name)
            if pattern:
                pattern["source"] = src.name
                patterns.append(pattern)
                logger.debug(f"[CASCADE] Padrão: {pattern['pattern'][:60]}")
            processed += 1

        logger.info(f"[CASCADE] {len(patterns)} padrões extraídos de {processed} fontes processadas")

        # 3. Persistir no AKL
        akl_saved = _save_to_akl(patterns, self.session_id)

        # 4. Atualizar KG
        kg_added = _save_to_kg(patterns)

        # 5. Gerar relatório
        report_path = _generate_report(patterns, len(sources), self.session_id, akl_saved, kg_added)
        logger.info(f"[CASCADE] Relatório: {report_path}")

        result = {
            "session_id":      self.session_id,
            "sources_found":   len(sources),
            "processed":       processed,
            "patterns_found":  len(patterns),
            "akl_saved":       akl_saved,
            "kg_relations":    kg_added,
            "report":          str(report_path),
            "timestamp":       datetime.now().isoformat(timespec="seconds"),
        }
        logger.info(f"[CASCADE] Concluído: {result}")
        return result


# ── Singleton + registry ───────────────────────────────────────────────────────

_last_result: dict | None = None


def run_cascade(hours: int = 24) -> dict[str, Any]:
    global _last_result
    cc = CascadeConsolidator(hours=hours)
    _last_result = cc.run()
    return _last_result


def cascade_status() -> dict[str, Any]:
    return _last_result or {"status": "never_run", "timestamp": datetime.now().isoformat(timespec="seconds")}


# ── Standalone ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    result = run_cascade(hours=hours)
    print(json.dumps(result, ensure_ascii=False, indent=2))
