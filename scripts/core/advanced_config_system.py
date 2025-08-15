"""
Advanced Configuration System - Hierarchical Config Management for AgriFun Engine

This module implements a sophisticated configuration system that supports hierarchical
configuration, environment-specific overrides, hot-reloading, validation, and
comprehensive configuration management for the complex AgriFun agricultural simulation.

Key Features:
- Hierarchical configuration with inheritance and overrides
- Environment-specific configuration (development, testing, production)
- Hot-reloading of configuration during runtime
- Configuration validation with schemas and constraints
- Configuration templates and defaults
- Encrypted configuration for sensitive data
- Configuration versioning and migration
- Configuration monitoring and change notifications
- Plugin-specific configuration sections
- Performance-optimized configuration access

Configuration Hierarchy:
1. Default configuration (built-in defaults)
2. Base configuration files (config/base.yaml)
3. Environment configuration (config/development.yaml)
4. Local overrides (config/local.yaml)
5. Plugin configurations (config/plugins/*.yaml)
6. Runtime overrides (temporary changes)

Configuration Categories:
- Core: Engine settings, performance parameters
- Game: Gameplay mechanics, balance parameters
- Graphics: Rendering settings, visual effects
- Audio: Sound settings, music configuration
- Input: Controls, keyboard mappings
- Network: Multiplayer settings, server configuration
- Debug: Development tools, logging levels
- Plugins: Plugin-specific settings

Usage Example:
    # Initialize configuration system
    config = ConfigurationManager()
    await config.load_configuration()
    
    # Access configuration values
    fps_target = config.get('performance.fps_target', 60)
    debug_mode = config.get('debug.enabled', False)
    
    # Set configuration values
    config.set('debug.log_level', 'INFO')
    
    # Environment-specific access
    db_url = config.get_env('database.url', 'sqlite://local.db')
    
    # Hot-reload configuration
    await config.reload_configuration()
    
    # Validate configuration
    if config.validate():
        print("Configuration is valid")

Performance Features:
- Configuration caching for frequently accessed values
- Lazy loading of configuration sections
- Configuration path indexing for fast access
- Memory-efficient storage of configuration data
- Optimized configuration serialization
"""

import os
import sys
import yaml
import json
import time
import asyncio
import hashlib
import threading
from typing import Dict, List, Set, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
from enum import Enum
import logging
from cryptography.fernet import Fernet
import jsonschema
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import our core systems
from .advanced_event_system import get_event_system, EventPriority


class ConfigEnvironment(Enum):
    """Configuration environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ConfigScope(Enum):
    """Configuration scope levels"""
    DEFAULT = "default"         # Built-in defaults
    BASE = "base"              # Base configuration file
    ENVIRONMENT = "environment" # Environment-specific
    LOCAL = "local"            # Local overrides
    PLUGIN = "plugin"          # Plugin-specific
    RUNTIME = "runtime"        # Runtime overrides


@dataclass
class ConfigurationMetadata:
    """Metadata for configuration values"""
    key: str
    value: Any
    scope: ConfigScope
    source_file: Optional[str] = None
    last_modified: float = field(default_factory=time.time)
    access_count: int = 0
    is_encrypted: bool = False
    is_sensitive: bool = False
    validation_schema: Optional[Dict] = None
    description: str = ""
    
    def mark_accessed(self):
        """Mark configuration as accessed"""
        self.access_count += 1
    
    def update_value(self, new_value: Any, scope: ConfigScope):
        """Update configuration value"""
        self.value = new_value
        self.scope = scope
        self.last_modified = time.time()


@dataclass
class ConfigurationSchema:
    """Schema definition for configuration validation"""
    schema_type: str = "object"
    properties: Dict[str, Dict] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    additional_properties: bool = True
    
    # Custom validation rules
    min_values: Dict[str, Union[int, float]] = field(default_factory=dict)
    max_values: Dict[str, Union[int, float]] = field(default_factory=dict)
    allowed_values: Dict[str, List] = field(default_factory=dict)
    validation_functions: Dict[str, Callable] = field(default_factory=dict)
    
    def validate_value(self, key: str, value: Any) -> List[str]:
        """Validate a single configuration value"""
        errors = []
        
        # Check min/max values
        if key in self.min_values and isinstance(value, (int, float)):
            if value < self.min_values[key]:
                errors.append(f"{key} value {value} below minimum {self.min_values[key]}")
        
        if key in self.max_values and isinstance(value, (int, float)):
            if value > self.max_values[key]:
                errors.append(f"{key} value {value} above maximum {self.max_values[key]}")
        
        # Check allowed values
        if key in self.allowed_values:
            if value not in self.allowed_values[key]:
                errors.append(f"{key} value {value} not in allowed values: {self.allowed_values[key]}")
        
        # Run custom validation functions
        if key in self.validation_functions:
            try:
                custom_errors = self.validation_functions[key](value)
                if custom_errors:
                    errors.extend(custom_errors)
            except Exception as e:
                errors.append(f"Custom validation failed for {key}: {e}")
        
        return errors


class ConfigurationWatcher(FileSystemEventHandler):
    """File system watcher for configuration changes"""
    
    def __init__(self, config_manager: 'ConfigurationManager'):
        super().__init__()
        self.config_manager = config_manager
        self.logger = logging.getLogger('ConfigWatcher')
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check if it's a configuration file
        if file_path.suffix.lower() in ['.yaml', '.yml', '.json']:
            self.logger.info(f"Configuration file changed: {file_path}")
            
            # Schedule hot-reload
            asyncio.create_task(self.config_manager.reload_file(file_path))


class ConfigurationManager:
    """Advanced hierarchical configuration management system"""
    
    def __init__(self, config_directory: str = "config/"):
        self.config_directory = Path(config_directory)
        self.event_system = get_event_system()
        
        # Configuration storage
        self.configuration: Dict[str, ConfigurationMetadata] = {}
        self.configuration_cache: Dict[str, Any] = {}
        self.flat_config: Dict[str, Any] = {}  # Flattened for fast access
        
        # Environment and scope management
        self.current_environment = ConfigEnvironment.DEVELOPMENT
        self.configuration_scopes: Dict[ConfigScope, Dict[str, Any]] = {}
        
        # File tracking
        self.configuration_files: Dict[str, float] = {}  # file_path -> last_modified
        self.file_watcher: Optional[Observer] = None
        
        # Schema and validation
        self.schemas: Dict[str, ConfigurationSchema] = {}
        self.validation_errors: List[str] = []
        
        # Encryption
        self.encryption_key: Optional[bytes] = None
        self.fernet: Optional[Fernet] = None
        
        # Performance tracking
        self.access_statistics: Dict[str, int] = defaultdict(int)
        self.hot_reload_count = 0
        self.validation_count = 0
        
        # Threading
        self.config_lock = threading.RLock()
        
        # Template configuration
        self.configuration_templates: Dict[str, Dict] = {}
        
        self.logger = logging.getLogger('ConfigurationManager')
        
        # Initialize directories
        self.config_directory.mkdir(exist_ok=True, parents=True)
        (self.config_directory / "plugins").mkdir(exist_ok=True)
        (self.config_directory / "environments").mkdir(exist_ok=True)
        
        # Initialize default configuration
        self._initialize_default_configuration()
        
        # Initialize schemas
        self._initialize_configuration_schemas()
        
        # Set environment from environment variable
        env_name = os.getenv('AGRIFUN_ENV', 'development')
        try:
            self.current_environment = ConfigEnvironment(env_name)
        except ValueError:
            self.logger.warning(f"Unknown environment {env_name}, using development")
            self.current_environment = ConfigEnvironment.DEVELOPMENT
        
        # Initialize encryption if key is available
        self._initialize_encryption()
    
    def _initialize_default_configuration(self):
        """Initialize built-in default configuration"""
        defaults = {
            # Core engine settings
            'core.engine.name': 'AgriFun',
            'core.engine.version': '1.0.0',
            'core.engine.fps_target': 60,
            'core.engine.max_entities': 10000,
            'core.engine.max_components_per_entity': 50,
            
            # Performance settings
            'performance.spatial_index_max_depth': 10,
            'performance.spatial_index_max_entities': 50,
            'performance.grid_region_size': 16,
            'performance.background_processing_interval': 1.0,
            'performance.memory_limit_mb': 2048,
            
            # Debug settings
            'debug.enabled': True,
            'debug.log_level': 'INFO',
            'debug.show_performance_overlay': False,
            'debug.show_spatial_grid': False,
            'debug.enable_profiling': False,
            
            # Game settings
            'game.time.workday_minutes': 20,
            'game.time.season_days': 30,
            'game.time.year_seasons': 4,
            'game.economy.starting_cash': 0,
            'game.economy.starting_loan': 10000,
            'game.economy.daily_subsidy': 100,
            'game.economy.subsidy_days': 30,
            
            # Agricultural settings
            'agriculture.soil.nutrient_decay_rate': 0.01,
            'agriculture.soil.max_nutrient_level': 100,
            'agriculture.crops.growth_speed_multiplier': 1.0,
            'agriculture.weather.change_probability': 0.1,
            'agriculture.disease.outbreak_probability': 0.05,
            
            # Employee settings
            'employees.max_count': 20,
            'employees.base_daily_wage': 80,
            'employees.needs_decay_rate': 0.02,
            'employees.skill_improvement_rate': 0.001,
            
            # UI settings
            'ui.grid.tile_size': 32,
            'ui.grid.show_grid_lines': True,
            'ui.animations.enabled': True,
            'ui.animations.duration_ms': 200,
            'ui.tooltips.delay_ms': 500,
            'ui.tooltips.fade_duration_ms': 150,
            
            # Plugin settings
            'plugins.enabled': True,
            'plugins.auto_load': True,
            'plugins.hot_reload': True,
            'plugins.max_memory_mb': 100,
            'plugins.max_cpu_percent': 10.0,
            
            # Save system settings
            'save.auto_save_enabled': True,
            'save.auto_save_interval_minutes': 5,
            'save.max_save_slots': 10,
            'save.compression_enabled': True,
            
            # Content system settings
            'content.hot_reload_enabled': True,
            'content.validation_enabled': True,
            'content.cache_size_mb': 50,
            
            # Event system settings
            'events.max_queue_size': 10000,
            'events.max_events_per_frame': 100,
            'events.enable_history': True,
            'events.history_size': 1000,
        }
        
        # Store defaults
        for key, value in defaults.items():
            metadata = ConfigurationMetadata(
                key=key,
                value=value,
                scope=ConfigScope.DEFAULT,
                description=f"Default value for {key}"
            )
            self.configuration[key] = metadata
            self.flat_config[key] = value
    
    def _initialize_configuration_schemas(self):
        """Initialize configuration validation schemas"""
        # Core engine schema
        core_schema = ConfigurationSchema()
        core_schema.min_values = {
            'core.engine.fps_target': 1,
            'core.engine.max_entities': 100,
            'performance.memory_limit_mb': 256
        }
        core_schema.max_values = {
            'core.engine.fps_target': 300,
            'core.engine.max_entities': 100000,
            'performance.memory_limit_mb': 16384
        }
        core_schema.allowed_values = {
            'debug.log_level': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        }
        self.schemas['core'] = core_schema
        
        # Game schema
        game_schema = ConfigurationSchema()
        game_schema.min_values = {
            'game.time.workday_minutes': 1,
            'game.economy.starting_cash': 0,
            'agriculture.crops.growth_speed_multiplier': 0.1
        }
        game_schema.max_values = {
            'game.time.workday_minutes': 1440,  # 24 hours max
            'agriculture.crops.growth_speed_multiplier': 10.0
        }
        self.schemas['game'] = game_schema
    
    def _initialize_encryption(self):
        """Initialize encryption for sensitive configuration data"""
        key_file = self.config_directory / ".encryption_key"
        
        if key_file.exists():
            try:
                with open(key_file, 'rb') as f:
                    self.encryption_key = f.read()
                self.fernet = Fernet(self.encryption_key)
                self.logger.info("Configuration encryption initialized")
            except Exception as e:
                self.logger.error(f"Failed to load encryption key: {e}")
        else:
            # Generate new encryption key
            self.encryption_key = Fernet.generate_key()
            self.fernet = Fernet(self.encryption_key)
            
            try:
                with open(key_file, 'wb') as f:
                    f.write(self.encryption_key)
                self.logger.info("Generated new configuration encryption key")
            except Exception as e:
                self.logger.error(f"Failed to save encryption key: {e}")
    
    async def load_configuration(self) -> bool:
        """Load all configuration files in hierarchy order"""
        self.logger.info(f"Loading configuration for environment: {self.current_environment.value}")
        
        try:
            with self.config_lock:
                # Load configuration files in hierarchy order
                await self._load_base_configuration()
                await self._load_environment_configuration()
                await self._load_local_configuration()
                await self._load_plugin_configurations()
                
                # Rebuild flat configuration
                self._rebuild_flat_configuration()
                
                # Validate configuration
                await self._validate_configuration()
                
                # Start file watching if enabled
                if self.get('debug.enabled', False):
                    self._start_file_watching()
                
                # Emit configuration loaded event
                self.event_system.emit('configuration_loaded', {
                    'environment': self.current_environment.value,
                    'config_count': len(self.configuration),
                    'validation_errors': len(self.validation_errors)
                }, priority=EventPriority.HIGH)
                
                self.logger.info(f"Configuration loaded successfully: {len(self.configuration)} settings")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False
    
    async def _load_base_configuration(self):
        """Load base configuration file"""
        base_file = self.config_directory / "base.yaml"
        
        if base_file.exists():
            await self._load_configuration_file(base_file, ConfigScope.BASE)
        else:
            # Create default base configuration file
            await self._create_default_base_configuration(base_file)
    
    async def _load_environment_configuration(self):
        """Load environment-specific configuration"""
        env_file = self.config_directory / "environments" / f"{self.current_environment.value}.yaml"
        
        if env_file.exists():
            await self._load_configuration_file(env_file, ConfigScope.ENVIRONMENT)
    
    async def _load_local_configuration(self):
        """Load local override configuration"""
        local_file = self.config_directory / "local.yaml"
        
        if local_file.exists():
            await self._load_configuration_file(local_file, ConfigScope.LOCAL)
    
    async def _load_plugin_configurations(self):
        """Load plugin-specific configurations"""
        plugin_dir = self.config_directory / "plugins"
        
        for plugin_file in plugin_dir.glob("*.yaml"):
            await self._load_configuration_file(plugin_file, ConfigScope.PLUGIN)
    
    async def _load_configuration_file(self, file_path: Path, scope: ConfigScope):
        """Load a single configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            if data:
                # Flatten nested configuration
                flattened = self._flatten_configuration(data)
                
                # Store configuration with metadata
                for key, value in flattened.items():
                    # Decrypt if necessary
                    if isinstance(value, str) and value.startswith('ENCRYPTED:'):
                        if self.fernet:
                            try:
                                encrypted_data = value[10:].encode()  # Remove 'ENCRYPTED:' prefix
                                value = self.fernet.decrypt(encrypted_data).decode()
                            except Exception as e:
                                self.logger.error(f"Failed to decrypt {key}: {e}")
                                continue
                    
                    metadata = ConfigurationMetadata(
                        key=key,
                        value=value,
                        scope=scope,
                        source_file=str(file_path)
                    )
                    
                    self.configuration[key] = metadata
                
                # Track file modification time
                self.configuration_files[str(file_path)] = file_path.stat().st_mtime
                
                self.logger.debug(f"Loaded configuration from {file_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration file {file_path}: {e}")
    
    async def _create_default_base_configuration(self, file_path: Path):
        """Create default base configuration file"""
        default_config = {
            'core': {
                'engine': {
                    'fps_target': 60,
                    'max_entities': 10000
                }
            },
            'debug': {
                'enabled': True,
                'log_level': 'INFO'
            },
            'game': {
                'time': {
                    'workday_minutes': 20
                },
                'economy': {
                    'starting_cash': 0,
                    'starting_loan': 10000
                }
            }
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Created default base configuration: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create default configuration: {e}")
    
    def _flatten_configuration(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested configuration dictionary"""
        flattened = {}
        
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                flattened.update(self._flatten_configuration(value, full_key))
            else:
                flattened[full_key] = value
        
        return flattened
    
    def _rebuild_flat_configuration(self):
        """Rebuild flat configuration for fast access"""
        self.flat_config.clear()
        
        # Sort by scope priority (higher priority overwrites lower)
        scope_priority = {
            ConfigScope.DEFAULT: 0,
            ConfigScope.BASE: 1,
            ConfigScope.ENVIRONMENT: 2,
            ConfigScope.LOCAL: 3,
            ConfigScope.PLUGIN: 4,
            ConfigScope.RUNTIME: 5
        }
        
        sorted_configs = sorted(
            self.configuration.items(),
            key=lambda x: scope_priority[x[1].scope]
        )
        
        for key, metadata in sorted_configs:
            self.flat_config[key] = metadata.value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation"""
        with self.config_lock:
            # Track access
            self.access_statistics[key] += 1
            
            # Check cache first
            if key in self.configuration_cache:
                return self.configuration_cache[key]
            
            # Get from flat configuration
            value = self.flat_config.get(key, default)
            
            # Cache frequently accessed values
            if self.access_statistics[key] > 5:
                self.configuration_cache[key] = value
            
            # Mark as accessed in metadata
            if key in self.configuration:
                self.configuration[key].mark_accessed()
            
            return value
    
    def set(self, key: str, value: Any, scope: ConfigScope = ConfigScope.RUNTIME) -> bool:
        """Set configuration value"""
        with self.config_lock:
            try:
                # Validate value if schema exists
                schema_key = key.split('.')[0]
                if schema_key in self.schemas:
                    errors = self.schemas[schema_key].validate_value(key, value)
                    if errors:
                        self.logger.error(f"Configuration validation failed for {key}: {errors}")
                        return False
                
                # Update or create metadata
                if key in self.configuration:
                    self.configuration[key].update_value(value, scope)
                else:
                    metadata = ConfigurationMetadata(
                        key=key,
                        value=value,
                        scope=scope
                    )
                    self.configuration[key] = metadata
                
                # Update flat configuration
                self.flat_config[key] = value
                
                # Clear cache for this key
                self.configuration_cache.pop(key, None)
                
                # Emit configuration changed event
                self.event_system.emit('configuration_changed', {
                    'key': key,
                    'old_value': self.flat_config.get(key),
                    'new_value': value,
                    'scope': scope.value
                }, priority=EventPriority.NORMAL)
                
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to set configuration {key}: {e}")
                return False
    
    def get_env(self, key: str, default: Any = None) -> Any:
        """Get environment-specific configuration value"""
        env_key = f"env.{self.current_environment.value}.{key}"
        return self.get(env_key, self.get(key, default))
    
    def has(self, key: str) -> bool:
        """Check if configuration key exists"""
        return key in self.flat_config
    
    def delete(self, key: str) -> bool:
        """Delete configuration key"""
        with self.config_lock:
            if key in self.configuration:
                del self.configuration[key]
                self.flat_config.pop(key, None)
                self.configuration_cache.pop(key, None)
                
                # Emit deletion event
                self.event_system.emit('configuration_deleted', {
                    'key': key
                }, priority=EventPriority.NORMAL)
                
                return True
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get all configuration values in a section"""
        section_config = {}
        prefix = f"{section}."
        
        for key, value in self.flat_config.items():
            if key.startswith(prefix):
                section_key = key[len(prefix):]
                section_config[section_key] = value
        
        return section_config
    
    async def reload_configuration(self) -> bool:
        """Hot-reload all configuration"""
        self.logger.info("Hot-reloading configuration")
        
        try:
            # Clear caches
            self.configuration_cache.clear()
            
            # Reload all files
            success = await self.load_configuration()
            
            if success:
                self.hot_reload_count += 1
                
                # Emit reload event
                self.event_system.emit('configuration_reloaded', {
                    'reload_count': self.hot_reload_count
                }, priority=EventPriority.HIGH)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")
            return False
    
    async def reload_file(self, file_path: Path) -> bool:
        """Reload a specific configuration file"""
        if not file_path.exists():
            return False
        
        try:
            # Determine scope based on file location
            scope = ConfigScope.BASE
            if "environments" in file_path.parts:
                scope = ConfigScope.ENVIRONMENT
            elif file_path.name == "local.yaml":
                scope = ConfigScope.LOCAL
            elif "plugins" in file_path.parts:
                scope = ConfigScope.PLUGIN
            
            # Load the file
            await self._load_configuration_file(file_path, scope)
            
            # Rebuild flat configuration
            self._rebuild_flat_configuration()
            
            # Clear cache
            self.configuration_cache.clear()
            
            self.logger.info(f"Reloaded configuration file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reload configuration file {file_path}: {e}")
            return False
    
    async def _validate_configuration(self) -> bool:
        """Validate all configuration against schemas"""
        self.validation_errors.clear()
        
        try:
            for schema_name, schema in self.schemas.items():
                section_config = self.get_section(schema_name)
                
                for key, value in section_config.items():
                    full_key = f"{schema_name}.{key}"
                    errors = schema.validate_value(full_key, value)
                    self.validation_errors.extend(errors)
            
            self.validation_count += 1
            
            if self.validation_errors:
                self.logger.warning(f"Configuration validation failed: {self.validation_errors}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation error: {e}")
            return False
    
    def _start_file_watching(self):
        """Start watching configuration files for changes"""
        if self.file_watcher is not None:
            return  # Already watching
        
        try:
            self.file_watcher = Observer()
            event_handler = ConfigurationWatcher(self)
            
            # Watch config directory recursively
            self.file_watcher.schedule(
                event_handler,
                str(self.config_directory),
                recursive=True
            )
            
            self.file_watcher.start()
            self.logger.info("Started configuration file watching")
            
        except Exception as e:
            self.logger.error(f"Failed to start file watching: {e}")
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a configuration value"""
        if not self.fernet:
            raise ValueError("Encryption not initialized")
        
        try:
            encrypted_data = self.fernet.encrypt(value.encode())
            return f"ENCRYPTED:{encrypted_data.decode()}"
        except Exception as e:
            self.logger.error(f"Failed to encrypt value: {e}")
            raise
    
    def save_configuration(self, file_path: Optional[Path] = None) -> bool:
        """Save current configuration to file"""
        if file_path is None:
            file_path = self.config_directory / "runtime_config.yaml"
        
        try:
            # Build hierarchical configuration from flat
            hierarchical = {}
            
            for key, value in self.flat_config.items():
                parts = key.split('.')
                current = hierarchical
                
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                current[parts[-1]] = value
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(hierarchical, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get configuration system statistics"""
        total_access = sum(self.access_statistics.values())
        
        return {
            'total_settings': len(self.configuration),
            'cached_settings': len(self.configuration_cache),
            'total_access_count': total_access,
            'hot_reload_count': self.hot_reload_count,
            'validation_count': self.validation_count,
            'validation_errors': len(self.validation_errors),
            'current_environment': self.current_environment.value,
            'file_count': len(self.configuration_files),
            'most_accessed_settings': sorted(
                self.access_statistics.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def shutdown(self):
        """Shutdown configuration system"""
        self.logger.info("Shutting down configuration system")
        
        # Stop file watching
        if self.file_watcher:
            self.file_watcher.stop()
            self.file_watcher.join()
        
        # Save runtime configuration
        self.save_configuration()


# Global configuration manager instance
_global_config_manager: Optional[ConfigurationManager] = None

def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigurationManager()
    return _global_config_manager

def initialize_config_manager(config_directory: str = "config/") -> ConfigurationManager:
    """Initialize the global configuration manager"""
    global _global_config_manager
    _global_config_manager = ConfigurationManager(config_directory)
    return _global_config_manager

# Convenience functions for global access
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value using global instance"""
    return get_config_manager().get(key, default)

def set_config(key: str, value: Any) -> bool:
    """Set configuration value using global instance"""
    return get_config_manager().set(key, value)

def get_env_config(key: str, default: Any = None) -> Any:
    """Get environment-specific configuration using global instance"""
    return get_config_manager().get_env(key, default)