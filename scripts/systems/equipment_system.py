"""
Equipment & Machinery System - Comprehensive Farm Equipment for AgriFun Agricultural Simulation

This system provides realistic farm equipment and machinery with operational characteristics,
maintenance requirements, and economic factors. Integrates with weather, soil, crop, and
employee systems to create authentic agricultural equipment management gameplay.

Key Features:
- Comprehensive equipment catalog (tractors, implements, harvesters, etc.)
- Realistic operational parameters and fuel consumption
- Equipment condition and maintenance systems
- Weather-dependent operational constraints
- Economic factors (purchase, lease, depreciation, operating costs)
- Equipment-crop compatibility and efficiency modeling

Equipment Categories:
- Tractors: Various horsepower classes with PTO and hydraulic capabilities
- Tillage Equipment: Plows, discs, cultivators, field finishers
- Planting Equipment: Planters, drills, transplanters
- Harvesting Equipment: Combines, forage harvesters, specialty harvesters
- Hay Equipment: Mowers, tedders, rakes, balers
- Material Handling: Loaders, forklifts, conveyors
- Specialty Equipment: Sprayers, spreaders, irrigation systems

Educational Value:
- Real-world equipment specifications and capabilities
- Understanding of equipment selection and optimization
- Maintenance planning and cost management
- Equipment financing and depreciation concepts
- Agricultural mechanization principles

Integration Features:
- Weather System: Weather limitations on equipment operation
- Soil Health System: Soil compaction and structure effects
- Crop System: Equipment-crop compatibility and efficiency
- Employee System: Equipment operator skill requirements
- Economy System: Equipment costs and financing options

Usage Example:
    # Initialize equipment system
    equipment_system = EquipmentSystem()
    await equipment_system.initialize()
    
    # Purchase equipment
    tractor_id = equipment_system.purchase_equipment('john_deere_6120r')
    
    # Assign to field operation
    operation_id = equipment_system.create_field_operation(
        equipment_id=tractor_id,
        implement_id='disc_harrow_24ft',
        field_location='field_a',
        operation_type='tillage'
    )
    
    # Monitor equipment performance
    performance = equipment_system.get_equipment_performance(tractor_id)
"""

from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import logging
from datetime import datetime, timedelta
import json
import math
import random
import uuid

# Import Phase 1 systems
from scripts.core.advanced_event_system import EventSystem, get_event_system
from scripts.core.time_management import TimeManager, get_time_manager, Season
from scripts.core.advanced_config_system import ConfigurationManager, get_config_manager
from scripts.core.content_registry import ContentRegistry, get_content_registry
from scripts.core.entity_component_system import System, Entity

# Phase 3 system imports
from scripts.systems.weather_system import WeatherSystem, get_weather_system, WeatherCondition
from scripts.systems.soil_health_system import SoilHealthSystem, get_soil_health_system

# Configure logging for equipment system
logger = logging.getLogger(__name__)

class EquipmentCategory(Enum):
    """Equipment category classifications"""
    TRACTOR = "tractor"                    # Prime movers
    TILLAGE = "tillage"                   # Soil preparation equipment
    PLANTING = "planting"                 # Seeding and planting equipment
    HARVESTING = "harvesting"             # Crop harvesting equipment
    HAY_FORAGE = "hay_forage"            # Hay and forage equipment
    MATERIAL_HANDLING = "material_handling" # Loaders and handling equipment
    SPRAYING = "spraying"                 # Pesticide application equipment
    SPREADING = "spreading"               # Fertilizer spreading equipment
    IRRIGATION = "irrigation"             # Irrigation systems
    SPECIALTY = "specialty"               # Specialized equipment

class EquipmentCondition(Enum):
    """Equipment condition ratings"""
    EXCELLENT = "excellent"               # 90-100% of original performance
    VERY_GOOD = "very_good"              # 80-89% of original performance  
    GOOD = "good"                        # 70-79% of original performance
    FAIR = "fair"                        # 60-69% of original performance
    POOR = "poor"                        # 50-59% of original performance
    VERY_POOR = "very_poor"              # Below 50% of original performance

class OperationStatus(Enum):
    """Equipment operation status"""
    IDLE = "idle"                        # Equipment not in use
    OPERATING = "operating"              # Currently performing work
    TRANSPORTING = "transporting"        # Moving between locations
    MAINTENANCE = "maintenance"          # Under maintenance/repair
    BREAKDOWN = "breakdown"              # Equipment failure
    STORAGE = "storage"                  # In storage/seasonal

class FinancingType(Enum):
    """Equipment financing options"""
    PURCHASE = "purchase"                # Outright purchase
    LEASE = "lease"                     # Equipment lease
    LOAN = "loan"                       # Financed purchase
    RENTAL = "rental"                   # Short-term rental
    CUSTOM_HIRE = "custom_hire"         # Custom operator service

@dataclass
class EquipmentSpecification:
    """Equipment technical specifications"""
    equipment_id: str                   # Unique equipment identifier
    name: str                          # Equipment name/model
    manufacturer: str                  # Equipment manufacturer
    category: EquipmentCategory        # Equipment category
    
    # Physical specifications
    length: float                      # Length (meters)
    width: float                       # Width (meters)
    height: float                      # Height (meters)
    weight: float                      # Operating weight (kg)
    
    # Performance specifications
    max_speed: float                   # Maximum speed (km/h)
    working_speed: float               # Typical working speed (km/h)
    working_width: float               # Effective working width (meters)
    capacity: float                    # Tank/hopper capacity (liters)
    
    # Power specifications
    engine_power: float                # Engine power (kW)
    pto_power: Optional[float]         # PTO power output (kW)
    hydraulic_flow: Optional[float]    # Hydraulic flow rate (L/min)
    hydraulic_pressure: Optional[float] # Hydraulic pressure (bar)
    
    # Economic specifications
    purchase_price: float              # New purchase price
    annual_depreciation_rate: float    # Annual depreciation rate
    fuel_consumption_rate: float       # Fuel consumption (L/h)
    maintenance_cost_factor: float     # Maintenance cost factor
    
    # Operational requirements
    operator_skill_required: float     # Required operator skill (0.0-1.0)
    weather_limitations: Dict[str, Any] # Weather operational limits
    soil_limitations: Dict[str, Any]   # Soil condition limits
    
    # Compatibility
    compatible_implements: List[str]   # Compatible implement IDs
    required_attachments: List[str]    # Required attachment IDs
    crop_compatibility: Dict[str, float] # Crop-specific efficiency

@dataclass
class EquipmentInstance:
    """Individual equipment instance"""
    instance_id: str                   # Unique instance identifier
    equipment_spec_id: str             # Reference to equipment specification
    
    # Ownership information
    owner: str                        # Owner identifier
    acquisition_date: datetime        # Date acquired
    financing_type: FinancingType     # How equipment was acquired
    
    # Current condition
    condition: EquipmentCondition     # Current condition rating
    condition_score: float            # Numerical condition (0.0-1.0)
    operating_hours: float            # Total operating hours
    last_maintenance: Optional[datetime] # Last maintenance date
    
    # Current status
    status: OperationStatus           # Current operational status
    current_location: Optional[str]   # Current location
    assigned_operator: Optional[str]  # Assigned operator ID
    current_operation: Optional[str]  # Current operation ID
    
    # Performance tracking
    fuel_efficiency: float            # Current fuel efficiency factor
    reliability_score: float          # Reliability rating (0.0-1.0)
    breakdown_count: int              # Number of breakdowns
    maintenance_costs: float          # Cumulative maintenance costs
    
    # Economic tracking
    total_operating_cost: float       # Total operating costs
    annual_depreciation: float        # Annual depreciation amount
    insurance_cost: float             # Annual insurance cost
    
    def calculate_current_value(self, spec: EquipmentSpecification) -> float:
        """Calculate current equipment value"""
        age_years = (datetime.now() - self.acquisition_date).days / 365.25
        depreciated_value = spec.purchase_price * (
            (1 - spec.annual_depreciation_rate) ** age_years
        )
        
        # Adjust for condition
        condition_factors = {
            EquipmentCondition.EXCELLENT: 1.0,
            EquipmentCondition.VERY_GOOD: 0.9,
            EquipmentCondition.GOOD: 0.8,
            EquipmentCondition.FAIR: 0.7,
            EquipmentCondition.POOR: 0.6,
            EquipmentCondition.VERY_POOR: 0.4
        }
        
        condition_factor = condition_factors.get(self.condition, 0.8)
        return depreciated_value * condition_factor
    
    def needs_maintenance(self, spec: EquipmentSpecification) -> bool:
        """Check if equipment needs maintenance"""
        if not self.last_maintenance:
            return self.operating_hours > 50  # First maintenance after 50 hours
        
        # Maintenance intervals based on equipment type
        maintenance_intervals = {
            EquipmentCategory.TRACTOR: 250,      # Every 250 hours
            EquipmentCategory.HARVESTING: 200,   # Every 200 hours
            EquipmentCategory.TILLAGE: 300,      # Every 300 hours
        }
        
        interval = maintenance_intervals.get(spec.category, 250)
        hours_since_maintenance = self.operating_hours - (
            getattr(self, 'last_maintenance_hours', 0)
        )
        
        return hours_since_maintenance >= interval

@dataclass
class FieldOperation:
    """Field operation using equipment"""
    operation_id: str                 # Unique operation identifier
    operation_type: str               # Type of operation (tillage, planting, etc.)
    
    # Equipment and personnel
    primary_equipment_id: str         # Primary equipment instance ID
    implement_ids: List[str]          # Attached implement IDs
    operator_id: Optional[str]        # Operator employee ID
    
    # Location and timing
    field_location: str               # Field/location identifier
    planned_start: datetime           # Planned start time
    actual_start: Optional[datetime]  # Actual start time
    estimated_duration: float         # Estimated duration (hours)
    actual_duration: Optional[float]  # Actual duration (hours)
    
    # Operation parameters
    area_to_cover: float              # Area to cover (hectares)
    working_speed: float              # Planned working speed (km/h)
    working_depth: Optional[float]    # Working depth (cm)
    
    # Environmental conditions
    weather_conditions: Optional[Dict[str, Any]] # Weather during operation
    soil_conditions: Optional[Dict[str, Any]]    # Soil conditions during operation
    
    # Performance results
    area_completed: float             # Actual area completed (hectares)
    fuel_consumed: float              # Fuel consumed (liters)
    efficiency: float                 # Operation efficiency (0.0-1.0)
    quality_rating: float             # Work quality rating (0.0-1.0)
    
    # Status tracking
    status: str                       # Operation status
    completion_percentage: float      # Completion percentage
    issues_encountered: List[str]     # Issues during operation

@dataclass
class MaintenanceRecord:
    """Equipment maintenance record"""
    maintenance_id: str               # Unique maintenance identifier
    equipment_id: str                 # Equipment instance ID
    maintenance_type: str             # Type of maintenance
    
    # Scheduling
    scheduled_date: datetime          # Scheduled maintenance date
    actual_date: Optional[datetime]   # Actual maintenance date
    duration_hours: float             # Maintenance duration
    
    # Details
    description: str                  # Maintenance description
    parts_replaced: List[str]         # Parts that were replaced
    labor_hours: float               # Labor hours required
    
    # Costs
    parts_cost: float                # Cost of parts
    labor_cost: float                # Cost of labor
    total_cost: float                # Total maintenance cost
    
    # Technician information
    technician: str                  # Technician identifier
    shop_location: str               # Maintenance location
    
    # Results
    condition_before: float          # Equipment condition before maintenance
    condition_after: float           # Equipment condition after maintenance
    issues_resolved: List[str]       # Issues that were resolved
    recommendations: List[str]       # Future maintenance recommendations

class EquipmentSystem(System):
    """
    Equipment & Machinery System - Comprehensive farm equipment management
    
    This system manages realistic farm equipment with operational characteristics,
    maintenance requirements, economic factors, and agricultural integration.
    """
    
    def __init__(self):
        """Initialize the Equipment System"""
        super().__init__()
        self.system_name = "equipment_system"
        
        # Core system references
        self.event_system: Optional[EventSystem] = None
        self.time_manager: Optional[TimeManager] = None
        self.config_manager: Optional[ConfigurationManager] = None
        self.content_registry: Optional[ContentRegistry] = None
        self.weather_system: Optional[WeatherSystem] = None
        self.soil_system: Optional[SoilHealthSystem] = None
        
        # Equipment management
        self.equipment_specs: Dict[str, EquipmentSpecification] = {}
        self.equipment_instances: Dict[str, EquipmentInstance] = {}
        self.field_operations: Dict[str, FieldOperation] = {}
        self.maintenance_records: Dict[str, List[MaintenanceRecord]] = {}
        
        # System parameters
        self.update_frequency = 0.5  # Update every 30 minutes
        self.last_update_time = 0.0
        
        # Economic parameters
        self.fuel_price_per_liter = 1.2  # Base fuel price
        self.labor_rate_per_hour = 25.0  # Labor cost per hour
        
        # Performance tracking
        self.operation_efficiency_factors: Dict[str, float] = {}
        self.weather_penalties: Dict[str, float] = {}
        
        logger.info("Equipment System initialized")
    
    def initialize(self) -> bool:
        """Initialize the equipment system with required dependencies"""
        try:
            # Get system references
            self.event_system = get_event_system()
            self.time_manager = get_time_manager()
            self.config_manager = get_config_manager()
            self.content_registry = get_content_registry()
            self.weather_system = get_weather_system()
            self.soil_system = get_soil_health_system()
            
            # Load equipment specifications
            self._load_equipment_specifications()
            
            # Load configuration
            self._load_configuration()
            
            # Subscribe to relevant events
            self._subscribe_to_events()
            
            logger.info("Equipment System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Equipment System: {e}")
            return False
    
    def _load_equipment_specifications(self):
        """Load equipment specifications from content registry"""
        try:
            # Load equipment data from content registry
            equipment_data = self.content_registry.get_content("equipment", {})
            
            for equipment_id, data in equipment_data.items():
                self.equipment_specs[equipment_id] = EquipmentSpecification(
                    equipment_id=equipment_id,
                    name=data["name"],
                    manufacturer=data["manufacturer"],
                    category=EquipmentCategory(data["category"]),
                    length=data["dimensions"]["length"],
                    width=data["dimensions"]["width"],
                    height=data["dimensions"]["height"],
                    weight=data["weight"],
                    max_speed=data["performance"]["max_speed"],
                    working_speed=data["performance"]["working_speed"],
                    working_width=data["performance"]["working_width"],
                    capacity=data["performance"].get("capacity", 0.0),
                    engine_power=data["engine"]["power"],
                    pto_power=data["engine"].get("pto_power"),
                    hydraulic_flow=data.get("hydraulics", {}).get("flow"),
                    hydraulic_pressure=data.get("hydraulics", {}).get("pressure"),
                    purchase_price=data["economics"]["purchase_price"],
                    annual_depreciation_rate=data["economics"]["depreciation_rate"],
                    fuel_consumption_rate=data["economics"]["fuel_consumption"],
                    maintenance_cost_factor=data["economics"]["maintenance_factor"],
                    operator_skill_required=data["requirements"]["operator_skill"],
                    weather_limitations=data["requirements"]["weather_limits"],
                    soil_limitations=data["requirements"]["soil_limits"],
                    compatible_implements=data.get("compatibility", {}).get("implements", []),
                    required_attachments=data.get("compatibility", {}).get("required", []),
                    crop_compatibility=data.get("compatibility", {}).get("crops", {})
                )
            
            # Create default specifications if none loaded
            if not self.equipment_specs:
                self._create_default_equipment_specs()
            
            logger.info(f"Loaded {len(self.equipment_specs)} equipment specifications")
            
        except Exception as e:
            logger.error(f"Failed to load equipment specifications: {e}")
            self._create_default_equipment_specs()
    
    def _create_default_equipment_specs(self):
        """Create default equipment specifications"""
        # Create basic tractor specification
        self.equipment_specs["tractor_mid_size"] = EquipmentSpecification(
            equipment_id="tractor_mid_size",
            name="Mid-Size Farm Tractor",
            manufacturer="Generic Farm Equipment",
            category=EquipmentCategory.TRACTOR,
            length=5.5,
            width=2.4,
            height=3.0,
            weight=6500.0,
            max_speed=40.0,
            working_speed=12.0,
            working_width=0.0,  # Not applicable for tractors
            capacity=200.0,  # Fuel tank capacity
            engine_power=120.0,  # 120 kW
            pto_power=100.0,
            hydraulic_flow=85.0,
            hydraulic_pressure=210.0,
            purchase_price=85000.0,
            annual_depreciation_rate=0.12,
            fuel_consumption_rate=18.0,
            maintenance_cost_factor=0.03,
            operator_skill_required=0.7,
            weather_limitations={
                "min_temperature": -20.0,
                "max_temperature": 45.0,
                "max_wind_speed": 20.0,
                "max_precipitation": 5.0
            },
            soil_limitations={
                "max_moisture": 0.8,
                "min_bearing_capacity": 0.3
            },
            compatible_implements=["plow_4_bottom", "disc_harrow", "planter_8_row"],
            required_attachments=[],
            crop_compatibility={"corn": 1.0, "soybeans": 1.0, "wheat": 1.0}
        )
        
        # Create basic plow specification
        self.equipment_specs["plow_4_bottom"] = EquipmentSpecification(
            equipment_id="plow_4_bottom",
            name="4-Bottom Moldboard Plow",
            manufacturer="Generic Implements",
            category=EquipmentCategory.TILLAGE,
            length=4.0,
            width=1.8,
            height=1.5,
            weight=1800.0,
            max_speed=12.0,
            working_speed=8.0,
            working_width=1.4,  # 4 bottoms × 35cm each
            capacity=0.0,
            engine_power=0.0,  # Implement doesn't have engine
            pto_power=None,
            hydraulic_flow=None,
            hydraulic_pressure=None,
            purchase_price=15000.0,
            annual_depreciation_rate=0.08,
            fuel_consumption_rate=0.0,  # Uses tractor fuel
            maintenance_cost_factor=0.02,
            operator_skill_required=0.6,
            weather_limitations={
                "max_precipitation": 2.0,
                "max_wind_speed": 25.0
            },
            soil_limitations={
                "max_moisture": 0.6,
                "min_temperature": -5.0
            },
            compatible_implements=[],
            required_attachments=["tractor_3pt_hitch"],
            crop_compatibility={"corn": 0.9, "soybeans": 0.9, "wheat": 0.8}
        )
        
        logger.info("Created default equipment specifications")
    
    def _subscribe_to_events(self):
        """Subscribe to relevant system events"""
        if self.event_system:
            # Time-based events
            self.event_system.subscribe("time_advanced", self._on_time_advanced)
            self.event_system.subscribe("day_changed", self._on_day_changed)
            
            # Weather events
            self.event_system.subscribe("weather_updated", self._on_weather_updated)
            
            # Agricultural events
            self.event_system.subscribe("field_operation_requested", self._on_field_operation_requested)
            self.event_system.subscribe("equipment_maintenance_due", self._on_maintenance_due)
    
    def _load_configuration(self):
        """Load system configuration parameters"""
        if self.config_manager:
            config = self.config_manager.get_config("equipment_system", {})
            
            self.update_frequency = config.get("update_frequency", 0.5)
            self.fuel_price_per_liter = config.get("fuel_price", 1.2)
            self.labor_rate_per_hour = config.get("labor_rate", 25.0)
    
    def update(self, delta_time: float):
        """Update equipment operations and conditions"""
        try:
            # Check if it's time for update
            current_time = self.time_manager.get_game_time_hours() if self.time_manager else 0.0
            if current_time - self.last_update_time < self.update_frequency:
                return
            
            self.last_update_time = current_time
            
            # Update active field operations
            self._update_field_operations(delta_time)
            
            # Update equipment conditions
            self._update_equipment_conditions(delta_time)
            
            # Check maintenance schedules
            self._check_maintenance_schedules()
            
            # Update economic factors
            self._update_economic_factors()
            
        except Exception as e:
            logger.error(f"Error updating equipment system: {e}")
    
    def purchase_equipment(self, equipment_spec_id: str, financing_type: FinancingType = FinancingType.PURCHASE) -> str:
        """Purchase or acquire new equipment"""
        try:
            if equipment_spec_id not in self.equipment_specs:
                raise ValueError(f"Unknown equipment specification: {equipment_spec_id}")
            
            spec = self.equipment_specs[equipment_spec_id]
            instance_id = str(uuid.uuid4())
            current_time = self.time_manager.get_current_time() if self.time_manager else datetime.now()
            
            # Create equipment instance
            equipment_instance = EquipmentInstance(
                instance_id=instance_id,
                equipment_spec_id=equipment_spec_id,
                owner="player",  # Simplified ownership
                acquisition_date=current_time,
                financing_type=financing_type,
                condition=EquipmentCondition.EXCELLENT,
                condition_score=1.0,
                operating_hours=0.0,
                last_maintenance=None,
                status=OperationStatus.IDLE,
                current_location=None,
                assigned_operator=None,
                current_operation=None,
                fuel_efficiency=1.0,
                reliability_score=1.0,
                breakdown_count=0,
                maintenance_costs=0.0,
                total_operating_cost=0.0,
                annual_depreciation=spec.purchase_price * spec.annual_depreciation_rate,
                insurance_cost=spec.purchase_price * 0.015  # 1.5% of purchase price
            )
            
            self.equipment_instances[instance_id] = equipment_instance
            
            # Initialize maintenance records
            self.maintenance_records[instance_id] = []
            
            # Publish equipment purchased event
            if self.event_system:
                self.event_system.publish("equipment_purchased", {
                    "instance_id": instance_id,
                    "equipment_spec_id": equipment_spec_id,
                    "purchase_price": spec.purchase_price,
                    "financing_type": financing_type.value
                })
            
            logger.info(f"Purchased equipment: {spec.name} (ID: {instance_id})")
            return instance_id
            
        except Exception as e:
            logger.error(f"Failed to purchase equipment {equipment_spec_id}: {e}")
            raise
    
    def create_field_operation(self, primary_equipment_id: str, field_location: str,
                             operation_type: str, area_hectares: float,
                             implement_ids: Optional[List[str]] = None) -> str:
        """Create a new field operation"""
        try:
            if primary_equipment_id not in self.equipment_instances:
                raise ValueError(f"Equipment instance not found: {primary_equipment_id}")
            
            equipment = self.equipment_instances[primary_equipment_id]
            spec = self.equipment_specs[equipment.equipment_spec_id]
            
            # Check equipment availability
            if equipment.status != OperationStatus.IDLE:
                raise ValueError(f"Equipment is not available (status: {equipment.status.value})")
            
            # Check weather suitability
            if not self._check_weather_suitability(spec):
                raise ValueError("Weather conditions unsuitable for operation")
            
            operation_id = str(uuid.uuid4())
            current_time = self.time_manager.get_current_time() if self.time_manager else datetime.now()
            
            # Calculate operation parameters
            working_width = spec.working_width
            if implement_ids:
                # Adjust working width based on implements
                for implement_id in implement_ids:
                    if implement_id in self.equipment_specs:
                        impl_spec = self.equipment_specs[implement_id]
                        working_width = max(working_width, impl_spec.working_width)
            
            # Calculate estimated duration
            working_speed = spec.working_speed
            if working_width > 0 and working_speed > 0:
                # Area coverage rate (hectares per hour)
                coverage_rate = (working_width / 1000.0) * working_speed  # Convert to hectares
                estimated_duration = area_hectares / coverage_rate
            else:
                estimated_duration = area_hectares * 2.0  # Default 2 hours per hectare
            
            # Create field operation
            operation = FieldOperation(
                operation_id=operation_id,
                operation_type=operation_type,
                primary_equipment_id=primary_equipment_id,
                implement_ids=implement_ids or [],
                operator_id=None,  # To be assigned
                field_location=field_location,
                planned_start=current_time,
                actual_start=None,
                estimated_duration=estimated_duration,
                actual_duration=None,
                area_to_cover=area_hectares,
                working_speed=working_speed,
                working_depth=None,  # To be determined by operation type
                weather_conditions=None,
                soil_conditions=None,
                area_completed=0.0,
                fuel_consumed=0.0,
                efficiency=0.0,
                quality_rating=0.0,
                status="planned",
                completion_percentage=0.0,
                issues_encountered=[]
            )
            
            self.field_operations[operation_id] = operation
            
            # Update equipment status
            equipment.current_operation = operation_id
            
            # Publish operation created event
            if self.event_system:
                self.event_system.publish("field_operation_created", {
                    "operation_id": operation_id,
                    "operation_type": operation_type,
                    "equipment_id": primary_equipment_id,
                    "field_location": field_location,
                    "estimated_duration": estimated_duration
                })
            
            logger.info(f"Created field operation: {operation_type} at {field_location}")
            return operation_id
            
        except Exception as e:
            logger.error(f"Failed to create field operation: {e}")
            raise
    
    def start_field_operation(self, operation_id: str, operator_id: Optional[str] = None) -> bool:
        """Start a field operation"""
        try:
            if operation_id not in self.field_operations:
                raise ValueError(f"Operation not found: {operation_id}")
            
            operation = self.field_operations[operation_id]
            equipment = self.equipment_instances[operation.primary_equipment_id]
            spec = self.equipment_specs[equipment.equipment_spec_id]
            
            # Final checks before starting
            if not self._check_weather_suitability(spec):
                return False
            
            if equipment.condition == EquipmentCondition.VERY_POOR:
                operation.issues_encountered.append("Equipment in poor condition")
                return False
            
            # Start the operation
            current_time = self.time_manager.get_current_time() if self.time_manager else datetime.now()
            operation.actual_start = current_time
            operation.operator_id = operator_id
            operation.status = "active"
            
            # Get current weather and soil conditions
            if self.weather_system:
                current_weather = self.weather_system.get_current_weather()
                if current_weather:
                    operation.weather_conditions = {
                        "temperature": current_weather.temperature,
                        "humidity": current_weather.humidity,
                        "wind_speed": current_weather.wind_speed,
                        "precipitation": current_weather.precipitation_rate
                    }
            
            if self.soil_system:
                soil_info = self.soil_system.get_soil_health_summary(operation.field_location)
                if soil_info:
                    operation.soil_conditions = {
                        "moisture": soil_info["physical"]["current_moisture"],
                        "compaction": soil_info["physical"]["compaction_level"],
                        "temperature": soil_info["chemistry"].get("soil_temperature", 15.0)
                    }
            
            # Update equipment status
            equipment.status = OperationStatus.OPERATING
            
            # Publish operation started event
            if self.event_system:
                self.event_system.publish("field_operation_started", {
                    "operation_id": operation_id,
                    "equipment_id": operation.primary_equipment_id,
                    "operator_id": operator_id,
                    "start_time": current_time.isoformat()
                })
            
            logger.info(f"Started field operation {operation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start field operation {operation_id}: {e}")
            return False
    
    def _check_weather_suitability(self, spec: EquipmentSpecification) -> bool:
        """Check if current weather is suitable for equipment operation"""
        if not self.weather_system:
            return True  # Assume suitable if no weather data
        
        current_weather = self.weather_system.get_current_weather()
        if not current_weather:
            return True
        
        limits = spec.weather_limitations
        
        # Check temperature limits
        if "min_temperature" in limits and current_weather.temperature < limits["min_temperature"]:
            return False
        if "max_temperature" in limits and current_weather.temperature > limits["max_temperature"]:
            return False
        
        # Check wind speed limits
        if "max_wind_speed" in limits and current_weather.wind_speed > limits["max_wind_speed"]:
            return False
        
        # Check precipitation limits
        if "max_precipitation" in limits and current_weather.precipitation_rate > limits["max_precipitation"]:
            return False
        
        return True
    
    def _update_field_operations(self, delta_time: float):
        """Update active field operations"""
        current_time = self.time_manager.get_current_time() if self.time_manager else datetime.now()
        
        for operation_id, operation in list(self.field_operations.items()):
            if operation.status != "active":
                continue
            
            try:
                self._update_operation_progress(operation, delta_time)
                
                # Check if operation is complete
                if operation.completion_percentage >= 100.0:
                    self._complete_field_operation(operation_id)
                
            except Exception as e:
                logger.error(f"Error updating operation {operation_id}: {e}")
                operation.issues_encountered.append(f"Update error: {str(e)}")
    
    def _update_operation_progress(self, operation: FieldOperation, delta_time: float):
        """Update progress of an active operation"""
        if not operation.actual_start:
            return
        
        equipment = self.equipment_instances[operation.primary_equipment_id]
        spec = self.equipment_specs[equipment.equipment_spec_id]
        
        # Calculate base progress rate
        working_width = spec.working_width
        working_speed = operation.working_speed
        
        if working_width > 0 and working_speed > 0:
            # Area coverage rate (hectares per hour)
            base_coverage_rate = (working_width / 1000.0) * working_speed
        else:
            base_coverage_rate = 0.5  # Default coverage rate
        
        # Apply efficiency factors
        efficiency_factor = self._calculate_operation_efficiency(operation, equipment, spec)
        actual_coverage_rate = base_coverage_rate * efficiency_factor
        
        # Update progress
        progress_hours = delta_time
        area_covered_this_update = actual_coverage_rate * progress_hours
        
        operation.area_completed += area_covered_this_update
        operation.completion_percentage = min(100.0, 
                                            (operation.area_completed / operation.area_to_cover) * 100.0)
        
        # Update fuel consumption
        fuel_rate = spec.fuel_consumption_rate * efficiency_factor
        operation.fuel_consumed += fuel_rate * progress_hours
        
        # Update equipment operating hours
        equipment.operating_hours += progress_hours
        
        # Update equipment condition (wear and tear)
        wear_rate = 0.001 * (1.0 + (1.0 - efficiency_factor))  # More wear under poor conditions
        equipment.condition_score = max(0.0, equipment.condition_score - wear_rate * progress_hours)
        
        # Update condition rating based on score
        if equipment.condition_score >= 0.9:
            equipment.condition = EquipmentCondition.EXCELLENT
        elif equipment.condition_score >= 0.8:
            equipment.condition = EquipmentCondition.VERY_GOOD
        elif equipment.condition_score >= 0.7:
            equipment.condition = EquipmentCondition.GOOD
        elif equipment.condition_score >= 0.6:
            equipment.condition = EquipmentCondition.FAIR
        elif equipment.condition_score >= 0.5:
            equipment.condition = EquipmentCondition.POOR
        else:
            equipment.condition = EquipmentCondition.VERY_POOR
        
        # Calculate current efficiency and quality
        operation.efficiency = efficiency_factor
        operation.quality_rating = self._calculate_work_quality(operation, equipment, spec)
    
    def _calculate_operation_efficiency(self, operation: FieldOperation, 
                                      equipment: EquipmentInstance,
                                      spec: EquipmentSpecification) -> float:
        """Calculate operation efficiency based on various factors"""
        base_efficiency = 1.0
        
        # Equipment condition factor
        condition_factor = equipment.condition_score
        
        # Weather factor
        weather_factor = 1.0
        if operation.weather_conditions:
            # Temperature effects
            temp = operation.weather_conditions["temperature"]
            if temp < -10 or temp > 35:
                weather_factor *= 0.8
            elif temp < 0 or temp > 30:
                weather_factor *= 0.9
            
            # Wind effects
            wind_speed = operation.weather_conditions["wind_speed"]
            if wind_speed > 15:
                weather_factor *= 0.8
            elif wind_speed > 10:
                weather_factor *= 0.9
            
            # Precipitation effects
            precip = operation.weather_conditions["precipitation"]
            if precip > 2:
                weather_factor *= 0.7
            elif precip > 0.5:
                weather_factor *= 0.85
        
        # Soil factor
        soil_factor = 1.0
        if operation.soil_conditions:
            # Moisture effects
            moisture = operation.soil_conditions["moisture"]
            if moisture > 0.8:  # Too wet
                soil_factor *= 0.6
            elif moisture < 0.2:  # Too dry
                soil_factor *= 0.8
            elif 0.4 <= moisture <= 0.7:  # Optimal range
                soil_factor *= 1.1
            
            # Compaction effects
            compaction = operation.soil_conditions["compaction"]
            if compaction > 0.7:
                soil_factor *= 0.8
        
        # Operator skill factor (if available)
        operator_factor = 1.0
        if operation.operator_id:
            # This would integrate with employee system
            operator_factor = 0.9  # Assume moderate skill for now
        
        # Crop compatibility factor
        if operation.operation_type in ["planting", "harvesting"]:
            # This would need crop information
            crop_factor = 0.95  # Assume reasonable compatibility
        else:
            crop_factor = 1.0
        
        # Calculate overall efficiency
        overall_efficiency = (base_efficiency * condition_factor * weather_factor * 
                            soil_factor * operator_factor * crop_factor)
        
        return max(0.1, min(1.5, overall_efficiency))  # Clamp between 10% and 150%
    
    def _calculate_work_quality(self, operation: FieldOperation, 
                              equipment: EquipmentInstance, spec: EquipmentSpecification) -> float:
        """Calculate work quality rating"""
        base_quality = 0.8
        
        # Equipment condition affects quality
        condition_quality = equipment.condition_score
        
        # Weather affects quality
        weather_quality = 1.0
        if operation.weather_conditions:
            if operation.weather_conditions["wind_speed"] > 12:
                weather_quality *= 0.9  # Wind affects precision
            if operation.weather_conditions["precipitation"] > 1:
                weather_quality *= 0.8  # Rain affects quality
        
        # Soil conditions affect quality
        soil_quality = 1.0
        if operation.soil_conditions:
            moisture = operation.soil_conditions["moisture"]
            if 0.4 <= moisture <= 0.7:  # Optimal soil moisture
                soil_quality *= 1.1
            elif moisture > 0.8 or moisture < 0.2:
                soil_quality *= 0.8
        
        # Speed affects quality (too fast reduces quality)
        speed_quality = 1.0
        if operation.working_speed > spec.working_speed * 1.2:
            speed_quality = 0.85  # Working too fast reduces quality
        elif operation.working_speed < spec.working_speed * 0.8:
            speed_quality = 0.95  # Working too slow slightly reduces efficiency
        
        overall_quality = base_quality * condition_quality * weather_quality * soil_quality * speed_quality
        return max(0.0, min(1.0, overall_quality))
    
    def _complete_field_operation(self, operation_id: str):
        """Complete a field operation"""
        try:
            operation = self.field_operations[operation_id]
            equipment = self.equipment_instances[operation.primary_equipment_id]
            
            current_time = self.time_manager.get_current_time() if self.time_manager else datetime.now()
            
            # Calculate actual duration
            if operation.actual_start:
                operation.actual_duration = (current_time - operation.actual_start).total_seconds() / 3600.0
            
            # Finalize operation
            operation.status = "completed"
            operation.completion_percentage = 100.0
            
            # Update equipment status
            equipment.status = OperationStatus.IDLE
            equipment.current_operation = None
            
            # Calculate operating costs
            fuel_cost = operation.fuel_consumed * self.fuel_price_per_liter
            operator_cost = (operation.actual_duration or 0) * self.labor_rate_per_hour
            maintenance_cost = equipment.operating_hours * 0.5  # Simplified
            
            total_cost = fuel_cost + operator_cost + maintenance_cost
            equipment.total_operating_cost += total_cost
            
            # Publish operation completed event
            if self.event_system:
                self.event_system.publish("field_operation_completed", {
                    "operation_id": operation_id,
                    "equipment_id": operation.primary_equipment_id,
                    "area_completed": operation.area_completed,
                    "duration_hours": operation.actual_duration,
                    "fuel_consumed": operation.fuel_consumed,
                    "efficiency": operation.efficiency,
                    "quality_rating": operation.quality_rating,
                    "total_cost": total_cost
                })
            
            logger.info(f"Completed field operation {operation_id}: "
                       f"{operation.area_completed:.1f} hectares in "
                       f"{operation.actual_duration:.1f} hours")
            
        except Exception as e:
            logger.error(f"Failed to complete operation {operation_id}: {e}")
    
    def _update_equipment_conditions(self, delta_time: float):
        """Update equipment conditions over time"""
        for equipment_id, equipment in self.equipment_instances.items():
            try:
                # Equipment deteriorates slowly even when idle
                if equipment.status == OperationStatus.IDLE:
                    idle_deterioration = 0.0001 * delta_time  # Very slow deterioration
                    equipment.condition_score = max(0.0, equipment.condition_score - idle_deterioration)
                
                # Check for random breakdowns based on condition and hours
                breakdown_probability = self._calculate_breakdown_probability(equipment)
                if random.random() < breakdown_probability * delta_time:
                    self._trigger_equipment_breakdown(equipment_id)
                
            except Exception as e:
                logger.error(f"Error updating condition for equipment {equipment_id}: {e}")
    
    def _calculate_breakdown_probability(self, equipment: EquipmentInstance) -> float:
        """Calculate probability of equipment breakdown"""
        base_probability = 0.001  # 0.1% per hour base probability
        
        # Condition factor (worse condition = higher breakdown chance)
        condition_factor = (1.0 - equipment.condition_score) * 2.0
        
        # Hours factor (more hours = higher breakdown chance)
        hours_factor = min(2.0, equipment.operating_hours / 5000.0)
        
        # Reliability factor
        reliability_factor = (1.0 - equipment.reliability_score)
        
        total_probability = base_probability * (1.0 + condition_factor + hours_factor + reliability_factor)
        
        return min(0.1, total_probability)  # Cap at 10% per hour
    
    def _trigger_equipment_breakdown(self, equipment_id: str):
        """Trigger equipment breakdown"""
        equipment = self.equipment_instances[equipment_id]
        
        equipment.status = OperationStatus.BREAKDOWN
        equipment.breakdown_count += 1
        equipment.reliability_score = max(0.0, equipment.reliability_score - 0.05)
        
        # If equipment was in operation, stop it
        if equipment.current_operation:
            operation = self.field_operations[equipment.current_operation]
            operation.status = "interrupted"
            operation.issues_encountered.append("Equipment breakdown")
        
        # Publish breakdown event
        if self.event_system:
            self.event_system.publish("equipment_breakdown", {
                "equipment_id": equipment_id,
                "condition": equipment.condition.value,
                "operating_hours": equipment.operating_hours,
                "breakdown_count": equipment.breakdown_count
            })
        
        logger.warning(f"Equipment breakdown: {equipment_id}")
    
    def _check_maintenance_schedules(self):
        """Check if any equipment needs maintenance"""
        for equipment_id, equipment in self.equipment_instances.items():
            try:
                spec = self.equipment_specs[equipment.equipment_spec_id]
                
                if equipment.needs_maintenance(spec):
                    # Schedule maintenance
                    self._schedule_maintenance(equipment_id, "routine")
                
            except Exception as e:
                logger.error(f"Error checking maintenance for {equipment_id}: {e}")
    
    def _schedule_maintenance(self, equipment_id: str, maintenance_type: str):
        """Schedule maintenance for equipment"""
        equipment = self.equipment_instances[equipment_id]
        spec = self.equipment_specs[equipment.equipment_spec_id]
        
        current_time = self.time_manager.get_current_time() if self.time_manager else datetime.now()
        
        maintenance_id = str(uuid.uuid4())
        
        # Calculate maintenance parameters
        if maintenance_type == "routine":
            duration_hours = 4.0
            parts_cost = spec.purchase_price * 0.01  # 1% of purchase price
            labor_hours = 4.0
        elif maintenance_type == "repair":
            duration_hours = 8.0
            parts_cost = spec.purchase_price * 0.03  # 3% of purchase price
            labor_hours = 8.0
        else:
            duration_hours = 2.0
            parts_cost = spec.purchase_price * 0.005  # 0.5% of purchase price
            labor_hours = 2.0
        
        labor_cost = labor_hours * self.labor_rate_per_hour
        total_cost = parts_cost + labor_cost
        
        maintenance_record = MaintenanceRecord(
            maintenance_id=maintenance_id,
            equipment_id=equipment_id,
            maintenance_type=maintenance_type,
            scheduled_date=current_time + timedelta(days=1),  # Schedule for tomorrow
            actual_date=None,
            duration_hours=duration_hours,
            description=f"Scheduled {maintenance_type} maintenance",
            parts_replaced=[],
            labor_hours=labor_hours,
            parts_cost=parts_cost,
            labor_cost=labor_cost,
            total_cost=total_cost,
            technician="shop_technician",
            shop_location="main_shop",
            condition_before=equipment.condition_score,
            condition_after=0.0,  # Will be updated after maintenance
            issues_resolved=[],
            recommendations=[]
        )
        
        # Add to maintenance records
        if equipment_id not in self.maintenance_records:
            self.maintenance_records[equipment_id] = []
        
        self.maintenance_records[equipment_id].append(maintenance_record)
        
        # Publish maintenance scheduled event
        if self.event_system:
            self.event_system.publish("maintenance_scheduled", {
                "equipment_id": equipment_id,
                "maintenance_id": maintenance_id,
                "maintenance_type": maintenance_type,
                "scheduled_date": maintenance_record.scheduled_date.isoformat(),
                "estimated_cost": total_cost
            })
        
        logger.info(f"Scheduled {maintenance_type} maintenance for equipment {equipment_id}")
    
    def perform_maintenance(self, maintenance_id: str) -> bool:
        """Perform scheduled maintenance"""
        try:
            # Find maintenance record
            maintenance_record = None
            equipment_id = None
            
            for eq_id, records in self.maintenance_records.items():
                for record in records:
                    if record.maintenance_id == maintenance_id:
                        maintenance_record = record
                        equipment_id = eq_id
                        break
                if maintenance_record:
                    break
            
            if not maintenance_record or not equipment_id:
                raise ValueError(f"Maintenance record not found: {maintenance_id}")
            
            equipment = self.equipment_instances[equipment_id]
            current_time = self.time_manager.get_current_time() if self.time_manager else datetime.now()
            
            # Perform maintenance
            maintenance_record.actual_date = current_time
            maintenance_record.condition_before = equipment.condition_score
            
            # Improve equipment condition based on maintenance type
            if maintenance_record.maintenance_type == "routine":
                condition_improvement = 0.1
            elif maintenance_record.maintenance_type == "repair":
                condition_improvement = 0.3
            else:
                condition_improvement = 0.05
            
            equipment.condition_score = min(1.0, equipment.condition_score + condition_improvement)
            equipment.last_maintenance = current_time
            maintenance_record.condition_after = equipment.condition_score
            
            # Update equipment status
            if equipment.status == OperationStatus.BREAKDOWN:
                equipment.status = OperationStatus.IDLE
                equipment.reliability_score = min(1.0, equipment.reliability_score + 0.1)
                maintenance_record.issues_resolved.append("Equipment breakdown repaired")
            
            # Update costs
            equipment.maintenance_costs += maintenance_record.total_cost
            
            # Publish maintenance completed event
            if self.event_system:
                self.event_system.publish("maintenance_completed", {
                    "equipment_id": equipment_id,
                    "maintenance_id": maintenance_id,
                    "condition_improvement": condition_improvement,
                    "total_cost": maintenance_record.total_cost
                })
            
            logger.info(f"Completed maintenance {maintenance_id} for equipment {equipment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to perform maintenance {maintenance_id}: {e}")
            return False
    
    def _update_economic_factors(self):
        """Update economic factors like depreciation"""
        current_time = self.time_manager.get_current_time() if self.time_manager else datetime.now()
        
        for equipment_id, equipment in self.equipment_instances.items():
            try:
                # Calculate age in years
                age_years = (current_time - equipment.acquisition_date).days / 365.25
                
                # Update annual depreciation (pro-rated)
                if age_years > 0:
                    spec = self.equipment_specs[equipment.equipment_spec_id]
                    annual_depreciation = spec.purchase_price * spec.annual_depreciation_rate
                    equipment.annual_depreciation = annual_depreciation
                
            except Exception as e:
                logger.error(f"Error updating economic factors for {equipment_id}: {e}")
    
    # Event handlers
    def _on_time_advanced(self, event_data: Dict[str, Any]):
        """Handle time advancement"""
        delta_hours = event_data.get("delta_hours", 1.0)
        self.update(delta_hours)
    
    def _on_day_changed(self, event_data: Dict[str, Any]):
        """Handle day change events"""
        # Daily equipment checks and updates
        self._check_maintenance_schedules()
    
    def _on_weather_updated(self, event_data: Dict[str, Any]):
        """Handle weather updates"""
        weather_data = event_data.get("weather", {})
        
        # Check if any active operations need to be suspended due to weather
        for operation_id, operation in self.field_operations.items():
            if operation.status == "active":
                equipment = self.equipment_instances[operation.primary_equipment_id]
                spec = self.equipment_specs[equipment.equipment_spec_id]
                
                if not self._check_weather_suitability(spec):
                    # Suspend operation due to weather
                    operation.status = "suspended"
                    operation.issues_encountered.append("Suspended due to weather conditions")
                    
                    if self.event_system:
                        self.event_system.publish("field_operation_suspended", {
                            "operation_id": operation_id,
                            "reason": "weather_conditions"
                        })
    
    def _on_field_operation_requested(self, event_data: Dict[str, Any]):
        """Handle field operation requests"""
        try:
            equipment_id = event_data.get("equipment_id")
            field_location = event_data.get("field_location")
            operation_type = event_data.get("operation_type")
            area_hectares = event_data.get("area_hectares", 1.0)
            
            if equipment_id and field_location and operation_type:
                operation_id = self.create_field_operation(
                    primary_equipment_id=equipment_id,
                    field_location=field_location,
                    operation_type=operation_type,
                    area_hectares=area_hectares
                )
                
                # Auto-start if requested
                if event_data.get("auto_start", False):
                    self.start_field_operation(operation_id)
            
        except Exception as e:
            logger.error(f"Error handling field operation request: {e}")
    
    def _on_maintenance_due(self, event_data: Dict[str, Any]):
        """Handle maintenance due notifications"""
        equipment_id = event_data.get("equipment_id")
        maintenance_type = event_data.get("maintenance_type", "routine")
        
        if equipment_id in self.equipment_instances:
            self._schedule_maintenance(equipment_id, maintenance_type)
    
    # Public interface methods
    def get_available_equipment(self, category: Optional[EquipmentCategory] = None) -> List[Dict[str, Any]]:
        """Get list of available equipment"""
        available_equipment = []
        
        for instance_id, equipment in self.equipment_instances.items():
            if equipment.status not in [OperationStatus.IDLE, OperationStatus.STORAGE]:
                continue
            
            spec = self.equipment_specs[equipment.equipment_spec_id]
            
            if category and spec.category != category:
                continue
            
            available_equipment.append({
                "instance_id": instance_id,
                "spec_id": equipment.equipment_spec_id,
                "name": spec.name,
                "category": spec.category.value,
                "condition": equipment.condition.value,
                "condition_score": equipment.condition_score,
                "operating_hours": equipment.operating_hours,
                "current_location": equipment.current_location
            })
        
        return available_equipment
    
    def get_equipment_performance(self, equipment_id: str) -> Optional[Dict[str, Any]]:
        """Get equipment performance metrics"""
        if equipment_id not in self.equipment_instances:
            return None
        
        equipment = self.equipment_instances[equipment_id]
        spec = self.equipment_specs[equipment.equipment_spec_id]
        
        # Calculate performance metrics
        current_value = equipment.calculate_current_value(spec)
        
        return {
            "instance_id": equipment_id,
            "name": spec.name,
            "condition": {
                "rating": equipment.condition.value,
                "score": equipment.condition_score,
                "needs_maintenance": equipment.needs_maintenance(spec)
            },
            "performance": {
                "operating_hours": equipment.operating_hours,
                "fuel_efficiency": equipment.fuel_efficiency,
                "reliability_score": equipment.reliability_score,
                "breakdown_count": equipment.breakdown_count
            },
            "economics": {
                "current_value": current_value,
                "purchase_price": spec.purchase_price,
                "total_operating_cost": equipment.total_operating_cost,
                "maintenance_costs": equipment.maintenance_costs,
                "annual_depreciation": equipment.annual_depreciation
            },
            "status": {
                "current_status": equipment.status.value,
                "current_operation": equipment.current_operation,
                "assigned_operator": equipment.assigned_operator
            }
        }
    
    def get_field_operation_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get field operation status"""
        if operation_id not in self.field_operations:
            return None
        
        operation = self.field_operations[operation_id]
        
        return {
            "operation_id": operation_id,
            "operation_type": operation.operation_type,
            "status": operation.status,
            "progress": {
                "completion_percentage": operation.completion_percentage,
                "area_completed": operation.area_completed,
                "area_to_cover": operation.area_to_cover
            },
            "timing": {
                "planned_start": operation.planned_start.isoformat(),
                "actual_start": operation.actual_start.isoformat() if operation.actual_start else None,
                "estimated_duration": operation.estimated_duration,
                "actual_duration": operation.actual_duration
            },
            "performance": {
                "efficiency": operation.efficiency,
                "quality_rating": operation.quality_rating,
                "fuel_consumed": operation.fuel_consumed
            },
            "conditions": {
                "weather": operation.weather_conditions,
                "soil": operation.soil_conditions
            },
            "issues": operation.issues_encountered
        }
    
    def get_maintenance_schedule(self, equipment_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get maintenance schedule"""
        schedule = []
        
        equipment_list = [equipment_id] if equipment_id else list(self.maintenance_records.keys())
        
        for eq_id in equipment_list:
            if eq_id in self.maintenance_records:
                for record in self.maintenance_records[eq_id]:
                    schedule.append({
                        "maintenance_id": record.maintenance_id,
                        "equipment_id": eq_id,
                        "maintenance_type": record.maintenance_type,
                        "scheduled_date": record.scheduled_date.isoformat(),
                        "actual_date": record.actual_date.isoformat() if record.actual_date else None,
                        "estimated_cost": record.total_cost,
                        "status": "completed" if record.actual_date else "scheduled"
                    })
        
        # Sort by scheduled date
        schedule.sort(key=lambda x: x["scheduled_date"])
        return schedule
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive equipment system status"""
        active_operations = sum(1 for op in self.field_operations.values() if op.status == "active")
        equipment_breakdown = sum(1 for eq in self.equipment_instances.values() 
                                if eq.status == OperationStatus.BREAKDOWN)
        
        return {
            "system_name": self.system_name,
            "equipment_inventory": {
                "total_equipment": len(self.equipment_instances),
                "equipment_by_category": {
                    category.value: sum(1 for eq in self.equipment_instances.values()
                                      if self.equipment_specs[eq.equipment_spec_id].category == category)
                    for category in EquipmentCategory
                },
                "equipment_in_breakdown": equipment_breakdown
            },
            "operations": {
                "active_operations": active_operations,
                "total_operations": len(self.field_operations),
                "completed_operations": sum(1 for op in self.field_operations.values() 
                                          if op.status == "completed")
            },
            "maintenance": {
                "equipment_needing_maintenance": sum(1 for eq in self.equipment_instances.values()
                                                   if eq.needs_maintenance(self.equipment_specs[eq.equipment_spec_id])),
                "scheduled_maintenance": sum(len(records) for records in self.maintenance_records.values())
            },
            "economics": {
                "total_equipment_value": sum(eq.calculate_current_value(self.equipment_specs[eq.equipment_spec_id])
                                           for eq in self.equipment_instances.values()),
                "total_operating_costs": sum(eq.total_operating_cost for eq in self.equipment_instances.values()),
                "fuel_price_per_liter": self.fuel_price_per_liter
            },
            "update_frequency": self.update_frequency,
            "last_update": self.last_update_time
        }

# Global convenience functions for system access
_equipment_system_instance = None

def get_equipment_system() -> EquipmentSystem:
    """Get the global Equipment System instance"""
    global _equipment_system_instance
    if _equipment_system_instance is None:
        _equipment_system_instance = EquipmentSystem()
    return _equipment_system_instance

def initialize_equipment_system() -> bool:
    """Initialize the global Equipment System"""
    system = get_equipment_system()
    return system.initialize()

def get_available_tractors() -> List[Dict[str, Any]]:
    """Convenience function to get available tractors"""
    system = get_equipment_system()
    return system.get_available_equipment(EquipmentCategory.TRACTOR)

def purchase_tractor(spec_id: str) -> str:
    """Convenience function to purchase a tractor"""
    system = get_equipment_system()
    return system.purchase_equipment(spec_id, FinancingType.PURCHASE)

def create_tillage_operation(tractor_id: str, field_id: str, area: float) -> str:
    """Convenience function to create tillage operation"""
    system = get_equipment_system()
    return system.create_field_operation(tractor_id, field_id, "tillage", area)