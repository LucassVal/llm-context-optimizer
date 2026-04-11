#!/usr/bin/env python3
"""
NeoCortex MCP Server

Servidor MCP (Model Context Protocol) que expoe as 10 ferramentas multi-acao
para integracao com IDEs (VS Code, Cursor, Antigravity, etc.)

Baseado no protocolo MCP da Anthropic (FastMCP).
"""

import asyncio
import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Tentar importar FastMCP, se nao estiver disponivel, usar modo de simulacao
try:
    from mcp.server import FastMCP, NotificationOptions

    FAST_MCP_AVAILABLE = True
except ImportError:
    FAST_MCP_AVAILABLE = False
    print("WARNING: FastMCP nao encontrado. Usando modo de simulacao.", file=sys.stderr)

# Configuracao de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constantes
PROJECT_ROOT = Path(__file__).parent.parent
CORTEX_PATH = (
    PROJECT_ROOT
    / "DIR-CORE-FR-001-core-central"
    / ".agents"
    / "rules"
    / "NC-CTX-FR-001-cortex-central.mdc"
)
LEDGER_PATH = (
    PROJECT_ROOT
    / "DIR-CORE-FR-001-core-central"
    / "NC-LED-FR-001-framework-ledger.json"
)
ARCHIVE_PATH = PROJECT_ROOT / "DIR-ARC-FR-001-archive-main"
BACKUP_PATH = PROJECT_ROOT / "DIR-BAK-FR-001-backup-main"
TEMPLATES_PATH = PROJECT_ROOT / "DIR-TMP-FR-001-templates-main"
DOCS_PATH = PROJECT_ROOT / "DIR-DOC-FR-001-docs-main"
SOURCE_PATH = PROJECT_ROOT / "DIR-SRC-FR-001-source-main"

# Inicializar servidor MCP
if FAST_MCP_AVAILABLE:
    mcp = FastMCP("neocortex")
else:
    # Simulacao para desenvolvimento sem FastMCP
    class MockMCP:
        def __init__(self, name, version="4.2-cortex"):
            self.name = name
            self.version = version
            self.tools = {}

        def tool(self, name=None):
            def decorator(func):
                tool_name = name or func.__name__
                self.tools[tool_name] = func
                return func

            return decorator

        def run(self):
            logger.info(
                f"MockMCP '{self.name}' v{self.version} rodando com {len(self.tools)} ferramentas"
            )
            print(
                json.dumps(
                    {
                        "serverInfo": {"name": self.name, "version": self.version},
                        "tools": list(self.tools.keys()),
                    }
                )
            )

    mcp = MockMCP("neocortex")

# ==================== FUNCOES AUXILIARES ====================


def read_cortex() -> str:
    """Le o conteudo do arquivo cortex."""
    try:
        with open(CORTEX_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def write_cortex(content: str) -> bool:
    """Escreve conteudo no arquivo cortex."""
    try:
        with open(CORTEX_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Erro ao escrever cortex: {e}")
        return False


def read_ledger() -> Dict[str, Any]:
    """Le e parseia o ledger JSON."""
    try:
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_ledger(data: Dict[str, Any]) -> bool:
    """Escreve dados no ledger JSON."""
    try:
        with open(LEDGER_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Erro ao escrever ledger: {e}")
        return False


def find_lobes() -> List[str]:
    """Encontra todos os arquivos lobe (.mdc) no diretorio de regras."""
    lobes_dir = PROJECT_ROOT / "DIR-CORE-FR-001-core-central" / ".agents" / "rules"
    if not lobes_dir.exists():
        return []

    return [f.name for f in lobes_dir.glob("*.mdc") if f.name != "00-cortex.mdc"]


def get_lobe_content(lobe_name: str) -> Optional[str]:
    """Obtem o conteudo de um lobe especifico."""
    lobe_path = (
        PROJECT_ROOT / "DIR-CORE-FR-001-core-central" / ".agents" / "rules" / lobe_name
    )
    if not lobe_path.exists():
        return None

    try:
        with open(lobe_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


# ==================== FERRAMENTAS MCP ====================


@mcp.tool(name="neocortex_cortex")
def tool_cortex(action: str, section: str = "") -> Dict[str, Any]:
    """
    Acesso ao cortex central.

    Actions:
    - get_full: Retorna o conteudo completo do cortex
    - get_section: Retorna uma secao especifica
    - get_aliases: Retorna todos os aliases definidos
    - get_workflows: Retorna os workflows definidos
    - validate_alias: Valida se um alias esta correto
    """
    cortex_content = read_cortex()

    if action == "get_full":
        return {"success": True, "content": cortex_content}

    elif action == "get_section":
        # Busca simples por secao no markdown
        lines = cortex_content.split("\n")
        in_section = False
        section_lines = []

        for line in lines:
            if line.strip().startswith(f"## {section}"):
                in_section = True
                continue
            elif line.strip().startswith("## ") and in_section:
                break

            if in_section:
                section_lines.append(line)

        return {
            "success": True,
            "section": section,
            "content": "\n".join(section_lines).strip(),
        }

    elif action == "get_aliases":
        # Extrai aliases da tabela Compact Encoding
        lines = cortex_content.split("\n")
        aliases = []
        in_table = False

        for line in lines:
            if "Compact Encoding" in line and "|" in line:
                in_table = True
                continue
            elif "## " in line and in_table:
                break

            if in_table and "|" in line and "$" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2:
                    aliases.append({"symbol": parts[0], "path": parts[1]})

        return {"success": True, "aliases": aliases}

    elif action == "get_workflows":
        # Extrai workflows da secao ## Workflows
        lines = cortex_content.split("\n")
        workflows = []
        current_workflow = None
        in_workflows_section = False
        collecting_description = False

        for i, line in enumerate(lines):
            if "##  Workflows" in line or "## Workflows" in line:
                in_workflows_section = True
                continue
            elif line.strip().startswith("## ") and in_workflows_section:
                # Nova secao dentro de workflows
                if "### " in line:
                    if current_workflow:
                        workflows.append(current_workflow)
                    current_workflow = {
                        "name": line.strip().replace("### ", "").strip(),
                        "description": [],
                        "steps": [],
                    }
                    collecting_description = True
                continue
            elif line.strip().startswith("#") and in_workflows_section:
                # Saiu da secao workflows
                break

            if in_workflows_section and current_workflow:
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith(">"):
                    # E um passo numerado
                    if line_stripped[0].isdigit() and ". " in line_stripped:
                        step_num = line_stripped.split(". ")[0]
                        step_text = (
                            line_stripped.split(". ", 1)[1]
                            if ". " in line_stripped
                            else line_stripped
                        )
                        current_workflow["steps"].append(
                            {"step": step_num, "description": step_text}
                        )
                    elif collecting_description and line_stripped:
                        # Descricao do workflow
                        if "description" not in current_workflow:
                            current_workflow["description"] = []
                        current_workflow["description"].append(line_stripped)

        # Adiciona ultimo workflow se existir
        if current_workflow:
            workflows.append(current_workflow)

        # Formata descricoes
        for wf in workflows:
            if isinstance(wf.get("description"), list):
                wf["description"] = " ".join(wf["description"])

        return {"success": True, "workflows": workflows, "count": len(workflows)}

    elif action == "validate_alias":
        return {
            "success": True,
            "valid": True,
            "message": "Alias validation not yet implemented",
        }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_lobes")
def tool_lobes(action: str, lobe_name: str = "") -> Dict[str, Any]:
    """
    Gerenciamento de lobos.

    Actions:
    - list_active: Lista todos os lobos disponiveis
    - get_content: Retorna o conteudo de um lobe especifico
    - get_checkpoint_tree: Extrai a arvore de checkpoints de um lobe
    - activate: Marca um lobe como ativo (simulado)
    - deactivate: Marca um lobe como inativo (simulado)
    """
    if action == "list_active":
        lobes = find_lobes()
        ledger = read_ledger()
        active_lobes = ledger.get("memory_cortex", {}).get("active_lobes", [])

        return {"success": True, "all_lobes": lobes, "active_lobes": active_lobes}

    elif action == "get_content":
        if not lobe_name:
            return {"success": False, "error": "lobe_name e obrigatorio"}

        content = get_lobe_content(lobe_name)
        if content is None:
            return {"success": False, "error": f"Lobe nao encontrado: {lobe_name}"}

        return {"success": True, "lobe_name": lobe_name, "content": content}

    elif action == "get_checkpoint_tree":
        if not lobe_name:
            return {"success": False, "error": "lobe_name e obrigatorio"}

        content = get_lobe_content(lobe_name)
        if content is None:
            return {"success": False, "error": f"Lobe nao encontrado: {lobe_name}"}

        # Extrai checkpoints do formato markdown
        checkpoints = []
        lines = content.split("\n")
        for line in lines:
            if "- [x]" in line or "- [ ]" in line:
                checkpoints.append(line.strip())

        return {"success": True, "lobe_name": lobe_name, "checkpoints": checkpoints}

    elif action in ["activate", "deactivate"]:
        # Atualiza o ledger com o lobe ativo/inativo
        ledger = read_ledger()
        memory_cortex = ledger.get("memory_cortex", {})
        active_lobes = memory_cortex.get("active_lobes", [])

        if action == "activate":
            if lobe_name not in active_lobes:
                active_lobes.append(lobe_name)
        else:  # deactivate
            if lobe_name in active_lobes:
                active_lobes.remove(lobe_name)

        memory_cortex["active_lobes"] = active_lobes
        ledger["memory_cortex"] = memory_cortex
        write_ledger(ledger)

        return {
            "success": True,
            "action": action,
            "lobe_name": lobe_name,
            "active_lobes": active_lobes,
        }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_checkpoint")
def tool_checkpoint(
    action: str, checkpoint_id: str = "", description: str = ""
) -> Dict[str, Any]:
    """
    Controle de checkpoints.

    Actions:
    - get_current: Retorna o checkpoint atual
    - set_current: Define um novo checkpoint atual
    - complete_task: Marca uma tarefa como completa
    - list_history: Lista o historico de checkpoints
    """
    ledger = read_ledger()
    memory_cortex = ledger.get("memory_cortex", {})
    synapses = memory_cortex.get("synapses", {})

    if action == "get_current":
        current = synapses.get("current_context", {})
        return {
            "success": True,
            "current_checkpoint": current.get("checkpoint_id", "Nenhum"),
            "current_lobe": current.get("lobe_id", "Nenhum"),
        }

    elif action == "set_current":
        if not checkpoint_id:
            return {"success": False, "error": "checkpoint_id e obrigatorio"}

        synapses["current_context"] = {
            "lobe_id": "00-cortex",  # Por padrao, usa o cortex
            "checkpoint_id": checkpoint_id,
        }

        # Adiciona ao indice global
        global_index = memory_cortex.get("global_checkpoint_index", {})
        checkpoints = global_index.get("checkpoints", [])
        if checkpoint_id not in checkpoints:
            checkpoints.append(checkpoint_id)
            global_index["checkpoints"] = checkpoints
            memory_cortex["global_checkpoint_index"] = global_index

        memory_cortex["synapses"] = synapses
        ledger["memory_cortex"] = memory_cortex

        # Atualiza timeline
        timeline = ledger.get("session_timeline", [])
        timeline.append(
            {
                "timestamp": "auto_generated",
                "event": "checkpoint_set",
                "checkpoint_id": checkpoint_id,
                "description": description or "Checkpoint definido via MCP",
            }
        )
        ledger["session_timeline"] = timeline

        write_ledger(ledger)

        return {
            "success": True,
            "checkpoint_id": checkpoint_id,
            "description": description,
        }

    elif action == "complete_task":
        # Marca uma tarefa como completa no action_queue
        action_queue = ledger.get("action_queue", {})
        pending = action_queue.get("pending", [])
        in_progress = action_queue.get("in_progress", [])
        completed = action_queue.get("completed", [])

        task_to_complete = checkpoint_id  # Usando checkpoint_id como nome da tarefa

        if task_to_complete in pending:
            pending.remove(task_to_complete)
        elif task_to_complete in in_progress:
            in_progress.remove(task_to_complete)
        else:
            return {
                "success": False,
                "error": f"Tarefa nao encontrada: {task_to_complete}",
            }

        completed.append(task_to_complete)
        action_queue.update(
            {"pending": pending, "in_progress": in_progress, "completed": completed}
        )
        ledger["action_queue"] = action_queue

        write_ledger(ledger)

        return {"success": True, "task": task_to_complete, "status": "completed"}

    elif action == "list_history":
        timeline = ledger.get("session_timeline", [])
        return {
            "success": True,
            "history": timeline[-10:],  # Ultimos 10 eventos
        }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_regression")
def tool_regression(
    action: str, error: str = "", attempt: str = "", lesson: str = ""
) -> Dict[str, Any]:
    """
    STEP 0 e buffer de regressao.

    Actions:
    - check: Verifica se ha regressoes similares
    - add_entry: Adiciona uma nova entrada ao buffer
    - list_all: Lista todas as entradas do buffer
    """
    ledger = read_ledger()
    hierarchical_validation = ledger.get("hierarchical_validation", {})
    regression_buffer = hierarchical_validation.get("regression_buffer", {})
    failed_attempts = regression_buffer.get("failed_attempts", [])

    if action == "check":
        if not error:
            return {"success": True, "similar_errors": [], "count": 0}

        # Verifica similaridade simples (contem a string de erro)
        similar = [
            entry
            for entry in failed_attempts
            if error.lower() in entry.get("error", "").lower()
        ]

        return {
            "success": True,
            "similar_errors": similar,
            "count": len(similar),
            "warning": len(similar) > 0,
        }

    elif action == "add_entry":
        if not error or not attempt or not lesson:
            return {
                "success": False,
                "error": "error, attempt e lesson sao obrigatorios",
            }

        new_entry = {
            "error": error,
            "attempt": attempt,
            "lesson": lesson,
            "timestamp": "auto_generated",
        }

        failed_attempts.append(new_entry)
        regression_buffer["failed_attempts"] = failed_attempts
        hierarchical_validation["regression_buffer"] = regression_buffer
        ledger["hierarchical_validation"] = hierarchical_validation

        write_ledger(ledger)

        return {
            "success": True,
            "entry": new_entry,
            "total_entries": len(failed_attempts),
        }

    elif action == "list_all":
        return {
            "success": True,
            "entries": failed_attempts,
            "total": len(failed_attempts),
        }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_ledger")
def tool_ledger(action: str, metric: str = "") -> Dict[str, Any]:
    """
    Acesso ao ledger JSON.

    Actions:
    - get_metrics: Retorna metricas da sessao
    - get_atomic_locks: Retorna os atomic locks
    - get_dependency_graph: Retorna o grafo de dependencias
    - prune_context: Executa poda de contexto
    """
    ledger = read_ledger()

    if action == "get_metrics":
        session_metrics = ledger.get("session_metrics", {})
        return {"success": True, "metrics": session_metrics}

    elif action == "get_atomic_locks":
        granular_state = ledger.get("granular_state_management", {})
        atomic_locks = granular_state.get("atomic_locks", {})
        return {"success": True, "atomic_locks": atomic_locks}

    elif action == "get_dependency_graph":
        # Simulacao - retorna estrutura vazia
        return {
            "success": True,
            "dependency_graph": {
                "active_module": "",
                "first_degree": [],
                "second_degree": [],
            },
        }

    elif action == "prune_context":
        # Simulacao de poda de contexto
        memory_temp = ledger.get("memory_temperature", {})
        hot_context = memory_temp.get("hot_context", {})
        interactions = hot_context.get("interactions", [])

        if len(interactions) > 5:
            # Move os mais antigos para cold storage
            to_move = interactions[:-5]
            remaining = interactions[-5:]

            cold_storage = memory_temp.get("cold_storage", {})
            archived = cold_storage.get("archived_interactions", [])
            archived.extend(to_move)

            hot_context["interactions"] = remaining
            cold_storage["archived_interactions"] = archived
            memory_temp.update(
                {"hot_context": hot_context, "cold_storage": cold_storage}
            )

            # Log da compactacao
            compaction_log = memory_temp.get("compaction_log", {})
            entries = compaction_log.get("entries", [])
            entries.append(
                {
                    "timestamp": "auto_generated",
                    "moved_count": len(to_move),
                    "remaining_count": len(remaining),
                }
            )
            compaction_log["entries"] = entries
            memory_temp["compaction_log"] = compaction_log

            ledger["memory_temperature"] = memory_temp
            write_ledger(ledger)

            return {
                "success": True,
                "moved_to_cold": len(to_move),
                "remaining_in_hot": len(remaining),
                "message": f"Contexto podado: {len(to_move)} interacoes movidas para cold storage",
            }
        else:
            return {
                "success": True,
                "message": "Nenhuma poda necessaria (hot_context  5 interacoes)",
            }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_benchmark")
def tool_benchmark(action: str, benchmark_type: str = "") -> Dict[str, Any]:
    """
    Execucao de benchmarks.

    Actions:
    - run_drift: Executa benchmark Drift Exhaustion
    - run_titanomachy: Executa benchmark Titanomachy
    - get_last_report: Retorna o ultimo relatorio de benchmark
    """
    # Implementacao simulada - em producao, chamaria os scripts reais
    if action == "run_drift":
        return {
            "success": True,
            "benchmark": "drift_exhaustion",
            "status": "simulated",
            "message": "Benchmark Drift Exhaustion simulado. Em producao, executaria benchmark_master_suite.py",
        }

    elif action == "run_titanomachy":
        return {
            "success": True,
            "benchmark": "titanomachy",
            "status": "simulated",
            "message": "Benchmark Titanomachy simulado. Em producao, executaria com 100+ tarefas.",
        }

    elif action == "get_last_report":
        return {
            "success": True,
            "last_report": {
                "timestamp": "2026-04-09",
                "benchmark": "simulated",
                "results": {
                    "token_savings": "96.6%",
                    "context_drift": "0 errors",
                    "session_continuity": "100%",
                },
            },
        }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_agent")
def tool_agent(action: str, agent_id: str = "", role: str = "") -> Dict[str, Any]:
    """
    Orquestracao de agentes efemeros.

    Actions:
    - spawn: Cria um novo agente efemero
    - heartbeat: Verifica status do agente
    - consume: Consome resultados do agente
    - list_ephemeral: Lista agentes efemeros ativos
    """
    ledger = read_ledger()
    memory_cortex = ledger.get("memory_cortex", {})
    active_agents = memory_cortex.get("active_agents", [])

    if action == "spawn":
        if not role:
            return {"success": False, "error": "role e obrigatorio"}

        new_agent_id = f"ag-{len(active_agents) + 1:03d}"
        new_agent = {
            "agent_id": new_agent_id,
            "role": role,
            "status": "running",
            "created_at": "auto_generated",
            "lobe_ref": f"ephemeral/{new_agent_id}-{role.replace(' ', '-')}.mdc",
            "parent_task": "Tarefa criada via MCP",
        }

        active_agents.append(new_agent)
        memory_cortex["active_agents"] = active_agents
        ledger["memory_cortex"] = memory_cortex
        write_ledger(ledger)

        return {
            "success": True,
            "agent": new_agent,
            "message": f"Agente {new_agent_id} criado com role: {role}",
        }

    elif action == "list_ephemeral":
        return {
            "success": True,
            "active_agents": active_agents,
            "count": len(active_agents),
        }

    elif action == "heartbeat":
        if not agent_id:
            return {"success": False, "error": "agent_id e obrigatorio"}

        agent = next((a for a in active_agents if a.get("agent_id") == agent_id), None)
        if not agent:
            return {"success": False, "error": f"Agente nao encontrado: {agent_id}"}

        return {
            "success": True,
            "agent_id": agent_id,
            "status": agent.get("status", "unknown"),
            "last_heartbeat": "auto_generated",
        }

    elif action == "consume":
        if not agent_id:
            return {"success": False, "error": "agent_id e obrigatorio"}

        # Simulacao: remove o agente apos consumo
        agent = next((a for a in active_agents if a.get("agent_id") == agent_id), None)
        if not agent:
            return {"success": False, "error": f"Agente nao encontrado: {agent_id}"}

        # Move para archive
        agent_archive = memory_cortex.get("agent_archive", {})
        completed = agent_archive.get("completed", [])
        completed.append(agent)
        agent_archive["completed"] = completed
        memory_cortex["agent_archive"] = agent_archive

        # Remove dos ativos
        active_agents = [a for a in active_agents if a.get("agent_id") != agent_id]
        memory_cortex["active_agents"] = active_agents
        ledger["memory_cortex"] = memory_cortex

        write_ledger(ledger)

        return {
            "success": True,
            "agent_id": agent_id,
            "consumed": True,
            "message": f"Agente {agent_id} arquivado apos consumo",
        }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_init")
def tool_init(action: str, project_name: str = "") -> Dict[str, Any]:
    """
    Inicializacao de projetos.

    Actions:
    - scan_project: Analisa a estrutura do projeto atual
    - generate_cortex: Gera um cortex inicial
    - generate_lobe: Gera um lobe inicial para um modulo
    """
    if action == "scan_project":
        # Simulacao de analise de projeto
        return {
            "success": True,
            "project_structure": {
                "detected_stack": "python",
                "main_files": ["README.md", "requirements.txt"],
                "suggested_aliases": [
                    {"symbol": "$main", "path": "main.py"},
                    {"symbol": "@src", "path": "src/"},
                    {"symbol": "!run", "command": "python main.py"},
                ],
            },
        }

    elif action == "generate_cortex":
        if not project_name:
            return {"success": False, "error": "project_name e obrigatorio"}

        # Template basico de cortex
        cortex_template = f"""---
alwaysApply: true
description: "Central Cortex  {project_name}. NeoCortex v4.2-Cortex."
---

#  Cortex: {project_name}

##  STEP 0  REGRESSION + GOAL CHECK
> 1. Read Regression Buffer
> 2. If similar to error  ADVISE
> 3. Reaffirm goal
> 4. Confirm scope

##  Workspace Map
| File/Dir | Alias | Purpose |
|----------|-------|---------|
| main.py | $main | Entry point |

##  Compact Encoding
| $ = file | @ = directory | ! = command |
|----------|---------------|-------------|
| $main | @src | !run |

##  Current State
- **Version:** NeoCortex v4.2-Cortex
- **Active Phase:** Initial Setup
- **Last Checkpoint:** CP-INIT  Cortex generated 
"""

        return {
            "success": True,
            "project_name": project_name,
            "cortex_generated": True,
            "template": cortex_template,
        }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_config")
def tool_config(action: str, key: str = "", value: str = "") -> Dict[str, Any]:
    """
    Configuracao do sistema.

    Actions:
    - get_config: Retorna configuracao atual
    - set_model: Define o modelo LLM a ser usado
    - list_models: Lista modelos disponiveis
    """
    if action == "get_config":
        ledger = read_ledger()
        agent_session = ledger.get("agent_session", {})
        return {
            "success": True,
            "config": {
                "model": agent_session.get("model_id", "unknown"),
                "mode": agent_session.get("mode", "single_agent"),
                "platform": agent_session.get("platform", "unknown"),
            },
        }

    elif action == "set_model":
        if not key:
            return {"success": False, "error": "key (model name) e obrigatorio"}

        ledger = read_ledger()
        agent_session = ledger.get("agent_session", {})
        agent_session["model_id"] = key
        ledger["agent_session"] = agent_session
        write_ledger(ledger)

        return {
            "success": True,
            "model_set": key,
            "message": f"Modelo definido para: {key}",
        }

    elif action == "list_models":
        return {
            "success": True,
            "models": [
                "deepseek-reasoner",
                "gpt-4",
                "claude-3.5-sonnet",
                "llama-3.1",
                "qwen2.5",
            ],
        }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_export")
def tool_export(action: str, format: str = "markdown") -> Dict[str, Any]:
    """
    Exportacao de dados.

    Actions:
    - to_markdown: Exporta estado para markdown
    - to_json: Exporta estado para JSON
    - to_graph: Exporta para formato de grafo
    """
    ledger = read_ledger()

    if action == "to_markdown":
        # Exportacao basica para markdown
        markdown = f"""# NeoCortex Export - {ledger.get("project_identity", {}).get("name", "Unknown")}

## Session Metrics
- Total Interactions: {ledger.get("session_metrics", {}).get("total_interactions", 0)}
- Files Created: {ledger.get("session_metrics", {}).get("files_created", 0)}
- Problems Solved: {ledger.get("session_metrics", {}).get("problems_solved", 0)}

## Active Lobes
{chr(10).join(f"- {lobe}" for lobe in ledger.get("memory_cortex", {}).get("active_lobes", []))}

## Recent Timeline
{chr(10).join(f"- {event.get('event', '')}: {event.get('description', '')}" for event in ledger.get("session_timeline", [])[-5:])}
"""

        return {"success": True, "format": "markdown", "content": markdown}

    elif action == "to_json":
        return {
            "success": True,
            "format": "json",
            "content": json.dumps(ledger, indent=2, ensure_ascii=False),
        }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_manifest")
def tool_manifest(action: str, target: str = "", metadata: str = "") -> Dict[str, Any]:
    """
    Gerenciamento de manifestos (indices leves de lobos/cortex).

    Actions:
    - generate: Gera um manifesto para um lobe ou cortex
    - update: Atualiza metadados de um manifesto existente
    - query: Consulta manifestos por tags, dominio ou entidades
    """
    ledger = read_ledger()
    memory_cortex = ledger.get("memory_cortex", {})

    # Inicializa estrutura de manifestos se nao existir
    if "manifests" not in memory_cortex:
        memory_cortex["manifests"] = {}
        ledger["memory_cortex"] = memory_cortex

    manifests = memory_cortex["manifests"]

    if action == "generate":
        if not target:
            return {
                "success": False,
                "error": "target e obrigatorio (cortex ou lobe name)",
            }

        # Verifica se o target existe
        if target == "cortex":
            content_source = read_cortex()
            manifest_id = "cortex"
        else:
            # Assume que e um lobe
            content = get_lobe_content(target)
            if content is None:
                return {"success": False, "error": f"Lobe nao encontrado: {target}"}
            content_source = content
            manifest_id = target

        # Gera manifesto basico
        new_manifest = {
            "id": manifest_id,
            "type": "cortex" if target == "cortex" else "lobe",
            "created_at": "auto_generated",
            "last_accessed": "auto_generated",
            "metadata": {
                "line_count": len(content_source.split("\n")),
                "has_checkpoints": "- [x]" in content_source
                or "- [ ]" in content_source,
                "has_aliases": "$" in content_source,
            },
            "tags": [],
            "entities": [],
        }

        # Extrai tags automaticas (secoes ##)
        lines = content_source.split("\n")
        for line in lines:
            if line.strip().startswith("## "):
                tag = line.strip()[3:].strip()
                if tag and tag not in new_manifest["tags"]:
                    new_manifest["tags"].append(tag)

        manifests[manifest_id] = new_manifest
        memory_cortex["manifests"] = manifests
        ledger["memory_cortex"] = memory_cortex
        write_ledger(ledger)

        return {
            "success": True,
            "manifest": new_manifest,
            "message": f"Manifesto gerado para {target}",
        }

    elif action == "update":
        if not target:
            return {"success": False, "error": "target e obrigatorio (manifest ID)"}

        if target not in manifests:
            return {"success": False, "error": f"Manifesto nao encontrado: {target}"}

        # Atualiza metadados
        manifest = manifests[target]
        manifest["last_accessed"] = "auto_generated"

        # Parse metadata JSON se fornecido
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
                manifest["metadata"].update(metadata_dict)
            except json.JSONDecodeError:
                return {"success": False, "error": "metadata deve ser JSON valido"}

        manifests[target] = manifest
        memory_cortex["manifests"] = manifests
        ledger["memory_cortex"] = memory_cortex
        write_ledger(ledger)

        return {
            "success": True,
            "manifest": manifest,
            "message": f"Manifesto {target} atualizado",
        }

    elif action == "query":
        query_results = []

        for manifest_id, manifest in manifests.items():
            # Filtro simples por tags (se metadata contem tags)
            if metadata:
                # metadata pode ser tag ou termo de busca
                search_term = metadata.lower()
                matches = False

                # Busca em tags
                for tag in manifest.get("tags", []):
                    if search_term in tag.lower():
                        matches = True
                        break

                # Busca em entities
                for entity in manifest.get("entities", []):
                    if search_term in str(entity).lower():
                        matches = True
                        break

                # Busca no tipo
                if search_term in manifest.get("type", "").lower():
                    matches = True

                if not matches:
                    continue

            query_results.append(manifest)

        return {
            "success": True,
            "query": metadata or "all",
            "results": query_results,
            "count": len(query_results),
        }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_kg")
def tool_kg(
    action: str,
    entity: str = "",
    relation: str = "",
    target: str = "",
    metadata: str = "",
) -> Dict[str, Any]:
    """
    Mini Knowledge Graph  grafo semantico local (evolucao do Compact Encoding).

    Actions:
    - add_entity: Adiciona uma entidade ao Mini-KG
    - add_relation: Adiciona uma relacao entre entidades
    - query_relations: Retorna todas as relacoes de uma entidade
    - find_similar: Encontra entidades/lobos com caracteristicas semelhantes
    - visualize: Exporta o grafo em formato DOT ou estrutura simplificada
    """
    ledger = read_ledger()
    memory_cortex = ledger.get("memory_cortex", {})

    # Inicializa estrutura do KG se nao existir
    if "knowledge_graph" not in memory_cortex:
        memory_cortex["knowledge_graph"] = {
            "entities": {},
            "relations": [],
            "entity_types": [
                "lobe",
                "cortex",
                "file",
                "directory",
                "command",
                "pattern",
                "concept",
            ],
        }
        ledger["memory_cortex"] = memory_cortex

    kg = memory_cortex["knowledge_graph"]
    entities = kg.get("entities", {})
    relations = kg.get("relations", [])

    if action == "add_entity":
        if not entity:
            return {"success": False, "error": "entity e obrigatorio"}

        # Verifica se a entidade ja existe
        if entity in entities:
            return {
                "success": True,
                "entity": entity,
                "message": f"Entidade '{entity}' ja existe no KG",
                "existing": True,
            }

        # Cria nova entidade
        new_entity = {
            "id": entity,
            "type": metadata if metadata else "concept",
            "created_at": "auto_generated",
            "last_accessed": "auto_generated",
            "relations_count": 0,
            "metadata": {},
        }

        entities[entity] = new_entity
        kg["entities"] = entities
        memory_cortex["knowledge_graph"] = kg
        ledger["memory_cortex"] = memory_cortex
        write_ledger(ledger)

        return {
            "success": True,
            "entity": new_entity,
            "message": f"Entidade '{entity}' adicionada ao KG",
        }

    elif action == "add_relation":
        if not entity or not relation or not target:
            return {
                "success": False,
                "error": "entity, relation e target sao obrigatorios",
            }

        # Verifica se entidades existem
        if entity not in entities:
            return {
                "success": False,
                "error": f"Entidade fonte nao encontrada: {entity}",
            }
        if target not in entities:
            return {
                "success": False,
                "error": f"Entidade alvo nao encontrada: {target}",
            }

        # Cria nova relacao
        new_relation = {
            "source": entity,
            "relation": relation,
            "target": target,
            "created_at": "auto_generated",
            "metadata": json.loads(metadata) if metadata else {},
        }

        # Adiciona a lista de relacoes
        relations.append(new_relation)

        # Atualiza contadores nas entidades
        entities[entity]["relations_count"] = (
            entities[entity].get("relations_count", 0) + 1
        )
        entities[target]["relations_count"] = (
            entities[target].get("relations_count", 0) + 1
        )

        kg["relations"] = relations
        kg["entities"] = entities
        memory_cortex["knowledge_graph"] = kg
        ledger["memory_cortex"] = memory_cortex
        write_ledger(ledger)

        return {
            "success": True,
            "relation": new_relation,
            "message": f"Relacao '{entity}  {relation}  {target}' adicionada ao KG",
        }

    elif action == "query_relations":
        if not entity:
            return {"success": False, "error": "entity e obrigatorio"}

        if entity not in entities:
            return {"success": False, "error": f"Entidade nao encontrada: {entity}"}

        # Encontra todas as relacoes envolvendo a entidade
        entity_relations = []
        for rel in relations:
            if rel["source"] == entity or rel["target"] == entity:
                entity_relations.append(rel)

        # Classifica por tipo de relacao
        outgoing = [r for r in entity_relations if r["source"] == entity]
        incoming = [r for r in entity_relations if r["target"] == entity]

        return {
            "success": True,
            "entity": entity,
            "entity_info": entities[entity],
            "outgoing_relations": outgoing,
            "incoming_relations": incoming,
            "total_relations": len(entity_relations),
        }

    elif action == "find_similar":
        if not entity:
            # Se nenhuma entidade for fornecida, retorna entidades mais conectadas
            sorted_entities = sorted(
                entities.items(),
                key=lambda x: x[1].get("relations_count", 0),
                reverse=True,
            )
            top_entities = [{"id": e[0], **e[1]} for e in sorted_entities[:5]]

            return {
                "success": True,
                "similar_to": "none (most connected entities)",
                "results": top_entities,
                "count": len(top_entities),
            }

        if entity not in entities:
            return {"success": False, "error": f"Entidade nao encontrada: {entity}"}

        # Encontra entidades relacionadas (primeiro grau)
        related_entities = set()
        for rel in relations:
            if rel["source"] == entity:
                related_entities.add(rel["target"])
            elif rel["target"] == entity:
                related_entities.add(rel["source"])

        # Converte para lista com informacoes
        similar = []
        for ent_id in related_entities:
            if ent_id in entities:
                similar.append({"id": ent_id, **entities[ent_id]})

        return {
            "success": True,
            "similar_to": entity,
            "results": similar,
            "count": len(similar),
        }

    elif action == "visualize":
        # Gera representacao DOT simples do grafo
        dot_lines = ["digraph NeoCortexKG {"]
        dot_lines.append("  rankdir=LR;")
        dot_lines.append("  node [shape=box, style=filled, fillcolor=lightblue];")

        # Adiciona nos (entidades)
        for ent_id, ent_data in entities.items():
            label = f"{ent_id}\\n({ent_data.get('type', 'concept')})"
            dot_lines.append(f'  "{ent_id}" [label="{label}"];')

        # Adiciona arestas (relacoes)
        for rel in relations:
            dot_lines.append(
                f'  "{rel["source"]}" -> "{rel["target"]}" [label="{rel["relation"]}"];'
            )

        dot_lines.append("}")

        dot_content = "\n".join(dot_lines)

        # Retorna tambem estrutura JSON para analise
        return {
            "success": True,
            "format": "dot",
            "dot_content": dot_content,
            "stats": {
                "total_entities": len(entities),
                "total_relations": len(relations),
                "most_connected": max(
                    [(e, d.get("relations_count", 0)) for e, d in entities.items()],
                    key=lambda x: x[1],
                    default=("none", 0),
                )[0],
            },
            "message": "Grafo KG exportado em formato DOT. Use Graphviz para visualizar.",
        }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_consolidation")
def tool_consolidation(
    action: str,
    session_id: str = "",
    summary: str = "",
    target: str = "",
    metadata: str = "",
) -> Dict[str, Any]:
    """
    Consolidacao Semantica  transforma experiencia efemera em regras permanentes.

    Actions:
    - summarize_session: Resume uma sessao em regras concisas
    - merge_learnings: Combina aprendizados de multiplos agentes
    - promote_to_rule: Promove entrada do Regression Buffer a regra permanente
    """
    ledger = read_ledger()
    memory_cortex = ledger.get("memory_cortex", {})

    # Inicializa estruturas de consolidacao se nao existirem
    if "consolidation_sessions" not in memory_cortex:
        memory_cortex["consolidation_sessions"] = []
        ledger["memory_cortex"] = memory_cortex

    consolidation_sessions = memory_cortex.get("consolidation_sessions", [])

    if action == "summarize_session":
        if not session_id:
            return {"success": False, "error": "session_id e obrigatorio"}

        # Cria resumo da sessao
        new_session = {
            "id": session_id,
            "summary": summary if summary else "Sessao consolidada automaticamente",
            "created_at": "auto_generated",
            "metadata": json.loads(metadata) if metadata else {},
            "status": "summarized",
        }

        # Adiciona a lista de sessoes
        consolidation_sessions.append(new_session)
        memory_cortex["consolidation_sessions"] = consolidation_sessions
        ledger["memory_cortex"] = memory_cortex
        write_ledger(ledger)

        return {
            "success": True,
            "session": new_session,
            "message": f"Sessao '{session_id}' resumida e armazenada",
        }

    elif action == "merge_learnings":
        # Busca sessoes com status 'summarized'
        summarized = [
            s for s in consolidation_sessions if s.get("status") == "summarized"
        ]

        if len(summarized) < 2:
            return {
                "success": False,
                "error": "Necessario pelo menos 2 sessoes resumidas para merge",
            }

        # Merge simples: combina summaries
        combined_summary = "\n".join([s.get("summary", "") for s in summarized])
        merged_id = f"merged_{len(summarized)}_sessions"

        merged_session = {
            "id": merged_id,
            "summary": combined_summary,
            "created_at": "auto_generated",
            "source_sessions": [s["id"] for s in summarized],
            "status": "merged",
        }

        consolidation_sessions.append(merged_session)
        memory_cortex["consolidation_sessions"] = consolidation_sessions
        ledger["memory_cortex"] = memory_cortex
        write_ledger(ledger)

        return {
            "success": True,
            "merged_session": merged_session,
            "message": f"Aprendizados de {len(summarized)} sessoes mesclados",
        }

    elif action == "promote_to_rule":
        # Acessa regression buffer
        regression_buffer = ledger.get("hierarchical_validation", {}).get(
            "regression_buffer", {}
        )
        failed_attempts = regression_buffer.get("failed_attempts", [])

        if not target and not failed_attempts:
            return {
                "success": False,
                "error": "Nenhuma entrada no Regression Buffer para promover",
            }

        # Se target nao especificado, usa a primeira entrada
        if not target:
            target_entry = failed_attempts[0] if failed_attempts else None
        else:
            # Tenta encontrar por indice ou ID
            try:
                idx = int(target)
                target_entry = (
                    failed_attempts[idx] if idx < len(failed_attempts) else None
                )
            except ValueError:
                # Procura por ID
                target_entry = next(
                    (e for e in failed_attempts if e.get("id") == target), None
                )

        if not target_entry:
            return {"success": False, "error": f"Entrada nao encontrada: {target}"}

        # Le o cortex atual
        cortex_content = read_cortex()
        if not cortex_content:
            return {"success": False, "error": "Cortex nao encontrado ou vazio"}

        # Extrai regra do entry (simplificado)
        rule_text = target_entry.get("error", target_entry.get("description", ""))
        if not rule_text:
            rule_text = f"Regra promovida do Regression Buffer: {target_entry}"

        # Adiciona regra ao cortex (apenda no final)
        new_rule = f"\n\n##  Regra Promovida (auto)\n\n{rule_text}\n"
        updated_cortex = cortex_content + new_rule

        # Escreve cortex atualizado
        if write_cortex(updated_cortex):
            # Marca entry como promoted no regression buffer
            target_entry["promoted"] = True
            target_entry["promoted_at"] = "auto_generated"
            regression_buffer["failed_attempts"] = failed_attempts
            ledger["hierarchical_validation"]["regression_buffer"] = regression_buffer
            write_ledger(ledger)

            return {
                "success": True,
                "rule_added": new_rule,
                "message": "Regra promovida para o cortex com sucesso",
            }
        else:
            return {"success": False, "error": "Falha ao escrever cortex atualizado"}

    return {"success": False, "error": f"Acao desconhecida: {action}"}


@mcp.tool(name="neocortex_akl")
def tool_akl(
    action: str,
    target: str = "",
    metadata: str = "",
) -> Dict[str, Any]:
    """
    Adaptive Knowledge Lifecycle  gerencia relevancia do conhecimento.

    Actions:
    - assess_importance: Avalia importancia de regras com base no uso
    - decay_knowledge: Aplica decaimento a regras nao utilizadas
    - suggest_cleanup: Lista regras candidatas a arquivamento
    """
    ledger = read_ledger()
    memory_cortex = ledger.get("memory_cortex", {})

    # Inicializa metricas AKL se nao existirem
    if "akl_metrics" not in memory_cortex:
        memory_cortex["akl_metrics"] = {}
        ledger["memory_cortex"] = memory_cortex

    akl_metrics = memory_cortex.get("akl_metrics", {})

    if action == "assess_importance":
        if not target:
            # Avalia importancia de todas as regras com metricas existentes
            important_rules = []
            for rule_id, metrics in akl_metrics.items():
                importance = metrics.get("access_count", 0) * 10  # Peso simples
                important_rules.append(
                    {
                        "rule_id": rule_id,
                        "importance_score": importance,
                        "access_count": metrics.get("access_count", 0),
                        "last_accessed": metrics.get("last_accessed", "never"),
                    }
                )

            # Ordena por importancia decrescente
            important_rules.sort(key=lambda x: x["importance_score"], reverse=True)

            return {
                "success": True,
                "assessment": important_rules,
                "message": f"Avaliadas {len(important_rules)} regras",
            }

        # Avalia uma regra especifica
        if target not in akl_metrics:
            # Cria entrada inicial
            akl_metrics[target] = {
                "access_count": 0,
                "last_accessed": "never",
                "importance_score": 0,
                "created_at": "auto_generated",
            }

        metrics = akl_metrics[target]
        # Incrementa contador de acesso (simulacao)
        metrics["access_count"] = metrics.get("access_count", 0) + 1
        metrics["last_accessed"] = "auto_generated"
        metrics["importance_score"] = metrics["access_count"] * 10

        akl_metrics[target] = metrics
        memory_cortex["akl_metrics"] = akl_metrics
        ledger["memory_cortex"] = memory_cortex
        write_ledger(ledger)

        return {
            "success": True,
            "rule_id": target,
            "importance_score": metrics["importance_score"],
            "access_count": metrics["access_count"],
            "message": f"Importancia da regra '{target}' avaliada",
        }

    elif action == "decay_knowledge":
        # Aplica decaimento a todas as regras (simulacao)
        decayed_rules = []
        for rule_id, metrics in akl_metrics.items():
            # Reduz score baseado na inatividade (simplificado)
            old_score = metrics.get("importance_score", 0)
            new_score = max(0, old_score - 5)  # Decaimento fixo
            metrics["importance_score"] = new_score
            akl_metrics[rule_id] = metrics

            if new_score < old_score:
                decayed_rules.append(
                    {
                        "rule_id": rule_id,
                        "old_score": old_score,
                        "new_score": new_score,
                    }
                )

        memory_cortex["akl_metrics"] = akl_metrics
        ledger["memory_cortex"] = memory_cortex
        write_ledger(ledger)

        return {
            "success": True,
            "decayed_rules": decayed_rules,
            "count": len(decayed_rules),
            "message": f"Decaimento aplicado a {len(decayed_rules)} regras",
        }

    elif action == "suggest_cleanup":
        # Sugere regras com baixa importancia para arquivamento
        low_importance_threshold = 20  # Limite arbitrario
        candidates = []

        for rule_id, metrics in akl_metrics.items():
            score = metrics.get("importance_score", 0)
            if score < low_importance_threshold:
                candidates.append(
                    {
                        "rule_id": rule_id,
                        "importance_score": score,
                        "access_count": metrics.get("access_count", 0),
                        "last_accessed": metrics.get("last_accessed", "never"),
                        "suggestion": "archive",
                    }
                )

        # Ordena por menor importancia
        candidates.sort(key=lambda x: x["importance_score"])

        return {
            "success": True,
            "candidates": candidates,
            "count": len(candidates),
            "threshold": low_importance_threshold,
            "message": f"{len(candidates)} regras candidatas a arquivamento",
        }

    return {"success": False, "error": f"Acao desconhecida: {action}"}


# ==================== MAIN ====================


async def main_async():
    """Funcao principal assincrona do servidor MCP."""
    logger.info("Iniciando NeoCortex MCP Server v4.2-cortex")
    logger.info(f"Cortex path: {CORTEX_PATH}")
    logger.info(f"Ledger path: {LEDGER_PATH}")

    if FAST_MCP_AVAILABLE:
        # Executa o servidor FastMCP
        await mcp.run()
    else:
        # Modo de simulacao
        mcp.run()

        # Loop simples para testes
        print("\n=== Modo Simulacao ===")
        print("Ferramentas disponiveis:")
        for tool_name, tool_func in mcp.tools.items():
            print(f"  - {tool_name}")

        print("\nExemplo de uso via CLI:")
        print("  python neocortex_cli.py call neocortex_cortex get_full")
        print("  python neocortex_cli.py call neocortex_checkpoint get_current")


def main():
    """Wrapper sincrono para main_async."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuario")
    except Exception as e:
        logger.error(f"Erro no servidor: {e}")
        raise


if __name__ == "__main__":
    main()
