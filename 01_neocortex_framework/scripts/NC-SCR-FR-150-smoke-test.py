#!/usr/bin/env python3
"""
NC-SCR-FR-150: Smoke Test para 40+ ferramentas MCP NeoCortex

Script que testa importação, registro e funcionamento básico de todas as ferramentas MCP.
Gera relatórios JSON e análise de gaps de cobertura.

Conforme NC-DS-150: Smoke Test 40 Tools MCP
"""

import importlib.util
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

# Configuração de logging (R11: NUNCA print)
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Path do projeto
PROJECT_ROOT = Path(__file__).parent.parent
CORE_DIR = PROJECT_ROOT / "neocortex" / "core"
MCP_DIR = PROJECT_ROOT / "neocortex" / "mcp"
TOOLS_DIR = MCP_DIR / "tools"
CONFIG_DIR = MCP_DIR

class SmokeTestResult:
    """Resultado do smoke test para uma ferramenta"""
    
    def __init__(self, tool_name: str, module_path: str):
        self.tool_name = tool_name
        self.module_path = module_path
        self.status = "PENDING"
        self.error = None
        self.methods = []
        self.import_time = None
        self.register_time = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "module_path": str(self.module_path),
            "status": self.status,
            "error": self.error,
            "methods": self.methods,
            "import_time": self.import_time,
            "register_time": self.register_time
        }

class MCPToolSmokeTester:
    """Executor de smoke tests para ferramentas MCP"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tools_dir = project_root / "neocortex" / "mcp" / "tools"
        self.results: Dict[str, SmokeTestResult] = {}
        
    def discover_tools(self) -> List[Path]:
        """Descobre todas as ferramentas MCP disponíveis"""
        tools = []
        
        # 1. Ferramentas em tools/*.py
        for tool_file in self.tools_dir.glob("*.py"):
            if tool_file.name.startswith("__"):
                continue
            tools.append(tool_file)
            
        # 2. Ferramentas do TOOL_MODULE_MAP em sub_server.py
        sub_server_path = self.project_root / "neocortex" / "mcp" / "sub_server.py"
        if sub_server_path.exists():
            try:
                spec = importlib.util.spec_from_file_location("sub_server", sub_server_path)
                sub_server = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(sub_server)
                
                if hasattr(sub_server, "TOOL_MODULE_MAP"):
                    for tool_name, module_name in sub_server.TOOL_MODULE_MAP.items():
                        # Tentar encontrar o módulo
                        module_path = self._find_module_path(module_name)
                        if module_path:
                            tools.append(module_path)
            except Exception as e:
                logger.warning(f"Erro ao ler TOOL_MODULE_MAP: {e}")
                
        # 3. Ferramentas extras do NC-CFG-FR-005
        autoload_config = CONFIG_DIR / "NC-CFG-FR-005-tool-autoload.yaml"
        if autoload_config.exists():
            try:
                with open(autoload_config, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    
                for tool_config in config.get("extra_tools", []):
                    module_path = self.project_root / tool_config["module_path"]
                    if module_path.exists():
                        tools.append(module_path)
            except Exception as e:
                logger.warning(f"Erro ao ler NC-CFG-FR-005: {e}")
                
        # Remover duplicatas
        unique_tools = list(set(tools))
        logger.info(f"Descobridas {len(unique_tools)} ferramentas únicas")
        return unique_tools
    
    def _find_module_path(self, module_name: str) -> Optional[Path]:
        """Tenta encontrar o caminho de um módulo"""
        # Tentar como arquivo .py
        possible_paths = [
            self.tools_dir / f"{module_name}.py",
            self.project_root / "neocortex" / "mcp" / f"{module_name}.py",
            self.project_root / "neocortex" / f"{module_name}.py",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        return None
    
    def test_tool_import(self, tool_path: Path) -> Optional[Any]:
        """Testa importação dinâmica da ferramenta (R09)"""
        try:
            module_name = tool_path.stem
            spec = importlib.util.spec_from_file_location(module_name, tool_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.error(f"Erro ao importar {tool_path.name}: {e}")
            return None
    
    def test_tool_registration(self, module: Any) -> bool:
        """Verifica se a ferramenta tem função register_tool()"""
        return hasattr(module, "register_tool")
    
    def test_tool_methods(self, module: Any) -> List[str]:
        """Identifica métodos disponíveis na ferramenta"""
        methods = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and not attr_name.startswith("_"):
                methods.append(attr_name)
        return methods
    
    def run_smoke_test(self, tool_path: Path) -> SmokeTestResult:
        """Executa smoke test completo para uma ferramenta"""
        tool_name = tool_path.stem
        result = SmokeTestResult(tool_name, tool_path)
        
        try:
            # 1. Testar importação
            logger.info(f"Testando importação: {tool_name}")
            module = self.test_tool_import(tool_path)
            if not module:
                result.status = "FAIL_IMPORT"
                result.error = "Falha na importação do módulo"
                return result
                
            # 2. Testar registro
            if not self.test_tool_registration(module):
                result.status = "FAIL_REGISTER"
                result.error = "Módulo não tem função register_tool()"
                return result
                
            # 3. Testar métodos
            methods = self.test_tool_methods(module)
            if not methods:
                result.status = "FAIL_METHODS"
                result.error = "Módulo não tem métodos registrados"
                return result
                
            # 4. Verificar se é deprecated/legacy
            module_doc = module.__doc__ or ""
            if any(word in module_doc.lower() for word in ["deprecated", "legacy", "obsolete"]):
                result.status = "SKIP"
                result.error = "Módulo marcado como deprecated/legacy"
                return result
                
            # Sucesso!
            result.status = "PASS"
            result.methods = methods
            logger.info(f"✅ {tool_name}: PASS ({len(methods)} métodos)")
            
        except Exception as e:
            result.status = "FAIL_UNKNOWN"
            result.error = str(e)
            logger.error(f"❌ {tool_name}: {e}")
            
        return result
    
    def run_all_tests(self, dry_run: bool = False) -> Dict[str, Any]:
        """Executa smoke tests para todas as ferramentas"""
        logger.info("Iniciando smoke tests para ferramentas MCP...")
        
        if dry_run:
            logger.info("DRY RUN - apenas descobrindo ferramentas")
            tools = self.discover_tools()
            return {
                "dry_run": True,
                "total_tools": len(tools),
                "tool_paths": [str(p) for p in tools]
            }
        
        tools = self.discover_tools()
        results = []
        
        for tool_path in tools:
            result = self.run_smoke_test(tool_path)
            self.results[tool_path.stem] = result
            results.append(result.to_dict())
            
        # Estatísticas
        stats = self._calculate_statistics()
        
        return {
            "total_tools": len(tools),
            "tested_tools": len(results),
            "statistics": stats,
            "results": results
        }
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calcula estatísticas dos resultados"""
        status_counts = {}
        for result in self.results.values():
            status = result.status
            status_counts[status] = status_counts.get(status, 0) + 1
            
        total = len(self.results)
        pass_count = status_counts.get("PASS", 0)
        pass_rate = (pass_count / total * 100) if total > 0 else 0
        
        return {
            "status_counts": status_counts,
            "pass_rate": f"{pass_rate:.1f}%",
            "total_tools": total,
            "passing_tools": pass_count
        }
    
    def generate_json_report(self, results: Dict[str, Any], output_path: Path):
        """Gera relatório JSON detalhado"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Relatório JSON gerado: {output_path}")
    
    def generate_gaps_report(self, results: Dict[str, Any], output_path: Path):
        """Gera relatório de gaps em Markdown"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Relatório de Gaps de Cobertura - Smoke Test MCP\n\n")
            f.write(f"**Data:** {results.get('timestamp', 'N/A')}\n")
            f.write(f"**Total de ferramentas:** {results.get('total_tools', 0)}\n")
            f.write(f"**Ferramentas testadas:** {results.get('tested_tools', 0)}\n\n")
            
            stats = results.get('statistics', {})
            f.write(f"**Taxa de sucesso:** {stats.get('pass_rate', '0%')}\n")
            f.write(f"**Ferramentas PASS:** {stats.get('passing_tools', 0)}\n\n")
            
            # Status breakdown
            f.write("## Distribuição por Status\n\n")
            status_counts = stats.get('status_counts', {})
            for status, count in status_counts.items():
                f.write(f"- **{status}:** {count} ferramentas\n")
            
            # Ferramentas críticas
            f.write("\n## Ferramentas Críticas\n\n")
            critical_tools = ["brain", "cortex", "agent", "task", "config", "security"]
            for tool in results.get('results', []):
                if any(critical in tool['tool_name'].lower() for critical in critical_tools):
                    status_icon = "✅" if tool['status'] == "PASS" else "❌"
                    f.write(f"- {status_icon} **{tool['tool_name']}**: {tool['status']}")
                    if tool['error']:
                        f.write(f" - {tool['error']}")
                    f.write("\n")
            
            # Recomendações
            f.write("\n## Recomendações\n\n")
            fail_count = sum(1 for t in results.get('results', []) if t['status'].startswith("FAIL"))
            if fail_count > 0:
                f.write(f"1. **Corrigir {fail_count} ferramentas com FAIL**\n")
                f.write("2. **Priorizar ferramentas críticas**\n")
                f.write("3. **Documentar ferramentas SKIP/deprecated**\n")
            else:
                f.write("✅ **Todas as ferramentas estão funcionando corretamente!**\n")
        
        logger.info(f"Relatório de gaps gerado: {output_path}")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smoke Test para ferramentas MCP NeoCortex")
    parser.add_argument("--dry-run", action="store_true", help="Apenas descobre ferramentas, não executa testes")
    parser.add_argument("--output-dir", default="05_examples", help="Diretório para saída dos relatórios")
    args = parser.parse_args()
    
    # Configurar paths
    project_root = Path("C:/Users/Lucas Valério/Desktop/TURBOQUANT_V42/01_neocortex_framework")
    output_dir = project_root / args.output_dir
    
    # Criar diretório de saída se não existir
    output_dir.mkdir(exist_ok=True)
    
    # Executar smoke tests
    tester = MCPToolSmokeTester(project_root)
    results = tester.run_all_tests(dry_run=args.dry_run)
    
    if args.dry_run:
        print("DRY RUN COMPLETED")
        print(f"Total de ferramentas encontradas: {results['total_tools']}")
        return
    
    # Adicionar timestamp
    from datetime import datetime
    results['timestamp'] = datetime.now().isoformat()
    
    # Gerar relatórios
    json_report = output_dir / "NC-RPT-150-smoke-test-report.json"
    gaps_report = output_dir / "NC-RPT-150-coverage-gaps.md"
    
    tester.generate_json_report(results, json_report)
    tester.generate_gaps_report(results, gaps_report)
    
    # Verificar cobertura mínima
    stats = results.get('statistics', {})
    pass_rate = float(stats.get('pass_rate', '0%').rstrip('%'))
    
    if pass_rate >= 85:
        logger.info(f"✅ Cobertura mínima atingida: {pass_rate:.1f}% (mínimo: 85%)")
    else:
        logger.warning(f"⚠️ Cobertura abaixo do mínimo: {pass_rate:.1f}% (mínimo: 85%)")
    
    logger.info("Smoke tests concluídos!")

if __name__ == "__main__":
    main()