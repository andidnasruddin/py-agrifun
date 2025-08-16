"""
Entity-Component-System (ECS) Architecture for AgriFun Comprehensive Engine

This module implements a high-performance ECS architecture that forms the foundation
for all game objects in the comprehensive AgriFun simulation. The ECS pattern provides
maximum flexibility and performance for complex agricultural simulation with 15+ subsystems.

Key Benefits:
- Data-driven entity creation from JSON/YAML definitions
- Dynamic component composition without inheritance hierarchies
- Cache-friendly component storage for optimal performance
- Automatic serialization/deserialization for save/load
- Hot-swappable components for runtime modifications
- Query system for efficient entity retrieval
- Component dependencies and validation

Core Concepts:
- Entity: Unique ID representing a game object (employee, crop, equipment, etc.)
- Component: Pure data structure (Position, Health, Equipment, etc.)
- System: Logic that processes entities with specific component combinations

Supported Component Types:
- Transform: Position, rotation, scale in 2D space
- Renderable: Visual representation data
- Employee: Stats, needs, skills, specializations
- Crop: Growth stage, health, yield potential
- Equipment: Specifications, condition, capabilities
- Economic: Cost, value, depreciation data
- AI: Behavior state, goals, pathfinding
- Task: Work assignments, progress tracking

Example Usage:
    # Create entity manager
    entity_manager = EntityManager()
    
    # Create employee entity from data
    employee_data = {
        'transform': {'x': 5.0, 'y': 3.0},
        'employee': {'name': 'John', 'energy': 100},
        'ai': {'state': 'idle', 'goals': []}
    }
    
    employee_id = entity_manager.create_entity(employee_data)
    
    # Query entities with specific components
    workers = entity_manager.query(['transform', 'employee', 'ai'])
    
    # Update component data
    entity_manager.update_component(employee_id, 'employee', {'energy': 95})

Performance Features:
- Component pooling for memory efficiency
- Sparse component storage for cache optimization
- Batch operations for system processing
- Component change tracking for selective updates
- Archetype-based storage for query optimization
"""

import json
import time
import uuid
from typing import Dict, List, Set, Any, Optional, Type, TypeVar, Generic, Union
from dataclasses import dataclass, field, asdict, is_dataclass
from collections import defaultdict
from abc import ABC, abstractmethod
from enum import Enum

# Import the enhanced event system
from .event_system import get_global_event_system, EventPriority


# Type definitions for generic programming
T = TypeVar('T')
ComponentType = TypeVar('ComponentType')


class ComponentCategory(Enum):
    """Categories for component organization and validation"""
    CORE = "core"           # Essential components (Transform, Identity)
    PHYSICAL = "physical"   # Physical properties (Collision, Physics)
    VISUAL = "visual"       # Rendering and display (Sprite, Animation)
    GAMEPLAY = "gameplay"   # Game-specific logic (Employee, Crop, Equipment)
    AI = "ai"              # Artificial intelligence (Behavior, Pathfinding)
    ECONOMIC = "economic"   # Financial and economic data
    TEMPORAL = "temporal"   # Time-based components (Growth, Decay)


@dataclass
class Component:
    """Base class for all ECS components"""
    component_type: str = field(init=False, default="")
    category: ComponentCategory = ComponentCategory.CORE
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)
    version: int = 1
    
    def __post_init__(self):
        """Set component type from class name"""
        if not self.component_type:
            self.component_type = self.__class__.__name__.lower().replace('component', '')
    
    def mark_modified(self):
        """Mark component as modified"""
        self.modified_at = time.time()
        self.version += 1


# Core Components for all entities
@dataclass
class IdentityComponent(Component):
    """Core identity information for entities"""
    name: str = ""
    display_name: str = ""
    description: str = ""
    tags: Set[str] = field(default_factory=set)
    category: ComponentCategory = ComponentCategory.CORE


@dataclass
class TransformComponent(Component):
    """2D position, rotation, and scale"""
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0  # Degrees
    scale_x: float = 1.0
    scale_y: float = 1.0
    parent_entity: Optional[str] = None  # For hierarchical transforms
    category: ComponentCategory = ComponentCategory.PHYSICAL


@dataclass 
class RenderableComponent(Component):
    """Visual representation data"""
    sprite_path: str = ""
    color: tuple = (255, 255, 255, 255)  # RGBA
    layer: int = 0  # Rendering layer
    visible: bool = True
    animation_state: str = "idle"
    flip_x: bool = False
    flip_y: bool = False
    category: ComponentCategory = ComponentCategory.VISUAL


# Agricultural Components
@dataclass
class EmployeeComponent(Component):
    """Employee-specific data"""
    # Basic employee information
    first_name: str = ""
    last_name: str = ""
    age: int = 25
    hire_date: float = field(default_factory=time.time)
    daily_wage: float = 80.0
    
    # Employee stats (0-100 scale)
    energy: float = 100.0
    hunger: float = 100.0
    thirst: float = 100.0
    bladder: float = 100.0
    social: float = 100.0
    happiness: float = 100.0
    
    # Skills and capabilities
    skills: Dict[str, float] = field(default_factory=dict)  # Skill name -> level (0-100)
    traits: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    specialization: str = "general_worker"
    
    # Work tracking
    hours_worked_today: float = 0.0
    total_hours_worked: float = 0.0
    tasks_completed: int = 0
    performance_rating: float = 100.0
    
    category: ComponentCategory = ComponentCategory.GAMEPLAY


@dataclass
class CropComponent(Component):
    """Crop growth and health data"""
    # Crop identification
    crop_type: str = "corn"
    variety: str = "standard"
    planted_date: float = field(default_factory=time.time)
    
    # Growth tracking
    growth_stage: str = "seed"
    growth_progress: float = 0.0  # 0.0 to 1.0 within current stage
    days_to_maturity: int = 4
    
    # Health and condition
    health: float = 100.0
    water_level: float = 50.0
    nutrient_absorption: Dict[str, float] = field(default_factory=lambda: {"N": 0, "P": 0, "K": 0})
    disease_resistance: Dict[str, float] = field(default_factory=dict)
    pest_damage: float = 0.0
    
    # Yield potential
    base_yield: float = 15.0
    quality_factors: Dict[str, float] = field(default_factory=dict)
    expected_yield: float = 15.0
    expected_quality: float = 1.0
    
    category: ComponentCategory = ComponentCategory.GAMEPLAY


@dataclass
class EquipmentComponent(Component):
    """Equipment and machinery data"""
    # Equipment identification
    equipment_type: str = "hand_tool"
    model: str = ""
    manufacturer: str = ""
    
    # Technical specifications
    specifications: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    
    # Condition and maintenance
    condition: float = 100.0  # 0-100, affects performance
    maintenance_hours: float = 0.0
    next_maintenance_due: float = 100.0
    breakdown_probability: float = 0.001
    
    # Economics
    purchase_price: float = 0.0
    current_value: float = 0.0
    operational_cost_per_hour: float = 0.0
    
    # Usage tracking
    hours_used: float = 0.0
    tasks_completed: int = 0
    
    category: ComponentCategory = ComponentCategory.GAMEPLAY


@dataclass
class AIComponent(Component):
    """AI behavior state and goals"""
    # Current state
    current_state: str = "idle"
    previous_state: str = "idle"
    state_changed_at: float = field(default_factory=time.time)
    
    # Goals and planning
    current_goal: Optional[Dict[str, Any]] = None
    goal_queue: List[Dict[str, Any]] = field(default_factory=list)
    
    # Pathfinding
    current_path: List[tuple] = field(default_factory=list)
    path_target: Optional[tuple] = None
    movement_speed: float = 1.0
    
    # Behavior parameters
    decision_cooldown: float = 0.0
    last_decision_time: float = 0.0
    personality_traits: Dict[str, float] = field(default_factory=dict)
    
    category: ComponentCategory = ComponentCategory.AI


@dataclass
class TaskComponent(Component):
    """Task assignment and progress tracking"""
    # Task identification
    task_type: str = ""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    work_order_id: Optional[str] = None
    
    # Task details
    assigned_plots: List[tuple] = field(default_factory=list)
    required_skills: Dict[str, float] = field(default_factory=dict)
    required_equipment: List[str] = field(default_factory=list)
    
    # Progress tracking
    progress: float = 0.0  # 0.0 to 1.0
    started_at: Optional[float] = None
    estimated_completion: Optional[float] = None
    
    # Task metadata
    priority: int = 1  # 1-5 scale
    deadline: Optional[float] = None
    assigned_employee: Optional[str] = None
    
    category: ComponentCategory = ComponentCategory.GAMEPLAY


@dataclass
class EconomicComponent(Component):
    """Economic and financial data"""
    # Value tracking
    base_value: float = 0.0
    current_market_value: float = 0.0
    depreciation_rate: float = 0.0
    
    # Cost tracking
    acquisition_cost: float = 0.0
    maintenance_costs: float = 0.0
    operational_costs: float = 0.0
    
    # Revenue potential
    revenue_potential: float = 0.0
    profit_margin: float = 0.0
    
    # Market data
    market_demand: float = 1.0
    price_volatility: float = 0.1
    seasonal_modifiers: Dict[str, float] = field(default_factory=dict)
    
    category: ComponentCategory = ComponentCategory.ECONOMIC


class ComponentRegistry:
    """Registry for all component types and their schemas"""
    
    def __init__(self):
        self._component_types: Dict[str, Type[Component]] = {}
        self._component_schemas: Dict[str, Dict] = {}
        self._component_dependencies: Dict[str, List[str]] = {}
        
        # Register core components
        self.register_component(IdentityComponent)
        self.register_component(TransformComponent)
        self.register_component(RenderableComponent)
        self.register_component(EmployeeComponent)
        self.register_component(CropComponent)
        self.register_component(EquipmentComponent)
        self.register_component(AIComponent)
        self.register_component(TaskComponent)
        self.register_component(EconomicComponent)
    
    def register_component(self, component_class: Type[Component], 
                          dependencies: Optional[List[str]] = None):
        """Register a component type"""
        component_name = component_class.__name__.lower().replace('component', '')
        self._component_types[component_name] = component_class
        
        if dependencies:
            self._component_dependencies[component_name] = dependencies
        
        # Generate schema from dataclass fields (simplified)
        if is_dataclass(component_class):
            self._component_schemas[component_name] = {
                'fields': [field.name for field in component_class.__dataclass_fields__.values()],
                'required': []  # Can be extended with validation logic
            }
    
    def get_component_type(self, component_name: str) -> Optional[Type[Component]]:
        """Get component type by name"""
        return self._component_types.get(component_name)
    
    def get_component_schema(self, component_name: str) -> Optional[Dict]:
        """Get component schema by name"""
        return self._component_schemas.get(component_name)
    
    def get_all_component_types(self) -> List[str]:
        """Get list of all registered component types"""
        return list(self._component_types.keys())
    
    def validate_dependencies(self, entity_components: Set[str]) -> List[str]:
        """Validate component dependencies for an entity"""
        missing_dependencies = []
        
        for component in entity_components:
            if component in self._component_dependencies:
                for dependency in self._component_dependencies[component]:
                    if dependency not in entity_components:
                        missing_dependencies.append(
                            f"{component} requires {dependency}"
                        )
        
        return missing_dependencies


class EntityArchetype:
    """Archetype representing entities with same component composition"""
    
    def __init__(self, components: Set[str]):
        self.components = frozenset(components)
        self.entities: Set[str] = set()
        self.component_data: Dict[str, Dict[str, Component]] = defaultdict(dict)
    
    def add_entity(self, entity_id: str):
        """Add entity to this archetype"""
        self.entities.add(entity_id)
    
    def remove_entity(self, entity_id: str):
        """Remove entity from this archetype"""
        self.entities.discard(entity_id)
        # Clean up component data
        for component_type in self.components:
            self.component_data[component_type].pop(entity_id, None)
    
    def matches_query(self, required_components: Set[str]) -> bool:
        """Check if this archetype matches a component query"""
        return required_components.issubset(self.components)


class EntityManager:
    """Central manager for all entities and components"""
    
    def __init__(self):
        self.component_registry = ComponentRegistry()
        self.event_system = get_global_event_system()
        
        # Entity management
        self._entities: Set[str] = set()
        self._entity_components: Dict[str, Set[str]] = defaultdict(set)
        
        # Component storage organized by archetype
        self._archetypes: Dict[frozenset, EntityArchetype] = {}
        self._entity_archetype_map: Dict[str, EntityArchetype] = {}
        
        # Component data storage
        self._components: Dict[str, Dict[str, Component]] = defaultdict(dict)
        
        # Change tracking for optimization
        self._modified_entities: Set[str] = set()
        self._modified_components: Dict[str, Set[str]] = defaultdict(set)
        
        # Performance metrics
        self._entity_count = 0
        self._component_count = 0
        
    def create_entity(self, entity_data: Optional[Dict[str, Any]] = None,
                     entity_id: Optional[str] = None) -> str:
        """
        Create a new entity with optional components from data
        
        Args:
            entity_data: Dictionary mapping component names to component data
            entity_id: Optional specific entity ID (generated if not provided)
            
        Returns:
            Entity ID string
        """
        if entity_id is None:
            entity_id = str(uuid.uuid4())
        
        if entity_id in self._entities:
            raise ValueError(f"Entity {entity_id} already exists")
        
        # Create entity
        self._entities.add(entity_id)
        self._entity_count += 1
        
        # Add components from data
        if entity_data:
            for component_name, component_data in entity_data.items():
                self.add_component(entity_id, component_name, component_data)
        
        # Emit entity creation event
        self.event_system.publish('entity_created', {
            'entity_id': entity_id,
            'components': list(self._entity_components[entity_id])
        }, EventPriority.NORMAL, 'ecs')
        
        return entity_id
    
    def destroy_entity(self, entity_id: str):
        """Destroy an entity and all its components"""
        if entity_id not in self._entities:
            return
        
        # Remove from archetype
        if entity_id in self._entity_archetype_map:
            archetype = self._entity_archetype_map[entity_id]
            archetype.remove_entity(entity_id)
            del self._entity_archetype_map[entity_id]
        
        # Remove all components
        for component_type in list(self._entity_components[entity_id]):
            self.remove_component(entity_id, component_type)
        
        # Remove entity
        self._entities.remove(entity_id)
        del self._entity_components[entity_id]
        self._entity_count -= 1
        
        # Emit entity destruction event
        self.event_system.publish('entity_destroyed', {
            'entity_id': entity_id
        }, EventPriority.NORMAL, 'ecs')
    
    def add_component(self, entity_id: str, component_name: str, 
                     component_data: Union[Dict[str, Any], Component]):
        """Add a component to an entity"""
        if entity_id not in self._entities:
            raise ValueError(f"Entity {entity_id} does not exist")
        
        # Get component type
        component_type = self.component_registry.get_component_type(component_name)
        if component_type is None:
            raise ValueError(f"Unknown component type: {component_name}")
        
        # Create component instance
        if isinstance(component_data, Component):
            component = component_data
        elif isinstance(component_data, dict):
            try:
                component = component_type(**component_data)
            except TypeError as e:
                raise ValueError(f"Invalid component data for {component_name}: {e}")
        else:
            raise ValueError(f"Component data must be dict or Component instance")
        
        # Update archetype
        old_components = self._entity_components[entity_id].copy()
        new_components = old_components | {component_name}
        
        self._update_entity_archetype(entity_id, old_components, new_components)
        
        # Store component
        self._entity_components[entity_id].add(component_name)
        self._components[component_name][entity_id] = component
        self._component_count += 1
        
        # Track changes
        self._modified_entities.add(entity_id)
        self._modified_components[component_name].add(entity_id)
        
        # Emit component addition event
        self.event_system.publish('component_added', {
            'entity_id': entity_id,
            'component_type': component_name,
            'component_data': asdict(component) if is_dataclass(component) else {}
        }, EventPriority.NORMAL, 'ecs')
    
    def remove_component(self, entity_id: str, component_name: str):
        """Remove a component from an entity"""
        if entity_id not in self._entities:
            return
        
        if component_name not in self._entity_components[entity_id]:
            return
        
        # Update archetype
        old_components = self._entity_components[entity_id].copy()
        new_components = old_components - {component_name}
        
        self._update_entity_archetype(entity_id, old_components, new_components)
        
        # Remove component
        self._entity_components[entity_id].remove(component_name)
        del self._components[component_name][entity_id]
        self._component_count -= 1
        
        # Track changes
        self._modified_entities.add(entity_id)
        
        # Emit component removal event
        self.event_system.publish('component_removed', {
            'entity_id': entity_id,
            'component_type': component_name
        }, EventPriority.NORMAL, 'ecs')
    
    def get_component(self, entity_id: str, component_name: str) -> Optional[Component]:
        """Get a component from an entity"""
        if entity_id not in self._entities:
            return None
        
        return self._components[component_name].get(entity_id)
    
    def update_component(self, entity_id: str, component_name: str, 
                        update_data: Dict[str, Any]):
        """Update component data"""
        component = self.get_component(entity_id, component_name)
        if component is None:
            return
        
        # Update component fields
        for field_name, value in update_data.items():
            if hasattr(component, field_name):
                setattr(component, field_name, value)
        
        # Mark as modified
        component.mark_modified()
        self._modified_entities.add(entity_id)
        self._modified_components[component_name].add(entity_id)
        
        # Emit component update event
        self.event_system.publish('component_updated', {
            'entity_id': entity_id,
            'component_type': component_name,
            'updated_fields': list(update_data.keys())
        }, EventPriority.NORMAL, 'ecs')
    
    def query(self, required_components: List[str]) -> List[str]:
        """Query entities that have all required components"""
        required_set = set(required_components)
        matching_entities = []
        
        # Use archetype system for efficient querying
        for archetype in self._archetypes.values():
            if archetype.matches_query(required_set):
                matching_entities.extend(archetype.entities)
        
        return matching_entities
    
    def get_entities_with_component(self, component_name: str) -> List[str]:
        """Get all entities that have a specific component"""
        return list(self._components[component_name].keys())
    
    def has_component(self, entity_id: str, component_name: str) -> bool:
        """Check if an entity has a specific component"""
        return component_name in self._entity_components.get(entity_id, set())
    
    def get_entity_components(self, entity_id: str) -> Set[str]:
        """Get all component types for an entity"""
        return self._entity_components.get(entity_id, set()).copy()
    
    def _update_entity_archetype(self, entity_id: str, old_components: Set[str], 
                                new_components: Set[str]):
        """Update entity's archetype when components change"""
        # Remove from old archetype
        if entity_id in self._entity_archetype_map:
            old_archetype = self._entity_archetype_map[entity_id]
            old_archetype.remove_entity(entity_id)
            del self._entity_archetype_map[entity_id]
        
        # Add to new archetype
        if new_components:
            archetype_key = frozenset(new_components)
            
            if archetype_key not in self._archetypes:
                self._archetypes[archetype_key] = EntityArchetype(new_components)
            
            archetype = self._archetypes[archetype_key]
            archetype.add_entity(entity_id)
            self._entity_archetype_map[entity_id] = archetype
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get entity manager statistics"""
        component_counts = {
            comp_type: len(entities) 
            for comp_type, entities in self._components.items()
        }
        
        return {
            'total_entities': self._entity_count,
            'total_components': self._component_count,
            'archetype_count': len(self._archetypes),
            'component_counts': component_counts,
            'modified_entities': len(self._modified_entities),
            'registered_component_types': len(self.component_registry.get_all_component_types())
        }
    
    def serialize_entity(self, entity_id: str) -> Dict[str, Any]:
        """Serialize an entity to dictionary for saving"""
        if entity_id not in self._entities:
            return {}
        
        entity_data = {
            'entity_id': entity_id,
            'components': {}
        }
        
        for component_name in self._entity_components[entity_id]:
            component = self._components[component_name][entity_id]
            if is_dataclass(component):
                entity_data['components'][component_name] = asdict(component)
        
        return entity_data
    
    def deserialize_entity(self, entity_data: Dict[str, Any]) -> str:
        """Deserialize an entity from dictionary"""
        entity_id = entity_data.get('entity_id', str(uuid.uuid4()))
        components_data = entity_data.get('components', {})
        
        return self.create_entity(components_data, entity_id)
    
    def clear_modified_flags(self):
        """Clear all modification tracking flags"""
        self._modified_entities.clear()
        self._modified_components.clear()
    
    def shutdown(self):
        """Clean shutdown of entity manager"""
        # Emit shutdown event
        self.event_system.publish('entity_manager_shutdown', {
            'final_entity_count': self._entity_count,
            'final_component_count': self._component_count
        }, EventPriority.CRITICAL, 'ecs')
        
        # Clear all data
        self._entities.clear()
        self._entity_components.clear()
        self._archetypes.clear()
        self._entity_archetype_map.clear()
        self._components.clear()
        self._modified_entities.clear()
        self._modified_components.clear()


# Global entity manager instance
_global_entity_manager: Optional[EntityManager] = None

def get_entity_manager() -> EntityManager:
    """Get the global entity manager instance"""
    global _global_entity_manager
    if _global_entity_manager is None:
        _global_entity_manager = EntityManager()
    return _global_entity_manager

def initialize_entity_manager() -> EntityManager:
    """Initialize the global entity manager"""
    global _global_entity_manager
    _global_entity_manager = EntityManager()
    return _global_entity_manager

def get_entity_system() -> EntityManager:
    """Alias for get_entity_manager for backward compatibility"""
    return get_entity_manager()

class Entity:
    """
    Entity representation in the ECS system
    
    In modern ECS, entities are typically just unique IDs, but this class
    provides a convenient wrapper for systems that expect entity objects.
    """
    
    def __init__(self, entity_id: str, entity_manager: 'EntityManager'):
        """Initialize entity wrapper"""
        self.id = entity_id
        self.entity_manager = entity_manager
    
    def get_component(self, component_type: str) -> Optional[Component]:
        """Get a component from this entity"""
        return self.entity_manager.get_component(self.id, component_type)
    
    def set_component(self, component_type: str, component_data: Dict[str, Any]) -> bool:
        """Set component data on this entity"""
        return self.entity_manager.update_component(self.id, component_type, component_data)
    
    def add_component(self, component_type: str, component_data: Dict[str, Any]) -> bool:
        """Add a component to this entity"""
        return self.entity_manager.add_component(self.id, component_type, component_data)
    
    def remove_component(self, component_type: str) -> bool:
        """Remove a component from this entity"""
        return self.entity_manager.remove_component(self.id, component_type)
    
    def has_component(self, component_type: str) -> bool:
        """Check if entity has a specific component"""
        return self.entity_manager.has_component(self.id, component_type)
    
    def get_all_components(self) -> Dict[str, Component]:
        """Get all components attached to this entity"""
        return self.entity_manager.get_all_components(self.id)
    
    def destroy(self) -> bool:
        """Destroy this entity and all its components"""
        return self.entity_manager.destroy_entity(self.id)
    
    def __str__(self) -> str:
        """String representation of entity"""
        return f"Entity({self.id})"
    
    def __repr__(self) -> str:
        """Debug representation of entity"""
        components = list(self.get_all_components().keys())
        return f"Entity(id={self.id}, components={components})"

class System:
    """
    Base class for all ECS systems
    
    Systems contain the logic that processes entities with specific component combinations.
    They operate on the data stored in components but don't store state themselves.
    """
    
    def __init__(self):
        """Initialize the system"""
        self.system_name = "base_system"
        self.entity_manager = get_entity_manager()
        self.active = True
        self.update_frequency = 1.0  # Updates per second
        self.last_update_time = 0.0
    
    def initialize(self) -> bool:
        """
        Initialize the system with required dependencies
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        return True
    
    def update(self, delta_time: float):
        """
        Update the system logic
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        pass
    
    def shutdown(self):
        """Clean shutdown of the system"""
        self.active = False
    
    def get_entities_with_components(self, component_types: List[str]) -> List[str]:
        """
        Get all entities that have the specified components
        
        Args:
            component_types: List of component type names
            
        Returns:
            List of entity IDs that have all specified components
        """
        return self.entity_manager.query(component_types)
    
    def get_component(self, entity_id: str, component_type: str) -> Optional[Component]:
        """
        Get a component from an entity
        
        Args:
            entity_id: The entity to get the component from
            component_type: The type of component to retrieve
            
        Returns:
            The component instance or None if not found
        """
        return self.entity_manager.get_component(entity_id, component_type)
    
    def set_component(self, entity_id: str, component_type: str, component_data: Dict[str, Any]) -> bool:
        """
        Set component data on an entity
        
        Args:
            entity_id: The entity to set the component on
            component_type: The type of component to set
            component_data: The component data to set
            
        Returns:
            True if successful, False otherwise
        """
        return self.entity_manager.update_component(entity_id, component_type, component_data)
    
    def remove_component(self, entity_id: str, component_type: str) -> bool:
        """
        Remove a component from an entity
        
        Args:
            entity_id: The entity to remove the component from
            component_type: The type of component to remove
            
        Returns:
            True if successful, False otherwise
        """
        return self.entity_manager.remove_component(entity_id, component_type)
    
    def create_entity(self, entity_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new entity with optional initial components
        
        Args:
            entity_data: Optional dictionary of component data
            
        Returns:
            The ID of the created entity
        """
        return self.entity_manager.create_entity(entity_data)
    
    def destroy_entity(self, entity_id: str) -> bool:
        """
        Destroy an entity and all its components
        
        Args:
            entity_id: The entity to destroy
            
        Returns:
            True if successful, False otherwise
        """
        return self.entity_manager.destroy_entity(entity_id)