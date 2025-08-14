"""
Content Registry - Data-Driven Content System for AgriFun Comprehensive Engine

This module implements a comprehensive content management system that loads all game
mechanics, items, entities, and behaviors from external data files. This enables
infinite extensibility, modding support, and content creation without code changes.

Key Features:
- Hot-reloadable content from JSON/YAML files
- Hierarchical content inheritance (base types -> variants)
- Schema validation for all content types
- Localization support for all text content
- Version management and migration support
- Content dependency tracking and resolution
- Automatic content validation and error reporting
- Content caching and performance optimization

Content Categories:
- Crops: All plant types, varieties, and growth parameters
- Equipment: Tools, machinery, and their specifications
- Employees: Traits, skills, specializations, and generation parameters
- Diseases: Pests, diseases, and treatment options
- Research: Technology trees and advancement paths
- Contracts: Buyer types, contract templates, and market data
- Buildings: Structures, costs, and functional parameters
- Weather: Weather patterns, seasonal effects, and climate data

Directory Structure:
/data/
  /crops/
    - corn.yaml
    - wheat.yaml
    - tomato.yaml
  /equipment/
    - hand_tools.yaml
    - tractors.yaml
    - harvesters.yaml
  /employees/
    - traits.yaml
    - specializations.yaml
    - generation_rules.yaml
  /diseases/
    - fungal_diseases.yaml
    - pest_insects.yaml
    - treatments.yaml
  /research/
    - agriculture_tree.yaml
    - equipment_tree.yaml
    - sustainability_tree.yaml

Content Inheritance Example:
  base_corn.yaml:
    category: "grain_crop"
    growth_stages: [seed, sprout, vegetative, flowering, mature]
    
  hybrid_corn.yaml:
    inherits: "base_corn"
    display_name: "Hybrid Corn"
    yield_multiplier: 1.3
    disease_resistance: +0.2

Usage Example:
    # Initialize content registry
    content_registry = ContentRegistry("data/")
    await content_registry.load_all_content()
    
    # Get crop definition
    corn_data = content_registry.get_crop("corn_hybrid_premium")
    
    # Create entity from content
    entity_manager = get_entity_manager()
    crop_entity = content_registry.create_entity_from_content(
        "crop", "corn_hybrid_premium", position=(5, 3)
    )
    
    # Hot-reload content during development
    await content_registry.reload_content_type("crops")
"""

import os
import json
import yaml
import asyncio
import hashlib
from typing import Dict, List, Set, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import logging

# Import our ECS and event system
from .entity_component_system import get_entity_manager, EntityManager
from .advanced_event_system import get_event_system, EventPriority


@dataclass
class ContentMetadata:
    """Metadata for content items"""
    content_id: str
    content_type: str
    file_path: str
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    file_hash: str = ""
    dependencies: List[str] = field(default_factory=list)
    inheritance_chain: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)


@dataclass 
class ContentSchema:
    """Schema definition for content validation"""
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    field_types: Dict[str, type] = field(default_factory=dict)
    field_constraints: Dict[str, Dict] = field(default_factory=dict)
    inheritance_allowed: bool = True
    custom_validators: List[Callable] = field(default_factory=list)


class ContentValidator:
    """Validates content against schemas"""
    
    def __init__(self):
        self.schemas: Dict[str, ContentSchema] = {}
        self.logger = logging.getLogger('ContentValidator')
    
    def register_schema(self, content_type: str, schema: ContentSchema):
        """Register a validation schema for a content type"""
        self.schemas[content_type] = schema
    
    def validate_content(self, content_type: str, content_data: Dict[str, Any], 
                        content_id: str = "") -> List[str]:
        """
        Validate content data against registered schema
        
        Returns:
            List of validation error messages (empty if valid)
        """
        if content_type not in self.schemas:
            return [f"No schema registered for content type: {content_type}"]
        
        schema = self.schemas[content_type]
        errors = []
        
        # Check required fields
        for field in schema.required_fields:
            if field not in content_data:
                errors.append(f"Missing required field: {field}")
        
        # Check field types
        for field, expected_type in schema.field_types.items():
            if field in content_data:
                value = content_data[field]
                if not isinstance(value, expected_type):
                    errors.append(
                        f"Field {field} should be {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
        
        # Check field constraints
        for field, constraints in schema.field_constraints.items():
            if field in content_data:
                value = content_data[field]
                
                if 'min' in constraints and value < constraints['min']:
                    errors.append(f"Field {field} value {value} below minimum {constraints['min']}")
                
                if 'max' in constraints and value > constraints['max']:
                    errors.append(f"Field {field} value {value} above maximum {constraints['max']}")
                
                if 'choices' in constraints and value not in constraints['choices']:
                    errors.append(f"Field {field} value {value} not in allowed choices")
        
        # Run custom validators
        for validator in schema.custom_validators:
            try:
                validator_errors = validator(content_data, content_id)
                if validator_errors:
                    errors.extend(validator_errors)
            except Exception as e:
                errors.append(f"Custom validator error: {e}")
        
        return errors


class ContentRegistry:
    """Central registry for all game content"""
    
    def __init__(self, content_directory: str = "data/"):
        self.content_directory = Path(content_directory)
        self.entity_manager = get_entity_manager()
        self.event_system = get_event_system()
        self.validator = ContentValidator()
        
        # Content storage
        self.content: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.metadata: Dict[str, Dict[str, ContentMetadata]] = defaultdict(dict)
        
        # Content relationships
        self.inheritance_tree: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        # Caching and performance
        self.resolved_content_cache: Dict[str, Dict[str, Any]] = {}
        self.file_watchers: Dict[str, float] = {}  # file_path -> last_modified
        
        # Localization
        self.current_locale = "en"
        self.localization_data: Dict[str, Dict[str, str]] = defaultdict(dict)
        
        # Statistics
        self.load_stats = {
            'files_loaded': 0,
            'content_items': 0,
            'validation_errors': 0,
            'last_load_time': 0.0
        }
        
        self.logger = logging.getLogger('ContentRegistry')
        
        # Initialize default schemas
        self._register_default_schemas()
    
    def _register_default_schemas(self):
        """Register default validation schemas for content types"""
        
        # Crop schema
        crop_schema = ContentSchema(
            required_fields=['crop_type', 'category', 'growth_stages'],
            optional_fields=['display_name', 'description', 'base_yield', 'market_data'],
            field_types={
                'crop_type': str,
                'category': str,
                'base_yield': (int, float),
                'growth_stages': list
            },
            field_constraints={
                'base_yield': {'min': 0, 'max': 1000},
                'category': {'choices': ['grain_crop', 'vegetable', 'fruit', 'legume']}
            }
        )
        self.validator.register_schema('crops', crop_schema)
        
        # Equipment schema
        equipment_schema = ContentSchema(
            required_fields=['equipment_type', 'category'],
            optional_fields=['display_name', 'specifications', 'cost', 'capabilities'],
            field_types={
                'equipment_type': str,
                'category': str,
                'cost': (int, float),
                'capabilities': list
            },
            field_constraints={
                'cost': {'min': 0},
                'category': {'choices': ['hand_tool', 'tractor', 'implement', 'harvester', 'processing']}
            }
        )
        self.validator.register_schema('equipment', equipment_schema)
        
        # Employee schema
        employee_schema = ContentSchema(
            required_fields=['trait_type'],
            optional_fields=['display_name', 'description', 'modifiers', 'rarity'],
            field_types={
                'trait_type': str,
                'modifiers': dict,
                'rarity': str
            },
            field_constraints={
                'rarity': {'choices': ['common', 'uncommon', 'rare', 'legendary']}
            }
        )
        self.validator.register_schema('employees', employee_schema)
    
    async def load_all_content(self) -> bool:
        """Load all content from the content directory"""
        start_time = datetime.now()
        self.logger.info(f"Starting content load from {self.content_directory}")
        
        try:
            # Reset statistics
            self.load_stats = {
                'files_loaded': 0,
                'content_items': 0,
                'validation_errors': 0,
                'last_load_time': 0.0
            }
            
            # Load content by category
            content_categories = [
                'crops', 'equipment', 'employees', 'diseases', 
                'research', 'contracts', 'buildings', 'weather'
            ]
            
            for category in content_categories:
                await self._load_content_category(category)
            
            # Resolve inheritance after all content is loaded
            await self._resolve_inheritance()
            
            # Validate all content
            await self._validate_all_content()
            
            # Load localization data
            await self._load_localization()
            
            # Calculate final statistics
            end_time = datetime.now()
            self.load_stats['last_load_time'] = (end_time - start_time).total_seconds()
            
            # Emit content loaded event
            self.event_system.emit('content_loaded', {
                'categories_loaded': content_categories,
                'statistics': self.load_stats
            }, priority=EventPriority.HIGH)
            
            self.logger.info(
                f"Content loading complete: {self.load_stats['content_items']} items "
                f"from {self.load_stats['files_loaded']} files in "
                f"{self.load_stats['last_load_time']:.2f}s"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Content loading failed: {e}")
            return False
    
    async def _load_content_category(self, category: str):
        """Load all content files for a specific category"""
        category_path = self.content_directory / category
        
        if not category_path.exists():
            self.logger.warning(f"Content category directory not found: {category_path}")
            # Create directory structure for future use
            category_path.mkdir(parents=True, exist_ok=True)
            await self._create_example_content(category, category_path)
            return
        
        # Load all YAML and JSON files in category directory
        for file_path in category_path.rglob("*.yaml"):
            await self._load_content_file(category, file_path)
        
        for file_path in category_path.rglob("*.json"):
            await self._load_content_file(category, file_path)
    
    async def _load_content_file(self, category: str, file_path: Path):
        """Load content from a single file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.yaml':
                    content_data = yaml.safe_load(f)
                else:
                    content_data = json.load(f)
            
            if not content_data:
                self.logger.warning(f"Empty content file: {file_path}")
                return
            
            # Calculate file hash for change detection
            file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
            
            # Process content items (handle both single items and lists)
            if isinstance(content_data, list):
                # Multiple items in one file
                for item_data in content_data:
                    await self._process_content_item(category, item_data, file_path, file_hash)
            elif isinstance(content_data, dict):
                # Single item or multiple named items
                if 'content_id' in content_data or any(key.endswith('_type') for key in content_data):
                    # Single item
                    await self._process_content_item(category, content_data, file_path, file_hash)
                else:
                    # Multiple named items
                    for item_id, item_data in content_data.items():
                        if isinstance(item_data, dict):
                            item_data['content_id'] = item_id
                            await self._process_content_item(category, item_data, file_path, file_hash)
            
            self.load_stats['files_loaded'] += 1
            self.file_watchers[str(file_path)] = file_path.stat().st_mtime
            
        except Exception as e:
            self.logger.error(f"Failed to load content file {file_path}: {e}")
    
    async def _process_content_item(self, category: str, item_data: Dict[str, Any], 
                                  file_path: Path, file_hash: str):
        """Process a single content item"""
        # Determine content ID
        content_id = item_data.get('content_id')
        if not content_id:
            # Try to infer from file name or other fields
            content_id = file_path.stem
            if category == 'crops' and 'crop_type' in item_data:
                content_id = item_data['crop_type']
            elif category == 'equipment' and 'equipment_type' in item_data:
                content_id = item_data['equipment_type']
        
        if not content_id:
            self.logger.error(f"No content_id found for item in {file_path}")
            return
        
        # Create metadata
        metadata = ContentMetadata(
            content_id=content_id,
            content_type=category,
            file_path=str(file_path),
            file_hash=file_hash,
            version=item_data.get('version', '1.0')
        )
        
        # Track inheritance
        if 'inherits' in item_data:
            parent_id = item_data['inherits']
            metadata.inheritance_chain = [parent_id]
            self.inheritance_tree[category][content_id] = [parent_id]
        
        # Track dependencies
        dependencies = set()
        if 'dependencies' in item_data:
            dependencies.update(item_data['dependencies'])
        if 'required_research' in item_data:
            dependencies.update(item_data['required_research'])
        
        metadata.dependencies = list(dependencies)
        self.dependencies[f"{category}:{content_id}"] = dependencies
        
        # Store content and metadata
        self.content[category][content_id] = item_data.copy()
        self.metadata[category][content_id] = metadata
        self.load_stats['content_items'] += 1
        
        self.logger.debug(f"Loaded {category} content: {content_id}")
    
    async def _resolve_inheritance(self):
        """Resolve content inheritance by merging parent data with child data"""
        self.logger.info("Resolving content inheritance...")
        
        for category, items in self.content.items():
            for content_id, content_data in items.items():
                if 'inherits' in content_data:
                    resolved_data = await self._resolve_item_inheritance(category, content_id)
                    self.resolved_content_cache[f"{category}:{content_id}"] = resolved_data
    
    async def _resolve_item_inheritance(self, category: str, content_id: str, 
                                      visited: Optional[Set[str]] = None) -> Dict[str, Any]:
        """Resolve inheritance for a single content item"""
        if visited is None:
            visited = set()
        
        # Prevent circular inheritance
        full_id = f"{category}:{content_id}"
        if full_id in visited:
            self.logger.error(f"Circular inheritance detected: {full_id}")
            return self.content[category][content_id].copy()
        
        visited.add(full_id)
        
        content_data = self.content[category][content_id].copy()
        
        # If no inheritance, return as-is
        if 'inherits' not in content_data:
            return content_data
        
        parent_id = content_data['inherits']
        
        # Check if parent exists
        if parent_id not in self.content[category]:
            self.logger.error(f"Parent content not found: {parent_id} for {content_id}")
            return content_data
        
        # Recursively resolve parent inheritance
        parent_data = await self._resolve_item_inheritance(category, parent_id, visited)
        
        # Merge parent data with child data (child overrides parent)
        resolved_data = parent_data.copy()
        resolved_data.update(content_data)
        
        # Remove inheritance marker from resolved data
        resolved_data.pop('inherits', None)
        
        # Update inheritance chain metadata
        metadata = self.metadata[category][content_id]
        if parent_id in self.metadata[category]:
            parent_metadata = self.metadata[category][parent_id]
            metadata.inheritance_chain = parent_metadata.inheritance_chain + [parent_id]
        
        return resolved_data
    
    async def _validate_all_content(self):
        """Validate all loaded content against schemas"""
        self.logger.info("Validating all content...")
        
        total_errors = 0
        
        for category, items in self.content.items():
            for content_id, content_data in items.items():
                # Get resolved content for validation
                resolved_data = self.get_resolved_content(category, content_id)
                
                # Validate against schema
                errors = self.validator.validate_content(category, resolved_data, content_id)
                
                if errors:
                    total_errors += len(errors)
                    metadata = self.metadata[category][content_id]
                    metadata.validation_errors = errors
                    
                    self.logger.warning(f"Validation errors for {category}:{content_id}: {errors}")
        
        self.load_stats['validation_errors'] = total_errors
        
        if total_errors > 0:
            self.logger.warning(f"Content validation completed with {total_errors} errors")
        else:
            self.logger.info("All content validated successfully")
    
    async def _load_localization(self):
        """Load localization data"""
        localization_path = self.content_directory / "localization"
        
        if not localization_path.exists():
            return
        
        for locale_file in localization_path.glob("*.json"):
            locale = locale_file.stem
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self.localization_data[locale] = json.load(f)
                self.logger.debug(f"Loaded localization for locale: {locale}")
            except Exception as e:
                self.logger.error(f"Failed to load localization {locale_file}: {e}")
    
    async def _create_example_content(self, category: str, category_path: Path):
        """Create example content files for empty categories"""
        examples = {
            'crops': {
                'corn': {
                    'content_id': 'corn',
                    'crop_type': 'corn',
                    'category': 'grain_crop',
                    'display_name': 'Corn',
                    'description': 'A staple grain crop with good yield potential',
                    'growth_stages': ['seed', 'sprout', 'vegetative', 'flowering', 'mature'],
                    'base_yield': 15.0,
                    'growth_time_days': 4,
                    'market_data': {
                        'base_price_range': [3.0, 7.0],
                        'price_volatility': 0.15
                    }
                }
            },
            'equipment': {
                'hoe': {
                    'content_id': 'hoe',
                    'equipment_type': 'hoe',
                    'category': 'hand_tool',
                    'display_name': 'Garden Hoe',
                    'description': 'Basic hand tool for tilling soil',
                    'cost': 25.0,
                    'capabilities': ['tilling'],
                    'modifiers': {
                        'tilling_speed': 1.4,
                        'energy_efficiency': 0.5
                    }
                }
            }
        }
        
        if category in examples:
            example_file = category_path / f"example_{category}.yaml"
            with open(example_file, 'w') as f:
                yaml.dump(examples[category], f, default_flow_style=False)
            
            self.logger.info(f"Created example content file: {example_file}")
    
    def get_content(self, category: str, content_id: str) -> Optional[Dict[str, Any]]:
        """Get raw content data (before inheritance resolution)"""
        return self.content[category].get(content_id)
    
    def get_resolved_content(self, category: str, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content data with inheritance resolved"""
        cache_key = f"{category}:{content_id}"
        
        # Check cache first
        if cache_key in self.resolved_content_cache:
            return self.resolved_content_cache[cache_key].copy()
        
        # If not cached, resolve on demand
        if content_id in self.content[category]:
            try:
                resolved_data = asyncio.run(self._resolve_item_inheritance(category, content_id))
                self.resolved_content_cache[cache_key] = resolved_data
                return resolved_data.copy()
            except Exception as e:
                self.logger.error(f"Failed to resolve inheritance for {cache_key}: {e}")
                return self.content[category][content_id].copy()
        
        return None
    
    def get_crop(self, crop_id: str) -> Optional[Dict[str, Any]]:
        """Convenience method to get crop data"""
        return self.get_resolved_content('crops', crop_id)
    
    def get_equipment(self, equipment_id: str) -> Optional[Dict[str, Any]]:
        """Convenience method to get equipment data"""
        return self.get_resolved_content('equipment', equipment_id)
    
    def get_employee_trait(self, trait_id: str) -> Optional[Dict[str, Any]]:
        """Convenience method to get employee trait data"""
        return self.get_resolved_content('employees', trait_id)
    
    def list_content(self, category: str) -> List[str]:
        """Get list of all content IDs in a category"""
        return list(self.content[category].keys())
    
    def search_content(self, category: str, **filters) -> List[str]:
        """Search for content matching filters"""
        results = []
        
        for content_id in self.content[category]:
            content_data = self.get_resolved_content(category, content_id)
            if not content_data:
                continue
            
            match = True
            for field, value in filters.items():
                if field not in content_data or content_data[field] != value:
                    match = False
                    break
            
            if match:
                results.append(content_id)
        
        return results
    
    def create_entity_from_content(self, content_category: str, content_id: str, 
                                 **additional_components) -> Optional[str]:
        """Create an entity from content definition"""
        content_data = self.get_resolved_content(content_category, content_id)
        if not content_data:
            self.logger.error(f"Content not found: {content_category}:{content_id}")
            return None
        
        # Build entity components from content data
        entity_components = {}
        
        # Add identity component
        entity_components['identity'] = {
            'name': content_id,
            'display_name': content_data.get('display_name', content_id),
            'description': content_data.get('description', ''),
            'tags': set(content_data.get('tags', []))
        }
        
        # Add category-specific components
        if content_category == 'crops':
            entity_components['crop'] = {
                'crop_type': content_data['crop_type'],
                'variety': content_data.get('variety', 'standard'),
                'growth_stage': 'seed',
                'base_yield': content_data.get('base_yield', 10.0),
                'days_to_maturity': content_data.get('growth_time_days', 4)
            }
        
        elif content_category == 'equipment':
            entity_components['equipment'] = {
                'equipment_type': content_data['equipment_type'],
                'specifications': content_data.get('specifications', {}),
                'capabilities': content_data.get('capabilities', []),
                'purchase_price': content_data.get('cost', 0.0),
                'current_value': content_data.get('cost', 0.0)
            }
        
        # Add any additional components
        entity_components.update(additional_components)
        
        # Create entity
        entity_id = self.entity_manager.create_entity(entity_components)
        
        # Emit entity creation from content event
        self.event_system.emit('entity_created_from_content', {
            'entity_id': entity_id,
            'content_category': content_category,
            'content_id': content_id
        }, priority=EventPriority.NORMAL)
        
        return entity_id
    
    def get_localized_string(self, key: str, locale: Optional[str] = None) -> str:
        """Get localized string for current or specified locale"""
        if locale is None:
            locale = self.current_locale
        
        if locale in self.localization_data:
            return self.localization_data[locale].get(key, key)
        
        return key
    
    def set_locale(self, locale: str):
        """Set current localization locale"""
        self.current_locale = locale
        self.event_system.emit('locale_changed', {'locale': locale}, priority=EventPriority.NORMAL)
    
    async def reload_content_type(self, category: str) -> bool:
        """Hot-reload content for a specific category"""
        self.logger.info(f"Hot-reloading content category: {category}")
        
        try:
            # Clear existing content for category
            self.content[category].clear()
            self.metadata[category].clear()
            
            # Remove from cache
            cache_keys_to_remove = [
                key for key in self.resolved_content_cache.keys() 
                if key.startswith(f"{category}:")
            ]
            for key in cache_keys_to_remove:
                del self.resolved_content_cache[key]
            
            # Reload category
            await self._load_content_category(category)
            await self._resolve_inheritance()
            
            # Emit reload event
            self.event_system.emit('content_reloaded', {
                'category': category,
                'item_count': len(self.content[category])
            }, priority=EventPriority.HIGH)
            
            self.logger.info(f"Successfully reloaded {category} content")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reload {category} content: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive content registry statistics"""
        category_counts = {
            category: len(items) for category, items in self.content.items()
        }
        
        total_validation_errors = sum(
            len(metadata.validation_errors)
            for category_metadata in self.metadata.values()
            for metadata in category_metadata.values()
        )
        
        return {
            'content_directory': str(self.content_directory),
            'category_counts': category_counts,
            'total_content_items': sum(category_counts.values()),
            'cached_resolved_items': len(self.resolved_content_cache),
            'validation_errors': total_validation_errors,
            'load_statistics': self.load_stats,
            'current_locale': self.current_locale,
            'available_locales': list(self.localization_data.keys())
        }
    
    def export_content_report(self, output_path: str):
        """Export comprehensive content report to JSON"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'content_summary': {},
            'validation_errors': {},
            'inheritance_tree': dict(self.inheritance_tree)
        }
        
        # Generate content summary
        for category, items in self.content.items():
            report['content_summary'][category] = {}
            for content_id, content_data in items.items():
                metadata = self.metadata[category][content_id]
                report['content_summary'][category][content_id] = {
                    'version': metadata.version,
                    'file_path': metadata.file_path,
                    'has_inheritance': 'inherits' in content_data,
                    'dependency_count': len(metadata.dependencies)
                }
                
                if metadata.validation_errors:
                    if category not in report['validation_errors']:
                        report['validation_errors'][category] = {}
                    report['validation_errors'][category][content_id] = metadata.validation_errors
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Content report exported to {output_path}")


# Global content registry instance
_global_content_registry: Optional[ContentRegistry] = None

def get_content_registry() -> ContentRegistry:
    """Get the global content registry instance"""
    global _global_content_registry
    if _global_content_registry is None:
        _global_content_registry = ContentRegistry()
    return _global_content_registry

def initialize_content_registry(content_directory: str = "data/") -> ContentRegistry:
    """Initialize the global content registry"""
    global _global_content_registry
    _global_content_registry = ContentRegistry(content_directory)
    return _global_content_registry