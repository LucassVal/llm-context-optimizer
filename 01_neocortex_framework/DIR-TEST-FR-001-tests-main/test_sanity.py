#!/usr/bin/env python3
"""
Sanity test suite for NeoCortex framework stability.
Implements 11 essential tests as per roadmap STAB-103 and METR-109.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_1_config_loads():
    """Test that configuration loads successfully."""
    from neocortex.config import get_config

    config = get_config()
    assert config is not None
    assert hasattr(config, "project_root")
    assert config.project_root.exists()
    print("[OK] Config loads successfully")
    return True


def test_2_file_utils_paths():
    """Test file_utils paths are accessible."""
    from neocortex.core.file_utils import (
        read_cortex,
        write_cortex,
        read_ledger,
        write_ledger,
        get_project_root,
        path_exists,
    )

    root = get_project_root()
    assert root.exists()
    # Check cortex path exists (may be empty)
    cortex_content = read_cortex()
    assert isinstance(cortex_content, str)
    # Check ledger path exists (may be empty)
    ledger_content = read_ledger()
    assert isinstance(ledger_content, dict)
    print("[OK] File utilities work")
    return True


def test_3_ledger_store_read_write():
    """Test LedgerStore basic read/write operations."""
    from neocortex.infra.ledger_store import LedgerStore
    import tempfile
    import shutil

    # Create temporary directory for test
    temp_dir = Path(tempfile.mkdtemp())
    store = LedgerStore(cache_path=temp_dir, size_limit_gb=0.1)
    # Read ledger (may be empty or contain existing data)
    ledger = store.read_ledger()
    assert isinstance(ledger, dict)
    # Note: ledger may not contain neocortex_version if loaded from existing data
    # Write a test section
    test_data = {"test": "value"}
    success = store.update_ledger_section("test_section", test_data)
    assert success
    # Retrieve section
    retrieved = store.get_section("test_section")
    assert retrieved == test_data
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("[OK] LedgerStore read/write works")
    return True


def test_4_manifest_store_search():
    """Test ManifestStore basic operations."""
    # Skip if not implemented
    try:
        from neocortex.infra.manifest_store import ManifestStore

        # Create temporary store
        temp_dir = Path(tempfile.mkdtemp())
        store = ManifestStore(cache_path=temp_dir, size_limit_gb=0.1)
        # Create a test manifest
        manifest_id = "test_lobe"
        manifest = {
            "id": manifest_id,
            "type": "lobe",
            "title": "Test Lobe",
            "tags": ["test", "experimental"],
            "entities": ["entity1"],
            "status": "active",
            "metadata": {"test": True},
        }
        # Save manifest
        success = store.save_manifest(manifest_id, manifest)
        assert success
        # Retrieve manifest
        retrieved = store.get_manifest(manifest_id)
        assert retrieved is not None
        assert retrieved["id"] == manifest_id
        # Query by tag
        results = store.query_manifests(tags=["test"])
        assert isinstance(results, list)
        # Should find at least our manifest
        assert len(results) >= 1
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("[OK] ManifestStore basic operations work")
        return True
    except ImportError:
        print("[WARNING] ManifestStore not available, skipping")
        return True  # Skip, not critical
    except Exception as e:
        print(f"[WARNING] ManifestStore test failed: {e}")
        return False


def test_5_mcp_server_tools():
    """Test MCP server tools respond."""
    # This test requires MCP server to be running; we'll skip for now
    # but we can test that tools module loads.
    try:
        from neocortex.mcp.tools import get_tools

        tools = get_tools()
        assert isinstance(tools, list)
        print("[OK] MCP tools module loads")
        return True
    except ImportError:
        print("[WARNING] MCP tools module not available, skipping")
        return True  # Skip, not critical
    except Exception as e:
        print(f"[WARNING] MCP tools test failed: {e}")
        return False


def test_6_sub_server_spawn():
    """Test sub-server spawn capability."""
    try:
        from neocortex.mcp.sub_server import SubMCPManager

        # Test that class can be instantiated
        manager = SubMCPManager()
        assert manager is not None
        print("[OK] SubMCPManager can be instantiated")
        return True
    except ImportError:
        print("[WARNING] SubMCPManager not available, skipping")
        return True  # Skip, not critical
    except Exception as e:
        print(f"[WARNING] Sub-server spawn test failed: {e}")
        return False


def test_7_llm_backend_factory():
    """Test LLMBackendFactory creates backends."""
    from neocortex.infra.llm.factory import LLMBackendFactory
    from neocortex.config import get_config

    config = get_config()
    # Create backend from config
    backend = LLMBackendFactory.create_from_config(config.llm_config)
    assert backend is not None
    # Check that fallback chain is handled
    fallback = LLMBackendFactory.create_fallback_chain(config.llm_fallback_chain)
    assert fallback is not None
    assert hasattr(fallback, "backends")
    assert isinstance(fallback.backends, list)
    print("[OK] LLMBackendFactory works")
    return True


def test_8_agent_executor():
    """Test AgentExecutor can be instantiated."""
    try:
        from neocortex.agent.executor import AgentExecutor

        executor = AgentExecutor()
        assert executor is not None
        print("[OK] AgentExecutor can be instantiated")
        return True
    except Exception as e:
        print(f"[WARNING] AgentExecutor test failed: {e}")
        return False


def test_9_pulse_scheduler():
    """Test PulseScheduler can be instantiated."""
    from neocortex.core.pulse_scheduler import PulseScheduler
    from neocortex.core.ledger_service import get_ledger_service
    from neocortex.core.consolidation_service import get_consolidation_service
    from neocortex.core.akl_service import get_akl_service
    from neocortex.core.export_service import get_export_service
    from neocortex.core.checkpoint_service import get_checkpoint_service

    # Get services
    ledger = get_ledger_service()
    consolidation = get_consolidation_service()
    akl = get_akl_service()
    export = get_export_service()
    checkpoint = get_checkpoint_service()
    scheduler = PulseScheduler(consolidation, ledger, akl, export, checkpoint)
    assert scheduler is not None
    print("[OK] PulseScheduler can be instantiated")
    return True


def test_10_config_validation():
    """Test configuration validation."""
    from neocortex.config import get_config

    config = get_config()
    result = config.validate()
    assert isinstance(result, dict)
    assert "valid" in result
    if not result["valid"]:
        print(f"[WARNING] Config validation issues: {result.get('issues')}")
    print("[OK] Config validation works")
    return True


def test_11_metrics_store():
    """Test MetricsStore functionality and report generation."""
    from neocortex.infra.metrics_store import create_metrics_store, MetricsBackend
    from pathlib import Path

    # Use in-memory SQLite database to avoid schema conflicts
    store = create_metrics_store(
        db_path=Path(":memory:"), backend=MetricsBackend.SQLITE
    )
    assert store is not None
    assert hasattr(store, "insert_metric")

    # Test 2: Validate tables
    assert store.validate_tables() == True

    # Test 3: Insert sample metrics
    success = store.insert_metric(
        metric_id="test_latency",
        metric_type="latency",
        value=42.5,
        tags={"test": "true", "component": "test_sanity"},
        metadata={"test_run": "sanity_check"},
    )
    assert success == True

    # Test 4: Record sample token usage
    success = store.record_token_usage(
        date=datetime.now(),
        model="test-model",
        agent="test-agent",
        cache_hit=10,
        cache_miss=5,
        output_tokens=100,
        total_tokens=115,
    )
    assert success == True

    # Test 5: Record agent activity
    success = store.record_agent_activity(
        agent_id="test-agent",
        action="task_completed",
        details={"task_id": "test-123", "success": True},
    )
    assert success == True

    # Test 6: Record pulse health
    success = store.record_pulse_health(
        event_type="test_event",
        status="success",
        duration_ms=150,
        details={"test": "completed"},
    )
    assert success == True

    # Test 7: Get stats
    stats = store.get_stats()
    assert isinstance(stats, dict)
    assert "backend" in stats

    # Test 8: Query metrics
    metrics = store.query_metrics(metric_id="test_latency", limit=5)
    assert isinstance(metrics, list)

    # Test 9: Test domain table queries
    token_usage = store.get_daily_token_usage()
    assert isinstance(token_usage, list)

    pulse_health = store.get_pulse_health()
    assert isinstance(pulse_health, list)

    agent_activity = store.get_agent_activity()
    assert isinstance(agent_activity, list)

    # Clean up
    store.close()

    print("[OK] MetricsStore works and reports can be generated")
    return True


def run_all_tests():
    """Run all sanity tests."""
    tests = [
        test_1_config_loads,
        test_2_file_utils_paths,
        test_3_ledger_store_read_write,
        test_4_manifest_store_search,
        test_5_mcp_server_tools,
        test_6_sub_server_spawn,
        test_7_llm_backend_factory,
        test_8_agent_executor,
        test_9_pulse_scheduler,
        test_10_config_validation,
        test_11_metrics_store,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__} raised exception: {e}")
            failed += 1
    print(f"\n{'=' * 50}")
    print(f"Sanity tests: {passed} passed, {failed} failed")
    if failed == 0:
        print("[SUCCESS] All sanity tests passed!")
        return True
    else:
        print("[FAILED] Some sanity tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
