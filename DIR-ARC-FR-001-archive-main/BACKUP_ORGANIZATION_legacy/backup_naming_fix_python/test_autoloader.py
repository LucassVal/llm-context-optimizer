#!/usr/bin/env python3
"""
Test script for Picoclaw Tool Autoloader
"""

import json
import logging
import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from picoclaw_autoloader import ToolAutoloader

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_basic_functionality():
    """Test basic autoloader functionality"""
    print("=" * 60)
    print("Testing Basic Functionality")
    print("=" * 60)
    
    # Create autoloader with default config
    autoloader = ToolAutoloader()
    
    # Update scan directories to include our test tools
    autoloader.config['scan_directories'] = ['./tools/system/', './tools/user/', './tools/third_party/']
    autoloader.scanner.scan_directories = autoloader.config['scan_directories']
    
    # Test 1: Scan and register tools
    print("\n1. Scanning for tools...")
    registered_count = autoloader.scan_and_register()
    print(f"   Registered {registered_count} tools")
    
    # Test 2: List tools
    print("\n2. Listing registered tools...")
    tools = autoloader.list_tools()
    print(f"   Found {len(tools)} tools: {tools}")
    
    # Test 3: Get tool info
    print("\n3. Getting tool information...")
    for tool_name in tools:
        info = autoloader.get_tool_info(tool_name)
        if info:
            print(f"   {tool_name}: {info['description']} (v{info['version']})")
    
    # Test 4: Get status
    print("\n4. Getting autoloader status...")
    status = autoloader.get_status()
    print(f"   Running: {status['running']}")
    print(f"   Tools registered: {status['tools_registered']}")
    print(f"   Tools loaded: {status['tools_loaded']}")
    print(f"   Categories: {status['categories']}")
    
    return autoloader

def test_tool_execution(autoloader):
    """Test tool execution"""
    print("\n" + "=" * 60)
    print("Testing Tool Execution")
    print("=" * 60)
    
    # Test 1: Execute echo tool
    print("\n1. Testing echo tool...")
    try:
        result = autoloader.execute_tool(
            "echo",
            text="Hello from Picoclaw Autoloader!",
            repeat=3,
            uppercase=True
        )
        print(f"   Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Execute calculator tool
    print("\n2. Testing calculator tool...")
    try:
        result = autoloader.execute_tool(
            "calculator",
            operation="multiply",
            a=7,
            b=8,
            precision=0
        )
        print(f"   Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Execute file info tool
    print("\n3. Testing file info tool...")
    try:
        result = autoloader.execute_tool(
            "file_info",
            file_path=__file__,
            include_content=True,
            max_content_size=500
        )
        # Don't print full content to keep output clean
        if 'content_preview' in result:
            result['content_preview'] = result['content_preview'][:100] + "..."
        print(f"   Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")

def test_autoloader_service():
    """Test autoloader as a service"""
    print("\n" + "=" * 60)
    print("Testing Autoloader Service")
    print("=" * 60)
    
    # Create autoloader with service configuration
    config = {
        'scan_directories': ['./tools/system/', './tools/user/', './tools/third_party/'],
        'scan_interval': 10,  # Short interval for testing
        'enable_hot_reload': False,  # Disable for simple test
        'auto_load': True
    }
    
    # Create temporary config file
    import yaml
    config_path = 'test_config.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    
    autoloader = ToolAutoloader(config_path)
    
    # Start the autoloader
    print("\n1. Starting autoloader service...")
    autoloader.start()
    
    # Wait for initial scan
    time.sleep(2)
    
    # Check status
    status = autoloader.get_status()
    print(f"   Service running: {status['running']}")
    print(f"   Tools found: {status['tools_registered']}")
    
    # List tools
    tools = autoloader.list_tools()
    print(f"   Available tools: {tools}")
    
    # Stop the autoloader
    print("\n2. Stopping autoloader service...")
    autoloader.stop()
    
    # Clean up
    import os
    if os.path.exists(config_path):
        os.remove(config_path)
    
    print("   Service stopped")

def test_error_handling():
    """Test error handling scenarios"""
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    
    autoloader = ToolAutoloader()
    autoloader.config['scan_directories'] = ['./tools/system/']
    autoloader.scanner.scan_directories = autoloader.config['scan_directories']
    
    # Test 1: Non-existent tool
    print("\n1. Testing non-existent tool...")
    try:
        autoloader.execute_tool("non_existent_tool")
    except ValueError as e:
        print(f"   Expected error: {e}")
    
    # Test 2: Invalid parameters
    print("\n2. Testing invalid parameters...")
    autoloader.scan_and_register()
    try:
        autoloader.execute_tool("echo")  # Missing required parameter
    except ValueError as e:
        print(f"   Expected error: {e}")
    
    # Test 3: Tool with missing handler
    print("\n3. Testing tool with missing handler...")
    # Create a tool definition with non-existent handler
    import yaml
    bad_tool = {
        'name': 'bad_tool',
        'description': 'Tool with missing handler',
        'parameters': [],
        'handler': 'non_existent_module:missing_function'
    }
    
    bad_tool_path = 'tools/system/bad_tool.yaml'
    with open(bad_tool_path, 'w') as f:
        yaml.dump(bad_tool, f)
    
    # Scan should register but not load the tool
    autoloader.scan_and_register()
    
    # Try to execute should fail
    try:
        autoloader.execute_tool("bad_tool")
    except RuntimeError as e:
        print(f"   Expected error: {e}")
    
    # Clean up
    import os
    if os.path.exists(bad_tool_path):
        os.remove(bad_tool_path)

def test_performance():
    """Test performance with multiple tools"""
    print("\n" + "=" * 60)
    print("Testing Performance")
    print("=" * 60)
    
    import time
    
    autoloader = ToolAutoloader()
    autoloader.config['scan_directories'] = ['./tools/system/', './tools/user/', './tools/third_party/']
    autoloader.scanner.scan_directories = autoloader.config['scan_directories']
    
    # Time the scan
    print("\n1. Timing tool scan...")
    start_time = time.time()
    autoloader.scan_and_register()
    scan_time = time.time() - start_time
    print(f"   Scan completed in {scan_time:.3f} seconds")
    
    # Time tool execution
    print("\n2. Timing tool execution...")
    executions = 10
    start_time = time.time()
    
    for i in range(executions):
        autoloader.execute_tool(
            "echo",
            text=f"Test {i}",
            repeat=1,
            uppercase=False
        )
    
    exec_time = time.time() - start_time
    avg_time = exec_time / executions
    print(f"   {executions} executions in {exec_time:.3f} seconds")
    print(f"   Average: {avg_time:.3f} seconds per execution")

def main():
    """Run all tests"""
    setup_logging()
    
    print("Picoclaw Tool Autoloader - Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        autoloader = test_basic_functionality()
        test_tool_execution(autoloader)
        test_autoloader_service()
        test_error_handling()
        test_performance()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())