#!/usr/bin/env python3
"""
Example: NeoCortex Hexagonal Architecture

Demonstrates the use of Repository Pattern and Services in NeoCortex.
This shows how business logic is separated from storage implementation.
"""

import json
from pathlib import Path

# Import the new architecture components
from neocortex.core import (
    get_cortex_service,
    get_ledger_service,
    get_lobe_service,
    get_profile_service,
)

from neocortex.repositories import (
    FileSystemRepositoryFactory,
    FileSystemCortexRepository,
    FileSystemLedgerRepository,
)

from neocortex.schemas import LEDGER_SCHEMA, A2A_MESSAGE_SCHEMA


def demonstrate_repository_pattern():
    """Demonstrate Repository Pattern usage."""
    print("=" * 60)
    print("REPOSITORY PATTERN DEMONSTRATION")
    print("=" * 60)

    # 1. Create repository instances using factory
    factory = FileSystemRepositoryFactory()

    cortex_repo = factory.create_cortex_repository()
    ledger_repo = factory.create_ledger_repository()
    profile_repo = factory.create_profile_repository()
    lobe_repo = factory.create_lobe_repository()

    print("[OK] Created repository instances for all storage types")
    print(f"  - Cortex repository: {type(cortex_repo).__name__}")
    print(f"  - Ledger repository: {type(ledger_repo).__name__}")
    print(f"  - Profile repository: {type(profile_repo).__name__}")
    print(f"  - Lobe repository: {type(lobe_repo).__name__}")

    # 2. Demonstrate cortex operations
    print("\n2. Cortex Operations:")
    cortex_content = cortex_repo.read_cortex()
    print(f"   - Cortex size: {len(cortex_content)} characters")

    aliases = cortex_repo.get_aliases()
    print(f"   - Aliases found: {len(aliases)}")
    if aliases:
        for alias, value in list(aliases.items())[:3]:
            print(f"     * {alias} = {value}")

    # 3. Demonstrate ledger operations
    print("\n3. Ledger Operations:")
    ledger = ledger_repo.read_ledger()
    print(f"   - Ledger sections: {len(ledger)}")
    print(f"   - NeoCortex version: {ledger.get('neocortex_version', 'N/A')}")

    # 4. Demonstrate lobe operations
    print("\n4. Lobe Operations:")
    lobes = lobe_repo.list_lobes()
    print(f"   - Total lobes: {len(lobes)}")
    if lobes:
        for lobe in lobes[:3]:
            print(f"     * {lobe}")

    return cortex_repo, ledger_repo, profile_repo, lobe_repo


def demonstrate_service_layer():
    """Demonstrate Service Layer usage."""
    print("\n" + "=" * 60)
    print("SERVICE LAYER DEMONSTRATION")
    print("=" * 60)

    # 1. Get service instances (singleton pattern)
    cortex_service = get_cortex_service()
    ledger_service = get_ledger_service()
    lobe_service = get_lobe_service()
    profile_service = get_profile_service()

    print("[OK] Retrieved service instances (singleton pattern)")

    # 2. Demonstrate cortex service
    print("\n2. Cortex Service:")
    cortex_info = cortex_service.get_full_cortex()
    print(f"   - Cortex metadata: {cortex_info['metadata']}")

    # Get aliases via service
    aliases = cortex_service.get_aliases()
    print(f"   - Aliases via service: {len(aliases)}")

    # Validate an alias
    if aliases:
        sample_alias = list(aliases.keys())[0]
        validation = cortex_service.validate_alias(sample_alias)
        print(f"   - Validation for '{sample_alias}': {validation['valid']}")

    # 3. Demonstrate ledger service
    print("\n3. Ledger Service:")
    ledger_validation = ledger_service.validate_ledger()
    print(f"   - Ledger valid: {ledger_validation['valid']}")

    session_metrics = ledger_service.get_session_metrics()
    print(f"   - Session metrics: {session_metrics}")

    # 4. Demonstrate lobe service
    print("\n4. Lobe Service:")
    lobes_info = lobe_service.list_lobes()
    print(f"   - Total lobes: {lobes_info['total']}")
    print(f"   - Categories: {lobes_info['categories']}")

    # 5. Demonstrate profile service
    print("\n5. Profile Service:")
    profiles_info = profile_service.list_profiles()
    print(f"   - Total profiles: {profiles_info['total']}")
    print(f"   - Access levels: {profiles_info['access_levels']}")

    return cortex_service, ledger_service, lobe_service, profile_service


def demonstrate_json_schemas():
    """Demonstrate JSON Schema contracts."""
    print("\n" + "=" * 60)
    print("JSON SCHEMA CONTRACTS")
    print("=" * 60)

    if LEDGER_SCHEMA:
        print("[OK] Ledger schema loaded successfully")
        print(f"  - Title: {LEDGER_SCHEMA.get('title', 'N/A')}")
        print(f"  - Version: {LEDGER_SCHEMA.get('$schema', 'N/A')}")
        print(f"  - Required fields: {len(LEDGER_SCHEMA.get('required', []))}")
    else:
        print("[ERROR] Ledger schema not available")

    if A2A_MESSAGE_SCHEMA:
        print("\n[OK] A2A Message schema loaded successfully")
        print(f"  - Title: {A2A_MESSAGE_SCHEMA.get('title', 'N/A')}")
        message_types = A2A_MESSAGE_SCHEMA["properties"]["type"]["enum"]
        print(f"  - Message types: {len(message_types)}")
        print(f"    {', '.join(message_types[:5])}...")
    else:
        print("\n[ERROR] A2A Message schema not available")

    # Example: Create a valid A2A message
    print("\nExample A2A Message:")
    example_message = {
        "message_id": "123e4567-e89b-12d3-a456-426614174000",
        "sender": "agent-t0",
        "receiver": "agent-security",
        "timestamp": "2026-04-10T14:30:00Z",
        "type": "request",
        "payload": {
            "action": "validate_access",
            "parameters": {
                "user_id": "developer",
                "resource": "cortex",
                "operation": "read",
            },
            "expected_response": "immediate",
        },
        "metadata": {
            "priority": 5,
            "correlation_id": "123e4567-e89b-12d3-a456-426614174001",
        },
        "version": "1.0.0",
    }

    print(json.dumps(example_message, indent=2))


def demonstrate_future_integrations():
    """Demonstrate how the architecture enables future integrations."""
    print("\n" + "=" * 60)
    print("FUTURE INTEGRATION PREPARATION")
    print("=" * 60)

    print("1. Hexagonal Architecture enables:")
    print("   - Swap filesystem storage for database/hub storage")
    print("   - Keep same business logic (services)")
    print("   - Only change repository implementations")

    print("\n2. JSON Schemas enable:")
    print("   - Language-agnostic data exchange")
    print("   - Rust/Go implementations using same contracts")
    print("   - Validation across system boundaries")

    print("\n3. Repository Pattern enables:")
    print("   - FileSystemRepository (current)")
    print("   - HubRepository (future WebSocket hub)")
    print("   - DatabaseRepository (future SQL/NoSQL)")
    print("   - MockRepository (for testing)")

    print("\n4. A2A Protocol preparation:")
    print("   - Message schema defined")
    print("   - Can add A2A adapter without rewriting business logic")
    print("   - Enables multi-agent collaboration")


def main():
    """Main demonstration function."""
    print("NEOCTEX HEXAGONAL ARCHITECTURE DEMONSTRATION")
    print("=" * 60)

    try:
        # Demonstrate the new architecture
        repos = demonstrate_repository_pattern()
        services = demonstrate_service_layer()
        demonstrate_json_schemas()
        demonstrate_future_integrations()

        print("\n" + "=" * 60)
        print("ARCHITECTURE VALIDATION COMPLETE")
        print("=" * 60)
        print("[OK] Repository Pattern implemented")
        print("[OK] Service Layer implemented")
        print("[OK] JSON Schemas defined")
        print("[OK] Hexagonal separation achieved")
        print("[OK] Future integration prepared")

    except Exception as e:
        print(f"\n[ERROR] Error during demonstration: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
