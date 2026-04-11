#!/usr/bin/env python3
"""
Sub-MCP Server for NeoCortex Framework

Script para iniciar um sub-MCP server isolado para um Lobo específico.
Uso: python -m neocortex.mcp.sub_server --port 11435 --lobe-dir "lobes/agent-backend" --tools "lobes,kg,consolidation"
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import atexit
import importlib
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

from mcp.server import FastMCP, NotificationOptions
from mcp.server.models import InitializationOptions

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Logger dedicado ao Mentor Mode (separado para filtrar facilmente nos logs)
mentor_logger = logging.getLogger("neocortex.mentor")
mentor_logger.setLevel(logging.DEBUG)


# ─────────────────────────────────────────────────────────────────────────────
# AGENT-203: Mentor Mode — Step 0
# Intercepta tarefas antes de enviá-las ao LLM local.
# Lê os lobos relevantes e injeta contexto impositivo no prompt.
# ─────────────────────────────────────────────────────────────────────────────

# Mapeamento: role → lobos padrão a carregar. Expanded via tarefa + keywords.
ROLE_DEFAULT_LOBES: Dict[str, List[str]] = {
    "courier": ["NC-LBE-FR-ARCHITECTURE-001.mdc", "NC-LBE-FR-SECURITY-001.mdc"],
    "engineer": ["NC-LBE-FR-ARCHITECTURE-001.mdc", "NC-LBE-FR-DEVELOPMENT-001.mdc"],
    "guardian": ["NC-LBE-FR-SECURITY-001.mdc"],
    "backend_dev": ["NC-LBE-FR-ARCHITECTURE-001.mdc", "NC-LBE-FR-BENCHMARKS-001.mdc"],
    "indexer": ["NC-LBE-FR-WHITELABEL-001.mdc"],
}

# Keywords da tarefa → lobos adicionais a incluir
KEYWORD_LOBE_MAP: Dict[str, List[str]] = {
    "index": ["NC-LBE-FR-ARCHITECTURE-001.mdc"],
    "indexar": ["NC-LBE-FR-ARCHITECTURE-001.mdc"],
    "search": ["NC-LBE-FR-ARCHITECTURE-001.mdc"],
    "buscar": ["NC-LBE-FR-ARCHITECTURE-001.mdc"],
    "security": ["NC-LBE-FR-SECURITY-001.mdc"],
    "segurança": ["NC-LBE-FR-SECURITY-001.mdc"],
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
        f"[Mentor] Role='{agent_role}' | Task keywords matched → lobos: {relevant}"
    )
    return relevant


def extract_relevant_snippet(content: str, task_description: str, max_words: int = 400) -> str:
    """
    Extrai do conteúdo do lobo apenas os parágrafos mais relevantes para a tarefa.
    Usa heurística de pontuação por palavras-chave para minimizar ruído no prompt.
    """
    word_count = len(content.split())
    if word_count <= max_words:
        return content  # Lobo pequeno — retorna inteiro

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
        # Sem match direto — retorna o início do documento (cabeçalho/resumo)
        return content[: max_words * 5] + "\n[...trecho omitido por limite de tokens...]"

    return "\n\n".join(top)


def mentor_step_0(agent_role: str, task_description: str, lobe_dir: Optional[Path] = None) -> Optional[str]:
    """
    AGENT-203 — Mentor Mode Step 0.

    Intercepta a tarefa ANTES de enviá-la ao LLM local.
    1. Identifica quais lobos são relevantes para este agente + tarefa.
    2. Lê o conteúdo desses lobos via LobeService (FTS5-indexed).
    3. Extrai trechos relevantes para minimizar tokens.
    4. Retorna a instrução impositiva a ser prefixada no prompt do LLM.

    Returns:
        str: Instrução impositiva prefixada com [ORDEM DO SISTEMA], ou None se sem contexto.
    """
    mentor_logger.info(
        f"[Mentor] ▶ STEP 0 iniciado | role={agent_role} | tarefa='{task_description[:60]}...'"
    )

    # Importação lazy para evitar circular imports no startup
    try:
        from neocortex.core.lobe_service import get_lobe_service
        lobe_svc = get_lobe_service()
    except Exception as e:
        mentor_logger.error(f"[Mentor] ❌ Falha ao inicializar LobeService: {e}")
        return None

    # 1. Identificar lobos relevantes
    relevant_lobes = identify_relevant_lobes(agent_role, task_description)
    if not relevant_lobes:
        mentor_logger.info("[Mentor] Nenhum lobo relevante encontrado. Continuando sem contexto.")
        return None

    # 2. Ler conteúdo dos lobos e extrair trechos
    context_blocks: List[str] = []
    for lobe_name in relevant_lobes:
        try:
            result = lobe_svc.get_lobe(lobe_name)
            if not result.get("exists"):
                mentor_logger.warning(f"[Mentor] ⚠️ Lobo '{lobe_name}' não encontrado no repositório.")
                continue

            content = result.get("content", "")
            if not content:
                continue

            snippet = extract_relevant_snippet(content, task_description)
            word_count = len(snippet.split())
            mentor_logger.info(
                f"[Mentor] ✅ Lobo '{lobe_name}' carregado → {word_count} palavras extraídas."
            )
            context_blocks.append(
                f"=== CONHECIMENTO DO LOBO: {lobe_name} ===\n{snippet}\n=== FIM DO LOBO ==="
            )
        except Exception as e:
            mentor_logger.error(f"[Mentor] ❌ Erro ao ler lobo '{lobe_name}': {e}")

    if not context_blocks:
        mentor_logger.warning("[Mentor] Lobos identificados mas nenhum conteúdo carregado.")
        return None

    # 3. Montar instrução impositiva
    context_combined = "\n\n".join(context_blocks)
    instruction = (
        f"[ORDEM DO SISTEMA — LEIA ANTES DE AGIR]\n\n"
        f"Você é o agente '{agent_role}' do NeoCortex. "
        f"Execute APENAS a tarefa delegada. NÃO tome iniciativas além do solicitado.\n\n"
        f"CONTEXTO OBRIGATÓRIO (extraído dos lobos de conhecimento):\n\n"
        f"{context_combined}\n\n"
        f"REGRAS:\n"
        f"1. Baseie-se EXCLUSIVAMENTE no contexto acima e na tarefa.\n"
        f"2. Se o contexto for insuficiente, responda exatamente: CONTEXTO_INSUFICIENTE\n"
        f"3. Não invente caminhos, nomes de arquivos ou configurações.\n"
        f"4. Reporte o resultado via neocortex_task após concluir.\n"
    )

    mentor_logger.info(
        f"[Mentor] ✅ Instrução montada com {len(context_blocks)} bloco(s) de contexto. "
        f"Tamanho total: {len(instruction)} chars."
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
        task_description: Descrição textual da tarefa.
        agent_role: Papel do agente (courier, engineer, guardian...).
        task_id: ID único da tarefa (para log e ledger).
        lobe_dir: Diretório do lobo isolado (opcional).
        llm_backend: Backend LLM a ser usado (se None, não envia ao LLM agora).

    Returns:
        Dict com resultado da execução.
    """
    mentor_logger.info(f"[Mentor] ═══ handle_task START | id={task_id} ═══")

    # ── MENTOR STEP 0: Montar contexto ─────────────────────────────────────
    mentor_instruction = mentor_step_0(agent_role, task_description, lobe_dir)

    # ── Montar prompt final ─────────────────────────────────────────────────
    if mentor_instruction:
        final_prompt = f"{mentor_instruction}\n\n[TAREFA DELEGADA]\n{task_description}"
        mentor_logger.info("[Mentor] Prompt final montado COM instrução mentor.")
    else:
        final_prompt = task_description
        mentor_logger.info("[Mentor] Prompt final montado SEM instrução mentor (sem contexto relevante).")

    mentor_logger.debug(
        f"[Mentor] Prompt final ({len(final_prompt)} chars):\n{final_prompt[:300]}..."
    )

    # ── Enviar ao LLM (se backend disponível) ──────────────────────────────
    llm_response = None
    if llm_backend is not None:
        try:
            mentor_logger.info(f"[Mentor] Enviando prompt ao LLM backend: {type(llm_backend).__name__}")
            llm_response = llm_backend.generate(final_prompt)
            mentor_logger.info(f"[Mentor] ✅ Resposta LLM recebida ({len(str(llm_response))} chars).")
        except Exception as e:
            mentor_logger.error(f"[Mentor] ❌ Erro ao chamar LLM backend: {e}")
            llm_response = f"ERROR: {e}"
    else:
        mentor_logger.warning("[Mentor] Nenhum LLM backend fornecido. Retornando prompt montado.")

    mentor_logger.info(f"[Mentor] ═══ handle_task END | id={task_id} ═══")

    return {
        "task_id": task_id,
        "agent_role": agent_role,
        "mentor_active": mentor_instruction is not None,
        "prompt_length": len(final_prompt),
        "llm_response": llm_response,
        "status": "completed" if llm_response else "prompt_ready",
    }


def load_agent_config(lobe_dir: Path) -> Optional[Dict[str, Any]]:
    """Carrega configuração do agente a partir de neocortex_config.yaml."""
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
    """Filtra ferramentas baseado nas permissões do config."""
    if not config:
        return requested_tools

    allowed_tools = config.get("security", {}).get("allowed_tools", [])
    if not allowed_tools:
        return requested_tools

    # Converter nomes de ferramentas MCP para nomes de módulos
    tool_to_module = {v: k for k, v in TOOL_MODULE_MAP.items()}

    filtered = []
    for tool in requested_tools:
        # Verificar se ferramenta está na lista permitida
        if tool in allowed_tools or f"neocortex_{tool}" in allowed_tools:
            filtered.append(tool)
        else:
            logger.warning(f"Tool '{tool}' not in allowed_tools list: {allowed_tools}")

    return filtered


# Session Manager simplificado para sub-servidores
class SubSessionManager:
    """Gerencia o ciclo de vida da sessão do sub-servidor."""

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
        """Finaliza a sessão do sub-servidor."""
        if not self.active:
            return

        self.active = False
        logger.info(f"Finalizando sub-servidor {self.agent_id}...")
        # Limpeza específica do sub-servidor pode ser adicionada aqui


# Mapeamento de nomes de ferramentas para módulos
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
    "validate": "validate",  # Módulo não modificado por não estar na tools pool
    "audit": "audit",        # Módulo não modificado
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
    # Carregar configuração do agente
    agent_config = load_agent_config(lobe_dir)

    # Filtrar ferramentas baseado nas permissões
    if agent_config:
        original_count = len(enabled_tools)
        enabled_tools = filter_allowed_tools(enabled_tools, agent_config)
        filtered_count = len(enabled_tools)
        if filtered_count < original_count:
            logger.warning(
                f"Filtered {original_count - filtered_count} tools not allowed for role '{role}'"
            )

    # Definir variável de ambiente para o ConfigProvider usar este diretório como root
    os.environ["NEOCORTEX_PROJECT_ROOT"] = str(lobe_dir.resolve())
    logger.info(f"Configurando NEOCORTEX_PROJECT_ROOT={lobe_dir.resolve()}")

    # Reinicializar o ConfigProvider para pegar o novo root
    from ..config import get_config

    config = get_config()
    config.reload()
    logger.info(f"Config reloaded. Cortex path: {config.cortex_path}")

    # Criar servidor FastMCP
    server = FastMCP(f"neocortex_{role}_{lobe_dir.name}")

    # Inicializar SessionManager específico
    session_manager = SubSessionManager(lobe_dir, enabled_tools, port, role)

    # Registrar ferramentas habilitadas
    for tool_name in enabled_tools:
        if tool_name not in TOOL_MODULE_MAP:
            logger.warning(f"Ferramenta desconhecida: {tool_name}. Pulando.")
            continue

        module_name = TOOL_MODULE_MAP[tool_name]
        try:
            # Importação dinâmica
            module = importlib.import_module(
                f".tools.{module_name}", package="neocortex.mcp"
            )
            # Chama register_tool passando a instância server
            module.register_tool(server)
            logger.info(f"Ferramenta '{tool_name}' registrada com sucesso")
        except ImportError as e:
            logger.error(f"Erro ao importar ferramenta '{tool_name}': {e}")
        except AttributeError as e:
            logger.error(f"Erro ao registrar ferramenta '{tool_name}': {e}")
        except Exception as e:
            logger.error(f"Erro inesperado com ferramenta '{tool_name}': {e}")

    # Garantir que a ferramenta 'task' está sempre registrada (para receber tarefas)
    if "task" not in enabled_tools:
        try:
            module = importlib.import_module(".tools.task", package="neocortex.mcp")
            module.register_tool(server)
            logger.info(
                "Ferramenta 'task' registrada (obrigatória para sub-servidores)"
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
        help="Agent role (e.g., 'courier', 'engineer'). If not provided, will try to read from neocortex_config.yaml",
    )
    return parser.parse_args()


def main():
    """Main entry point for sub-MCP server."""
    args = parse_arguments()

    # Validar diretório do lobe
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
            logger.warning(f"Role not specified and config not found, using 'unknown'")

    logger.info(f"Starting sub-MCP server on port {args.port}")
    logger.info(f"Lobe directory: {args.lobe_dir}")
    logger.info(f"Role: {role}")
    logger.info(f"Enabled tools: {enabled_tools}")

    # Criar e configurar servidor
    server, session_manager = create_sub_mcp_server(
        lobe_dir=args.lobe_dir, enabled_tools=enabled_tools, port=args.port, role=role
    )

    # Executar servidor
    try:
        logger.info(f"Sub-MCP server '{session_manager.agent_id}' running")
        server.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info(
            f"Sub-servidor {session_manager.agent_id} interrompido pelo usuário"
        )
    except Exception as e:
        logger.error(f"Erro no sub-servidor {session_manager.agent_id}: {e}")
        raise


if __name__ == "__main__":
    main()
