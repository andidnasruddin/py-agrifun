"""
Configuration System - Hierarchical Settings Management for AgriFun Comprehensive Engine

This module implements a sophisticated configuration management system that supports
the complex settings requirements of the comprehensive agricultural simulation.
Features hierarchical configuration, environment-specific settings, validation,
hot-reloading, and secure configuration management.

Key Features:
- 6-level configuration hierarchy with proper inheritance
- Environment-specific configurations (development, testing, production)
- Hot-reloading with file system monitoring
- Schema-based validation with custom validation rules
- Secure configuration with encryption support for sensitive data
- Configuration caching and indexed access for performance
- Configuration versioning and migration support
- Event-driven configuration updates
- Configuration export and backup functionality

Configuration Hierarchy (Lowest to Highest Priority):
1. DEFAULT: Built-in system defaults
2. SYSTEM: System-wide configuration files
3. USER: User-specific configuration  
4. PROJECT: Project-specific settings
5. ENVIRONMENT: Environment-specific overrides (dev/test/prod)
6. RUNTIME: Runtime overrides and temporary settings

Configuration Categories:
- Core: System core settings (event processing, memory management)
- Rendering: Graphics and display settings
- Audio: Sound and music configuration
- Input: Controls and input device settings
- Gameplay: Game mechanics and balance parameters
- Performance: Optimization and performance tuning
- Debug: Development and debugging settings
- Network: Multiplayer and networking configuration
- Localization: Language and region settings
- Accessibility: Accessibility options and accommodations

Environment Support:
- Development: Debug features, verbose logging, development tools
- Testing: Test configurations, mock services, automated testing
- Production: Optimized settings, minimal logging, security hardening

Usage Example:
    # Initialize configuration system
    config_manager = ConfigurationManager()
    await config_manager.load_configurations()
    
    # Get configuration values with hierarchy resolution
    max_entities = config_manager.get('core.entity_manager.max_entities', default=10000)
    debug_enabled = config_manager.get('debug.enabled', default=False)
    
    # Set runtime configuration
    config_manager.set('gameplay.time_scale', 2.0, scope=ConfigScope.RUNTIME)
    
    # Environment-specific settings
    config_manager.set_environment('production')
    db_connection = config_manager.get('database.connection_string')
    
    # Configuration validation
    errors = config_manager.validate_configuration()
    if errors:
        print(f"Configuration errors: {errors}")
    
    # Hot-reload during development
    config_manager.enable_hot_reload()
    # Files automatically reloaded when changed
    
    # Secure configuration
    config_manager.set_encrypted('api.secret_key', 'sensitive_value')
    secret = config_manager.get_encrypted('api.secret_key')

Performance Features:
- Configuration caching with smart invalidation
- Indexed configuration access for frequently used settings
- Lazy loading of configuration files
- Configuration change batching
- Memory-efficient configuration storage
"""

import os
import json
import yaml
import time
import hashlib
import threading
from typing import Dict, List, Set, Any, Optional, Union, Callable, TypeVar
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
from enum import Enum
import logging
from cryptography.fernet import Fernet
import base64

# Import our core systems
from .event_system import get_global_event_system, EventPriority

# Type definitions
ConfigValue = Union[str, int, float, bool, list, dict, None]
T = TypeVar('T')


class ConfigScope(Enum):
    """Configuration scope levels (priority order)"""
    DEFAULT = 0      # Built-in defaults
    SYSTEM = 1       # System-wide configuration
    USER = 2         # User-specific configuration
    PROJECT = 3      # Project-specific settings
    ENVIRONMENT = 4  # Environment-specific overrides
    RUNTIME = 5      # Runtime overrides


class ConfigEnvironment(Enum):
    """Supported environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class ConfigCategory(Enum):
    """Configuration categories for organization"""
    CORE = "core"
    RENDERING = "rendering"
    AUDIO = "audio"
    INPUT = "input"
    GAMEPLAY = "gameplay"
    PERFORMANCE = "performance"
    DEBUG = "debug"
    NETWORK = "network"
    LOCALIZATION = "localization"
    ACCESSIBILITY = "accessibility"


@dataclass
class ConfigurationMetadata:
    """Metadata for configuration values"""
    key: str
    value: ConfigValue
    scope: ConfigScope
    category: ConfigCategory
    source_file: Optional[str] = None
    encrypted: bool = False
    validation_rules: List[str] = field(default_factory=list)
    description: str = ""
    last_modified: float = field(default_factory=time.time)
    access_count: int = 0
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ConfigurationSchema:
    """Schema definition for configuration validation"""
    required_keys: List[str] = field(default_factory=list)
    optional_keys: List[str] = field(default_factory=list)
    key_types: Dict[str, type] = field(default_factory=dict)
    key_constraints: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    custom_validators: List[Callable] = field(default_factory=list)
    environment_specific: Dict[ConfigEnvironment, Dict[str, Any]] = field(default_factory=dict)


class ConfigurationWatcher:
    """File system watcher for configuration hot-reload"""
    
    def __init__(self, config_manager: 'ConfigurationManager'):
        self.config_manager = config_manager
        self.watched_files: Dict[str, float] = {}
        self.watching = False
        self.watch_thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger('ConfigurationWatcher')
    
    def start_watching(self):
        """Start watching configuration files for changes"""
        if self.watching:
            return
        
        self.watching = True
        self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()
        self.logger.info("Configuration file watching started")
    
    def stop_watching(self):
        """Stop watching configuration files"""
        self.watching = False
        if self.watch_thread:
            self.watch_thread.join(timeout=1.0)
        self.logger.info("Configuration file watching stopped")
    
    def add_file(self, file_path: str):
        """Add a file to the watch list"""
        if os.path.exists(file_path):
            self.watched_files[file_path] = os.path.getmtime(file_path)
    
    def remove_file(self, file_path: str):
        """Remove a file from the watch list"""
        self.watched_files.pop(file_path, None)
    
    def _watch_loop(self):
        """Main watching loop"""
        while self.watching:
            try:
                for file_path, last_mtime in list(self.watched_files.items()):
                    if os.path.exists(file_path):
                        current_mtime = os.path.getmtime(file_path)
                        if current_mtime > last_mtime:
                            self.watched_files[file_path] = current_mtime
                            self.logger.info(f"Configuration file changed: {file_path}")
                            self.config_manager._on_file_changed(file_path)
                    else:
                        # File was deleted
                        self.remove_file(file_path)
                        self.logger.warning(f"Configuration file deleted: {file_path}")
                
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                self.logger.error(f"Error in configuration watch loop: {e}")
                time.sleep(1.0)


class ConfigurationManager:
    """Central configuration management system"""
    
    def __init__(self, base_directory: str = "config/"):
        self.base_directory = Path(base_directory)
        self.event_system = get_global_event_system()
        
        # Configuration storage organized by scope
        self.configurations: Dict[ConfigScope, Dict[str, ConfigValue]] = {
            scope: {} for scope in ConfigScope
        }
        
        # Metadata tracking
        self.metadata: Dict[str, ConfigurationMetadata] = {}
        
        # Environment and category management
        self.current_environment = ConfigEnvironment.DEVELOPMENT
        self.schema_registry: Dict[ConfigCategory, ConfigurationSchema] = {}
        
        # Caching and performance
        self.configuration_cache: Dict[str, ConfigValue] = {}
        self.cache_valid: bool = False
        self.access_patterns: Dict[str, int] = defaultdict(int)
        
        # Hot-reload support
        self.watcher = ConfigurationWatcher(self)
        self.hot_reload_enabled = False
        
        # Encryption support
        self.encryption_key: Optional[bytes] = None
        self.fernet: Optional[Fernet] = None
        
        # Performance metrics
        self.statistics = {
            'configurations_loaded': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'validations_performed': 0,
            'hot_reloads': 0,
            'encryption_operations': 0
        }
        
        self.logger = logging.getLogger('ConfigurationManager')
        
        # Initialize with default configurations
        self._initialize_defaults()
        
        # Register default schemas
        self._register_default_schemas()
    
    def _initialize_defaults(self):
        """Initialize default configuration values"""
        defaults = {
            # Core system settings
            'core.entity_manager.max_entities': 50000,
            'core.entity_manager.component_pool_size': 1000,
            'core.event_system.queue_size': 10000,
            'core.event_system.max_processing_time_ms': 16.67,  # 60 FPS
            'core.memory_management.gc_threshold': 0.8,
            
            # Grid system settings
            'grid.default_size': [32, 32],
            'grid.region_size': 16,
            'grid.max_entities_per_tile': 50,
            'grid.pathfinding_max_iterations': 10000,
            'grid.spatial_index_max_depth': 8,
            
            # Rendering settings
            'rendering.target_fps': 60,
            'rendering.vsync_enabled': True,
            'rendering.fullscreen': False,
            'rendering.resolution': [1920, 1080],
            'rendering.quality_level': 'high',
            'rendering.anti_aliasing': True,
            
            # Audio settings
            'audio.master_volume': 0.8,
            'audio.music_volume': 0.6,
            'audio.sfx_volume': 0.8,
            'audio.voice_volume': 0.9,
            'audio.audio_quality': 'high',
            
            # Gameplay settings
            'gameplay.auto_save_interval': 300,  # 5 minutes
            'gameplay.time_scale': 1.0,
            'gameplay.pause_on_focus_loss': True,
            'gameplay.difficulty_level': 'normal',
            'gameplay.tutorial_enabled': True,
            
            # Performance settings
            'performance.max_cpu_usage': 0.8,
            'performance.max_memory_usage_mb': 4096,
            'performance.background_processing': True,
            'performance.level_of_detail_enabled': True,
            'performance.culling_enabled': True,
            
            # Debug settings
            'debug.enabled': False,
            'debug.log_level': 'INFO',
            'debug.show_fps': False,
            'debug.show_memory_usage': False,
            'debug.profiling_enabled': False,
            'debug.crash_reporting': True,
            
            # Network settings (for future multiplayer)
            'network.server_address': 'localhost',
            'network.server_port': 7777,
            'network.connection_timeout': 10.0,
            'network.max_players': 8,
            'network.compression_enabled': True,
            
            # Localization settings
            'localization.language': 'en',
            'localization.region': 'US',
            'localization.currency_format': 'USD',
            'localization.date_format': 'MM/DD/YYYY',
            'localization.number_format': 'en_US',
            
            # Accessibility settings
            'accessibility.font_size_multiplier': 1.0,
            'accessibility.high_contrast': False,
            'accessibility.screen_reader_support': False,
            'accessibility.colorblind_support': False,
            'accessibility.subtitles_enabled': False
        }
        
        for key, value in defaults.items():
            self.configurations[ConfigScope.DEFAULT][key] = value
            
            # Create metadata
            category = self._determine_category(key)
            self.metadata[key] = ConfigurationMetadata(
                key=key,
                value=value,
                scope=ConfigScope.DEFAULT,
                category=category,
                description=f"Default value for {key}"
            )
    
    def _determine_category(self, key: str) -> ConfigCategory:
        """Determine configuration category from key"""
        category_mapping = {
            'core': ConfigCategory.CORE,
            'grid': ConfigCategory.CORE,
            'rendering': ConfigCategory.RENDERING,
            'audio': ConfigCategory.AUDIO,
            'input': ConfigCategory.INPUT,
            'gameplay': ConfigCategory.GAMEPLAY,
            'performance': ConfigCategory.PERFORMANCE,
            'debug': ConfigCategory.DEBUG,
            'network': ConfigCategory.NETWORK,
            'localization': ConfigCategory.LOCALIZATION,
            'accessibility': ConfigCategory.ACCESSIBILITY
        }
        
        prefix = key.split('.')[0]
        return category_mapping.get(prefix, ConfigCategory.CORE)
    
    def _register_default_schemas(self):
        """Register default validation schemas"""
        # Core schema
        core_schema = ConfigurationSchema(
            required_keys=['core.entity_manager.max_entities'],
            key_types={
                'core.entity_manager.max_entities': int,
                'core.event_system.queue_size': int,
                'core.memory_management.gc_threshold': float
            },
            key_constraints={
                'core.entity_manager.max_entities': {'min': 1000, 'max': 1000000},
                'core.memory_management.gc_threshold': {'min': 0.1, 'max': 1.0}
            }
        )
        self.schema_registry[ConfigCategory.CORE] = core_schema
        
        # Rendering schema
        rendering_schema = ConfigurationSchema(
            key_types={
                'rendering.target_fps': int,
                'rendering.vsync_enabled': bool,
                'rendering.fullscreen': bool,
                'rendering.resolution': list
            },
            key_constraints={
                'rendering.target_fps': {'min': 30, 'max': 240},
                'rendering.quality_level': {'choices': ['low', 'medium', 'high', 'ultra']}
            }
        )
        self.schema_registry[ConfigCategory.RENDERING] = rendering_schema
        
        # Audio schema
        audio_schema = ConfigurationSchema(
            key_types={
                'audio.master_volume': float,
                'audio.music_volume': float,
                'audio.sfx_volume': float
            },
            key_constraints={
                'audio.master_volume': {'min': 0.0, 'max': 1.0},
                'audio.music_volume': {'min': 0.0, 'max': 1.0},
                'audio.sfx_volume': {'min': 0.0, 'max': 1.0}
            }
        )
        self.schema_registry[ConfigCategory.AUDIO] = audio_schema
    
    async def load_configurations(self) -> bool:
        """Load all configuration files from the directory hierarchy"""
        self.logger.info("Loading configurations from file system")
        
        try:
            # Create directory structure if it doesn't exist
            self.base_directory.mkdir(parents=True, exist_ok=True)
            
            # Load configurations by scope
            await self._load_scope_configurations(ConfigScope.SYSTEM, "system")
            await self._load_scope_configurations(ConfigScope.USER, "user")
            await self._load_scope_configurations(ConfigScope.PROJECT, "project")
            await self._load_environment_configurations()
            
            # Invalidate cache after loading
            self._invalidate_cache()
            
            # Validate loaded configurations
            validation_errors = await self.validate_all_configurations()
            if validation_errors:
                self.logger.warning(f"Configuration validation errors: {validation_errors}")
            
            # Emit configuration loaded event
            self.event_system.publish('configurations_loaded', {
                'scopes_loaded': [scope.name for scope in ConfigScope if scope != ConfigScope.RUNTIME],
                'total_configurations': len(self.metadata),
                'validation_errors': len(validation_errors)
            }, EventPriority.HIGH, 'configuration_system')
            
            self.logger.info(f"Configurations loaded successfully: {len(self.metadata)} total")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configurations: {e}")
            return False
    
    async def _load_scope_configurations(self, scope: ConfigScope, directory_name: str):
        """Load configurations for a specific scope"""
        scope_directory = self.base_directory / directory_name
        
        if not scope_directory.exists():
            scope_directory.mkdir(parents=True, exist_ok=True)
            await self._create_example_configuration(scope_directory, scope)
            return
        
        # Load all configuration files in the directory
        for config_file in scope_directory.rglob("*.yaml"):
            await self._load_configuration_file(config_file, scope)
        
        for config_file in scope_directory.rglob("*.json"):
            await self._load_configuration_file(config_file, scope)
    
    async def _load_environment_configurations(self):
        """Load environment-specific configurations"""
        env_directory = self.base_directory / "environments"
        
        if not env_directory.exists():
            env_directory.mkdir(parents=True, exist_ok=True)
            
            # Create example environment files
            for env in ConfigEnvironment:
                await self._create_example_environment_config(env_directory, env)
            return
        
        # Load current environment configuration
        env_file = env_directory / f"{self.current_environment.value}.yaml"
        if env_file.exists():
            await self._load_configuration_file(env_file, ConfigScope.ENVIRONMENT)
    
    async def _load_configuration_file(self, file_path: Path, scope: ConfigScope):
        """Load a single configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.yaml':
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            if not config_data:
                return
            
            # Flatten nested configuration
            flattened = self._flatten_config(config_data)
            
            # Store configurations
            for key, value in flattened.items():
                self.configurations[scope][key] = value
                
                # Update or create metadata
                if key in self.metadata:
                    metadata = self.metadata[key]
                    metadata.value = value
                    metadata.scope = scope
                    metadata.source_file = str(file_path)
                    metadata.last_modified = time.time()
                else:
                    category = self._determine_category(key)
                    self.metadata[key] = ConfigurationMetadata(
                        key=key,
                        value=value,
                        scope=scope,
                        category=category,
                        source_file=str(file_path)
                    )
            
            # Add file to watcher if hot-reload is enabled
            if self.hot_reload_enabled:
                self.watcher.add_file(str(file_path))
            
            self.statistics['configurations_loaded'] += 1
            self.logger.debug(f"Loaded configuration file: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration file {file_path}: {e}")
    
    def _flatten_config(self, config_data: Dict[str, Any], prefix: str = "") -> Dict[str, ConfigValue]:
        """Flatten nested configuration dictionary"""
        result = {}
        
        for key, value in config_data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                result.update(self._flatten_config(value, full_key))
            else:
                result[full_key] = value
        
        return result
    
    def get(self, key: str, default: Optional[ConfigValue] = None) -> ConfigValue:
        """Get configuration value with hierarchy resolution"""
        # Track access patterns
        self.access_patterns[key] += 1
        
        # Check cache first
        if self.cache_valid and key in self.configuration_cache:
            self.statistics['cache_hits'] += 1
            return self.configuration_cache[key]
        
        self.statistics['cache_misses'] += 1
        
        # Resolve value through hierarchy (highest priority first)
        for scope in reversed(ConfigScope):
            if key in self.configurations[scope]:
                value = self.configurations[scope][key]
                
                # Handle encrypted values
                if key in self.metadata and self.metadata[key].encrypted:
                    value = self._decrypt_value(value)
                
                # Cache the resolved value
                self.configuration_cache[key] = value
                
                # Update metadata access count
                if key in self.metadata:
                    self.metadata[key].access_count += 1
                
                return value
        
        # Return default if not found
        return default
    
    def set(self, key: str, value: ConfigValue, scope: ConfigScope = ConfigScope.RUNTIME,
            category: Optional[ConfigCategory] = None) -> bool:
        """Set configuration value"""
        try:
            # Validate value if schema exists
            if category and category in self.schema_registry:
                errors = self._validate_value(key, value, category)
                if errors:
                    self.logger.warning(f"Configuration validation failed for {key}: {errors}")
                    return False
            
            # Store configuration
            self.configurations[scope][key] = value
            
            # Update or create metadata
            if key in self.metadata:
                metadata = self.metadata[key]
                metadata.value = value
                metadata.scope = scope
                metadata.last_modified = time.time()
            else:
                detected_category = category or self._determine_category(key)
                self.metadata[key] = ConfigurationMetadata(
                    key=key,
                    value=value,
                    scope=scope,
                    category=detected_category
                )
            
            # Invalidate cache
            self._invalidate_cache()
            
            # Emit configuration change event
            self.event_system.publish('configuration_changed', {
                'key': key,
                'value': value,
                'scope': scope.name,
                'category': (category or self._determine_category(key)).name
            }, EventPriority.NORMAL, 'configuration_system')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set configuration {key}: {e}")
            return False
    
    def set_encrypted(self, key: str, value: str, scope: ConfigScope = ConfigScope.RUNTIME) -> bool:
        """Set encrypted configuration value"""
        if not self.fernet:
            self._initialize_encryption()
        
        try:
            encrypted_value = self.fernet.encrypt(value.encode('utf-8')).decode('utf-8')
            success = self.set(key, encrypted_value, scope)
            
            if success and key in self.metadata:
                self.metadata[key].encrypted = True
                self.statistics['encryption_operations'] += 1
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to encrypt configuration {key}: {e}")
            return False
    
    def get_encrypted(self, key: str) -> Optional[str]:
        """Get decrypted configuration value"""
        if not self.fernet:
            self._initialize_encryption()
        
        encrypted_value = self.get(key)
        if encrypted_value is None:
            return None
        
        try:
            decrypted_value = self.fernet.decrypt(encrypted_value.encode('utf-8')).decode('utf-8')
            self.statistics['encryption_operations'] += 1
            return decrypted_value
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt configuration {key}: {e}")
            return None
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a configuration value"""
        if not self.fernet:
            self._initialize_encryption()
        
        try:
            if isinstance(encrypted_value, str):
                return self.fernet.decrypt(encrypted_value.encode('utf-8')).decode('utf-8')
            else:
                return str(encrypted_value)  # Return as string if not encrypted
        except Exception as e:
            self.logger.warning(f"Failed to decrypt value: {e}")
            return str(encrypted_value)  # Return as-is if decryption fails
    
    def _initialize_encryption(self):
        """Initialize encryption system"""
        if self.encryption_key is None:
            # Generate or load encryption key
            key_file = self.base_directory / ".encryption_key"
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                self.encryption_key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(self.encryption_key)
                
                # Set restrictive permissions
                key_file.chmod(0o600)
        
        self.fernet = Fernet(self.encryption_key)
    
    def set_environment(self, environment: ConfigEnvironment):
        """Set current environment and reload environment-specific configurations"""
        old_environment = self.current_environment
        self.current_environment = environment
        
        # Clear environment scope configurations
        self.configurations[ConfigScope.ENVIRONMENT].clear()
        
        # Load new environment configurations
        import asyncio
        asyncio.create_task(self._load_environment_configurations())
        
        # Invalidate cache
        self._invalidate_cache()
        
        # Emit environment change event
        self.event_system.publish('environment_changed', {
            'old_environment': old_environment.value,
            'new_environment': environment.value
        }, EventPriority.HIGH, 'configuration_system')
        
        self.logger.info(f"Environment changed from {old_environment.value} to {environment.value}")
    
    def enable_hot_reload(self):
        """Enable hot-reloading of configuration files"""
        self.hot_reload_enabled = True
        self.watcher.start_watching()
        
        # Add all current configuration files to watcher
        for metadata in self.metadata.values():
            if metadata.source_file:
                self.watcher.add_file(metadata.source_file)
        
        self.logger.info("Configuration hot-reload enabled")
    
    def disable_hot_reload(self):
        """Disable hot-reloading of configuration files"""
        self.hot_reload_enabled = False
        self.watcher.stop_watching()
        self.logger.info("Configuration hot-reload disabled")
    
    def _on_file_changed(self, file_path: str):
        """Handle configuration file change event"""
        self.logger.info(f"Reloading configuration file: {file_path}")
        
        # Determine scope from file path
        path_obj = Path(file_path)
        relative_path = path_obj.relative_to(self.base_directory)
        
        scope = ConfigScope.PROJECT  # Default
        if 'system' in relative_path.parts:
            scope = ConfigScope.SYSTEM
        elif 'user' in relative_path.parts:
            scope = ConfigScope.USER
        elif 'environments' in relative_path.parts:
            scope = ConfigScope.ENVIRONMENT
        
        # Reload the file
        import asyncio
        asyncio.create_task(self._load_configuration_file(path_obj, scope))
        
        self.statistics['hot_reloads'] += 1
        
        # Emit hot-reload event
        self.event_system.publish('configuration_hot_reloaded', {
            'file_path': file_path,
            'scope': scope.name
        }, EventPriority.NORMAL, 'configuration_system')
    
    async def validate_all_configurations(self) -> List[str]:
        """Validate all configurations against their schemas"""
        validation_errors = []
        
        for category, schema in self.schema_registry.items():
            category_configs = {
                key: metadata for key, metadata in self.metadata.items()
                if metadata.category == category
            }
            
            errors = await self._validate_category_configs(category_configs, schema)
            validation_errors.extend(errors)
        
        self.statistics['validations_performed'] += 1
        return validation_errors
    
    async def _validate_category_configs(self, configs: Dict[str, ConfigurationMetadata],
                                        schema: ConfigurationSchema) -> List[str]:
        """Validate configurations for a specific category"""
        errors = []
        
        # Check required keys
        for required_key in schema.required_keys:
            if required_key not in configs:
                errors.append(f"Missing required configuration: {required_key}")
        
        # Validate individual configurations
        for key, metadata in configs.items():
            key_errors = self._validate_value(key, metadata.value, metadata.category)
            errors.extend(key_errors)
        
        # Run custom validators
        for validator in schema.custom_validators:
            try:
                config_values = {key: metadata.value for key, metadata in configs.items()}
                custom_errors = validator(config_values)
                if custom_errors:
                    errors.extend(custom_errors)
            except Exception as e:
                errors.append(f"Custom validator error: {e}")
        
        return errors
    
    def _validate_value(self, key: str, value: ConfigValue, category: ConfigCategory) -> List[str]:
        """Validate a single configuration value"""
        errors = []
        
        if category not in self.schema_registry:
            return errors
        
        schema = self.schema_registry[category]
        
        # Type validation
        if key in schema.key_types:
            expected_type = schema.key_types[key]
            if not isinstance(value, expected_type):
                errors.append(f"{key}: Expected {expected_type.__name__}, got {type(value).__name__}")
        
        # Constraint validation
        if key in schema.key_constraints:
            constraints = schema.key_constraints[key]
            
            # Only apply numeric constraints to numeric types
            if 'min' in constraints and isinstance(value, (int, float)):
                if value < constraints['min']:
                    errors.append(f"{key}: Value {value} below minimum {constraints['min']}")
            
            if 'max' in constraints and isinstance(value, (int, float)):
                if value > constraints['max']:
                    errors.append(f"{key}: Value {value} above maximum {constraints['max']}")
            
            if 'choices' in constraints and value not in constraints['choices']:
                errors.append(f"{key}: Value {value} not in allowed choices")
        
        return errors
    
    def _invalidate_cache(self):
        """Invalidate configuration cache"""
        self.configuration_cache.clear()
        self.cache_valid = False
    
    def _rebuild_cache(self):
        """Rebuild configuration cache with frequently accessed values"""
        self.configuration_cache.clear()
        
        # Cache most frequently accessed configurations
        frequent_keys = sorted(self.access_patterns.items(), key=lambda x: x[1], reverse=True)[:100]
        
        for key, _ in frequent_keys:
            # Resolve value through hierarchy
            for scope in reversed(ConfigScope):
                if key in self.configurations[scope]:
                    value = self.configurations[scope][key]
                    if key in self.metadata and self.metadata[key].encrypted:
                        value = self._decrypt_value(value)
                    self.configuration_cache[key] = value
                    break
        
        self.cache_valid = True
    
    async def _create_example_configuration(self, directory: Path, scope: ConfigScope):
        """Create example configuration file for a scope"""
        example_configs = {
            ConfigScope.SYSTEM: {
                'core': {
                    'entity_manager': {'max_entities': 100000},
                    'memory_management': {'gc_threshold': 0.9}
                },
                'performance': {
                    'background_processing': True,
                    'max_cpu_usage': 0.9
                }
            },
            ConfigScope.USER: {
                'rendering': {
                    'resolution': [1920, 1080],
                    'fullscreen': False
                },
                'audio': {
                    'master_volume': 0.8,
                    'music_volume': 0.6
                }
            },
            ConfigScope.PROJECT: {
                'gameplay': {
                    'auto_save_interval': 300,
                    'difficulty_level': 'normal'
                },
                'debug': {
                    'enabled': False,
                    'log_level': 'INFO'
                }
            }
        }
        
        if scope in example_configs:
            example_file = directory / f"{scope.name.lower()}_config.yaml"
            with open(example_file, 'w') as f:
                yaml.dump(example_configs[scope], f, default_flow_style=False)
            
            self.logger.info(f"Created example configuration file: {example_file}")
    
    async def _create_example_environment_config(self, directory: Path, environment: ConfigEnvironment):
        """Create example environment-specific configuration"""
        env_configs = {
            ConfigEnvironment.DEVELOPMENT: {
                'debug': {'enabled': True, 'log_level': 'DEBUG', 'profiling_enabled': True},
                'performance': {'max_cpu_usage': 1.0, 'level_of_detail_enabled': False}
            },
            ConfigEnvironment.TESTING: {
                'debug': {'enabled': True, 'log_level': 'INFO', 'crash_reporting': False},
                'gameplay': {'auto_save_interval': 60}
            },
            ConfigEnvironment.PRODUCTION: {
                'debug': {'enabled': False, 'log_level': 'WARNING'},
                'performance': {'max_cpu_usage': 0.8, 'background_processing': True}
            }
        }
        
        if environment in env_configs:
            env_file = directory / f"{environment.value}.yaml"
            with open(env_file, 'w') as f:
                yaml.dump(env_configs[environment], f, default_flow_style=False)
            
            self.logger.info(f"Created example environment configuration: {env_file}")
    
    def export_configuration(self, output_path: str, include_encrypted: bool = False) -> bool:
        """Export all configurations to a single file"""
        try:
            export_data = {
                'metadata': {
                    'export_timestamp': time.time(),
                    'environment': self.current_environment.value,
                    'total_configurations': len(self.metadata)
                },
                'configurations': {}
            }
            
            # Group configurations by scope
            for scope in ConfigScope:
                scope_configs = {}
                for key, value in self.configurations[scope].items():
                    if key in self.metadata:
                        metadata = self.metadata[key]
                        if metadata.encrypted and not include_encrypted:
                            continue  # Skip encrypted values unless explicitly requested
                    
                    scope_configs[key] = value
                
                if scope_configs:
                    export_data['configurations'][scope.name] = scope_configs
            
            # Write to file
            output_path_obj = Path(output_path)
            with open(output_path_obj, 'w') as f:
                if output_path_obj.suffix.lower() == '.yaml':
                    yaml.dump(export_data, f, default_flow_style=False)
                else:
                    json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"Configuration exported to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive configuration system statistics"""
        # Calculate configuration counts by scope and category
        scope_counts = {scope.name: len(configs) for scope, configs in self.configurations.items()}
        category_counts = defaultdict(int)
        encrypted_count = 0
        
        for metadata in self.metadata.values():
            category_counts[metadata.category.name] += 1
            if metadata.encrypted:
                encrypted_count += 1
        
        # Get most accessed configurations
        top_accessed = sorted(self.access_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_configurations': len(self.metadata),
            'scope_counts': scope_counts,
            'category_counts': dict(category_counts),
            'encrypted_configurations': encrypted_count,
            'current_environment': self.current_environment.value,
            'hot_reload_enabled': self.hot_reload_enabled,
            'cache_size': len(self.configuration_cache),
            'cache_hit_rate': (
                self.statistics['cache_hits'] / 
                max(1, self.statistics['cache_hits'] + self.statistics['cache_misses'])
            ),
            'most_accessed_configurations': top_accessed,
            'performance_statistics': self.statistics
        }
    
    def shutdown(self):
        """Clean shutdown of configuration system"""
        # Stop hot-reload watcher
        if self.hot_reload_enabled:
            self.disable_hot_reload()
        
        # Emit shutdown event
        self.event_system.publish('configuration_system_shutdown', {
            'final_configuration_count': len(self.metadata),
            'total_cache_hits': self.statistics['cache_hits'],
            'total_hot_reloads': self.statistics['hot_reloads']
        }, EventPriority.CRITICAL, 'configuration_system')
        
        # Clear all data
        self.configurations.clear()
        self.metadata.clear()
        self.configuration_cache.clear()
        self.access_patterns.clear()
        
        self.logger.info("Configuration system shut down successfully")


# Global configuration manager instance
_global_configuration_manager: Optional[ConfigurationManager] = None

def get_configuration_manager() -> ConfigurationManager:
    """Get the global configuration manager instance"""
    global _global_configuration_manager
    if _global_configuration_manager is None:
        _global_configuration_manager = ConfigurationManager()
    return _global_configuration_manager

def initialize_configuration_manager(base_directory: str = "config/") -> ConfigurationManager:
    """Initialize the global configuration manager"""
    global _global_configuration_manager
    _global_configuration_manager = ConfigurationManager(base_directory)
    return _global_configuration_manager

# Convenience functions for quick access
def get_config(key: str, default: Optional[ConfigValue] = None) -> ConfigValue:
    """Quick access to configuration values"""
    return get_configuration_manager().get(key, default)

def set_config(key: str, value: ConfigValue, scope: ConfigScope = ConfigScope.RUNTIME) -> bool:
    """Quick access to set configuration values"""
    return get_configuration_manager().set(key, value, scope)