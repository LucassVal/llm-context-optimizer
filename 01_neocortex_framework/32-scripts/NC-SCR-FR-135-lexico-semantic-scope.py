# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3
"""---
NC-SCR-FR-135-lexico-semantic-scope.py — LEXICO-002
---
"""

"""---
NC-SCR-FR-135-lexico-semantic-scope.py — LEXICO-002
---
"""

"""
NC-SCR-FR-135-lexico-semantic-scope.py — LEXICO-002

Adiciona o campo `semantic_scope` a cada termo do NC-LEXICO-LATEST.json,
classificando cada termo na sua região cerebral:
  $frontal   → planejamento, governança, roadmap, tickets
  $temporal  → léxico, semantica, linguagem, KG, AKL, NLP
  $parietal  → MCP, integração, API, health, profiles, ferramentas
  $occipital → naming, patterns, manifests, ADR, estrutura, código
  $cerebelo  → Guardian, daemon, ciclos, automação, benchmark, deployment
  $hipocampo → sessão, savepoint, handoff, histórico, audit, rollback

Estratégia:
  1. Classifica por keywords presentes no termo + definição + fontes
  2. Para termos ambíguos → usa Qwen 1.5b (LLM local)
  3. Salva LEXICO atualizado + relatório de cobertura
"""
import json
import os
import urllib.request
from collections import defaultdict
from pathlib import Path

FW      = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
LEX_DIR = FW / ".neocortex" / "lexico"
LEX_IN  = LEX_DIR / "NC-LEXICO-LATEST.json"
OLLAMA  = os.environ.get("NC_OLLAMA", "http://localhost:11434")
MODEL   = "qwen2.5-coder:1.5b-instruct"

# ── Dicionário de keywords por região ──────────────────────────────────────
# REGRA: keywords devem ser substrings únicas — evitar palavras que aparecem
# em outros contextos (ex: "term" aparece em "terminal", "determine", etc.)
REGION_KEYWORDS: dict[str, list[str]] = {
    "$frontal": [
        "roadmap", "ticket", "governance", "governan", "compliance",
        "policy", "polici", "rule", "audit", "atomic lock",
        "naming convention", "todo", "sprint", "milestone", "priority",
        "decision log", "adr ", "okr", "kpi", "strategic",
    ],
    "$temporal": [
        # Léxico e semântica — muito específicos
        "lexico", "lexic", "lexical", "glossar",
        "semantic_scope", "semantic scope", "neuroplastic",
        "ubiquitous language", "ubiquitous-language",
        "knowledge graph", "kg_service", "kgservice",
        "akl_service", "akl service", "adaptive knowledge",
        "nlp ", " nlp", "natural language",
        "linguistic", "vocabular",
        "ontolog", "embedding", "vector store",
        "context window", "token budget", "similarity search",
        "corpus", "tokeniz", "langchain", "llm context",
        "lexico_service", "lexicoservice",
    ],
    "$parietal": [
        "mcp tool", "fastmcp", " api ", "api_key", "api key",
        "endpoint", " health", "profile",
        "picoclaw", "opencode", "antigravity",
        "mission control", "pixel agent",
        "plugin", "extension", ".sdk", "sub_server",
        "http request", "rest api", "webhook",
        "nc-super", "nc_super", "super tool",
        "mcp server", "mcp client", "tool_call",
        "register_tool", "tool_module", "fastmcp",
    ],
    "$occipital": [
        "naming pattern", "naming convention", "nc-nam",
        "manifest", "template", "cc_pattern", "cc-pattern",
        "workflow pattern", "pipeline pattern",
        "struct", "design pattern", "schema design",
        "architecture pattern", "architect pattern",
        "format standard", "file format", "data format",
        "code pattern", "implementation pattern",
    ],
    "$cerebelo": [
        "guardian", "daemon", "ciclo ", " cycle", "cron job",
        "scheduled", "pulse_scheduler", "automati",
        "benchmark", "deploy", "bootup", "startup sync",
        "smoke test", "worker pattern", "batch job",
        "consolidat", "cascade_consolidator", "cascadeconsolidator",
        "guardian_state", "ciclo3", "ciclo4",
        "lobe.populate", "catalog.refresh",
    ],
    "$hipocampo": [
        "session ", "sessao", "savepoint", "rollback", "checkpoint",
        "handoff", " audit log", "history log", "episod",
        "snapshot", "backup", "archive", "ledger_service",
        "ledgerservice", "journa", " record", "handoff.yaml",
        "session_id", "session mate", "ttl session",
        "session startup",
    ],
}

# Mapa de prioridade para desempate — regiões mais "raras" têm prioridade
REGION_PRIORITY = {
    "$temporal": 6,    # mais raro → mais prioridade no empate
    "$hipocampo": 5,
    "$cerebelo": 4,
    "$occipital": 3,
    "$frontal": 2,
    "$parietal": 1,    # mais comum → menor prioridade no empate
}


def classify_term(term: str, definition: str, sources: list[str]) -> str:
    """Classifica o termo na região cerebral por keyword matching com desempate por REGION_PRIORITY."""
    text = ((term or "") + " " + (definition or "") + " " + " ".join(sources or [])).lower()
    scores: dict[str, int] = defaultdict(int)
    for region, keywords in REGION_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[region] += 1
    if not scores:
        return "$temporal"  # default: semântico
    # Em caso de empate, usar REGION_PRIORITY (regiões raras ganham)
    max_score = max(scores.values())
    candidates = [r for r, s in scores.items() if s == max_score]
    return max(candidates, key=lambda r: REGION_PRIORITY.get(r, 0))

def classify_via_llm(term: str, definition: str) -> str:
    """Fallback: Qwen 1.5b para termos sem keyword clara."""
    regions = list(REGION_KEYWORDS.keys())
    prompt = (
        f"Classify this technical term into ONE region:\n"
        f"Term: {term}\nDefinition: {definition[:100]}\n"
        f"Regions: {', '.join(regions)}\n"
        f"Answer with ONLY the region name (e.g. $temporal):"
    )
    try:
        body = json.dumps({
            "model": MODEL, "prompt": prompt, "stream": False,
            "options": {"num_predict": 15, "temperature": 0.0},
        }).encode()
        req = urllib.request.Request(
            f"{OLLAMA}/api/generate", data=body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            ans = json.loads(r.read())["response"].strip().lower()
        for reg in regions:
            if reg.lstrip("$") in ans:
                return reg
    except Exception:
        pass
    return "$temporal"

def main():
    print("\nLEXICO-002 — semantic_scope classifier")
    print(f"Lendo {LEX_IN}...")
    data = json.loads(LEX_IN.read_text("utf-8"))
    terms: dict = data.get("terms", {})
    print(f"Termos: {len(terms)}")

    region_count: dict[str, int] = defaultdict(int)
    llm_used = 0
    keyword_used = 0
    # Verificar se Ollama está disponível
    ollama_ok = False
    try:
        urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=2)
        ollama_ok = True
        print(f"Ollama: disponível ({OLLAMA}) — usará LLM para ambíguos")
    except Exception:
        print("Ollama: OFFLINE — classificação apenas por keywords")

    for term, entry in terms.items():
        definition = entry.get("definition", "") or ""
        sources    = entry.get("sources", []) or []
        # Sempre re-classificar (reset forçado para aplicar novos keywords)
        entry.pop("semantic_scope", None)

        scope = classify_term(term, definition, sources)

        # Se score 0, tentar LLM
        text2 = ((term or "") + " " + (definition or "") + " " + " ".join(sources or [])).lower()
        has_keyword = any(kw in text2 for kws in REGION_KEYWORDS.values() for kw in kws)
        if not has_keyword and ollama_ok:
            scope = classify_via_llm(term, definition or "")
            llm_used += 1
        else:
            keyword_used += 1

        entry["semantic_scope"] = scope
        region_count[scope] += 1

    # Salvar lexico atualizado
    data["terms"] = terms
    data["semantic_scope_version"] = "LEXICO-002"
    LEX_IN.write_text(json.dumps(data, indent=2, ensure_ascii=False), "utf-8")

    # Salvar symlink latest
    latest = LEX_DIR / "NC-LEXICO-LATEST.json"
    print(f"\nSalvo: {latest}")

    # Relatório
    print(f"\n{'='*50}")
    print("LEXICO-002 — Relatório de Cobertura")
    print(f"{'='*50}")
    total = len(terms)
    for region in sorted(REGION_KEYWORDS.keys()):
        count = region_count.get(region, 0)
        pct   = count * 100 // max(total, 1)
        bar   = "█" * (pct // 5) + "░" * (20 - pct // 5)
        print(f"  {region:15} {bar} {count:4d} termos ({pct}%)")
    print(f"\n  Total: {total} termos")
    print(f"  Keyword: {keyword_used} | LLM: {llm_used}")

    # Salvar relatório JSON
    report = {
        "total_terms": total, "keyword_classified": keyword_used,
        "llm_classified": llm_used, "region_distribution": dict(region_count),
        "version": "LEXICO-002",
    }
    rpt = LEX_DIR / "nc_lexico_scope_report.json"
    rpt.write_text(json.dumps(report, indent=2, ensure_ascii=False), "utf-8")
    print(f"  Relatório: {rpt}")

if __name__ == "__main__":
    main()
