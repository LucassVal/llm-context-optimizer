#!/usr/bin/env python3
"""
Test script for picoclaw server integration tests
"""

import sys
import os
import time
import json
import urllib.request
import urllib.error

# Add the neocortex framework to path
neocortex_path = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework"
sys.path.insert(0, neocortex_path)

def test_server_lifecycle():
    """Test PLC-001: server-startup"""
    print("=== Test PLC-001: server-startup ===")
    
    try:
        # Import and start server
        import importlib.util
        server_path = os.path.join(neocortex_path, "neocortex", "core", "services", "NC-SVC-FR-019-picoclaw-server.py")
        spec = importlib.util.spec_from_file_location("picoclaw_server", server_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        # Start server
        print("Starting picoclaw server...")
        start_result = mod.start()
        print(f"Start result: {start_result}")
        
        if not start_result.get("ok"):
            print("❌ FAILED: Server failed to start")
            return False
        
        # Wait for server to initialize
        time.sleep(2)
        
        # Test HTTP health endpoint
        try:
            response = urllib.request.urlopen("http://localhost:18790/health", timeout=5)
            health_data = json.loads(response.read())
            print(f"HTTP health check: {health_data}")
            
            if health_data.get("status") == "ok":
                print("✅ PASSED: Server started successfully on port 18790")
                return True
            else:
                print(f"❌ FAILED: Health check failed: {health_data}")
                return False
                
        except urllib.error.URLError as e:
            print(f"❌ FAILED: Cannot connect to server: {e}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_operacional_tier():
    """Test PLC-003: llm-operacional-tier"""
    print("\n=== Test PLC-003: llm-operacional-tier ===")
    
    data = {
        "prompt": "What is 2+2?",
        "system": "You are a helpful assistant.",
        "complexity": "OPERACIONAL",
        "max_tokens": 50
    }
    
    try:
        req = urllib.request.Request(
            "http://localhost:18790/llm/call",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read())
        print(f"LLM call result: {json.dumps(result, indent=2)}")
        
        if result.get("ok"):
            response_text = result.get("response", "")
            if "4" in response_text:
                print("✅ PASSED: LLM OPERACIONAL tier responded correctly")
                return True
            else:
                print(f"❌ FAILED: Response doesn't contain expected answer: {response_text}")
                return False
        else:
            print(f"❌ FAILED: LLM call failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Exception: {e}")
        return False

def test_event_publish_poll():
    """Test PLC-006: task-publish-poll"""
    print("\n=== Test PLC-006: task-publish-poll ===")
    
    # Publish event
    publish_data = {
        "event_type": "test_task",
        "payload": {"action": "echo", "message": "test"},
        "source": "mcp"
    }
    
    try:
        # Publish event
        req = urllib.request.Request(
            "http://localhost:18790/event/publish",
            data=json.dumps(publish_data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        response = urllib.request.urlopen(req, timeout=5)
        publish_result = json.loads(response.read())
        print(f"Publish result: {publish_result}")
        
        if not publish_result.get("ok"):
            print("❌ FAILED: Event publish failed")
            return False
        
        # Poll for event
        poll_url = "http://localhost:18790/event/poll?type=test_task&t=5"
        response = urllib.request.urlopen(poll_url, timeout=10)
        poll_result = json.loads(response.read())
        print(f"Poll result: {poll_result}")
        
        if poll_result.get("ok") and poll_result.get("event_type") == "test_task":
            print("✅ PASSED: Event publish and poll successful")
            return True
        else:
            print(f"❌ FAILED: Poll failed or wrong event: {poll_result}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Exception: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting NC-DS-119 Picoclaw Integration Tests")
    print("=" * 50)
    
    results = []
    
    # Test 1: Server lifecycle
    results.append(("PLC-001: server-startup", test_server_lifecycle()))
    
    # Only continue if server started successfully
    if results[0][1]:
        # Test 2: LLM operacional tier
        results.append(("PLC-003: llm-operacional-tier", test_llm_operacional_tier()))
        
        # Test 3: Event publish/poll
        results.append(("PLC-006: task-publish-poll", test_event_publish_poll()))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print("=" * 50)
    
    passed = 0
    total = 0
    
    for test_name, success in results:
        total += 1
        if success:
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())