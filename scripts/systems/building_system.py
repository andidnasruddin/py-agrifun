"""
Building & Infrastructure System - Comprehensive Farm Construction for AgriFun Agricultural Simulation

This system provides complete building and infrastructure management with construction mechanics,
building types, upgrade systems, and economic integration. Integrates with all Phase 2 systems
for comprehensive farm development and operational efficiency improvements.

Key Features:
- Multiple building types (storage, processing, utility, residential)
- Construction system with material requirements and labor costs
- Building upgrades and expansion capabilities
- Infrastructure networks (power, water, roads)
- Maintenance and repair systems
- Economic integration with construction costs and operational benefits
- Employee housing and facility management
- Equipment storage and workshop buildings

Building Categories:
- Storage Buildings: Silos, warehouses, cold storage, grain bins
- Processing Buildings: Mills, packaging plants, processing facilities
- Utility Buildings: Power generators, water systems, fuel storage
- Agricultural Buildings: Greenhouses, livestock barns, equipment sheds
- Residential Buildings: Employee housing, offices, cafeterias
- Infrastructure: Roads, fencing, irrigation systems, power lines

Integration Features:
- Economy system integration for construction costs and financing
- Employee system integration for construction labor and housing
- Crop system integration for storage and processing capabilities
- Time system integration for construction duration and seasonal effects
- Save/load system integration for building persistence

Usage Example:
    # Initialize building system
    building_system = BuildingSystem()
    await building_system.initialize()
    
    # Construct buildings
    building_id = await building_system.start_construction('grain_silo', (10, 12))
    
    # Manage construction
    await building_system.assign_construction_workers(building_id, ['employee_1', 'employee_2'])
    
    # Upgrade buildings
    await building_system.upgrade_building(building_id, 'capacity_expansion')
"""

import time
import math
import random
from typing import Dict, List, Set, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

# Import Phase 1 architecture
from scripts.core.entity_component_system import System, Entity, Component
from scripts.core.advanced_event_system import get_event_system, EventPriority
from scripts.core.time_management import get_time_manager, Season, WeatherType
from scripts.core.advanced_config_system import get_config_manager
from scripts.systems.economy_system import get_economy_system
from scripts.systems.employee_system import get_employee_system
from scripts.systems.crop_system import get_crop_system


class BuildingType(Enum):
    """Types of buildings available for construction"""
    # Storage Buildings
    GRAIN_SILO = "grain_silo"
    WAREHOUSE = "warehouse"
    COLD_STORAGE = "cold_storage"
    EQUIPMENT_SHED = "equipment_shed"
    
    # Processing Buildings
    GRAIN_MILL = "grain_mill"
    PACKAGING_PLANT = "packaging_plant"
    PROCESSING_FACILITY = "processing_facility"
    
    # Utility Buildings
    GENERATOR = "generator"
    WATER_TOWER = "water_tower"
    FUEL_STORAGE = "fuel_storage"
    MAINTENANCE_SHOP = "maintenance_shop"
    
    # Agricultural Buildings
    GREENHOUSE = "greenhouse"
    LIVESTOCK_BARN = "livestock_barn"
    EQUIPMENT_GARAGE = "equipment_garage"
    
    # Residential Buildings
    EMPLOYEE_HOUSING = "employee_housing"
    OFFICE_BUILDING = "office_building"
    CAFETERIA = "cafeteria"
    
    # Infrastructure
    ROAD_SECTION = "road_section"
    FENCE_SECTION = "fence_section"
    IRRIGATION_PUMP = "irrigation_pump"
    POWER_LINE = "power_line"


class BuildingStatus(Enum):
    """Building construction and operational status"""
    PLANNED = "planned"
    UNDER_CONSTRUCTION = "under_construction"
    OPERATIONAL = "operational"
    UNDER_MAINTENANCE = "under_maintenance"
    DAMAGED = "damaged"
    DEMOLISHED = "demolished"


class ConstructionStage(Enum):
    """Stages of building construction"""
    FOUNDATION = "foundation"
    FRAMING = "framing"
    WALLS = "walls"
    ROOFING = "roofing"
    UTILITIES = "utilities"
    INTERIOR = "interior"
    FINISHING = "finishing"
    INSPECTION = "inspection"


class MaterialType(Enum):
    """Construction materials"""
    CONCRETE = "concrete"
    STEEL = "steel"
    LUMBER = "lumber"
    BRICK = "brick"
    INSULATION = "insulation"
    ROOFING = "roofing"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    PAINT = "paint"
    HARDWARE = "hardware"


@dataclass
class Material:
    """Construction material specification"""
    material_type: MaterialType
    quantity: float
    unit: str = "units"  # tons, cubic meters, square meters, etc.
    cost_per_unit: float = 10.0
    supplier: str = "Local Supplier"
    delivery_time_days: int = 3
    quality_grade: str = "standard"
    
    def get_total_cost(self) -> float:
        """Calculate total cost for this material"""
        return self.quantity * self.cost_per_unit


@dataclass
class BuildingTemplate:
    """Template defining a building type's characteristics"""
    building_type: BuildingType
    name: str
    description: str
    category: str
    
    # Physical characteristics
    size: Tuple[int, int] = (2, 2)  # Grid squares occupied
    height: float = 5.0  # Meters
    foundation_required: bool = True
    
    # Construction requirements
    construction_time_days: int = 14
    required_materials: List[Material] = field(default_factory=list)
    labor_hours_required: float = 120.0
    skilled_labor_percentage: float = 0.3  # Percentage requiring skilled workers
    
    # Economic factors
    base_cost: float = 15000.0
    maintenance_cost_annual: float = 1500.0
    insurance_cost_annual: float = 800.0
    property_tax_multiplier: float = 0.02
    
    # Operational characteristics
    capacity: Dict[str, float] = field(default_factory=dict)  # Storage, processing, etc.
    efficiency_bonus: Dict[str, float] = field(default_factory=dict)  # Production bonuses
    employee_capacity: int = 0  # Max employees who can work here
    power_consumption_kw: float = 10.0
    water_consumption_daily: float = 100.0  # Liters
    
    # Upgrade possibilities
    available_upgrades: List[str] = field(default_factory=list)
    max_upgrade_level: int = 3
    
    # Environmental requirements
    min_distance_from_other_buildings: float = 2.0
    requires_road_access: bool = True
    requires_power: bool = True
    requires_water: bool = True
    noise_level: float = 5.0  # 0-10 scale
    
    # Special features
    climate_controlled: bool = False
    fire_suppression: bool = False
    security_system: bool = False
    automated_systems: bool = False
    
    def get_total_construction_cost(self) -> float:
        """Calculate total construction cost including materials and labor"""
        material_cost = sum(material.get_total_cost() for material in self.required_materials)
        labor_cost = self.labor_hours_required * 25.0  # $25/hour average
        return self.base_cost + material_cost + labor_cost
    
    def get_annual_operating_cost(self) -> float:
        """Calculate annual operating costs"""
        return (self.maintenance_cost_annual + 
                self.insurance_cost_annual + 
                (self.base_cost * self.property_tax_multiplier))


@dataclass
class BuildingInstance:
    """Individual building instance on the farm"""
    building_id: str
    template: BuildingTemplate
    position: Tuple[int, int]
    rotation: int = 0  # 0, 90, 180, 270 degrees
    
    # Construction tracking
    status: BuildingStatus = BuildingStatus.PLANNED
    construction_started: Optional[int] = None  # Game time
    construction_completed: Optional[int] = None
    current_stage: ConstructionStage = ConstructionStage.FOUNDATION
    stage_progress: float = 0.0  # 0-1 within current stage
    overall_progress: float = 0.0  # 0-1 total construction progress
    
    # Workers and resources
    assigned_workers: List[str] = field(default_factory=list)  # Employee IDs
    materials_delivered: Dict[MaterialType, float] = field(default_factory=dict)
    materials_used: Dict[MaterialType, float] = field(default_factory=dict)
    
    # Operational data
    upgrade_level: int = 0
    installed_upgrades: List[str] = field(default_factory=list)
    current_capacity: Dict[str, float] = field(default_factory=dict)
    stored_items: Dict[str, float] = field(default_factory=dict)  # What's currently stored
    
    # Maintenance and condition
    condition: float = 1.0  # 0-1, affects efficiency
    last_maintenance: Optional[int] = None
    maintenance_due: bool = False
    repair_needed: bool = False
    
    # Economics
    total_cost_invested: float = 0.0
    annual_operating_costs: float = 0.0
    revenue_generated: float = 0.0
    
    # Utilities and infrastructure
    power_connected: bool = False
    water_connected: bool = False
    road_access: bool = False
    internet_connected: bool = False
    
    # Environmental tracking
    energy_consumption_today: float = 0.0
    water_consumption_today: float = 0.0
    waste_generated_today: float = 0.0
    
    def get_effective_capacity(self) -> Dict[str, float]:
        """Get capacity adjusted for condition and upgrades"""
        base_capacity = self.template.capacity.copy()
        
        # Upgrade bonuses
        upgrade_multiplier = 1.0 + (self.upgrade_level * 0.25)  # 25% per level
        
        # Condition affects capacity
        condition_multiplier = 0.5 + (self.condition * 0.5)  # 50-100% based on condition
        
        effective_capacity = {}
        for capacity_type, base_value in base_capacity.items():
            effective_capacity[capacity_type] = base_value * upgrade_multiplier * condition_multiplier
        
        return effective_capacity
    
    def get_efficiency_multiplier(self) -> float:
        """Get efficiency multiplier for operations in this building"""
        base_efficiency = 1.0
        
        # Condition affects efficiency
        condition_bonus = self.condition * 0.5  # Up to 50% bonus
        
        # Upgrade bonuses
        upgrade_bonus = self.upgrade_level * 0.15  # 15% per level
        
        # Utility bonuses
        utility_bonus = 0.0
        if self.power_connected:
            utility_bonus += 0.1
        if self.water_connected:
            utility_bonus += 0.05
        if self.internet_connected:
            utility_bonus += 0.05
        
        return base_efficiency + condition_bonus + upgrade_bonus + utility_bonus
    
    def can_start_construction(self) -> bool:
        """Check if construction can begin"""
        return (self.status == BuildingStatus.PLANNED and 
                len(self.assigned_workers) > 0 and
                self._has_required_materials())
    
    def _has_required_materials(self) -> bool:
        """Check if required materials are available"""
        for material in self.template.required_materials:
            delivered = self.materials_delivered.get(material.material_type, 0.0)
            if delivered < material.quantity * 0.1:  # Need at least 10% to start
                return False
        return True
    
    def update_construction(self, hours_passed: float, worker_efficiency: float = 1.0):
        """Update construction progress"""
        if self.status != BuildingStatus.UNDER_CONSTRUCTION:
            return
        
        if not self.assigned_workers:
            return
        
        # Calculate work progress based on workers and efficiency
        worker_count = len(self.assigned_workers)
        base_progress_per_hour = 1.0 / (self.template.construction_time_days * 24)
        
        # Worker efficiency affects progress
        efficiency_factor = worker_efficiency * min(1.5, worker_count * 0.3)  # Diminishing returns
        
        # Material availability affects progress
        material_factor = self._get_material_availability_factor()
        
        # Weather can affect construction
        weather_factor = self._get_weather_construction_factor()
        
        # Calculate actual progress
        progress_this_period = (base_progress_per_hour * hours_passed * 
                              efficiency_factor * material_factor * weather_factor)
        
        # Update stage progress
        stage_duration = self._get_current_stage_duration()
        stage_progress_per_hour = 1.0 / stage_duration
        self.stage_progress += stage_progress_per_hour * hours_passed * efficiency_factor
        
        # Check for stage advancement
        if self.stage_progress >= 1.0:
            self._advance_construction_stage()
        
        # Update overall progress
        self.overall_progress = min(1.0, self.overall_progress + progress_this_period)
        
        # Check for completion
        if self.overall_progress >= 1.0:
            self._complete_construction()
        
        # Consume materials
        self._consume_materials(progress_this_period)
    
    def _get_material_availability_factor(self) -> float:
        """Get material availability factor affecting construction speed"""
        if not self.template.required_materials:
            return 1.0
        
        availability_factors = []
        for material in self.template.required_materials:
            delivered = self.materials_delivered.get(material.material_type, 0.0)
            used = self.materials_used.get(material.material_type, 0.0)
            available = delivered - used
            required_now = material.quantity * (self.overall_progress + 0.1)  # Future need
            
            if available >= required_now:
                availability_factors.append(1.0)
            elif available > 0:
                availability_factors.append(available / required_now)
            else:
                availability_factors.append(0.1)  # Minimal progress without materials
        
        return sum(availability_factors) / len(availability_factors)
    
    def _get_weather_construction_factor(self) -> float:
        """Get weather factor affecting construction"""
        current_weather = get_time_manager().get_current_weather()
        
        weather_factors = {
            WeatherType.CLEAR: 1.0,
            WeatherType.PARTLY_CLOUDY: 1.0,
            WeatherType.CLOUDY: 0.9,
            WeatherType.LIGHT_RAIN: 0.7,
            WeatherType.HEAVY_RAIN: 0.3,
            WeatherType.STORM: 0.1,
            WeatherType.EXTREME_HEAT: 0.6,
            WeatherType.EXTREME_COLD: 0.5,
            WeatherType.SNOW: 0.4,
            WeatherType.FOG: 0.8
        }
        
        return weather_factors.get(current_weather.weather_type, 1.0)
    
    def _get_current_stage_duration(self) -> float:
        """Get duration in hours for current construction stage"""
        total_hours = self.template.construction_time_days * 24
        stage_percentages = {
            ConstructionStage.FOUNDATION: 0.20,
            ConstructionStage.FRAMING: 0.15,
            ConstructionStage.WALLS: 0.20,
            ConstructionStage.ROOFING: 0.10,
            ConstructionStage.UTILITIES: 0.15,
            ConstructionStage.INTERIOR: 0.10,
            ConstructionStage.FINISHING: 0.08,
            ConstructionStage.INSPECTION: 0.02
        }
        
        percentage = stage_percentages.get(self.current_stage, 0.1)
        return total_hours * percentage
    
    def _advance_construction_stage(self):
        """Advance to the next construction stage"""
        stages = list(ConstructionStage)
        current_index = stages.index(self.current_stage)
        
        if current_index < len(stages) - 1:
            self.current_stage = stages[current_index + 1]
            self.stage_progress = 0.0
    
    def _complete_construction(self):
        """Complete building construction"""
        self.status = BuildingStatus.OPERATIONAL
        self.construction_completed = get_time_manager().get_current_time().total_minutes
        self.condition = 1.0  # New building in perfect condition
        self.current_capacity = self.template.capacity.copy()
        
        # Initialize utility connections (would be more complex in real system)
        self.power_connected = True
        self.water_connected = True
        self.road_access = True
    
    def _consume_materials(self, progress_amount: float):
        """Consume materials based on construction progress"""
        for material in self.template.required_materials:
            material_type = material.material_type
            consumption_rate = material.quantity * progress_amount
            
            if material_type not in self.materials_used:
                self.materials_used[material_type] = 0.0
            
            available = self.materials_delivered.get(material_type, 0.0) - self.materials_used[material_type]
            consumed = min(consumption_rate, available)
            self.materials_used[material_type] += consumed


class BuildingSystem(System):
    """Comprehensive building and infrastructure management system"""
    
    def __init__(self):
        super().__init__()
        self.system_name = "building_system"
        
        # Core system references
        self.event_system = get_event_system()
        self.time_manager = get_time_manager()
        self.config_manager = get_config_manager()
        self.economy_system = get_economy_system()
        self.employee_system = get_employee_system()
        self.crop_system = get_crop_system()
        
        # Building data storage
        self.building_templates: Dict[str, BuildingTemplate] = {}
        self.active_buildings: Dict[str, BuildingInstance] = {}  # building_id -> BuildingInstance
        self.construction_queue: List[str] = []  # Planned buildings
        
        # Grid and placement management
        self.grid_size: Tuple[int, int] = (16, 16)
        self.occupied_positions: Set[Tuple[int, int]] = set()
        self.building_positions: Dict[Tuple[int, int], str] = {}  # position -> building_id
        
        # Infrastructure networks
        self.power_grid: Dict[Tuple[int, int], bool] = {}
        self.water_network: Dict[Tuple[int, int], bool] = {}
        self.road_network: Set[Tuple[int, int]] = set()
        self.communication_network: Dict[Tuple[int, int], bool] = {}
        
        # Material and supply management
        self.material_inventory: Dict[MaterialType, float] = {}
        self.material_suppliers: Dict[MaterialType, List[str]] = {}
        self.pending_deliveries: List[Dict[str, Any]] = []
        
        # Construction management
        self.construction_crews: Dict[str, List[str]] = {}  # crew_id -> employee_ids
        self.active_construction_sites: Set[str] = set()  # building_ids under construction
        
        # Economic tracking
        self.total_construction_investment: float = 0.0
        self.annual_building_costs: float = 0.0
        self.building_revenue: float = 0.0
        self.maintenance_budget: float = 50000.0
        
        # Performance tracking
        self.buildings_constructed: int = 0
        self.buildings_demolished: int = 0
        self.total_storage_capacity: float = 0.0
        self.total_processing_capacity: float = 0.0
        
        # Configuration
        self.construction_update_frequency = 3600.0  # Update every hour
        self.last_construction_update = 0.0
        self.auto_material_ordering = True
        self.quality_control_enabled = True
    
    async def initialize(self):
        """Initialize the building system"""
        # Load configuration
        await self._load_building_configuration()
        
        # Initialize building templates
        await self._initialize_building_templates()
        
        # Initialize infrastructure networks
        await self._initialize_infrastructure()
        
        # Initialize material suppliers
        await self._initialize_material_suppliers()
        
        # Subscribe to time events
        self.event_system.subscribe('time_hour_passed', self._on_hour_passed)
        self.event_system.subscribe('time_day_passed', self._on_day_passed)
        self.event_system.subscribe('time_season_changed', self._on_season_changed)
        self.event_system.subscribe('weather_changed', self._on_weather_changed)
        
        # Subscribe to game events
        self.event_system.subscribe('employee_hired', self._on_employee_hired)
        self.event_system.subscribe('crop_harvested', self._on_crop_harvested)
        
        self.logger.info("Building System initialized successfully")
    
    async def _load_building_configuration(self):
        """Load building system configuration"""
        try:
            building_config = self.config_manager.get_section('buildings')
            
            # Load system parameters
            self.construction_update_frequency = building_config.get('construction_update_frequency', 3600.0)
            self.auto_material_ordering = building_config.get('auto_material_ordering', True)
            self.quality_control_enabled = building_config.get('quality_control_enabled', True)
            self.maintenance_budget = building_config.get('maintenance_budget', 50000.0)
            
            # Load grid configuration
            grid_config = building_config.get('grid', {})
            self.grid_size = tuple(grid_config.get('size', [16, 16]))
            
        except Exception as e:
            self.logger.warning(f"Failed to load building configuration: {e}")
    
    async def _initialize_building_templates(self):
        """Initialize building templates for all available building types"""
        # Storage Buildings
        templates = [
            BuildingTemplate(
                building_type=BuildingType.GRAIN_SILO,
                name="Grain Storage Silo",
                description="Large capacity grain storage with automated loading/unloading",
                category="storage",
                size=(3, 3),
                height=20.0,
                construction_time_days=21,
                required_materials=[
                    Material(MaterialType.CONCRETE, 15.0, "cubic_meters", 150.0),
                    Material(MaterialType.STEEL, 8.0, "tons", 800.0),
                    Material(MaterialType.ELECTRICAL, 5.0, "units", 200.0),
                    Material(MaterialType.HARDWARE, 3.0, "units", 150.0)
                ],
                labor_hours_required=280.0,
                skilled_labor_percentage=0.4,
                base_cost=45000.0,
                maintenance_cost_annual=2500.0,
                capacity={"grain_storage": 500.0},  # tons
                power_consumption_kw=15.0,
                available_upgrades=["capacity_expansion", "automated_handling", "quality_monitoring"],
                max_upgrade_level=3
            ),
            
            BuildingTemplate(
                building_type=BuildingType.WAREHOUSE,
                name="General Storage Warehouse",
                description="Multi-purpose storage facility for equipment and supplies",
                category="storage",
                size=(4, 6),
                height=8.0,
                construction_time_days=18,
                required_materials=[
                    Material(MaterialType.STEEL, 12.0, "tons", 800.0),
                    Material(MaterialType.CONCRETE, 8.0, "cubic_meters", 150.0),
                    Material(MaterialType.ROOFING, 24.0, "square_meters", 45.0),
                    Material(MaterialType.ELECTRICAL, 3.0, "units", 200.0)
                ],
                labor_hours_required=220.0,
                base_cost=35000.0,
                capacity={"general_storage": 200.0, "equipment_storage": 50.0},
                employee_capacity=8,
                available_upgrades=["climate_control", "security_system", "expanded_capacity"]
            ),
            
            BuildingTemplate(
                building_type=BuildingType.COLD_STORAGE,
                name="Refrigerated Cold Storage",
                description="Temperature-controlled storage for perishable crops",
                category="storage",
                size=(3, 4),
                height=6.0,
                construction_time_days=25,
                required_materials=[
                    Material(MaterialType.CONCRETE, 10.0, "cubic_meters", 150.0),
                    Material(MaterialType.STEEL, 6.0, "tons", 800.0),
                    Material(MaterialType.INSULATION, 15.0, "cubic_meters", 80.0),
                    Material(MaterialType.ELECTRICAL, 8.0, "units", 200.0)
                ],
                labor_hours_required=320.0,
                skilled_labor_percentage=0.6,
                base_cost=55000.0,
                maintenance_cost_annual=4500.0,
                capacity={"cold_storage": 150.0},  # tons
                power_consumption_kw=35.0,
                climate_controlled=True,
                available_upgrades=["temperature_zones", "automated_inventory", "expansion"]
            ),
            
            # Processing Buildings
            BuildingTemplate(
                building_type=BuildingType.GRAIN_MILL,
                name="Grain Processing Mill",
                description="Facility for processing grains into flour and feed",
                category="processing",
                size=(4, 5),
                height=12.0,
                construction_time_days=35,
                required_materials=[
                    Material(MaterialType.CONCRETE, 20.0, "cubic_meters", 150.0),
                    Material(MaterialType.STEEL, 15.0, "tons", 800.0),
                    Material(MaterialType.ELECTRICAL, 12.0, "units", 200.0),
                    Material(MaterialType.HARDWARE, 8.0, "units", 150.0)
                ],
                labor_hours_required=450.0,
                skilled_labor_percentage=0.7,
                base_cost=85000.0,
                maintenance_cost_annual=6500.0,
                capacity={"grain_processing": 100.0},  # tons per day
                efficiency_bonus={"grain_value": 1.8},  # 80% value increase
                employee_capacity=12,
                power_consumption_kw=75.0,
                noise_level=8.0,
                available_upgrades=["automation", "quality_control", "capacity_expansion"]
            ),
            
            # Utility Buildings
            BuildingTemplate(
                building_type=BuildingType.GENERATOR,
                name="Backup Power Generator",
                description="Diesel generator for backup power and peak load management",
                category="utility",
                size=(2, 3),
                height=4.0,
                construction_time_days=8,
                required_materials=[
                    Material(MaterialType.CONCRETE, 4.0, "cubic_meters", 150.0),
                    Material(MaterialType.STEEL, 3.0, "tons", 800.0),
                    Material(MaterialType.ELECTRICAL, 6.0, "units", 200.0)
                ],
                labor_hours_required=80.0,
                skilled_labor_percentage=0.8,
                base_cost=25000.0,
                maintenance_cost_annual=3000.0,
                capacity={"power_generation": 150.0},  # kW
                noise_level=9.0,
                requires_road_access=True,
                available_upgrades=["fuel_efficiency", "noise_reduction", "remote_monitoring"]
            ),
            
            BuildingTemplate(
                building_type=BuildingType.WATER_TOWER,
                name="Water Storage Tower",
                description="Elevated water storage for farm-wide water pressure",
                category="utility",
                size=(2, 2),
                height=25.0,
                construction_time_days=12,
                required_materials=[
                    Material(MaterialType.CONCRETE, 8.0, "cubic_meters", 150.0),
                    Material(MaterialType.STEEL, 5.0, "tons", 800.0),
                    Material(MaterialType.PLUMBING, 3.0, "units", 300.0)
                ],
                labor_hours_required=150.0,
                skilled_labor_percentage=0.5,
                base_cost=30000.0,
                maintenance_cost_annual=1800.0,
                capacity={"water_storage": 50000.0},  # liters
                available_upgrades=["capacity_expansion", "pressure_system", "filtration"]
            ),
            
            # Agricultural Buildings
            BuildingTemplate(
                building_type=BuildingType.GREENHOUSE,
                name="Climate-Controlled Greenhouse",
                description="Year-round growing facility with environmental controls",
                category="agricultural",
                size=(6, 8),
                height=4.0,
                construction_time_days=20,
                required_materials=[
                    Material(MaterialType.STEEL, 8.0, "tons", 800.0),
                    Material(MaterialType.CONCRETE, 6.0, "cubic_meters", 150.0),
                    Material(MaterialType.ELECTRICAL, 10.0, "units", 200.0),
                    Material(MaterialType.PLUMBING, 4.0, "units", 300.0)
                ],
                labor_hours_required=240.0,
                skilled_labor_percentage=0.6,
                base_cost=65000.0,
                maintenance_cost_annual=5500.0,
                capacity={"growing_area": 48.0},  # square meters
                efficiency_bonus={"crop_yield": 2.5, "crop_quality": 1.4},
                employee_capacity=6,
                power_consumption_kw=25.0,
                water_consumption_daily=500.0,
                climate_controlled=True,
                available_upgrades=["automation", "hydroponic_system", "expansion"]
            ),
            
            # Residential Buildings
            BuildingTemplate(
                building_type=BuildingType.EMPLOYEE_HOUSING,
                name="Employee Housing Unit",
                description="Comfortable housing for farm workers",
                category="residential",
                size=(3, 4),
                height=6.0,
                construction_time_days=16,
                required_materials=[
                    Material(MaterialType.LUMBER, 8.0, "cubic_meters", 400.0),
                    Material(MaterialType.CONCRETE, 5.0, "cubic_meters", 150.0),
                    Material(MaterialType.ROOFING, 12.0, "square_meters", 45.0),
                    Material(MaterialType.ELECTRICAL, 4.0, "units", 200.0),
                    Material(MaterialType.PLUMBING, 3.0, "units", 300.0),
                    Material(MaterialType.INSULATION, 6.0, "cubic_meters", 80.0)
                ],
                labor_hours_required=200.0,
                base_cost=40000.0,
                maintenance_cost_annual=2200.0,
                capacity={"housing_units": 4.0},  # Number of employees
                efficiency_bonus={"employee_satisfaction": 1.3, "employee_retention": 1.5},
                power_consumption_kw=12.0,
                water_consumption_daily=400.0,
                available_upgrades=["comfort_improvements", "energy_efficiency", "additional_units"]
            )
        ]
        
        for template in templates:
            self.building_templates[template.building_type.value] = template
        
        self.logger.info(f"Initialized {len(templates)} building templates")
    
    async def _initialize_infrastructure(self):
        """Initialize basic infrastructure networks"""
        # Initialize basic road network (farm roads)
        for x in range(self.grid_size[0]):
            if x % 4 == 0:  # Roads every 4 tiles
                for y in range(self.grid_size[1]):
                    self.road_network.add((x, y))
        
        for y in range(self.grid_size[1]):
            if y % 4 == 0:
                for x in range(self.grid_size[0]):
                    self.road_network.add((x, y))
        
        # Initialize basic power and water (would be more complex in real system)
        for position in self.road_network:
            self.power_grid[position] = True
            self.water_network[position] = True
        
        self.logger.info("Initialized basic infrastructure networks")
    
    async def _initialize_material_suppliers(self):
        """Initialize material suppliers and pricing"""
        suppliers = {
            MaterialType.CONCRETE: ["Regional Concrete Co.", "BuildMix Suppliers"],
            MaterialType.STEEL: ["Steel Dynamics", "National Steel Supply"],
            MaterialType.LUMBER: ["Timber Works", "Forest Products Inc."],
            MaterialType.ELECTRICAL: ["ElectroSupply", "Power Components Ltd."],
            MaterialType.PLUMBING: ["Pipe & Fittings Co.", "Hydro Systems"],
            MaterialType.ROOFING: ["Roof Masters", "Weather Guard Supply"],
            MaterialType.INSULATION: ["Thermal Solutions", "Energy Saver Materials"],
            MaterialType.HARDWARE: ["Farm Hardware Co.", "Industrial Supply"],
            MaterialType.BRICK: ["Brick & Stone Ltd.", "Masonry Supply"],
            MaterialType.PAINT: ["Color Solutions", "Protective Coatings"]
        }
        
        for material_type, supplier_list in suppliers.items():
            self.material_suppliers[material_type] = supplier_list
            self.material_inventory[material_type] = 0.0
    
    async def start_construction(self, building_type: str, position: Tuple[int, int], 
                               rotation: int = 0) -> Optional[str]:
        """Start construction of a new building"""
        if building_type not in self.building_templates:
            self.logger.error(f"Unknown building type: {building_type}")
            return None
        
        template = self.building_templates[building_type]
        
        # Check if position is valid and available
        if not self._is_position_valid(position, template.size, rotation):
            self.logger.warning(f"Invalid position {position} for {building_type}")
            return None
        
        # Check construction costs
        total_cost = template.get_total_construction_cost()
        if self.economy_system.player_cash < total_cost * 0.3:  # Need 30% upfront
            self.logger.warning(f"Insufficient funds for {building_type} construction")
            return None
        
        # Create building instance
        building_id = f"building_{int(time.time())}_{random.randint(1000, 9999)}"
        
        building = BuildingInstance(
            building_id=building_id,
            template=template,
            position=position,
            rotation=rotation
        )
        
        # Reserve the position
        self._occupy_positions(position, template.size, rotation, building_id)
        
        # Process initial payment (30% down payment)
        down_payment = total_cost * 0.3
        self.economy_system.player_cash -= down_payment
        self.economy_system.total_expenses += down_payment
        building.total_cost_invested = down_payment
        
        # Add to tracking
        self.active_buildings[building_id] = building
        self.construction_queue.append(building_id)
        
        # Order materials
        await self._order_construction_materials(building_id)
        
        # Emit construction started event
        self.event_system.emit('construction_started', {
            'building_id': building_id,
            'building_type': building_type,
            'building_name': template.name,
            'position': position,
            'total_cost': total_cost,
            'down_payment': down_payment
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Started construction of {template.name} at {position}")
        return building_id
    
    def _is_position_valid(self, position: Tuple[int, int], size: Tuple[int, int], rotation: int) -> bool:
        """Check if a building position is valid"""
        x, y = position
        width, height = size
        
        # Adjust size for rotation
        if rotation in [90, 270]:
            width, height = height, width
        
        # Check grid bounds
        if (x + width > self.grid_size[0] or y + height > self.grid_size[1] or
            x < 0 or y < 0):
            return False
        
        # Check for overlapping buildings
        for dx in range(width):
            for dy in range(height):
                check_pos = (x + dx, y + dy)
                if check_pos in self.occupied_positions:
                    return False
        
        return True
    
    def _occupy_positions(self, position: Tuple[int, int], size: Tuple[int, int], 
                         rotation: int, building_id: str):
        """Mark positions as occupied by a building"""
        x, y = position
        width, height = size
        
        # Adjust size for rotation
        if rotation in [90, 270]:
            width, height = height, width
        
        for dx in range(width):
            for dy in range(height):
                pos = (x + dx, y + dy)
                self.occupied_positions.add(pos)
                self.building_positions[pos] = building_id
    
    async def _order_construction_materials(self, building_id: str):
        """Order materials for construction"""
        if building_id not in self.active_buildings:
            return
        
        building = self.active_buildings[building_id]
        template = building.template
        
        total_material_cost = 0.0
        
        for material in template.required_materials:
            # Calculate delivery timing
            delivery_time = self.time_manager.get_current_time().total_minutes + (material.delivery_time_days * 1440)
            
            # Add to pending deliveries
            delivery = {
                'building_id': building_id,
                'material_type': material.material_type,
                'quantity': material.quantity,
                'cost': material.get_total_cost(),
                'delivery_time': delivery_time,
                'supplier': material.supplier
            }
            
            self.pending_deliveries.append(delivery)
            total_material_cost += material.get_total_cost()
        
        # Process material payment
        self.economy_system.player_cash -= total_material_cost
        self.economy_system.total_expenses += total_material_cost
        building.total_cost_invested += total_material_cost
        
        self.logger.info(f"Ordered materials for {building_id}: ${total_material_cost:.2f}")
    
    async def assign_construction_workers(self, building_id: str, employee_ids: List[str]) -> bool:
        """Assign workers to a construction project"""
        if building_id not in self.active_buildings:
            return False
        
        building = self.active_buildings[building_id]
        
        # Validate employees exist and are available
        valid_employees = []
        for employee_id in employee_ids:
            employee_info = self.employee_system.get_employee_info(employee_id)
            if employee_info and employee_info['current_state'] != 'unavailable':
                valid_employees.append(employee_id)
        
        if not valid_employees:
            return False
        
        # Assign workers
        building.assigned_workers = valid_employees
        
        # Start construction if not already started
        if building.status == BuildingStatus.PLANNED and building.can_start_construction():
            building.status = BuildingStatus.UNDER_CONSTRUCTION
            building.construction_started = self.time_manager.get_current_time().total_minutes
            self.active_construction_sites.add(building_id)
            
            # Emit construction began event
            self.event_system.emit('construction_began', {
                'building_id': building_id,
                'worker_count': len(valid_employees),
                'worker_ids': valid_employees
            }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Assigned {len(valid_employees)} workers to {building_id}")
        return True
    
    async def upgrade_building(self, building_id: str, upgrade_type: str) -> bool:
        """Upgrade an existing building"""
        if building_id not in self.active_buildings:
            return False
        
        building = self.active_buildings[building_id]
        
        if building.status != BuildingStatus.OPERATIONAL:
            self.logger.warning(f"Building {building_id} is not operational")
            return False
        
        if upgrade_type not in building.template.available_upgrades:
            self.logger.warning(f"Upgrade {upgrade_type} not available for this building")
            return False
        
        if building.upgrade_level >= building.template.max_upgrade_level:
            self.logger.warning(f"Building {building_id} is at maximum upgrade level")
            return False
        
        # Calculate upgrade cost
        base_cost = building.template.base_cost
        upgrade_cost = base_cost * 0.3 * (building.upgrade_level + 1)  # Increasing cost per level
        
        if self.economy_system.player_cash < upgrade_cost:
            self.logger.warning(f"Insufficient funds for upgrade: ${upgrade_cost:.2f}")
            return False
        
        # Process upgrade
        self.economy_system.player_cash -= upgrade_cost
        self.economy_system.total_expenses += upgrade_cost
        building.total_cost_invested += upgrade_cost
        
        building.upgrade_level += 1
        building.installed_upgrades.append(upgrade_type)
        
        # Apply upgrade effects
        self._apply_upgrade_effects(building, upgrade_type)
        
        # Emit upgrade event
        self.event_system.emit('building_upgraded', {
            'building_id': building_id,
            'upgrade_type': upgrade_type,
            'new_level': building.upgrade_level,
            'cost': upgrade_cost
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Upgraded {building_id} with {upgrade_type} for ${upgrade_cost:.2f}")
        return True
    
    def _apply_upgrade_effects(self, building: BuildingInstance, upgrade_type: str):
        """Apply effects of a specific upgrade"""
        if upgrade_type == "capacity_expansion":
            for capacity_type in building.current_capacity:
                building.current_capacity[capacity_type] *= 1.5
        elif upgrade_type == "automated_handling":
            building.template.efficiency_bonus["automation"] = 1.3
        elif upgrade_type == "quality_monitoring":
            building.template.efficiency_bonus["quality_control"] = 1.2
        elif upgrade_type == "climate_control":
            building.template.climate_controlled = True
            building.template.efficiency_bonus["climate"] = 1.25
        elif upgrade_type == "security_system":
            building.template.security_system = True
        elif upgrade_type == "energy_efficiency":
            building.template.power_consumption_kw *= 0.7
    
    def get_building_info(self, building_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a building"""
        if building_id not in self.active_buildings:
            return None
        
        building = self.active_buildings[building_id]
        
        return {
            'building_id': building_id,
            'building_type': building.template.building_type.value,
            'name': building.template.name,
            'category': building.template.category,
            'position': building.position,
            'size': building.template.size,
            'rotation': building.rotation,
            'status': building.status.value,
            'construction_progress': building.overall_progress,
            'current_stage': building.current_stage.value if building.status == BuildingStatus.UNDER_CONSTRUCTION else None,
            'condition': building.condition,
            'upgrade_level': building.upgrade_level,
            'installed_upgrades': building.installed_upgrades,
            'capacity': building.get_effective_capacity(),
            'stored_items': building.stored_items,
            'assigned_workers': len(building.assigned_workers),
            'efficiency_multiplier': building.get_efficiency_multiplier(),
            'annual_operating_cost': building.template.get_annual_operating_cost(),
            'total_investment': building.total_cost_invested,
            'utilities': {
                'power_connected': building.power_connected,
                'water_connected': building.water_connected,
                'road_access': building.road_access,
                'internet_connected': building.internet_connected
            },
            'maintenance_due': building.maintenance_due,
            'repair_needed': building.repair_needed
        }
    
    def get_all_buildings(self) -> List[Dict[str, Any]]:
        """Get information for all buildings"""
        return [self.get_building_info(building_id) for building_id in self.active_buildings.keys()]
    
    def get_available_building_types(self) -> List[Dict[str, Any]]:
        """Get all available building types and their characteristics"""
        building_types = []
        for template in self.building_templates.values():
            building_types.append({
                'building_type': template.building_type.value,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'size': template.size,
                'construction_time_days': template.construction_time_days,
                'total_cost': template.get_total_construction_cost(),
                'annual_operating_cost': template.get_annual_operating_cost(),
                'capacity': template.capacity,
                'efficiency_bonus': template.efficiency_bonus,
                'power_consumption': template.power_consumption_kw,
                'available_upgrades': template.available_upgrades,
                'max_upgrade_level': template.max_upgrade_level
            })
        return building_types
    
    async def store_items(self, building_id: str, item_type: str, quantity: float) -> bool:
        """Store items in a building"""
        if building_id not in self.active_buildings:
            return False
        
        building = self.active_buildings[building_id]
        
        if building.status != BuildingStatus.OPERATIONAL:
            return False
        
        # Check storage capacity
        capacity = building.get_effective_capacity()
        storage_key = self._get_storage_key_for_item(item_type)
        
        if storage_key not in capacity:
            return False
        
        current_stored = sum(building.stored_items.values())
        available_capacity = capacity[storage_key] - current_stored
        
        if quantity > available_capacity:
            quantity = available_capacity  # Store what fits
        
        if quantity <= 0:
            return False
        
        # Store the items
        if item_type not in building.stored_items:
            building.stored_items[item_type] = 0.0
        building.stored_items[item_type] += quantity
        
        # Emit storage event
        self.event_system.emit('items_stored', {
            'building_id': building_id,
            'item_type': item_type,
            'quantity_stored': quantity,
            'total_stored': building.stored_items[item_type]
        }, priority=EventPriority.NORMAL)
        
        return True
    
    def _get_storage_key_for_item(self, item_type: str) -> str:
        """Get the appropriate storage capacity key for an item type"""
        storage_mappings = {
            'corn': 'grain_storage',
            'wheat': 'grain_storage',
            'soybeans': 'grain_storage',
            'tomatoes': 'cold_storage',
            'potatoes': 'general_storage',
            'equipment': 'equipment_storage'
        }
        return storage_mappings.get(item_type, 'general_storage')
    
    async def update(self, delta_time: float):
        """Update building system"""
        current_time = time.time()
        
        # Update construction progress
        if current_time - self.last_construction_update >= self.construction_update_frequency:
            await self._update_construction_progress(self.construction_update_frequency / 3600.0)
            self.last_construction_update = current_time
        
        # Process material deliveries
        await self._process_material_deliveries()
        
        # Update building conditions
        await self._update_building_conditions()
    
    async def _update_construction_progress(self, hours_passed: float):
        """Update construction progress for all active construction sites"""
        for building_id in list(self.active_construction_sites):
            if building_id not in self.active_buildings:
                self.active_construction_sites.remove(building_id)
                continue
            
            building = self.active_buildings[building_id]
            
            if building.status != BuildingStatus.UNDER_CONSTRUCTION:
                self.active_construction_sites.remove(building_id)
                continue
            
            # Calculate worker efficiency
            worker_efficiency = self._calculate_worker_efficiency(building)
            
            # Update construction
            building.update_construction(hours_passed, worker_efficiency)
            
            # Check if construction completed
            if building.status == BuildingStatus.OPERATIONAL:
                await self._complete_building_construction(building_id)
    
    def _calculate_worker_efficiency(self, building: BuildingInstance) -> float:
        """Calculate overall worker efficiency for construction"""
        if not building.assigned_workers:
            return 0.0
        
        total_efficiency = 0.0
        worker_count = len(building.assigned_workers)
        
        for employee_id in building.assigned_workers:
            employee_info = self.employee_system.get_employee_info(employee_id)
            if employee_info:
                # Base efficiency from employee condition
                base_efficiency = employee_info['needs']['effectiveness']
                
                # Skill bonus for construction
                construction_skills = ['maintenance', 'equipment_operation']
                skill_bonus = 1.0
                for skill in construction_skills:
                    if skill in employee_info['skills']:
                        skill_bonus += employee_info['skills'][skill]['efficiency'] * 0.1
                
                total_efficiency += base_efficiency * skill_bonus
        
        # Average efficiency with team coordination factor
        avg_efficiency = total_efficiency / worker_count
        coordination_factor = min(1.2, 1.0 + (worker_count - 1) * 0.05)  # Small bonus for teams
        
        return avg_efficiency * coordination_factor
    
    async def _complete_building_construction(self, building_id: str):
        """Handle completion of building construction"""
        building = self.active_buildings[building_id]
        
        # Final payment (remaining 70%)
        total_cost = building.template.get_total_construction_cost()
        final_payment = total_cost * 0.7
        self.economy_system.player_cash -= final_payment
        self.economy_system.total_expenses += final_payment
        building.total_cost_invested += final_payment
        
        # Update tracking
        self.buildings_constructed += 1
        self.total_construction_investment += building.total_cost_invested
        
        # Update capacity tracking
        capacity = building.get_effective_capacity()
        if 'grain_storage' in capacity or 'general_storage' in capacity or 'cold_storage' in capacity:
            self.total_storage_capacity += sum(capacity.values())
        if 'grain_processing' in capacity:
            self.total_processing_capacity += capacity['grain_processing']
        
        # Remove workers from construction
        building.assigned_workers.clear()
        
        # Emit construction completed event
        self.event_system.emit('construction_completed', {
            'building_id': building_id,
            'building_name': building.template.name,
            'total_cost': building.total_cost_invested,
            'construction_time_days': (building.construction_completed - building.construction_started) / 1440.0
        }, priority=EventPriority.HIGH)
        
        self.logger.info(f"Completed construction of {building.template.name}")
    
    async def _process_material_deliveries(self):
        """Process pending material deliveries"""
        current_time = self.time_manager.get_current_time().total_minutes
        
        completed_deliveries = []
        
        for delivery in self.pending_deliveries:
            if current_time >= delivery['delivery_time']:
                building_id = delivery['building_id']
                
                if building_id in self.active_buildings:
                    building = self.active_buildings[building_id]
                    material_type = delivery['material_type']
                    quantity = delivery['quantity']
                    
                    # Add materials to building
                    if material_type not in building.materials_delivered:
                        building.materials_delivered[material_type] = 0.0
                    building.materials_delivered[material_type] += quantity
                    
                    # Add to general inventory
                    self.material_inventory[material_type] += quantity
                    
                    # Emit delivery event
                    self.event_system.emit('materials_delivered', {
                        'building_id': building_id,
                        'material_type': material_type.value,
                        'quantity': quantity,
                        'supplier': delivery['supplier']
                    }, priority=EventPriority.NORMAL)
                
                completed_deliveries.append(delivery)
        
        # Remove completed deliveries
        for delivery in completed_deliveries:
            self.pending_deliveries.remove(delivery)
    
    async def _update_building_conditions(self):
        """Update condition and maintenance status of buildings"""
        for building in self.active_buildings.values():
            if building.status == BuildingStatus.OPERATIONAL:
                # Natural condition degradation
                degradation_rate = 0.0001  # Very slow degradation
                building.condition = max(0.0, building.condition - degradation_rate)
                
                # Check maintenance requirements
                if building.last_maintenance:
                    time_since_maintenance = (self.time_manager.get_current_time().total_minutes - 
                                           building.last_maintenance) / 1440.0  # Days
                    if time_since_maintenance > 180:  # 6 months
                        building.maintenance_due = True
                
                # Check repair requirements
                if building.condition < 0.7:
                    building.repair_needed = True
    
    # Event handlers
    async def _on_hour_passed(self, event_data):
        """Handle hourly updates"""
        # Update utility consumption
        for building in self.active_buildings.values():
            if building.status == BuildingStatus.OPERATIONAL:
                building.energy_consumption_today += building.template.power_consumption_kw
                building.water_consumption_today += building.template.water_consumption_daily / 24.0
    
    async def _on_day_passed(self, event_data):
        """Handle daily updates"""
        # Reset daily consumption tracking
        for building in self.active_buildings.values():
            building.energy_consumption_today = 0.0
            building.water_consumption_today = 0.0
            building.waste_generated_today = 0.0
        
        # Process daily building costs
        daily_costs = 0.0
        for building in self.active_buildings.values():
            if building.status == BuildingStatus.OPERATIONAL:
                daily_cost = building.template.get_annual_operating_cost() / 365.0
                daily_costs += daily_cost
        
        self.annual_building_costs += daily_costs * 365.0
        self.economy_system.player_cash -= daily_costs
        self.economy_system.total_expenses += daily_costs
    
    async def _on_season_changed(self, event_data):
        """Handle seasonal changes affecting buildings"""
        new_season = Season(event_data.get('new_season'))
        
        # Seasonal effects on construction
        if new_season == Season.WINTER:
            # Construction slower in winter
            for building in self.active_buildings.values():
                if building.status == BuildingStatus.UNDER_CONSTRUCTION:
                    # Extend construction time slightly
                    pass
    
    async def _on_weather_changed(self, event_data):
        """Handle weather changes affecting construction and buildings"""
        weather_type = WeatherType(event_data.get('weather_type'))
        
        # Severe weather affects construction
        if weather_type in [WeatherType.STORM, WeatherType.EXTREME_COLD, WeatherType.HEAVY_RAIN]:
            for building in self.active_buildings.values():
                if building.status == BuildingStatus.UNDER_CONSTRUCTION:
                    # Construction may be delayed
                    pass
    
    async def _on_employee_hired(self, event_data):
        """Handle new employee hiring for housing needs"""
        # Check if employee housing is available
        housing_capacity = 0
        for building in self.active_buildings.values():
            if (building.template.building_type == BuildingType.EMPLOYEE_HOUSING and 
                building.status == BuildingStatus.OPERATIONAL):
                housing_capacity += building.get_effective_capacity().get('housing_units', 0)
        
        current_employees = len(self.employee_system.get_all_employees())
        
        if current_employees > housing_capacity:
            # Suggest building more housing
            self.event_system.emit('housing_shortage', {
                'current_employees': current_employees,
                'housing_capacity': housing_capacity,
                'shortage': current_employees - housing_capacity
            }, priority=EventPriority.HIGH)
    
    async def _on_crop_harvested(self, event_data):
        """Handle crop harvest for storage needs"""
        crop_type = event_data.get('variety_name', '').lower()
        yield_kg = event_data.get('yield_kg', 0)
        
        if yield_kg > 0:
            # Try to find appropriate storage
            stored = False
            for building in self.active_buildings.values():
                if building.status == BuildingStatus.OPERATIONAL:
                    if await self.store_items(building.building_id, crop_type, yield_kg):
                        stored = True
                        break
            
            if not stored:
                # Suggest building more storage
                self.event_system.emit('storage_shortage', {
                    'crop_type': crop_type,
                    'quantity_unstored': yield_kg
                }, priority=EventPriority.HIGH)
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive building system summary"""
        buildings_by_type = {}
        buildings_by_status = {}
        
        for building in self.active_buildings.values():
            building_type = building.template.building_type.value
            status = building.status.value
            
            buildings_by_type[building_type] = buildings_by_type.get(building_type, 0) + 1
            buildings_by_status[status] = buildings_by_status.get(status, 0) + 1
        
        return {
            'total_buildings': len(self.active_buildings),
            'buildings_constructed': self.buildings_constructed,
            'buildings_by_type': buildings_by_type,
            'buildings_by_status': buildings_by_status,
            'active_construction_sites': len(self.active_construction_sites),
            'total_storage_capacity': self.total_storage_capacity,
            'total_processing_capacity': self.total_processing_capacity,
            'total_construction_investment': self.total_construction_investment,
            'annual_building_costs': self.annual_building_costs,
            'material_inventory': {material.value: quantity for material, quantity in self.material_inventory.items()},
            'pending_deliveries': len(self.pending_deliveries),
            'road_network_size': len(self.road_network)
        }
    
    async def shutdown(self):
        """Shutdown the building system"""
        self.logger.info("Shutting down Building System")
        
        # Save final building system state
        final_summary = self.get_system_summary()
        
        self.event_system.emit('building_system_shutdown', {
            'final_summary': final_summary,
            'total_buildings': len(self.active_buildings)
        }, priority=EventPriority.HIGH)
        
        self.logger.info("Building System shutdown complete")


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