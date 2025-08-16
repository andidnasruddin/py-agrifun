"""
Building & Infrastructure System - Comprehensive Farm Construction for AgriFun

This system provides complete building and infrastructure management including farm buildings,
infrastructure networks, construction management, and economic integration. Supports strategic
farm development with realistic construction mechanics and upgrade systems.

Key Features:
- Farm building construction (storage, barns, processing, utilities)
- Infrastructure networks (roads, fences, irrigation, power)
- Multi-stage construction with resource requirements
- Building upgrade and expansion systems
- Maintenance and operational costs
- Property value and asset management
- Integration with all Phase 2 systems
"""

import time
import math
import random
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

# Import foundation systems
from ..core.event_system import get_global_event_system, EventPriority
from ..core.entity_component_system import get_entity_manager
from ..core.configuration_system import get_configuration_manager
from ..core.state_management import get_state_manager
from ..core.advanced_grid_system import get_grid_system, GridLayer
from ..systems.time_system import get_time_system, Season
from ..systems.economy_system import get_economy_system, TransactionType
from ..systems.employee_system import get_employee_system, TaskType


class BuildingType(Enum):
    """Types of buildings that can be constructed"""
    # Storage Buildings
    STORAGE_SILO = "storage_silo"
    GRAIN_BIN = "grain_bin"
    COLD_STORAGE = "cold_storage"
    WAREHOUSE = "warehouse"
    
    # Production Buildings
    BARN = "barn"
    GREENHOUSE = "greenhouse"
    PROCESSING_FACILITY = "processing_facility"
    EQUIPMENT_SHED = "equipment_shed"
    
    # Utility Buildings
    FARMHOUSE = "farmhouse"
    OFFICE = "office"
    MAINTENANCE_SHOP = "maintenance_shop"
    FUEL_STATION = "fuel_station"
    
    # Infrastructure
    IRRIGATION_PUMP = "irrigation_pump"
    POWER_GENERATOR = "power_generator"
    WATER_TOWER = "water_tower"
    COMPOSTING_FACILITY = "composting_facility"


class BuildingStatus(Enum):
    """Construction and operational status of buildings"""
    PLANNED = "planned"              # Design phase, not yet started
    UNDER_CONSTRUCTION = "under_construction"  # Currently being built
    OPERATIONAL = "operational"      # Fully functional
    MAINTENANCE = "maintenance"      # Temporarily offline for repairs
    DAMAGED = "damaged"             # Needs repair
    DEMOLISHED = "demolished"        # Torn down


class InfrastructureType(Enum):
    """Types of infrastructure that can be built"""
    ROAD = "road"                   # Vehicle access
    FENCE = "fence"                 # Property boundaries and livestock
    IRRIGATION_PIPE = "irrigation_pipe"  # Water distribution
    POWER_LINE = "power_line"       # Electrical distribution
    DRAINAGE = "drainage"           # Water management
    LIGHTING = "lighting"           # Area illumination


class ResourceType(Enum):
    """Construction resource types"""
    LUMBER = "lumber"
    CONCRETE = "concrete"
    STEEL = "steel"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    INSULATION = "insulation"
    ROOFING = "roofing"
    FOUNDATION = "foundation"


@dataclass
class BuildingSpecs:
    """Specifications for building types"""
    building_type: BuildingType
    
    # Physical properties
    size_x: int = 2                 # Width in tiles
    size_y: int = 2                 # Height in tiles
    height: float = 3.0             # Building height in meters
    
    # Construction requirements
    construction_cost: float = 5000.0
    construction_time_days: int = 7
    required_resources: Dict[ResourceType, int] = field(default_factory=dict)
    required_workers: int = 2
    
    # Operational properties
    storage_capacity: int = 0       # Storage units (if applicable)
    power_requirement: float = 0.0  # kW required
    water_requirement: float = 0.0  # Liters per day
    maintenance_cost_daily: float = 5.0
    
    # Economic properties
    property_value: float = 8000.0
    insurance_cost_daily: float = 2.0
    depreciation_rate: float = 0.02  # Annual rate
    
    # Functionality
    provides_functionality: List[str] = field(default_factory=list)
    efficiency_bonus: Dict[str, float] = field(default_factory=dict)


@dataclass
class Infrastructure:
    """Infrastructure element (roads, fences, utilities)"""
    infrastructure_id: str
    infrastructure_type: InfrastructureType
    start_location: Tuple[int, int]
    end_location: Tuple[int, int]
    
    # Construction
    construction_cost: float = 50.0
    construction_time_hours: int = 4
    status: BuildingStatus = BuildingStatus.PLANNED
    
    # Properties
    capacity: float = 100.0         # Usage capacity
    current_load: float = 0.0       # Current usage
    maintenance_cost_daily: float = 1.0
    
    # Network connectivity
    connected_buildings: List[str] = field(default_factory=list)
    network_efficiency: float = 1.0
    
    def get_length(self) -> float:
        """Calculate infrastructure length"""
        dx = self.end_location[0] - self.start_location[0]
        dy = self.end_location[1] - self.start_location[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def is_overloaded(self) -> bool:
        """Check if infrastructure is over capacity"""
        return self.current_load > self.capacity


@dataclass
class Building:
    """Complete building instance with all properties"""
    building_id: str
    building_type: BuildingType
    location: Tuple[int, int]
    
    # Construction details
    construction_start_time: int = 0
    construction_progress: float = 0.0
    status: BuildingStatus = BuildingStatus.PLANNED
    
    # Physical state
    condition: float = 100.0        # Building condition (0-100)
    last_maintenance: int = 0
    upgrade_level: int = 1          # Building upgrade level
    
    # Operational state
    current_storage: int = 0        # Current stored items
    power_connected: bool = False
    water_connected: bool = False
    operational_efficiency: float = 1.0
    
    # Economic tracking
    total_construction_cost: float = 0.0
    total_maintenance_cost: float = 0.0
    current_value: float = 0.0
    
    # Connectivity
    connected_infrastructure: List[str] = field(default_factory=list)
    served_tiles: List[Tuple[int, int]] = field(default_factory=list)
    
    def get_effective_capacity(self, specs: BuildingSpecs) -> int:
        """Get effective storage capacity considering condition and upgrades"""
        base_capacity = specs.storage_capacity
        condition_factor = self.condition / 100.0
        upgrade_factor = 1.0 + (self.upgrade_level - 1) * 0.3
        efficiency_factor = self.operational_efficiency
        
        return int(base_capacity * condition_factor * upgrade_factor * efficiency_factor)
    
    def needs_maintenance(self) -> bool:
        """Check if building needs maintenance"""
        return self.condition < 80.0
    
    def is_functional(self) -> bool:
        """Check if building is operational"""
        return (self.status == BuildingStatus.OPERATIONAL and 
                self.condition > 20.0)


class ConstructionManager:
    """Manages building construction processes"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger('ConstructionManager')
        
        # Resource inventory
        self.resource_inventory: Dict[ResourceType, int] = {
            resource: 0 for resource in ResourceType
        }
        
        # Add starting resources
        self.resource_inventory[ResourceType.LUMBER] = 100
        self.resource_inventory[ResourceType.CONCRETE] = 50
        
        # Construction projects
        self.active_projects: Dict[str, Dict[str, Any]] = {}
        
        # Building specifications
        self.building_specs = self._initialize_building_specs()
    
    def _initialize_building_specs(self) -> Dict[BuildingType, BuildingSpecs]:
        """Initialize building specifications"""
        specs = {}
        
        # Storage Buildings
        specs[BuildingType.STORAGE_SILO] = BuildingSpecs(
            building_type=BuildingType.STORAGE_SILO,
            size_x=3, size_y=3, height=12.0,
            construction_cost=15000.0,
            construction_time_days=14,
            required_resources={
                ResourceType.CONCRETE: 50,
                ResourceType.STEEL: 30,
                ResourceType.ELECTRICAL: 10
            },
            required_workers=3,
            storage_capacity=1000,
            power_requirement=5.0,
            maintenance_cost_daily=15.0,
            property_value=20000.0,
            provides_functionality=["grain_storage", "automated_loading"],
            efficiency_bonus={"storage_efficiency": 1.5}
        )
        
        specs[BuildingType.BARN] = BuildingSpecs(
            building_type=BuildingType.BARN,
            size_x=4, size_y=6, height=8.0,
            construction_cost=25000.0,
            construction_time_days=21,
            required_resources={
                ResourceType.LUMBER: 80,
                ResourceType.CONCRETE: 40,
                ResourceType.STEEL: 20,
                ResourceType.ROOFING: 30
            },
            required_workers=4,
            storage_capacity=500,
            power_requirement=10.0,
            water_requirement=200.0,
            maintenance_cost_daily=25.0,
            property_value=35000.0,
            provides_functionality=["livestock_housing", "equipment_storage", "workshop"],
            efficiency_bonus={"livestock_productivity": 1.3, "equipment_protection": 1.2}
        )
        
        specs[BuildingType.GREENHOUSE] = BuildingSpecs(
            building_type=BuildingType.GREENHOUSE,
            size_x=5, size_y=8, height=4.0,
            construction_cost=30000.0,
            construction_time_days=28,
            required_resources={
                ResourceType.STEEL: 40,
                ResourceType.ELECTRICAL: 25,
                ResourceType.PLUMBING: 20,
                ResourceType.INSULATION: 15
            },
            required_workers=3,
            power_requirement=20.0,
            water_requirement=500.0,
            maintenance_cost_daily=30.0,
            property_value=40000.0,
            provides_functionality=["controlled_environment", "year_round_growing", "crop_research"],
            efficiency_bonus={"crop_yield": 2.0, "crop_quality": 1.5, "growing_season": 4.0}
        )
        
        specs[BuildingType.EQUIPMENT_SHED] = BuildingSpecs(
            building_type=BuildingType.EQUIPMENT_SHED,
            size_x=3, size_y=4, height=5.0,
            construction_cost=8000.0,
            construction_time_days=10,
            required_resources={
                ResourceType.LUMBER: 40,
                ResourceType.CONCRETE: 20,
                ResourceType.ROOFING: 15
            },
            required_workers=2,
            storage_capacity=200,
            power_requirement=5.0,
            maintenance_cost_daily=8.0,
            property_value=12000.0,
            provides_functionality=["equipment_storage", "maintenance_bay"],
            efficiency_bonus={"equipment_durability": 1.4, "maintenance_efficiency": 1.3}
        )
        
        specs[BuildingType.FARMHOUSE] = BuildingSpecs(
            building_type=BuildingType.FARMHOUSE,
            size_x=4, size_y=5, height=6.0,
            construction_cost=50000.0,
            construction_time_days=45,
            required_resources={
                ResourceType.LUMBER: 100,
                ResourceType.CONCRETE: 60,
                ResourceType.ELECTRICAL: 40,
                ResourceType.PLUMBING: 30,
                ResourceType.INSULATION: 25,
                ResourceType.ROOFING: 20
            },
            required_workers=5,
            power_requirement=15.0,
            water_requirement=300.0,
            maintenance_cost_daily=20.0,
            property_value=75000.0,
            provides_functionality=["living_quarters", "office_space", "storage"],
            efficiency_bonus={"employee_satisfaction": 1.4, "management_efficiency": 1.3}
        )
        
        # Utility Buildings
        specs[BuildingType.IRRIGATION_PUMP] = BuildingSpecs(
            building_type=BuildingType.IRRIGATION_PUMP,
            size_x=2, size_y=2, height=3.0,
            construction_cost=12000.0,
            construction_time_days=7,
            required_resources={
                ResourceType.STEEL: 15,
                ResourceType.ELECTRICAL: 20,
                ResourceType.PLUMBING: 25
            },
            required_workers=2,
            power_requirement=25.0,
            maintenance_cost_daily=12.0,
            property_value=15000.0,
            provides_functionality=["water_distribution", "irrigation_control"],
            efficiency_bonus={"irrigation_efficiency": 1.6, "water_pressure": 1.4}
        )
        
        return specs
    
    def can_build(self, building_type: BuildingType, location: Tuple[int, int]) -> Dict[str, Any]:
        """Check if building can be constructed at location"""
        specs = self.building_specs[building_type]
        
        # Check resources
        resource_check = True
        missing_resources = []
        for resource, amount in specs.required_resources.items():
            if self.resource_inventory[resource] < amount:
                resource_check = False
                missing_resources.append(f"{resource.value}: {amount - self.resource_inventory[resource]}")
        
        # Check space (simplified - would integrate with grid system)
        space_available = True  # TODO: Implement proper grid checking
        
        return {
            'can_build': resource_check and space_available,
            'resource_check': resource_check,
            'space_check': space_available,
            'missing_resources': missing_resources,
            'estimated_cost': specs.construction_cost,
            'construction_time': specs.construction_time_days
        }
    
    def start_construction(self, building_id: str, building_type: BuildingType, 
                          location: Tuple[int, int]) -> Dict[str, Any]:
        """Begin construction of a building"""
        specs = self.building_specs[building_type]
        
        # Check if construction is possible
        can_build_result = self.can_build(building_type, location)
        if not can_build_result['can_build']:
            return {
                'success': False,
                'message': 'Cannot start construction',
                'details': can_build_result
            }
        
        # Consume resources
        for resource, amount in specs.required_resources.items():
            self.resource_inventory[resource] -= amount
        
        # Create construction project
        project = {
            'building_id': building_id,
            'building_type': building_type,
            'location': location,
            'start_time': time.time(),
            'progress': 0.0,
            'workers_assigned': 0,
            'daily_progress_rate': 1.0 / specs.construction_time_days
        }
        
        self.active_projects[building_id] = project
        
        return {
            'success': True,
            'project_id': building_id,
            'estimated_completion_days': specs.construction_time_days
        }
    
    def update_construction(self, delta_time_hours: float):
        """Update all active construction projects"""
        completed_projects = []
        
        for project_id, project in self.active_projects.items():
            # Calculate progress based on assigned workers
            if project['workers_assigned'] >= self.building_specs[project['building_type']].required_workers:
                daily_progress = project['daily_progress_rate']
                hourly_progress = daily_progress / 24.0
                
                project['progress'] += hourly_progress * delta_time_hours
                
                # Check for completion
                if project['progress'] >= 1.0:
                    completed_projects.append(project_id)
        
        return completed_projects
    
    def complete_construction(self, project_id: str) -> Building:
        """Complete a construction project and return the building"""
        project = self.active_projects[project_id]
        specs = self.building_specs[project['building_type']]
        
        # Create completed building
        building = Building(
            building_id=project['building_id'],
            building_type=project['building_type'],
            location=project['location'],
            construction_start_time=int(project['start_time']),
            construction_progress=1.0,
            status=BuildingStatus.OPERATIONAL,
            condition=100.0,
            total_construction_cost=specs.construction_cost,
            current_value=specs.property_value
        )
        
        # Remove from active projects
        del self.active_projects[project_id]
        
        return building


class BuildingSystem:
    """Main building and infrastructure management system"""
    
    def __init__(self):
        # Core systems
        self.event_system = get_global_event_system()
        self.entity_manager = get_entity_manager()
        self.config_manager = get_configuration_manager()
        self.state_manager = get_state_manager()
        self.time_system = get_time_system()
        self.economy_system = get_economy_system()
        self.employee_system = get_employee_system()
        self.grid_system = get_grid_system()
        
        # Building management
        self.buildings: Dict[str, Building] = {}
        self.infrastructure: Dict[str, Infrastructure] = {}
        self.building_counter = 0
        self.infrastructure_counter = 0
        
        # Construction management
        self.construction_manager = ConstructionManager(self.config_manager)
        
        # Property and asset tracking
        self.total_property_value = 0.0
        self.total_construction_investment = 0.0
        self.total_maintenance_costs = 0.0
        
        self.logger = logging.getLogger('BuildingSystem')
        
        # Load configuration
        self._load_configuration()
        
        # Subscribe to events
        self._subscribe_to_events()
        
        # Initialize system
        self._initialize_system()
    
    def _load_configuration(self):
        """Load building system configuration"""
        default_config = {
            'buildings.construction_speed_modifier': 1.0,
            'buildings.maintenance_cost_modifier': 1.0,
            'buildings.resource_efficiency': 1.0,
            'buildings.max_buildings': 50,
            'infrastructure.max_infrastructure': 200
        }
        
        for key, value in default_config.items():
            if self.config_manager.get(key) is None:
                self.config_manager.set(key, value)
    
    def _subscribe_to_events(self):
        """Subscribe to relevant system events"""
        self.event_system.subscribe('hour_changed', self._on_hour_changed)
        self.event_system.subscribe('day_changed', self._on_day_changed)
        self.event_system.subscribe('season_changed', self._on_season_changed)
    
    def _initialize_system(self):
        """Initialize building system"""
        # Add starting resources
        self.construction_manager.resource_inventory[ResourceType.LUMBER] = 200
        self.construction_manager.resource_inventory[ResourceType.CONCRETE] = 100
        self.construction_manager.resource_inventory[ResourceType.STEEL] = 50
        
        self.logger.info("Building system initialized")
    
    def plan_building(self, building_type: BuildingType, location: Tuple[int, int]) -> Dict[str, Any]:
        """Plan a new building construction"""
        max_buildings = self.config_manager.get('buildings.max_buildings', 50)
        if len(self.buildings) >= max_buildings:
            return {'success': False, 'message': 'Maximum building capacity reached'}
        
        # Generate building ID
        self.building_counter += 1
        building_id = f"building_{self.building_counter:04d}"
        
        # Check if construction is viable
        can_build = self.construction_manager.can_build(building_type, location)
        
        if not can_build['can_build']:
            return {
                'success': False,
                'message': 'Cannot build at this location',
                'details': can_build
            }
        
        # Calculate total cost including labor
        specs = self.construction_manager.building_specs[building_type]
        base_cost = specs.construction_cost
        labor_cost = specs.required_workers * specs.construction_time_days * 100  # $100/worker/day
        total_cost = base_cost + labor_cost
        
        return {
            'success': True,
            'building_id': building_id,
            'building_type': building_type.value,
            'location': location,
            'total_cost': total_cost,
            'construction_time_days': specs.construction_time_days,
            'required_resources': {r.value: a for r, a in specs.required_resources.items()},
            'required_workers': specs.required_workers,
            'provides_functionality': specs.provides_functionality
        }
    
    def start_construction(self, building_type: BuildingType, location: Tuple[int, int]) -> Dict[str, Any]:
        """Begin construction of a building"""
        # Plan the building first
        plan_result = self.plan_building(building_type, location)
        if not plan_result['success']:
            return plan_result
        
        building_id = plan_result['building_id']
        
        # Check funds
        total_cost = plan_result['total_cost']
        if self.economy_system.current_cash < total_cost:
            return {'success': False, 'message': 'Insufficient funds for construction'}
        
        # Start construction
        construction_result = self.construction_manager.start_construction(
            building_id, building_type, location
        )
        
        if not construction_result['success']:
            return construction_result
        
        # Pay for construction
        transaction_id = self.economy_system.add_transaction(
            TransactionType.EQUIPMENT_PURCHASE,
            -total_cost,
            f"Construction: {building_type.value}",
            metadata={
                'building_id': building_id,
                'building_type': building_type.value,
                'location': location
            }
        )
        
        # Create building in planned state
        building = Building(
            building_id=building_id,
            building_type=building_type,
            location=location,
            construction_start_time=self.time_system.get_current_time().total_minutes,
            status=BuildingStatus.UNDER_CONSTRUCTION,
            total_construction_cost=total_cost
        )
        
        self.buildings[building_id] = building
        self.total_construction_investment += total_cost
        
        # Assign workers if available
        self._assign_construction_workers(building_id)
        
        # Emit construction event
        self.event_system.publish('construction_started', {
            'building_id': building_id,
            'building_type': building_type.value,
            'location': location,
            'total_cost': total_cost,
            'transaction_id': transaction_id
        }, EventPriority.NORMAL, 'building_system')
        
        self.logger.info(f"Started construction of {building_type.value} at {location} for ${total_cost:.2f}")
        
        return {
            'success': True,
            'building_id': building_id,
            'transaction_id': transaction_id,
            'estimated_completion_days': construction_result['estimated_completion_days']
        }
    
    def upgrade_building(self, building_id: str) -> Dict[str, Any]:
        """Upgrade an existing building"""
        if building_id not in self.buildings:
            return {'success': False, 'message': 'Building not found'}
        
        building = self.buildings[building_id]
        
        if building.status != BuildingStatus.OPERATIONAL:
            return {'success': False, 'message': 'Building must be operational to upgrade'}
        
        # Calculate upgrade cost
        specs = self.construction_manager.building_specs[building.building_type]
        upgrade_cost = specs.construction_cost * 0.5 * building.upgrade_level
        
        if self.economy_system.current_cash < upgrade_cost:
            return {'success': False, 'message': 'Insufficient funds for upgrade'}
        
        # Perform upgrade
        building.upgrade_level += 1
        building.status = BuildingStatus.MAINTENANCE  # Temporarily offline
        building.current_value = specs.property_value * (1.0 + (building.upgrade_level - 1) * 0.4)
        
        # Pay for upgrade
        transaction_id = self.economy_system.add_transaction(
            TransactionType.EQUIPMENT_PURCHASE,
            -upgrade_cost,
            f"Building upgrade: {building.building_type.value}",
            metadata={'building_id': building_id, 'new_level': building.upgrade_level}
        )
        
        self.logger.info(f"Upgraded {building.building_type.value} to level {building.upgrade_level}")
        
        return {
            'success': True,
            'new_level': building.upgrade_level,
            'upgrade_cost': upgrade_cost,
            'new_value': building.current_value,
            'transaction_id': transaction_id
        }
    
    def demolish_building(self, building_id: str) -> Dict[str, Any]:
        """Demolish a building"""
        if building_id not in self.buildings:
            return {'success': False, 'message': 'Building not found'}
        
        building = self.buildings[building_id]
        
        # Calculate salvage value
        salvage_value = building.current_value * 0.3  # 30% salvage value
        
        # Add salvage income
        transaction_id = self.economy_system.add_transaction(
            TransactionType.EQUIPMENT_PURCHASE,  # Using equipment category for building transactions
            salvage_value,
            f"Building demolition salvage: {building.building_type.value}",
            metadata={'building_id': building_id}
        )
        
        # Remove building
        building.status = BuildingStatus.DEMOLISHED
        del self.buildings[building_id]
        
        return {
            'success': True,
            'salvage_value': salvage_value,
            'transaction_id': transaction_id
        }
    
    def build_infrastructure(self, infrastructure_type: InfrastructureType, 
                           start_location: Tuple[int, int], 
                           end_location: Tuple[int, int]) -> Dict[str, Any]:
        """Build infrastructure between two points"""
        max_infrastructure = self.config_manager.get('infrastructure.max_infrastructure', 200)
        if len(self.infrastructure) >= max_infrastructure:
            return {'success': False, 'message': 'Maximum infrastructure capacity reached'}
        
        # Generate infrastructure ID
        self.infrastructure_counter += 1
        infrastructure_id = f"infrastructure_{self.infrastructure_counter:04d}"
        
        # Calculate cost based on length and type
        length = math.sqrt((end_location[0] - start_location[0]) ** 2 + 
                          (end_location[1] - start_location[1]) ** 2)
        
        cost_per_unit = {
            InfrastructureType.ROAD: 100.0,
            InfrastructureType.FENCE: 25.0,
            InfrastructureType.IRRIGATION_PIPE: 50.0,
            InfrastructureType.POWER_LINE: 75.0,
            InfrastructureType.DRAINAGE: 60.0,
            InfrastructureType.LIGHTING: 150.0
        }
        
        total_cost = length * cost_per_unit[infrastructure_type]
        
        if self.economy_system.current_cash < total_cost:
            return {'success': False, 'message': 'Insufficient funds for infrastructure'}
        
        # Create infrastructure
        infrastructure = Infrastructure(
            infrastructure_id=infrastructure_id,
            infrastructure_type=infrastructure_type,
            start_location=start_location,
            end_location=end_location,
            construction_cost=total_cost,
            status=BuildingStatus.OPERATIONAL
        )
        
        self.infrastructure[infrastructure_id] = infrastructure
        
        # Pay for construction
        transaction_id = self.economy_system.add_transaction(
            TransactionType.EQUIPMENT_PURCHASE,
            -total_cost,
            f"Infrastructure: {infrastructure_type.value}",
            metadata={
                'infrastructure_id': infrastructure_id,
                'type': infrastructure_type.value,
                'length': length
            }
        )
        
        self.logger.info(f"Built {infrastructure_type.value} infrastructure for ${total_cost:.2f}")
        
        return {
            'success': True,
            'infrastructure_id': infrastructure_id,
            'total_cost': total_cost,
            'length': length,
            'transaction_id': transaction_id
        }
    
    def get_building_info(self, building_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a building"""
        if building_id not in self.buildings:
            return None
        
        building = self.buildings[building_id]
        specs = self.construction_manager.building_specs[building.building_type]
        
        # Check if under construction
        construction_info = None
        if building.status == BuildingStatus.UNDER_CONSTRUCTION:
            if building_id in self.construction_manager.active_projects:
                project = self.construction_manager.active_projects[building_id]
                construction_info = {
                    'progress': project['progress'],
                    'workers_assigned': project['workers_assigned'],
                    'required_workers': specs.required_workers,
                    'estimated_completion_days': (1.0 - project['progress']) / project['daily_progress_rate']
                }
        
        return {
            'building_id': building_id,
            'building_type': building.building_type.value,
            'location': building.location,
            'status': building.status.value,
            'upgrade_level': building.upgrade_level,
            'condition': building.condition,
            'current_value': building.current_value,
            'storage_capacity': building.get_effective_capacity(specs),
            'current_storage': building.current_storage,
            'power_connected': building.power_connected,
            'water_connected': building.water_connected,
            'operational_efficiency': building.operational_efficiency,
            'provides_functionality': specs.provides_functionality,
            'efficiency_bonus': specs.efficiency_bonus,
            'construction_info': construction_info,
            'maintenance_needed': building.needs_maintenance()
        }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get building system summary"""
        # Count buildings by type and status
        building_counts = {}
        status_counts = {}
        
        for building in self.buildings.values():
            building_type = building.building_type.value
            status = building.status.value
            
            building_counts[building_type] = building_counts.get(building_type, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count infrastructure by type
        infrastructure_counts = {}
        for infrastructure in self.infrastructure.values():
            infra_type = infrastructure.infrastructure_type.value
            infrastructure_counts[infra_type] = infrastructure_counts.get(infra_type, 0) + 1
        
        # Calculate total property value
        self.total_property_value = sum(building.current_value for building in self.buildings.values())
        
        # Calculate daily operational costs
        daily_maintenance = 0.0
        for building in self.buildings.values():
            if building.status == BuildingStatus.OPERATIONAL:
                specs = self.construction_manager.building_specs[building.building_type]
                daily_maintenance += specs.maintenance_cost_daily
        
        for infrastructure in self.infrastructure.values():
            if infrastructure.status == BuildingStatus.OPERATIONAL:
                daily_maintenance += infrastructure.maintenance_cost_daily
        
        return {
            'total_buildings': len(self.buildings),
            'total_infrastructure': len(self.infrastructure),
            'buildings_by_type': building_counts,
            'buildings_by_status': status_counts,
            'infrastructure_by_type': infrastructure_counts,
            'total_property_value': self.total_property_value,
            'total_construction_investment': self.total_construction_investment,
            'total_maintenance_costs': self.total_maintenance_costs,
            'daily_maintenance_cost': daily_maintenance,
            'active_construction_projects': len(self.construction_manager.active_projects),
            'resource_inventory': dict(self.construction_manager.resource_inventory)
        }
    
    def _assign_construction_workers(self, building_id: str):
        """Assign available workers to construction project"""
        if building_id not in self.construction_manager.active_projects:
            return
        
        project = self.construction_manager.active_projects[building_id]
        required_workers = self.construction_manager.building_specs[project['building_type']].required_workers
        
        # Try to assign workers (simplified - would integrate with employee system)
        # For now, assume workers are automatically assigned
        project['workers_assigned'] = required_workers
    
    def _on_hour_changed(self, event_data: Dict[str, Any]):
        """Handle hourly building updates"""
        # Update construction progress
        completed_projects = self.construction_manager.update_construction(1.0)  # 1 hour
        
        # Complete any finished construction projects
        for project_id in completed_projects:
            if project_id in self.buildings:
                building = self.construction_manager.complete_construction(project_id)
                self.buildings[project_id] = building
                
                # Emit completion event
                self.event_system.publish('construction_completed', {
                    'building_id': building.building_id,
                    'building_type': building.building_type.value,
                    'location': building.location
                }, EventPriority.NORMAL, 'building_system')
    
    def _on_day_changed(self, event_data: Dict[str, Any]):
        """Handle daily building management"""
        # Process maintenance costs
        daily_costs = 0.0
        
        for building in self.buildings.values():
            if building.status == BuildingStatus.OPERATIONAL:
                specs = self.construction_manager.building_specs[building.building_type]
                
                # Daily maintenance cost
                maintenance_cost = specs.maintenance_cost_daily
                daily_costs += maintenance_cost
                
                # Gradual condition degradation
                degradation_rate = 0.1  # 0.1% per day
                building.condition = max(0, building.condition - degradation_rate)
                
                # Update last maintenance if condition gets too low
                if building.condition < 50.0:
                    building.last_maintenance = self.time_system.get_current_time().total_minutes
        
        # Process infrastructure maintenance
        for infrastructure in self.infrastructure.values():
            if infrastructure.status == BuildingStatus.OPERATIONAL:
                daily_costs += infrastructure.maintenance_cost_daily
        
        # Pay daily maintenance costs
        if daily_costs > 0:
            transaction_id = self.economy_system.add_transaction(
                TransactionType.OPERATING_EXPENSE,
                -daily_costs,
                "Daily building and infrastructure maintenance",
                metadata={'maintenance_cost': daily_costs}
            )
            
            self.total_maintenance_costs += daily_costs
    
    def _on_season_changed(self, event_data: Dict[str, Any]):
        """Handle seasonal building effects"""
        new_season = event_data['new_season']
        
        # Seasonal effects on construction and maintenance
        seasonal_modifiers = {
            'spring': 1.1,  # Optimal construction season
            'summer': 1.0,
            'fall': 0.9,    # Slightly slower due to weather
            'winter': 0.7   # Difficult construction conditions
        }
        
        modifier = seasonal_modifiers.get(new_season, 1.0)
        
        # Update construction progress rates
        for project in self.construction_manager.active_projects.values():
            base_rate = 1.0 / self.construction_manager.building_specs[project['building_type']].construction_time_days
            project['daily_progress_rate'] = base_rate * modifier
        
        self.logger.info(f"Applied seasonal construction modifier for {new_season}: {modifier:.1%}")


# Global building system instance
_global_building_system: Optional[BuildingSystem] = None

def get_building_system() -> BuildingSystem:
    """Get the global building system instance"""
    global _global_building_system
    if _global_building_system is None:
        _global_building_system = BuildingSystem()
    return _global_building_system

def initialize_building_system() -> BuildingSystem:
    """Initialize the global building system"""
    global _global_building_system
    _global_building_system = BuildingSystem()
    return _global_building_system

# Convenience functions
def start_construction(building_type: BuildingType, location: Tuple[int, int]) -> Dict[str, Any]:
    """Start building construction"""
    return get_building_system().start_construction(building_type, location)

def get_building_info(building_id: str) -> Optional[Dict[str, Any]]:
    """Get building information"""
    return get_building_system().get_building_info(building_id)

def get_building_summary() -> Dict[str, Any]:
    """Get building system summary"""
    return get_building_system().get_system_summary()