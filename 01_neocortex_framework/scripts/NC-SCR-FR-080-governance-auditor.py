#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NC-SCR-FR-080-governance-auditor.py
Auditor e Sincronizador de Ambientes NeoCortex

Script de governana refinado que:
1. Identifica o ambiente ativo (original vs espelho)
2. Mapeia "materialidade" do ambiente: arquivos Python, YAML, MD, PIPs
3. Cruza com catlogos existentes (artifact_catalog.json, renaming_plan.yaml, genealogy_graph.json)
4. Aplica as 20 regras de governana de IA
5. Gera relatrios de conformidade (Markdown + JSON)

Uso:
    python NC-SCR-FR-080-governance-auditor.py --environment original --dry-run
    python NC-SCR-FR-080-governance-auditor.py --environment original --execute
    python NC-SCR-FR-080-governance-auditor.py --compare-environments

Ciclo de vida (Dupla Mordaa):
    Criao  Abertura  Verificao  Execuo  Fechamento
"""

import argparse
import hashlib
import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Fix encoding for Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# 20 REGRAS DE GOVERNANA DE IA (categorizadas)
# ------------------------------------------------------------------------------
IA_GOVERNANCE_RULES = {
    # Categoria 1: Fundao e Estrutura
    "R01": "Inventrio de Ativos de IA: manter catlogo completo de modelos, ferramentas, agentes e fontes de dados",
    "R02": "Poltica Formalizada: polticas de governana escritas, versionadas e acessveis como cdigo ou documentos SSOT",
    "R03": "Estrutura de Diretrios Cannica: definir e impor estrutura padronizada",
    "R04": "Nomenclatura Padronizada: todos os arquivos seguem NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext",
    "R05": "Segregao de Ambientes: manter ambientes separados para desenvolvimento, teste e produo",
    # Categoria 2: Controle de Acesso e Identidade
    "R06": "Identidade para Agentes: cada agente deve ter identidade nica e verificvel",
    "R07": "Privilgio Mnimo (PoLP): agentes tm apenas permisses estritamente necessrias",
    "R08": "Atomic Locks (Path-Based): arquivos crticos protegidos contra modificao",
    "R09": "Segregao de Zonas de Escrita: agentes de diferentes domnios no podem escrever nos mesmos diretrios",
    # Categoria 3: Rastreabilidade e Auditoria
    "R10": "Trilha de Auditoria Imutvel: todas as aes registradas em log  prova de adulterao",
    "R11": "Versionamento de Artefatos: todos os artefatos de governana versionados (Git) com hashes de integridade",
    "R12": "Handoffs Formais: toda tarefa delegada a um agente documentada em handoff YAML",
    "R13": "Checkpoints e Save Points: estado do sistema salvo periodicamente e antes de operaes crticas",
    # Categoria 4: Execuo e Orquestrao
    "R14": "STEP 0 (Validao Pr-Ao): validar tarefa contra Regression Buffer e polticas antes de executar",
    "R15": "STEP -1 (Save Point): snapshot do estado antes de aes de escrita para possvel rollback",
    "R16": "Circuit Breaker: se um agente falhar repetidamente, deve ser suspenso para evitar loops de falha",
    "R17": "Rate Limiting por Ferramenta: limitar frequncia de chamadas a ferramentas crticas ou caras",
    # Categoria 5: Ciclo de Vida e Melhoria Contnua
    "R18": "Ciclo de Vida de Tickets: toda tarefa registrada como ticket e seguir fluxo formal",
    "R19": "Rotina de 4 Ciclos: trabalho deve seguir rotina diria/semanal para garantir continuidade e limpeza",
    "R20": "Reviso e Arquivo de Artefatos: artefatos antigos arquivados periodicamente para evitar acmulo",
}


class EnvironmentDetector:
    """Detecta se est no ambiente original ou espelho."""

    @staticmethod
    def detect() -> str:
        script_path = Path(__file__).resolve()
        if "_RENAMED" in str(script_path):
            return "mirror"
        else:
            return "original"

    @staticmethod
    def get_base_path(environment: str) -> Path:
        if environment == "original":
            return Path("01_neocortex_framework")
        elif environment == "mirror":
            return Path("01_neocortex_framework_RENAMED")
        else:
            raise ValueError(f"Ambiente desconhecido: {environment}")


class PIPAuditor:
    """Audita dependncias PIP do ambiente."""

    @staticmethod
    def get_installed_packages() -> List[Dict[str, Any]]:
        """Retorna lista de pacotes PIP instalados."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format", "json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.warning(f"Falha ao listar PIPs: {result.stderr}")
                return []
        except subprocess.TimeoutExpired:
            logger.warning("pip list excedeu timeout de 30s — retornando []")
            return []
        except Exception as e:
            logger.error(f"Erro ao obter PIPs: {e}")
            return []

    @staticmethod
    def audit_vulnerabilities() -> Dict[str, Any]:
        """Executa pip-audit para verificar vulnerabilidades (skip se não instalado)."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip_audit", "--format", "json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                if result.stdout:
                    try:
                        return json.loads(result.stdout)
                    except Exception:
                        return {"error": result.stderr}
                return {"error": result.stderr}
        except subprocess.TimeoutExpired:
            logger.warning("pip_audit excedeu timeout de 30s — skipping")
            return {"error": "timeout", "skipped": True}
        except FileNotFoundError:
            logger.info("pip-audit não instalado — skipping vulnerability check")
            return {"error": "pip-audit não instalado", "skipped": True}
        except Exception as e:
            logger.error(f"Erro no pip-audit: {e}")
            return {"error": str(e), "skipped": True}

    @staticmethod
    def get_dependency_tree() -> Dict[str, Any]:
        """Retorna árvore de dependências usando pipdeptree (skip se não instalado)."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pipdeptree", "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.warning(f"Falha no pipdeptree: {result.stderr}")
                return {}
        except subprocess.TimeoutExpired:
            logger.warning("pipdeptree excedeu timeout de 30s — skipping")
            return {"error": "timeout", "skipped": True}
        except FileNotFoundError:
            logger.info("pipdeptree não instalado — skipping dependency tree")
            return {"error": "pipdeptree não instalado", "skipped": True}
        except Exception as e:
            logger.error(f"Erro no pipdeptree: {e}")
            return {"error": str(e), "skipped": True}


class FileSystemMapper:
    """Mapeia arquivos do sistema de arquivos."""

    def __init__(self, base_path: Path):
        self.base_path = base_path

    def map_files(self, patterns: List[str] = None) -> List[Dict[str, Any]]:
        """Mapeia arquivos no ambiente."""
        if patterns is None:
            patterns = ["**/*.py", "**/*.yaml", "**/*.yml", "**/*.md", "**/*.json"]

        files = []
        for pattern in patterns:
            for file_path in self.base_path.rglob(pattern):
                # Ignorar diretrios como __pycache__
                if any(
                    part.startswith("__") and part.endswith("__")
                    for part in file_path.parts
                ):
                    continue
                if any(part.startswith(".") for part in file_path.parts):
                    continue

                try:
                    stat = file_path.stat()
                    files.append(
                        {
                            "path": str(file_path.relative_to(self.base_path)),
                            "absolute_path": str(file_path),
                            "size_bytes": stat.st_size,
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                            "created": datetime.fromtimestamp(
                                stat.st_ctime
                            ).isoformat(),
                            "extension": file_path.suffix.lower(),
                            "name": file_path.name,
                        }
                    )
                except OSError as e:
                    logger.warning(f"Erro ao acessar {file_path}: {e}")

        return files

    def compute_hash(self, filepath: Path) -> Optional[str]:
        """Calcula SHA-256 de um arquivo."""
        try:
            sha256 = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Erro ao calcular hash de {filepath}: {e}")
            return None


class CatalogCrossChecker:
    """Cruza mapeamento com catlogos existentes."""

    def __init__(self, base_path: Path):
        self.base_path = base_path

    def load_artifact_catalog(self) -> Dict[str, Any]:
        """Carrega artifact_catalog.json."""
        catalog_path = (
            self.base_path / "DIR-DOC-FR-001-docs-main" / "artifact_catalog.json"
        )
        if catalog_path.exists():
            try:
                with open(catalog_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar artifact_catalog: {e}")
        return {}

    def load_renaming_plan(self) -> Dict[str, Any]:
        """Carrega renaming_plan_v2_dedup.yaml."""
        plan_path = (
            self.base_path / "DIR-DOC-FR-001-docs-main" / "renaming_plan_v2_dedup.yaml"
        )
        if plan_path.exists():
            try:
                with open(plan_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar renaming_plan: {e}")
        return {}

    def load_genealogy_graph(self) -> Dict[str, Any]:
        """Carrega genealogy_graph.json."""
        graph_path = self.base_path.parent / "genealogy_graph.json"
        if graph_path.exists():
            try:
                with open(graph_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar genealogy_graph: {e}")
        return {}

    def check_naming_convention(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verifica conformidade com padro NC  ."""
        pattern = re.compile(r"^NC-[A-Z]+-[A-Z]+-\d{3}-.+\.\w+$")
        results = {
            "total_files": len(files),
            "nc_files": 0,
            "non_nc_files": [],
            "compliance_rate": 0.0,
        }

        for file in files:
            if pattern.match(file["name"]):
                results["nc_files"] += 1
            else:
                # Ignorar arquivos comuns como README.md, .gitignore, etc.
                if not (
                    file["name"]
                    in ["README.md", ".gitignore", ".gitattributes", "LICENSE"]
                    or file["name"].startswith(".")
                ):
                    results["non_nc_files"].append(file["path"])

        if results["total_files"] > 0:
            results["compliance_rate"] = (
                results["nc_files"] / results["total_files"]
            ) * 100

        return results


class GovernanceAuditor:
    """Auditor principal de governana."""

    def __init__(self, environment: str, base_path: Path):
        self.environment = environment
        self.base_path = base_path
        self.detector = EnvironmentDetector()
        self.pip_auditor = PIPAuditor()
        self.mapper = FileSystemMapper(base_path)
        self.cross_checker = CatalogCrossChecker(base_path)
        self.report_dir = (
            base_path.parent
            / "reports"
            / "governance"
            / datetime.now().strftime("%Y-%m-%d")
        )
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def run_audit(self, dry_run: bool = True) -> Dict[str, Any]:
        """Executa auditoria completa."""
        logger.info(
            f"Iniciando auditoria de governana para ambiente: {self.environment}"
        )

        # 1. Mapear arquivos
        logger.info("Mapeando arquivos do ambiente...")
        files = self.mapper.map_files()

        # 2. Auditar PIPs
        logger.info("Auditando dependncias PIP...")
        pip_packages = self.pip_auditor.get_installed_packages()
        pip_vulnerabilities = self.pip_auditor.audit_vulnerabilities()
        pip_dependency_tree = self.pip_auditor.get_dependency_tree()

        # 3. Cruzar com catlogos
        logger.info("Cruzando com catlogos existentes...")
        artifact_catalog = self.cross_checker.load_artifact_catalog()
        renaming_plan = self.cross_checker.load_renaming_plan()
        genealogy_graph = self.cross_checker.load_genealogy_graph()
        naming_check = self.cross_checker.check_naming_convention(files)

        # 4. Aplicar regras de governana
        logger.info("Aplicando 20 regras de governana de IA...")
        governance_compliance = self._check_governance_rules(files, pip_packages)

        # 5. Preparar resultados
        results = {
            "metadata": {
                "environment": self.environment,
                "audit_timestamp": datetime.now().isoformat(),
                "dry_run": dry_run,
                "base_path": str(self.base_path),
            },
            "file_system": {
                "total_files": len(files),
                "files_by_extension": self._count_by_extension(files),
                "naming_convention": naming_check,
            },
            "dependencies": {
                "pip_packages_count": len(pip_packages),
                "pip_packages": pip_packages[:20],  # Amostra
                "vulnerabilities": pip_vulnerabilities,
                "dependency_tree_available": bool(
                    pip_dependency_tree and "error" not in pip_dependency_tree
                ),
            },
            "catalogs": {
                "artifact_catalog_loaded": bool(artifact_catalog),
                "renaming_plan_loaded": bool(renaming_plan),
                "genealogy_graph_loaded": bool(genealogy_graph),
            },
            "governance_compliance": governance_compliance,
            "discrepancies": self._find_discrepancies(
                files, artifact_catalog, renaming_plan
            ),
        }

        # 6. Gerar relatrios (se no for dry_run)
        if not dry_run:
            self._generate_reports(results)

        return results

    def _count_by_extension(self, files: List[Dict[str, Any]]) -> Dict[str, int]:
        """Conta arquivos por extenso."""
        counts = {}
        for file in files:
            ext = file["extension"]
            counts[ext] = counts.get(ext, 0) + 1
        return counts

    def _check_governance_rules(
        self, files: List[Dict[str, Any]], pip_packages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aplica as 20 regras de governana."""
        compliance = {}

        # R04: Nomenclatura Padronizada
        nc_pattern = re.compile(r"^NC-[A-Z]+-[A-Z]+-\d{3}-.+\.\w+$")
        nc_files = [f for f in files if nc_pattern.match(f["name"])]
        compliance["R04"] = {
            "description": IA_GOVERNANCE_RULES["R04"],
            "status": len(nc_files) > 0,
            "details": f"{len(nc_files)} arquivos seguem padro NC-",
        }

        # R05: Segregao de Ambientes
        compliance["R05"] = {
            "description": IA_GOVERNANCE_RULES["R05"],
            "status": self.environment in ["original", "mirror"],
            "details": f"Ambiente detectado: {self.environment}",
        }

        # R11: Versionamento de Artefatos
        # Verificar se arquivos YAML de governana tm hash
        gov_yamls = [
            f
            for f in files
            if "NC-" in f["name"]
            and f["extension"] in [".yaml", ".yml"]
            and any(
                keyword in f["name"].lower()
                for keyword in ["atomic", "policy", "rules", "gov"]
            )
        ]
        has_hash_count = 0
        for yaml_file in gov_yamls[:5]:  # Amostra
            try:
                with open(Path(yaml_file["absolute_path"]), "r", encoding="utf-8") as f:
                    content = f.read()
                    if "hash:" in content or "sha256:" in content:
                        has_hash_count += 1
            except:
                pass

        compliance["R11"] = {
            "description": IA_GOVERNANCE_RULES["R11"],
            "status": has_hash_count > 0,
            "details": f"{has_hash_count} de {len(gov_yamls)} YAMLs de governana possuem hash",
        }

        # Extended rule checks
        # R01: Inventário de Ativos de IA
        artifact_catalog_path = (
            self.base_path.parent / "DIR-DOC-FR-001-docs-main" / "artifact_catalog.json"
        )
        mcp_inventory_path = (
            self.base_path.parent
            / "DIR-DOC-FR-001-docs-main"
            / "mcp_tools_inventory.json"
        )
        genealogy_graph_path = self.base_path.parent / "genealogy_graph.json"
        r01_artifacts_exist = (
            artifact_catalog_path.exists() and genealogy_graph_path.exists()
        )
        r01_details = f"artifact_catalog.json: {artifact_catalog_path.exists()}, mcp_tools_inventory.json: {mcp_inventory_path.exists()}, genealogy_graph.json: {genealogy_graph_path.exists()}"
        compliance["R01"] = {
            "description": IA_GOVERNANCE_RULES["R01"],
            "status": r01_artifacts_exist,
            "details": r01_details,
        }

        # R02: Política Formalizada
        naming_path = (
            self.base_path
            / "DIR-DOC-FR-001-docs-main"
            / "NC-NAM-FR-001-naming-convention.md"
        )
        atomic_locks_path = (
            self.base_path
            / "DIR-DOC-FR-001-docs-main"
            / "NC-SEC-FR-001-atomic-locks.yaml"
        )
        rules_policy_path = (
            self.base_path
            / "DIR-DOC-FR-001-docs-main"
            / "NC-CFG-FR-002-rules-policy.yaml"
        )
        governance_rules_path = (
            self.base_path
            / "DIR-DOC-FR-001-docs-main"
            / "NC-GOV-FR-003-ia-governance-rules.yaml"
        )
        r02_files_exist = (
            naming_path.exists()
            and atomic_locks_path.exists()
            and rules_policy_path.exists()
            and governance_rules_path.exists()
        )
        r02_details = f"NC-NAM-FR-001: {naming_path.exists()}, NC-SEC-FR-001: {atomic_locks_path.exists()}, NC-CFG-FR-002: {rules_policy_path.exists()}, NC-GOV-FR-003: {governance_rules_path.exists()}"
        compliance["R02"] = {
            "description": IA_GOVERNANCE_RULES["R02"],
            "status": r02_files_exist,
            "details": r02_details,
        }

        # R06: Identidade para Agentes
        handoff_dir = self.base_path / "DIR-DS-002-audit-logs"
        handoff_files = (
            list(handoff_dir.glob("NC-DS-*-handoff-*.yaml"))
            if handoff_dir.exists()
            else []
        )
        r06_status = handoff_dir.exists() and len(handoff_files) > 0
        compliance["R06"] = {
            "description": IA_GOVERNANCE_RULES["R06"],
            "status": r06_status,
            "details": f"Handoff directory exists: {handoff_dir.exists()}, handoff files: {len(handoff_files)}",
        }

        # R07: Privilégio Mínimo (PoLP)
        agent_policy_path = (
            self.base_path
            / "DIR-DOC-FR-001-docs-main"
            / "NC-CFG-FR-001-agent-policy-template.yaml"
        )
        compliance["R07"] = {
            "description": IA_GOVERNANCE_RULES["R07"],
            "status": agent_policy_path.exists(),
            "details": f"Agent policy template exists: {agent_policy_path.exists()}",
        }

        # R08: Atomic Locks (Path-Based) - already checked in R02
        compliance["R08"] = {
            "description": IA_GOVERNANCE_RULES["R08"],
            "status": atomic_locks_path.exists(),
            "details": f"Atomic locks file exists: {atomic_locks_path.exists()}",
        }

        # R09: Segregação de Zonas de Escrita
        # Check if rules policy contains write_zones key (simple check)
        write_zones_exist = False
        if rules_policy_path.exists():
            try:
                import yaml

                with open(rules_policy_path, "r", encoding="utf-8") as f:
                    policy = yaml.safe_load(f)
                    write_zones_exist = "write_zones" in policy
            except:
                pass
        compliance["R09"] = {
            "description": IA_GOVERNANCE_RULES["R09"],
            "status": write_zones_exist,
            "details": f"Write zones defined in policy: {write_zones_exist}",
        }

        # R10: Trilha de Auditoria Imutável
        audit_log_dir = self.base_path / "DIR-DS-002-audit-logs"
        compliance["R10"] = {
            "description": IA_GOVERNANCE_RULES["R10"],
            "status": audit_log_dir.exists(),
            "details": f"Audit log directory exists: {audit_log_dir.exists()}",
        }

        # R12: Handoffs Formais (same as R06)
        compliance["R12"] = {
            "description": IA_GOVERNANCE_RULES["R12"],
            "status": r06_status,
            "details": f"Handoff files: {len(handoff_files)}",
        }

        # R13: Checkpoints e Save Points
        checkpoint_tool_path = (
            self.base_path / "neocortex" / "mcp" / "tools" / "NC-TOOL-FR-022-session.py"
        )
        compliance["R13"] = {
            "description": IA_GOVERNANCE_RULES["R13"],
            "status": checkpoint_tool_path.exists(),
            "details": f"Checkpoint tool exists: {checkpoint_tool_path.exists()}",
        }

        # R14: STEP 0 (Validação Pré-Ação)
        sub_server_path = self.base_path / "neocortex" / "mcp" / "sub_server.py"
        mentor_step_exists = False
        if sub_server_path.exists():
            try:
                with open(sub_server_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    mentor_step_exists = "mentor_step_0" in content
            except:
                pass
        compliance["R14"] = {
            "description": IA_GOVERNANCE_RULES["R14"],
            "status": mentor_step_exists,
            "details": f"mentor_step_0 function exists: {mentor_step_exists}",
        }

        # R15: STEP -1 (Save Point)
        savepoint_tool_path = (
            self.base_path
            / "neocortex"
            / "mcp"
            / "tools"
            / "NC-TOOL-FR-031-savepoint.py"
        )
        compliance["R15"] = {
            "description": IA_GOVERNANCE_RULES["R15"],
            "status": savepoint_tool_path.exists(),
            "details": f"Save point tool exists: {savepoint_tool_path.exists()}",
        }

        # R18: Ciclo de Vida de Tickets
        tickets_dir = self.base_path / "DIR-DS-001-tickets"
        ticket_files = (
            list(tickets_dir.glob("NC-DS-*.yaml")) if tickets_dir.exists() else []
        )
        compliance["R18"] = {
            "description": IA_GOVERNANCE_RULES["R18"],
            "status": tickets_dir.exists() and len(ticket_files) > 0,
            "details": f"Tickets directory exists: {tickets_dir.exists()}, ticket files: {len(ticket_files)}",
        }

        # R19: Rotina de 4 Ciclos
        cycle_validation_path = (
            self.base_path
            / "DIR-DOC-FR-001-docs-main"
            / "NC-CYC-FR-001-4-cycle-validation.md"
        )
        compliance["R19"] = {
            "description": IA_GOVERNANCE_RULES["R19"],
            "status": cycle_validation_path.exists(),
            "details": f"Cycle validation document exists: {cycle_validation_path.exists()}",
        }

        # R20: Revisão e Arquivo de Artefatos
        archive_dir = self.base_path / "DIR-ARC-FR-001-archive-main"
        compliance["R20"] = {
            "description": IA_GOVERNANCE_RULES["R20"],
            "status": archive_dir.exists(),
            "details": f"Archive directory exists: {archive_dir.exists()}",
        }

        # MCP-specific checks
        mcp_server_path = self.base_path / "neocortex" / "mcp" / "server.py"
        mission_control_adapter_path = (
            self.base_path
            / "neocortex"
            / "core"
            / "adapters"
            / "NC-ADP-FR-001-mission-control.py"
        )
        compliance["MCP_EXTRA"] = {
            "description": "MCP & Mission Control Integration Health",
            "status": mcp_server_path.exists()
            and mission_control_adapter_path.exists(),
            "details": f"MCP server exists: {mcp_server_path.exists()}, Mission Control adapter exists: {mission_control_adapter_path.exists()}",
        }

        # Remaining rules without implementation (R03, R16, R17)
        for rule_id in ["R03", "R16", "R17"]:
            compliance[rule_id] = {
                "description": IA_GOVERNANCE_RULES[rule_id],
                "status": "pending_implementation",
                "details": "Verificao no implementada nesta verso",
            }

        return compliance

    def _find_discrepancies(
        self,
        files: List[Dict[str, Any]],
        artifact_catalog: Dict[str, Any],
        renaming_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Encontra discrepncias entre ambiente e catlogos."""
        discrepancies = {
            "files_not_in_catalog": [],
            "catalog_entries_not_found": [],
            "renaming_plan_mismatches": [],
        }

        # Verificar arquivos vs catlogo
        if artifact_catalog and "python_files" in artifact_catalog:
            catalog_paths = {
                item.get("path", "")
                for item in artifact_catalog.get("python_files", [])
            }
            catalog_paths.update(
                item.get("path", "") for item in artifact_catalog.get("yaml_files", [])
            )

            for file in files:
                rel_path = file["path"]
                if rel_path not in catalog_paths and file["extension"] in [
                    ".py",
                    ".yaml",
                    ".yml",
                ]:
                    discrepancies["files_not_in_catalog"].append(rel_path)

        # Verificar renaming plan
        if renaming_plan and isinstance(renaming_plan, dict):
            # Implementao bsica
            pass

        return discrepancies

    def _generate_reports(self, results: Dict[str, Any]):
        """Gera relatrios em Markdown e JSON."""
        # JSON report
        json_report = self.report_dir / "environment_snapshot.json"
        with open(json_report, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Relatrio JSON gerado: {json_report}")

        # Markdown report
        md_report = self.report_dir / "compliance_report.md"
        self._generate_markdown_report(results, md_report)
        logger.info(f"Relatrio Markdown gerado: {md_report}")

        # YAML discrepancies
        yaml_report = self.report_dir / "discrepancies.yaml"
        with open(yaml_report, "w", encoding="utf-8") as f:
            yaml.dump(
                results["discrepancies"],
                f,
                default_flow_style=False,
                allow_unicode=True,
            )
        logger.info(f"Discrepncias YAML geradas: {yaml_report}")

    def _generate_markdown_report(self, results: Dict[str, Any], output_path: Path):
        """Gera relatrio Markdown legvel."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Relatrio de Governana NeoCortex\n\n")
            f.write(
                f"**Data da Auditoria:** {results['metadata']['audit_timestamp']}\n"
            )
            f.write(f"**Ambiente:** {results['metadata']['environment']}\n")
            f.write(f"**Caminho Base:** {results['metadata']['base_path']}\n\n")

            f.write("## 1. Sistema de Arquivos\n")
            f.write(
                f"- **Total de arquivos:** {results['file_system']['total_files']}\n"
            )
            for ext, count in results["file_system"]["files_by_extension"].items():
                f.write(f"- **{ext}:** {count}\n")

            nc = results["file_system"]["naming_convention"]
            f.write(
                f"\n- **Conformidade NC-:** {nc['compliance_rate']:.1f}% ({nc['nc_files']}/{nc['total_files']})\n"
            )
            if nc["non_nc_files"]:
                f.write(f"- **Arquivos no conformes:** {len(nc['non_nc_files'])}\n")

            f.write("\n## 2. Dependncias PIP\n")
            f.write(
                f"- **Pacotes instalados:** {results['dependencies']['pip_packages_count']}\n"
            )
            if (
                "vulnerabilities" in results["dependencies"]
                and results["dependencies"]["vulnerabilities"]
            ):
                if "error" not in results["dependencies"]["vulnerabilities"]:
                    f.write("- **Vulnerabilidades:** Encontradas (ver JSON)\n")
                else:
                    f.write(
                        f"- **Vulnerabilidades:** {results['dependencies']['vulnerabilities']['error']}\n"
                    )

            f.write("\n## 3. Conformidade com Governana de IA\n")
            for rule_id, rule_info in results["governance_compliance"].items():
                status_icon = (
                    ""
                    if rule_info.get("status") == True
                    else ""
                    if rule_info.get("status") == False
                    else ""
                )
                f.write(f"### {rule_id}: {rule_info['description']}\n")
                f.write(f"{status_icon} **Status:** {rule_info['status']}\n")
                f.write(f"**Detalhes:** {rule_info.get('details', 'N/A')}\n\n")

            f.write("\n## 4. Discrepncias\n")
            disc = results["discrepancies"]
            f.write(
                f"- **Arquivos no no catlogo:** {len(disc['files_not_in_catalog'])}\n"
            )
            if disc["files_not_in_catalog"]:
                for file in disc["files_not_in_catalog"][:10]:
                    f.write(f"  - {file}\n")
                if len(disc["files_not_in_catalog"]) > 10:
                    f.write(
                        f"  - ... e mais {len(disc['files_not_in_catalog']) - 10} arquivos\n"
                    )

            f.write("\n## 5. Recomendaes\n")
            f.write("1. Executar auditoria regularmente (Ciclo 4 - Limpeza Semanal)\n")
            f.write("2. Corrigir arquivos que no seguem conveno NC-\n")
            f.write("3. Atualizar catlogo de artefatos com arquivos ausentes\n")
            f.write("4. Implementar verificaes completas para todas as 20 regras\n")


def main():
    parser = argparse.ArgumentParser(description="Auditor de Governana NeoCortex")
    parser.add_argument(
        "--environment",
        choices=["original", "mirror", "auto"],
        default="auto",
        help="Ambiente a auditar (padro: auto-detect)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa auditoria sem gerar relatrios (padro)",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Executa auditoria e gera relatrios"
    )
    parser.add_argument(
        "--compare-environments",
        action="store_true",
        help="Compara ambientes original e espelho",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Log detalhado")
    args = parser.parse_args()

    # Configurar logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Detectar ambiente
    if args.environment == "auto":
        environment = EnvironmentDetector.detect()
    else:
        environment = args.environment

    base_path = EnvironmentDetector.get_base_path(environment)
    if not base_path.exists():
        logger.error(f"Caminho base no encontrado: {base_path}")
        sys.exit(1)

    # Executar auditoria
    auditor = GovernanceAuditor(environment, base_path)
    dry_run = not args.execute  # Se --execute no for passado,  dry_run
    results = auditor.run_audit(dry_run=dry_run)

    # Exibir resumo
    print("\n" + "=" * 60)
    print("RESUMO DA AUDITORIA DE GOVERNANA")
    print("=" * 60)
    print(f"Ambiente: {environment}")
    print(f"Arquivos mapeados: {results['file_system']['total_files']}")
    print(f"Pacotes PIP: {results['dependencies']['pip_packages_count']}")

    nc = results["file_system"]["naming_convention"]
    print(f"Conformidade NC-: {nc['compliance_rate']:.1f}%")

    # Verificar vulnerabilidades
    vuln = results["dependencies"]["vulnerabilities"]
    if vuln and "error" not in vuln:
        if isinstance(vuln, dict) and "vulnerabilities" in vuln:
            print(f"Vulnerabilidades encontradas: {len(vuln['vulnerabilities'])}")
        else:
            print("Vulnerabilidades: Verificar relatrio")

    print(f"\nRelatrios gerados em: {auditor.report_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
