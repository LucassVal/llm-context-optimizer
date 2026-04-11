#!/usr/bin/env python3
"""
NC-HUB-FR-001 - NeoCortex MCP Hub (WebSocket Multi-User Server)

Prototype of MCP hub supporting unlimited hierarchical users.
Uses FastMCP WebSocket transport for multi-user connections.
"""

import asyncio
import sys
import json
import logging
import uuid
import time
from pathlib import Path

# Add core directory to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "DIR-CORE-FR-001-core-central"))

# Try to import security utilities for user validation
try:
    from NC_SEC_FR_001_security_utils import can_access, load_profile

    SECURITY_UTILS_AVAILABLE = True
except ImportError:
    SECURITY_UTILS_AVAILABLE = False
    print(
        "WARNING: Security utilities not found. User validation will be limited.",
        file=sys.stderr,
    )

# Try to import FastMCP
try:
    from mcp.server import FastMCP

    FAST_MCP_AVAILABLE = True
except ImportError:
    FAST_MCP_AVAILABLE = False
    print(
        "ERROR: FastMCP not installed. Install with: pip install mcp", file=sys.stderr
    )
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global user session store (in production, use database)
active_sessions = {}  # session_id -> {user_id, profile, connection_info}

# Create MCP instance for the hub
hub_mcp = FastMCP("neocortex-hub")

# ==================== HUB TOOLS ====================


@hub_mcp.tool(name="hub_authenticate")
async def tool_hub_authenticate(user_id: str, session_token: str = "") -> dict:
    """
    Authenticate user and create session.

    Parameters:
        user_id: User identifier (email or username)
        session_token: Existing session token (optional)

    Returns:
        Session information with token and permissions
    """
    global active_sessions

    # Load user profile
    if SECURITY_UTILS_AVAILABLE:
        profile = load_profile(user_id)
        if not profile:
            return {"success": False, "error": f"User profile not found: {user_id}"}
    else:
        # Simulated profile
        profile = {
            "identity": {"user_id": user_id},
            "hierarchy": {"level": 0},
            "permissions": {"roles": ["user"]},
        }

    # Generate session token
    session_id = str(uuid.uuid4())
    token = f"tok_{session_id[:8]}"

    # Store session
    active_sessions[session_id] = {
        "user_id": user_id,
        "profile": profile,
        "created_at": time.time(),
        "last_activity": time.time(),
        "token": token,
    }

    logger.info(f"User authenticated: {user_id} (session: {session_id[:8]})")

    return {
        "success": True,
        "session_id": session_id,
        "token": token,
        "user_id": user_id,
        "profile_summary": {
            "display_name": profile.get("identity", {}).get("display_name", user_id),
            "level": profile.get("hierarchy", {}).get("level", 0),
            "roles": profile.get("permissions", {}).get("roles", []),
        },
        "message": f"Authenticated as {user_id}",
    }


@hub_mcp.tool(name="hub_list_users")
async def tool_hub_list_users(session_id: str, filter_level: int = -1) -> dict:
    """
    List users visible to the current session (respecting hierarchy).

    Parameters:
        session_id: Current session ID
        filter_level: Filter by hierarchy level (-1 = all)

    Returns:
        List of visible users with basic info
    """
    global active_sessions

    if session_id not in active_sessions:
        return {"success": False, "error": "Invalid session"}

    current_session = active_sessions[session_id]
    current_user_id = current_session["user_id"]
    current_profile = current_session["profile"]

    # In a real implementation, we would query a user database
    # For prototype, return active sessions and mock users
    visible_users = []

    # Add current user
    visible_users.append(
        {
            "user_id": current_user_id,
            "display_name": current_profile.get("identity", {}).get(
                "display_name", current_user_id
            ),
            "level": current_profile.get("hierarchy", {}).get("level", 0),
            "status": "active",
        }
    )

    # Add other active sessions (simulating visibility)
    for sid, session in active_sessions.items():
        if sid == session_id:
            continue
        user_id = session["user_id"]
        profile = session["profile"]
        visible_users.append(
            {
                "user_id": user_id,
                "display_name": profile.get("identity", {}).get(
                    "display_name", user_id
                ),
                "level": profile.get("hierarchy", {}).get("level", 0),
                "status": "active",
            }
        )

    # Filter by level if specified
    if filter_level >= 0:
        visible_users = [u for u in visible_users if u["level"] == filter_level]

    # Sort by level (descending)
    visible_users.sort(key=lambda u: u["level"], reverse=True)

    return {
        "success": True,
        "users": visible_users,
        "count": len(visible_users),
        "message": f"Found {len(visible_users)} visible users",
    }


@hub_mcp.tool(name="hub_validate_access")
async def tool_hub_validate_access(
    session_id: str, target_user_id: str, access_type: str = "read"
) -> dict:
    """
    Validate access from current session user to target user.

    Parameters:
        session_id: Current session ID
        target_user_id: Target user ID
        access_type: "read" or "write"

    Returns:
        Access validation result
    """
    global active_sessions

    if session_id not in active_sessions:
        return {"success": False, "error": "Invalid session"}

    current_user_id = active_sessions[session_id]["user_id"]

    if SECURITY_UTILS_AVAILABLE:
        allowed, reason = can_access(current_user_id, target_user_id, access_type)
        access_granted = allowed
    else:
        # Simulate access: allow if same user, else deny
        access_granted = current_user_id == target_user_id
        reason = "simulated_same_user_only"

    logger.info(
        f"Access validation: {current_user_id} -> {target_user_id} ({access_type}) = {access_granted}"
    )

    return {
        "success": True,
        "access_granted": access_granted,
        "current_user_id": current_user_id,
        "target_user_id": target_user_id,
        "access_type": access_type,
        "reason": reason,
        "message": f"Access {'granted' if access_granted else 'denied'}: {reason}",
    }


@hub_mcp.tool(name="hub_get_profile")
async def tool_hub_get_profile(session_id: str, target_user_id: str = "") -> dict:
    """
    Get profile of a user (if accessible).

    Parameters:
        session_id: Current session ID
        target_user_id: Target user ID (empty for current user)

    Returns:
        User profile (limited by visibility rules)
    """
    global active_sessions

    if session_id not in active_sessions:
        return {"success": False, "error": "Invalid session"}

    current_user_id = active_sessions[session_id]["user_id"]

    # Determine target user
    if not target_user_id:
        target_user_id = current_user_id

    # Check access
    if SECURITY_UTILS_AVAILABLE:
        allowed, reason = can_access(current_user_id, target_user_id, "read")
        if not allowed:
            return {
                "success": False,
                "error": f"Access denied to profile of {target_user_id}",
                "reason": reason,
            }

    # Load target profile
    if SECURITY_UTILS_AVAILABLE:
        profile = load_profile(target_user_id)
    else:
        # Simulated profile
        profile = {
            "identity": {"user_id": target_user_id},
            "hierarchy": {"level": 0},
            "permissions": {"roles": ["user"]},
        }

    if not profile:
        return {"success": False, "error": f"Profile not found: {target_user_id}"}

    # Filter sensitive data based on access level
    # For prototype, return full profile
    return {
        "success": True,
        "user_id": target_user_id,
        "profile": profile,
        "message": f"Profile retrieved for {target_user_id}",
    }


# ==================== SERVER STARTUP ====================


async def main():
    """Start the MCP Hub WebSocket server."""
    import argparse

    parser = argparse.ArgumentParser(
        description="NeoCortex MCP Hub - Multi-User WebSocket Server"
    )
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on")
    parser.add_argument(
        "--transport",
        default="websocket",
        choices=["websocket", "stdio"],
        help="Transport protocol",
    )

    args = parser.parse_args()

    logger.info(f"Starting NeoCortex MCP Hub v4.2-cortex")
    logger.info(f"Host: {args.host}:{args.port}")
    logger.info(f"Transport: {args.transport}")
    logger.info(f"Security utilities: {SECURITY_UTILS_AVAILABLE}")
    logger.info(f"Active tools: {len(hub_mcp.tools)}")

    # Start the server with the specified transport
    try:
        if args.transport == "websocket":
            logger.info(f"WebSocket server listening on ws://{args.host}:{args.port}")
            await hub_mcp.run(transport="websocket", host=args.host, port=args.port)
        else:
            logger.info("Running in stdio mode (single connection)")
            await hub_mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Hub stopped by user")
    except Exception as e:
        logger.error(f"Hub error: {e}")
        raise


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
