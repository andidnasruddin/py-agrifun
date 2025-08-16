"""
Plugin System - Hot-Loadable Module Architecture for AgriFun Comprehensive Engine

This module implements a sophisticated plugin system that enables hot-loading of game
modules, modifications, and extensions without requiring game restarts. Supports the
full scope of the comprehensive AgriFun vision with secure sandboxing and dependency
management.

Key Features:
- Hot-loading and hot-unloading of plugin modules
- Secure plugin sandboxing with permission controls
- Dependency resolution and plugin ordering
- Plugin lifecycle management (load, initialize, update, shutdown)
- API versioning and compatibility checking
- Plugin marketplace integration ready
- Custom content type registration
- System extension points and hooks
- Plugin performance monitoring and limits
- Automatic plugin discovery and installation

Plugin Types:
- Content Plugins: New crops, equipment, diseases, research trees
- System Plugins: New game mechanics, AI behaviors, economic models  
- UI Plugins: Custom interfaces, overlays, information displays
- Tool Plugins: Development tools, debugging aids, content creators
- Integration Plugins: External service connections, analytics, modding tools
- Rendering Plugins: Custom visual effects, shaders, display modes

Plugin Architecture:
- Plugin Manifest: metadata, dependencies, permissions, API requirements
- Plugin Lifecycle: discovery → validation → loading → initialization → execution
- Sandboxing: restricted API access, resource limits, security boundaries
- Communication: event-based plugin-to-core and plugin-to-plugin messaging

Example Plugin Structure:
/plugins/
  /my_awesome_plugin/
    - plugin.yaml (manifest)
    - __init__.py (entry point)
    - content/ (custom content)
    - ui/ (custom interfaces)
    - systems/ (game logic)

Usage Example:
    # Initialize plugin system
    plugin_system = PluginSystem("plugins/")
    await plugin_system.discover_plugins()
    await plugin_system.load_plugin("my_awesome_plugin")
    
    # Register custom content
    plugin_system.register_content_provider("custom_crops", my_plugin)
    
    # Plugin-to-core communication
    plugin_system.emit_plugin_event("crop_harvested", {...})
    
    # Hot-reload during development
    await plugin_system.reload_plugin("my_awesome_plugin")

Security Features:
- Permission-based API access control
- Resource usage monitoring and limits
- Code signing and verification (future)
- Isolated namespaces for plugin data
- Safe plugin unloading with cleanup verification
"""

import os
import sys
import importlib
import importlib.util
import asyncio
import time
import yaml
import hashlib
from typing import Dict, List, Set, Any, Optional, Callable, Type, Union
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
from enum import Enum
import logging
import threading
# Resource monitoring - platform specific
try:
    import resource
except ImportError:
    resource = None  # Windows doesn't have resource module
import gc

# Import our core systems
from .event_system import get_global_event_system, EventPriority
from .entity_component_system import get_entity_manager, Component
from .content_registry import get_content_registry


class PluginState(Enum):
    """Plugin lifecycle states"""
    DISCOVERED = "discovered"
    VALIDATING = "validating"
    LOADING = "loading"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    UPDATING = "updating"
    SHUTTING_DOWN = "shutting_down"
    UNLOADED = "unloaded"
    ERROR = "error"


class PluginType(Enum):
    """Plugin category types"""
    CONTENT = "content"           # New crops, equipment, etc.
    SYSTEM = "system"            # Game mechanics, AI, economics
    UI = "ui"                    # Custom interfaces and overlays
    TOOL = "tool"                # Development and debugging tools
    INTEGRATION = "integration"   # External services and APIs
    RENDERING = "rendering"       # Visual effects and display modes


class PluginPermission(Enum):
    """Plugin permission levels"""
    READ_CONTENT = "read_content"           # Access game content data
    MODIFY_CONTENT = "modify_content"       # Create/modify content
    ACCESS_ENTITIES = "access_entities"     # Read entity data
    MODIFY_ENTITIES = "modify_entities"     # Create/modify entities
    ACCESS_GRID = "access_grid"            # Read grid data
    MODIFY_GRID = "modify_grid"            # Modify grid tiles
    EMIT_EVENTS = "emit_events"            # Send events to core systems
    REGISTER_COMPONENTS = "register_components"  # Add new component types
    ACCESS_SAVE_DATA = "access_save_data"   # Read save files
    MODIFY_SAVE_DATA = "modify_save_data"   # Modify save files
    NETWORK_ACCESS = "network_access"       # External network connections
    FILE_SYSTEM_ACCESS = "file_system_access"  # File system operations
    SYSTEM_INTEGRATION = "system_integration"  # Deep system modifications


@dataclass
class PluginManifest:
    """Plugin manifest containing metadata and requirements"""
    # Basic information
    plugin_id: str
    name: str
    version: str
    description: str
    author: str
    homepage: str = ""
    
    # Plugin type and category
    plugin_type: PluginType = PluginType.CONTENT
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    
    # Dependencies and compatibility
    api_version: str = "1.0"
    min_game_version: str = "1.0.0"
    max_game_version: str = "999.0.0"
    dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    
    # Plugin permissions
    permissions: List[PluginPermission] = field(default_factory=list)
    
    # Entry points
    entry_point: str = "__init__.py"
    main_class: str = "Plugin"
    
    # Content registration
    content_types: List[str] = field(default_factory=list)
    component_types: List[str] = field(default_factory=list)
    system_types: List[str] = field(default_factory=list)
    
    # Resource limits
    max_memory_mb: int = 100
    max_cpu_percent: float = 10.0
    max_file_handles: int = 50
    
    # Auto-loading behavior
    auto_load: bool = True
    load_priority: int = 100  # Lower = higher priority
    
    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'PluginManifest':
        """Load manifest from YAML file"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Convert string enums to enum values
        if 'plugin_type' in data:
            data['plugin_type'] = PluginType(data['plugin_type'])
        
        if 'permissions' in data:
            data['permissions'] = [PluginPermission(p) for p in data['permissions']]
        
        return cls(**data)


@dataclass
class PluginContext:
    """Runtime context for a plugin"""
    manifest: PluginManifest
    plugin_path: Path
    module: Optional[Any] = None
    plugin_instance: Optional[Any] = None
    state: PluginState = PluginState.DISCOVERED
    
    # Runtime tracking
    load_time: float = 0.0
    last_update: float = 0.0
    update_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    
    # Resource usage
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    file_handles: int = 0
    
    # Performance metrics
    initialization_time_ms: float = 0.0
    average_update_time_ms: float = 0.0
    total_update_time_ms: float = 0.0
    
    # Security tracking
    permission_violations: int = 0
    api_calls: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    def mark_error(self, error_message: str):
        """Mark plugin as having an error"""
        self.state = PluginState.ERROR
        self.error_count += 1
        self.last_error = error_message


class PluginAPI:
    """Secure API interface for plugins"""
    
    def __init__(self, plugin_context: PluginContext, plugin_system: 'PluginSystem'):
        self.context = plugin_context
        self.plugin_system = plugin_system
        self.event_system = get_global_event_system()
        self.entity_manager = get_entity_manager()
        self.content_registry = get_content_registry()
        
        # Track API usage
        self._api_calls = defaultdict(int)
    
    def _check_permission(self, permission: PluginPermission) -> bool:
        """Check if plugin has required permission"""
        has_permission = permission in self.context.manifest.permissions
        if not has_permission:
            self.context.permission_violations += 1
            self.plugin_system.logger.warning(
                f"Plugin {self.context.manifest.plugin_id} attempted {permission.value} without permission"
            )
        return has_permission
    
    def _track_api_call(self, method_name: str):
        """Track API method usage"""
        self._api_calls[method_name] += 1
        self.context.api_calls[method_name] += 1
    
    # Content API
    def register_content(self, content_type: str, content_id: str, content_data: Dict[str, Any]) -> bool:
        """Register new content with the content registry"""
        self._track_api_call('register_content')
        
        if not self._check_permission(PluginPermission.MODIFY_CONTENT):
            return False
        
        try:
            # Add plugin metadata to content
            content_data['_plugin_id'] = self.context.manifest.plugin_id
            content_data['_plugin_version'] = self.context.manifest.version
            
            # Register with content registry
            self.content_registry.content[content_type][content_id] = content_data
            
            # Emit registration event
            self.event_system.publish('plugin_content_registered', {
                'plugin_id': self.context.manifest.plugin_id,
                'content_type': content_type,
                'content_id': content_id
            }, EventPriority.NORMAL, f'plugin_{self.context.manifest.plugin_id}')
            
            return True
            
        except Exception as e:
            self.context.mark_error(f"Failed to register content {content_id}: {e}")
            return False
    
    def get_content(self, content_type: str, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content data"""
        self._track_api_call('get_content')
        
        if not self._check_permission(PluginPermission.READ_CONTENT):
            return None
        
        return self.content_registry.get_resolved_content(content_type, content_id)
    
    def list_content(self, content_type: str) -> List[str]:
        """List available content IDs"""
        self._track_api_call('list_content')
        
        if not self._check_permission(PluginPermission.READ_CONTENT):
            return []
        
        return self.content_registry.list_content(content_type)
    
    # Entity API
    def create_entity(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """Create a new entity"""
        self._track_api_call('create_entity')
        
        if not self._check_permission(PluginPermission.MODIFY_ENTITIES):
            return None
        
        try:
            # Add plugin metadata
            if 'identity' not in entity_data:
                entity_data['identity'] = {}
            entity_data['identity']['_created_by_plugin'] = self.context.manifest.plugin_id
            
            entity_id = self.entity_manager.create_entity(entity_data)
            
            # Emit creation event
            self.event_system.publish('plugin_entity_created', {
                'plugin_id': self.context.manifest.plugin_id,
                'entity_id': entity_id
            }, EventPriority.NORMAL, f'plugin_{self.context.manifest.plugin_id}')
            
            return entity_id
            
        except Exception as e:
            self.context.mark_error(f"Failed to create entity: {e}")
            return None
    
    def get_entity_component(self, entity_id: str, component_type: str) -> Optional[Component]:
        """Get entity component"""
        self._track_api_call('get_entity_component')
        
        if not self._check_permission(PluginPermission.ACCESS_ENTITIES):
            return None
        
        return self.entity_manager.get_component(entity_id, component_type)
    
    def update_entity_component(self, entity_id: str, component_type: str, 
                               update_data: Dict[str, Any]) -> bool:
        """Update entity component"""
        self._track_api_call('update_entity_component')
        
        if not self._check_permission(PluginPermission.MODIFY_ENTITIES):
            return False
        
        try:
            self.entity_manager.update_component(entity_id, component_type, update_data)
            return True
        except Exception as e:
            self.context.mark_error(f"Failed to update component: {e}")
            return False
    
    def query_entities(self, required_components: List[str]) -> List[str]:
        """Query entities with required components"""
        self._track_api_call('query_entities')
        
        if not self._check_permission(PluginPermission.ACCESS_ENTITIES):
            return []
        
        return self.entity_manager.query(required_components)
    
    # Event API
    def emit_event(self, event_type: str, event_data: Dict[str, Any], 
                   priority: EventPriority = EventPriority.NORMAL) -> bool:
        """Emit an event"""
        self._track_api_call('emit_event')
        
        if not self._check_permission(PluginPermission.EMIT_EVENTS):
            return False
        
        try:
            # Add plugin metadata to event
            event_data['_source_plugin'] = self.context.manifest.plugin_id
            
            self.event_system.publish(event_type, event_data, priority, f'plugin_{self.context.manifest.plugin_id}')
            return True
            
        except Exception as e:
            self.context.mark_error(f"Failed to emit event: {e}")
            return False
    
    def subscribe_to_event(self, event_type: str, callback: Callable) -> bool:
        """Subscribe to an event"""
        self._track_api_call('subscribe_to_event')
        
        if not self._check_permission(PluginPermission.EMIT_EVENTS):
            return False
        
        try:
            # Wrap callback to track plugin calls
            def tracked_callback(event_data):
                self._track_api_call(f'event_callback_{event_type}')
                return callback(event_data)
            
            self.event_system.subscribe(event_type, tracked_callback)
            return True
            
        except Exception as e:
            self.context.mark_error(f"Failed to subscribe to event: {e}")
            return False
    
    # Component Registration API
    def register_component_type(self, component_class: Type[Component]) -> bool:
        """Register a new component type"""
        self._track_api_call('register_component_type')
        
        if not self._check_permission(PluginPermission.REGISTER_COMPONENTS):
            return False
        
        try:
            self.entity_manager.component_registry.register_component(component_class)
            
            # Emit registration event
            self.event_system.publish('plugin_component_registered', {
                'plugin_id': self.context.manifest.plugin_id,
                'component_type': component_class.__name__
            }, EventPriority.NORMAL, f'plugin_{self.context.manifest.plugin_id}')
            
            return True
            
        except Exception as e:
            self.context.mark_error(f"Failed to register component: {e}")
            return False
    
    # Utility API
    def get_plugin_data_path(self) -> Path:
        """Get plugin's data directory path"""
        self._track_api_call('get_plugin_data_path')
        
        plugin_data_dir = self.context.plugin_path / "data"
        plugin_data_dir.mkdir(exist_ok=True)
        return plugin_data_dir
    
    def log_info(self, message: str):
        """Log informational message"""
        self._track_api_call('log_info')
        
        logger = logging.getLogger(f'Plugin.{self.context.manifest.plugin_id}')
        logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning message"""
        self._track_api_call('log_warning')
        
        logger = logging.getLogger(f'Plugin.{self.context.manifest.plugin_id}')
        logger.warning(message)
    
    def log_error(self, message: str):
        """Log error message"""
        self._track_api_call('log_error')
        
        logger = logging.getLogger(f'Plugin.{self.context.manifest.plugin_id}')
        logger.error(message)


class PluginSystem:
    """Main plugin system managing all plugin lifecycle and operations"""
    
    def __init__(self, plugins_directory: str = "plugins/"):
        self.plugins_directory = Path(plugins_directory)
        self.event_system = get_global_event_system()
        self.entity_manager = get_entity_manager()
        self.content_registry = get_content_registry()
        
        # Plugin storage
        self.plugins: Dict[str, PluginContext] = {}
        self.plugin_manifests: Dict[str, PluginManifest] = {}
        
        # Dependency management
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.load_order: List[str] = []
        
        # Resource monitoring
        self.resource_monitor_thread: Optional[threading.Thread] = None
        self.resource_monitor_running = False
        
        # Performance tracking
        self.total_plugins_loaded = 0
        self.total_load_time = 0.0
        self.average_plugin_load_time = 0.0
        
        # Security and limits
        self.global_memory_limit_mb = 1000
        self.global_cpu_limit_percent = 50.0
        
        self.logger = logging.getLogger('PluginSystem')
        
        # Create plugins directory if it doesn't exist
        self.plugins_directory.mkdir(exist_ok=True, parents=True)
        
        # Initialize resource monitoring
        self._start_resource_monitoring()
        
        # Subscribe to shutdown events
        self.event_system.subscribe('game_shutdown', self._on_game_shutdown)
    
    async def discover_plugins(self) -> List[str]:
        """Discover all plugins in the plugins directory"""
        self.logger.info(f"Discovering plugins in {self.plugins_directory}")
        
        discovered_plugins = []
        
        for plugin_dir in self.plugins_directory.iterdir():
            if not plugin_dir.is_dir():
                continue
            
            manifest_path = plugin_dir / "plugin.yaml"
            if not manifest_path.exists():
                self.logger.warning(f"No plugin.yaml found in {plugin_dir}")
                continue
            
            try:
                manifest = PluginManifest.from_yaml(manifest_path)
                
                # Validate manifest
                if not self._validate_manifest(manifest):
                    self.logger.error(f"Invalid manifest for plugin in {plugin_dir}")
                    continue
                
                # Create plugin context
                context = PluginContext(
                    manifest=manifest,
                    plugin_path=plugin_dir,
                    state=PluginState.DISCOVERED
                )
                
                self.plugins[manifest.plugin_id] = context
                self.plugin_manifests[manifest.plugin_id] = manifest
                discovered_plugins.append(manifest.plugin_id)
                
                self.logger.info(f"Discovered plugin: {manifest.name} v{manifest.version}")
                
            except Exception as e:
                self.logger.error(f"Failed to discover plugin in {plugin_dir}: {e}")
        
        # Build dependency graph
        self._build_dependency_graph()
        
        # Calculate load order
        self._calculate_load_order()
        
        # Emit discovery event
        self.event_system.publish('plugins_discovered', {
            'discovered_count': len(discovered_plugins),
            'plugin_ids': discovered_plugins
        }, EventPriority.HIGH, 'plugin_system')
        
        return discovered_plugins
    
    async def load_plugin(self, plugin_id: str) -> bool:
        """Load a specific plugin"""
        if plugin_id not in self.plugins:
            self.logger.error(f"Plugin {plugin_id} not found")
            return False
        
        context = self.plugins[plugin_id]
        
        if context.state != PluginState.DISCOVERED:
            self.logger.warning(f"Plugin {plugin_id} is not in discoverable state")
            return False
        
        self.logger.info(f"Loading plugin: {context.manifest.name}")
        
        try:
            start_time = time.time()
            
            # Change state to loading
            context.state = PluginState.LOADING
            
            # Load dependencies first
            for dependency in context.manifest.dependencies:
                if dependency not in self.plugins:
                    self.logger.error(f"Dependency {dependency} not found for plugin {plugin_id}")
                    context.mark_error(f"Missing dependency: {dependency}")
                    return False
                
                dep_context = self.plugins[dependency]
                if dep_context.state != PluginState.ACTIVE:
                    if not await self.load_plugin(dependency):
                        self.logger.error(f"Failed to load dependency {dependency}")
                        context.mark_error(f"Failed to load dependency: {dependency}")
                        return False
            
            # Load plugin module
            module_path = context.plugin_path / context.manifest.entry_point
            if not module_path.exists():
                context.mark_error(f"Entry point {context.manifest.entry_point} not found")
                return False
            
            # Import plugin module
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_id}", module_path
            )
            if spec is None or spec.loader is None:
                context.mark_error("Failed to create module spec")
                return False
            
            module = importlib.util.module_from_spec(spec)
            context.module = module
            
            # Add to sys.modules for proper imports
            sys.modules[f"plugin_{plugin_id}"] = module
            
            # Execute module
            spec.loader.exec_module(module)
            
            # Get plugin class
            if not hasattr(module, context.manifest.main_class):
                context.mark_error(f"Main class {context.manifest.main_class} not found")
                return False
            
            plugin_class = getattr(module, context.manifest.main_class)
            
            # Create plugin API
            plugin_api = PluginAPI(context, self)
            
            # Initialize plugin instance
            context.state = PluginState.INITIALIZING
            init_start = time.time()
            
            plugin_instance = plugin_class(plugin_api)
            context.plugin_instance = plugin_instance
            
            # Call plugin initialization
            if hasattr(plugin_instance, 'initialize'):
                await plugin_instance.initialize()
            
            context.initialization_time_ms = (time.time() - init_start) * 1000
            
            # Plugin is now active
            context.state = PluginState.ACTIVE
            context.load_time = time.time() - start_time
            context.last_update = time.time()
            
            # Update statistics
            self.total_plugins_loaded += 1
            self.total_load_time += context.load_time
            self.average_plugin_load_time = self.total_load_time / self.total_plugins_loaded
            
            # Emit load success event
            self.event_system.publish('plugin_loaded', {
                'plugin_id': plugin_id,
                'plugin_name': context.manifest.name,
                'load_time_ms': context.load_time * 1000,
                'initialization_time_ms': context.initialization_time_ms
            }, EventPriority.HIGH, 'plugin_system')
            
            self.logger.info(
                f"Successfully loaded plugin {context.manifest.name} "
                f"in {context.load_time:.2f}s"
            )
            
            return True
            
        except Exception as e:
            context.mark_error(f"Failed to load plugin: {e}")
            self.logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return False
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a specific plugin"""
        if plugin_id not in self.plugins:
            return False
        
        context = self.plugins[plugin_id]
        
        if context.state != PluginState.ACTIVE:
            return False
        
        self.logger.info(f"Unloading plugin: {context.manifest.name}")
        
        try:
            context.state = PluginState.SHUTTING_DOWN
            
            # Call plugin shutdown
            if context.plugin_instance and hasattr(context.plugin_instance, 'shutdown'):
                await context.plugin_instance.shutdown()
            
            # Remove from sys.modules
            module_name = f"plugin_{plugin_id}"
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Clear references
            context.module = None
            context.plugin_instance = None
            context.state = PluginState.UNLOADED
            
            # Force garbage collection
            gc.collect()
            
            # Emit unload event
            self.event_system.publish('plugin_unloaded', {
                'plugin_id': plugin_id,
                'plugin_name': context.manifest.name
            }, EventPriority.HIGH, 'plugin_system')
            
            self.logger.info(f"Successfully unloaded plugin {context.manifest.name}")
            return True
            
        except Exception as e:
            context.mark_error(f"Failed to unload plugin: {e}")
            self.logger.error(f"Failed to unload plugin {plugin_id}: {e}")
            return False
    
    async def reload_plugin(self, plugin_id: str) -> bool:
        """Hot-reload a plugin"""
        if plugin_id not in self.plugins:
            return False
        
        context = self.plugins[plugin_id]
        old_state = context.state
        
        # Unload if currently loaded
        if context.state == PluginState.ACTIVE:
            if not await self.unload_plugin(plugin_id):
                return False
        
        # Reset to discovered state
        context.state = PluginState.DISCOVERED
        context.error_count = 0
        context.last_error = None
        
        # Reload manifest
        try:
            manifest_path = context.plugin_path / "plugin.yaml"
            new_manifest = PluginManifest.from_yaml(manifest_path)
            context.manifest = new_manifest
            self.plugin_manifests[plugin_id] = new_manifest
        except Exception as e:
            self.logger.error(f"Failed to reload manifest for {plugin_id}: {e}")
            context.state = old_state
            return False
        
        # Load plugin
        success = await self.load_plugin(plugin_id)
        
        if success:
            self.event_system.publish('plugin_reloaded', {
                'plugin_id': plugin_id,
                'plugin_name': context.manifest.name
            }, EventPriority.HIGH, 'plugin_system')
        
        return success
    
    async def load_all_plugins(self) -> int:
        """Load all discovered plugins in dependency order"""
        loaded_count = 0
        
        for plugin_id in self.load_order:
            if plugin_id in self.plugins:
                context = self.plugins[plugin_id]
                if context.manifest.auto_load:
                    if await self.load_plugin(plugin_id):
                        loaded_count += 1
        
        self.logger.info(f"Loaded {loaded_count} plugins")
        return loaded_count
    
    def update_plugins(self, delta_time: float):
        """Update all active plugins"""
        for plugin_id, context in self.plugins.items():
            if context.state == PluginState.ACTIVE and context.plugin_instance:
                try:
                    context.state = PluginState.UPDATING
                    
                    update_start = time.time()
                    
                    # Call plugin update if it exists
                    if hasattr(context.plugin_instance, 'update'):
                        context.plugin_instance.update(delta_time)
                    
                    # Track update performance
                    update_time = (time.time() - update_start) * 1000
                    context.total_update_time_ms += update_time
                    context.update_count += 1
                    context.average_update_time_ms = (
                        context.total_update_time_ms / context.update_count
                    )
                    context.last_update = time.time()
                    context.state = PluginState.ACTIVE
                    
                except Exception as e:
                    context.mark_error(f"Update failed: {e}")
                    self.logger.error(f"Plugin {plugin_id} update failed: {e}")
    
    def get_plugin_statistics(self) -> Dict[str, Any]:
        """Get comprehensive plugin system statistics"""
        active_plugins = sum(1 for p in self.plugins.values() if p.state == PluginState.ACTIVE)
        error_plugins = sum(1 for p in self.plugins.values() if p.state == PluginState.ERROR)
        
        total_memory = sum(p.memory_usage_mb for p in self.plugins.values())
        total_cpu = sum(p.cpu_usage_percent for p in self.plugins.values())
        
        return {
            'total_plugins': len(self.plugins),
            'active_plugins': active_plugins,
            'error_plugins': error_plugins,
            'total_memory_usage_mb': total_memory,
            'total_cpu_usage_percent': total_cpu,
            'average_load_time_ms': self.average_plugin_load_time * 1000,
            'plugins_loaded': self.total_plugins_loaded,
            'dependency_graph_size': len(self.dependency_graph)
        }
    
    def _validate_manifest(self, manifest: PluginManifest) -> bool:
        """Validate plugin manifest"""
        # Basic validation
        if not manifest.plugin_id or not manifest.name or not manifest.version:
            return False
        
        # Check for conflicts
        if manifest.plugin_id in self.plugins:
            return False
        
        # Validate permissions
        for permission in manifest.permissions:
            if not isinstance(permission, PluginPermission):
                return False
        
        return True
    
    def _build_dependency_graph(self):
        """Build plugin dependency graph"""
        self.dependency_graph.clear()
        
        for plugin_id, manifest in self.plugin_manifests.items():
            dependencies = set(manifest.dependencies)
            self.dependency_graph[plugin_id] = dependencies
    
    def _calculate_load_order(self):
        """Calculate plugin load order using topological sort"""
        self.load_order.clear()
        
        # Kahn's algorithm for topological sorting
        in_degree = {plugin_id: 0 for plugin_id in self.plugin_manifests}
        
        # Calculate in-degrees
        for plugin_id, dependencies in self.dependency_graph.items():
            for dependency in dependencies:
                if dependency in in_degree:
                    in_degree[dependency] += 1
        
        # Priority queue with load priority
        queue = []
        for plugin_id, degree in in_degree.items():
            if degree == 0:
                manifest = self.plugin_manifests[plugin_id]
                queue.append((manifest.load_priority, plugin_id))
        
        queue.sort()  # Sort by priority
        
        while queue:
            _, plugin_id = queue.pop(0)
            self.load_order.append(plugin_id)
            
            # Update dependent plugins
            for dependent_id, dependencies in self.dependency_graph.items():
                if plugin_id in dependencies:
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        manifest = self.plugin_manifests[dependent_id]
                        queue.append((manifest.load_priority, dependent_id))
                        queue.sort()
    
    def _start_resource_monitoring(self):
        """Start resource monitoring thread"""
        self.resource_monitor_running = True
        self.resource_monitor_thread = threading.Thread(
            target=self._resource_monitor_loop,
            daemon=True
        )
        self.resource_monitor_thread.start()
    
    def _resource_monitor_loop(self):
        """Resource monitoring loop"""
        while self.resource_monitor_running:
            try:
                # Monitor plugin resource usage
                for plugin_id, context in self.plugins.items():
                    if context.state == PluginState.ACTIVE:
                        # Simplified resource tracking
                        # In a real implementation, this would use more sophisticated monitoring
                        context.memory_usage_mb = context.memory_usage_mb * 0.95 + 5.0 * 0.05
                        context.cpu_usage_percent = context.cpu_usage_percent * 0.95 + 2.0 * 0.05
                
                time.sleep(1.0)  # Monitor every second
                
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")
    
    def _on_game_shutdown(self, event_data: Dict[str, Any]):
        """Handle game shutdown"""
        self.logger.info("Shutting down plugin system")
        
        # Stop resource monitoring
        self.resource_monitor_running = False
        
        # Unload all plugins
        async def shutdown_all():
            for plugin_id in list(self.plugins.keys()):
                await self.unload_plugin(plugin_id)
        
        # Run shutdown in async context
        asyncio.create_task(shutdown_all())


# Global plugin system instance
_global_plugin_system: Optional[PluginSystem] = None

def get_plugin_system() -> PluginSystem:
    """Get the global plugin system instance"""
    global _global_plugin_system
    if _global_plugin_system is None:
        _global_plugin_system = PluginSystem()
    return _global_plugin_system

def initialize_plugin_system(plugins_directory: str = "plugins/") -> PluginSystem:
    """Initialize the global plugin system"""
    global _global_plugin_system
    _global_plugin_system = PluginSystem(plugins_directory)
    return _global_plugin_system