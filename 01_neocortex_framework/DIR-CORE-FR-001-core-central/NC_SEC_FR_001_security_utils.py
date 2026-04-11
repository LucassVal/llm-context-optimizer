#!/usr/bin/env python3
"""
NC-SEC-FR-001 - Security Utilities for NeoCortex Framework

Hierarchical access control and profile validation.
Implements can_access function based on unlimited hierarchical levels.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# ==================== CONSTANTS ====================

PROJECT_ROOT = Path(__file__).parent.parent
PROFILES_DIR = PROJECT_ROOT / "DIR-PRF-FR-001-profiles-main"
USERS_DIR = PROFILES_DIR / "users"

# ==================== PROFILE LOADING ====================


def load_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Load user profile from users/{user_id}/NC-PRF-USR-001-profile.json

    Returns None if profile not found.
    """
    profile_path = USERS_DIR / user_id / "NC-PRF-USR-001-profile.json"
    if not profile_path.exists():
        # Fallback: check if profile exists in legacy location
        profile_path = PROFILES_DIR / f"profile_{user_id}.json"
        if not profile_path.exists():
            return None

    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_profile(user_id: str, profile: Dict[str, Any]) -> bool:
    """Save user profile to disk."""
    try:
        profile_dir = USERS_DIR / user_id
        profile_dir.mkdir(parents=True, exist_ok=True)
        profile_path = profile_dir / "NC-PRF-USR-001-profile.json"

        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


# ==================== HIERARCHICAL ACCESS CONTROL ====================


def can_access(
    current_user_id: str, target_user_id: str, access_type: str = "read"
) -> Tuple[bool, str]:
    """
    Determine if current user can access target user's resources.

    Rules:
    - Users can read equal, lateral, and inferior levels (siblings, descendants)
    - Users CANNOT read superior levels (ancestors)
    - Write permissions are more restrictive (default: only self and descendants)

    Parameters:
        current_user_id: ID of user making the request
        target_user_id: ID of user whose resources are being accessed
        access_type: "read" or "write"

    Returns:
        Tuple (allowed: bool, reason: str)
    """
    # Same user always has access
    if current_user_id == target_user_id:
        return True, "same_user"

    # Load profiles
    current_profile = load_profile(current_user_id)
    target_profile = load_profile(target_user_id)

    if not current_profile:
        return False, f"current_user_profile_not_found:{current_user_id}"
    if not target_profile:
        return False, f"target_user_profile_not_found:{target_user_id}"

    # Extract hierarchy info
    current_hierarchy = current_profile.get("hierarchy", {})
    target_hierarchy = target_profile.get("hierarchy", {})

    current_level = current_hierarchy.get("level", 0)
    target_level = target_hierarchy.get("level", 0)

    current_ancestors = current_hierarchy.get("ancestors", [])
    target_ancestors = target_hierarchy.get("ancestors", [])

    # Rule 1: Cannot read upwards (target level < current level)
    if target_level < current_level:
        return (
            False,
            f"access_upwards_blocked:target_level_{target_level}_current_level_{current_level}",
        )

    # Rule 2: For read access, allow equal, lateral, and inferior levels
    if access_type == "read":
        # Check visibility rules
        visibility = current_hierarchy.get("visibility_rules", {})
        can_read_upwards = visibility.get("can_read_upwards", False)
        can_read_siblings = visibility.get("can_read_siblings", True)
        can_read_descendants = visibility.get("can_read_descendants", True)

        # If target is superior and can_read_upwards is False, block
        if target_level < current_level and not can_read_upwards:
            return False, "upwards_read_blocked_by_visibility_rules"

        # If target is sibling (same level) and can_read_siblings is False, block
        if target_level == current_level and not can_read_siblings:
            # Verify they're not the same user (already handled)
            # Check if they share parent (simplified: assume same level = sibling)
            return False, "sibling_read_blocked_by_visibility_rules"

        # If target is descendant (inferior) and can_read_descendants is False, block
        if target_level > current_level and not can_read_descendants:
            return False, "descendant_read_blocked_by_visibility_rules"

        # Additional check: target must be in current user's hierarchy tree
        # i.e., target's ancestors include current user's ID or current user is ancestor
        if (
            current_user_id not in target_ancestors
            and target_user_id not in current_ancestors
        ):
            # Check if they share a common ancestor (same organization)
            # For simplicity, allow if both have at least one common ancestor
            common_ancestors = set(current_ancestors) & set(target_ancestors)
            if not common_ancestors:
                return False, "no_common_hierarchy_branch"

        return True, "read_access_granted"

    # Rule 3: Write access is more restrictive
    elif access_type == "write":
        # Default: can write only to self and descendants
        visibility = current_hierarchy.get("visibility_rules", {})
        write_permission = visibility.get("write_permission", ["self", "descendants"])

        if "self" in write_permission and current_user_id == target_user_id:
            return True, "write_to_self_allowed"

        if "descendants" in write_permission and target_level > current_level:
            # Verify target is indeed a descendant
            if current_user_id in target_ancestors:
                return True, "write_to_descendant_allowed"

        if "siblings" in write_permission and target_level == current_level:
            return True, "write_to_sibling_allowed"

        if "ancestors" in write_permission and target_level < current_level:
            return True, "write_to_ancestor_allowed"

        return False, f"write_access_denied:permissions_{write_permission}"

    return False, f"unknown_access_type:{access_type}"


# ==================== PROFILE VALIDATION ====================


def validate_profile_structure(profile: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate profile against NeoCortex schema."""
    required_sections = ["identity", "hierarchy", "permissions"]
    for section in required_sections:
        if section not in profile:
            return False, f"missing_section:{section}"

    identity = profile["identity"]
    if "user_id" not in identity:
        return False, "missing_user_id"

    hierarchy = profile["hierarchy"]
    if "level" not in hierarchy:
        return False, "missing_hierarchy_level"

    # Level must be integer >= 0
    try:
        level = int(hierarchy["level"])
        if level < 0:
            return False, "hierarchy_level_negative"
    except (TypeError, ValueError):
        return False, "hierarchy_level_not_integer"

    return True, "valid"


# ==================== SESSION MANAGEMENT ====================


def get_current_session_profile() -> Optional[Dict[str, Any]]:
    """Load current session profile from ledger."""
    ledger_path = (
        PROJECT_ROOT
        / "DIR-CORE-FR-001-core-central"
        / "NC-LED-FR-001-framework-ledger.json"
    )
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            ledger = json.load(f)

        user_context = ledger.get("user_context", {})
        user_id = user_context.get("current_user_id")
        if not user_id:
            return None

        return load_profile(user_id)
    except Exception:
        return None


# ==================== TEST FUNCTIONS ====================

if __name__ == "__main__":
    # Simple test
    print("Testing hierarchical access control...")

    # Create mock profiles for testing
    root_profile = {
        "identity": {"user_id": "root", "display_name": "Root Admin"},
        "hierarchy": {
            "level": 0,
            "parent_id": None,
            "children_ids": ["org1"],
            "ancestors": [],
            "descendants_count": 5,
            "visibility_rules": {
                "can_read_upwards": True,
                "can_read_siblings": True,
                "can_read_descendants": True,
                "write_permission": ["self", "descendants", "siblings", "ancestors"],
            },
        },
        "permissions": {"roles": ["admin"], "scopes": ["*"]},
    }

    org_profile = {
        "identity": {"user_id": "org1", "display_name": "Organization 1"},
        "hierarchy": {
            "level": 1,
            "parent_id": "root",
            "children_ids": ["user1"],
            "ancestors": ["root"],
            "descendants_count": 3,
            "visibility_rules": {
                "can_read_upwards": False,
                "can_read_siblings": True,
                "can_read_descendants": True,
                "write_permission": ["self", "descendants"],
            },
        },
        "permissions": {"roles": ["manager"], "scopes": ["team:manage"]},
    }

    user_profile = {
        "identity": {"user_id": "user1", "display_name": "User 1"},
        "hierarchy": {
            "level": 2,
            "parent_id": "org1",
            "children_ids": [],
            "ancestors": ["root", "org1"],
            "descendants_count": 0,
            "visibility_rules": {
                "can_read_upwards": False,
                "can_read_siblings": True,
                "can_read_descendants": True,
                "write_permission": ["self"],
            },
        },
        "permissions": {
            "roles": ["developer"],
            "scopes": ["project:read", "project:write"],
        },
    }

    # Save test profiles
    test_dir = USERS_DIR / "test_hierarchy"
    test_dir.mkdir(parents=True, exist_ok=True)

    for user_id, profile in [
        ("root", root_profile),
        ("org1", org_profile),
        ("user1", user_profile),
    ]:
        profile_path = test_dir / f"{user_id}_profile.json"
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)

    # Test access patterns
    tests = [
        ("user1", "user1", "read", True, "self read"),
        ("user1", "org1", "read", False, "upwards read blocked"),
        ("org1", "user1", "read", True, "descendant read allowed"),
        ("root", "user1", "read", True, "root can read descendant"),
        ("user1", "root", "read", False, "user cannot read root"),
    ]

    for curr, target, access_type, expected, desc in tests:
        # Temporarily load from test directory
        allowed, reason = can_access(curr, target, access_type)
        status = "PASS" if allowed == expected else "FAIL"
        print(
            f"{status}: {desc} ({curr} -> {target}): allowed={allowed}, reason={reason}"
        )

    print("\nTest completed.")
