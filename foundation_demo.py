#!/usr/bin/env python3
"""
AgriFun Foundation Architecture Demo
====================================

This demo showcases the new comprehensive agricultural simulation architecture
with Event System, Entity-Component System, and Content Registry integration.

Demo Scenarios:
1. Event-driven communication between systems
2. Entity creation and component management
3. Data-driven content loading and hot-reload
4. Cross-system integration example

Run with: python foundation_demo.py
"""

import time
import json
import random
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# FOUNDATION ARCHITECTURE DEMO IMPLEMENTATION
# ============================================================================

class EventPriority(Enum):
    """Event priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class EventSystem:
    """Simplified Event System for demo purposes"""
    
    def __init__(self):
        self.subscribers = {}
        self.event_history = []
        self.events_processed = 0
        
    def subscribe(self, event_type: str, callback):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        print(f"[SUBSCRIBE] Subscribed to '{event_type}' events")
    
    def publish(self, event_type: str, event_data: Dict[str, Any], priority: EventPriority = EventPriority.NORMAL):
        """Publish an event to all subscribers"""
        event = {
            'type': event_type,
            'data': event_data,
            'priority': priority.value,
            'timestamp': datetime.now(),
            'event_id': f"evt_{self.events_processed:06d}"
        }
        
        # Store in history
        self.event_history.append(event)
        self.events_processed += 1
        
        # Notify subscribers
        if event_type in self.subscribers:
            print(f"🚀 Publishing {priority.value.upper()} event: {event_type}")
            for callback in self.subscribers[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    print(f"❌ Error in event handler: {e}")
        
        return event['event_id']


class ComponentType(Enum):
    """Component types for ECS"""
    IDENTITY = "identity"
    TRANSFORM = "transform"
    CROP = "crop"
    EMPLOYEE = "employee"
    EQUIPMENT = "equipment"


@dataclass
class IdentityComponent:
    """Identity component for entities"""
    entity_id: str
    name: str
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TransformComponent:
    """Transform component for spatial entities"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    rotation: float = 0.0


@dataclass
class CropComponent:
    """Crop component for agricultural entities"""
    crop_type: str
    variety: str
    growth_stage: int = 0
    max_growth_stages: int = 10
    health: float = 100.0
    yield_potential: float = 1.0
    planted_date: datetime = field(default_factory=datetime.now)


@dataclass
class EmployeeComponent:
    """Employee component for worker entities"""
    employee_id: str
    name: str
    specialization: str
    skill_level: int = 1
    current_task: str = "idle"
    energy: float = 100.0
    assigned_equipment: str = ""


class EntityComponentSystem:
    """Simplified ECS for demo purposes"""
    
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        self.entities = {}
        self.components = {component_type: {} for component_type in ComponentType}
        self.next_entity_id = 1
        
        print("🔧 Entity-Component System initialized")
    
    def create_entity(self, name: str = "") -> str:
        """Create a new entity"""
        entity_id = f"entity_{self.next_entity_id:06d}"
        self.next_entity_id += 1
        
        self.entities[entity_id] = {
            'created_at': datetime.now(),
            'components': set()
        }
        
        # Auto-add identity component
        identity = IdentityComponent(entity_id=entity_id, name=name or f"Entity {entity_id}")
        self.add_component(entity_id, ComponentType.IDENTITY, identity)
        
        print(f"🆕 Created entity: {entity_id} ({name})")
        
        # Publish entity creation event
        self.event_system.publish('entity_created', {
            'entity_id': entity_id,
            'name': name
        })
        
        return entity_id
    
    def add_component(self, entity_id: str, component_type: ComponentType, component_data):
        """Add component to entity"""
        if entity_id not in self.entities:
            raise ValueError(f"Entity {entity_id} does not exist")
        
        self.components[component_type][entity_id] = component_data
        self.entities[entity_id]['components'].add(component_type)
        
        print(f"📦 Added {component_type.value} component to {entity_id}")
        
        # Publish component addition event
        self.event_system.publish('component_added', {
            'entity_id': entity_id,
            'component_type': component_type.value
        })
    
    def get_component(self, entity_id: str, component_type: ComponentType):
        """Get component from entity"""
        return self.components[component_type].get(entity_id)
    
    def get_entities_with_components(self, *component_types: ComponentType) -> List[str]:
        """Query entities that have all specified components"""
        entities_with_components = []
        
        for entity_id, entity_data in self.entities.items():
            if all(comp_type in entity_data['components'] for comp_type in component_types):
                entities_with_components.append(entity_id)
        
        return entities_with_components
    
    def update_component(self, entity_id: str, component_type: ComponentType, **updates):
        """Update component data"""
        if entity_id in self.components[component_type]:
            component = self.components[component_type][entity_id]
            for key, value in updates.items():
                if hasattr(component, key):
                    setattr(component, key, value)
            
            print(f"🔄 Updated {component_type.value} component for {entity_id}")
            
            # Publish component update event
            self.event_system.publish('component_updated', {
                'entity_id': entity_id,
                'component_type': component_type.value,
                'updates': updates
            })


class ContentRegistry:
    """Simplified Content Registry for demo purposes"""
    
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        self.content_data = {}
        self.content_schemas = {}
        
        print("📚 Content Registry initialized")
        self._load_demo_content()
    
    def _load_demo_content(self):
        """Load demo agricultural content"""
        
        # Crop varieties content
        crop_varieties = {
            "corn_standard": {
                "name": "Standard Field Corn",
                "category": "grain",
                "growth_stages": 10,
                "base_yield": 180.0,
                "water_requirement": "medium",
                "soil_preference": "well_drained",
                "maturity_days": 120,
                "traits": ["high_yield", "disease_resistant"]
            },
            "corn_sweet": {
                "name": "Sweet Corn",
                "category": "vegetable",
                "growth_stages": 8,
                "base_yield": 120.0,
                "water_requirement": "high",
                "soil_preference": "fertile",
                "maturity_days": 85,
                "traits": ["early_maturing", "sweet"]
            },
            "soybean_premium": {
                "name": "Premium Soybeans",
                "category": "legume",
                "growth_stages": 9,
                "base_yield": 50.0,
                "water_requirement": "medium",
                "soil_preference": "well_drained",
                "maturity_days": 110,
                "traits": ["nitrogen_fixing", "high_protein"]
            }
        }
        
        # Equipment content
        equipment_data = {
            "tractor_compact": {
                "name": "Compact Tractor",
                "category": "tractor",
                "horsepower": 45,
                "fuel_capacity": 25.0,
                "implements_supported": ["plow_small", "planter_small", "cultivator"],
                "purchase_cost": 35000,
                "operating_cost_per_hour": 12.50
            },
            "tractor_utility": {
                "name": "Utility Tractor",
                "category": "tractor",
                "horsepower": 85,
                "fuel_capacity": 50.0,
                "implements_supported": ["plow_medium", "planter_medium", "sprayer"],
                "purchase_cost": 65000,
                "operating_cost_per_hour": 22.00
            },
            "combine_harvester": {
                "name": "Combine Harvester",
                "category": "harvester",
                "horsepower": 300,
                "grain_tank_capacity": 350.0,
                "header_width": 30.0,
                "purchase_cost": 450000,
                "operating_cost_per_hour": 85.00
            }
        }
        
        # Employee specializations
        employee_specializations = {
            "field_operator": {
                "name": "Field Equipment Operator",
                "description": "Skilled in operating tractors and field implements",
                "base_wage_per_hour": 18.50,
                "efficiency_bonus": {
                    "tillage": 1.2,
                    "planting": 1.15,
                    "cultivation": 1.1
                },
                "equipment_proficiency": ["tractor_compact", "tractor_utility"]
            },
            "harvest_specialist": {
                "name": "Harvest Specialist",
                "description": "Expert in harvest operations and grain handling",
                "base_wage_per_hour": 22.00,
                "efficiency_bonus": {
                    "harvesting": 1.3,
                    "grain_handling": 1.25
                },
                "equipment_proficiency": ["combine_harvester", "grain_cart"]
            },
            "precision_ag_tech": {
                "name": "Precision Agriculture Technician",
                "description": "Specialist in GPS-guided equipment and data analysis",
                "base_wage_per_hour": 26.50,
                "efficiency_bonus": {
                    "precision_planting": 1.4,
                    "variable_rate_application": 1.35,
                    "data_analysis": 1.5
                },
                "equipment_proficiency": ["gps_tractor", "variable_rate_applicator"]
            }
        }
        
        # Store content
        self.content_data['crop_varieties'] = crop_varieties
        self.content_data['equipment'] = equipment_data
        self.content_data['employee_specializations'] = employee_specializations
        
        print(f"📦 Loaded content: {len(crop_varieties)} crops, {len(equipment_data)} equipment, {len(employee_specializations)} specializations")
        
        # Publish content loaded event
        self.event_system.publish('content_loaded', {
            'categories': list(self.content_data.keys()),
            'total_items': sum(len(data) for data in self.content_data.values())
        })
    
    def get_content(self, category: str, item_id: str = None):
        """Get content data"""
        if category not in self.content_data:
            return None
        
        if item_id:
            return self.content_data[category].get(item_id)
        else:
            return self.content_data[category]
    
    def get_all_content_categories(self) -> List[str]:
        """Get all available content categories"""
        return list(self.content_data.keys())


class AgriculturalSimulation:
    """Demo agricultural simulation integrating all foundation systems"""
    
    def __init__(self):
        print("🌾 Initializing AgriFun Foundation Architecture Demo")
        print("=" * 60)
        
        # Initialize foundation systems
        self.event_system = EventSystem()
        self.ecs = EntityComponentSystem(self.event_system)
        self.content_registry = ContentRegistry(self.event_system)
        
        # Subscribe to events for demo purposes
        self.event_system.subscribe('entity_created', self.on_entity_created)
        self.event_system.subscribe('component_added', self.on_component_added)
        self.event_system.subscribe('crop_planted', self.on_crop_planted)
        self.event_system.subscribe('employee_hired', self.on_employee_hired)
        
        print("\n🎯 Foundation systems initialized successfully!")
        print("=" * 60)
    
    def on_entity_created(self, event_data):
        """Handle entity creation events"""
        print(f"👂 Event Handler: New entity created - {event_data['entity_id']}")
    
    def on_component_added(self, event_data):
        """Handle component addition events"""
        print(f"👂 Event Handler: Component {event_data['component_type']} added to {event_data['entity_id']}")
    
    def on_crop_planted(self, event_data):
        """Handle crop planting events"""
        print(f"👂 Event Handler: {event_data['variety']} planted at ({event_data['x']}, {event_data['y']})")
    
    def on_employee_hired(self, event_data):
        """Handle employee hiring events"""
        print(f"👂 Event Handler: Hired {event_data['name']} as {event_data['specialization']}")
    
    def create_farm_scenario(self):
        """Create a demo farm scenario"""
        print("\n🚜 Creating Demo Farm Scenario")
        print("-" * 40)
        
        # Create farm entities
        farm_entities = []
        
        # 1. Plant some crops
        crop_varieties = self.content_registry.get_content('crop_varieties')
        for i, (variety_id, variety_data) in enumerate(list(crop_varieties.items())[:3]):
            # Create crop entity
            crop_entity = self.ecs.create_entity(f"{variety_data['name']} Plot {i+1}")
            farm_entities.append(crop_entity)
            
            # Add transform component (position on farm)
            transform = TransformComponent(x=i*10, y=0, z=0)
            self.ecs.add_component(crop_entity, ComponentType.TRANSFORM, transform)
            
            # Add crop component with data from content registry
            crop_comp = CropComponent(
                crop_type=variety_data['category'],
                variety=variety_id,
                growth_stage=random.randint(1, 5),
                max_growth_stages=variety_data['growth_stages'],
                health=random.uniform(80, 100),
                yield_potential=variety_data['base_yield'] / 100.0
            )
            self.ecs.add_component(crop_entity, ComponentType.CROP, crop_comp)
            
            # Publish crop planting event
            self.event_system.publish('crop_planted', {
                'entity_id': crop_entity,
                'variety': variety_data['name'],
                'x': transform.x,
                'y': transform.y
            }, EventPriority.HIGH)
        
        # 2. Hire some employees
        specializations = self.content_registry.get_content('employee_specializations')
        for i, (spec_id, spec_data) in enumerate(list(specializations.items())[:2]):
            # Create employee entity
            employee_entity = self.ecs.create_entity(f"Worker {i+1}")
            farm_entities.append(employee_entity)
            
            # Add transform component
            transform = TransformComponent(x=0, y=i*5, z=0)
            self.ecs.add_component(employee_entity, ComponentType.TRANSFORM, transform)
            
            # Add employee component
            employee_comp = EmployeeComponent(
                employee_id=employee_entity,
                name=f"Employee {i+1}",
                specialization=spec_id,
                skill_level=random.randint(1, 5),
                current_task="idle",
                energy=random.uniform(70, 100)
            )
            self.ecs.add_component(employee_entity, ComponentType.EMPLOYEE, employee_comp)
            
            # Publish employee hiring event
            self.event_system.publish('employee_hired', {
                'entity_id': employee_entity,
                'name': employee_comp.name,
                'specialization': spec_data['name']
            }, EventPriority.NORMAL)
        
        return farm_entities
    
    def simulate_farm_operations(self, farm_entities: List[str]):
        """Simulate some farm operations"""
        print("\n⚡ Simulating Farm Operations")
        print("-" * 40)
        
        # Simulate crop growth
        crop_entities = self.ecs.get_entities_with_components(ComponentType.CROP, ComponentType.TRANSFORM)
        for entity_id in crop_entities:
            crop_comp = self.ecs.get_component(entity_id, ComponentType.CROP)
            if crop_comp and crop_comp.growth_stage < crop_comp.max_growth_stages:
                # Simulate growth
                self.ecs.update_component(entity_id, ComponentType.CROP, 
                                        growth_stage=crop_comp.growth_stage + 1)
                
                # Publish growth event
                self.event_system.publish('crop_growth', {
                    'entity_id': entity_id,
                    'new_stage': crop_comp.growth_stage + 1,
                    'variety': crop_comp.variety
                })
        
        # Simulate employee task assignment
        employee_entities = self.ecs.get_entities_with_components(ComponentType.EMPLOYEE, ComponentType.TRANSFORM)
        tasks = ["planting", "cultivation", "harvesting", "equipment_maintenance"]
        
        for entity_id in employee_entities:
            new_task = random.choice(tasks)
            self.ecs.update_component(entity_id, ComponentType.EMPLOYEE, 
                                    current_task=new_task)
            
            # Publish task assignment event
            self.event_system.publish('task_assigned', {
                'entity_id': entity_id,
                'task': new_task
            })
    
    def display_farm_status(self):
        """Display current farm status"""
        print("\n📊 Current Farm Status")
        print("-" * 40)
        
        # Display crops
        crop_entities = self.ecs.get_entities_with_components(ComponentType.CROP)
        print(f"🌱 Crops: {len(crop_entities)}")
        for entity_id in crop_entities:
            identity = self.ecs.get_component(entity_id, ComponentType.IDENTITY)
            crop_comp = self.ecs.get_component(entity_id, ComponentType.CROP)
            transform = self.ecs.get_component(entity_id, ComponentType.TRANSFORM)
            
            if identity and crop_comp and transform:
                print(f"   • {identity.name}: Stage {crop_comp.growth_stage}/{crop_comp.max_growth_stages} "
                      f"at ({transform.x:.0f}, {transform.y:.0f}) - Health: {crop_comp.health:.1f}%")
        
        # Display employees
        employee_entities = self.ecs.get_entities_with_components(ComponentType.EMPLOYEE)
        print(f"\n👥 Employees: {len(employee_entities)}")
        for entity_id in employee_entities:
            identity = self.ecs.get_component(entity_id, ComponentType.IDENTITY)
            employee_comp = self.ecs.get_component(entity_id, ComponentType.EMPLOYEE)
            
            if identity and employee_comp:
                print(f"   • {employee_comp.name}: {employee_comp.specialization} "
                      f"(Skill Level {employee_comp.skill_level}) - Current Task: {employee_comp.current_task}")
        
        # Display event statistics
        print(f"\n📡 Events Processed: {self.event_system.events_processed}")
        print(f"📈 Total Entities: {len(self.ecs.entities)}")
    
    def demonstrate_content_system(self):
        """Demonstrate content system capabilities"""
        print("\n📚 Content System Demonstration")
        print("-" * 40)
        
        # Show available content categories
        categories = self.content_registry.get_all_content_categories()
        print(f"Available content categories: {categories}")
        
        # Demonstrate content querying
        for category in categories:
            content = self.content_registry.get_content(category)
            print(f"\n{category.title()} ({len(content)} items):")
            for item_id, item_data in list(content.items())[:2]:  # Show first 2 items
                print(f"   • {item_id}: {item_data.get('name', 'Unknown')}")
                if 'category' in item_data:
                    print(f"     Category: {item_data['category']}")
                if 'base_yield' in item_data:
                    print(f"     Base Yield: {item_data['base_yield']}")
                if 'horsepower' in item_data:
                    print(f"     Horsepower: {item_data['horsepower']}")
    
    def run_demo(self):
        """Run the complete foundation demo"""
        try:
            # 1. Demonstrate content system
            self.demonstrate_content_system()
            
            # 2. Create farm scenario
            farm_entities = self.create_farm_scenario()
            
            # 3. Display initial status
            self.display_farm_status()
            
            # 4. Simulate some operations
            print("\n⏱️  Simulating 3 time steps...")
            for step in range(3):
                print(f"\n--- Time Step {step + 1} ---")
                self.simulate_farm_operations(farm_entities)
                time.sleep(1)  # Brief pause for demo effect
            
            # 5. Display final status
            self.display_farm_status()
            
            # 6. Show event history summary
            print(f"\n📋 Event History Summary")
            print("-" * 40)
            event_types = {}
            for event in self.event_system.event_history:
                event_type = event['type']
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            for event_type, count in sorted(event_types.items()):
                print(f"   • {event_type}: {count} events")
            
            print(f"\n🎉 Demo completed successfully!")
            print(f"📊 Total events processed: {self.event_system.events_processed}")
            print(f"🏗️  Total entities created: {len(self.ecs.entities)}")
            
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main demo function"""
    print("AGRIFUN FOUNDATION ARCHITECTURE DEMO")
    print("====================================")
    print("Demonstrating:")
    print("• Event-driven communication")
    print("• Entity-Component System")
    print("• Content Registry integration")
    print("• Cross-system coordination")
    print("\nStarting demo...\n")
    
    # Create and run the simulation demo
    simulation = AgriculturalSimulation()
    simulation.run_demo()
    
    print("\n" + "=" * 60)
    print("FOUNDATION ARCHITECTURE DEMO COMPLETE!")
    print("This demonstrates the core systems working together")
    print("in preparation for the full agricultural simulation.")
    print("=" * 60)


if __name__ == "__main__":
    main()