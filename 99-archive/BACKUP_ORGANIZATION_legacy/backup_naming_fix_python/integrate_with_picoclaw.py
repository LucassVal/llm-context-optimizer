#!/usr/bin/env python3
"""
Integration script for Picoclaw Tool Autoloader
Shows how to integrate with existing Picoclaw server
"""

import json
import logging
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from picoclaw_autoloader import ToolAutoloader, get_autoloader

def demonstrate_integration():
    """Demonstrate how to integrate with Picoclaw server"""
    print("Picoclaw Tool Autoloader - Integration Demonstration")
    print("=" * 60)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 1. Create and configure autoloader
    print("\n1. Creating and configuring autoloader...")
    
    # Configuration matching the design spec
    config = {
        'scan_directories': [
            './tools/system/',
            './tools/user/', 
            './tools/third_party/'
        ],
        'scan_interval': 300,  # 5 minutes
        'enable_hot_reload': True,
        'validation_strictness': True,
        'conflict_resolution': 'last-wins',
        'log_level': 'INFO',
        'auto_load': True
    }
    
    # Save config to file
    import yaml
    config_path = 'picoclaw-autoloader-config.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    
    # Create autoloader instance
    autoloader = ToolAutoloader(config_path)
    
    # 2. Start the autoloader
    print("\n2. Starting autoloader...")
    autoloader.start()
    
    # 3. Demonstrate tool discovery
    print("\n3. Tool discovery demonstration:")
    tools = autoloader.list_tools()
    print(f"   Discovered {len(tools)} tools: {tools}")
    
    # 4. Show tool categories
    print("\n4. Tool categories:")
    status = autoloader.get_status()
    for category in status['categories']:
        tools_in_category = autoloader.list_tools(category)
        print(f"   {category}: {len(tools_in_category)} tools")
    
    # 5. Demonstrate tool execution via autoloader
    print("\n5. Tool execution demonstration:")
    
    # Execute echo tool
    print("   Executing echo tool...")
    result = autoloader.execute_tool(
        "echo",
        text="Integration test",
        repeat=2,
        uppercase=True
    )
    print(f"   Result: {result['result']}")
    
    # Execute calculator tool
    print("   Executing calculator tool...")
    result = autoloader.execute_tool(
        "calculator",
        operation="add",
        a=42,
        b=58
    )
    print(f"   Result: {result['result']}")
    
    # 6. Show how this would integrate with Picoclaw HTTP endpoints
    print("\n6. Picoclaw HTTP endpoint integration example:")
    
    # Simulate Picoclaw endpoint handlers
    class MockPicoclawHandler:
        """Mock Picoclaw HTTP handler showing integration points"""
        
        def __init__(self, autoloader):
            self.autoloader = autoloader
        
        def handle_tools_list(self):
            """GET /tools - List all tools"""
            tools = self.autoloader.list_tools()
            return {
                'tools': tools,
                'count': len(tools),
                'categories': list(self.autoloader.registry.categories.keys())
            }
        
        def handle_tool_info(self, tool_name):
            """GET /tools/{name} - Get tool details"""
            info = self.autoloader.get_tool_info(tool_name)
            if not info:
                return {'error': 'Tool not found'}, 404
            return info
        
        def handle_tool_execute(self, tool_name, params):
            """POST /tools/{name}/execute - Execute tool"""
            try:
                result = self.autoloader.execute_tool(tool_name, **params)
                return {'success': True, 'result': result}
            except Exception as e:
                return {'success': False, 'error': str(e)}, 400
        
        def handle_scan(self):
            """POST /tools/scan - Trigger manual scan"""
            count = self.autoloader.rescan()
            return {'success': True, 'tools_registered': count}
        
        def handle_status(self):
            """GET /tools/status - Get autoloader status"""
            return self.autoloader.get_status()
    
    # Create mock handler
    mock_handler = MockPicoclawHandler(autoloader)
    
    # Demonstrate endpoint responses
    print("   Mock endpoint responses:")
    
    # List tools endpoint
    list_response = mock_handler.handle_tools_list()
    print(f"   GET /tools -> {len(list_response['tools'])} tools")
    
    # Tool info endpoint
    info_response = mock_handler.handle_tool_info('echo')
    print(f"   GET /tools/echo -> {info_response['description']}")
    
    # Tool execute endpoint
    execute_response = mock_handler.handle_tool_execute(
        'calculator',
        {'operation': 'subtract', 'a': 100, 'b': 42}
    )
    if execute_response['success']:
        print(f"   POST /tools/calculator/execute -> result: {execute_response['result']['result']}")
    
    # 7. Show hot reload capability
    print("\n7. Hot reload demonstration:")
    print("   With hot reload enabled, the autoloader will automatically:")
    print("   - Detect new tool definition files")
    print("   - Detect modifications to existing tool files")
    print("   - Detect deletion of tool files")
    print("   - Update the tool registry without restarting")
    
    # 8. Show how to extend existing Picoclaw server
    print("\n8. Extending existing Picoclaw server:")
    
    existing_picoclaw_code = '''
    # In NC-SVC-FR-019-picoclaw-server.py, add:
    
    # Import the autoloader
    from picoclaw_autoloader import get_autoloader, register_picoclaw_endpoints
    
    # Initialize autoloader on server start
    def start(port: int = PICOCLAW_PORT) -> Dict[str, Any]:
        # ... existing code ...
        
        # Initialize autoloader
        autoloader = get_autoloader("picoclaw-autoloader-config.yaml")
        autoloader.start()
        
        # Register endpoints
        register_picoclaw_endpoints(server)
        
        # ... rest of existing code ...
    
    # Add new endpoint handlers to PicoClawHandler class:
    class PicoClawHandler(BaseHTTPRequestHandler):
        # ... existing methods ...
        
        def do_GET(self):
            path = urllib.parse.urlparse(self.path).path.rstrip("/")
            
            # Add autoloader endpoints
            if path == "/tools":
                self._handle_tools_list()
                return
            elif path.startswith("/tools/"):
                tool_name = path.split("/")[-1]
                if tool_name == "scan":
                    self._handle_tools_scan()
                elif tool_name == "status":
                    self._handle_tools_status()
                else:
                    self._handle_tool_info(tool_name)
                return
            
            # ... existing endpoint handling ...
        
        def do_POST(self):
            path = urllib.parse.urlparse(self.path).path.rstrip("/")
            
            # Add autoloader execute endpoint
            if path.startswith("/tools/") and path.endswith("/execute"):
                tool_name = path.split("/")[-2]
                self._handle_tool_execute(tool_name)
                return
            
            # ... existing endpoint handling ...
    '''
    
    print("   Code modifications shown above demonstrate integration points")
    
    # 9. Clean up and stop
    print("\n9. Cleaning up...")
    autoloader.stop()
    
    # Remove config file
    import os
    if os.path.exists(config_path):
        os.remove(config_path)
    
    print("\n" + "=" * 60)
    print("Integration demonstration complete!")
    print("=" * 60)
    print("\nKey integration points demonstrated:")
    print("1. Autoloader configuration and startup")
    print("2. Tool discovery and registration")
    print("3. Tool execution through autoloader")
    print("4. HTTP endpoint integration pattern")
    print("5. Hot reload capability")
    print("6. Extension of existing Picoclaw server")

def create_integration_patch():
    """Create a patch file showing the integration changes"""
    print("\n" + "=" * 60)
    print("Creating Integration Patch")
    print("=" * 60)
    
    patch_content = '''--- a/neocortex/core/services/NC-SVC-FR-019-picoclaw-server.py
+++ b/neocortex/core/services/NC-SVC-FR-019-picoclaw-server.py
@@ -32,6 +32,10 @@
 from http.server import BaseHTTPRequestHandler, HTTPServer
 from typing import Any, Dict, Optional
 
+# Import autoloader
+from picoclaw_autoloader import get_autoloader
+
 logger = logging.getLogger(__name__)
 
 # ── Configuração ────────────────────────────────────────────────────────────
@@ -52,6 +56,9 @@
 _server_instance: Optional[HTTPServer] = None
 _server_thread:   Optional[threading.Thread] = None
 _start_time:      Optional[float] = None
+
+# Autoloader instance
+_autoloader_instance = None
 
 # Queues por event_type para long-poll
 _event_queues: Dict[str, queue.Queue] = {}
@@ -289,6 +296,12 @@
         if _server_instance is not None:
             return {"ok": False, "reason": "already_running", "port": port}
         try:
+            # Initialize autoloader
+            global _autoloader_instance
+            _autoloader_instance = get_autoloader(
+                "config/picoclaw-autoloader-config.yaml"
+            )
+            _autoloader_instance.start()
             server = HTTPServer(("0.0.0.0", port), PicoClawHandler)
             _server_instance = server
             _start_time = time.time()
@@ -319,6 +332,11 @@
         if _server_instance is None:
             return {"ok": False, "reason": "not_running"}
         try:
+            # Stop autoloader
+            global _autoloader_instance
+            if _autoloader_instance:
+                _autoloader_instance.stop()
+                _autoloader_instance = None
             _server_instance.shutdown()
             _server_instance = None
             if _server_thread:
@@ -335,6 +353,60 @@
             return {"ok": False, "error": str(e)}
 
 
+# ── Autoloader Endpoint Handlers ─────────────────────────────────────────────
+
+def _handle_tools_list(self):
+    """GET /tools - List all tools"""
+    if _autoloader_instance is None:
+        self._send_json({"error": "autoloader not initialized"}, 503)
+        return
+    tools = _autoloader_instance.list_tools()
+    self._send_json({
+        "tools": tools,
+        "count": len(tools),
+        "categories": list(_autoloader_instance.registry.categories.keys())
+    })
+
+def _handle_tool_info(self, tool_name: str):
+    """GET /tools/{name} - Get tool details"""
+    if _autoloader_instance is None:
+        self._send_json({"error": "autoloader not initialized"}, 503)
+        return
+    info = _autoloader_instance.get_tool_info(tool_name)
+    if not info:
+        self._send_json({"error": "tool not found"}, 404)
+        return
+    self._send_json(info)
+
+def _handle_tool_execute(self, tool_name: str):
+    """POST /tools/{name}/execute - Execute tool"""
+    if _autoloader_instance is None:
+        self._send_json({"error": "autoloader not initialized"}, 503)
+        return
+    body = self._read_json()
+    if body is None:
+        self._send_json({"error": "invalid JSON"}, 400)
+        return
+    try:
+        result = _autoloader_instance.execute_tool(tool_name, **body)
+        self._send_json({"success": True, "result": result})
+    except Exception as e:
+        self._send_json({"success": False, "error": str(e)}, 400)
+
+def _handle_tools_scan(self):
+    """POST /tools/scan - Trigger manual scan"""
+    if _autoloader_instance is None:
+        self._send_json({"error": "autoloader not initialized"}, 503)
+        return
+    count = _autoloader_instance.rescan()
+    self._send_json({"success": True, "tools_registered": count})
+
+def _handle_tools_status(self):
+    """GET /tools/status - Get autoloader status"""
+    if _autoloader_instance is None:
+        self._send_json({"error": "autoloader not initialized"}, 503)
+        return
+    self._send_json(_autoloader_instance.get_status())
+
 # ── API pública ───────────────────────────────────────────────────────────────
 def start(port: int = PICOCLAW_PORT) -> Dict[str, Any]:
     """Iniciar PICOCLAW em background thread."""'''
    
    print("Patch file content (showing integration changes):")
    print(patch_content)
    
    # Save patch file
    patch_path = 'picoclaw-autoloader-integration.patch'
    with open(patch_path, 'w') as f:
        f.write(patch_content)
    
    print(f"\nPatch saved to: {patch_path}")
    print("\nTo apply this integration:")
    print("1. Copy the autoloader files to your project")
    print("2. Apply the patch to NC-SVC-FR-019-picoclaw-server.py")
    print("3. Create tool directories and configuration")
    print("4. Restart the Picoclaw server")

if __name__ == "__main__":
    demonstrate_integration()
    create_integration_patch()