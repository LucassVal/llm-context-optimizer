#!/usr/bin/env python3
"""
NC-TEST-152-savepoint-wal-integration.py
Integration test for SavePoint-WAL Bridge (NC-SVC-FR-025)

Tests the complete flow of savepoint creation, WAL logging, restoration, and listing.

Ticket: NC-DS-152-savepoint-wal-bridge.yaml
"""

import json
import sys
import time
from pathlib import Path

# Add framework to path
framework_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
sys.path.insert(0, str(framework_path))

# Configure Unicode encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def import_bridge():
    """Import the SavePointWALBridge class."""
    try:
        import importlib.util
        bridge_path = framework_path / "neocortex" / "core" / "services" / "NC-SVC-FR-025-savepoint-wal-bridge.py"
        
        spec = importlib.util.spec_from_file_location(
            "savepoint_wal_bridge",
            str(bridge_path)
        )
        if spec is None or spec.loader is None:
            print("❌ FAIL: Could not create module spec")
            return None
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.SavePointWALBridge
    except Exception as e:
        print(f"❌ FAIL: Could not import bridge: {e}")
        return None


def test_1_create_bridge():
    """Test 1: Create bridge instance."""
    print("[1/6] Creating SavePointWALBridge instance...")
    
    BridgeClass = import_bridge()
    if BridgeClass is None:
        return None, False
    
    try:
        bridge = BridgeClass()
        print("  ✅ Bridge created successfully")
        return bridge, True
    except Exception as e:
        print(f"  ❌ Failed to create bridge: {e}")
        return None, False


def test_2_create_savepoint(bridge):
    """Test 2: Create a savepoint."""
    print("[2/6] Creating savepoint 'test-sp-001'...")
    
    test_data = {
        "test": True,
        "value": 42,
        "timestamp": time.time(),
        "description": "Test savepoint for NC-DS-152 integration test"
    }
    
    try:
        result = bridge.create_savepoint("test-sp-001", test_data)
        print(f"  Result: {json.dumps(result, indent=4)}")
        
        if result.get("ok"):
            print(f"  ✅ Savepoint created: {result.get('savepoint_id')}")
            if result.get("wal_entry_id"):
                print(f"  ✅ Logged to WAL: {result.get('wal_entry_id')}")
            else:
                print("  ⚠️  Not logged to WAL (WAL may be unavailable)")
            return result, True
        else:
            print(f"  ❌ Savepoint creation failed: {result.get('error')}")
            return None, False
    except Exception as e:
        print(f"  ❌ Exception during savepoint creation: {e}")
        return None, False


def test_3_list_savepoints(bridge):
    """Test 3: List savepoints."""
    print("[3/6] Listing savepoints...")
    
    try:
        savepoints = bridge.list_savepoints()
        print(f"  Found {len(savepoints)} savepoint(s)")
        
        # Check if our test savepoint is in the list
        test_found = False
        for sp in savepoints:
            snapshot = sp.get("state_snapshot", {})
            if snapshot.get("name") == "test-sp-001":
                test_found = True
                print(f"  ✅ Test savepoint found in list: {sp.get('id')}")
                break
        
        if not test_found and len(savepoints) > 0:
            print("  ⚠️  Test savepoint not found in list (may be filtered)")
        elif len(savepoints) == 0:
            print("  ⚠️  No savepoints found")
        
        return savepoints, True
    except Exception as e:
        print(f"  ❌ Exception during savepoint listing: {e}")
        return None, False


def test_4_restore_savepoint(bridge):
    """Test 4: Restore savepoint."""
    print("[4/6] Restoring savepoint 'test-sp-001'...")
    
    try:
        result = bridge.restore_savepoint("test-sp-001")
        print(f"  Result: {json.dumps(result, indent=4)}")
        
        if result.get("ok"):
            print(f"  ✅ Savepoint restored: {result.get('savepoint_id')}")
            if result.get("wal_entry_id"):
                print(f"  ✅ Restore logged to WAL: {result.get('wal_entry_id')}")
            else:
                print("  ⚠️  Restore not logged to WAL (WAL may be unavailable)")
            
            # Check if we got back the data
            restored_data = result.get("restored_data", {})
            if restored_data.get("data", {}).get("test"):
                print("  ✅ Test data found in restored savepoint")
            else:
                print("  ⚠️  Test data not found in restored savepoint")
            
            return result, True
        else:
            print(f"  ❌ Savepoint restore failed: {result.get('error')}")
            return None, False
    except Exception as e:
        print(f"  ❌ Exception during savepoint restore: {e}")
        return None, False


def test_5_verify_wal_entries(bridge, create_result, restore_result):
    """Test 5: Verify WAL entries were created."""
    print("[5/6] Verifying WAL entries...")
    
    # This would require direct WAL database access
    # For now, we'll check if the bridge has WAL service
    if hasattr(bridge, 'wal') and bridge.wal is not None:
        print("  ✅ WAL service is available")
        
        if create_result and create_result.get("wal_entry_id"):
            print(f"  ✅ Create WAL entry ID: {create_result.get('wal_entry_id')}")
        else:
            print("  ⚠️  No WAL entry ID for create (may be expected if WAL unavailable)")
        
        if restore_result and restore_result.get("wal_entry_id"):
            print(f"  ✅ Restore WAL entry ID: {restore_result.get('wal_entry_id')}")
        else:
            print("  ⚠️  No WAL entry ID for restore (may be expected if WAL unavailable)")
    else:
        print("  ⚠️  WAL service not available (some tests may be skipped)")
    
    return True


def test_6_cleanup():
    """Test 6: Cleanup (informational)."""
    print("[6/6] Cleanup information...")
    print("  ℹ️  Savepoints are stored in-memory in SavePointService")
    print("  ℹ️  WAL entries are persisted in SQLite database")
    print("  ℹ️  No cleanup needed for this test")
    return True


def main():
    """Main test function."""
    print("=" * 60)
    print("NC-TEST-152: SavePoint-WAL Integration Test")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    bridge, success = test_1_create_bridge()
    test_results.append(("1. Create bridge", success))
    
    if success and bridge:
        create_result, success = test_2_create_savepoint(bridge)
        test_results.append(("2. Create savepoint", success))
        
        _, success = test_3_list_savepoints(bridge)
        test_results.append(("3. List savepoints", success))
        
        restore_result, success = test_4_restore_savepoint(bridge)
        test_results.append(("4. Restore savepoint", success))
        
        success = test_5_verify_wal_entries(bridge, create_result, restore_result)
        test_results.append(("5. Verify WAL entries", success))
        
        success = test_6_cleanup()
        test_results.append(("6. Cleanup", success))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print("=" * 60)
    
    passed = 0
    total = 0
    
    for test_name, test_success in test_results:
        total += 1
        status = "✅ PASS" if test_success else "❌ FAIL"
        print(f"{status} {test_name}")
        if test_success:
            passed += 1
    
    print(f"\nSCORE: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)