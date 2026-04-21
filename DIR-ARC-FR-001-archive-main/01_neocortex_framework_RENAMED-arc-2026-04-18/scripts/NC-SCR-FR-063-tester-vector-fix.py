#!/usr/bin/env python3
# Fix encoding for Windows (UTF-8)
import sys

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
domain: "testing"
layer: "infra"
type: "SCR"
tags: ["tester", "vector", "async", "api", "correction", "coverage", "nc-ds-063"]
hash: "auto-generated"
---

NC-SCR-FR-063-tester-vector-fix.py
Agente Tester: Corrige incompatibilidade assncrona e divergncia de API nos testes do VectorEngine.
Autor: T0 (NeoCortex)
Data: 2026-04-14
Status: Fase 4/3 - Estabilizao da suite de testes
"""

import ast
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

# Configuraes
PROJECT_ROOT = Path(__file__).parent.parent.parent
VECTOR_ENGINE_PATH = (
    PROJECT_ROOT / "01_neocortex_framework" / "neocortex" / "infra" / "vector_engine.py"
)
TEST_FILE_PATH = (
    PROJECT_ROOT / "01_neocortex_framework" / "tests" / "test_vector_engine.py"
)
COVERAGE_CHECKLIST = (
    PROJECT_ROOT
    / "01_neocortex_framework"
    / "DIR-DOC-FR-001-docs-main"
    / "test_coverage_checklist.md"
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def analyze_vector_engine_api() -> Dict[str, Dict[str, Any]]:
    """
    Analisa a classe VectorEngine via AST para extrair assinaturas reais dos mtodos.
    """
    logger.info(f"Analisando API real de {VECTOR_ENGINE_PATH.name}")

    if not VECTOR_ENGINE_PATH.exists():
        logger.error(f"Arquivo VectorEngine no encontrado: {VECTOR_ENGINE_PATH}")
        return {}

    try:
        content = VECTOR_ENGINE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(content)

        api_info = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                if "VectorEngine" in class_name:
                    logger.info(f"Encontrada classe: {class_name}")

                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            method_name = item.name
                            is_async = isinstance(item, ast.AsyncFunctionDef)

                            # Extrair parmetros
                            params = []
                            for arg in item.args.args:
                                params.append(arg.arg)

                            # Verificar se tem decorators especficos
                            decorators = []
                            for decorator in item.decorator_list:
                                if isinstance(decorator, ast.Name):
                                    decorators.append(decorator.id)
                                elif isinstance(decorator, ast.Attribute):
                                    decorators.append(decorator.attr)

                            api_info[method_name] = {
                                "class": class_name,
                                "is_async": is_async,
                                "params": params,
                                "decorators": decorators,
                                "line": item.lineno,
                            }

        logger.info(f"Mtodos pblicos encontrados: {list(api_info.keys())}")
        return api_info

    except Exception as e:
        logger.error(f"Erro ao analisar VectorEngine: {e}")
        return {}


def analyze_test_file() -> Dict[str, List[int]]:
    """
    Analisa o arquivo de teste para encontrar testes e suas chamadas.
    """
    logger.info(f"Analisando arquivo de teste: {TEST_FILE_PATH.name}")

    if not TEST_FILE_PATH.exists():
        logger.error(f"Arquivo de teste no encontrado: {TEST_FILE_PATH}")
        return {}

    try:
        content = TEST_FILE_PATH.read_text(encoding="utf-8")

        # Encontrar funes de teste
        test_functions = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            if line.strip().startswith("def test_"):
                func_name = line.strip().split("def ")[1].split("(")[0]
                test_functions.append((func_name, i))

        # Encontrar chamadas a mtodos do VectorEngine
        method_calls = {}
        pattern = r"self\.(engine|vector_engine)\.(\w+)\("
        matches = re.findall(pattern, content)

        for match in matches:
            method_name = match[1]
            if method_name not in method_calls:
                method_calls[method_name] = []
            # No capturamos nmeros de linha aqui, mas podemos se necessrio

        logger.info(f"Funes de teste encontradas: {len(test_functions)}")
        logger.info(f"Chamadas de mtodo encontradas: {list(method_calls.keys())}")

        return {
            "test_functions": test_functions,
            "method_calls": method_calls,
            "content": content,
            "lines": lines,
        }

    except Exception as e:
        logger.error(f"Erro ao analisar arquivo de teste: {e}")
        return {}


def fix_async_incompatibility(test_analysis: Dict, api_info: Dict) -> str:
    """
    Corrige incompatibilidade assncrona no arquivo de teste.
    Retorna o contedo corrigido.
    """
    logger.info("Aplicando correes de incompatibilidade assncrona")

    content = test_analysis.get("content", "")
    lines = test_analysis.get("lines", [])

    if not content:
        return content

    # 1. Adicionar import pytest_asyncio se necessrio
    if "import pytest_asyncio" not in content:
        # Encontrar onde inserir (aps outros imports, evitando dentro de blocos multi-linha)
        paren_count = 0
        in_import_block = False
        import_block_end = -1
        for i, line in enumerate(lines):
            # Contar parnteses para detectar blocos multi-linha
            paren_before = paren_count
            paren_count += line.count("(") - line.count(")")
            # Detecta incio de um bloco de import (fora de parnteses)
            if (
                line.strip().startswith("import ") or line.strip().startswith("from ")
            ) and paren_before == 0:
                in_import_block = True
            # Se estamos em um bloco de import e os parnteses fecharam, este  o fim do bloco
            if in_import_block and paren_count == 0:
                import_block_end = i  # linha atual  a ltima do bloco
                in_import_block = False
        # Se encontramos um bloco de import, inserir aps ele
        if import_block_end != -1:
            insert_line = import_block_end + 1
        else:
            # Caso contrrio, inserir aps a primeira linha no vazia (aps shebang/docstring)
            for i, line in enumerate(lines):
                if (
                    line.strip()
                    and not line.strip().startswith("#")
                    and not line.strip().startswith('"""')
                ):
                    insert_line = i + 1
                    break
            else:
                insert_line = 0
        lines.insert(insert_line, "import pytest_asyncio")
        logger.info("Import pytest_asyncio adicionado")

    # 2. Adicionar @pytest.mark.asyncio aos testes que chamam mtodos async
    test_functions = test_analysis.get("test_functions", [])
    method_calls = test_analysis.get("method_calls", {})

    # Identificar quais mtodos da API so async
    async_methods = [name for name, info in api_info.items() if info.get("is_async")]

    # Para cada funo de teste, verificar se chama mtodos async
    for func_name, line_num in test_functions:
        # Encontrar corpo da funo
        func_start = line_num - 1
        func_end = None
        indent_level = None

        # Determinar indentao da funo
        if func_start < len(lines):
            indent_level = len(lines[func_start]) - len(lines[func_start].lstrip())

        # Encontrar fim da funo
        for i in range(func_start + 1, len(lines)):
            if (
                lines[i].strip()
                and len(lines[i]) - len(lines[i].lstrip()) <= indent_level
            ):
                func_end = i
                break

        if func_end is None:
            func_end = len(lines)

        # Verificar se h chamadas a mtodos async no corpo
        has_async_call = False
        for i in range(func_start, func_end):
            for async_method in async_methods:
                if f".{async_method}(" in lines[i]:
                    has_async_call = True
                    break
            if has_async_call:
                break

        if has_async_call:
            # Adicionar decorator @pytest.mark.asyncio se no tiver
            decorator_line = lines[func_start - 1] if func_start > 0 else ""
            if "@pytest.mark.asyncio" not in decorator_line:
                lines.insert(func_start, " " * indent_level + "@pytest.mark.asyncio")
                logger.info(f"Decorator @pytest.mark.asyncio adicionado a {func_name}")

    # 3. Corrigir chamadas de mtodo para corresponder  API real
    # Mapeamento de nomes antigos para novos (se necessrio)
    method_mapping = {
        "get_vector": "get_by_id",
        "delete_vector": "delete",
    }

    for i, line in enumerate(lines):
        for old_name, new_name in method_mapping.items():
            if f".{old_name}(" in line and old_name in line:
                # Verificar se o novo nome existe na API
                if new_name in api_info:
                    lines[i] = line.replace(f".{old_name}(", f".{new_name}(")
                    logger.info(f"Corrigido {old_name} -> {new_name} na linha {i + 1}")

    # 4. Adicionar mocks para mtodos no testados
    # Identificar mtodos da API que no so chamados nos testes
    tested_methods = set(method_calls.keys())
    all_api_methods = set(api_info.keys())
    untested_methods = all_api_methods - tested_methods

    # Mtodos que devem ser mockados (no crticos para testes)
    methods_to_mock = {"initialize", "clear", "close", "update"}

    for method in methods_to_mock:
        if method in untested_methods:
            logger.info(
                f"Mtodo {method} no testado - considerar adicionar mock se necessrio"
            )

    return "\n".join(lines)


def fix_api_divergence(content: str, api_info: Dict) -> str:
    """
    Corrige divergncia de API (nomes de mtodo, parmetros).
    """
    lines = content.split("\n")

    # Correes especficas baseadas na anlise real
    # Estas correes devem ser ajustadas aps inspecionar a API real

    corrections = [
        # (padro_antigo, novo_padro)
        (r"self\.engine\.vector_dimension", "self.engine._vector_dimension"),  # exemplo
        (r'add_vectors\("test"', 'add("test"'),  # exemplo
    ]

    for i, line in enumerate(lines):
        for pattern, replacement in corrections:
            if re.search(pattern, line):
                lines[i] = re.sub(pattern, replacement, line)
                logger.info(f"Correo de API aplicada na linha {i + 1}")

    return "\n".join(lines)


def generate_coverage_checklist(api_info: Dict, test_analysis: Dict) -> None:
    """
    Gera checklist de cobertura de testes.
    """
    logger.info("Gerando checklist de cobertura de testes")

    tested_methods = set(test_analysis.get("method_calls", {}).keys())

    checklist_content = "# Checklist de Cobertura de Testes - VectorEngine\n\n"
    checklist_content += "Gerado em: 2026-04-14\n"
    checklist_content += f"API analisada: {VECTOR_ENGINE_PATH.name}\n"
    checklist_content += f"Arquivo de teste: {TEST_FILE_PATH.name}\n\n"

    checklist_content += "## Mtodos Pblicos da API\n\n"

    for method_name, info in sorted(api_info.items()):
        if method_name.startswith("_"):
            continue  # Ignorar mtodos privados

        is_tested = method_name in tested_methods
        status = "[x]" if is_tested else "[ ]"

        checklist_content += f"{status} **{method_name}**\n"
        checklist_content += f"  - Classe: {info.get('class', 'N/A')}\n"
        checklist_content += f"  - Async: {info.get('is_async', False)}\n"
        checklist_content += f"  - Parmetros: {', '.join(info.get('params', []))}\n"
        checklist_content += f"  - Linha: {info.get('line', 'N/A')}\n"

        if not is_tested:
            checklist_content += "  - **ATENO**: No testado\n"

        checklist_content += "\n"

    # Estatsticas
    total_methods = len([m for m in api_info.keys() if not m.startswith("_")])
    tested_count = len([m for m in tested_methods if not m.startswith("_")])
    coverage_pct = (tested_count / total_methods * 100) if total_methods > 0 else 0

    checklist_content += "## Estatsticas\n\n"
    checklist_content += f"- Total de mtodos pblicos: {total_methods}\n"
    checklist_content += f"- Mtodos testados: {tested_count}\n"
    checklist_content += f"- Mtodos no testados: {total_methods - tested_count}\n"
    checklist_content += f"- Cobertura: {coverage_pct:.1f}%\n\n"

    checklist_content += "## Prximos Passos\n\n"
    checklist_content += "1. Executar testes corrigidos: `pytest tests/test_vector_engine.py -v --asyncio-mode=auto`\n"
    checklist_content += "2. Verificar se todos os testes passam\n"
    checklist_content += "3. Adicionar testes para mtodos marcados como no testados\n"
    checklist_content += "4. Atualizar este checklist aps novas implementaes\n"

    with open(COVERAGE_CHECKLIST, "w", encoding="utf-8") as f:
        f.write(checklist_content)

    logger.info(f"Checklist de cobertura salvo em {COVERAGE_CHECKLIST}")
    logger.info(f"Cobertura atual: {coverage_pct:.1f}%")


def validate_test_file(content: str) -> bool:
    """
    Validaes bsicas no arquivo de teste corrigido.
    """
    # Verificar imports necessrios
    required_imports = ["pytest", "asyncio"]
    missing_imports = []

    for imp in required_imports:
        if imp not in content and f"import {imp}" not in content:
            missing_imports.append(imp)

    if missing_imports:
        logger.warning(f"Imports faltantes: {missing_imports}")

    # Verificar se h chamadas await para mtodos async
    lines = content.split("\n")
    has_async_calls = False
    has_awaits = False

    for line in lines:
        if "async def" in line:
            has_async_calls = True
        if "await " in line:
            has_awaits = True

    if has_async_calls and not has_awaits:
        logger.warning("Testes async detectados mas sem chamadas await")

    return len(missing_imports) == 0


def main() -> None:
    """
    Fluxo principal do Agente Tester.
    """
    logger.info("=== INCIO: Agente Tester - Correo de Testes VectorEngine ===")

    # 1. Anlise da API real
    api_info = analyze_vector_engine_api()

    if not api_info:
        logger.error("No foi possvel analisar a API do VectorEngine. Abortando.")
        return

    # 2. Anlise do arquivo de teste atual
    test_analysis = analyze_test_file()

    if not test_analysis:
        logger.error("No foi possvel analisar o arquivo de teste. Abortando.")
        return

    # 3. Backup do arquivo original
    backup_path = TEST_FILE_PATH.with_suffix(".py.backup")
    if not backup_path.exists():
        TEST_FILE_PATH.rename(backup_path)
        logger.info(f"Backup criado: {backup_path}")

    # 4. Aplicar correes
    logger.info("Aplicando correes no arquivo de teste...")

    # 4.1. Corrigir incompatibilidade assncrona
    fixed_content = fix_async_incompatibility(test_analysis, api_info)

    # 4.2. Corrigir divergncia de API
    fixed_content = fix_api_divergence(fixed_content, api_info)

    # 5. Validar correes
    is_valid = validate_test_file(fixed_content)

    if not is_valid:
        logger.warning("Validao encontrou problemas, mas continuando...")

    # 6. Salvar arquivo corrigido
    with open(TEST_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(fixed_content)

    logger.info(f"Arquivo de teste corrigido salvo em {TEST_FILE_PATH}")

    # 7. Gerar checklist de cobertura
    generate_coverage_checklist(api_info, test_analysis)

    # 8. Relatrio final
    logger.info("=== RELATRIO FINAL ===")
    logger.info(f"Mtodos da API analisados: {len(api_info)}")
    logger.info(
        f"Funes de teste encontradas: {len(test_analysis.get('test_functions', []))}"
    )
    logger.info(f"Arquivo corrigido: {TEST_FILE_PATH}")
    logger.info(f"Checklist de cobertura: {COVERAGE_CHECKLIST}")
    logger.info(f"Backup mantido em: {backup_path}")

    # 9. Instrues para execuo
    print("\n" + "=" * 60)
    print("INSTRUES PARA VALIDAO:")
    print("=" * 60)
    print("1. Execute os testes corrigidos:")
    print("   pytest tests/test_vector_engine.py -v --asyncio-mode=auto")
    print("2. Verifique se todos os testes passam")
    print(f"3. Consulte o checklist de cobertura: {COVERAGE_CHECKLIST}")
    print("4. Se houver falhas, revise as correes aplicadas")
    print("5. O backup original est em: tests/test_vector_engine.py.backup")
    print("=" * 60)

    logger.info("=== FIM: Agente Tester concludo ===")


if __name__ == "__main__":
    main()
