#!/usr/bin/env python3
"""
NC-PRF-FR-003 - Profile Loader & Converter

Converte Lucas.json para schema NeoCortex Profile e gerencia perfis hierarquicos.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# ==================== CONFIGURACOES ====================

# Caminhos
PROJECT_ROOT = Path(__file__).parent.parent  # neocortex_framework
PROFILES_DIR = PROJECT_ROOT / "DIR-PRF-FR-001-profiles-main"
TEMPLATES_DIR = PROFILES_DIR / "templates"
USERS_DIR = PROFILES_DIR / "users"

# Schema versions
DEV_PROFILE_SCHEMA = "neocortex-profile-v1.0"
TEAM_PROFILE_SCHEMA = "neocortex-team-v1.0"

# ==================== FUNCOES AUXILIARES ====================


def load_json_file(filepath: Path) -> Dict[str, Any]:
    """Carrega arquivo JSON com tratamento de erro."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Arquivo nao encontrado: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Erro ao decodificar JSON em {filepath}: {e}")
        sys.exit(1)


def save_json_file(filepath: Path, data: Dict[str, Any], indent: int = 2):
    """Salva arquivo JSON com formatacao."""
    os.makedirs(filepath.parent, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    print(f"[OK] Arquivo salvo: {filepath}")


def get_timestamp() -> str:
    """Retorna timestamp no formato ISO."""
    return datetime.now().isoformat() + "Z"


# ==================== CONVERSOR LUCAS.JSON ====================


def convert_lucas_to_neocortex(
    lucas_data: Dict[str, Any],
    user_id: str = "lucas_valerio",
    hierarchy_level: int = 5,
    parent_id: Optional[str] = "org_panda_factory",
) -> Dict[str, Any]:
    """
    Converte Lucas.json (v6.2.0) para schema NeoCortex Profile.

    Args:
        lucas_data: Dados do Lucas.json original
        user_id: ID do usuario no novo schema
        hierarchy_level: Nivel hierarquico (0 = root)
        parent_id: ID do pai na hierarquia

    Returns:
        Perfil no formato NeoCortex Profile
    """
    timestamp = get_timestamp()

    # Extrair dados do Lucas.json
    work_style = lucas_data.get("work_style", {})
    knowledge_graph = lucas_data.get("knowledge_graph", {})
    linguistic_fingerprint = lucas_data.get("linguistic_fingerprint", {})
    operating_principles = lucas_data.get("operating_principles", {})
    psychological_profile = lucas_data.get("psychological_profile", {})

    # Construir perfil NeoCortex
    profile = {
        "$schema": DEV_PROFILE_SCHEMA,
        "profile_type": "developer",
        "version": "1.0.0",
        "identity": {
            "user_id": user_id,
            "display_name": "Lucas Valerio",
            "email": "",  # Nao disponivel no Lucas.json
            "avatar_url": "",
            "created_at": lucas_data.get("_meta", {}).get("created", timestamp),
            "updated_at": lucas_data.get("_meta", {}).get("updated", timestamp),
        },
        "hierarchy": {
            "level": hierarchy_level,
            "parent_id": parent_id,
            "children_ids": [],
            "ancestors": ["root_global", "org_brazil", "org_sao_paulo", parent_id]
            if parent_id
            else [],
            "descendants_count": 0,
            "sibling_ids": [],
            "visibility_rules": {
                "can_read_upwards": False,
                "can_read_siblings": True,
                "can_read_descendants": True,
                "max_read_depth": -1,
                "write_permission": ["self", "descendants"],
            },
        },
        "permissions": {
            "roles": ["developer", "admin", "founder"],
            "scopes": [
                "project:read",
                "project:write",
                "team:manage",
                "user:invite",
                "billing:view",
            ],
            "constraints": {
                "max_projects": 50,
                "max_storage_mb": 1024,
                "max_api_calls_per_day": 10000,
            },
        },
        "personal_patterns": {
            "productivity": {
                "peak_hours": _extract_peak_hours(work_style),
                "session_duration_avg": "2.5h",  # Estimado
                "context_switch_tolerance": "high"
                if work_style.get("attention_pattern", "").lower() == "multithreading"
                else "medium",
                "preferred_days": ["segunda", "terca", "quarta", "quinta", "sexta"],
            },
            "tech_preferences": {
                "frontend": _extract_tech_stack(knowledge_graph, "Frontend"),
                "backend": _extract_tech_stack(knowledge_graph, "Google_Core"),
                "trading": _extract_tech_stack(knowledge_graph, "Trading_Systems"),
                "automation": _extract_tech_stack(knowledge_graph, "Data_&_Automation"),
                "mastery_levels": _extract_mastery_levels(knowledge_graph),
            },
            "communication": {
                "preferred_languages": ["pt-BR", "en"],
                "message_style": "fragmented"
                if linguistic_fingerprint.get("syntax_patterns", [])
                else "standard",
                "response_expectation": "fast",
                "syntax_patterns": linguistic_fingerprint.get("syntax_patterns", []),
            },
        },
        "learning_engine": {
            "common_mistakes": [],  # Sera preenchido pelo uso
            "historical_patterns": {
                "project_completion_rate": "85%",  # Estimado
                "bug_resolution_time_avg": "1.2h",
                "feature_development_speed": "3.5 dias",
                "preferred_project_size": "medium",
            },
            "prediction_model": {
                "next_best_action_accuracy": "0%",  # Inicial
                "stack_suggestion_accuracy": "0%",
                "time_estimation_accuracy": "0%",
                "last_training_date": timestamp,
            },
        },
        "current_context": {
            "active_projects": ["neocortex_framework", "panda_factory"],
            "current_focus": "mcp_hub_development",
            "available_hours_weekly": 40,
            "location": {
                "city": "Americana",
                "state": "Sao Paulo",
                "country": "Brasil",
                "timezone": "America/Sao_Paulo",
            },
            "device_preferences": ["desktop", "dual_monitor"],
        },
        "integrations": {
            "mcp_servers": ["antigravity", "vscode"],
            "external_tools": ["github", "discord"],
            "api_keys": {
                "firebase": "configured",
                "gemini": "configured",
                "stripe": "configured",
            },
        },
        "metadata": {
            "source": f"lucas.json_v{lucas_data.get('_meta', {}).get('version', '6.2.0')}_converted",
            "conversion_date": timestamp,
            "privacy_level": "private",
            "sync_status": "local",
            "backup_frequency": "daily",
        },
    }

    # Adicionar regras pessoais se disponiveis
    if operating_principles:
        profile["personal_patterns"]["personal_rules"] = [
            f"{k}: {v}" for k, v in operating_principles.items()
        ]

    return profile


def _extract_peak_hours(work_style: Dict[str, Any]) -> List[str]:
    """Extrai horarios de pico do work_style."""
    # Lucas trabalha ate tarde, baseado no session_pattern
    if (
        work_style.get("session_pattern", "").lower()
        == "deep work sessions that extend past midnight"
    ):
        return ["09:00-12:00", "21:00-02:00"]
    return ["09:00-12:00", "14:00-18:00"]


def _extract_tech_stack(knowledge_graph: Dict[str, Any], category: str) -> List[str]:
    """Extrai tech stack de uma categoria especifica."""
    tech_mastery = knowledge_graph.get("tech_stack_mastery", {})
    if category in tech_mastery:
        data = tech_mastery[category]
        if isinstance(data, dict) and "tools" in data:
            # Categoria com estrutura {tools: [], mastery_level: str}
            tools = data.get("tools", [])
            if isinstance(tools, list):
                return tools
        elif isinstance(data, list):
            # Categoria é lista direta (ex: Trading_Systems)
            return data
    return []


def _extract_mastery_levels(knowledge_graph: Dict[str, Any]) -> Dict[str, str]:
    """Extrai niveis de maestria."""
    mastery_levels = {}
    tech_mastery = knowledge_graph.get("tech_stack_mastery", {})

    for category, data in tech_mastery.items():
        if isinstance(data, dict) and "mastery_level" in data:
            # Simplificar nome da categoria
            cat_key = category.lower().replace("_&_", "_").replace(" ", "_")
            mastery_levels[cat_key] = data["mastery_level"]

    return mastery_levels


# ==================== GERENCIADOR DE PERFIS ====================


def create_dev_profile_from_template(
    user_id: str,
    display_name: str,
    email: str = "",
    hierarchy_level: int = 0,
    parent_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Cria novo perfil de desenvolvedor a partir do template.

    Args:
        user_id: ID unico do usuario
        display_name: Nome para exibicao
        email: Email do usuario (opcional)
        hierarchy_level: Nivel hierarquico inicial
        parent_id: ID do pai na hierarquia (opcional)

    Returns:
        Perfil preenchido
    """
    template_path = TEMPLATES_DIR / "NC-PRF-TMP-001-dev-profile-template.json"
    template = load_json_file(template_path)

    # Substituir placeholders
    timestamp = get_timestamp()

    profile = template.copy()
    profile["identity"]["user_id"] = user_id
    profile["identity"]["display_name"] = display_name
    profile["identity"]["email"] = email
    profile["identity"]["created_at"] = timestamp
    profile["identity"]["updated_at"] = timestamp

    profile["hierarchy"]["level"] = hierarchy_level
    profile["hierarchy"]["parent_id"] = parent_id

    profile["learning_engine"]["prediction_model"]["last_training_date"] = timestamp
    profile["metadata"]["conversion_date"] = timestamp

    return profile


def save_dev_profile(profile: Dict[str, Any], user_id: Optional[str] = None) -> Path:
    """
    Salva perfil de desenvolvedor no diretorio de usuarios.

    Args:
        profile: Dados do perfil
        user_id: ID do usuario (se None, usa do perfil)

    Returns:
        Caminho do arquivo salvo
    """
    user_id = user_id or profile["identity"]["user_id"]
    user_dir = USERS_DIR / user_id
    user_dir.mkdir(exist_ok=True)

    filepath = user_dir / f"NC-PRF-USR-{user_id}-profile.json"
    save_json_file(filepath, profile)

    return filepath


# ==================== VERIFICACAO DE ACESSO HIERARQUICO ====================


def check_hierarchical_access(
    user_profile: Dict[str, Any], resource_profile: Dict[str, Any], action: str = "read"
) -> Dict[str, Any]:
    """
    Verifica se usuario pode acessar recurso baseado em hierarquia.

    Regras:
    1. Usuario pode ler recursos do MESMO nivel se for dono OU se recurso for publico
    2. Usuario pode ler recursos de NIVEIS INFERIORES sempre
    3. Usuario NAO pode ler recursos de NIVEIS SUPERIORES
    4. Recursos laterais (mesmo nivel, dono diferente) requerem permissao explicita

    Args:
        user_profile: Perfil do usuario solicitante
        resource_profile: Perfil do recurso (ou dono do recurso)
        action: Acao desejada (read/write)

    Returns:
        Dict com allowed (bool) e reason (str)
    """
    user_level = user_profile["hierarchy"]["level"]
    resource_level = resource_profile["hierarchy"]["level"]
    user_id = user_profile["identity"]["user_id"]
    resource_owner_id = resource_profile["identity"]["user_id"]

    # REGRA 1: Usuario e SUPERIOR ao recurso  PERMITIDO (para leitura)
    if user_level > resource_level:
        if action == "read":
            return {
                "allowed": True,
                "reason": "hierarchy_superior_can_read_descendants",
            }
        elif action == "write":
            # Para escrita, verificar se usuario pode escrever em descendentes
            write_permission = user_profile["hierarchy"]["visibility_rules"][
                "write_permission"
            ]
            if "descendants" in write_permission:
                return {
                    "allowed": True,
                    "reason": "hierarchy_superior_can_write_descendants",
                }
            else:
                return {
                    "allowed": False,
                    "reason": "no_write_permission_for_descendants",
                }

    # REGRA 2: Mesmo nivel  verificar ownership
    elif user_level == resource_level:
        if user_id == resource_owner_id:
            return {"allowed": True, "reason": "self_ownership"}
        else:
            # Recurso lateral  verificar permissoes explicitas
            if action == "read":
                can_read_siblings = user_profile["hierarchy"]["visibility_rules"][
                    "can_read_siblings"
                ]
                if can_read_siblings:
                    return {"allowed": True, "reason": "sibling_read_allowed"}
                else:
                    return {
                        "allowed": False,
                        "reason": "lateral_access_requires_explicit_permission",
                    }
            else:  # write
                return {
                    "allowed": False,
                    "reason": "cannot_write_others_sibling_resources",
                }

    # REGRA 3: Usuario e INFERIOR ao recurso  NEGADO (para leitura de superiores)
    else:  # user_level < resource_level
        if action == "read":
            can_read_upwards = user_profile["hierarchy"]["visibility_rules"][
                "can_read_upwards"
            ]
            if can_read_upwards:
                return {"allowed": True, "reason": "upwards_read_allowed_by_config"}
            else:
                return {
                    "allowed": False,
                    "reason": "hierarchy_inferior_cannot_read_upwards",
                }
        else:  # write
            return {"allowed": False, "reason": "cannot_write_upwards"}


# ==================== INTERFACE DE LINHA DE COMANDO ====================


def main():
    """Funcao principal do loader."""
    import argparse

    parser = argparse.ArgumentParser(
        description="NeoCortex Profile Loader & Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Converter Lucas.json para NeoCortex Profile
  python NC-PRF-FR-003-profile-loader.py convert \\
    --input "C:/Users/Lucas Valerio/Desktop/JSON LUCAS/Lucas.json" \\
    --output "users/lucas_valerio/profile.json"
  
  # Criar novo perfil a partir do template
  python NC-PRF-FR-003-profile-loader.py create \\
    --user_id "novo_usuario" \\
    --display_name "Novo Usuario"
  
  # Verificar acesso entre perfis
  python NC-PRF-FR-003-profile-loader.py check-access \\
    --user_profile "users/user1/profile.json" \\
    --resource_profile "users/user2/profile.json" \\
    --action read
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # Parser para conversao
    convert_parser = subparsers.add_parser(
        "convert", help="Converter Lucas.json para NeoCortex Profile"
    )
    convert_parser.add_argument(
        "--input", required=True, help="Caminho do Lucas.json original"
    )
    convert_parser.add_argument(
        "--output", required=True, help="Caminho de saida (relativo a profiles dir)"
    )
    convert_parser.add_argument(
        "--user_id", default="lucas_valerio", help="ID do usuario no novo schema"
    )
    convert_parser.add_argument(
        "--hierarchy_level", type=int, default=5, help="Nivel hierarquico (0=root)"
    )
    convert_parser.add_argument("--parent_id", help="ID do pai na hierarquia")

    # Parser para criacao
    create_parser = subparsers.add_parser(
        "create", help="Criar novo perfil a partir do template"
    )
    create_parser.add_argument("--user_id", required=True, help="ID unico do usuario")
    create_parser.add_argument(
        "--display_name", required=True, help="Nome para exibicao"
    )
    create_parser.add_argument("--email", default="", help="Email do usuario")
    create_parser.add_argument(
        "--hierarchy_level", type=int, default=0, help="Nivel hierarquico inicial"
    )
    create_parser.add_argument("--parent_id", help="ID do pai na hierarquia")

    # Parser para verificacao de acesso
    access_parser = subparsers.add_parser(
        "check-access", help="Verificar acesso hierarquico"
    )
    access_parser.add_argument(
        "--user_profile", required=True, help="Caminho do perfil do usuario"
    )
    access_parser.add_argument(
        "--resource_profile", required=True, help="Caminho do perfil do recurso"
    )
    access_parser.add_argument(
        "--action", default="read", choices=["read", "write"], help="Acao desejada"
    )

    args = parser.parse_args()

    if args.command == "convert":
        # Converter Lucas.json
        print(f"[LOAD] Carregando: {args.input}")
        lucas_data = load_json_file(Path(args.input))

        print("[CONVERT] Convertendo Lucas.json para NeoCortex Profile...")
        profile = convert_lucas_to_neocortex(
            lucas_data,
            user_id=args.user_id,
            hierarchy_level=args.hierarchy_level,
            parent_id=args.parent_id,
        )

        output_path = PROFILES_DIR / args.output
        save_json_file(output_path, profile)
        print(f"[OK] Conversao concluida: {output_path}")

    elif args.command == "create":
        # Criar novo perfil
        print(f"[USER] Criando perfil para: {args.user_id}")
        profile = create_dev_profile_from_template(
            user_id=args.user_id,
            display_name=args.display_name,
            email=args.email,
            hierarchy_level=args.hierarchy_level,
            parent_id=args.parent_id,
        )

        filepath = save_dev_profile(profile)
        print(f"[OK] Perfil criado: {filepath}")

    elif args.command == "check-access":
        # Verificar acesso
        user_profile = load_json_file(PROFILES_DIR / args.user_profile)
        resource_profile = load_json_file(PROFILES_DIR / args.resource_profile)

        result = check_hierarchical_access(
            user_profile, resource_profile, action=args.action
        )

        print(f"[ACCESS] Verificacao de acesso:")
        print(
            f"  Usuario: {user_profile['identity']['user_id']} (nivel {user_profile['hierarchy']['level']})"
        )
        print(
            f"  Recurso: {resource_profile['identity']['user_id']} (nivel {resource_profile['hierarchy']['level']})"
        )
        print(f"  Acao: {args.action}")
        print(
            f"  Resultado: {'[OK] PERMITIDO' if result['allowed'] else '[ERROR] NEGADO'}"
        )
        print(f"  Razao: {result['reason']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
