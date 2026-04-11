#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Povoamento exaustivo dos Lobos do NeoCortex com conteúdo específico do projeto.
Analisa a estrutura do projeto e preenche cada Lobo com informações relevantes.
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from neocortex.core import (
    get_init_service,
    get_lobe_service,
    get_kg_service,
    get_checkpoint_service,
    get_manifest_service,
)

PROJECT_ROOT = Path(__file__).parent.parent


def analyze_project_structure():
    """Analisa a estrutura do projeto usando o serviço init."""
    print("Analisando estrutura do projeto...")
    init_service = get_init_service()
    result = init_service.scan_project()

    if not result.get("success"):
        print(f"Erro na análise: {result.get('error', 'Unknown')}")
        return {}

    return result


def get_lobe_mapping():
    """Retorna mapeamento de Lobos para módulos/áreas do projeto."""
    return {
        "NC-LBE-FR-ARCHITECTURE-001.mdc": {
            "module": "architecture",
            "description": "Arquitetura do framework, padrões, componentes",
            "target_dirs": ["neocortex_framework/", "neocortex/"],
            "target_files": ["**/*.py"],
            "analysis_focus": [
                "imports",
                "classes",
                "functions",
                "directory_structure",
            ],
        },
        "NC-LBE-FR-DEVELOPMENT-001.mdc": {
            "module": "development",
            "description": "Práticas de desenvolvimento, código fonte, convenções",
            "target_dirs": [
                "neocortex_framework/neocortex/",
                "neocortex_framework/DIR-SRC-FR-001-source-main/",
            ],
            "target_files": ["**/*.py", "**/*.md"],
            "analysis_focus": ["code_style", "conventions", "development_workflow"],
        },
        "NC-LBE-FR-TESTING-001.mdc": {
            "module": "testing",
            "description": "Testes, qualidade, cobertura",
            "target_dirs": [
                "neocortex_framework/tests/",
                "neocortex_framework/neocortex/tests/",
            ],
            "target_files": ["**/test_*.py", "**/*_test.py"],
            "analysis_focus": ["test_cases", "coverage", "testing_patterns"],
        },
        "NC-LBE-FR-CLI-001.mdc": {
            "module": "cli",
            "description": "Interface de linha de comando",
            "target_dirs": ["neocortex_framework/neocortex/cli/"],
            "target_files": ["**/cli.py", "**/cli/**/*.py"],
            "analysis_focus": ["commands", "arguments", "cli_structure"],
        },
        "NC-LBE-FR-WHITELABEL-001.mdc": {
            "module": "white_label",
            "description": "Template de white label",
            "target_dirs": ["white_label/"],
            "target_files": ["**/*.py", "**/*.md", "**/*.json"],
            "analysis_focus": ["templates", "configuration", "customization"],
        },
        "NC-LBE-FR-KNOWLEDGE-001.mdc": {
            "module": "knowledge",
            "description": "Conhecimento geral, graph, relações",
            "target_dirs": ["neocortex_framework/DIR-CORE-FR-001-core-central/"],
            "target_files": ["**/*.mdc", "**/*.json"],
            "analysis_focus": ["knowledge_graph", "relationships", "metadata"],
        },
        "NC-LBE-FR-SECURITY-001.mdc": {
            "module": "security",
            "description": "Segurança, autenticação, permissões",
            "target_dirs": ["neocortex_framework/neocortex/security/"],
            "target_files": ["**/security.py", "**/*_security.py"],
            "analysis_focus": ["security_measures", "authentication", "encryption"],
        },
        "NC-LBE-FR-DEPLOYMENT-001.mdc": {
            "module": "deployment",
            "description": "Deploy, CI/CD, infraestrutura",
            "target_dirs": [],
            "target_files": [
                "**/Dockerfile",
                "**/docker-compose*.yml",
                "**/.github/**/*.yml",
            ],
            "analysis_focus": ["deployment_config", "ci_cd", "infrastructure"],
        },
        "NC-LBE-FR-DOCUMENTATION-001.mdc": {
            "module": "documentation",
            "description": "Documentação, guias, referências",
            "target_dirs": ["neocortex_framework/DIR-DOC-FR-001-docs-main/"],
            "target_files": ["**/*.md", "**/*.rst", "**/*.txt"],
            "analysis_focus": ["documentation_structure", "guides", "references"],
        },
        "NC-LBE-FR-INTEGRATION-001.mdc": {
            "module": "integration",
            "description": "Integração com outros sistemas",
            "target_dirs": ["neocortex_framework/neocortex/mcp/"],
            "target_files": ["**/mcp/*.py", "**/integration/*.py"],
            "analysis_focus": ["integrations", "apis", "protocols"],
        },
        "NC-LBE-FR-MONITORING-001.mdc": {
            "module": "monitoring",
            "description": "Monitoramento, logs, métricas",
            "target_dirs": ["neocortex_framework/neocortex/core/"],
            "target_files": ["**/pulse_scheduler.py", "**/monitoring.py"],
            "analysis_focus": ["monitoring_tools", "logs", "metrics"],
        },
        "NC-LBE-FR-PERFORMANCE-001.mdc": {
            "module": "performance",
            "description": "Performance, benchmarks, otimização",
            "target_dirs": ["neocortex_framework/benchmarks/"],
            "target_files": ["**/benchmark*.py", "**/performance*.py"],
            "analysis_focus": ["benchmarks", "performance_metrics", "optimization"],
        },
        "NC-LBE-FR-LEGACY-001.mdc": {
            "module": "legacy",
            "description": "Arquivos legados, archive",
            "target_dirs": [
                "neocortex_framework/DIR-ARC-FR-001-archive-main/",
                "backup_root/",
            ],
            "target_files": ["**/*.py", "**/*.md"],
            "analysis_focus": ["legacy_files", "archive_structure", "migration_info"],
        },
        "NC-LBE-FR-CORE-001.mdc": {
            "module": "core",
            "description": "Núcleo do framework",
            "target_dirs": ["neocortex_framework/neocortex/core/"],
            "target_files": ["**/core/*.py"],
            "analysis_focus": ["core_components", "foundation", "essential_services"],
        },
        "NC-LBE-FR-MCP-001.mdc": {
            "module": "mcp",
            "description": "Model Context Protocol",
            "target_dirs": ["neocortex_framework/neocortex/mcp/"],
            "target_files": ["**/mcp/*.py", "**/server.py"],
            "analysis_focus": [
                "mcp_tools",
                "server_implementation",
                "protocol_details",
            ],
        },
        "NC-LBE-FR-BENCHMARKS-001.mdc": {
            "module": "benchmarks",
            "description": "Benchmarks, testes de performance",
            "target_dirs": ["neocortex_framework/benchmarks/"],
            "target_files": ["**/benchmark*.py"],
            "analysis_focus": ["benchmark_results", "performance_tests", "metrics"],
        },
        "NC-LBE-FR-PROFILES-001.mdc": {
            "module": "profiles",
            "description": "Perfis de configuração",
            "target_dirs": ["neocortex_framework/DIR-PRF-FR-001-profiles-main/"],
            "target_files": ["**/*.json", "**/*.yaml", "**/*.yml"],
            "analysis_focus": [
                "profiles_structure",
                "configuration_profiles",
                "settings",
            ],
        },
        "NC-LBE-FR-PULSE-001.mdc": {
            "module": "pulse",
            "description": "Pulse Scheduler, execução periódica",
            "target_dirs": ["neocortex_framework/neocortex/core/"],
            "target_files": ["**/pulse_scheduler.py"],
            "analysis_focus": ["scheduling", "periodic_tasks", "automation"],
        },
    }


def analyze_directory(dir_path, pattern="**/*.py"):
    """Analisa um diretório específico e retorna informações."""
    path = (
        PROJECT_ROOT / dir_path if not Path(dir_path).is_absolute() else Path(dir_path)
    )
    if not path.exists():
        return {"exists": False, "files": []}

    files = []
    for file_path in path.glob(pattern):
        if file_path.is_file():
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                stats = file_path.stat()
                # Caminho relativo ao projeto raiz
                rel_path = file_path.relative_to(PROJECT_ROOT)
                files.append(
                    {
                        "path": str(rel_path),
                        "size": stats.st_size,
                        "lines": len(content.splitlines()),
                        "ext": file_path.suffix,
                    }
                )
            except Exception as e:
                files.append(
                    {
                        "path": str(file_path),
                        "error": str(e),
                    }
                )

    return {"exists": True, "files": files, "total_files": len(files)}


def extract_python_info(file_path):
    """Extrai informações básicas de um arquivo Python."""
    try:
        # file_path é relativo ao PROJECT_ROOT
        abs_path = (
            PROJECT_ROOT / file_path
            if not Path(file_path).is_absolute()
            else Path(file_path)
        )
        content = abs_path.read_text(encoding="utf-8", errors="ignore")

        # Contar classes
        classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)

        # Contar funções
        functions = re.findall(r"^def\s+(\w+)", content, re.MULTILINE)

        # Encontrar imports
        imports = re.findall(r"^import\s+(\w+)", content, re.MULTILINE)
        imports_from = re.findall(r"^from\s+(\w+)", content, re.MULTILINE)

        return {
            "classes": classes,
            "functions": functions,
            "imports": list(set(imports + imports_from)),
            "total_lines": len(content.splitlines()),
        }
    except Exception as e:
        return {"error": str(e)}


def generate_lobe_content(lobe_name, mapping, project_analysis, dir_analysis):
    """Gera conteúdo específico para um Lobo baseado na análise."""
    module = mapping["module"]
    description = mapping["description"]

    content = f"# {lobe_name.replace('.mdc', '')}\n\n"
    content += f"{description}\n\n"

    content += "## Status\nAtivo (povoado automaticamente)\n\n"

    content += "## Tags\n"
    content += f"#{module}, #framework, #neocortex, #auto_populated\n\n"

    content += "## Checkpoints\n"
    content += f"- CP-{module.upper()}-001: Criação inicial\n"
    content += f"- CP-{module.upper()}-002: Povoamento automático\n\n"

    # Adicionar análise de diretório
    if dir_analysis.get("exists"):
        content += f"## Análise do Diretório\n"
        content += f"- **Total de arquivos**: {dir_analysis['total_files']}\n"

        if dir_analysis["files"]:
            content += "\n### Arquivos Principais\n"
            for file in dir_analysis["files"][:10]:  # Limitar a 10 arquivos
                if "error" not in file:
                    content += f"- `{file['path']}` ({file['lines']} linhas, {file['size']} bytes)\n"

        # Analisar alguns arquivos Python
        python_files = [
            f
            for f in dir_analysis["files"]
            if f.get("ext") == ".py" and "error" not in f
        ]
        if python_files:
            content += "\n### Análise de Código Python\n"
            for file in python_files[:5]:  # Analisar até 5 arquivos
                py_info = extract_python_info(file["path"])
                if "error" not in py_info:
                    content += f"\n#### `{file['path']}`\n"
                    content += f"- **Classes**: {len(py_info['classes'])}\n"
                    if py_info["classes"]:
                        content += f"  - {', '.join(py_info['classes'][:5])}\n"
                    content += f"- **Funções**: {len(py_info['functions'])}\n"
                    if py_info["functions"]:
                        content += f"  - {', '.join(py_info['functions'][:5])}\n"
                    content += f"- **Imports**: {len(py_info['imports'])}\n"
                    if py_info["imports"]:
                        content += f"  - {', '.join(py_info['imports'][:10])}\n"

    # Adicionar informações do projeto
    if project_analysis:
        content += "\n## Contexto do Projeto\n"
        content += (
            f"- **Nome do projeto**: {project_analysis.get('project_name', 'N/A')}\n"
        )
        content += f"- **Total de arquivos no projeto**: {len(project_analysis.get('files', []))}\n"

    content += "\n## Notas de Povoamento\n"
    content += f"- Povoado automaticamente por OpenCode\n"
    content += f"- Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"- Foco da análise: {', '.join(mapping.get('analysis_focus', []))}\n"

    return content


def update_lobe_with_content(lobe_name, new_content):
    """Atualiza um Lobo existente com novo conteúdo."""
    lobe_service = get_lobe_service()

    # Obter conteúdo atual
    lobe_info = lobe_service.get_lobe(lobe_name)
    if not lobe_info.get("exists"):
        print(f"  [ERROR] Lobe '{lobe_name}' não encontrado")
        return False

    # Combinar conteúdo atual com novo (adicionar seção de análise)
    current_content = lobe_info["content"]

    # Verificar se já existe seção de análise
    if "## Análise do Diretório" in current_content:
        # Substituir seção existente
        lines = current_content.split("\n")
        new_lines = []
        in_analysis_section = False
        for line in lines:
            if line.startswith("## Análise do Diretório"):
                in_analysis_section = True
                new_lines.append("## Análise do Diretório (atualizada)")
            elif in_analysis_section and line.startswith("## "):
                in_analysis_section = False
                new_lines.append(line)
            elif not in_analysis_section:
                new_lines.append(line)

        # Adicionar nova análise no final
        updated_content = "\n".join(new_lines)
        # Extrair apenas a seção de análise do novo conteúdo
        analysis_start = new_content.find("## Análise do Diretório")
        if analysis_start != -1:
            analysis_section = new_content[analysis_start:]
            # Inserir antes da primeira seção após a análise
            updated_content = updated_content.replace(
                "## Análise do Diretório (atualizada)", analysis_section
            )
    else:
        # Adicionar nova análise ao final
        updated_content = current_content + "\n\n" + new_content

    # Atualizar lobe
    update_result = lobe_service.update_lobe(lobe_name, updated_content)
    return update_result.get("success", False)


def create_kg_relations(lobe_name, mapping):
    """Cria relações no Knowledge Graph para o Lobo."""
    kg_service = get_kg_service()

    # Garantir que as entidades existam
    entities = ["NC-CTX-FR-001-cortex-central.mdc", lobe_name]
    for entity in entities:
        entity_result = kg_service.add_entity(
            entity, entity_type="lobe" if "LBE" in entity else "cortex"
        )
        if not entity_result.get("success"):
            print(
                f"    [WARN] Falha ao adicionar entidade {entity}: {entity_result.get('error', 'Unknown')}"
            )
            # Continuar mesmo se falhar (pode já existir)

    # Criar relação com o córtex central
    relation_result = kg_service.add_relation(
        source="NC-CTX-FR-001-cortex-central.mdc",
        relation="contains",
        target=lobe_name,
        metadata={
            "module": mapping["module"],
            "auto_generated": True,
            "timestamp": datetime.now().isoformat(),
        },
    )

    return relation_result.get("success", False)


def main():
    print("=== POVOAMENTO EXAUSTIVO DOS LOBOS NEOCORTEX ===\n")

    # 1. Analisar estrutura do projeto
    project_analysis = analyze_project_structure()

    # 2. Obter mapeamento de Lobos
    lobe_mapping = get_lobe_mapping()

    # 3. Processar cada Lobo
    lobe_service = get_lobe_service()
    manifest_service = get_manifest_service()

    total_lobes = len(lobe_mapping)
    processed = 0
    successes = 0

    for lobe_name, mapping in lobe_mapping.items():
        processed += 1
        print(
            f"\n[{processed}/{total_lobes}] Processando {lobe_name} ({mapping['module']})..."
        )

        # Verificar se Lobo existe
        lobe_info = lobe_service.get_lobe(lobe_name)
        if not lobe_info.get("exists"):
            print(f"  [SKIP] Lobe não encontrado, criando...")
            # Criar lobe básico primeiro
            basic_content = (
                f"# {lobe_name.replace('.mdc', '')}\n\n{mapping['description']}\n\n"
            )
            create_result = lobe_service.create_lobe(
                lobe_name=lobe_name,
                content=basic_content,
                metadata={
                    "module": mapping["module"],
                    "status": "active",
                    "auto_populated": True,
                },
            )
            if not create_result.get("success"):
                print(
                    f"  [ERROR] Falha ao criar lobe: {create_result.get('error', 'Unknown')}"
                )
                continue

        # Analisar diretórios alvo
        dir_analysis = {"exists": False, "files": [], "total_files": 0}
        for target_dir in mapping["target_dirs"]:
            if target_dir:
                analysis = analyze_directory(
                    target_dir,
                    mapping["target_files"][0] if mapping["target_files"] else "**/*",
                )
                if analysis["exists"]:
                    dir_analysis["exists"] = True
                    dir_analysis["files"].extend(analysis["files"])
                    dir_analysis["total_files"] += analysis["total_files"]

        # Gerar conteúdo específico
        new_content = generate_lobe_content(
            lobe_name, mapping, project_analysis, dir_analysis
        )

        # Atualizar Lobo
        update_success = update_lobe_with_content(lobe_name, new_content)
        if update_success:
            print(f"  [OK] Lobo atualizado com conteúdo específico")

            # Gerar manifesto
            manifest_result = manifest_service.generate_manifest(target=lobe_name)
            if manifest_result.get("success"):
                print(f"  [OK] Manifesto gerado")
            else:
                print(
                    f"  [WARN] Falha ao gerar manifesto: {manifest_result.get('error', 'Unknown')}"
                )

            # Criar relações no KG
            kg_success = create_kg_relations(lobe_name, mapping)
            if kg_success:
                print(f"  [OK] Relações KG criadas")
            else:
                print(f"  [WARN] Falha ao criar relações KG")

            successes += 1
        else:
            print(f"  [ERROR] Falha ao atualizar lobe")

    # 4. Criar checkpoint final
    checkpoint_service = get_checkpoint_service()
    checkpoint_id = f"CP-POPULATION-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    checkpoint_result = checkpoint_service.set_current_checkpoint(
        checkpoint_id=checkpoint_id,
        description=f"Povoamento exaustivo de {successes}/{total_lobes} Lobos",
        lobe_id="NC-LBE-FR-KNOWLEDGE-001.mdc",
    )

    if checkpoint_result.get("success"):
        print(f"\n[OK] Checkpoint criado: {checkpoint_id}")
    else:
        print(
            f"\n[WARN] Falha ao criar checkpoint: {checkpoint_result.get('error', 'Unknown')}"
        )

    # Resumo
    print(f"\n{'=' * 60}")
    print("RESUMO DO POVOAMENTO EXAUSTIVO")
    print(f"{'=' * 60}")
    print(f"- Total de Lobos processados: {processed}")
    print(f"- Lobos atualizados com sucesso: {successes}")
    print(f"- Análise do projeto: {'Sim' if project_analysis else 'Não'}")
    print(
        f"- Checkpoint: {checkpoint_id if checkpoint_result.get('success') else 'Falha'}"
    )

    return 0 if successes > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
