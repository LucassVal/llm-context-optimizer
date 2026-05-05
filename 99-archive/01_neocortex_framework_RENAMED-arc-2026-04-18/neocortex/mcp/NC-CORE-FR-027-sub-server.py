"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["sub", "server"]
hash: "auto-generated"
---"""
#!/usr/bin/env python3
"""
Sub-MCP Server for NeoCortex Framework

Script para iniciar um sub-MCP server isolado para um Lobo especfico.
Uso: python -m neocortex.mcp.sub_server --port 11435 --lobe-dir "lobes/courier" --tools "lobes" --role courier --http-port 11435
"""

import argparse
import atexit
import importlib
import json
import logging
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# PRE-1: Policy enforcement (R09: via neocortex.core wrapper)
try:
    from neocortex.core import get_lock_guard as _get_guard
    from neocortex.core import get_policy_loader as _get_policy
    _POLICY_AVAILABLE = True
except ImportError:
    _POLICY_AVAILABLE = False

# SAVE-002/003: Save Point + Rollback (Camada 3  R09: via neocortex.core wrapper)
try:
    from neocortex.core import get_save_point_service as _get_sps
    _SAVE_POINT_AVAILABLE = True
except ImportError:
    _SAVE_POINT_AVAILABLE = False

from mcp.server import FastMCP

# Configurao de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Logger dedicado ao Mentor Mode (separado para filtrar facilmente nos logs)
mentor_logger = logging.getLogger("neocortex.mentor")
mentor_logger.setLevel(logging.DEBUG)


# 
# AGENT-203: Mentor Mode  Step 0
# Intercepta tarefas antes de envi-las ao LLM local.
# L os lobos relevantes e injeta contexto impositivo no prompt.
# 

# Mapeamento: role  lobos padro a carregar. Expanded via tarefa + keywords.
ROLE_DEFAULT_LOBES: Dict[str, List[str]] = {
    "courier": ["NC-LBE-FR-ARCHITECTURE-001.mdc", "NC-LBE-FR-SECURITY-001.mdc"],
    "engineer": ["NC-LBE-FR-ARCHITECTURE-001.mdc", "NC-LBE-FR-DEVELOPMENT-001.mdc"],
    "guardian": ["NC-LBE-FR-SECURITY-001.mdc"],
    "backend_dev": ["NC-LBE-FR-ARCHITECTURE-001.mdc", "NC-LBE-FR-BENCHMARKS-001.mdc"],
    "indexer": ["NC-LBE-FR-WHITELABEL-001.mdc"],
}

# Keywords da tarefa  lobos adicionais a incluir
KEYWORD_LOBE_MAP: Dict[str, List[str]] = {
    "index": ["NC-LBE-FR-ARCHITECTURE-001.mdc"],
    "indexar": ["NC-LBE-FR-ARCHITECTURE-001.mdc"],
    "search": ["NC-LBE-FR-ARCHITECTURE-001.mdc"],
    "buscar": ["NC-LBE-FR-ARCHITECTURE-001.mdc"],
    "security": ["NC-LBE-FR-SECURITY-001.mdc"],
    "segurana": ["NC-LBE-FR-SECURITY-001.mdc"],
    "lock": ["NC-LBE-FR-SECURITY-001.mdc"],
    "audit": ["NC-LBE-FR-SECURITY-001.mdc"],
    "test": ["NC-LBE-FR-DEVELOPMENT-001.mdc"],
    "teste": ["NC-LBE-FR-DEVELOPMENT-001.mdc"],
    "benchmark": ["NC-LBE-FR-BENCHMARKS-001.mdc"],
    "white": ["NC-LBE-FR-WHITELABEL-001.mdc"],
    "template": ["NC-LBE-FR-WHITELABEL-001.mdc"],
    "profile": ["NC-LBE-FR-PROFILES-001.mdc"],
    "perfil": ["NC-LBE-FR-PROFILES-001.mdc"],
}


def identify_relevant_lobes(agent_role: str, task_description: str) -> List[str]:
    """
    Decide quais lobos devem ser consultados com base no papel do agente e keywords da tarefa.
    Retorna lista deduplicada de nomes de arquivos .mdc.
    """
    relevant: List[str] = list(ROLE_DEFAULT_LOBES.get(agent_role, []))

    task_lower = task_description.lower()
    for keyword, lobes in KEYWORD_LOBE_MAP.items():
        if keyword in task_lower:
            for lobe in lobes:
                if lobe not in relevant:
                    relevant.append(lobe)

    mentor_logger.debug(
        f"[Mentor] Role='{agent_role}' | Task keywords matched  lobos: {relevant}"
    )
    return relevant


def extract_relevant_snippet(content: str, task_description: str, max_words: int = 400) -> str:
    """
    Extrai do contedo do lobo apenas os pargrafos mais relevantes para a tarefa.
    Usa heurstica de pontuao por palavras-chave para minimizar rudo no prompt.
    """
    word_count = len(content.split())
    if word_count <= max_words:
        return content  # Lobo pequeno  retorna inteiro

    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    task_keywords = set(w.lower() for w in task_description.split() if len(w) > 3)

    scored = []
    for para in paragraphs:
        para_words = set(para.lower().split())
        score = len(task_keywords & para_words)
        scored.append((score, para))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [p for score, p in scored[:4] if score > 0]

    if not top:
        # Sem match direto  retorna o incio do documento (cabealho/resumo)
        return content[: max_words * 5] + "\n[...trecho omitido por limite de tokens...]"

    return "\n\n".join(top)


def mentor_step_0(agent_role: str, task_description: str, lobe_dir: Optional[Path] = None) -> Optional[str]:
    """
    AGENT-203 / PRE-1  Mentor Mode Step 0.

    Intercepta a tarefa ANTES de envi-la ao LLM local.
    1. Identifica quais lobos so relevantes para este agente + tarefa.
    2. L o contedo desses lobos via LobeService (FTS5-indexed).
    3. Extrai trechos relevantes para minimizar tokens.
    4. PRE-1: Aplica limites de tokens do NC-CFG-FR-001 (PolicyLoader).
    5. Retorna a instruo impositiva a ser prefixada no prompt do LLM.

    Returns:
        str: Instruo impositiva prefixada com [ORDEM DO SISTEMA], ou None se sem contexto.
    """
    mentor_logger.info(
        f"[Mentor]  STEP 0 iniciado | role={agent_role} | tarefa='{task_description[:60]}...'"
    )

    # PRE-1: Load policy for this role
    policy = _get_policy() if _POLICY_AVAILABLE else None
    if policy:
        limits = policy.get_limits(role=agent_role)
        max_tokens_per_task = limits.get("max_tokens_per_task", 2048)
        mentor_prefix = policy.get_mentor_prefix(role=agent_role)
        mentor_logger.info(f"[Mentor/Policy] max_tokens_per_task={max_tokens_per_task} role={agent_role}")
    else:
        max_tokens_per_task = 2048
        mentor_prefix = ""

    # Importao lazy para evitar circular imports no startup
    try:
        from neocortex.core.NC-CORE-FR-018-lobe-service import get_lobe_service
        lobe_svc = get_lobe_service()
    except Exception as e:
        mentor_logger.error(f"[Mentor]  Falha ao inicializar LobeService: {e}")
        return None

    # 1. Identificar lobos relevantes
    relevant_lobes = identify_relevant_lobes(agent_role, task_description)
    if not relevant_lobes:
        mentor_logger.info("[Mentor] Nenhum lobo relevante encontrado. Continuando sem contexto.")
        return None

    # 2. Ler contedo dos lobos e extrair trechos
    context_blocks: List[str] = []
    for lobe_name in relevant_lobes:
        try:
            result = lobe_svc.get_lobe(lobe_name)
            if not result.get("exists"):
                mentor_logger.warning(f"[Mentor]  Lobo '{lobe_name}' no encontrado no repositrio.")
                continue

            content = result.get("content", "")
            if not content:
                continue

            snippet = extract_relevant_snippet(content, task_description)
            word_count = len(snippet.split())
            mentor_logger.info(
                f"[Mentor]  Lobo '{lobe_name}' carregado  {word_count} palavras extradas."
            )
            context_blocks.append(
                f"=== CONHECIMENTO DO LOBO: {lobe_name} ===\n{snippet}\n=== FIM DO LOBO ==="
            )
        except Exception as e:
            mentor_logger.error(f"[Mentor]  Erro ao ler lobo '{lobe_name}': {e}")

    if not context_blocks:
        mentor_logger.warning("[Mentor] Lobos identificados mas nenhum contedo carregado.")
        return None

    # 3. Montar instruo impositiva
    context_combined = "\n\n".join(context_blocks)

    # PRE-1: Include role-specific mentor_prefix from NC-CFG-FR-001 if available
    prefix_block = f"{mentor_prefix}\n\n" if mentor_prefix else ""

    instruction = (
        f"[ORDEM DO SISTEMA  LEIA ANTES DE AGIR]\n\n"
        f"{prefix_block}"
        f"Voc  o agente '{agent_role}' do NeoCortex. "
        f"Execute APENAS a tarefa delegada. NO tome iniciativas alm do solicitado.\n\n"
        f"CONTEXTO OBRIGATRIO (extrado dos lobos de conhecimento):\n\n"
        f"{context_combined}\n\n"
        f"REGRAS:\n"
        f"1. Baseie-se EXCLUSIVAMENTE no contexto acima e na tarefa.\n"
        f"2. Se o contexto for insuficiente, responda exatamente: CONTEXTO_INSUFICIENTE\n"
        f"3. No invente caminhos, nomes de arquivos ou configuraes.\n"
        f"4. Reporte o resultado via neocortex_task aps concluir.\n"
    )

    # PRE-1: Enforce token limit  truncate if over budget
    approx_tokens = len(instruction) // 4
    if approx_tokens > max_tokens_per_task:
        # Keep [ORDEM DO SISTEMA] header + first N chars that fit within budget
        char_budget = max_tokens_per_task * 4
        instruction = instruction[:char_budget] + f"\n\n[TRUNCADO: limite de {max_tokens_per_task} tokens atingido para role '{agent_role}']\n"
        mentor_logger.warning(
            f"[Mentor/Policy]  Instruo truncada a {max_tokens_per_task} tokens para role '{agent_role}'"
        )

    # PRE-1: Record token usage
    if policy:
        policy.record_token_usage(agent_role, len(instruction) // 4)

    mentor_logger.info(
        f"[Mentor]  Instruo montada com {len(context_blocks)} bloco(s) de contexto. "
        f"Tamanho total: {len(instruction)} chars (~{len(instruction)//4} tokens)."
    )
    return instruction

def handle_task(
    task_description: str,
    agent_role: str,
    task_id: str = "unknown",
    lobe_dir: Optional[Path] = None,
    llm_backend=None,
) -> Dict[str, Any]:
    """
    Handler central para processamento de tarefas com Mentor Mode ativo.
    Chamado pelo sub-server ao receber qualquer tarefa via neocortex_task.execute.

    Args:
        task_description: Descrio textual da tarefa.
        agent_role: Papel do agente (courier, engineer, guardian...).
        task_id: ID nico da tarefa (para log e ledger).
        lobe_dir: Diretrio do lobo isolado (opcional).
        llm_backend: Backend LLM a ser usado (se None, no envia ao LLM agora).

    Returns:
        Dict com resultado da execuo.
    """
    mentor_logger.info(f"[Mentor]  handle_task START | id={task_id} ")

    #  STEP -1: Save Point (SAVE-002/003  Camada 3) 
    _save_id = None
    if _SAVE_POINT_AVAILABLE:
        try:
            _sps = _get_sps()
            _save_id, _allowed = _sps.capture(
                action="task_execute",
                agent_role=agent_role,
                context={"task_id": task_id, "task_preview": task_description[:200]},
            )
            if not _allowed:
                return {
                    "task_id": task_id, "status": "blocked",
                    "error": "[STEP -1] Task bloqueada pelo LockGuard", "agent_role": agent_role,
                }
            mentor_logger.info(f"[Mentor]  STEP -1 captured | save_id={_save_id}")
        except Exception as _spe:
            mentor_logger.warning(f"[Mentor]  STEP -1 error (non-blocking): {_spe}")

    try:
        #  STEP 0: Mentor Mode 
        mentor_instruction = mentor_step_0(agent_role, task_description, lobe_dir)

        #  Montar prompt final 
        if mentor_instruction:
            final_prompt = f"{mentor_instruction}\n\n[TAREFA DELEGADA]\n{task_description}"
            mentor_logger.info("[Mentor] Prompt final montado COM instruo mentor.")
        else:
            final_prompt = task_description
            mentor_logger.info("[Mentor] Prompt final montado SEM instruo mentor (sem contexto relevante).")

        mentor_logger.debug(
            f"[Mentor] Prompt final ({len(final_prompt)} chars):\n{final_prompt[:300]}..."
        )

        #  Enviar ao LLM (se backend disponvel) 
        llm_response = None
        if llm_backend is not None:
            try:
                mentor_logger.info(f"[Mentor] Enviando prompt ao LLM backend: {type(llm_backend).__name__}")
                llm_response = llm_backend.generate(final_prompt)
                mentor_logger.info(f"[Mentor]  Resposta LLM recebida ({len(str(llm_response))} chars).")
            except Exception as e:
                mentor_logger.error(f"[Mentor]  Erro ao chamar LLM backend: {e}")
                llm_response = f"ERROR: {e}"
        else:
            mentor_logger.warning("[Mentor] Nenhum LLM backend fornecido. Retornando prompt montado.")

        #  Commit Save Point (operao bem-sucedida) 
        if _save_id and _SAVE_POINT_AVAILABLE:
            _get_sps().commit(_save_id)

        mentor_logger.info(f"[Mentor]  handle_task END | id={task_id} ")

        return {
            "task_id": task_id,
            "agent_role": agent_role,
            "mentor_active": mentor_instruction is not None,
            "prompt_length": len(final_prompt),
            "llm_response": llm_response,
            "status": "completed" if llm_response else "prompt_ready",
            "save_id": _save_id,
        }

    except Exception as exc:
        #  STEP +1: Rollback automtico (SAVE-003) 
        rollback_result = {}
        if _save_id and _SAVE_POINT_AVAILABLE:
            rollback_result = _get_sps().rollback(_save_id)
            mentor_logger.error(
                f"[Mentor]  STEP +1 ROLLBACK | save_id={_save_id} | error={exc}"
            )
        else:
            mentor_logger.error(f"[Mentor]  handle_task FAILED (no save point) | error={exc}")

        return {
            "task_id": task_id, "agent_role": agent_role,
            "status": "error", "error": str(exc),
            "rollback": rollback_result, "save_id": _save_id,
        }



def load_agent_config(lobe_dir: Path) -> Optional[Dict[str, Any]]:
    """Carrega configurao do agente a partir de neocortex_config.yaml."""
    config_path = lobe_dir / "neocortex_config.yaml"
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logger.info(f"Config loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load config {config_path}: {e}")
        return None


def filter_allowed_tools(
    requested_tools: List[str], config: Dict[str, Any]
) -> List[str]:
    """Filtra ferramentas baseado nas permisses do config."""
    if not config:
        return requested_tools

    allowed_tools = config.get("security", {}).get("allowed_tools", [])
    if not allowed_tools:
        return requested_tools

    # Converter nomes de ferramentas MCP para nomes de mdulos
    tool_to_module = {v: k for k, v in TOOL_MODULE_MAP.items()}

    filtered = []
    for tool in requested_tools:
        # Verificar se ferramenta est na lista permitida
        if tool in allowed_tools or f"neocortex_{tool}" in allowed_tools:
            filtered.append(tool)
        else:
            logger.warning(f"Tool '{tool}' not in allowed_tools list: {allowed_tools}")

    return filtered


# Session Manager simplificado para sub-servidores
class SubSessionManager:
    """Gerencia o ciclo de vida da sesso do sub-servidor."""

    def __init__(
        self, lobe_dir: Path, tools: List[str], port: int, role: str = "unknown"
    ):
        self.lobe_dir = lobe_dir
        self.tools = tools
        self.port = port
        self.role = role
        self.active = True
        self.agent_id = f"{role}_{lobe_dir.name}_{port}"
        self.config = load_agent_config(lobe_dir)

        logger.info(f"Sub-servidor iniciado: {self.agent_id}")
        logger.info(f"Lobe directory: {lobe_dir}")
        logger.info(f"Role: {role}")
        logger.info(f"Tools enabled: {tools}")
        logger.info(f"Port: {port}")
        if self.config:
            logger.info(
                f"Agent config loaded: role={self.config.get('agent', {}).get('role', 'unknown')}"
            )

        atexit.register(self.finalize_session)

    def finalize_session(self):
        """Finaliza a sesso do sub-servidor."""
        if not self.active:
            return

        self.active = False
        logger.info(f"Finalizando sub-servidor {self.agent_id}...")
        # Limpeza especfica do sub-servidor pode ser adicionada aqui


# Mapeamento de nomes de ferramentas para mdulos
TOOL_MODULE_MAP = {
    "cortex": "NC-TOOL-FR-001-cortex",
    "agent": "NC-TOOL-FR-002-agent",
    "benchmark": "NC-TOOL-FR-003-benchmark",
    "checkpoint": "NC-TOOL-FR-004-checkpoint",
    "config": "NC-TOOL-FR-005-config",
    "export": "NC-TOOL-FR-006-export",
    "init": "NC-TOOL-FR-007-init",
    "ledger": "NC-TOOL-FR-008-ledger",
    "lobes": "NC-TOOL-FR-009-lobes",
    "peers": "NC-TOOL-FR-010-peers",
    "pulse": "NC-TOOL-FR-011-pulse",
    "regression": "NC-TOOL-FR-012-regression",
    "report": "NC-TOOL-FR-013-report",
    "search": "NC-TOOL-FR-014-search",
    "security": "NC-TOOL-FR-015-security",
    "subserver": "NC-TOOL-FR-016-subserver",
    "task": "NC-TOOL-FR-017-task",
    "manifest": "NC-TOOL-FR-020-knowledge",
    "kg": "NC-TOOL-FR-020-knowledge",
    "consolidation": "NC-TOOL-FR-020-knowledge",
    "akl": "NC-TOOL-FR-020-knowledge",
    "brain": "NC-TOOL-FR-000-brain",
    "validate": "validate",  # Mdulo no modificado por no estar na tools pool
    "audit": "audit",        # Mdulo no modificado
}


def create_sub_mcp_server(
    lobe_dir: Path, enabled_tools: List[str], port: int, role: str = "unknown"
):
    """
    Create and configure a sub-MCP server instance for a specific lobe.

    Args:
        lobe_dir: Directory path for the lobe (becomes project root)
        enabled_tools: List of tool names to enable
        port: Port for the server (used for identification)
        role: Agent role (e.g., 'courier', 'engineer')

    Returns:
        Configured MCP server instance
    """
    # Carregar configurao do agente
    agent_config = load_agent_config(lobe_dir)

    # Filtrar ferramentas baseado nas permisses
    if agent_config:
        original_count = len(enabled_tools)
        enabled_tools = filter_allowed_tools(enabled_tools, agent_config)
        filtered_count = len(enabled_tools)
        if filtered_count < original_count:
            logger.warning(
                f"Filtered {original_count - filtered_count} tools not allowed for role '{role}'"
            )

    # Definir varivel de ambiente para o ConfigProvider usar este diretrio como root
    os.environ["NEOCORTEX_PROJECT_ROOT"] = str(lobe_dir.resolve())
    logger.info(f"Configurando NEOCORTEX_PROJECT_ROOT={lobe_dir.resolve()}")

    # Reinicializar o ConfigProvider para pegar o novo root
    from ..config import get_config

    config = get_config()
    config.reload()
    logger.info(f"Config reloaded. Cortex path: {config.cortex_path}")

    # Criar servidor FastMCP
    server = FastMCP(f"neocortex_{role}_{lobe_dir.name}")

    # Inicializar SessionManager especfico
    session_manager = SubSessionManager(lobe_dir, enabled_tools, port, role)

    # Registrar ferramentas habilitadas
    for tool_name in enabled_tools:
        if tool_name not in TOOL_MODULE_MAP:
            logger.warning(f"Ferramenta desconhecida: {tool_name}. Pulando.")
            continue

        module_name = TOOL_MODULE_MAP[tool_name]
        try:
            # Importao dinmica
            module = importlib.import_module(
                f".tools.{module_name}", package="neocortex.mcp"
            )
            # Chama register_tool passando a instncia server
            module.register_tool(server)
            logger.info(f"Ferramenta '{tool_name}' registrada com sucesso")
        except ImportError as e:
            logger.error(f"Erro ao importar ferramenta '{tool_name}': {e}")
        except AttributeError as e:
            logger.error(f"Erro ao registrar ferramenta '{tool_name}': {e}")
        except Exception as e:
            logger.error(f"Erro inesperado com ferramenta '{tool_name}': {e}")

    # Garantir que a ferramenta 'task' est sempre registrada (para receber tarefas)
    if "task" not in enabled_tools:
        try:
            module = importlib.import_module(".tools.task", package="neocortex.mcp")
            module.register_tool(server)
            logger.info(
                "Ferramenta 'task' registrada (obrigatria para sub-servidores)"
            )
        except Exception as e:
            logger.error(f"Erro ao registrar ferramenta 'task': {e}")

    logger.info(f"Sub-MCP server criado com {len(enabled_tools)} ferramentas")
    return server, session_manager


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Sub-MCP Server for NeoCortex")
    parser.add_argument(
        "--port",
        type=int,
        required=True,
        help="Port number for the sub-server (used for identification)",
    )
    parser.add_argument(
        "--lobe-dir",
        type=Path,
        required=True,
        help="Path to lobe directory (will become project root)",
    )
    parser.add_argument(
        "--tools",
        type=str,
        required=True,
        help="Comma-separated list of tools to enable (e.g., 'lobes,kg,consolidation')",
    )
    parser.add_argument(
        "--role",
        type=str,
        default="unknown",
        help="Agent role (courier, engineer, guardian). Falls back to neocortex_config.yaml.",
    )
    # ORCH-302: HTTP port para /task e /health endpoints
    parser.add_argument(
        "--http-port",
        type=int,
        default=None,
        help="HTTP port for /task and /health REST endpoints. If not set, HTTP server is not started.",
    )
    return parser.parse_args()


# 
# ORCH-302: HTTP Task Server  /task (POST) + /health (GET)
# Runs in a daemon thread alongside the MCP STDIO server.
# Allows send_task() from NC-TOOL-FR-016 to deliver tasks via HTTP IPC.
# 

def make_http_handler(agent_role: str, lobe_dir: Path):
    """Factory: returns a BaseHTTPRequestHandler with role+lobe_dir in closure."""

    class TaskHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):  # suppress access logs
            logger.debug(f"[HTTP] {format % args}")

        def _send_json(self, data: dict, status: int = 200):
            body = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            if self.path == "/health":
                self._send_json({"status": "ok", "role": agent_role, "lobe_dir": str(lobe_dir)})
            else:
                self._send_json({"error": "Not found"}, 404)

        def do_POST(self):  # noqa: N802
            if self.path != "/task":
                self._send_json({"error": "Not found"}, 404)
                return

            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8")
                payload = json.loads(body) if body else {}
            except Exception as e:
                self._send_json({"success": False, "error": f"Bad request: {e}"}, 400)
                return

            task_description = payload.get("task", payload.get("description", ""))
            task_id = payload.get("task_id", f"http_{id(payload)}")

            if not task_description:
                self._send_json({"success": False, "error": "Missing 'task' field in payload"}, 400)
                return

            try:
                # Load LLM backend from config
                from neocortex.NC-CORE-FR-001-config import get_config
                from neocortex.infra.llm.NC-INFRA-FR-009-factory import LLMFactory
                cfg = get_config()
                llm = LLMFactory.create(cfg)
            except Exception:
                llm = None  # Sem backend  retorna apenas o prompt montado

            result = handle_task(
                task_description=task_description,
                agent_role=agent_role,
                task_id=task_id,
                lobe_dir=lobe_dir,
                llm_backend=llm,
            )
            self._send_json({"success": True, **result})

    return TaskHandler


def start_http_server(http_port: int, agent_role: str, lobe_dir: Path):
    """Start the HTTP task server in a background daemon thread."""
    handler = make_http_handler(agent_role, lobe_dir)
    httpd = HTTPServer(("127.0.0.1", http_port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    logger.info(f"[ORCH-302] HTTP task server running on http://127.0.0.1:{http_port} (role={agent_role})")
    return httpd


def main():
    """Main entry point for sub-MCP server."""
    args = parse_arguments()

    # Validar diretrio do lobe
    if not args.lobe_dir.exists():
        logger.error(f"Lobe directory does not exist: {args.lobe_dir}")
        sys.exit(1)

    # Parse lista de ferramentas
    enabled_tools = [t.strip() for t in args.tools.split(",")]

    # Determinar role: do argumento ou do config.yaml
    role = args.role
    if role == "unknown":
        agent_config = load_agent_config(args.lobe_dir)
        if agent_config:
            role = agent_config.get("agent", {}).get("role", "unknown")
            logger.info(f"Role determined from config: {role}")
        else:
            logger.warning("Role not specified and config not found, using 'unknown'")

    logger.info(f"Starting sub-MCP server on port {args.port}")
    logger.info(f"Lobe directory: {args.lobe_dir}")
    logger.info(f"Role: {role}")
    logger.info(f"Enabled tools: {enabled_tools}")

    # ORCH-302: Iniciar HTTP task server se --http-port foi fornecido
    if args.http_port:
        start_http_server(args.http_port, role, args.lobe_dir)

    # Criar e configurar servidor MCP
    server, session_manager = create_sub_mcp_server(
        lobe_dir=args.lobe_dir, enabled_tools=enabled_tools, port=args.port, role=role
    )

    # Executar servidor MCP (STDIO)
    try:
        logger.info(f"Sub-MCP server '{session_manager.agent_id}' running")
        server.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info(
            f"Sub-servidor {session_manager.agent_id} interrompido pelo usurio"
        )
    except Exception as e:
        logger.error(f"Erro no sub-servidor {session_manager.agent_id}: {e}")
        raise


if __name__ == "__main__":
    main()
