#!/usr/bin/env python3
"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation']
hash: "auto-generated"
---
"""

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation']
hash: "auto-generated"
---
"""

import sys

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation']
hash: "auto-generated"
---"""

"""
NC-SCR-FR-001-populate-lobes-ssot.py
Script de Povoamento Automtico de Lobos a partir dos Arquivos SSOT

L os arquivos SSOT do NeoCortex e os injeta nos lobos apropriados,
garantindo que o conhecimento fique indexado e buscvel via FTS5.

Uso:
    cd 01_neocortex_framework
    python scripts/NC-SCR-FR-001-populate-lobes-ssot.py

Ou com flag de dry-run para s visualizar o que seria feito:
    python scripts/NC-SCR-FR-001-populate-lobes-ssot.py --dry-run
"""

import argparse
import logging
import os
import subprocess
import sys
import yaml
from pathlib import Path

#  Setup do PATH para importar o pacote neocortex
SCRIPT_DIR = Path(__file__).parent.resolve()
FRAMEWORK_ROOT = SCRIPT_DIR.parent  # 01_neocortex_framework/
sys.path.insert(0, str(FRAMEWORK_ROOT))

#  Imports do NeoCortex
try:
    from neocortex.core.lobe_service import get_lobe_service
except ImportError as e:
    print(f"[ERRO] No foi possvel importar o pacote neocortex: {e}")
    print("       Certifique-se de executar de dentro de 01_neocortex_framework/ ou")
    print(f"       que PYTHONPATH aponta para {FRAMEWORK_ROOT}")
    sys.exit(1)

#  Configurao de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("populate_lobes")

#  Mapeamento SSOT  Lobo
# Cada entrada: (caminho_relativo_ao_framework, nome_do_lobo, tags)
SSOT_LOBE_MAP = [
    #  Arquitetura e Documentao  Lobo architecture
    (
        "DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md",
        "NC-LBE-FR-ARCHITECTURE-001",
        ["ssot", "roadmap", "tickets", "architecture"],
    ),
    (
        "DIR-DOC-FR-001-docs-main/NC-APP-FR-001-technical-appendix.md",
        "NC-LBE-FR-ARCHITECTURE-001",
        ["ssot", "technical", "libraries", "llm", "architecture"],
    ),
    (
        "DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md",
        "NC-LBE-FR-ARCHITECTURE-001",
        ["ssot", "naming", "ssot-map", "changelog", "architecture"],
    ),
    (
        "DIR-DOC-FR-001-docs-main/NC-ARC-FR-001-decision-log.md",
        "NC-LBE-FR-ARCHITECTURE-001",
        ["ssot", "adr", "decisions", "architecture"],
    ),
    (
        "DIR-DOC-FR-001-docs-main/NC-DOC-FR-002-directory-convention.md",
        "NC-LBE-FR-ARCHITECTURE-001",
        ["ssot", "directories", "conventions", "architecture"],
    ),
    #  MCP e Desenvolvimento  Lobo development
    (
        "DIR-DOC-FR-001-docs-main/NC-ALN-FR-001-arquitetural-alignment.md",
        "NC-LBE-FR-DEVELOPMENT-001",
        ["ssot", "alignment", "architecture", "development"],
    ),
    #  Segurana  Lobo security
    (
        "DIR-DOC-FR-001-docs-main/SANITIZATION_CHECKLIST.md",
        "NC-LBE-FR-SECURITY-001",
        ["ssot", "sanitization", "checklist", "security"],
    ),
    (
        "DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml",
        "NC-LBE-FR-SECURITY-001",
        ["ssot", "atomic-locks", "security", "policy"],
    ),
    (
        "DIR-DOC-FR-001-docs-main/NC-CFG-FR-001-agent-policy-template.yaml",
        "NC-LBE-FR-SECURITY-001",
        ["ssot", "agent-policy", "security", "limits"],
    ),
    (
        "DIR-DOC-FR-001-docs-main/NC-SOP-FR-001-session-startup.md",
        "NC-LBE-FR-SECURITY-001",
        ["ssot", "sop", "startup", "checklist", "security"],
    ),
    #  Profiles e Config  Lobo profiles
    (
        "DIR-PRF-FR-001-profiles-main/NC-PRF-FR-001-developer-schema.md",
        "NC-LBE-FR-PROFILES-001",
        ["ssot", "profile", "developer", "schema"],
    ),
    (
        "DIR-PRF-FR-001-profiles-main/NC-PRF-FR-002-team-schema.md",
        "NC-LBE-FR-PROFILES-001",
        ["ssot", "profile", "team", "schema"],
    ),
    #  White Label  Lobo whitelabel
    (
        "../03_white_label_templates/NC-DOC-WL-001-readme.md",
        "NC-LBE-FR-WHITELABEL-001",
        ["ssot", "whitelabel", "readme", "templates"],
    ),
    (
        "../03_white_label_templates/NC-DOC-WL-001-hybrid-mode.md",
        "NC-LBE-FR-WHITELABEL-001",
        ["ssot", "whitelabel", "hybrid-mode"],
    ),
    #  Checklist Pr-MCP  Lobo development
    (
        "../NC-PROMPT-FR-002-pre-mcp-manual-checklist.md",
        "NC-LBE-FR-DEVELOPMENT-001",
        ["ssot", "checklist", "pre-mcp", "governance", "session"],
    ),
    #  Plano de Refatorao 10 Tools  Lobo architecture
    (
        "DIR-DOC-FR-001-docs-main/NC-MAN-FR-001-project-manifest.md",
        "NC-LBE-FR-ARCHITECTURE-001",
        ["ssot", "manifest", "tools", "architecture", "refactoring"],
    ),
    #  Manifesto de Projeto (tool map, bootcontext)  Lobo mcp
    (
        "DIR-DOC-FR-001-docs-main/NC-MAN-FR-001-project-manifest.md",
        "NC-LBE-FR-MCP-001",
        ["ssot", "manifest", "mcp", "tools", "boot-context", "system-profile"],
    ),
    #  Benchmarks  Lobo benchmarks
    (
        "DIR-DOC-FR-001-docs-main/BENCHMARKS.md",
        "NC-LBE-FR-BENCHMARKS-001",
        ["ssot", "benchmarks", "performance"],
    ),
    (
        "DIR-DOC-FR-001-docs-main/BENCHMARKS_HYBRID.md",
        "NC-LBE-FR-BENCHMARKS-001",
        ["ssot", "benchmarks", "hybrid", "llm"],
    ),
    #  Claude Code Leak Analysis  Lobos CC
    (
        "../DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-LBE-CC-002-memory-arch.mdc",
        "NC-LBE-CC-002-memory-arch.mdc",
        ["claude-code", "memory", "architecture", "leak", "analysis"],
    ),
    (
        "../DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-LBE-CC-003-orchestration.mdc",
        "NC-LBE-CC-003-orchestration.mdc",
        ["claude-code", "orchestration", "coordinator", "leak", "analysis"],
    ),
    #  DeepSeek Agents (DSA a DSD)  Lobos DS
    (
        "DIR-TMP-FR-001-templates-main/NC-LBE-DS-001-deepseek-agent.mdc",
        "NC-LBE-DS-001-deepseek-agent.mdc",
        ["deepseek", "agent", "t1", "ds-a", "executor"],
    ),
    (
        "DIR-TMP-FR-001-templates-main/NC-LBE-DS-002-deepseek-agent-b.mdc",
        "NC-LBE-DS-002-deepseek-agent-b.mdc",
        ["deepseek", "agent", "t1", "ds-b", "research"],
    ),
    (
        "DIR-TMP-FR-001-templates-main/NC-LBE-DS-003-deepseek-agent-c.mdc",
        "NC-LBE-DS-003-deepseek-agent-c.mdc",
        ["deepseek", "agent", "t1", "ds-c", "development"],
    ),
    (
        "DIR-TMP-FR-001-templates-main/NC-LBE-DS-004-deepseek-agent-d.mdc",
        "NC-LBE-DS-004-deepseek-agent-d.mdc",
        ["deepseek", "agent", "t1", "ds-d", "observability"],
    ),

    # ══════════════════════════════════════════════════════════
    #  REGIÕES CEREBRAIS v2.0 (2026-04-20)
    #  Nomes: NC-LBE-CEREBRAL-{REGION}-001 (sem / para LobeService)
    # ══════════════════════════════════════════════════════════

    # $FRONTAL — Planejamento e Governança
    (
        "DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md",
        "NC-LBE-CEREBRAL-FRONTAL-001",
        ["frontal", "roadmap", "planejamento", "governanca", "tickets"],
    ),
    (
        "DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md",
        "NC-LBE-CEREBRAL-FRONTAL-001",
        ["frontal", "ssot", "naming", "governance"],
    ),
    (
        "../02_memory_lobes/06_governance/NC-LBE-FR-TICKETS-001.mdc",
        "NC-LBE-FR-TICKETS-001.mdc",
        ["frontal", "governance", "tickets", "ssot", "validator", "rules"],
    ),

    # $TEMPORAL — Memória Semântica (Léxico + KG + ULQ)
    (
        "DIR-DOC-FR-001-docs-main/NC-DOC-FR-001-ubiquitous-language-dictionary.md",
        "NC-LBE-CEREBRAL-TEMPORAL-001",
        ["temporal", "ulq", "lexico", "semantico", "linguagem-ubiqua"],
    ),

    # $PARIETAL — Integração (MCP, Profiles, Health)
    (
        "DIR-DOC-FR-001-docs-main/NC-ALN-FR-001-arquitetural-alignment.md",
        "NC-LBE-CEREBRAL-PARIETAL-001",
        ["parietal", "mcp", "integracao", "alinhamento", "health"],
    ),
    (
        "DIR-PRF-FR-001-profiles-main/NC-PRF-FR-001-developer-schema.md",
        "NC-LBE-CEREBRAL-PARIETAL-001",
        ["parietal", "profile", "developer", "schema"],
    ),

    # $OCCIPITAL — Padrões Estruturais (Naming, Manifests, Architecture)
    (
        "DIR-DOC-FR-001-docs-main/NC-ARC-FR-001-decision-log.md",
        "NC-LBE-CEREBRAL-OCCIPITAL-001",
        ["occipital", "adr", "decisoes", "arquitetura", "patterns"],
    ),
    (
        "DIR-DOC-FR-001-docs-main/NC-APP-FR-001-technical-appendix.md",
        "NC-LBE-CEREBRAL-OCCIPITAL-001",
        ["occipital", "technical", "libraries", "llm", "patterns"],
    ),

    # $CEREBELO — Controle Motor Automático (Guardian, Benchmark)
    (
        "DIR-DOC-FR-001-docs-main/BENCHMARKS.md",
        "NC-LBE-CEREBRAL-CEREBELO-001",
        ["cerebelo", "benchmark", "automacao", "guardian", "ciclos"],
    ),
    (
        "DIR-DOC-FR-001-docs-main/BENCHMARKS_HYBRID.md",
        "NC-LBE-CEREBRAL-CEREBELO-001",
        ["cerebelo", "benchmark", "hybrid", "llm", "automacao"],
    ),

    # $HIPOCAMPO — Memória Episódica (Sessões, Savepoints, SOP)
    (
        "DIR-DOC-FR-001-docs-main/NC-SOP-FR-001-session-startup.md",
        "NC-LBE-CEREBRAL-HIPOCAMPO-001",
        ["hipocampo", "sop", "startup", "checklist", "episodico"],
    ),
    (
        "DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml",
        "NC-LBE-CEREBRAL-HIPOCAMPO-001",
        ["hipocampo", "locks", "security", "savepoint"],
    ),
]


def load_index_yaml() -> dict:
    """Carrega o _INDEX.yaml se existir."""
    index_path = FRAMEWORK_ROOT.parent / "02_memory_lobes" / "_INDEX.yaml"
    if not index_path.exists():
        return {}
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return {item["filename"]: item for item in data.get("lobes", [])}
    except Exception as e:
        log.error(f"Erro ao ler _INDEX.yaml: {e}")
        return {}


def create_junction(target_path: Path, link_path: Path, dry_run: bool = False):
    """Cria um directory junction no Windows, removendo se j existir como dir normal."""
    if not target_path.exists():
        target_path.mkdir(parents=True, exist_ok=True)

    if link_path.exists() or link_path.is_symlink():
        # Verificar se  um junction/symlink real
        is_junction = False
        if sys.platform == "win32":
            try:
                res = subprocess.run(
                    ["cmd", "/c", "fsutil", "reparsepoint", "query", str(link_path)],
                    capture_output=True,
                )
                if res.returncode == 0:
                    is_junction = True
            except Exception:
                pass
        else:
            if link_path.is_symlink():
                is_junction = True

        if is_junction:
            return

        # Se chegou aqui, existe mas NO  junction -> remover
        log.info(
            f"   [JUNCTION] Removendo diretrio normal para criar link: {link_path.name}"
        )
        if not dry_run:
            import shutil

            try:
                shutil.rmtree(link_path)
            except Exception as e:
                log.error(f"      Erro ao remover dir normal: {e}")
                return

    log.info(f"   [JUNCTION] Criando link {link_path.name} -> {target_path.name}")
    if dry_run:
        return

    try:
        if sys.platform == "win32":
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link_path), str(target_path)],
                check=True,
                capture_output=True,
            )
        else:
            os.symlink(target_path, link_path, target_is_directory=True)
    except Exception as e:
        log.error(f"   Falha ao criar junction: {e}")


def build_lobe_content(
    lobe_name: str, file_path: Path, raw_content: str, tags: list, capabilities: list = None
) -> str:
    """
    Monta o contedo do lobo em formato MDC com header e metadados.
    """
    tag_str = ", ".join(tags)
    header = (
        f"<!-- source: {file_path.name} -->\n"
        f"<!-- tags: {tag_str} -->\n"
    )
    if capabilities:
        header += f"<!-- deepseek_capabilities: {', '.join(capabilities)} -->\n"
    
    header += f"<!-- auto-generated: true -->\n\n"
    return header + raw_content


def populate_lobes(dry_run: bool = False):
    """
    Iterage sobre o mapeamento SSOTLobo e injeta o contedo nos lobos.
    """
    svc = get_lobe_service()

    # Acumulador: lobo_name  contedo completo concatenado
    lobe_contents: dict[str, dict] = {}

    log.info("" * 60)
    log.info("  NeoCortex  Povoamento de Lobos via SSOT")
    log.info("" * 60)
    log.info(f"  Framework Root: {FRAMEWORK_ROOT}")
    log.info(f"  Dry-run: {'SIM (nada ser gravado)' if dry_run else 'NO (gravando)'}")
    log.info("" * 60)

    # Carregar Index YAML para capacidades e junctions
    index_map = load_index_yaml()
    lobes_root = FRAMEWORK_ROOT.parent / "02_memory_lobes"

    for rel_path, lobe_name, tags in SSOT_LOBE_MAP:
        file_path = (FRAMEWORK_ROOT / rel_path).resolve()

        # Verificar se arquivo existe
        if not file_path.exists():
            log.warning(f"    ARQUIVO NO ENCONTRADO (pulando): {file_path.name}")
            continue

        # Ler contedo
        try:
            raw = file_path.read_text(encoding="utf-8")
        except Exception as e:
            log.error(f"   Erro ao ler {file_path.name}: {e}")
            continue

        # Validar via Index
        lobe_key = lobe_name if lobe_name.endswith(".mdc") else f"{lobe_name}.mdc"
        info = index_map.get(lobe_key, {})
        capabilities = info.get("deepseek_capabilities", [])

        # Acumular por lobo
        section = build_lobe_content(lobe_name, file_path, raw, tags, capabilities)

        if lobe_name not in lobe_contents:
            lobe_contents[lobe_name] = {
                "header": f"# {lobe_name}\n\n> Lobo SSOT auto-gerado pelo script populate_lobes_from_ssot. No edite manualmente.\n\n",
                "sections": [],
                "files": [],
                "info": info,
            }

        lobe_contents[lobe_name]["sections"].append(section)
        lobe_contents[lobe_name]["files"].append(file_path.name)
        log.info(f"   Lendo {file_path.name}  {lobe_name}")

        # Se tiver info de junction no index, preparar para criar
        if info:
            target_dir = lobes_root / info["domain_dir"]
            link_dir = lobes_root / info["brain_tag"].lower() # e.g. $frontal -> $frontal/
            create_junction(target_dir, link_dir, dry_run=dry_run)

    log.info("" * 60)

    #  Gravar / atualizar cada lobo
    results = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

    for lobe_name, data in lobe_contents.items():
        # Montar contedo final com separador entre arquivos
        separator = "\n\n---\n\n"
        full_content = data["header"] + separator.join(data["sections"])

        files_str = ", ".join(data["files"])
        log.info(f"   Processando lobo: {lobe_name}")
        log.info(f"     Arquivos: {files_str}")
        log.info(f"     Tamanho: {len(full_content):,} chars")

        if dry_run:
            log.info(f"   [DRY-RUN] Lobo '{lobe_name}' seria criado/atualizado.")
            results["skipped"] += 1
            continue

        # Verificar se lobo exists (MDC extension)
        lobe_file = f"{lobe_name}.mdc" if not lobe_name.endswith(".mdc") else lobe_name

        if svc.repository.lobe_exists(lobe_file):
            result = svc.update_lobe(lobe_file, full_content)
            verb = "atualizado"
            results["updated"] += 1
        else:
            result = svc.create_lobe(lobe_name, full_content)
            verb = "criado"
            results["created"] += 1

        if result.get("success"):
            log.info(f"   Lobo '{lobe_name}' {verb} com sucesso!")
            # Ativar o lobo no ledger
            try:
                svc.activate_lobe(lobe_file)
                log.info("      Lobo ativado no ledger.")
            except Exception as e:
                log.warning(f"       Falha ao ativar no ledger: {e}")
        else:
            log.error(
                f"   Falha ao {verb[:-1]}r lobo '{lobe_name}': {result.get('error')}"
            )
            results["errors"] += 1

    #  Resumo final
    log.info("" * 60)
    log.info("  RESUMO")
    log.info(f"   Criados:     {results['created']}")
    log.info(f"   Atualizados: {results['updated']}")
    log.info(f"    Pulados:     {results['skipped']}")
    log.info(f"   Erros:       {results['errors']}")
    log.info("" * 60)

    if results["errors"] == 0:
        log.info("   Conhecimento SSOT indexado com sucesso nos lobos!")
        log.info("  Use neocortex_search para buscar contedo nos lobos agora.")
    else:
        log.warning(
            f"    {results['errors']} erro(s) ocorreram. Verifique os logs acima."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Povoa os lobos NeoCortex com o contedo dos arquivos SSOT."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Exibe o que seria feito sem gravar nada.",
    )
    args = parser.parse_args()
    populate_lobes(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
