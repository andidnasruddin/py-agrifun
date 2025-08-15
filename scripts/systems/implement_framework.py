"""
Implement Framework - Comprehensive Agricultural Implement System for AgriFun

This system provides realistic simulation of agricultural implements including tillage,
planting, harvesting, and specialty equipment. Integrates with the Tractor System to
provide complete agricultural machinery workflows.

Key Features:
- Comprehensive implement categories (Tillage, Planting, Harvesting, Specialty)
- Realistic working widths, power requirements, and operational parameters
- Compatibility matrix with tractor categories and specifications
- Performance modeling based on soil conditions and weather
- Economic analysis with purchase vs lease decisions
- Maintenance scheduling and condition tracking
- Educational content about implement selection and usage

Implement Categories:
- Tillage: Plows, Discs, Cultivators, Harrows, Subsoilers
- Planting: Planters, Seeders, Drills, Transplanters
- Harvesting: Combines, Headers, Forage Harvesters, Balers
- Specialty: Sprayers, Spreaders, Mowers, Loaders

Educational Value:
- Understanding of implement selection for different operations
- Power requirements and tractor compatibility
- Economic decision-making for implement acquisition
- Maintenance importance and operational efficiency
- Soil condition impact on implement performance
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

class ImplementCategory(Enum):
    """Agricultural implement categories"""
    TILLAGE = "tillage"           # Soil preparation implements
    PLANTING = "planting"         # Seeding and planting equipment
    HARVESTING = "harvesting"     # Crop harvesting equipment
    SPRAYING = "spraying"         # Chemical application equipment
    SPREADING = "spreading"       # Fertilizer and lime spreading
    MOWING = "mowing"            # Cutting and mowing equipment
    LOADING = "loading"          # Material handling equipment
    SPECIALTY = "specialty"       # Specialized implements

class AttachmentType(Enum):
    """Implement attachment methods"""
    THREE_POINT = "3_point"       # 3-point hitch attachment
    DRAWBAR = "drawbar"          # Drawbar attachment
    FRONT_MOUNT = "front_mount"   # Front-mounted implement
    SELF_PROPELLED = "self_propelled"  # Self-propelled equipment
    PTO_DRIVEN = "pto_driven"     # PTO-powered implement

class SoilCondition(Enum):
    """Soil condition classifications"""
    IDEAL = "ideal"               # Perfect working conditions
    GOOD = "good"                # Good working conditions
    FAIR = "fair"                # Acceptable conditions
    POOR = "poor"                # Challenging conditions
    UNSUITABLE = "unsuitable"     # Cannot operate safely

@dataclass
class ImplementSpecification:
    """Detailed implement specifications and capabilities"""
    # Basic identification
    implement_id: str
    make: str
    model: str
    implement_category: ImplementCategory
    attachment_type: AttachmentType
    
    # Physical specifications
    working_width_m: float          # Working width in meters
    transport_width_m: float        # Transport width in meters
    weight_kg: int                  # Implement weight in kilograms
    length_m: float                 # Overall length in meters
    height_m: float                 # Overall height in meters
    
    # Power requirements
    min_tractor_hp: int            # Minimum tractor horsepower
    recommended_tractor_hp: int    # Recommended tractor horsepower
    max_tractor_hp: Optional[int]  # Maximum tractor horsepower (None if no limit)
    pto_power_required_hp: Optional[int]  # PTO power requirement
    hydraulic_flow_required_lpm: Optional[float]  # Hydraulic flow requirement
    
    # Operational parameters
    working_speed_min_kph: float   # Minimum working speed
    working_speed_max_kph: float   # Maximum working speed
    working_speed_optimal_kph: float  # Optimal working speed
    working_depth_min_cm: Optional[float]  # Minimum working depth
    working_depth_max_cm: Optional[float]  # Maximum working depth
    
    # Performance characteristics
    field_efficiency: float        # Field efficiency factor (0.6-0.9)
    fuel_consumption_factor: float # Fuel consumption multiplier
    soil_disturbance_rating: int   # Soil disturbance level (1-10)
    residue_handling_capability: int  # Crop residue handling (1-10)
    
    # Operational requirements
    required_soil_conditions: List[SoilCondition]  # Acceptable soil conditions
    weather_limitations: Dict[str, Any]  # Weather operation limits
    operator_skill_required: int   # Required operator skill level (1-10)
    setup_time_minutes: int       # Setup/adjustment time
    
    # Maintenance specifications
    maintenance_interval_hours: int  # Hours between maintenance
    maintenance_complexity: int     # Maintenance difficulty (1-10)
    wear_parts_cost_annual: float   # Annual wear parts cost
    
    # Economic data
    new_price_usd: float           # New purchase price
    used_price_range: Tuple[float, float]  # Used price range (min, max)
    depreciation_rate: float       # Annual depreciation rate
    insurance_rate: float          # Insurance as percentage of value
    lease_rate_annual: float       # Annual lease rate as % of new price
    
    # Crop-specific parameters
    suitable_crops: List[str]      # List of suitable crop types
    crop_specific_settings: Dict[str, Dict]  # Crop-specific operational settings
    
    # Compatibility matrix
    compatible_tractor_categories: List[str]  # Compatible tractor categories
    incompatible_implements: List[str]  # Cannot be used with these implements
    required_accessories: List[str]  # Required additional accessories

@dataclass
class ImplementComponent(Component):
    """ECS component for implement-specific data"""
    # Specification reference
    specification: ImplementSpecification
    
    # Current state
    attached_to_tractor: Optional[str] = None
    attachment_point: Optional[str] = None
    currently_working: bool = False
    
    # Operational settings
    current_working_depth_cm: Optional[float] = None
    current_working_speed_kph: float = 0.0
    current_working_width_m: Optional[float] = None
    
    # Performance tracking
    total_working_hours: float = 0.0
    total_area_worked_ha: float = 0.0
    total_distance_worked_km: float = 0.0
    hours_since_maintenance: float = 0.0
    
    # Condition tracking
    wear_level: float = 0.0        # 0.0 = new, 1.0 = completely worn
    maintenance_due: bool = False
    broken_parts: List[str] = field(default_factory=list)
    
    # Economic tracking
    operational_cost_total: float = 0.0
    maintenance_cost_total: float = 0.0
    
    # Performance metrics
    current_efficiency: float = 0.0
    fuel_consumption_multiplier: float = 1.0
    work_quality_rating: float = 0.0
    
    category: ComponentCategory = ComponentCategory.GAMEPLAY

@dataclass
class ImplementTask:
    """Represents a task to be performed with an implement"""
    task_id: str
    operation_type: str            # "tillage", "planting", "harvesting", etc.
    assigned_plots: List[Tuple[int, int]]
    target_depth_cm: Optional[float]
    target_speed_kph: float
    crop_type: Optional[str]
    estimated_time_hours: float
    fuel_requirement_l: float
    priority: int = 1
    weather_requirements: Dict[str, Any] = field(default_factory=dict)
    soil_requirements: List[SoilCondition] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

class ImplementFramework:
    """Comprehensive implement management system"""
    
    def __init__(self):
        """Initialize the implement framework"""
        self.system_name = "implement_framework"
        self.event_system = get_event_system()
        self.entity_manager = get_entity_manager()
        self.config_manager = get_config_manager()
        self.time_manager = get_time_manager()
        
        # Implement management
        self.implement_specifications: Dict[str, ImplementSpecification] = {}
        self.active_implements: Dict[str, str] = {}  # implement_id -> entity_id
        self.implement_tasks: Dict[str, List[ImplementTask]] = {}
        
        # Performance tracking
        self.operational_statistics: Dict[str, Dict] = {}
        self.compatibility_matrix: Dict[str, Dict] = {}
        
        # Economic modeling
        self.lease_rates: Dict[str, float] = {}
        self.maintenance_costs: Dict[str, float] = {}
        
        # System state
        self.initialized = False
        self.update_frequency = 1.0
        
        print("Implement Framework initialized")
    
    def initialize(self) -> bool:
        """Initialize the implement framework with specifications"""
        try:
            # Subscribe to events
            self.event_system.subscribe('time_advanced', self._handle_time_advanced)
            self.event_system.subscribe('weather_updated', self._handle_weather_change)
            self.event_system.subscribe('soil_condition_updated', self._handle_soil_change)
            
            # Load implement specifications
            self._load_implement_specifications()
            
            # Initialize compatibility matrix
            self._initialize_compatibility_matrix()
            
            # Initialize performance tracking
            self._initialize_performance_tracking()
            
            self.initialized = True
            
            # Emit initialization complete event
            self.event_system.emit('implement_framework_initialized', {
                'available_implements': len(self.implement_specifications),
                'categories': len(set(spec.implement_category for spec in self.implement_specifications.values())),
                'system_status': 'ready'
            }, priority=EventPriority.NORMAL)
            
            print("Implement Framework initialization complete")
            return True
            
        except Exception as e:
            print(f"Failed to initialize Implement Framework: {e}")
            return False
    
    def _load_implement_specifications(self):
        """Load implement specifications from data or create defaults"""
        
        # Tillage implements
        tillage_implements = [
            ImplementSpecification(
                implement_id="plow_kuhn_multi_master_183",
                make="Kuhn",
                model="Multi-Master 183",
                implement_category=ImplementCategory.TILLAGE,
                attachment_type=AttachmentType.THREE_POINT,
                working_width_m=4.4,
                transport_width_m=2.5,
                weight_kg=3200,
                length_m=3.8,
                height_m=1.8,
                min_tractor_hp=120,
                recommended_tractor_hp=150,
                max_tractor_hp=200,
                pto_power_required_hp=None,
                hydraulic_flow_required_lpm=40.0,
                working_speed_min_kph=6.0,
                working_speed_max_kph=12.0,
                working_speed_optimal_kph=8.5,
                working_depth_min_cm=15.0,
                working_depth_max_cm=35.0,
                field_efficiency=0.82,
                fuel_consumption_factor=1.4,
                soil_disturbance_rating=9,
                residue_handling_capability=7,
                required_soil_conditions=[SoilCondition.IDEAL, SoilCondition.GOOD, SoilCondition.FAIR],
                weather_limitations={"max_rain_rate_mm": 2.0, "min_temperature_c": -5.0},
                operator_skill_required=6,
                setup_time_minutes=15,
                maintenance_interval_hours=50,
                maintenance_complexity=5,
                wear_parts_cost_annual=2800.0,
                new_price_usd=85000,
                used_price_range=(35000, 65000),
                depreciation_rate=0.12,
                insurance_rate=0.015,
                lease_rate_annual=0.18,
                suitable_crops=["corn", "soybeans", "wheat", "barley"],
                crop_specific_settings={
                    "corn": {"optimal_depth_cm": 25.0, "optimal_speed_kph": 8.0},
                    "soybeans": {"optimal_depth_cm": 20.0, "optimal_speed_kph": 9.0},
                    "wheat": {"optimal_depth_cm": 22.0, "optimal_speed_kph": 8.5}
                },
                compatible_tractor_categories=["utility", "row_crop", "four_wd"],
                incompatible_implements=["disc", "cultivator"],
                required_accessories=["depth_control", "hydraulic_adjustment"]
            ),
            ImplementSpecification(
                implement_id="disc_john_deere_2623",
                make="John Deere",
                model="2623 Disk",
                implement_category=ImplementCategory.TILLAGE,
                attachment_type=AttachmentType.DRAWBAR,
                working_width_m=6.7,
                transport_width_m=4.2,
                weight_kg=4800,
                length_m=4.5,
                height_m=2.1,
                min_tractor_hp=180,
                recommended_tractor_hp=220,
                max_tractor_hp=280,
                pto_power_required_hp=None,
                hydraulic_flow_required_lpm=None,
                working_speed_min_kph=8.0,
                working_speed_max_kph=16.0,
                working_speed_optimal_kph=12.0,
                working_depth_min_cm=5.0,
                working_depth_max_cm=25.0,
                field_efficiency=0.85,
                fuel_consumption_factor=1.2,
                soil_disturbance_rating=6,
                residue_handling_capability=8,
                required_soil_conditions=[SoilCondition.IDEAL, SoilCondition.GOOD],
                weather_limitations={"max_rain_rate_mm": 1.0, "max_wind_speed_kph": 25.0},
                operator_skill_required=4,
                setup_time_minutes=10,
                maintenance_interval_hours=75,
                maintenance_complexity=3,
                wear_parts_cost_annual=1800.0,
                new_price_usd=65000,
                used_price_range=(28000, 45000),
                depreciation_rate=0.15,
                insurance_rate=0.012,
                lease_rate_annual=0.16,
                suitable_crops=["corn", "soybeans", "wheat", "sunflower"],
                crop_specific_settings={
                    "corn": {"optimal_depth_cm": 15.0, "optimal_speed_kph": 11.0},
                    "soybeans": {"optimal_depth_cm": 12.0, "optimal_speed_kph": 13.0}
                },
                compatible_tractor_categories=["row_crop", "four_wd"],
                incompatible_implements=["plow"],
                required_accessories=["transport_wheels"]
            ),
            ImplementSpecification(
                implement_id="cultivator_case_ih_tiger_mate_200",
                make="Case IH",
                model="Tiger-Mate 200",
                implement_category=ImplementCategory.TILLAGE,
                attachment_type=AttachmentType.DRAWBAR,
                working_width_m=6.1,
                transport_width_m=3.8,
                weight_kg=3500,
                length_m=4.2,
                height_m=1.9,
                min_tractor_hp=140,
                recommended_tractor_hp=170,
                max_tractor_hp=220,
                pto_power_required_hp=None,
                hydraulic_flow_required_lpm=25.0,
                working_speed_min_kph=10.0,
                working_speed_max_kph=20.0,
                working_speed_optimal_kph=15.0,
                working_depth_min_cm=3.0,
                working_depth_max_cm=15.0,
                field_efficiency=0.88,
                fuel_consumption_factor=1.0,
                soil_disturbance_rating=4,
                residue_handling_capability=9,
                required_soil_conditions=[SoilCondition.IDEAL, SoilCondition.GOOD, SoilCondition.FAIR],
                weather_limitations={"max_rain_rate_mm": 0.5, "max_wind_speed_kph": 30.0},
                operator_skill_required=3,
                setup_time_minutes=8,
                maintenance_interval_hours=100,
                maintenance_complexity=2,
                wear_parts_cost_annual=1200.0,
                new_price_usd=45000,
                used_price_range=(20000, 32000),
                depreciation_rate=0.18,
                insurance_rate=0.01,
                lease_rate_annual=0.15,
                suitable_crops=["corn", "soybeans", "cotton", "sunflower"],
                crop_specific_settings={
                    "corn": {"optimal_depth_cm": 8.0, "optimal_speed_kph": 16.0},
                    "soybeans": {"optimal_depth_cm": 6.0, "optimal_speed_kph": 18.0}
                },
                compatible_tractor_categories=["utility", "row_crop", "four_wd"],
                incompatible_implements=["plow", "disc"],
                required_accessories=["leveling_harrow"]
            )
        ]
        
        # Planting implements
        planting_implements = [
            ImplementSpecification(
                implement_id="planter_john_deere_1770nt",
                make="John Deere",
                model="1770NT Planter",
                implement_category=ImplementCategory.PLANTING,
                attachment_type=AttachmentType.DRAWBAR,
                working_width_m=5.6,  # 16-row, 76cm spacing
                transport_width_m=4.2,
                weight_kg=5200,
                length_m=6.8,
                height_m=3.2,
                min_tractor_hp=120,
                recommended_tractor_hp=160,
                max_tractor_hp=220,
                pto_power_required_hp=None,
                hydraulic_flow_required_lpm=60.0,
                working_speed_min_kph=6.0,
                working_speed_max_kph=12.0,
                working_speed_optimal_kph=8.5,
                working_depth_min_cm=2.0,
                working_depth_max_cm=8.0,
                field_efficiency=0.80,
                fuel_consumption_factor=1.1,
                soil_disturbance_rating=3,
                residue_handling_capability=8,
                required_soil_conditions=[SoilCondition.IDEAL, SoilCondition.GOOD],
                weather_limitations={"max_rain_rate_mm": 0.0, "min_soil_temp_c": 10.0},
                operator_skill_required=7,
                setup_time_minutes=25,
                maintenance_interval_hours=40,
                maintenance_complexity=8,
                wear_parts_cost_annual=3500.0,
                new_price_usd=165000,
                used_price_range=(75000, 125000),
                depreciation_rate=0.15,
                insurance_rate=0.018,
                lease_rate_annual=0.20,
                suitable_crops=["corn", "soybeans", "sunflower"],
                crop_specific_settings={
                    "corn": {"optimal_depth_cm": 5.0, "optimal_speed_kph": 8.0, "seed_rate": 32000},
                    "soybeans": {"optimal_depth_cm": 3.0, "optimal_speed_kph": 9.0, "seed_rate": 140000}
                },
                compatible_tractor_categories=["utility", "row_crop"],
                incompatible_implements=["drill", "broadcaster"],
                required_accessories=["seed_hoppers", "fertilizer_tanks", "monitor_system"]
            ),
            ImplementSpecification(
                implement_id="drill_case_ih_adc2510",
                make="Case IH",
                model="ADC2510 Air Drill",
                implement_category=ImplementCategory.PLANTING,
                attachment_type=AttachmentType.DRAWBAR,
                working_width_m=7.6,
                transport_width_m=4.5,
                weight_kg=8500,
                length_m=8.2,
                height_m=3.8,
                min_tractor_hp=200,
                recommended_tractor_hp=250,
                max_tractor_hp=350,
                pto_power_required_hp=35,
                hydraulic_flow_required_lpm=80.0,
                working_speed_min_kph=8.0,
                working_speed_max_kph=16.0,
                working_speed_optimal_kph=12.0,
                working_depth_min_cm=1.0,
                working_depth_max_cm=5.0,
                field_efficiency=0.85,
                fuel_consumption_factor=1.3,
                soil_disturbance_rating=2,
                residue_handling_capability=9,
                required_soil_conditions=[SoilCondition.IDEAL, SoilCondition.GOOD, SoilCondition.FAIR],
                weather_limitations={"max_rain_rate_mm": 0.0, "max_wind_speed_kph": 20.0},
                operator_skill_required=6,
                setup_time_minutes=20,
                maintenance_interval_hours=60,
                maintenance_complexity=7,
                wear_parts_cost_annual=2800.0,
                new_price_usd=185000,
                used_price_range=(85000, 140000),
                depreciation_rate=0.12,
                insurance_rate=0.016,
                lease_rate_annual=0.18,
                suitable_crops=["wheat", "barley", "canola", "peas"],
                crop_specific_settings={
                    "wheat": {"optimal_depth_cm": 2.5, "optimal_speed_kph": 12.0, "seed_rate": 90},
                    "barley": {"optimal_depth_cm": 2.0, "optimal_speed_kph": 13.0, "seed_rate": 95}
                },
                compatible_tractor_categories=["row_crop", "four_wd"],
                incompatible_implements=["planter"],
                required_accessories=["air_cart", "seed_monitor", "blockage_sensors"]
            )
        ]
        
        # Harvesting implements
        harvesting_implements = [
            ImplementSpecification(
                implement_id="mower_kuhn_fc_3160",
                make="Kuhn",
                model="FC 3160 Mower",
                implement_category=ImplementCategory.MOWING,
                attachment_type=AttachmentType.THREE_POINT,
                working_width_m=3.16,
                transport_width_m=2.5,
                weight_kg=820,
                length_m=2.2,
                height_m=1.1,
                min_tractor_hp=45,
                recommended_tractor_hp=65,
                max_tractor_hp=90,
                pto_power_required_hp=25,
                hydraulic_flow_required_lpm=None,
                working_speed_min_kph=8.0,
                working_speed_max_kph=18.0,
                working_speed_optimal_kph=12.0,
                working_depth_min_cm=3.0,
                working_depth_max_cm=12.0,
                field_efficiency=0.90,
                fuel_consumption_factor=0.8,
                soil_disturbance_rating=1,
                residue_handling_capability=3,
                required_soil_conditions=[SoilCondition.IDEAL, SoilCondition.GOOD, SoilCondition.FAIR],
                weather_limitations={"max_rain_rate_mm": 1.0, "min_dew_point_c": -5.0},
                operator_skill_required=3,
                setup_time_minutes=5,
                maintenance_interval_hours=25,
                maintenance_complexity=3,
                wear_parts_cost_annual=850.0,
                new_price_usd=18500,
                used_price_range=(8000, 14000),
                depreciation_rate=0.20,
                insurance_rate=0.012,
                lease_rate_annual=0.15,
                suitable_crops=["hay", "grass", "alfalfa"],
                crop_specific_settings={
                    "hay": {"optimal_height_cm": 8.0, "optimal_speed_kph": 12.0},
                    "alfalfa": {"optimal_height_cm": 6.0, "optimal_speed_kph": 10.0}
                },
                compatible_tractor_categories=["compact", "utility"],
                incompatible_implements=["baler"],
                required_accessories=["safety_chains"]
            ),
            ImplementSpecification(
                implement_id="baler_new_holland_bb960a",
                make="New Holland",
                model="BB960A Big Baler",
                implement_category=ImplementCategory.HARVESTING,
                attachment_type=AttachmentType.DRAWBAR,
                working_width_m=2.4,
                transport_width_m=2.55,
                weight_kg=7200,
                length_m=8.5,
                height_m=3.4,
                min_tractor_hp=130,
                recommended_tractor_hp=160,
                max_tractor_hp=200,
                pto_power_required_hp=95,
                hydraulic_flow_required_lpm=None,
                working_speed_min_kph=6.0,
                working_speed_max_kph=15.0,
                working_speed_optimal_kph=10.0,
                working_depth_min_cm=None,
                working_depth_max_cm=None,
                field_efficiency=0.75,
                fuel_consumption_factor=1.5,
                soil_disturbance_rating=1,
                residue_handling_capability=10,
                required_soil_conditions=[SoilCondition.IDEAL, SoilCondition.GOOD],
                weather_limitations={"max_rain_rate_mm": 0.0, "max_humidity_percent": 85},
                operator_skill_required=8,
                setup_time_minutes=30,
                maintenance_interval_hours=35,
                maintenance_complexity=9,
                wear_parts_cost_annual=4200.0,
                new_price_usd=285000,
                used_price_range=(140000, 220000),
                depreciation_rate=0.10,
                insurance_rate=0.020,
                lease_rate_annual=0.22,
                suitable_crops=["hay", "straw", "corn_stalks"],
                crop_specific_settings={
                    "hay": {"optimal_moisture": 15.0, "optimal_speed_kph": 10.0},
                    "straw": {"optimal_moisture": 12.0, "optimal_speed_kph": 12.0}
                },
                compatible_tractor_categories=["utility", "row_crop"],
                incompatible_implements=["mower", "tedder"],
                required_accessories=["twine_boxes", "moisture_sensor", "bale_counter"]
            )
        ]
        
        # Spraying implements
        spraying_implements = [
            ImplementSpecification(
                implement_id="sprayer_apache_as1220",
                make="Apache",
                model="AS1220 Sprayer",
                implement_category=ImplementCategory.SPRAYING,
                attachment_type=AttachmentType.SELF_PROPELLED,
                working_width_m=36.6,  # 120 feet
                transport_width_m=4.3,
                weight_kg=15800,
                length_m=11.2,
                height_m=3.8,
                min_tractor_hp=0,  # Self-propelled
                recommended_tractor_hp=0,
                max_tractor_hp=None,
                pto_power_required_hp=None,
                hydraulic_flow_required_lpm=None,
                working_speed_min_kph=16.0,
                working_speed_max_kph=32.0,
                working_speed_optimal_kph=24.0,
                working_depth_min_cm=None,
                working_depth_max_cm=None,
                field_efficiency=0.90,
                fuel_consumption_factor=2.2,
                soil_disturbance_rating=0,
                residue_handling_capability=10,
                required_soil_conditions=[SoilCondition.IDEAL, SoilCondition.GOOD, SoilCondition.FAIR, SoilCondition.POOR],
                weather_limitations={"max_wind_speed_kph": 15.0, "max_temperature_c": 30.0},
                operator_skill_required=9,
                setup_time_minutes=45,
                maintenance_interval_hours=100,
                maintenance_complexity=8,
                wear_parts_cost_annual=8500.0,
                new_price_usd=475000,
                used_price_range=(220000, 380000),
                depreciation_rate=0.08,
                insurance_rate=0.025,
                lease_rate_annual=0.20,
                suitable_crops=["corn", "soybeans", "wheat", "cotton", "canola"],
                crop_specific_settings={
                    "corn": {"optimal_speed_kph": 22.0, "spray_height_cm": 50.0},
                    "soybeans": {"optimal_speed_kph": 24.0, "spray_height_cm": 40.0}
                },
                compatible_tractor_categories=[],  # Self-propelled
                incompatible_implements=["any"],  # Self-propelled, no attachments
                required_accessories=["gps_guidance", "boom_height_control", "rate_controller"]
            )
        ]
        
        # Store all specifications
        all_implements = (tillage_implements + planting_implements + 
                         harvesting_implements + spraying_implements)
        
        for implement in all_implements:
            self.implement_specifications[implement.implement_id] = implement
        
        print(f"Loaded {len(all_implements)} implement specifications")
    
    def _initialize_compatibility_matrix(self):
        """Initialize tractor-implement compatibility matrix"""
        for implement_id, spec in self.implement_specifications.items():
            self.compatibility_matrix[implement_id] = {
                'compatible_tractors': spec.compatible_tractor_categories.copy(),
                'power_requirements': {
                    'min_hp': spec.min_tractor_hp,
                    'recommended_hp': spec.recommended_tractor_hp,
                    'max_hp': spec.max_tractor_hp,
                    'pto_hp': spec.pto_power_required_hp,
                    'hydraulic_flow': spec.hydraulic_flow_required_lpm
                },
                'attachment_type': spec.attachment_type.value,
                'operational_limits': spec.weather_limitations
            }
    
    def _initialize_performance_tracking(self):
        """Initialize performance tracking for all implements"""
        for implement_id in self.implement_specifications.keys():
            self.operational_statistics[implement_id] = {
                'total_hours': 0.0,
                'total_area_worked': 0.0,
                'maintenance_events': 0,
                'efficiency_average': 0.0,
                'cost_per_hectare': 0.0,
                'downtime_hours': 0.0
            }
    
    def create_implement(self, implement_specification_id: str, farm_location: Tuple[float, float]) -> str:
        """Create a new implement entity"""
        if implement_specification_id not in self.implement_specifications:
            raise ValueError(f"Unknown implement specification: {implement_specification_id}")
        
        spec = self.implement_specifications[implement_specification_id]
        
        # Create implement entity with ECS components
        entity_data = {
            'identity': {
                'name': f"{spec.make} {spec.model}",
                'display_name': f"{spec.make} {spec.model}",
                'description': f"{spec.working_width_m}m {spec.implement_category.value}",
                'tags': {'implement', spec.implement_category.value, spec.make.lower()}
            },
            'transform': {
                'x': farm_location[0],
                'y': farm_location[1]
            },
            'renderable': {
                'sprite_path': f"assets/implements/{spec.implement_category.value}.png",
                'layer': 4
            },
            'implement': ImplementComponent(specification=spec),
            'equipment': {
                'equipment_type': "implement",
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
        
        # Register implement
        self.active_implements[implement_specification_id] = entity_id
        self.implement_tasks[entity_id] = []
        
        # Emit implement creation event
        self.event_system.emit('implement_created', {
            'entity_id': entity_id,
            'implement_id': implement_specification_id,
            'specification': spec.__dict__,
            'location': farm_location
        }, priority=EventPriority.NORMAL)
        
        print(f"Created implement: {spec.make} {spec.model} at {farm_location}")
        return entity_id
    
    def check_tractor_compatibility(self, implement_entity_id: str, 
                                   tractor_specification: Dict[str, Any]) -> Dict[str, Any]:
        """Check if an implement is compatible with a tractor"""
        implement_component = self.entity_manager.get_component(implement_entity_id, 'implement')
        if not implement_component:
            return {'compatible': False, 'reason': 'Implement not found'}
        
        spec = implement_component.specification
        compatibility_result = {
            'compatible': True,
            'warnings': [],
            'requirements_met': {},
            'recommendations': []
        }
        
        # Check power requirements
        tractor_hp = tractor_specification.get('engine_power_hp', 0)
        if tractor_hp < spec.min_tractor_hp:
            compatibility_result['compatible'] = False
            compatibility_result['warnings'].append(
                f"Insufficient power: {tractor_hp} HP < {spec.min_tractor_hp} HP required"
            )
        elif tractor_hp > (spec.max_tractor_hp or float('inf')):
            compatibility_result['warnings'].append(
                f"Excessive power: {tractor_hp} HP > {spec.max_tractor_hp} HP maximum"
            )
        elif tractor_hp < spec.recommended_tractor_hp:
            compatibility_result['recommendations'].append(
                f"Consider higher power: {spec.recommended_tractor_hp} HP recommended"
            )
        
        compatibility_result['requirements_met']['power'] = tractor_hp >= spec.min_tractor_hp
        
        # Check PTO requirements
        if spec.pto_power_required_hp:
            tractor_pto_speeds = tractor_specification.get('pto_speed_rpm', [])
            if not tractor_pto_speeds:
                compatibility_result['compatible'] = False
                compatibility_result['warnings'].append("PTO required but tractor has no PTO")
            compatibility_result['requirements_met']['pto'] = bool(tractor_pto_speeds)
        
        # Check hydraulic requirements
        if spec.hydraulic_flow_required_lpm:
            tractor_flow = tractor_specification.get('hydraulic_flow_lpm', 0)
            if tractor_flow < spec.hydraulic_flow_required_lpm:
                compatibility_result['compatible'] = False
                compatibility_result['warnings'].append(
                    f"Insufficient hydraulic flow: {tractor_flow} LPM < {spec.hydraulic_flow_required_lpm} LPM required"
                )
            compatibility_result['requirements_met']['hydraulics'] = tractor_flow >= spec.hydraulic_flow_required_lpm
        
        # Check hitch compatibility
        tractor_hitch = tractor_specification.get('three_point_hitch_category', '')
        if spec.attachment_type == AttachmentType.THREE_POINT:
            if not tractor_hitch:
                compatibility_result['compatible'] = False
                compatibility_result['warnings'].append("3-point hitch required but tractor has none")
            compatibility_result['requirements_met']['hitch'] = bool(tractor_hitch)
        
        # Check tractor category compatibility
        tractor_category = tractor_specification.get('category', '')
        if tractor_category not in spec.compatible_tractor_categories:
            compatibility_result['warnings'].append(
                f"Tractor category '{tractor_category}' not in recommended categories: {spec.compatible_tractor_categories}"
            )
        
        return compatibility_result
    
    def assign_task(self, implement_entity_id: str, task: ImplementTask) -> bool:
        """Assign a task to an implement"""
        if implement_entity_id not in self.implement_tasks:
            return False
        
        # Validate task requirements
        implement_component = self.entity_manager.get_component(implement_entity_id, 'implement')
        if not implement_component:
            return False
        
        # Check if implement is suitable for task
        spec = implement_component.specification
        if task.crop_type and task.crop_type not in spec.suitable_crops:
            print(f"Implement not suitable for crop: {task.crop_type}")
            return False
        
        # Add task to queue
        self.implement_tasks[implement_entity_id].append(task)
        
        # Emit task assignment event
        self.event_system.emit('implement_task_assigned', {
            'implement_entity_id': implement_entity_id,
            'task_id': task.task_id,
            'operation_type': task.operation_type,
            'plots': len(task.assigned_plots)
        }, priority=EventPriority.NORMAL)
        
        return True
    
    def calculate_operational_cost(self, implement_entity_id: str, 
                                  area_hectares: float, operation_duration_hours: float) -> Dict[str, float]:
        """Calculate operational costs for an implement operation"""
        implement_component = self.entity_manager.get_component(implement_entity_id, 'implement')
        if not implement_component:
            return {}
        
        spec = implement_component.specification
        
        # Calculate costs
        depreciation_cost = (spec.new_price_usd * spec.depreciation_rate / 1000.0) * operation_duration_hours
        insurance_cost = (spec.new_price_usd * spec.insurance_rate / 8760.0) * operation_duration_hours  # Per hour
        maintenance_cost = spec.wear_parts_cost_annual / 1000.0 * operation_duration_hours
        
        total_cost = depreciation_cost + insurance_cost + maintenance_cost
        cost_per_hectare = total_cost / max(area_hectares, 0.01)
        
        return {
            'depreciation_cost': depreciation_cost,
            'insurance_cost': insurance_cost,
            'maintenance_cost': maintenance_cost,
            'total_cost': total_cost,
            'cost_per_hectare': cost_per_hectare,
            'area_worked': area_hectares,
            'duration_hours': operation_duration_hours
        }
    
    def get_purchase_vs_lease_analysis(self, implement_specification_id: str, 
                                     annual_usage_hours: float) -> Dict[str, Any]:
        """Analyze purchase vs lease economics for an implement"""
        if implement_specification_id not in self.implement_specifications:
            return {}
        
        spec = self.implement_specifications[implement_specification_id]
        
        # Purchase analysis (5-year period)
        purchase_price = spec.new_price_usd
        annual_depreciation = purchase_price * spec.depreciation_rate
        annual_insurance = purchase_price * spec.insurance_rate
        annual_maintenance = spec.wear_parts_cost_annual + (annual_usage_hours * spec.maintenance_complexity * 25.0)
        
        total_annual_purchase_cost = annual_depreciation + annual_insurance + annual_maintenance
        five_year_purchase_cost = total_annual_purchase_cost * 5
        
        # Lease analysis
        annual_lease_cost = purchase_price * spec.lease_rate_annual
        five_year_lease_cost = annual_lease_cost * 5
        
        # Cost per hour analysis
        purchase_cost_per_hour = total_annual_purchase_cost / max(annual_usage_hours, 1)
        lease_cost_per_hour = annual_lease_cost / max(annual_usage_hours, 1)
        
        # Break-even analysis
        break_even_hours = annual_lease_cost / (purchase_cost_per_hour - lease_cost_per_hour) if purchase_cost_per_hour != lease_cost_per_hour else 0
        
        return {
            'purchase_analysis': {
                'initial_cost': purchase_price,
                'annual_depreciation': annual_depreciation,
                'annual_insurance': annual_insurance,
                'annual_maintenance': annual_maintenance,
                'total_annual_cost': total_annual_purchase_cost,
                'five_year_cost': five_year_purchase_cost,
                'cost_per_hour': purchase_cost_per_hour
            },
            'lease_analysis': {
                'annual_lease_cost': annual_lease_cost,
                'five_year_cost': five_year_lease_cost,
                'cost_per_hour': lease_cost_per_hour
            },
            'comparison': {
                'purchase_preferred': five_year_purchase_cost < five_year_lease_cost,
                'savings_five_year': abs(five_year_purchase_cost - five_year_lease_cost),
                'break_even_hours': break_even_hours,
                'recommendation': 'purchase' if five_year_purchase_cost < five_year_lease_cost else 'lease'
            }
        }
    
    def update(self, delta_time: float):
        """Update implement framework"""
        if not self.initialized:
            return
        
        # Update all active implements
        for entity_id in self.active_implements.values():
            self._update_implement(entity_id, delta_time)
        
        # Process scheduled maintenance
        self._process_maintenance_schedule()
        
        # Update performance statistics
        self._update_performance_statistics()
    
    def _update_implement(self, entity_id: str, delta_time: float):
        """Update individual implement state"""
        implement_component = self.entity_manager.get_component(entity_id, 'implement')
        if not implement_component or not implement_component.currently_working:
            return
        
        # Update working hours
        hours_delta = delta_time / 3600.0
        implement_component.total_working_hours += hours_delta
        implement_component.hours_since_maintenance += hours_delta
        
        # Calculate area worked (simplified)
        if implement_component.current_working_speed_kph > 0 and implement_component.current_working_width_m:
            distance_km = implement_component.current_working_speed_kph * hours_delta
            area_ha = distance_km * implement_component.current_working_width_m / 10.0  # Convert to hectares
            implement_component.total_area_worked_ha += area_ha
            implement_component.total_distance_worked_km += distance_km
        
        # Update wear level
        wear_factor = implement_component.specification.maintenance_complexity / 1000.0
        implement_component.wear_level += wear_factor * hours_delta
        implement_component.wear_level = min(1.0, implement_component.wear_level)
        
        # Check maintenance due
        if implement_component.hours_since_maintenance >= implement_component.specification.maintenance_interval_hours:
            implement_component.maintenance_due = True
        
        # Update operational costs
        cost_per_hour = implement_component.specification.wear_parts_cost_annual / 8760.0
        implement_component.operational_cost_total += cost_per_hour * hours_delta
        
        # Update component
        self.entity_manager.update_component(entity_id, 'implement', {
            'total_working_hours': implement_component.total_working_hours,
            'total_area_worked_ha': implement_component.total_area_worked_ha,
            'total_distance_worked_km': implement_component.total_distance_worked_km,
            'hours_since_maintenance': implement_component.hours_since_maintenance,
            'wear_level': implement_component.wear_level,
            'maintenance_due': implement_component.maintenance_due,
            'operational_cost_total': implement_component.operational_cost_total
        })
    
    def _process_maintenance_schedule(self):
        """Process scheduled maintenance for all implements"""
        for entity_id in self.active_implements.values():
            implement_component = self.entity_manager.get_component(entity_id, 'implement')
            if not implement_component or not implement_component.maintenance_due:
                continue
            
            # Emit maintenance reminder
            self.event_system.emit('implement_maintenance_due', {
                'implement_entity_id': entity_id,
                'hours_overdue': implement_component.hours_since_maintenance - implement_component.specification.maintenance_interval_hours,
                'estimated_cost': implement_component.specification.wear_parts_cost_annual / 8760.0 * implement_component.specification.maintenance_interval_hours
            }, priority=EventPriority.HIGH)
    
    def _update_performance_statistics(self):
        """Update performance statistics for all implements"""
        for implement_id, entity_id in self.active_implements.items():
            implement_component = self.entity_manager.get_component(entity_id, 'implement')
            if not implement_component:
                continue
            
            stats = self.operational_statistics[implement_id]
            stats['total_hours'] = implement_component.total_working_hours
            stats['total_area_worked'] = implement_component.total_area_worked_ha
            stats['cost_per_hectare'] = (implement_component.operational_cost_total / 
                                       max(implement_component.total_area_worked_ha, 0.01))
    
    def _handle_time_advanced(self, event_data: Dict[str, Any]):
        """Handle time advancement events"""
        pass
    
    def _handle_weather_change(self, event_data: Dict[str, Any]):
        """Handle weather change events"""
        # Adjust operational capabilities based on weather
        pass
    
    def _handle_soil_change(self, event_data: Dict[str, Any]):
        """Handle soil condition changes"""
        # Adjust performance based on soil conditions
        pass
    
    def get_available_implements(self) -> List[Dict[str, Any]]:
        """Get list of available implement specifications"""
        available = []
        
        for implement_id, spec in self.implement_specifications.items():
            available.append({
                'implement_id': implement_id,
                'make': spec.make,
                'model': spec.model,
                'category': spec.implement_category.value,
                'working_width_m': spec.working_width_m,
                'min_tractor_hp': spec.min_tractor_hp,
                'recommended_tractor_hp': spec.recommended_tractor_hp,
                'price': spec.new_price_usd,
                'suitable_crops': spec.suitable_crops,
                'field_efficiency': spec.field_efficiency
            })
        
        return available
    
    def get_implements_by_category(self, category: ImplementCategory) -> List[Dict[str, Any]]:
        """Get implements filtered by category"""
        filtered = []
        
        for implement_id, spec in self.implement_specifications.items():
            if spec.implement_category == category:
                filtered.append({
                    'implement_id': implement_id,
                    'make': spec.make,
                    'model': spec.model,
                    'working_width_m': spec.working_width_m,
                    'min_tractor_hp': spec.min_tractor_hp,
                    'price': spec.new_price_usd,
                    'field_efficiency': spec.field_efficiency
                })
        
        return filtered
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive implement framework statistics"""
        total_implements = len(self.active_implements)
        categories = {}
        
        for spec in self.implement_specifications.values():
            category = spec.implement_category.value
            categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_implements': total_implements,
            'available_specifications': len(self.implement_specifications),
            'categories': categories,
            'operational_statistics': self.operational_statistics,
            'compatibility_matrix': self.compatibility_matrix
        }

# Global implement framework instance
_global_implement_framework: Optional[ImplementFramework] = None

def get_implement_framework() -> ImplementFramework:
    """Get the global implement framework instance"""
    global _global_implement_framework
    if _global_implement_framework is None:
        _global_implement_framework = ImplementFramework()
        _global_implement_framework.initialize()
    return _global_implement_framework

def initialize_implement_framework() -> ImplementFramework:
    """Initialize the global implement framework"""
    global _global_implement_framework
    _global_implement_framework = ImplementFramework()
    _global_implement_framework.initialize()
    return _global_implement_framework

# Convenience functions
def create_implement(specification_id: str, location: Tuple[float, float] = (8.0, 8.0)) -> str:
    """Convenience function to create an implement"""
    return get_implement_framework().create_implement(specification_id, location)

def get_available_implements() -> List[Dict[str, Any]]:
    """Convenience function to get available implements"""
    return get_implement_framework().get_available_implements()

def check_implement_tractor_compatibility(implement_id: str, tractor_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to check tractor compatibility"""
    return get_implement_framework().check_tractor_compatibility(implement_id, tractor_spec)