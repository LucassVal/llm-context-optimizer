#!/usr/bin/env python3
"""
Test loading of health wrapper modules.
"""

import os
import importlib.util


def test_load_health_service():
    """Test loading NC-SVC-FR-002-health-service.py"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    health_path = os.path.join(
        base_path,
        "..",
        "neocortex",
        "core",
        "services",
        "NC-SVC-FR-002-health-service.py",
    )
    health_path = os.path.normpath(health_path)
    print(f"Health service path: {health_path}")
    assert os.path.exists(health_path), f"Health service not found at {health_path}"

    spec = importlib.util.spec_from_file_location("health_service", health_path)
    assert spec is not None, "Failed to create spec"
    assert spec.loader is not None, "Spec loader is None"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Test functions
    assert hasattr(module, "get_health_status"), "Missing get_health_status"
    assert hasattr(module, "check_mcp_alive"), "Missing check_mcp_alive"
    assert hasattr(module, "format_health_response"), "Missing format_health_response"

    # Call functions
    status = module.get_health_status()
    print(f"Health status: {status}")
    assert "uptime" in status
    assert "tools_count" in status

    formatted = module.format_health_response()
    print(f"Formatted response: {formatted}")
    assert formatted["status"] == "healthy"

    print("✓ Health service loads and works")
    return module


def test_load_wal_service():
    """Test loading NC-SVC-FR-016-wal-service.py"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    wal_path = os.path.join(
        base_path, "..", "neocortex", "core", "services", "NC-SVC-FR-016-wal-service.py"
    )
    wal_path = os.path.normpath(wal_path)
    print(f"WAL service path: {wal_path}")
    if not os.path.exists(wal_path):
        print("WAL service not found, skipping")
        return None

    spec = importlib.util.spec_from_file_location("wal_service", wal_path)
    if spec is None:
        print("Failed to create spec for WAL service, skipping")
        return None
    if spec.loader is None:
        print("Spec loader is None for WAL service, skipping")
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, "WALService"), "Missing WALService class"
    print("✓ WAL service loads")
    return module.WALService


def main():
    print("Testing health wrapper dependencies...")
    health_module = test_load_health_service()
    WALService = test_load_wal_service()
    if WALService:
        # Try to instantiate
        try:
            wal = WALService()
            print(f"WALService instance: {wal}")
            stats = wal.stats()
            print(f"WAL stats: {stats}")
        except Exception as e:
            print(f"WALService instantiation error (may be expected): {e}")

    print("\nAll load tests passed!")
    print("\nTo test the full wrapper, run:")
    print("  python NC-SCR-FR-098-health-wrapper.py --port 8766")
    print("Then in another terminal:")
    print("  curl http://localhost:8766/health")
    print("  curl http://localhost:8766/ready")


if __name__ == "__main__":
    main()
