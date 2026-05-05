#!/usr/bin/env python3
"""
NC-SVC-FR-020-picoclaw-autoloader.py
PICOCLAW Tool Autoloader - Automatic tool discovery and registration

Implements the design from NC-DS-120-picoclaw-tool-autoloader.yaml
"""

import json
import logging
import os
import threading
import time
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

# ── Data Models ────────────────────────────────────────────────────────────────

@dataclass
class ToolParameter:
    """Parameter definition for a tool"""
    name: str
    type: str
    description: str = ""
    required: bool = True
    default: Any = None

@dataclass
class ToolDefinition:
    """Tool definition from YAML/JSON file"""
    name: str
    description: str
    parameters: List[ToolParameter]
    handler: str  # Function or endpoint
    version: str = "1.0.0"
    category: str = "general"
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 30
    permissions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    file_path: str = ""
    loaded_at: Optional[datetime] = None

@dataclass
class ToolInstance:
    """Loaded tool instance"""
    definition: ToolDefinition
    module: Any = None
    handler_func: Any = None
    is_loaded: bool = False
    last_used: Optional[datetime] = None
    usage_count: int = 0

# ── Tool Scanner ───────────────────────────────────────────────────────────────

class ToolScanner:
    """Scans directories for tool definition files"""
    
    def __init__(self, scan_directories: List[str] = None):
        self.scan_directories = scan_directories or []
        self.supported_extensions = {'.yaml', '.yml', '.json'}
    
    def scan(self) -> List[ToolDefinition]:
        """Scan all configured directories for tool definitions"""
        all_tools = []
        
        for directory in self.scan_directories:
            if not os.path.exists(directory):
                logger.warning(f"Scan directory does not exist: {directory}")
                continue
            
            tools = self._scan_directory(directory)
            all_tools.extend(tools)
        
        logger.info(f"Scanner found {len(all_tools)} tools in {len(self.scan_directories)} directories")
        return all_tools
    
    def _scan_directory(self, directory: str) -> List[ToolDefinition]:
        """Scan a single directory recursively for tool definitions"""
        tools = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in self.supported_extensions:
                    if self._is_tool_definition_file(file_path):
                        try:
                            tool_def = self._load_tool_definition(file_path)
                            if tool_def:
                                tools.append(tool_def)
                        except Exception as e:
                            logger.error(f"Failed to load tool definition from {file_path}: {e}")
        
        return tools
    
    def _is_tool_definition_file(self, file_path: str) -> bool:
        """Check if file appears to be a tool definition"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1024)  # Read first 1KB
                
            # Check for common tool definition markers
            markers = ['name:', 'description:', 'parameters:', 'handler:']
            content_lower = content.lower()
            return any(marker in content_lower for marker in markers)
        except:
            return False
    
    def _load_tool_definition(self, file_path: str) -> Optional[ToolDefinition]:
        """Load tool definition from YAML/JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)
            
            # Validate required fields
            required_fields = ['name', 'description', 'parameters', 'handler']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Parse parameters
            parameters = []
            for param_data in data.get('parameters', []):
                param = ToolParameter(
                    name=param_data.get('name', ''),
                    type=param_data.get('type', 'string'),
                    description=param_data.get('description', ''),
                    required=param_data.get('required', True),
                    default=param_data.get('default')
                )
                parameters.append(param)
            
            # Create tool definition
            tool_def = ToolDefinition(
                name=data['name'],
                description=data['description'],
                parameters=parameters,
                handler=data['handler'],
                version=data.get('version', '1.0.0'),
                category=data.get('category', 'general'),
                dependencies=data.get('dependencies', []),
                timeout=data.get('timeout', 30),
                permissions=data.get('permissions', []),
                tags=data.get('tags', []),
                file_path=file_path,
                loaded_at=datetime.now()
            )
            
            return tool_def
            
        except Exception as e:
            logger.error(f"Error loading tool definition from {file_path}: {e}")
            return None

# ── Tool Validator ─────────────────────────────────────────────────────────────

class ToolValidator:
    """Validates tool definitions and dependencies"""
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.validated_tools: Set[str] = set()
    
    def validate(self, tool_def: ToolDefinition) -> Tuple[bool, List[str]]:
        """Validate a tool definition"""
        errors = []
        
        # Check name
        if not tool_def.name or not isinstance(tool_def.name, str):
            errors.append("Tool name must be a non-empty string")
        
        # Check for name conflicts
        if tool_def.name in self.validated_tools:
            errors.append(f"Tool name conflict: '{tool_def.name}' already exists")
        
        # Check description
        if not tool_def.description or not isinstance(tool_def.description, str):
            errors.append("Tool description must be a non-empty string")
        
        # Check parameters
        if not isinstance(tool_def.parameters, list):
            errors.append("Parameters must be a list")
        else:
            for i, param in enumerate(tool_def.parameters):
                param_errors = self._validate_parameter(param, i)
                errors.extend(param_errors)
        
        # Check handler
        if not tool_def.handler or not isinstance(tool_def.handler, str):
            errors.append("Handler must be a non-empty string")
        
        # Check dependencies (if strict mode)
        if self.strict_mode and tool_def.dependencies:
            for dep in tool_def.dependencies:
                if not isinstance(dep, str):
                    errors.append(f"Dependency must be string: {dep}")
        
        is_valid = len(errors) == 0
        if is_valid:
            self.validated_tools.add(tool_def.name)
        
        return is_valid, errors
    
    def _validate_parameter(self, param: ToolParameter, index: int) -> List[str]:
        """Validate a single parameter"""
        errors = []
        
        if not param.name or not isinstance(param.name, str):
            errors.append(f"Parameter {index}: name must be non-empty string")
        
        if not param.type or not isinstance(param.type, str):
            errors.append(f"Parameter {index}: type must be non-empty string")
        
        if not isinstance(param.required, bool):
            errors.append(f"Parameter {index}: required must be boolean")
        
        return errors
    
    def clear(self):
        """Clear validation cache"""
        self.validated_tools.clear()

# ── Tool Registry ──────────────────────────────────────────────────────────────

class ToolRegistry:
    """Central registry of available tools"""
    
    def __init__(self):
        self.tools: Dict[str, ToolInstance] = {}
        self.categories: Dict[str, List[str]] = {}
        self.lock = threading.RLock()
    
    def register(self, tool_def: ToolDefinition) -> bool:
        """Register a tool definition"""
        with self.lock:
            if tool_def.name in self.tools:
                logger.warning(f"Tool '{tool_def.name}' already registered")
                return False
            
            # Create tool instance
            tool_instance = ToolInstance(definition=tool_def)
            
            # Store in registry
            self.tools[tool_def.name] = tool_instance
            
            # Update category index
            category = tool_def.category
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(tool_def.name)
            
            logger.info(f"Registered tool: {tool_def.name} (category: {category})")
            return True
    
    def unregister(self, tool_name: str) -> bool:
        """Unregister a tool"""
        with self.lock:
            if tool_name not in self.tools:
                return False
            
            # Remove from category index
            tool_def = self.tools[tool_name].definition
            category = tool_def.category
            if category in self.categories and tool_name in self.categories[category]:
                self.categories[category].remove(tool_name)
                if not self.categories[category]:
                    del self.categories[category]
            
            # Remove from registry
            del self.tools[tool_name]
            
            logger.info(f"Unregistered tool: {tool_name}")
            return True
    
    def get(self, tool_name: str) -> Optional[ToolInstance]:
        """Get a tool instance by name"""
        with self.lock:
            return self.tools.get(tool_name)
    
    def list_tools(self, category: str = None) -> List[str]:
        """List all tool names, optionally filtered by category"""
        with self.lock:
            if category:
                return self.categories.get(category, [])
            return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get tool information dictionary"""
        with self.lock:
            if tool_name not in self.tools:
                return None
            
            instance = self.tools[tool_name]
            defn = instance.definition
            
            return {
                'name': defn.name,
                'description': defn.description,
                'version': defn.version,
                'category': defn.category,
                'parameters': [
                    {
                        'name': p.name,
                        'type': p.type,
                        'description': p.description,
                        'required': p.required,
                        'default': p.default
                    }
                    for p in defn.parameters
                ],
                'dependencies': defn.dependencies,
                'timeout': defn.timeout,
                'permissions': defn.permissions,
                'tags': defn.tags,
                'file_path': defn.file_path,
                'loaded_at': defn.loaded_at.isoformat() if defn.loaded_at else None,
                'is_loaded': instance.is_loaded,
                'usage_count': instance.usage_count,
                'last_used': instance.last_used.isoformat() if instance.last_used else None
            }
    
    def clear(self):
        """Clear all registered tools"""
        with self.lock:
            self.tools.clear()
            self.categories.clear()
            logger.info("Cleared tool registry")

# ── Tool Loader ────────────────────────────────────────────────────────────────

class ToolLoader:
    """Loads and initializes tool implementations"""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.loaded_modules: Dict[str, Any] = {}
    
    def load_tool(self, tool_name: str) -> bool:
        """Load and initialize a tool implementation"""
        with self.registry.lock:
            if tool_name not in self.registry.tools:
                logger.error(f"Cannot load unknown tool: {tool_name}")
                return False
            
            instance = self.registry.tools[tool_name]
            if instance.is_loaded:
                logger.debug(f"Tool already loaded: {tool_name}")
                return True
            
            try:
                # Parse handler specification
                # Format: "module:function" or "module.Class.method"
                handler_spec = instance.definition.handler
                
                if ':' in handler_spec:
                    # module:function format
                    module_path, func_name = handler_spec.split(':', 1)
                    module = self._import_module(module_path)
                    handler_func = getattr(module, func_name, None)
                else:
                    # Assume it's a direct function reference (for backward compatibility)
                    # This would need more sophisticated parsing for class methods
                    logger.warning(f"Simple handler format may not work: {handler_spec}")
                    handler_func = None
                
                if handler_func is None:
                    logger.error(f"Handler function not found: {handler_spec}")
                    return False
                
                # Update tool instance
                instance.handler_func = handler_func
                instance.is_loaded = True
                instance.module = module
                
                logger.info(f"Loaded tool implementation: {tool_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load tool {tool_name}: {e}")
                return False
    
    def _import_module(self, module_path: str) -> Any:
        """Import a module by path"""
        # Check if already loaded
        if module_path in self.loaded_modules:
            return self.loaded_modules[module_path]
        
        # Import module
        import importlib
        module = importlib.import_module(module_path)
        self.loaded_modules[module_path] = module
        return module
    
    def unload_tool(self, tool_name: str) -> bool:
        """Unload a tool implementation"""
        with self.registry.lock:
            if tool_name not in self.registry.tools:
                return False
            
            instance = self.registry.tools[tool_name]
            if not instance.is_loaded:
                return True
            
            # Clear references
            instance.handler_func = None
            instance.module = None
            instance.is_loaded = False
            
            logger.info(f"Unloaded tool implementation: {tool_name}")
            return True

# ── Hot Reload Monitor ─────────────────────────────────────────────────────────

class ToolFileHandler(FileSystemEventHandler):
    """Watchdog event handler for tool file changes"""
    
    def __init__(self, autoloader: 'ToolAutoloader'):
        self.autoloader = autoloader
        self.change_queue = Queue()
    
    def on_created(self, event):
        if not event.is_directory:
            self.change_queue.put(('created', event.src_path))
    
    def on_modified(self, event):
        if not event.is_directory:
            self.change_queue.put(('modified', event.src_path))
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.change_queue.put(('deleted', event.src_path))

class HotReloadMonitor:
    """Monitors tool directories for changes"""
    
    def __init__(self, autoloader: 'ToolAutoloader'):
        self.autoloader = autoloader
        self.observer = Observer()
        self.event_handler = ToolFileHandler(autoloader)
        self.watched_dirs: Set[str] = set()
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
    
    def start(self, directories: List[str]):
        """Start monitoring directories"""
        if self.running:
            logger.warning("Hot reload monitor already running")
            return
        
        self.running = True
        
        # Schedule directories for observation
        for directory in directories:
            if os.path.exists(directory):
                self.observer.schedule(self.event_handler, directory, recursive=True)
                self.watched_dirs.add(directory)
                logger.info(f"Monitoring directory for changes: {directory}")
        
        # Start observer in background thread
        self.observer.start()
        
        # Start change processor thread
        self.monitor_thread = threading.Thread(target=self._process_changes, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Hot reload monitor started")
    
    def stop(self):
        """Stop monitoring"""
        if not self.running:
            return
        
        self.running = False
        self.observer.stop()
        self.observer.join()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("Hot reload monitor stopped")
    
    def _process_changes(self):
        """Process file change events from queue"""
        while self.running:
            try:
                # Wait for event with timeout
                event_type, file_path = self.event_handler.change_queue.get(timeout=1)
                
                # Process based on event type
                if event_type in ('created', 'modified'):
                    logger.info(f"File {event_type}: {file_path}")
                    # Trigger rescan of affected directory
                    self.autoloader.rescan()
                elif event_type == 'deleted':
                    logger.info(f"File deleted: {file_path}")
                    # Check if this was a tool definition file
                    # and unregister corresponding tool
                    self.autoloader._handle_file_deletion(file_path)
                    
            except Exception as e:
                # Timeout is expected, other errors should be logged
                if not isinstance(e, Exception) or "empty" not in str(e):
                    logger.debug(f"Change processor error: {e}")

# ── Main Autoloader Class ──────────────────────────────────────────────────────

class ToolAutoloader:
    """Main autoloader class coordinating all components"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.scanner = ToolScanner(self.config.get('scan_directories', []))
        self.validator = ToolValidator(self.config.get('validation_strictness', True))
        self.registry = ToolRegistry()
        self.loader = ToolLoader(self.registry)
        self.monitor = HotReloadMonitor(self)
        
        self.scan_interval = self.config.get('scan_interval', 300)  # 5 minutes
        self.enable_hot_reload = self.config.get('enable_hot_reload', False)
        self.conflict_resolution = self.config.get('conflict_resolution', 'last-wins')
        
        self.scan_thread: Optional[threading.Thread] = None
        self.running = False
    
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from file"""
        default_config = {
            'scan_directories': [
                './tools/system/',
                './tools/user/',
                './tools/third_party/'
            ],
            'scan_interval': 300,
            'enable_hot_reload': False,
            'validation_strictness': True,
            'conflict_resolution': 'last-wins',
            'log_level': 'INFO'
        }
        
        if not config_path:
            return default_config
        
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    if config_path.endswith('.json'):
                        user_config = json.load(f)
                    else:
                        user_config = yaml.safe_load(f)
                
                # Merge with defaults
                default_config.update(user_config)
                logger.info(f"Loaded configuration from {config_path}")
        
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
        
        return default_config
    
    def start(self):
        """Start the autoloader"""
        if self.running:
            logger.warning("Autoloader already running")
            return
        
        self.running = True
        
        # Initial scan
        self.scan_and_register()
        
        # Start periodic scanning
        if self.scan_interval > 0:
            self.scan_thread = threading.Thread(target=self._periodic_scan, daemon=True)
            self.scan_thread.start()
        
        # Start hot reload monitor if enabled
        if self.enable_hot_reload:
            self.monitor.start(self.config.get('scan_directories', []))
        
        logger.info(f"Tool autoloader started (scan interval: {self.scan_interval}s)")
    
    def stop(self):
        """Stop the autoloader"""
        if not self.running:
            return
        
        self.running = False
        self.monitor.stop()
        
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
        
        logger.info("Tool autoloader stopped")
    
    def scan_and_register(self):
        """Scan for tools and register valid ones"""
        logger.info("Starting tool scan...")
        
        # Scan for tool definitions
        tool_defs = self.scanner.scan()
        
        registered_count = 0
        skipped_count = 0
        
        for tool_def in tool_defs:
            # Validate tool
            is_valid, errors = self.validator.validate(tool_def)
            
            if not is_valid:
                logger.warning(f"Tool validation failed for '{tool_def.name}': {errors}")
                skipped_count += 1
                continue
            
            # Check for conflicts
            existing_tool = self.registry.get(tool_def.name)
            if existing_tool:
                if self.conflict_resolution == 'skip':
                    logger.info(f"Skipping duplicate tool: {tool_def.name}")
                    skipped_count += 1
                    continue
                elif self.conflict_resolution == 'error':
                    logger.error(f"Tool conflict: {tool_def.name} already registered")
                    skipped_count += 1
                    continue
                elif self.conflict_resolution == 'last-wins':
                    logger.info(f"Replacing existing tool: {tool_def.name}")
                    self.registry.unregister(tool_def.name)
            
            # Register tool
            if self.registry.register(tool_def):
                registered_count += 1
                
                # Auto-load tool implementation
                if self.config.get('auto_load', True):
                    self.loader.load_tool(tool_def.name)
        
        logger.info(f"Scan complete: {registered_count} registered, {skipped_count} skipped")
        return registered_count
    
    def rescan(self):
        """Trigger a rescan of tool directories"""
        logger.info("Manual rescan triggered")
        return self.scan_and_register()
    
    def _periodic_scan(self):
        """Periodic scanning thread"""
        while self.running:
            time.sleep(self.scan_interval)
            if self.running:
                self.scan_and_register()
    
    def _handle_file_deletion(self, file_path: str):
        """Handle deletion of a tool definition file"""
        # Find tool by file path
        tool_to_remove = None
        for tool_name, instance in self.registry.tools.items():
            if instance.definition.file_path == file_path:
                tool_to_remove = tool_name
                break
        
        if tool_to_remove:
            logger.info(f"Tool definition file deleted, unregistering: {tool_to_remove}")
            self.registry.unregister(tool_to_remove)
    
    # ── Public API ─────────────────────────────────────────────────────────────
    
    def get_tool(self, tool_name: str) -> Optional[ToolInstance]:
        """Get a tool instance"""
        return self.registry.get(tool_name)
    
    def list_tools(self, category: str = None) -> List[str]:
        """List available tools"""
        return self.registry.list_tools(category)
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get detailed tool information"""
        return self.registry.get_tool_info(tool_name)
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool with given parameters"""
        instance = self.get_tool(tool_name)
        if not instance:
            raise ValueError(f"Tool not found: {tool_name}")
        
        if not instance.is_loaded:
            # Try to load the tool
            if not self.loader.load_tool(tool_name):
                raise RuntimeError(f"Failed to load tool: {tool_name}")
        
        # Validate parameters
        self._validate_parameters(instance.definition, kwargs)
        
        # Execute tool
        try:
            result = instance.handler_func(**kwargs)
            instance.usage_count += 1
            instance.last_used = datetime.now()
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name} - {e}")
            raise
    
    def _validate_parameters(self, tool_def: ToolDefinition, params: Dict):
        """Validate tool parameters"""
        param_names = {p.name for p in tool_def.parameters}
        
        # Check for required parameters
        for param in tool_def.parameters:
            if param.required and param.name not in params:
                raise ValueError(f"Missing required parameter: {param.name}")
        
        # Check for unknown parameters
        for param_name in params:
            if param_name not in param_names:
                logger.warning(f"Unknown parameter '{param_name}' for tool '{tool_def.name}'")
    
    def get_status(self) -> Dict:
        """Get autoloader status"""
        return {
            'running': self.running,
            'tools_registered': len(self.registry.tools),
            'tools_loaded': sum(1 for t in self.registry.tools.values() if t.is_loaded),
            'categories': list(self.registry.categories.keys()),
            'scan_directories': self.config.get('scan_directories', []),
            'scan_interval': self.scan_interval,
            'hot_reload_enabled': self.enable_hot_reload,
            'conflict_resolution': self.conflict_resolution
        }

# ── Singleton Instance ─────────────────────────────────────────────────────────

_autoloader_instance: Optional[ToolAutoloader] = None

def get_autoloader(config_path: str = None) -> ToolAutoloader:
    """Get or create the singleton autoloader instance"""
    global _autoloader_instance
    if _autoloader_instance is None:
        _autoloader_instance = ToolAutoloader(config_path)
    return _autoloader_instance

# ── Picoclaw Integration ───────────────────────────────────────────────────────

def register_picoclaw_endpoints(picoclaw_server):
    """Register autoloader endpoints with Picoclaw server"""
    
    autoloader = get_autoloader()
    
    # Add endpoint handlers to the Picoclaw server
    # This would need to be integrated with the existing Picoclaw server code
    
    logger.info("Registered autoloader endpoints with Picoclaw")

# ── Main Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Picoclaw Tool Autoloader")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--scan", action="store_true", help="Run scan and exit")
    parser.add_argument("--list", action="store_true", help="List registered tools")
    parser.add_argument("--info", help="Get info about specific tool")
    parser.add_argument("--status", action="store_true", help="Show autoloader status")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create autoloader
    autoloader = ToolAutoloader(args.config)
    
    if args.scan:
        # Run scan and exit
        count = autoloader.scan_and_register()
        print(f"Registered {count} tools")
    
    elif args.list:
        # List tools
        autoloader.scan_and_register()
        tools = autoloader.list_tools()
        print(f"Registered tools ({len(tools)}):")
        for tool in tools:
            print(f"  - {tool}")
    
    elif args.info:
        # Get tool info
        autoloader.scan_and_register()
        info = autoloader.get_tool_info(args.info)
        if info:
            print(json.dumps(info, indent=2, default=str))
        else:
            print(f"Tool not found: {args.info}")
    
    elif args.status:
        # Show status
        autoloader.start()
        time.sleep(1)  # Give it time to initialize
        status = autoloader.get_status()
        print(json.dumps(status, indent=2))
        autoloader.stop()
    
    else:
        # Run as service
        print("Starting Picoclaw Tool Autoloader...")
        autoloader.start()
        
        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            autoloader.stop()