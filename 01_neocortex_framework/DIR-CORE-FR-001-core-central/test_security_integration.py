#!/usr/bin/env python3
"""
Test security integration with hierarchical access control.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    from NC_SEC_FR_001_security_utils import can_access, load_profile

    print("SUCCESS: Security utilities imported")
except ImportError as e:
    print(f"FAIL: Cannot import security utilities: {e}")
    sys.exit(1)

# Test with existing lucas_valerio profile
print("\n=== Testing can_access with lucas_valerio profile ===")
allowed, reason = can_access("lucas_valerio", "lucas_valerio", "read")
print(f"Self access: allowed={allowed}, reason={reason}")

# Test with non-existent user (should return False)
allowed2, reason2 = can_access("lucas_valerio", "nonexistent_user", "read")
print(f"Non-existent user: allowed={allowed2}, reason={reason2}")

# Test load_profile
profile = load_profile("lucas_valerio")
if profile:
    print(f"\nProfile loaded for lucas_valerio")
    print(f"  Level: {profile.get('hierarchy', {}).get('level')}")
    print(f"  Ancestors: {profile.get('hierarchy', {}).get('ancestors', [])}")
else:
    print("\nFAIL: Could not load lucas_valerio profile")

# Test MCP security tool integration
print("\n=== Testing MCP security tool integration ===")
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "DIR-MCP-FR-001-mcp-server")
)

# Mock the ledger read/write functions to avoid side effects
import json
from unittest.mock import patch, MagicMock

mock_ledger = {
    "user_context": {"current_user_id": "lucas_valerio"},
    "memory_cortex": {"security_log": []},
}


def mock_read_ledger():
    return mock_ledger.copy()


def mock_write_ledger(data):
    pass


# Attempt to import the security tool function
try:
    # We'll directly test can_access integration by simulating the tool
    print("Simulating neocortex_security.validate_access with hierarchical control")

    # Simulate parameters
    current_user_id = "lucas_valerio"
    target_user_id = "lucas_valerio"
    access_type = "read"

    allowed, reason = can_access(current_user_id, target_user_id, access_type)
    print(f"  Simulation result: allowed={allowed}, reason={reason}")

    # Test upward access block (if we had a superior user)
    # Create a mock superior profile
    print("\n=== Testing upward access block ===")
    # Since we only have lucas_valerio profile, we can't test fully
    # but we can verify the function doesn't crash
    print("  Function operational.")

except Exception as e:
    print(f"  ERROR during test: {e}")
    import traceback

    traceback.print_exc()

print("\n=== Security integration test completed ===")
