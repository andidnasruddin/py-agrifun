"""
Combine Harvester System - Advanced Grain Harvesting for AgriFun Agricultural Simulation

This system provides comprehensive simulation of combine harvesters including multiple
combine classes, interchangeable headers, grain handling systems, and harvest optimization.
Integrates with crop, weather, and economic systems for realistic harvest operations.

Key Features:
- Multiple combine classes (Class 5-10) with realistic specifications
- Interchangeable header system (grain, corn, flex, draper headers)
- Advanced grain handling with cleaning, storage, and unloading systems
- Harvest optimization based on crop moisture, weather, and field conditions
- Economic modeling with custom vs service provider analysis
- Performance tracking and efficiency calculations
- Educational content about combine selection and operation

Combine Classifications:
- Class 5-6: Mid-range combines (200-350 HP, 6000-9000L tank)
- Class 7-8: Large combines (350-500 HP, 9000-14000L tank)  
- Class 9-10: High-capacity combines (500-700+ HP, 14000-18000L tank)

Educational Value:
- Understanding of combine capacity and crop throughput
- Header selection for different crop types and conditions
- Harvest timing optimization and grain quality management
- Economic analysis of ownership vs custom harvesting
- Maintenance scheduling and operational efficiency
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
from .equipment_system import EquipmentSystem, EquipmentCategory

class CombineClass(Enum):
    """Combine harvester class classifications"""
    CLASS_5 = 5    # Mid-range: 200-250 HP, 6000-7000L tank
    CLASS_6 = 6    # Mid-range: 250-300 HP, 7000-9000L tank
    CLASS_7 = 7    # Large: 300-400 HP, 9000-11000L tank
    CLASS_8 = 8    # Large: 400-500 HP, 11000-14000L tank
    CLASS_9 = 9    # High-capacity: 500-600 HP, 14000-16000L tank
    CLASS_10 = 10  # High-capacity: 600+ HP, 16000+ L tank

class HeaderType(Enum):
    """Types of combine headers"""
    GRAIN = "grain"           # Standard grain header for small grains
    CORN = "corn"            # Corn header with row units
    FLEX = "flex"            # Flexible cutterbar for soybeans
    DRAPER = "draper"        # Draper header for uniform feeding
    SUNFLOWER = "sunflower"  # Specialized sunflower header
    PICKUP = "pickup"        # Pickup header for windrow harvesting

class ThreshingSystem(Enum):
    """Types of threshing systems"""
    CONVENTIONAL = "conventional"  # Cylinder and concaves
    ROTARY = "rotary"            # Axial flow rotary system
    HYBRID = "hybrid"            # Combination system

class GrainHandlingMode(Enum):
    """Grain handling and unloading modes"""
    TANK_FILL = "tank_fill"      # Filling grain tank
    UNLOADING = "unloading"      # Unloading to cart/truck
    SAMPLE_TEST = "sample_test"  # Testing grain quality

@dataclass
class HeaderSpecification:
    """Detailed header specifications"""
    header_id: str
    header_type: HeaderType
    make: str
    model: str
    
    # Physical specifications
    cutting_width_m: float          # Cutting width in meters
    transport_width_m: float        # Transport width in meters
    weight_kg: int                  # Header weight in kilograms
    height_m: float                 # Overall height in meters
    
    # Operational parameters
    min_cutting_height_cm: float    # Minimum cutting height
    max_cutting_height_cm: float    # Maximum cutting height
    optimal_ground_speed_kph: float # Optimal ground speed
    max_ground_speed_kph: float     # Maximum ground speed
    
    # Crop-specific capabilities
    suitable_crops: List[str]       # Compatible crop types
    row_spacing_cm: Optional[float] # For row crop headers
    number_of_rows: Optional[int]   # For row crop headers
    
    # Performance characteristics
    feeding_efficiency: float       # Feed rate efficiency (0.8-0.95)
    crop_flow_capacity_tph: float   # Crop flow capacity tons/hour
    header_loss_factor: float       # Typical header loss percentage
    
    # Economic data
    price_new_usd: float           # New header price
    depreciation_rate: float       # Annual depreciation
    maintenance_cost_annual: float # Annual maintenance cost

@dataclass
class CombineSpecification:
    """Detailed combine harvester specifications"""
    # Basic identification
    combine_id: str
    make: str
    model: str
    year: int
    combine_class: CombineClass
    
    # Engine and drive specifications
    engine_power_hp: float          # Engine horsepower
    engine_power_kw: float          # Engine kilowatts
    fuel_tank_capacity_l: float     # Fuel capacity in liters
    fuel_consumption_l_per_hour: float  # Fuel consumption at rated load
    transmission_type: str          # CVT, PowerShift, etc.
    
    # Threshing and separation system
    threshing_system: ThreshingSystem
    threshing_width_mm: int         # Threshing cylinder/rotor width
    separation_area_m2: float       # Separation area in square meters
    cleaning_fan_diameter_mm: int   # Cleaning fan diameter
    sieve_area_m2: float           # Total sieve area
    
    # Grain handling system
    grain_tank_capacity_l: int      # Grain tank capacity in liters
    unloading_rate_l_per_min: int   # Unloading rate liters per minute
    unloading_height_m: float       # Maximum unloading height
    unloading_reach_m: float        # Unloading auger reach
    
    # Physical specifications
    overall_length_m: float         # Overall length with header
    overall_width_m: float          # Overall width (transport)
    overall_height_m: float         # Overall height
    ground_clearance_mm: int        # Minimum ground clearance
    wheelbase_mm: int              # Wheelbase measurement
    turning_radius_m: float         # Minimum turning radius
    
    # Performance capabilities
    theoretical_capacity_tph: float  # Theoretical throughput tons/hour
    typical_capacity_tph: float     # Typical field capacity
    field_efficiency: float         # Typical field efficiency
    grain_sample_quality: float     # Grain cleaning effectiveness (0-1)
    
    # Operational parameters
    min_ground_speed_kph: float     # Minimum operating speed
    max_ground_speed_kph: float     # Maximum operating speed
    optimal_ground_speed_kph: float # Optimal operating speed
    rotor_speed_min_rpm: int        # Minimum rotor/cylinder speed
    rotor_speed_max_rpm: int        # Maximum rotor/cylinder speed
    
    # Compatible headers
    compatible_header_types: List[HeaderType]
    max_header_width_m: float       # Maximum header width supported
    header_lift_capacity_kg: int    # Maximum header lift capacity
    
    # Economic specifications
    new_price_usd: float           # New combine price
    depreciation_rate: float       # Annual depreciation rate
    insurance_rate: float          # Insurance as % of value
    maintenance_cost_per_hour: float # Maintenance cost per hour
    
    # Environmental capabilities
    max_slope_degrees: float       # Maximum slope capability
    wet_crop_capability: bool      # Can harvest wet crops
    dusty_condition_capability: bool # Can operate in dusty conditions
    night_harvesting_capability: bool # Has lighting for night work

@dataclass
class CombineComponent(Component):
    """ECS component for combine harvester data"""
    # Specification reference
    specification: CombineSpecification
    
    # Current operational state
    engine_running: bool = False
    header_attached: Optional[str] = None
    header_height_cm: float = 50.0
    currently_harvesting: bool = False
    
    # Threshing and separation settings
    rotor_speed_rpm: int = 0
    concave_clearance_mm: float = 12.0
    fan_speed_rpm: int = 0
    upper_sieve_opening_mm: float = 15.0
    lower_sieve_opening_mm: float = 8.0
    
    # Grain handling status
    grain_tank_level_percent: float = 0.0
    grain_tank_contents_l: float = 0.0
    unloading_active: bool = False
    
    # Performance tracking
    total_engine_hours: float = 0.0
    total_acres_harvested: float = 0.0
    total_grain_harvested_tonnes: float = 0.0
    fuel_consumed_total_l: float = 0.0
    hours_since_maintenance: float = 0.0
    
    # Current performance metrics
    current_throughput_tph: float = 0.0
    current_ground_speed_kph: float = 0.0
    current_fuel_consumption_lph: float = 0.0
    grain_loss_percent: float = 2.0
    grain_damage_percent: float = 1.0
    foreign_material_percent: float = 1.5
    
    # Condition and maintenance
    overall_condition: float = 100.0
    maintenance_due: bool = False
    worn_parts: List[str] = field(default_factory=list)
    
    # Economic tracking
    operational_cost_total: float = 0.0
    maintenance_cost_total: float = 0.0
    fuel_cost_total: float = 0.0
    revenue_generated: float = 0.0
    
    # Environmental adaptation
    current_crop_moisture: Optional[float] = None
    weather_efficiency_factor: float = 1.0
    field_condition_factor: float = 1.0
    
    category: ComponentCategory = ComponentCategory.GAMEPLAY

@dataclass
class HarvestTask:
    """Represents a harvesting task for a combine"""
    task_id: str
    crop_type: str
    assigned_plots: List[Tuple[int, int]]
    target_header_height_cm: float
    target_ground_speed_kph: float
    estimated_yield_tph: float
    grain_moisture_target: float
    quality_requirements: Dict[str, float]
    priority: int = 1
    custom_rate_per_acre: Optional[float] = None
    created_at: float = field(default_factory=time.time)

class CombineHarvesterSystem:
    """Comprehensive combine harvester management system"""
    
    def __init__(self):
        """Initialize the combine harvester system"""
        self.system_name = "combine_harvester_system"
        self.event_system = get_event_system()
        self.entity_manager = get_entity_manager()
        self.config_manager = get_config_manager()
        self.time_manager = get_time_manager()
        
        # Combine and header management
        self.combine_specifications: Dict[str, CombineSpecification] = {}
        self.header_specifications: Dict[str, HeaderSpecification] = {}
        self.active_combines: Dict[str, str] = {}  # combine_id -> entity_id
        self.combine_tasks: Dict[str, List[HarvestTask]] = {}
        
        # Performance tracking
        self.harvest_statistics: Dict[str, Dict] = {}
        self.fuel_prices: Dict[str, float] = {"diesel": 1.20}
        self.grain_prices: Dict[str, float] = {"corn": 5.50, "soybeans": 12.80, "wheat": 7.20}
        
        # Custom harvesting rates
        self.custom_rates: Dict[str, Dict] = {
            "corn": {"rate_per_acre": 35.0, "base_moisture": 15.5},
            "soybeans": {"rate_per_acre": 28.0, "base_moisture": 13.0},
            "wheat": {"rate_per_acre": 22.0, "base_moisture": 13.5}
        }
        
        # System state
        self.initialized = False
        self.update_frequency = 2.0  # Updates per second for combines
        
        print("Combine Harvester System initialized")
    
    def initialize(self) -> bool:
        """Initialize the combine harvester system"""
        try:
            # Subscribe to events
            self.event_system.subscribe('time_advanced', self._handle_time_advanced)
            self.event_system.subscribe('weather_updated', self._handle_weather_change)
            self.event_system.subscribe('crop_ready_for_harvest', self._handle_crop_ready)
            self.event_system.subscribe('grain_price_updated', self._handle_grain_price_change)
            
            # Load specifications
            self._load_combine_specifications()
            self._load_header_specifications()
            
            # Initialize performance tracking
            self._initialize_performance_tracking()
            
            self.initialized = True
            
            # Emit initialization complete event
            self.event_system.emit('combine_system_initialized', {
                'available_combines': len(self.combine_specifications),
                'available_headers': len(self.header_specifications),
                'system_status': 'ready'
            }, priority=EventPriority.NORMAL)
            
            print("Combine Harvester System initialization complete")
            return True
            
        except Exception as e:
            print(f"Failed to initialize Combine Harvester System: {e}")
            return False
    
    def _load_combine_specifications(self):
        """Load combine specifications"""
        # Class 6 combines
        class6_combines = [
            CombineSpecification(
                combine_id="john_deere_s670",
                make="John Deere",
                model="S670",
                year=2024,
                combine_class=CombineClass.CLASS_6,
                engine_power_hp=290,
                engine_power_kw=216,
                fuel_tank_capacity_l=950,
                fuel_consumption_l_per_hour=45.0,
                transmission_type="CVT",
                threshing_system=ThreshingSystem.ROTARY,
                threshing_width_mm=1676,
                separation_area_m2=5.7,
                cleaning_fan_diameter_mm=1320,
                sieve_area_m2=5.1,
                grain_tank_capacity_l=8700,
                unloading_rate_l_per_min=132,
                unloading_height_m=4.8,
                unloading_reach_m=7.2,
                overall_length_m=11.2,
                overall_width_m=4.1,
                overall_height_m=4.0,
                ground_clearance_mm=360,
                wheelbase_mm=4200,
                turning_radius_m=7.3,
                theoretical_capacity_tph=38.0,
                typical_capacity_tph=28.0,
                field_efficiency=0.85,
                grain_sample_quality=0.92,
                min_ground_speed_kph=3.2,
                max_ground_speed_kph=32.0,
                optimal_ground_speed_kph=6.5,
                rotor_speed_min_rpm=300,
                rotor_speed_max_rpm=1100,
                compatible_header_types=[HeaderType.GRAIN, HeaderType.FLEX, HeaderType.CORN],
                max_header_width_m=10.7,
                header_lift_capacity_kg=3600,
                new_price_usd=485000,
                depreciation_rate=0.12,
                insurance_rate=0.018,
                maintenance_cost_per_hour=28.5,
                max_slope_degrees=18,
                wet_crop_capability=True,
                dusty_condition_capability=True,
                night_harvesting_capability=True
            ),
            CombineSpecification(
                combine_id="case_ih_axial_flow_7140",
                make="Case IH",
                model="Axial-Flow 7140",
                year=2024,
                combine_class=CombineClass.CLASS_6,
                engine_power_hp=285,
                engine_power_kw=212,
                fuel_tank_capacity_l=910,
                fuel_consumption_l_per_hour=43.5,
                transmission_type="PowerShift",
                threshing_system=ThreshingSystem.ROTARY,
                threshing_width_mm=1626,
                separation_area_m2=5.5,
                cleaning_fan_diameter_mm=1270,
                sieve_area_m2=4.9,
                grain_tank_capacity_l=8200,
                unloading_rate_l_per_min=125,
                unloading_height_m=4.6,
                unloading_reach_m=6.8,
                overall_length_m=10.8,
                overall_width_m=3.9,
                overall_height_m=3.9,
                ground_clearance_mm=350,
                wheelbase_mm=4100,
                turning_radius_m=7.1,
                theoretical_capacity_tph=36.0,
                typical_capacity_tph=26.5,
                field_efficiency=0.83,
                grain_sample_quality=0.90,
                min_ground_speed_kph=3.0,
                max_ground_speed_kph=30.0,
                optimal_ground_speed_kph=6.2,
                rotor_speed_min_rpm=280,
                rotor_speed_max_rpm=1050,
                compatible_header_types=[HeaderType.GRAIN, HeaderType.FLEX, HeaderType.CORN],
                max_header_width_m=10.2,
                header_lift_capacity_kg=3400,
                new_price_usd=465000,
                depreciation_rate=0.13,
                insurance_rate=0.017,
                maintenance_cost_per_hour=26.8,
                max_slope_degrees=17,
                wet_crop_capability=True,
                dusty_condition_capability=True,
                night_harvesting_capability=True
            )
        ]
        
        # Class 8 combines
        class8_combines = [
            CombineSpecification(
                combine_id="john_deere_s780",
                make="John Deere",
                model="S780",
                year=2024,
                combine_class=CombineClass.CLASS_8,
                engine_power_hp=473,
                engine_power_kw=353,
                fuel_tank_capacity_l=1400,
                fuel_consumption_l_per_hour=68.0,
                transmission_type="CVT",
                threshing_system=ThreshingSystem.ROTARY,
                threshing_width_mm=1676,
                separation_area_m2=6.7,
                cleaning_fan_diameter_mm=1520,
                sieve_area_m2=6.2,
                grain_tank_capacity_l=14100,
                unloading_rate_l_per_min=165,
                unloading_height_m=5.2,
                unloading_reach_m=7.8,
                overall_length_m=11.8,
                overall_width_m=4.3,
                overall_height_m=4.1,
                ground_clearance_mm=380,
                wheelbase_mm=4400,
                turning_radius_m=7.8,
                theoretical_capacity_tph=58.0,
                typical_capacity_tph=42.0,
                field_efficiency=0.88,
                grain_sample_quality=0.94,
                min_ground_speed_kph=3.5,
                max_ground_speed_kph=40.0,
                optimal_ground_speed_kph=7.2,
                rotor_speed_min_rpm=300,
                rotor_speed_max_rpm=1200,
                compatible_header_types=[HeaderType.GRAIN, HeaderType.FLEX, HeaderType.CORN, HeaderType.DRAPER],
                max_header_width_m=13.7,
                header_lift_capacity_kg=5400,
                new_price_usd=685000,
                depreciation_rate=0.10,
                insurance_rate=0.020,
                maintenance_cost_per_hour=42.5,
                max_slope_degrees=20,
                wet_crop_capability=True,
                dusty_condition_capability=True,
                night_harvesting_capability=True
            ),
            CombineSpecification(
                combine_id="claas_lexion_770",
                make="CLAAS",
                model="LEXION 770",
                year=2024,
                combine_class=CombineClass.CLASS_8,
                engine_power_hp=435,
                engine_power_kw=324,
                fuel_tank_capacity_l=1350,
                fuel_consumption_l_per_hour=62.5,
                transmission_type="CVT",
                threshing_system=ThreshingSystem.HYBRID,
                threshing_width_mm=1700,
                separation_area_m2=7.2,
                cleaning_fan_diameter_mm=1600,
                sieve_area_m2=6.8,
                grain_tank_capacity_l=12500,
                unloading_rate_l_per_min=158,
                unloading_height_m=5.0,
                unloading_reach_m=7.5,
                overall_length_m=11.5,
                overall_width_m=4.2,
                overall_height_m=4.0,
                ground_clearance_mm=370,
                wheelbase_mm=4300,
                turning_radius_m=7.6,
                theoretical_capacity_tph=55.0,
                typical_capacity_tph=40.0,
                field_efficiency=0.87,
                grain_sample_quality=0.95,
                min_ground_speed_kph=3.2,
                max_ground_speed_kph=38.0,
                optimal_ground_speed_kph=7.0,
                rotor_speed_min_rpm=280,
                rotor_speed_max_rpm=1150,
                compatible_header_types=[HeaderType.GRAIN, HeaderType.FLEX, HeaderType.CORN, HeaderType.DRAPER],
                max_header_width_m=12.8,
                header_lift_capacity_kg=5100,
                new_price_usd=725000,
                depreciation_rate=0.09,
                insurance_rate=0.019,
                maintenance_cost_per_hour=38.2,
                max_slope_degrees=22,
                wet_crop_capability=True,
                dusty_condition_capability=True,
                night_harvesting_capability=True
            )
        ]
        
        # Class 10 combines
        class10_combines = [
            CombineSpecification(
                combine_id="john_deere_s790",
                make="John Deere",
                model="S790",
                year=2024,
                combine_class=CombineClass.CLASS_10,
                engine_power_hp=590,
                engine_power_kw=440,
                fuel_tank_capacity_l=1800,
                fuel_consumption_l_per_hour=85.0,
                transmission_type="CVT",
                threshing_system=ThreshingSystem.ROTARY,
                threshing_width_mm=1676,
                separation_area_m2=8.1,
                cleaning_fan_diameter_mm=1720,
                sieve_area_m2=7.5,
                grain_tank_capacity_l=18900,
                unloading_rate_l_per_min=195,
                unloading_height_m=5.5,
                unloading_reach_m=8.2,
                overall_length_m=12.5,
                overall_width_m=4.6,
                overall_height_m=4.2,
                ground_clearance_mm=400,
                wheelbase_mm=4600,
                turning_radius_m=8.2,
                theoretical_capacity_tph=75.0,
                typical_capacity_tph=58.0,
                field_efficiency=0.90,
                grain_sample_quality=0.96,
                min_ground_speed_kph=4.0,
                max_ground_speed_kph=45.0,
                optimal_ground_speed_kph=8.0,
                rotor_speed_min_rpm=350,
                rotor_speed_max_rpm=1300,
                compatible_header_types=[HeaderType.GRAIN, HeaderType.FLEX, HeaderType.CORN, HeaderType.DRAPER],
                max_header_width_m=15.2,
                header_lift_capacity_kg=6800,
                new_price_usd=895000,
                depreciation_rate=0.08,
                insurance_rate=0.022,
                maintenance_cost_per_hour=58.5,
                max_slope_degrees=22,
                wet_crop_capability=True,
                dusty_condition_capability=True,
                night_harvesting_capability=True
            )
        ]
        
        # Store all specifications
        all_combines = class6_combines + class8_combines + class10_combines
        
        for combine in all_combines:
            self.combine_specifications[combine.combine_id] = combine
        
        print(f"Loaded {len(all_combines)} combine specifications")
    
    def _load_header_specifications(self):
        """Load header specifications"""
        headers = [
            # Grain headers
            HeaderSpecification(
                header_id="john_deere_635f",
                header_type=HeaderType.FLEX,
                make="John Deere",
                model="635F FlexDraper",
                cutting_width_m=10.7,
                transport_width_m=4.3,
                weight_kg=2850,
                height_m=1.8,
                min_cutting_height_cm=2.5,
                max_cutting_height_cm=76.0,
                optimal_ground_speed_kph=6.5,
                max_ground_speed_kph=12.0,
                suitable_crops=["soybeans", "wheat", "barley", "canola"],
                row_spacing_cm=None,
                number_of_rows=None,
                feeding_efficiency=0.92,
                crop_flow_capacity_tph=35.0,
                header_loss_factor=1.2,
                price_new_usd=85000,
                depreciation_rate=0.15,
                maintenance_cost_annual=4500
            ),
            HeaderSpecification(
                header_id="case_ih_3020",
                header_type=HeaderType.GRAIN,
                make="Case IH",
                model="3020 Grain Header",
                cutting_width_m=9.1,
                transport_width_m=4.1,
                weight_kg=2450,
                height_m=1.6,
                min_cutting_height_cm=3.0,
                max_cutting_height_cm=70.0,
                optimal_ground_speed_kph=6.0,
                max_ground_speed_kph=11.0,
                suitable_crops=["wheat", "barley", "oats", "rye"],
                row_spacing_cm=None,
                number_of_rows=None,
                feeding_efficiency=0.88,
                crop_flow_capacity_tph=32.0,
                header_loss_factor=1.5,
                price_new_usd=72000,
                depreciation_rate=0.18,
                maintenance_cost_annual=3800
            ),
            # Corn headers
            HeaderSpecification(
                header_id="john_deere_612c",
                header_type=HeaderType.CORN,
                make="John Deere",
                model="612C Corn Header",
                cutting_width_m=9.1,  # 12 rows × 76cm
                transport_width_m=4.2,
                weight_kg=3850,
                height_m=2.2,
                min_cutting_height_cm=15.0,
                max_cutting_height_cm=85.0,
                optimal_ground_speed_kph=7.2,
                max_ground_speed_kph=10.0,
                suitable_crops=["corn"],
                row_spacing_cm=76.2,
                number_of_rows=12,
                feeding_efficiency=0.94,
                crop_flow_capacity_tph=45.0,
                header_loss_factor=2.5,
                price_new_usd=125000,
                depreciation_rate=0.12,
                maintenance_cost_annual=6800
            ),
            HeaderSpecification(
                header_id="claas_conspeed_8_75",
                header_type=HeaderType.CORN,
                make="CLAAS",
                model="CONSPEED 8-75",
                cutting_width_m=6.0,  # 8 rows × 75cm
                transport_width_m=3.8,
                weight_kg=3250,
                height_m=2.1,
                min_cutting_height_cm=12.0,
                max_cutting_height_cm=80.0,
                optimal_ground_speed_kph=7.5,
                max_ground_speed_kph=11.0,
                suitable_crops=["corn"],
                row_spacing_cm=75.0,
                number_of_rows=8,
                feeding_efficiency=0.93,
                crop_flow_capacity_tph=38.0,
                header_loss_factor=2.2,
                price_new_usd=98000,
                depreciation_rate=0.14,
                maintenance_cost_annual=5500
            ),
            # Draper headers
            HeaderSpecification(
                header_id="macdon_fd75",
                header_type=HeaderType.DRAPER,
                make="MacDon",
                model="FD75 FlexDraper",
                cutting_width_m=12.2,
                transport_width_m=4.5,
                weight_kg=3450,
                height_m=1.9,
                min_cutting_height_cm=2.0,
                max_cutting_height_cm=78.0,
                optimal_ground_speed_kph=8.0,
                max_ground_speed_kph=14.0,
                suitable_crops=["wheat", "barley", "canola", "soybeans"],
                row_spacing_cm=None,
                number_of_rows=None,
                feeding_efficiency=0.96,
                crop_flow_capacity_tph=48.0,
                header_loss_factor=0.8,
                price_new_usd=115000,
                depreciation_rate=0.13,
                maintenance_cost_annual=6200
            )
        ]
        
        for header in headers:
            self.header_specifications[header.header_id] = header
        
        print(f"Loaded {len(headers)} header specifications")
    
    def _initialize_performance_tracking(self):
        """Initialize performance tracking for all combines"""
        for combine_id in self.combine_specifications.keys():
            self.harvest_statistics[combine_id] = {
                'total_hours': 0.0,
                'total_acres_harvested': 0.0,
                'total_grain_harvested': 0.0,
                'average_throughput': 0.0,
                'fuel_efficiency': 0.0,
                'maintenance_cost_per_acre': 0.0,
                'revenue_per_acre': 0.0
            }
    
    def create_combine(self, combine_specification_id: str, farm_location: Tuple[float, float]) -> str:
        """Create a new combine entity"""
        if combine_specification_id not in self.combine_specifications:
            raise ValueError(f"Unknown combine specification: {combine_specification_id}")
        
        spec = self.combine_specifications[combine_specification_id]
        
        # Create combine entity with ECS components
        entity_data = {
            'identity': {
                'name': f"{spec.make} {spec.model}",
                'display_name': f"{spec.make} {spec.model} ({spec.year})",
                'description': f"Class {spec.combine_class.value} combine harvester",
                'tags': {'combine', f'class_{spec.combine_class.value}', spec.make.lower()}
            },
            'transform': {
                'x': farm_location[0],
                'y': farm_location[1]
            },
            'renderable': {
                'sprite_path': f"assets/combines/class_{spec.combine_class.value}.png",
                'layer': 6
            },
            'combine': CombineComponent(specification=spec),
            'equipment': {
                'equipment_type': "combine",
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
        
        # Register combine
        self.active_combines[combine_specification_id] = entity_id
        self.combine_tasks[entity_id] = []
        
        # Emit combine creation event
        self.event_system.emit('combine_created', {
            'entity_id': entity_id,
            'combine_id': combine_specification_id,
            'specification': spec.__dict__,
            'location': farm_location
        }, priority=EventPriority.NORMAL)
        
        print(f"Created combine: {spec.make} {spec.model} at {farm_location}")
        return entity_id
    
    def attach_header(self, combine_entity_id: str, header_specification_id: str) -> bool:
        """Attach a header to a combine"""
        combine_component = self.entity_manager.get_component(combine_entity_id, 'combine')
        if not combine_component:
            return False
        
        if header_specification_id not in self.header_specifications:
            print(f"Unknown header specification: {header_specification_id}")
            return False
        
        header_spec = self.header_specifications[header_specification_id]
        combine_spec = combine_component.specification
        
        # Check header compatibility
        if header_spec.header_type not in combine_spec.compatible_header_types:
            print(f"Header type {header_spec.header_type.value} not compatible with combine")
            return False
        
        if header_spec.cutting_width_m > combine_spec.max_header_width_m:
            print(f"Header width {header_spec.cutting_width_m}m exceeds maximum {combine_spec.max_header_width_m}m")
            return False
        
        # Attach header
        combine_component.header_attached = header_specification_id
        
        # Update component
        self.entity_manager.update_component(combine_entity_id, 'combine', {
            'header_attached': header_specification_id
        })
        
        # Emit header attachment event
        self.event_system.emit('header_attached', {
            'combine_entity_id': combine_entity_id,
            'header_id': header_specification_id,
            'header_type': header_spec.header_type.value,
            'cutting_width_m': header_spec.cutting_width_m
        }, priority=EventPriority.NORMAL)
        
        return True
    
    def start_engine(self, combine_entity_id: str) -> bool:
        """Start combine engine"""
        combine_component = self.entity_manager.get_component(combine_entity_id, 'combine')
        if not combine_component:
            return False
        
        # Check fuel level (simplified - should be tracked separately)
        if combine_component.specification.fuel_tank_capacity_l <= 0:
            print("Cannot start engine - no fuel")
            return False
        
        combine_component.engine_running = True
        combine_component.rotor_speed_rpm = combine_component.specification.rotor_speed_min_rpm
        
        # Update component
        self.entity_manager.update_component(combine_entity_id, 'combine', {
            'engine_running': True,
            'rotor_speed_rpm': combine_component.specification.rotor_speed_min_rpm
        })
        
        # Emit engine start event
        self.event_system.emit('combine_engine_started', {
            'combine_entity_id': combine_entity_id
        }, priority=EventPriority.NORMAL)
        
        return True
    
    def start_harvesting(self, combine_entity_id: str, crop_type: str) -> bool:
        """Start harvesting operation"""
        combine_component = self.entity_manager.get_component(combine_entity_id, 'combine')
        if not combine_component:
            return False
        
        if not combine_component.engine_running:
            print("Engine must be running to start harvesting")
            return False
        
        if not combine_component.header_attached:
            print("Header must be attached to start harvesting")
            return False
        
        # Check header suitability for crop
        header_spec = self.header_specifications[combine_component.header_attached]
        if crop_type not in header_spec.suitable_crops:
            print(f"Attached header not suitable for {crop_type}")
            return False
        
        combine_component.currently_harvesting = True
        
        # Set optimal operational parameters for crop
        optimal_settings = self._get_optimal_settings(combine_component.specification, crop_type)
        combine_component.rotor_speed_rpm = optimal_settings['rotor_speed_rpm']
        combine_component.current_ground_speed_kph = optimal_settings['ground_speed_kph']
        combine_component.fan_speed_rpm = optimal_settings['fan_speed_rpm']
        
        # Update component
        self.entity_manager.update_component(combine_entity_id, 'combine', {
            'currently_harvesting': True,
            'rotor_speed_rpm': combine_component.rotor_speed_rpm,
            'current_ground_speed_kph': combine_component.current_ground_speed_kph,
            'fan_speed_rpm': combine_component.fan_speed_rpm
        })
        
        # Emit harvesting start event
        self.event_system.emit('harvesting_started', {
            'combine_entity_id': combine_entity_id,
            'crop_type': crop_type,
            'header_type': header_spec.header_type.value
        }, priority=EventPriority.NORMAL)
        
        return True
    
    def _get_optimal_settings(self, combine_spec: CombineSpecification, crop_type: str) -> Dict[str, Any]:
        """Get optimal combine settings for specific crop"""
        # Base settings
        settings = {
            'rotor_speed_rpm': (combine_spec.rotor_speed_min_rpm + combine_spec.rotor_speed_max_rpm) // 2,
            'ground_speed_kph': combine_spec.optimal_ground_speed_kph,
            'fan_speed_rpm': 750  # Default fan speed
        }
        
        # Crop-specific adjustments
        if crop_type == "corn":
            settings['rotor_speed_rpm'] = int(combine_spec.rotor_speed_max_rpm * 0.7)
            settings['ground_speed_kph'] = combine_spec.optimal_ground_speed_kph * 0.9
            settings['fan_speed_rpm'] = 650
        elif crop_type == "soybeans":
            settings['rotor_speed_rpm'] = int(combine_spec.rotor_speed_max_rpm * 0.5)
            settings['ground_speed_kph'] = combine_spec.optimal_ground_speed_kph * 1.1
            settings['fan_speed_rpm'] = 800
        elif crop_type == "wheat":
            settings['rotor_speed_rpm'] = int(combine_spec.rotor_speed_max_rpm * 0.8)
            settings['ground_speed_kph'] = combine_spec.optimal_ground_speed_kph
            settings['fan_speed_rpm'] = 750
        
        return settings
    
    def unload_grain_tank(self, combine_entity_id: str) -> Dict[str, Any]:
        """Unload grain tank contents"""
        combine_component = self.entity_manager.get_component(combine_entity_id, 'combine')
        if not combine_component:
            return {'success': False, 'error': 'Combine not found'}
        
        if combine_component.grain_tank_contents_l <= 0:
            return {'success': False, 'error': 'Grain tank is empty'}
        
        # Calculate unloading time
        unload_rate = combine_component.specification.unloading_rate_l_per_min
        unload_time_minutes = combine_component.grain_tank_contents_l / unload_rate
        
        # Store unload details
        unload_result = {
            'success': True,
            'grain_amount_l': combine_component.grain_tank_contents_l,
            'unload_time_minutes': unload_time_minutes,
            'grain_quality': {
                'damage_percent': combine_component.grain_damage_percent,
                'foreign_material_percent': combine_component.foreign_material_percent,
                'moisture_content': combine_component.current_crop_moisture or 15.0
            }
        }
        
        # Empty grain tank
        combine_component.grain_tank_contents_l = 0.0
        combine_component.grain_tank_level_percent = 0.0
        
        # Update component
        self.entity_manager.update_component(combine_entity_id, 'combine', {
            'grain_tank_contents_l': 0.0,
            'grain_tank_level_percent': 0.0
        })
        
        # Emit unload event
        self.event_system.emit('grain_tank_unloaded', {
            'combine_entity_id': combine_entity_id,
            'grain_amount_l': unload_result['grain_amount_l'],
            'unload_time_minutes': unload_time_minutes
        }, priority=EventPriority.NORMAL)
        
        return unload_result
    
    def calculate_custom_harvesting_cost(self, combine_specification_id: str, 
                                        acres_to_harvest: float, crop_type: str) -> Dict[str, float]:
        """Calculate cost for custom harvesting services"""
        if combine_specification_id not in self.combine_specifications:
            return {}
        
        if crop_type not in self.custom_rates:
            return {}
        
        spec = self.combine_specifications[combine_specification_id]
        base_rate = self.custom_rates[crop_type]['rate_per_acre']
        
        # Calculate costs
        harvest_cost = acres_to_harvest * base_rate
        
        # Estimated time (simplified)
        estimated_hours = acres_to_harvest / spec.typical_capacity_tph * 2.47  # acres per hour approximation
        
        # Fuel cost
        fuel_cost = estimated_hours * spec.fuel_consumption_l_per_hour * self.fuel_prices['diesel']
        
        return {
            'base_harvest_cost': harvest_cost,
            'fuel_cost': fuel_cost,
            'total_cost': harvest_cost + fuel_cost,
            'cost_per_acre': (harvest_cost + fuel_cost) / acres_to_harvest,
            'estimated_hours': estimated_hours
        }
    
    def get_ownership_vs_custom_analysis(self, combine_specification_id: str, 
                                        annual_acres: float, crop_types: List[str]) -> Dict[str, Any]:
        """Analyze ownership vs custom harvesting economics"""
        if combine_specification_id not in self.combine_specifications:
            return {}
        
        spec = self.combine_specifications[combine_specification_id]
        
        # Ownership costs (annual)
        purchase_price = spec.new_price_usd
        annual_depreciation = purchase_price * spec.depreciation_rate
        annual_insurance = purchase_price * spec.insurance_rate
        
        # Estimated annual usage hours
        estimated_hours = annual_acres / 15.0  # Rough acres per hour
        annual_fuel_cost = estimated_hours * spec.fuel_consumption_l_per_hour * self.fuel_prices['diesel']
        annual_maintenance = estimated_hours * spec.maintenance_cost_per_hour
        
        total_ownership_cost = annual_depreciation + annual_insurance + annual_fuel_cost + annual_maintenance
        
        # Custom harvesting costs
        custom_cost_total = 0.0
        for crop_type in crop_types:
            if crop_type in self.custom_rates:
                acres_for_crop = annual_acres / len(crop_types)  # Simplified equal distribution
                custom_cost_total += acres_for_crop * self.custom_rates[crop_type]['rate_per_acre']
        
        # Break-even analysis
        ownership_cost_per_acre = total_ownership_cost / annual_acres
        custom_cost_per_acre = custom_cost_total / annual_acres
        
        return {
            'ownership_analysis': {
                'purchase_price': purchase_price,
                'annual_depreciation': annual_depreciation,
                'annual_insurance': annual_insurance,
                'annual_fuel_cost': annual_fuel_cost,
                'annual_maintenance': annual_maintenance,
                'total_annual_cost': total_ownership_cost,
                'cost_per_acre': ownership_cost_per_acre
            },
            'custom_analysis': {
                'total_annual_cost': custom_cost_total,
                'cost_per_acre': custom_cost_per_acre
            },
            'comparison': {
                'ownership_preferred': total_ownership_cost < custom_cost_total,
                'annual_savings': abs(total_ownership_cost - custom_cost_total),
                'break_even_acres': purchase_price / (custom_cost_per_acre - ownership_cost_per_acre) if custom_cost_per_acre != ownership_cost_per_acre else 0,
                'recommendation': 'ownership' if total_ownership_cost < custom_cost_total else 'custom'
            }
        }
    
    def update(self, delta_time: float):
        """Update combine harvester system"""
        if not self.initialized:
            return
        
        # Update all active combines
        for entity_id in self.active_combines.values():
            self._update_combine(entity_id, delta_time)
        
        # Update performance statistics
        self._update_performance_statistics()
    
    def _update_combine(self, entity_id: str, delta_time: float):
        """Update individual combine state"""
        combine_component = self.entity_manager.get_component(entity_id, 'combine')
        if not combine_component or not combine_component.engine_running:
            return
        
        # Update engine hours
        hours_delta = delta_time / 3600.0
        combine_component.total_engine_hours += hours_delta
        combine_component.hours_since_maintenance += hours_delta
        
        # Update fuel consumption
        fuel_consumed = combine_component.specification.fuel_consumption_l_per_hour * hours_delta
        combine_component.fuel_consumed_total_l += fuel_consumed
        combine_component.fuel_cost_total += fuel_consumed * self.fuel_prices['diesel']
        
        if combine_component.currently_harvesting:
            # Simulate grain collection (simplified)
            throughput = combine_component.specification.typical_capacity_tph * hours_delta
            combine_component.total_grain_harvested_tonnes += throughput
            
            # Update grain tank level
            grain_volume = throughput * 1.28  # Convert tonnes to liters (approximate for corn)
            combine_component.grain_tank_contents_l += grain_volume
            combine_component.grain_tank_level_percent = (combine_component.grain_tank_contents_l / 
                                                         combine_component.specification.grain_tank_capacity_l) * 100
            
            # Check tank capacity
            if combine_component.grain_tank_level_percent >= 100:
                combine_component.currently_harvesting = False
                self.event_system.emit('grain_tank_full', {
                    'combine_entity_id': entity_id
                }, priority=EventPriority.HIGH)
        
        # Update maintenance due
        if combine_component.hours_since_maintenance >= 250:  # 250 hours maintenance interval
            combine_component.maintenance_due = True
        
        # Update operational costs
        maintenance_cost = combine_component.specification.maintenance_cost_per_hour * hours_delta
        combine_component.maintenance_cost_total += maintenance_cost
        combine_component.operational_cost_total += fuel_consumed * self.fuel_prices['diesel'] + maintenance_cost
        
        # Update component
        self.entity_manager.update_component(entity_id, 'combine', {
            'total_engine_hours': combine_component.total_engine_hours,
            'hours_since_maintenance': combine_component.hours_since_maintenance,
            'fuel_consumed_total_l': combine_component.fuel_consumed_total_l,
            'fuel_cost_total': combine_component.fuel_cost_total,
            'total_grain_harvested_tonnes': combine_component.total_grain_harvested_tonnes,
            'grain_tank_contents_l': combine_component.grain_tank_contents_l,
            'grain_tank_level_percent': combine_component.grain_tank_level_percent,
            'maintenance_due': combine_component.maintenance_due,
            'operational_cost_total': combine_component.operational_cost_total
        })
    
    def _update_performance_statistics(self):
        """Update performance statistics for all combines"""
        for combine_id, entity_id in self.active_combines.items():
            combine_component = self.entity_manager.get_component(entity_id, 'combine')
            if not combine_component:
                continue
            
            stats = self.harvest_statistics[combine_id]
            stats['total_hours'] = combine_component.total_engine_hours
            stats['total_grain_harvested'] = combine_component.total_grain_harvested_tonnes
            
            # Calculate derived statistics
            if combine_component.total_engine_hours > 0:
                stats['fuel_efficiency'] = combine_component.total_grain_harvested_tonnes / combine_component.fuel_consumed_total_l
            if combine_component.total_acres_harvested > 0:
                stats['maintenance_cost_per_acre'] = combine_component.maintenance_cost_total / combine_component.total_acres_harvested
    
    def _handle_time_advanced(self, event_data: Dict[str, Any]):
        """Handle time advancement events"""
        pass
    
    def _handle_weather_change(self, event_data: Dict[str, Any]):
        """Handle weather change events"""
        # Adjust harvest efficiency based on weather
        pass
    
    def _handle_crop_ready(self, event_data: Dict[str, Any]):
        """Handle crop ready for harvest events"""
        pass
    
    def _handle_grain_price_change(self, event_data: Dict[str, Any]):
        """Handle grain price changes"""
        if 'crop_prices' in event_data:
            self.grain_prices.update(event_data['crop_prices'])
    
    def get_available_combines(self) -> List[Dict[str, Any]]:
        """Get list of available combine specifications"""
        available = []
        
        for combine_id, spec in self.combine_specifications.items():
            available.append({
                'combine_id': combine_id,
                'make': spec.make,
                'model': spec.model,
                'year': spec.year,
                'class': spec.combine_class.value,
                'engine_hp': spec.engine_power_hp,
                'grain_tank_capacity_l': spec.grain_tank_capacity_l,
                'typical_capacity_tph': spec.typical_capacity_tph,
                'price': spec.new_price_usd,
                'compatible_headers': [header.value for header in spec.compatible_header_types]
            })
        
        return available
    
    def get_available_headers(self) -> List[Dict[str, Any]]:
        """Get list of available header specifications"""
        available = []
        
        for header_id, spec in self.header_specifications.items():
            available.append({
                'header_id': header_id,
                'make': spec.make,
                'model': spec.model,
                'type': spec.header_type.value,
                'cutting_width_m': spec.cutting_width_m,
                'suitable_crops': spec.suitable_crops,
                'price': spec.price_new_usd,
                'feeding_efficiency': spec.feeding_efficiency
            })
        
        return available
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive combine system statistics"""
        total_combines = len(self.active_combines)
        total_headers = len(self.header_specifications)
        
        class_distribution = {}
        for spec in self.combine_specifications.values():
            class_key = f"class_{spec.combine_class.value}"
            class_distribution[class_key] = class_distribution.get(class_key, 0) + 1
        
        return {
            'total_combines': total_combines,
            'total_headers': total_headers,
            'available_combine_specs': len(self.combine_specifications),
            'class_distribution': class_distribution,
            'fuel_price_diesel': self.fuel_prices['diesel'],
            'grain_prices': self.grain_prices,
            'custom_rates': self.custom_rates,
            'harvest_statistics': self.harvest_statistics
        }

# Global combine harvester system instance
_global_combine_system: Optional[CombineHarvesterSystem] = None

def get_combine_system() -> CombineHarvesterSystem:
    """Get the global combine system instance"""
    global _global_combine_system
    if _global_combine_system is None:
        _global_combine_system = CombineHarvesterSystem()
        _global_combine_system.initialize()
    return _global_combine_system

def initialize_combine_system() -> CombineHarvesterSystem:
    """Initialize the global combine system"""
    global _global_combine_system
    _global_combine_system = CombineHarvesterSystem()
    _global_combine_system.initialize()
    return _global_combine_system

# Convenience functions
def create_combine(specification_id: str, location: Tuple[float, float] = (8.0, 8.0)) -> str:
    """Convenience function to create a combine"""
    return get_combine_system().create_combine(specification_id, location)

def get_available_combines() -> List[Dict[str, Any]]:
    """Convenience function to get available combines"""
    return get_combine_system().get_available_combines()

def attach_header_to_combine(combine_id: str, header_id: str) -> bool:
    """Convenience function to attach header to combine"""
    return get_combine_system().attach_header(combine_id, header_id)