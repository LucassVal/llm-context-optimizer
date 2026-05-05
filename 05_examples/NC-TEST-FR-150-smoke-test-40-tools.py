#!/usr/bin/env python3
"""
NC-TEST-FR-150 — Smoke Test das 40 Tools MCP
Validação end-to-end via import check (não JSON-RPC real)

Objetivo: verificar que cada módulo de tool importa sem erro
e tem função register_tool() obrigatória.
"""

import importlib.util
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def get_config():
    """Obtém configuração do NeoCortex."""
    try:
        # Tentar importar via módulo core
        import importlib
        mod = importlib.import_module("neocortex.config")
        return mod.get_config()
    except ImportError:
        # Fallback: usar caminho padrão
        class MockConfig:
            def __init__(self):
                self.project_root = Path(__file__).parents[1]  # TURBOQUANT_V42/
                self.cortex_path = self.project_root / "01_neocortex_framework" / ".neocortex"
        
        return MockConfig()

def find_tools_directory() -> Path:
    """Encontra o diretório de tools MCP."""
    config = get_config()
    
    # Possíveis locais
    possible_paths = [
        config.project_root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools",
        Path(__file__).parent.parent / "01_neocortex_framework" / "neocortex" / "mcp" / "tools",
        Path(__file__).parent / "neocortex" / "mcp" / "tools",
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info("Tools directory encontrado: %s", path)
            return path
    
    raise FileNotFoundError("Diretório de tools não encontrado")

def import_tool_module(tool_path: Path) -> Dict:
    """
    Tenta importar um módulo de tool.
    
    Returns:
        Dict com status e informações
    """
    result = {
        "tool_name": tool_path.name,
        "tool_path": str(tool_path),
        "status": "UNKNOWN",
        "error": None,
        "has_register_tool": False,
        "import_time_ms": 0,
    }
    
    start_time = datetime.now()
    
    try:
        # Verificar compilação Python
        import py_compile
        py_compile.compile(tool_path, doraise=True)
        
        # Importar módulo dinamicamente
        module_name = tool_path.stem.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, tool_path)
        
        if spec is None or spec.loader is None:
            result["status"] = "FAIL"
            result["error"] = "spec_from_file_location retornou None"
            return result
        
        module = importlib.util.module_from_spec(spec)
        
        # Executar módulo em namespace isolado
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # Verificar se tem register_tool
        if hasattr(module, "register_tool"):
            result["has_register_tool"] = True
            result["status"] = "PASS"
        else:
            result["status"] = "FAIL"
            result["error"] = "Módulo não tem função register_tool"
        
    except py_compile.PyCompileError as e:
        result["status"] = "FAIL"
        result["error"] = f"Erro de compilação: {e}"
    except SyntaxError as e:
        result["status"] = "FAIL"
        result["error"] = f"Erro de sintaxe: {e}"
    except ImportError as e:
        result["status"] = "FAIL"
        result["error"] = f"Erro de importação: {e}"
    except Exception as e:
        result["status"] = "FAIL"
        result["error"] = f"Erro inesperado: {type(e).__name__}: {e}"
    
    # Calcular tempo
    end_time = datetime.now()
    result["import_time_ms"] = int((end_time - start_time).total_seconds() * 1000)
    
    return result

def should_skip_tool(tool_name: str) -> bool:
    """Determina se deve pular uma tool."""
    # Pular arquivos especiais
    if tool_name in ["__init__.py", "__pycache__"]:
        return True
    
    # Pular se não for .py
    if not tool_name.endswith(".py"):
        return True
    
    # Pular se for bridge/legacy
    skip_patterns = ["pulse.py", "bridge", "legacy", "backup"]
    for pattern in skip_patterns:
        if pattern in tool_name.lower():
            return True
    
    return False

def run_smoke_test() -> Dict:
    """Executa smoke test em todas as tools."""
    try:
        tools_dir = find_tools_directory()
    except FileNotFoundError as e:
        logger.error("Erro ao encontrar tools directory: %s", e)
        return {
            "success": False,
            "error": str(e),
            "results": [],
            "summary": {"total": 0, "pass": 0, "fail": 0, "skip": 0}
        }
    
    logger.info("Iniciando smoke test em: %s", tools_dir)
    
    # Coletar todas as tools
    all_tools = list(tools_dir.glob("*.py"))
    
    # Incluir também tools da subpasta v1/
    v1_dir = tools_dir / "v1"
    if v1_dir.exists():
        all_tools.extend(v1_dir.glob("*.py"))
    
    results = []
    summary = {"total": 0, "pass": 0, "fail": 0, "skip": 0}
    
    for tool_path in all_tools:
        tool_name = tool_path.name
        
        if should_skip_tool(tool_name):
            logger.debug("Pulando tool: %s", tool_name)
            results.append({
                "tool_name": tool_name,
                "tool_path": str(tool_path),
                "status": "SKIP",
                "reason": "skip_pattern",
                "import_time_ms": 0,
            })
            summary["skip"] += 1
            summary["total"] += 1
            continue
        
        logger.info("Testando tool: %s", tool_name)
        result = import_tool_module(tool_path)
        results.append(result)
        
        summary["total"] += 1
        if result["status"] == "PASS":
            summary["pass"] += 1
            logger.info("  ✅ PASS: %s (%.1f ms)", tool_name, result["import_time_ms"])
        else:
            summary["fail"] += 1
            logger.warning("  ❌ FAIL: %s - %s", tool_name, result["error"])
    
    # Ordenar resultados por status
    results.sort(key=lambda x: {"PASS": 0, "FAIL": 1, "SKIP": 2, "UNKNOWN": 3}[x["status"]])
    
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "tools_directory": str(tools_dir),
        "summary": summary,
        "results": results,
    }

def save_report(report: Dict, output_path: Optional[Path] = None) -> Path:
    """Salva relatório em JSON."""
    if output_path is None:
        output_path = Path(__file__).parent / "NC-RPT-150-smoke-test-results.json"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info("Relatório salvo em: %s", output_path)
    return output_path

def print_summary(report: Dict):
    """Imprime resumo do smoke test."""
    if not report["success"]:
        print(f"❌ Smoke test falhou: {report.get('error', 'Erro desconhecido')}")
        return
    
    summary = report["summary"]
    total = summary["total"]
    pass_count = summary["pass"]
    fail_count = summary["fail"]
    skip_count = summary["skip"]
    
    print("\n" + "="*60)
    print("SMOKE TEST DAS TOOLS MCP - RESUMO")
    print("="*60)
    print(f"Total de tools: {total}")
    print(f"✅ PASS: {pass_count} ({pass_count/total*100:.1f}%)")
    print(f"❌ FAIL: {fail_count} ({fail_count/total*100:.1f}%)")
    print(f"⏭️  SKIP: {skip_count} ({skip_count/total*100:.1f}%)")
    print("="*60)
    
    # Listar failures
    if fail_count > 0:
        print("\n❌ TOOLS COM FALHA:")
        for result in report["results"]:
            if result["status"] == "FAIL":
                print(f"  • {result['tool_name']}: {result.get('error', 'Erro desconhecido')}")
    
    # Listar skips
    if skip_count > 0:
        print(f"\n⏭️  TOOLS PULADAS: {skip_count}")
    
    print(f"\n📊 Relatório completo: {report.get('tools_directory', 'N/A')}")
    print(f"📅 Timestamp: {report.get('timestamp', 'N/A')}")

def main():
    """Função principal."""
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Iniciando NC-TEST-FR-150 Smoke Test")
    
    try:
        # Executar smoke test
        report = run_smoke_test()
        
        # Salvar relatório
        report_path = save_report(report)
        
        # Imprimir resumo
        print_summary(report)
        
        # Verificar se passou critério mínimo
        summary = report["summary"]
        if summary["fail"] > 0:
            logger.warning("%d tools falharam no smoke test", summary["fail"])
            sys.exit(1)
        else:
            logger.info("✅ Todas as tools passaram no smoke test!")
            sys.exit(0)
            
    except Exception as e:
        logger.error("Erro fatal no smoke test: %s", e, exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()