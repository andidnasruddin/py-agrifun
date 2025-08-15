"""
Tractor System - Comprehensive Tractor Management for AgriFun Agricultural Simulation

This system provides realistic tractor simulation including multiple tractor types,
operational capabilities, fuel consumption, maintenance scheduling, and economic
modeling. Integrates with the Equipment System and supports implement attachments.

Key Features:
- Multiple tractor categories (Compact, Utility, Row Crop, 4WD)
- Realistic engine power and fuel consumption modeling
- Implement compatibility and PTO (Power Take-Off) management
- Maintenance scheduling based on operating hours
- Economic modeling with depreciation and operational costs
- Weather-dependent operational limitations
- Performance tracking and efficiency calculations

Tractor Categories:
- Compact Tractors: 15-50 HP, ideal for small operations and specialized tasks
- Utility Tractors: 45-100 HP, versatile mid-range tractors for general farming
- Row Crop Tractors: 75-300 HP, designed for row crop operations with narrow wheels
- 4WD Tractors: 200-600 HP, high-power tractors for large-scale field operations

Educational Value:
- Real-world tractor specifications and capabilities
- Understanding of power requirements for different implements
- Economic decision-making between tractor sizes and types
- Maintenance importance and cost management
- Fuel efficiency and operational planning
"""

import time
import uuid
from typing import Dict, List, Set, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

# Import core systems
from ..core.advanced_event_system import get_event_system, EventPriority
from ..core.entity_component_system import get_entity_manager, Component, ComponentCategory
from ..core.advanced_config_system import get_config_manager
from ..core.time_management import get_time_manager
from .equipment_system import EquipmentSystem, EquipmentCategory, EquipmentSpecification

class TractorCategory(Enum):
    """Tractor category classifications"""
    COMPACT = "compact"           # 15-50 HP, small operations
    UTILITY = "utility"           # 45-100 HP, general farming
    ROW_CROP = "row_crop"        # 75-300 HP, row crop operations
    FOUR_WD = "four_wd"          # 200-600 HP, large-scale operations
    SPECIALTY = "specialty"       # Specialized tractors (orchard, vineyard, etc.)

class TransmissionType(Enum):
    """Tractor transmission types"""
    MANUAL = "manual"                    # Manual gear transmission
    HYDROSTATIC = "hydrostatic"          # Hydrostatic transmission
    POWERSHIFT = "powershift"            # Powershift transmission
    CVT = "cvt"                         # Continuously Variable Transmission
    DUAL_CLUTCH = "dual_clutch"         # Dual clutch transmission

class DriveType(Enum):
    """Tractor drive system types"""
    TWO_WD = "2wd"              # Two-wheel drive
    FOUR_WD = "4wd"             # Four-wheel drive
    MFWD = "mfwd"               # Mechanical Front Wheel Drive
    AWD = "awd"                 # All-wheel drive

@dataclass
class TractorSpecification:
    """Detailed tractor specifications and capabilities"""
    # Basic identification
    tractor_id: str
    make: str
    model: str
    year: int
    category: TractorCategory
    
    # Engine specifications
    engine_power_hp: float          # Horsepower at rated RPM
    engine_power_kw: float          # Kilowatts at rated RPM
    engine_displacement_l: float    # Engine displacement in liters
    fuel_tank_capacity_l: float     # Fuel tank capacity in liters
    fuel_consumption_l_per_hour: float  # Fuel consumption at rated power
    
    # Transmission and drive
    transmission_type: TransmissionType
    drive_type: DriveType
    number_of_gears: int
    max_speed_kph: float            # Maximum speed in km/h
    pto_speed_rpm: List[int]        # Available PTO speeds
    
    # Physical specifications
    wheelbase_mm: int               # Wheelbase in millimeters
    total_length_mm: int            # Total length in millimeters
    total_width_mm: int             # Total width in millimeters
    total_height_mm: int            # Total height in millimeters
    ground_clearance_mm: int        # Ground clearance in millimeters
    turning_radius_m: float         # Minimum turning radius in meters
    
    # Weight and capacity
    operating_weight_kg: int        # Operating weight in kilograms
    max_lift_capacity_kg: int       # Maximum hydraulic lift capacity
    hydraulic_flow_lpm: float       # Hydraulic flow in liters per minute
    hydraulic_pressure_bar: float   # Hydraulic pressure in bar
    
    # Implement compatibility
    three_point_hitch_category: str # Category I, II, or III
    front_loader_compatible: bool   # Can mount front loader
    supported_implement_types: List[str]  # List of compatible implement types
    max_implement_width_m: float    # Maximum implement width
    
    # Operational capabilities
    field_efficiency: float         # Field efficiency factor (0.7-0.9)
    transport_efficiency: float     # Transport efficiency factor
    fuel_efficiency_factor: float   # Fuel efficiency multiplier
    maintenance_interval_hours: int # Hours between maintenance
    
    # Economic data
    new_price_usd: float           # New purchase price in USD
    depreciation_rate: float       # Annual depreciation rate
    maintenance_cost_per_hour: float # Maintenance cost per operating hour
    insurance_cost_annual: float   # Annual insurance cost
    
    # Environmental limitations
    max_slope_degrees: float       # Maximum slope capability
    wet_soil_capability: bool      # Can operate in wet conditions
    min_temperature_c: float       # Minimum operating temperature
    max_temperature_c: float       # Maximum operating temperature

@dataclass
class TractorComponent(Component):
    """ECS component for tractor-specific data"""
    # Specification reference
    specification: TractorSpecification
    
    # Current operational state
    engine_running: bool = False
    current_rpm: float = 0.0
    fuel_level_percent: float = 100.0
    hydraulic_pressure_current: float = 0.0
    
    # Attached implements
    front_implement_id: Optional[str] = None
    rear_implement_id: Optional[str] = None
    pto_engaged: bool = False
    pto_speed_current: int = 0
    
    # Operational tracking
    engine_hours: float = 0.0
    distance_traveled_km: float = 0.0
    fuel_consumed_l: float = 0.0
    hours_since_maintenance: float = 0.0
    
    # Performance metrics
    current_field_efficiency: float = 0.0
    current_fuel_efficiency: float = 0.0
    current_work_quality: float = 0.0
    
    # Maintenance and condition
    maintenance_due: bool = False
    next_maintenance_hours: float = 0.0
    breakdown_risk: float = 0.0
    
    # Economic tracking
    operational_cost_total: float = 0.0
    maintenance_cost_total: float = 0.0
    fuel_cost_total: float = 0.0
    
    category: ComponentCategory = ComponentCategory.GAMEPLAY

@dataclass
class TractorTask:
    """Represents a task assigned to a tractor"""
    task_id: str
    task_type: str              # "tillage", "planting", "harvesting", "transport"
    assigned_plots: List[Tuple[int, int]]
    implement_required: Optional[str]
    estimated_duration_hours: float
    fuel_requirement_l: float
    priority: int = 1
    assigned_operator: Optional[str] = None
    created_at: float = field(default_factory=time.time)

class TractorSystem:
    """Comprehensive tractor management system"""
    
    def __init__(self):
        """Initialize the tractor system"""
        self.system_name = "tractor_system"
        self.event_system = get_event_system()
        self.entity_manager = get_entity_manager()
        self.config_manager = get_config_manager()
        self.time_manager = get_time_manager()
        
        # Tractor management
        self.tractor_specifications: Dict[str, TractorSpecification] = {}
        self.active_tractors: Dict[str, str] = {}  # tractor_id -> entity_id
        self.tractor_tasks: Dict[str, List[TractorTask]] = {}
        
        # Performance tracking
        self.fuel_prices: Dict[str, float] = {"diesel": 1.20}  # Price per liter
        self.maintenance_costs: Dict[str, float] = {}
        self.operational_statistics: Dict[str, Dict] = {}
        
        # System state
        self.initialized = False
        self.update_frequency = 1.0  # Updates per second
        
        print("Tractor System initialized")
    
    def initialize(self) -> bool:
        """Initialize the tractor system with default specifications"""
        try:
            # Subscribe to events
            self.event_system.subscribe('time_advanced', self._handle_time_advanced)
            self.event_system.subscribe('weather_updated', self._handle_weather_change)
            self.event_system.subscribe('fuel_price_updated', self._handle_fuel_price_change)
            
            # Load tractor specifications
            self._load_tractor_specifications()
            
            # Initialize performance tracking
            self._initialize_performance_tracking()
            
            self.initialized = True
            
            # Emit initialization complete event
            self.event_system.emit('tractor_system_initialized', {
                'available_tractors': len(self.tractor_specifications),
                'system_status': 'ready'
            }, priority=EventPriority.NORMAL)
            
            print("Tractor System initialization complete")
            return True
            
        except Exception as e:
            print(f"Failed to initialize Tractor System: {e}")
            return False
    
    def _load_tractor_specifications(self):
        """Load tractor specifications from data or create defaults"""
        # Compact tractor specifications
        compact_tractors = [
            TractorSpecification(
                tractor_id="compact_kubota_b26",
                make="Kubota",
                model="B26",
                year=2024,
                category=TractorCategory.COMPACT,
                engine_power_hp=26.0,
                engine_power_kw=19.4,
                engine_displacement_l=1.123,
                fuel_tank_capacity_l=28.0,
                fuel_consumption_l_per_hour=2.8,
                transmission_type=TransmissionType.HYDROSTATIC,
                drive_type=DriveType.FOUR_WD,
                number_of_gears=1,  # Hydrostatic
                max_speed_kph=20.1,
                pto_speed_rpm=[540],
                wheelbase_mm=1520,
                total_length_mm=2845,
                total_width_mm=1245,
                total_height_mm=2380,
                ground_clearance_mm=280,
                turning_radius_m=2.1,
                operating_weight_kg=1157,
                max_lift_capacity_kg=680,
                hydraulic_flow_lpm=24.6,
                hydraulic_pressure_bar=172,
                three_point_hitch_category="I",
                front_loader_compatible=True,
                supported_implement_types=["mower", "tiller", "box_blade", "front_loader"],
                max_implement_width_m=1.8,
                field_efficiency=0.75,
                transport_efficiency=0.85,
                fuel_efficiency_factor=0.9,
                maintenance_interval_hours=50,
                new_price_usd=28500,
                depreciation_rate=0.15,
                maintenance_cost_per_hour=2.5,
                insurance_cost_annual=850,
                max_slope_degrees=30,
                wet_soil_capability=True,
                min_temperature_c=-20,
                max_temperature_c=45
            ),
            TractorSpecification(
                tractor_id="compact_john_deere_1025r",
                make="John Deere",
                model="1025R",
                year=2024,
                category=TractorCategory.COMPACT,
                engine_power_hp=25.2,
                engine_power_kw=18.8,
                engine_displacement_l=1.131,
                fuel_tank_capacity_l=26.5,
                fuel_consumption_l_per_hour=2.7,
                transmission_type=TransmissionType.HYDROSTATIC,
                drive_type=DriveType.FOUR_WD,
                number_of_gears=1,
                max_speed_kph=19.3,
                pto_speed_rpm=[540],
                wheelbase_mm=1626,
                total_length_mm=2832,
                total_width_mm=1194,
                total_height_mm=2667,
                ground_clearance_mm=254,
                turning_radius_m=2.3,
                operating_weight_kg=1030,
                max_lift_capacity_kg=635,
                hydraulic_flow_lpm=22.7,
                hydraulic_pressure_bar=165,
                three_point_hitch_category="I",
                front_loader_compatible=True,
                supported_implement_types=["mower", "tiller", "cultivator", "front_loader"],
                max_implement_width_m=1.5,
                field_efficiency=0.78,
                transport_efficiency=0.88,
                fuel_efficiency_factor=0.92,
                maintenance_interval_hours=50,
                new_price_usd=26800,
                depreciation_rate=0.14,
                maintenance_cost_per_hour=2.3,
                insurance_cost_annual=800,
                max_slope_degrees=32,
                wet_soil_capability=True,
                min_temperature_c=-25,
                max_temperature_c=50
            )
        ]
        
        # Utility tractor specifications
        utility_tractors = [
            TractorSpecification(
                tractor_id="utility_kubota_m5_091",
                make="Kubota",
                model="M5-091",
                year=2024,
                category=TractorCategory.UTILITY,
                engine_power_hp=91.0,
                engine_power_kw=67.9,
                engine_displacement_l=3.769,
                fuel_tank_capacity_l=120.0,
                fuel_consumption_l_per_hour=8.5,
                transmission_type=TransmissionType.POWERSHIFT,
                drive_type=DriveType.FOUR_WD,
                number_of_gears=24,
                max_speed_kph=40.0,
                pto_speed_rpm=[540, 1000],
                wheelbase_mm=2350,
                total_length_mm=4280,
                total_width_mm=2050,
                total_height_mm=2750,
                ground_clearance_mm=380,
                turning_radius_m=4.2,
                operating_weight_kg=3950,
                max_lift_capacity_kg=3175,
                hydraulic_flow_lpm=68.0,
                hydraulic_pressure_bar=200,
                three_point_hitch_category="II",
                front_loader_compatible=True,
                supported_implement_types=["plow", "disc", "cultivator", "planter", "mower", "baler"],
                max_implement_width_m=3.5,
                field_efficiency=0.82,
                transport_efficiency=0.90,
                fuel_efficiency_factor=0.85,
                maintenance_interval_hours=100,
                new_price_usd=75000,
                depreciation_rate=0.12,
                maintenance_cost_per_hour=5.8,
                insurance_cost_annual=2250,
                max_slope_degrees=35,
                wet_soil_capability=True,
                min_temperature_c=-30,
                max_temperature_c=45
            ),
            TractorSpecification(
                tractor_id="utility_new_holland_t4_75",
                make="New Holland",
                model="T4.75",
                year=2024,
                category=TractorCategory.UTILITY,
                engine_power_hp=75.0,
                engine_power_kw=55.9,
                engine_displacement_l=3.4,
                fuel_tank_capacity_l=110.0,
                fuel_consumption_l_per_hour=7.2,
                transmission_type=TransmissionType.POWERSHIFT,
                drive_type=DriveType.FOUR_WD,
                number_of_gears=16,
                max_speed_kph=40.0,
                pto_speed_rpm=[540, 1000],
                wheelbase_mm=2210,
                total_length_mm=4115,
                total_width_mm=1990,
                total_height_mm=2695,
                ground_clearance_mm=360,
                turning_radius_m=3.8,
                operating_weight_kg=3250,
                max_lift_capacity_kg=2500,
                hydraulic_flow_lpm=58.0,
                hydraulic_pressure_bar=190,
                three_point_hitch_category="II",
                front_loader_compatible=True,
                supported_implement_types=["plow", "disc", "cultivator", "planter", "sprayer"],
                max_implement_width_m=3.0,
                field_efficiency=0.80,
                transport_efficiency=0.88,
                fuel_efficiency_factor=0.87,
                maintenance_interval_hours=100,
                new_price_usd=68500,
                depreciation_rate=0.13,
                maintenance_cost_per_hour=5.2,
                insurance_cost_annual=2050,
                max_slope_degrees=33,
                wet_soil_capability=True,
                min_temperature_c=-25,
                max_temperature_c=50
            )
        ]
        
        # Row crop tractor specifications
        row_crop_tractors = [
            TractorSpecification(
                tractor_id="row_crop_john_deere_6155r",
                make="John Deere",
                model="6155R",
                year=2024,
                category=TractorCategory.ROW_CROP,
                engine_power_hp=155.0,
                engine_power_kw=115.6,
                engine_displacement_l=6.8,
                fuel_tank_capacity_l=380.0,
                fuel_consumption_l_per_hour=14.8,
                transmission_type=TransmissionType.CVT,
                drive_type=DriveType.FOUR_WD,
                number_of_gears=1,  # CVT
                max_speed_kph=50.0,
                pto_speed_rpm=[540, 1000],
                wheelbase_mm=2794,
                total_length_mm=5080,
                total_width_mm=2438,
                total_height_mm=3048,
                ground_clearance_mm=508,
                turning_radius_m=5.2,
                operating_weight_kg=7500,
                max_lift_capacity_kg=5900,
                hydraulic_flow_lpm=113.0,
                hydraulic_pressure_bar=210,
                three_point_hitch_category="II/III",
                front_loader_compatible=True,
                supported_implement_types=["plow", "disc", "planter", "cultivator", "combine_header", "sprayer"],
                max_implement_width_m=6.0,
                field_efficiency=0.85,
                transport_efficiency=0.92,
                fuel_efficiency_factor=0.82,
                maintenance_interval_hours=250,
                new_price_usd=185000,
                depreciation_rate=0.10,
                maintenance_cost_per_hour=12.5,
                insurance_cost_annual=5550,
                max_slope_degrees=25,
                wet_soil_capability=False,
                min_temperature_c=-30,
                max_temperature_c=45
            ),
            TractorSpecification(
                tractor_id="row_crop_case_ih_magnum_280",
                make="Case IH",
                model="Magnum 280",
                year=2024,
                category=TractorCategory.ROW_CROP,
                engine_power_hp=280.0,
                engine_power_kw=208.8,
                engine_displacement_l=8.7,
                fuel_tank_capacity_l=680.0,
                fuel_consumption_l_per_hour=26.5,
                transmission_type=TransmissionType.CVT,
                drive_type=DriveType.FOUR_WD,
                number_of_gears=1,
                max_speed_kph=50.0,
                pto_speed_rpm=[540, 1000],
                wheelbase_mm=3150,
                total_length_mm=5842,
                total_width_mm=2591,
                total_height_mm=3327,
                ground_clearance_mm=559,
                turning_radius_m=6.1,
                operating_weight_kg=12200,
                max_lift_capacity_kg=9070,
                hydraulic_flow_lpm=189.0,
                hydraulic_pressure_bar=248,
                three_point_hitch_category="III",
                front_loader_compatible=False,
                supported_implement_types=["heavy_plow", "disc", "planter", "cultivator", "sprayer", "heavy_tillage"],
                max_implement_width_m=9.0,
                field_efficiency=0.88,
                transport_efficiency=0.90,
                fuel_efficiency_factor=0.78,
                maintenance_interval_hours=500,
                new_price_usd=425000,
                depreciation_rate=0.08,
                maintenance_cost_per_hour=28.5,
                insurance_cost_annual=12750,
                max_slope_degrees=20,
                wet_soil_capability=False,
                min_temperature_c=-35,
                max_temperature_c=50
            )
        ]
        
        # 4WD tractor specifications
        four_wd_tractors = [
            TractorSpecification(
                tractor_id="four_wd_john_deere_9620r",
                make="John Deere",
                model="9620R",
                year=2024,
                category=TractorCategory.FOUR_WD,
                engine_power_hp=620.0,
                engine_power_kw=462.4,
                engine_displacement_l=13.6,
                fuel_tank_capacity_l=1514.0,
                fuel_consumption_l_per_hour=58.0,
                transmission_type=TransmissionType.CVT,
                drive_type=DriveType.FOUR_WD,
                number_of_gears=1,
                max_speed_kph=50.0,
                pto_speed_rpm=[1000],
                wheelbase_mm=3658,
                total_length_mm=7010,
                total_width_mm=3048,
                total_height_mm=3810,
                ground_clearance_mm=610,
                turning_radius_m=8.5,
                operating_weight_kg=22680,
                max_lift_capacity_kg=0,  # No 3-point hitch
                hydraulic_flow_lpm=284.0,
                hydraulic_pressure_bar=248,
                three_point_hitch_category="N/A",
                front_loader_compatible=False,
                supported_implement_types=["heavy_tillage", "large_planter", "air_seeder", "large_sprayer"],
                max_implement_width_m=15.0,
                field_efficiency=0.90,
                transport_efficiency=0.85,
                fuel_efficiency_factor=0.75,
                maintenance_interval_hours=500,
                new_price_usd=725000,
                depreciation_rate=0.08,
                maintenance_cost_per_hour=48.5,
                insurance_cost_annual=21750,
                max_slope_degrees=15,
                wet_soil_capability=False,
                min_temperature_c=-40,
                max_temperature_c=50
            )
        ]
        
        # Store all specifications
        all_tractors = compact_tractors + utility_tractors + row_crop_tractors + four_wd_tractors
        
        for tractor in all_tractors:
            self.tractor_specifications[tractor.tractor_id] = tractor
        
        print(f"Loaded {len(all_tractors)} tractor specifications")
    
    def _initialize_performance_tracking(self):
        """Initialize performance tracking systems"""
        for tractor_id in self.tractor_specifications.keys():
            self.operational_statistics[tractor_id] = {
                'total_hours': 0.0,
                'total_fuel_consumed': 0.0,
                'total_distance': 0.0,
                'maintenance_events': 0,
                'breakdown_events': 0,
                'efficiency_average': 0.0,
                'cost_per_hour': 0.0
            }
    
    def create_tractor(self, tractor_specification_id: str, farm_location: Tuple[float, float]) -> str:
        """Create a new tractor entity"""
        if tractor_specification_id not in self.tractor_specifications:
            raise ValueError(f"Unknown tractor specification: {tractor_specification_id}")
        
        spec = self.tractor_specifications[tractor_specification_id]
        
        # Create tractor entity with ECS components
        entity_data = {
            'identity': {
                'name': f"{spec.make} {spec.model}",
                'display_name': f"{spec.make} {spec.model} ({spec.year})",
                'description': f"{spec.engine_power_hp} HP {spec.category.value} tractor",
                'tags': {'tractor', spec.category.value, spec.make.lower()}
            },
            'transform': {
                'x': farm_location[0],
                'y': farm_location[1]
            },
            'renderable': {
                'sprite_path': f"assets/tractors/{spec.category.value}.png",
                'layer': 5
            },
            'tractor': TractorComponent(specification=spec),
            'equipment': {
                'equipment_type': "tractor",
                'condition': 100.0,
                'maintenance_hours': 0.0
            },
            'economic': {
                'base_value': spec.new_price_usd,
                'current_market_value': spec.new_price_usd,
                'depreciation_rate': spec.depreciation_rate,
                'maintenance_costs': 0.0,
                'operational_costs': 0.0
            }
        }
        
        entity_id = self.entity_manager.create_entity(entity_data)
        
        # Register tractor
        self.active_tractors[tractor_specification_id] = entity_id
        self.tractor_tasks[entity_id] = []
        
        # Emit tractor creation event
        self.event_system.emit('tractor_created', {
            'entity_id': entity_id,
            'tractor_id': tractor_specification_id,
            'specification': spec.__dict__,
            'location': farm_location
        }, priority=EventPriority.NORMAL)
        
        print(f"Created tractor: {spec.make} {spec.model} at {farm_location}")
        return entity_id
    
    def assign_task(self, tractor_entity_id: str, task: TractorTask) -> bool:
        """Assign a task to a tractor"""
        if tractor_entity_id not in self.tractor_tasks:
            return False
        
        # Validate task requirements
        tractor_component = self.entity_manager.get_component(tractor_entity_id, 'tractor')
        if not tractor_component:
            return False
        
        # Check implement compatibility if required
        if task.implement_required:
            if task.implement_required not in tractor_component.specification.supported_implement_types:
                print(f"Tractor cannot use required implement: {task.implement_required}")
                return False
        
        # Add task to queue
        self.tractor_tasks[tractor_entity_id].append(task)
        
        # Emit task assignment event
        self.event_system.emit('tractor_task_assigned', {
            'tractor_entity_id': tractor_entity_id,
            'task_id': task.task_id,
            'task_type': task.task_type,
            'plots': len(task.assigned_plots)
        }, priority=EventPriority.NORMAL)
        
        return True
    
    def start_engine(self, tractor_entity_id: str) -> bool:
        """Start tractor engine"""
        tractor_component = self.entity_manager.get_component(tractor_entity_id, 'tractor')
        if not tractor_component:
            return False
        
        if tractor_component.fuel_level_percent <= 0:
            print("Cannot start engine - no fuel")
            return False
        
        tractor_component.engine_running = True
        tractor_component.current_rpm = 800.0  # Idle RPM
        
        # Update component
        self.entity_manager.update_component(tractor_entity_id, 'tractor', {
            'engine_running': True,
            'current_rpm': 800.0
        })
        
        # Emit engine start event
        self.event_system.emit('tractor_engine_started', {
            'tractor_entity_id': tractor_entity_id,
            'fuel_level': tractor_component.fuel_level_percent
        }, priority=EventPriority.NORMAL)
        
        return True
    
    def stop_engine(self, tractor_entity_id: str) -> bool:
        """Stop tractor engine"""
        tractor_component = self.entity_manager.get_component(tractor_entity_id, 'tractor')
        if not tractor_component:
            return False
        
        tractor_component.engine_running = False
        tractor_component.current_rpm = 0.0
        tractor_component.pto_engaged = False
        
        # Update component
        self.entity_manager.update_component(tractor_entity_id, 'tractor', {
            'engine_running': False,
            'current_rpm': 0.0,
            'pto_engaged': False
        })
        
        # Emit engine stop event
        self.event_system.emit('tractor_engine_stopped', {
            'tractor_entity_id': tractor_entity_id
        }, priority=EventPriority.NORMAL)
        
        return True
    
    def attach_implement(self, tractor_entity_id: str, implement_entity_id: str, 
                        attachment_point: str = "rear") -> bool:
        """Attach an implement to a tractor"""
        tractor_component = self.entity_manager.get_component(tractor_entity_id, 'tractor')
        if not tractor_component:
            return False
        
        # Check attachment point availability
        if attachment_point == "front":
            if not tractor_component.specification.front_loader_compatible:
                print("Tractor does not support front implements")
                return False
            if tractor_component.front_implement_id:
                print("Front attachment point already occupied")
                return False
            tractor_component.front_implement_id = implement_entity_id
        elif attachment_point == "rear":
            if tractor_component.rear_implement_id:
                print("Rear attachment point already occupied")
                return False
            tractor_component.rear_implement_id = implement_entity_id
        else:
            print(f"Invalid attachment point: {attachment_point}")
            return False
        
        # Update component
        update_data = {}
        if attachment_point == "front":
            update_data['front_implement_id'] = implement_entity_id
        else:
            update_data['rear_implement_id'] = implement_entity_id
        
        self.entity_manager.update_component(tractor_entity_id, 'tractor', update_data)
        
        # Emit implement attachment event
        self.event_system.emit('implement_attached', {
            'tractor_entity_id': tractor_entity_id,
            'implement_entity_id': implement_entity_id,
            'attachment_point': attachment_point
        }, priority=EventPriority.NORMAL)
        
        return True
    
    def detach_implement(self, tractor_entity_id: str, attachment_point: str) -> bool:
        """Detach an implement from a tractor"""
        tractor_component = self.entity_manager.get_component(tractor_entity_id, 'tractor')
        if not tractor_component:
            return False
        
        implement_id = None
        if attachment_point == "front":
            implement_id = tractor_component.front_implement_id
            tractor_component.front_implement_id = None
        elif attachment_point == "rear":
            implement_id = tractor_component.rear_implement_id
            tractor_component.rear_implement_id = None
        else:
            print(f"Invalid attachment point: {attachment_point}")
            return False
        
        if not implement_id:
            print(f"No implement attached at {attachment_point}")
            return False
        
        # Update component
        update_data = {}
        if attachment_point == "front":
            update_data['front_implement_id'] = None
        else:
            update_data['rear_implement_id'] = None
        
        self.entity_manager.update_component(tractor_entity_id, 'tractor', update_data)
        
        # Emit implement detachment event
        self.event_system.emit('implement_detached', {
            'tractor_entity_id': tractor_entity_id,
            'implement_entity_id': implement_id,
            'attachment_point': attachment_point
        }, priority=EventPriority.NORMAL)
        
        return True
    
    def update(self, delta_time: float):
        """Update tractor system"""
        if not self.initialized:
            return
        
        # Update all active tractors
        for entity_id in self.active_tractors.values():
            self._update_tractor(entity_id, delta_time)
        
        # Process scheduled maintenance
        self._process_maintenance_schedule()
        
        # Update performance statistics
        self._update_performance_statistics()
    
    def _update_tractor(self, entity_id: str, delta_time: float):
        """Update individual tractor state"""
        tractor_component = self.entity_manager.get_component(entity_id, 'tractor')
        if not tractor_component:
            return
        
        if tractor_component.engine_running:
            # Update engine hours
            tractor_component.engine_hours += delta_time / 3600.0  # Convert seconds to hours
            tractor_component.hours_since_maintenance += delta_time / 3600.0
            
            # Calculate fuel consumption
            fuel_rate = tractor_component.specification.fuel_consumption_l_per_hour
            fuel_consumed = fuel_rate * (delta_time / 3600.0)
            
            # Update fuel level
            tank_capacity = tractor_component.specification.fuel_tank_capacity_l
            fuel_consumed_percent = (fuel_consumed / tank_capacity) * 100
            tractor_component.fuel_level_percent = max(0, tractor_component.fuel_level_percent - fuel_consumed_percent)
            tractor_component.fuel_consumed_l += fuel_consumed
            
            # Update operational costs
            fuel_cost = fuel_consumed * self.fuel_prices["diesel"]
            maintenance_cost = tractor_component.specification.maintenance_cost_per_hour * (delta_time / 3600.0)
            tractor_component.operational_cost_total += fuel_cost
            tractor_component.maintenance_cost_total += maintenance_cost
            
            # Check maintenance due
            if tractor_component.hours_since_maintenance >= tractor_component.specification.maintenance_interval_hours:
                tractor_component.maintenance_due = True
                tractor_component.next_maintenance_hours = 0
            
            # Calculate breakdown risk
            maintenance_overdue = max(0, tractor_component.hours_since_maintenance - tractor_component.specification.maintenance_interval_hours)
            base_risk = 0.001  # 0.1% base risk per hour
            tractor_component.breakdown_risk = base_risk + (maintenance_overdue * 0.0005)
            
            # Update component
            self.entity_manager.update_component(entity_id, 'tractor', {
                'engine_hours': tractor_component.engine_hours,
                'fuel_level_percent': tractor_component.fuel_level_percent,
                'fuel_consumed_l': tractor_component.fuel_consumed_l,
                'hours_since_maintenance': tractor_component.hours_since_maintenance,
                'operational_cost_total': tractor_component.operational_cost_total,
                'maintenance_cost_total': tractor_component.maintenance_cost_total,
                'maintenance_due': tractor_component.maintenance_due,
                'breakdown_risk': tractor_component.breakdown_risk
            })
            
            # Stop engine if out of fuel
            if tractor_component.fuel_level_percent <= 0:
                self.stop_engine(entity_id)
                self.event_system.emit('tractor_out_of_fuel', {
                    'tractor_entity_id': entity_id
                }, priority=EventPriority.HIGH)
    
    def _process_maintenance_schedule(self):
        """Process scheduled maintenance for all tractors"""
        current_time = time.time()
        
        for entity_id in self.active_tractors.values():
            tractor_component = self.entity_manager.get_component(entity_id, 'tractor')
            if not tractor_component or not tractor_component.maintenance_due:
                continue
            
            # Emit maintenance reminder
            self.event_system.emit('tractor_maintenance_due', {
                'tractor_entity_id': entity_id,
                'hours_overdue': tractor_component.hours_since_maintenance - tractor_component.specification.maintenance_interval_hours,
                'estimated_cost': tractor_component.specification.maintenance_cost_per_hour * tractor_component.specification.maintenance_interval_hours
            }, priority=EventPriority.HIGH)
    
    def _update_performance_statistics(self):
        """Update performance statistics for all tractors"""
        for tractor_id, entity_id in self.active_tractors.items():
            tractor_component = self.entity_manager.get_component(entity_id, 'tractor')
            if not tractor_component:
                continue
            
            stats = self.operational_statistics[tractor_id]
            stats['total_hours'] = tractor_component.engine_hours
            stats['total_fuel_consumed'] = tractor_component.fuel_consumed_l
            stats['cost_per_hour'] = (tractor_component.operational_cost_total + 
                                    tractor_component.maintenance_cost_total) / max(1, tractor_component.engine_hours)
    
    def _handle_time_advanced(self, event_data: Dict[str, Any]):
        """Handle time advancement events"""
        # Update time-based calculations
        pass
    
    def _handle_weather_change(self, event_data: Dict[str, Any]):
        """Handle weather change events"""
        # Adjust operational capabilities based on weather
        pass
    
    def _handle_fuel_price_change(self, event_data: Dict[str, Any]):
        """Handle fuel price changes"""
        if 'diesel_price' in event_data:
            self.fuel_prices['diesel'] = event_data['diesel_price']
    
    def perform_maintenance(self, tractor_entity_id: str) -> Dict[str, Any]:
        """Perform maintenance on a tractor"""
        tractor_component = self.entity_manager.get_component(tractor_entity_id, 'tractor')
        if not tractor_component:
            return {'success': False, 'error': 'Tractor not found'}
        
        # Calculate maintenance cost
        maintenance_hours = tractor_component.hours_since_maintenance
        base_cost = tractor_component.specification.maintenance_cost_per_hour * tractor_component.specification.maintenance_interval_hours
        overdue_multiplier = 1.0 + (max(0, maintenance_hours - tractor_component.specification.maintenance_interval_hours) / 100.0)
        total_cost = base_cost * overdue_multiplier
        
        # Reset maintenance tracking
        tractor_component.hours_since_maintenance = 0.0
        tractor_component.maintenance_due = False
        tractor_component.next_maintenance_hours = tractor_component.specification.maintenance_interval_hours
        tractor_component.breakdown_risk = 0.001
        tractor_component.maintenance_cost_total += total_cost
        
        # Update equipment condition
        equipment_component = self.entity_manager.get_component(tractor_entity_id, 'equipment')
        if equipment_component:
            self.entity_manager.update_component(tractor_entity_id, 'equipment', {
                'condition': 100.0,
                'maintenance_hours': 0.0
            })
        
        # Update tractor component
        self.entity_manager.update_component(tractor_entity_id, 'tractor', {
            'hours_since_maintenance': 0.0,
            'maintenance_due': False,
            'next_maintenance_hours': tractor_component.specification.maintenance_interval_hours,
            'breakdown_risk': 0.001,
            'maintenance_cost_total': tractor_component.maintenance_cost_total
        })
        
        # Emit maintenance completed event
        self.event_system.emit('tractor_maintenance_completed', {
            'tractor_entity_id': tractor_entity_id,
            'maintenance_cost': total_cost,
            'hours_maintained': maintenance_hours
        }, priority=EventPriority.NORMAL)
        
        return {
            'success': True,
            'maintenance_cost': total_cost,
            'hours_maintained': maintenance_hours,
            'condition_restored': 100.0
        }
    
    def get_available_tractors(self) -> List[Dict[str, Any]]:
        """Get list of available tractor specifications"""
        available = []
        
        for tractor_id, spec in self.tractor_specifications.items():
            available.append({
                'tractor_id': tractor_id,
                'make': spec.make,
                'model': spec.model,
                'year': spec.year,
                'category': spec.category.value,
                'horsepower': spec.engine_power_hp,
                'price': spec.new_price_usd,
                'fuel_consumption': spec.fuel_consumption_l_per_hour,
                'maintenance_interval': spec.maintenance_interval_hours,
                'max_implement_width': spec.max_implement_width_m
            })
        
        return available
    
    def get_tractor_status(self, entity_id: str) -> Dict[str, Any]:
        """Get detailed status of a specific tractor"""
        tractor_component = self.entity_manager.get_component(entity_id, 'tractor')
        if not tractor_component:
            return {}
        
        identity_component = self.entity_manager.get_component(entity_id, 'identity')
        transform_component = self.entity_manager.get_component(entity_id, 'transform')
        
        return {
            'entity_id': entity_id,
            'name': identity_component.display_name if identity_component else 'Unknown Tractor',
            'specification': {
                'make': tractor_component.specification.make,
                'model': tractor_component.specification.model,
                'horsepower': tractor_component.specification.engine_power_hp,
                'fuel_capacity': tractor_component.specification.fuel_tank_capacity_l
            },
            'operational_status': {
                'engine_running': tractor_component.engine_running,
                'fuel_level_percent': tractor_component.fuel_level_percent,
                'engine_hours': tractor_component.engine_hours,
                'maintenance_due': tractor_component.maintenance_due,
                'breakdown_risk': tractor_component.breakdown_risk
            },
            'implements': {
                'front': tractor_component.front_implement_id,
                'rear': tractor_component.rear_implement_id,
                'pto_engaged': tractor_component.pto_engaged
            },
            'location': {
                'x': transform_component.x if transform_component else 0,
                'y': transform_component.y if transform_component else 0
            },
            'economics': {
                'operational_cost_total': tractor_component.operational_cost_total,
                'maintenance_cost_total': tractor_component.maintenance_cost_total,
                'fuel_consumed_total': tractor_component.fuel_consumed_l
            },
            'tasks': len(self.tractor_tasks.get(entity_id, []))
        }
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive tractor system statistics"""
        total_tractors = len(self.active_tractors)
        total_engine_hours = sum(
            self.operational_statistics[tid]['total_hours'] 
            for tid in self.operational_statistics.keys()
        )
        total_fuel_consumed = sum(
            self.operational_statistics[tid]['total_fuel_consumed'] 
            for tid in self.operational_statistics.keys()
        )
        
        # Calculate average costs
        avg_cost_per_hour = sum(
            self.operational_statistics[tid]['cost_per_hour'] 
            for tid in self.operational_statistics.keys()
        ) / max(1, total_tractors)
        
        return {
            'total_tractors': total_tractors,
            'available_specifications': len(self.tractor_specifications),
            'total_engine_hours': total_engine_hours,
            'total_fuel_consumed_l': total_fuel_consumed,
            'average_cost_per_hour': avg_cost_per_hour,
            'fuel_price_diesel': self.fuel_prices['diesel'],
            'operational_statistics': self.operational_statistics
        }

# Global tractor system instance
_global_tractor_system: Optional[TractorSystem] = None

def get_tractor_system() -> TractorSystem:
    """Get the global tractor system instance"""
    global _global_tractor_system
    if _global_tractor_system is None:
        _global_tractor_system = TractorSystem()
        _global_tractor_system.initialize()
    return _global_tractor_system

def initialize_tractor_system() -> TractorSystem:
    """Initialize the global tractor system"""
    global _global_tractor_system
    _global_tractor_system = TractorSystem()
    _global_tractor_system.initialize()
    return _global_tractor_system

# Convenience functions
def create_tractor(specification_id: str, location: Tuple[float, float] = (8.0, 8.0)) -> str:
    """Convenience function to create a tractor"""
    return get_tractor_system().create_tractor(specification_id, location)

def get_available_tractors() -> List[Dict[str, Any]]:
    """Convenience function to get available tractors"""
    return get_tractor_system().get_available_tractors()

def start_tractor_engine(entity_id: str) -> bool:
    """Convenience function to start tractor engine"""
    return get_tractor_system().start_engine(entity_id)

def attach_implement_to_tractor(tractor_id: str, implement_id: str, point: str = "rear") -> bool:
    """Convenience function to attach implement to tractor"""
    return get_tractor_system().attach_implement(tractor_id, implement_id, point)