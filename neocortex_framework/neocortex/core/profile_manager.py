#!/usr/bin/env python3
"""
NeoCortex Profile Manager

Módulo para gerenciamento de perfis hierárquicos de desenvolvedores e equipes.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Importar constante PROJECT_ROOT do módulo file_utils
from .file_utils import PROJECT_ROOT

# ==================== CONFIGURAÇÕES ====================

# Caminhos relativos ao diretório do framework
PROFILES_DIR = PROJECT_ROOT / "DIR-PRF-FR-001-profiles-main"
TEMPLATES_DIR = PROFILES_DIR / "templates"
USERS_DIR = PROFILES_DIR / "users"

# Schema versions
DEV_PROFILE_SCHEMA = "neocortex-profile-v1.0"
TEAM_PROFILE_SCHEMA = "neocortex-team-v1.0"

# ==================== FUNÇÕES AUXILIARES ====================


def load_json_file(filepath: Path) -> Dict[str, Any]:
    """Carrega arquivo JSON com tratamento de erro."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao decodificar JSON em {filepath}: {e}")


def save_json_file(filepath: Path, data: Dict[str, Any], indent: int = 2):
    """Salva arquivo JSON com formatação."""
    os.makedirs(filepath.parent, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def get_timestamp() -> str:
    """Retorna timestamp no formato ISO."""
    return datetime.now().isoformat() + "Z"


# ==================== GESTÃO DE PERFIS ====================


def load_profile(user_id: str) -> Dict[str, Any]:
    """
    Carrega perfil de desenvolvedor pelo user_id.

    Args:
        user_id: ID do usuário (ex: "lucas_valerio")

    Returns:
        Dicionário com perfil carregado

    Raises:
        FileNotFoundError: Se perfil não existir
    """
    profile_path = USERS_DIR / user_id / f"NC-PRF-USR-{user_id}-profile.json"
    if not profile_path.exists():
        # Tentar caminho alternativo (sem prefixo)
        alt_path = USERS_DIR / user_id / "profile.json"
        if alt_path.exists():
            profile_path = alt_path
        else:
            raise FileNotFoundError(f"Perfil não encontrado para user_id: {user_id}")

    return load_json_file(profile_path)


def save_profile(profile: Dict[str, Any]) -> Path:
    """
    Salva perfil de desenvolvedor.

    Args:
        profile: Dicionário com dados do perfil

    Returns:
        Caminho do arquivo salvo
    """
    user_id = profile["identity"]["user_id"]
    user_dir = USERS_DIR / user_id
    user_dir.mkdir(exist_ok=True)

    filepath = user_dir / f"NC-PRF-USR-{user_id}-profile.json"
    save_json_file(filepath, profile)

    return filepath


def create_profile(
    user_id: str,
    display_name: str,
    email: str = "",
    hierarchy_level: int = 0,
    parent_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Cria novo perfil a partir do template.

    Args:
        user_id: ID único do usuário
        display_name: Nome para exibição
        email: Email do usuário (opcional)
        hierarchy_level: Nível hierárquico inicial
        parent_id: ID do pai na hierarquia (opcional)

    Returns:
        Perfil preenchido
    """
    # Carregar template
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


def profile_exists(user_id: str) -> bool:
    """
    Verifica se perfil existe.

    Args:
        user_id: ID do usuário

    Returns:
        True se perfil existir
    """
    profile_path = USERS_DIR / user_id / f"NC-PRF-USR-{user_id}-profile.json"
    alt_path = USERS_DIR / user_id / "profile.json"
    return profile_path.exists() or alt_path.exists()


# ==================== VERIFICAÇÃO DE ACESSO HIERÁRQUICO ====================


def check_hierarchical_access(
    user_profile: Dict[str, Any], resource_profile: Dict[str, Any], action: str = "read"
) -> Dict[str, Any]:
    """
    Verifica se usuário pode acessar recurso baseado em hierarquia.

    Regras:
    1. Usuário pode ler recursos do MESMO nível se for dono OU se recurso for público
    2. Usuário pode ler recursos de NÍVEIS INFERIORES sempre
    3. Usuário NÃO pode ler recursos de NÍVEIS SUPERIORES
    4. Recursos laterais (mesmo nível, dono diferente) requerem permissão explícita

    Args:
        user_profile: Perfil do usuário solicitante
        resource_profile: Perfil do recurso (ou dono do recurso)
        action: Ação desejada ("read" ou "write")

    Returns:
        Dict com:
        - allowed (bool): Se acesso é permitido
        - reason (str): Razão da decisão
        - required_permission (str, opcional): Permissão necessária se negado
    """
    user_level = user_profile["hierarchy"]["level"]
    resource_level = resource_profile["hierarchy"]["level"]
    user_id = user_profile["identity"]["user_id"]
    resource_owner_id = resource_profile["identity"]["user_id"]

    # REGRA 1: Usuário é SUPERIOR ao recurso → PERMITIDO (para leitura)
    if user_level > resource_level:
        if action == "read":
            return {
                "allowed": True,
                "reason": "hierarchy_superior_can_read_descendants",
            }
        elif action == "write":
            # Para escrita, verificar se usuário pode escrever em descendentes
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
                    "required_permission": "write_descendants",
                }

    # REGRA 2: Mesmo nível → verificar ownership
    elif user_level == resource_level:
        if user_id == resource_owner_id:
            return {"allowed": True, "reason": "self_ownership"}
        else:
            # Recurso lateral → verificar permissões explícitas
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
                        "required_permission": "read_siblings",
                    }
            else:  # write
                return {
                    "allowed": False,
                    "reason": "cannot_write_others_sibling_resources",
                    "required_permission": "write_siblings",
                }

    # REGRA 3: Usuário é INFERIOR ao recurso → NEGADO (para leitura de superiores)
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
                    "required_permission": "read_upwards",
                }
        else:  # write
            return {
                "allowed": False,
                "reason": "cannot_write_upwards",
                "required_permission": "write_upwards",
            }


def can_access(
    user_id: str, resource_owner_id: str, action: str = "read"
) -> Dict[str, Any]:
    """
    Verificação de acesso simplificada (carrega perfis automaticamente).

    Args:
        user_id: ID do usuário solicitante
        resource_owner_id: ID do dono do recurso
        action: Ação desejada ("read" ou "write")

    Returns:
        Resultado da verificação (mesma estrutura de check_hierarchical_access)
    """
    try:
        user_profile = load_profile(user_id)
        resource_profile = load_profile(resource_owner_id)
        return check_hierarchical_access(user_profile, resource_profile, action)
    except FileNotFoundError as e:
        return {"allowed": False, "reason": f"profile_not_found: {str(e)}"}


# ==================== UTILITÁRIOS DE HIERARQUIA ====================


def get_user_level(user_id: str) -> Optional[int]:
    """
    Obtém nível hierárquico do usuário.

    Args:
        user_id: ID do usuário

    Returns:
        Nível hierárquico ou None se perfil não existir
    """
    try:
        profile = load_profile(user_id)
        return profile["hierarchy"]["level"]
    except FileNotFoundError:
        return None


def get_user_ancestors(user_id: str) -> List[str]:
    """
    Obtém ancestrais (caminho até a raiz) do usuário.

    Args:
        user_id: ID do usuário

    Returns:
        Lista de IDs dos ancestrais (do mais próximo à raiz)
    """
    try:
        profile = load_profile(user_id)
        return profile["hierarchy"]["ancestors"]
    except FileNotFoundError:
        return []


def get_user_descendants(user_id: str, max_depth: int = -1) -> List[str]:
    """
    Obtém descendentes do usuário (filhos, netos, etc.).

    Args:
        user_id: ID do usuário
        max_depth: Profundidade máxima (-1 = todos)

    Returns:
        Lista de IDs dos descendentes
    """
    # Nota: Implementação simplificada - precisaria de índice para ser eficiente
    # Por enquanto retorna lista vazia (será implementado quando tivermos BD)
    return []


def get_accessible_users(user_id: str) -> List[str]:
    """
    Obtém lista de usuários que o usuário atual pode acessar.

    Args:
        user_id: ID do usuário

    Returns:
        Lista de IDs de usuários acessíveis
    """
    try:
        profile = load_profile(user_id)
        user_level = profile["hierarchy"]["level"]

        # Regra simplificada: pode acessar usuários do mesmo nível ou inferiores
        # Implementação real precisaria varrer todos os perfis
        # Por enquanto retorna lista vazia
        return []
    except FileNotFoundError:
        return []


# ==================== ATUALIZAÇÃO DE PERFIL ====================


def update_profile_pattern(
    user_id: str, pattern_type: str, data: Dict[str, Any]
) -> bool:
    """
    Atualiza padrão no perfil do usuário (para aprendizado contínuo).

    Args:
        user_id: ID do usuário
        pattern_type: Tipo de padrão (ex: "common_mistakes", "tech_preferences")
        data: Dados do padrão

    Returns:
        True se atualizado com sucesso
    """
    try:
        profile = load_profile(user_id)

        # Atualizar timestamp
        profile["identity"]["updated_at"] = get_timestamp()

        # Adicionar ao learning_engine
        if pattern_type == "common_mistakes":
            if "common_mistakes" not in profile["learning_engine"]:
                profile["learning_engine"]["common_mistakes"] = []
            profile["learning_engine"]["common_mistakes"].append(data)

        # Salvar perfil atualizado
        save_profile(profile)
        return True

    except Exception:
        return False


def get_profile_insights(user_id: str) -> Dict[str, Any]:
    """
    Retorna insights do perfil (para predições).

    Args:
        user_id: ID do usuário

    Returns:
        Dicionário com insights
    """
    try:
        profile = load_profile(user_id)

        return {
            "productivity_peaks": profile["personal_patterns"]["productivity"][
                "peak_hours"
            ],
            "preferred_stacks": profile["personal_patterns"]["tech_preferences"],
            "common_mistakes_count": len(
                profile["learning_engine"].get("common_mistakes", [])
            ),
            "hierarchy_level": profile["hierarchy"]["level"],
            "prediction_accuracy": profile["learning_engine"]["prediction_model"],
        }
    except FileNotFoundError:
        return {}


# ==================== VALIDAÇÃO ====================


def validate_profile(profile: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida estrutura do perfil.

    Args:
        profile: Dicionário com perfil

    Returns:
        Tuple (is_valid, error_messages)
    """
    errors = []

    # Verificar campos obrigatórios
    required_fields = [
        ("identity.user_id", str),
        ("identity.display_name", str),
        ("hierarchy.level", int),
        ("hierarchy.visibility_rules.can_read_upwards", bool),
        ("hierarchy.visibility_rules.can_read_siblings", bool),
        ("hierarchy.visibility_rules.can_read_descendants", bool),
    ]

    for field_path, expected_type in required_fields:
        try:
            # Navegar pelo caminho
            parts = field_path.split(".")
            value = profile
            for part in parts:
                value = value[part]

            if not isinstance(value, expected_type):
                errors.append(f"Campo {field_path} deve ser {expected_type.__name__}")
        except KeyError:
            errors.append(f"Campo obrigatório faltando: {field_path}")

    # Verificar níveis hierárquicos
    level = profile.get("hierarchy", {}).get("level")
    if level is not None and level < 0:
        errors.append("Nível hierárquico não pode ser negativo")

    return (len(errors) == 0, errors)
