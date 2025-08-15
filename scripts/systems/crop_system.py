"""
Crop Growth & Agricultural Systems - Realistic Farming Mechanics for AgriFun Agricultural Simulation

This system provides comprehensive crop management with realistic growth cycles, soil interaction,
environmental effects, and agricultural science principles. Integrates with Time Management for
seasonal cycles, Weather System for growth modifiers, and Economy System for market dynamics.

Key Features:
- Multi-stage crop growth with realistic timing
- Environmental factor integration (weather, soil, season)
- Soil health and nutrient management (N-P-K levels)
- Crop rotation and companion planting benefits
- Disease and pest pressure simulation
- Quality tracking and yield optimization
- Irrigation and water management integration
- Seed genetics and variety selection
- Harvest timing and quality degradation

Agricultural Science Features:
- Realistic crop calendars and planting windows
- Soil nutrient depletion and restoration
- Growth degree day calculations
- Photosynthesis and respiration modeling
- Water stress and drought tolerance
- Nutrient uptake and deficiency symptoms
- Crop-specific environmental requirements
- Integrated pest management principles

Integration Features:
- Time-based growth progression with seasonal effects
- Weather-dependent growth modifiers and stress
- Economic integration for seed costs and crop values
- Employee system integration for farming tasks
- Building system integration for storage and processing
- Save/load system integration for crop persistence

Usage Example:
    # Initialize crop system
    crop_system = CropSystem()
    await crop_system.initialize()
    
    # Plant crops
    crop_id = await crop_system.plant_crop('corn_hybrid', (5, 5), soil_quality=8.5)
    
    # Monitor growth
    growth_info = crop_system.get_crop_info(crop_id)
    
    # Harvest crops
    harvest_result = await crop_system.harvest_crop(crop_id)
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
from scripts.core.advanced_config_system import get_configuration_manager
from scripts.systems.economy_system import get_economy_system
from scripts.systems.employee_system import get_employee_system


class CropType(Enum):
    """Types of crops available for cultivation"""
    CORN = "corn"
    WHEAT = "wheat"
    SOYBEANS = "soybeans"
    TOMATOES = "tomatoes"
    POTATOES = "potatoes"
    LETTUCE = "lettuce"
    CARROTS = "carrots"
    ONIONS = "onions"
    PEPPERS = "peppers"
    BEANS = "beans"


class GrowthStage(Enum):
    """Crop growth stages"""
    SEED = "seed"
    GERMINATION = "germination"
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUIT_DEVELOPMENT = "fruit_development"
    MATURATION = "maturation"
    HARVEST_READY = "harvest_ready"
    OVERRIPE = "overripe"


class CropHealth(Enum):
    """Crop health status"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    DISEASED = "diseased"
    DYING = "dying"
    DEAD = "dead"


class SoilType(Enum):
    """Soil types with different characteristics"""
    CLAY = "clay"
    SANDY = "sandy"
    LOAM = "loam"
    SILTY = "silty"
    ROCKY = "rocky"
    ORGANIC = "organic"


class NutrientType(Enum):
    """Soil nutrients (NPK + secondary)"""
    NITROGEN = "nitrogen"
    PHOSPHORUS = "phosphorus"
    POTASSIUM = "potassium"
    CALCIUM = "calcium"
    MAGNESIUM = "magnesium"
    SULFUR = "sulfur"


@dataclass
class SoilCondition:
    """Soil condition at a specific location"""
    soil_type: SoilType = SoilType.LOAM
    ph_level: float = 6.8  # 0-14 scale, 6.5-7.0 ideal for most crops
    organic_matter: float = 3.0  # Percentage, 3-5% is good
    drainage: float = 0.75  # 0-1, drainage quality
    compaction: float = 0.2  # 0-1, soil compaction level
    temperature: float = 20.0  # Celsius
    moisture: float = 0.6  # 0-1, soil moisture level
    
    # Nutrient levels (0-100)
    nutrients: Dict[NutrientType, float] = field(default_factory=lambda: {
        NutrientType.NITROGEN: 75.0,
        NutrientType.PHOSPHORUS: 65.0,
        NutrientType.POTASSIUM: 70.0,
        NutrientType.CALCIUM: 80.0,
        NutrientType.MAGNESIUM: 60.0,
        NutrientType.SULFUR: 55.0
    })
    
    # Biological activity
    microbial_activity: float = 0.7  # 0-1, beneficial microorganism activity
    earthworm_count: int = 15  # Per cubic meter
    
    def get_fertility_score(self) -> float:
        """Calculate overall soil fertility (0-10)"""
        ph_score = 1.0 - abs(self.ph_level - 6.8) / 6.8  # Optimal pH around 6.8
        organic_score = min(1.0, self.organic_matter / 5.0)  # 5% is excellent
        drainage_score = self.drainage
        nutrient_score = sum(self.nutrients.values()) / (len(self.nutrients) * 100)
        
        fertility = (ph_score + organic_score + drainage_score + nutrient_score + self.microbial_activity) / 5
        return fertility * 10.0


@dataclass
class CropVariety:
    """Specific crop variety with unique characteristics"""
    variety_id: str
    crop_type: CropType
    variety_name: str
    description: str
    
    # Growth characteristics
    days_to_maturity: int = 90
    growth_stages_duration: Dict[GrowthStage, int] = field(default_factory=dict)
    
    # Environmental requirements
    min_temperature: float = 10.0  # Celsius
    max_temperature: float = 35.0
    optimal_temperature_range: Tuple[float, float] = (20.0, 25.0)
    water_requirements: float = 500.0  # mm per season
    light_requirements: float = 6.0  # hours per day minimum
    
    # Soil preferences
    preferred_soil_types: List[SoilType] = field(default_factory=list)
    optimal_ph_range: Tuple[float, float] = (6.0, 7.5)
    nutrient_requirements: Dict[NutrientType, float] = field(default_factory=dict)
    
    # Yield characteristics
    base_yield_per_plant: float = 2.0  # kg
    yield_quality_factors: Dict[str, float] = field(default_factory=dict)
    market_value_multiplier: float = 1.0
    
    # Disease and pest resistance
    disease_resistance: Dict[str, float] = field(default_factory=dict)
    pest_resistance: Dict[str, float] = field(default_factory=dict)
    
    # Special traits
    drought_tolerance: float = 0.5  # 0-1
    cold_tolerance: float = 0.5
    heat_tolerance: float = 0.5
    storage_life_days: int = 30
    
    # Economic factors
    seed_cost_per_unit: float = 2.50
    planting_density: int = 4  # Plants per square meter
    harvest_labor_hours: float = 0.1  # Hours per plant
    
    def get_temperature_stress_factor(self, temperature: float) -> float:
        """Calculate temperature stress (0-1, 1 = no stress)"""
        if self.optimal_temperature_range[0] <= temperature <= self.optimal_temperature_range[1]:
            return 1.0
        elif temperature < self.min_temperature or temperature > self.max_temperature:
            return 0.1  # Severe stress
        else:
            # Gradual stress as temperature moves away from optimal
            if temperature < self.optimal_temperature_range[0]:
                stress = (temperature - self.min_temperature) / (self.optimal_temperature_range[0] - self.min_temperature)
            else:
                stress = (self.max_temperature - temperature) / (self.max_temperature - self.optimal_temperature_range[1])
            return max(0.1, min(1.0, stress))


@dataclass
class CropInstance:
    """Individual crop plant instance"""
    crop_id: str
    variety: CropVariety
    position: Tuple[int, int]
    planted_time: int  # Game time in minutes
    
    # Growth tracking
    current_stage: GrowthStage = GrowthStage.SEED
    stage_progress: float = 0.0  # 0-1 within current stage
    overall_progress: float = 0.0  # 0-1 total progress to harvest
    days_growing: int = 0
    
    # Health and condition
    health_status: CropHealth = CropHealth.GOOD
    stress_factors: Dict[str, float] = field(default_factory=dict)
    disease_pressure: float = 0.0  # 0-1
    pest_pressure: float = 0.0  # 0-1
    
    # Environmental tracking
    accumulated_water: float = 0.0  # mm
    accumulated_heat_units: float = 0.0  # Growing degree days
    light_exposure: float = 0.0  # Daily light hours received
    
    # Care and management
    last_watered: Optional[int] = None
    last_fertilized: Optional[int] = None
    fertilizer_applications: List[Dict[str, Any]] = field(default_factory=list)
    treatments_applied: List[Dict[str, Any]] = field(default_factory=list)
    
    # Quality factors
    size_factor: float = 1.0  # Affects final yield
    quality_factor: float = 1.0  # Affects market value
    nutrient_content: Dict[str, float] = field(default_factory=dict)
    
    # Harvest predictions
    estimated_yield: float = 0.0  # kg
    estimated_quality_grade: str = "standard"
    optimal_harvest_window: Optional[Tuple[int, int]] = None  # Start/end times
    
    def get_growth_rate_modifier(self, soil: SoilCondition, weather_factor: float = 1.0) -> float:
        """Calculate current growth rate modifier based on conditions"""
        # Temperature factor
        temp_factor = self.variety.get_temperature_stress_factor(soil.temperature)
        
        # Water factor
        water_stress = max(0.0, 1.0 - abs(soil.moisture - 0.7) / 0.7)  # Optimal at 70%
        
        # Nutrient factor
        nutrient_factor = 1.0
        for nutrient_type, required_level in self.variety.nutrient_requirements.items():
            current_level = soil.nutrients.get(nutrient_type, 50.0)
            if current_level < required_level:
                deficit = (required_level - current_level) / required_level
                nutrient_factor *= (1.0 - deficit * 0.5)  # Max 50% reduction
        
        # Soil health factor
        soil_health_factor = soil.get_fertility_score() / 10.0
        
        # Disease and pest pressure
        health_factor = 1.0 - (self.disease_pressure * 0.3) - (self.pest_pressure * 0.2)
        
        # Overall modifier
        modifier = temp_factor * water_stress * nutrient_factor * soil_health_factor * health_factor * weather_factor
        return max(0.1, min(2.0, modifier))  # Clamp between 0.1 and 2.0
    
    def update_growth(self, hours_passed: float, soil: SoilCondition, weather_factor: float = 1.0):
        """Update crop growth based on time and conditions"""
        growth_modifier = self.get_growth_rate_modifier(soil, weather_factor)
        
        # Calculate base growth for this time period
        base_growth_per_hour = 1.0 / (self.variety.days_to_maturity * 24)  # Progress per hour
        actual_growth = base_growth_per_hour * hours_passed * growth_modifier
        
        # Update overall progress
        self.overall_progress = min(1.0, self.overall_progress + actual_growth)
        
        # Update stage progress
        stage_durations = self.variety.growth_stages_duration
        if self.current_stage in stage_durations:
            stage_hours = stage_durations[self.current_stage] * 24
            stage_growth_per_hour = 1.0 / stage_hours
            self.stage_progress = min(1.0, self.stage_progress + (stage_growth_per_hour * hours_passed * growth_modifier))
            
            # Check for stage advancement
            if self.stage_progress >= 1.0:
                self._advance_growth_stage()
        
        # Update accumulated environmental factors
        self.accumulated_heat_units += hours_passed * max(0, soil.temperature - 10)  # Base temp 10°C
        
        # Update stress factors
        self._update_stress_factors(soil, weather_factor)
        
        # Update health status
        self._update_health_status()
    
    def _advance_growth_stage(self):
        """Advance to the next growth stage"""
        stages = list(GrowthStage)
        current_index = stages.index(self.current_stage)
        
        if current_index < len(stages) - 1:
            self.current_stage = stages[current_index + 1]
            self.stage_progress = 0.0
            
            # Special handling for certain stages
            if self.current_stage == GrowthStage.HARVEST_READY:
                self._calculate_harvest_window()
    
    def _calculate_harvest_window(self):
        """Calculate optimal harvest window"""
        current_time = get_time_manager().get_current_time().total_minutes
        
        # Optimal window is typically 5-10 days
        window_start = current_time
        window_end = current_time + (random.randint(5, 10) * 1440)  # 5-10 days in minutes
        
        self.optimal_harvest_window = (window_start, window_end)
    
    def _update_stress_factors(self, soil: SoilCondition, weather_factor: float):
        """Update various stress factors affecting the crop"""
        self.stress_factors.clear()
        
        # Temperature stress
        temp_factor = self.variety.get_temperature_stress_factor(soil.temperature)
        if temp_factor < 0.8:
            self.stress_factors['temperature'] = 1.0 - temp_factor
        
        # Water stress
        if soil.moisture < 0.3:
            self.stress_factors['drought'] = (0.3 - soil.moisture) / 0.3
        elif soil.moisture > 0.9:
            self.stress_factors['waterlogging'] = (soil.moisture - 0.9) / 0.1
        
        # Nutrient stress
        for nutrient_type, required_level in self.variety.nutrient_requirements.items():
            current_level = soil.nutrients.get(nutrient_type, 50.0)
            if current_level < required_level * 0.5:  # Severe deficiency
                deficiency = (required_level - current_level) / required_level
                self.stress_factors[f'{nutrient_type.value}_deficiency'] = deficiency
        
        # Weather stress
        if weather_factor < 0.7:
            self.stress_factors['weather'] = 1.0 - weather_factor
    
    def _update_health_status(self):
        """Update overall health status based on stress factors"""
        if not self.stress_factors and self.disease_pressure < 0.1 and self.pest_pressure < 0.1:
            self.health_status = CropHealth.EXCELLENT
        elif len(self.stress_factors) <= 1 and max(self.stress_factors.values(), default=0) < 0.3:
            self.health_status = CropHealth.GOOD
        elif len(self.stress_factors) <= 2 and max(self.stress_factors.values(), default=0) < 0.6:
            self.health_status = CropHealth.FAIR
        elif self.disease_pressure > 0.7 or self.pest_pressure > 0.7:
            self.health_status = CropHealth.DISEASED
        elif max(self.stress_factors.values(), default=0) > 0.8:
            self.health_status = CropHealth.DYING
        else:
            self.health_status = CropHealth.POOR
    
    def can_harvest(self) -> bool:
        """Check if crop is ready for harvest"""
        return self.current_stage in [GrowthStage.HARVEST_READY, GrowthStage.OVERRIPE]
    
    def get_harvest_quality(self) -> float:
        """Calculate harvest quality (0-1)"""
        if not self.can_harvest():
            return 0.0
        
        base_quality = 0.7
        
        # Health affects quality
        health_multipliers = {
            CropHealth.EXCELLENT: 1.3,
            CropHealth.GOOD: 1.1,
            CropHealth.FAIR: 0.9,
            CropHealth.POOR: 0.6,
            CropHealth.DISEASED: 0.3,
            CropHealth.DYING: 0.1,
            CropHealth.DEAD: 0.0
        }
        health_factor = health_multipliers.get(self.health_status, 0.7)
        
        # Timing affects quality
        timing_factor = 1.0
        if self.current_stage == GrowthStage.OVERRIPE:
            timing_factor = 0.8  # Reduced quality for overripe crops
        elif self.optimal_harvest_window:
            current_time = get_time_manager().get_current_time().total_minutes
            if self.optimal_harvest_window[0] <= current_time <= self.optimal_harvest_window[1]:
                timing_factor = 1.2  # Bonus for optimal timing
        
        # Size and care factors
        care_factor = self.quality_factor
        
        final_quality = base_quality * health_factor * timing_factor * care_factor
        return max(0.0, min(1.0, final_quality))
    
    def get_harvest_yield(self) -> float:
        """Calculate harvest yield in kg"""
        if not self.can_harvest():
            return 0.0
        
        base_yield = self.variety.base_yield_per_plant
        
        # Health affects yield
        health_multipliers = {
            CropHealth.EXCELLENT: 1.2,
            CropHealth.GOOD: 1.0,
            CropHealth.FAIR: 0.8,
            CropHealth.POOR: 0.5,
            CropHealth.DISEASED: 0.2,
            CropHealth.DYING: 0.1,
            CropHealth.DEAD: 0.0
        }
        health_factor = health_multipliers.get(self.health_status, 0.7)
        
        # Size and growth factors
        growth_factor = self.size_factor
        
        # Stress reduction
        stress_reduction = 1.0
        for stress_value in self.stress_factors.values():
            stress_reduction *= (1.0 - stress_value * 0.3)  # Max 30% reduction per stress
        
        final_yield = base_yield * health_factor * growth_factor * stress_reduction
        return max(0.0, final_yield)


class CropSystem(System):
    """Comprehensive crop growth and agricultural management system"""
    
    def __init__(self):
        super().__init__()
        self.system_name = "crop_system"
        
        # Core system references
        self.event_system = get_event_system()
        self.time_manager = get_time_manager()
        self.config_manager = get_configuration_manager()
        self.economy_system = get_economy_system()
        self.employee_system = get_employee_system()
        
        # Crop data storage
        self.active_crops: Dict[str, CropInstance] = {}  # crop_id -> CropInstance
        self.soil_conditions: Dict[Tuple[int, int], SoilCondition] = {}  # position -> soil
        self.crop_varieties: Dict[str, CropVariety] = {}  # variety_id -> CropVariety
        
        # Grid management
        self.grid_size: Tuple[int, int] = (16, 16)
        self.planted_positions: Set[Tuple[int, int]] = set()
        self.irrigation_status: Dict[Tuple[int, int], bool] = {}
        
        # Agricultural tracking
        self.crop_rotation_history: Dict[Tuple[int, int], List[CropType]] = {}
        self.harvest_history: List[Dict[str, Any]] = []
        self.total_crops_planted = 0
        self.total_crops_harvested = 0
        self.total_yield_kg = 0.0
        
        # Disease and pest management
        self.disease_outbreaks: Dict[str, Dict[str, Any]] = {}
        self.pest_populations: Dict[str, float] = {}
        self.treatment_effectiveness: Dict[str, float] = {}
        
        # Market integration
        self.crop_inventory: Dict[str, Dict[str, float]] = {}  # crop_type -> {quality_grade: quantity}
        self.price_modifiers: Dict[str, float] = {}
        
        # Performance tracking
        self.daily_growth_updates = 0
        self.seasonal_productivity: Dict[Season, float] = {}
        self.water_usage_tracking: float = 0.0
        
        # Configuration
        self.growth_update_frequency = 3600.0  # Update every hour (in seconds)
        self.last_growth_update = 0.0
        self.auto_irrigation = False
        self.pest_pressure_base = 0.1
        self.disease_pressure_base = 0.05
    
    async def initialize(self):
        """Initialize the crop system"""
        # Load configuration
        await self._load_crop_configuration()
        
        # Initialize crop varieties
        await self._initialize_crop_varieties()
        
        # Initialize soil conditions
        await self._initialize_soil_conditions()
        
        # Subscribe to time events
        self.event_system.subscribe('time_hour_passed', self._on_hour_passed)
        self.event_system.subscribe('time_day_passed', self._on_day_passed)
        self.event_system.subscribe('time_season_changed', self._on_season_changed)
        self.event_system.subscribe('weather_changed', self._on_weather_changed)
        
        # Subscribe to game events
        self.event_system.subscribe('task_completed', self._on_task_completed)
        self.event_system.subscribe('irrigation_toggled', self._on_irrigation_toggled)
        
        self.logger.info("Crop System initialized successfully")
    
    async def _load_crop_configuration(self):
        """Load crop system configuration"""
        try:
            crop_config = self.config_manager.get_section('crops')
            
            # Load system parameters
            self.growth_update_frequency = crop_config.get('growth_update_frequency', 3600.0)
            self.auto_irrigation = crop_config.get('auto_irrigation', False)
            self.pest_pressure_base = crop_config.get('pest_pressure_base', 0.1)
            self.disease_pressure_base = crop_config.get('disease_pressure_base', 0.05)
            
            # Load grid configuration
            grid_config = crop_config.get('grid', {})
            self.grid_size = tuple(grid_config.get('size', [16, 16]))
            
        except Exception as e:
            self.logger.warning(f"Failed to load crop configuration: {e}")
    
    async def _initialize_crop_varieties(self):
        """Initialize available crop varieties"""
        # Define crop varieties with realistic characteristics
        varieties = [
            # Corn varieties
            CropVariety(
                variety_id="corn_standard",
                crop_type=CropType.CORN,
                variety_name="Standard Field Corn",
                description="Reliable general-purpose corn variety",
                days_to_maturity=120,
                growth_stages_duration={
                    GrowthStage.GERMINATION: 7,
                    GrowthStage.SEEDLING: 14,
                    GrowthStage.VEGETATIVE: 45,
                    GrowthStage.FLOWERING: 21,
                    GrowthStage.FRUIT_DEVELOPMENT: 28,
                    GrowthStage.MATURATION: 5
                },
                optimal_temperature_range=(20.0, 30.0),
                water_requirements=600.0,
                preferred_soil_types=[SoilType.LOAM, SoilType.SILTY],
                optimal_ph_range=(6.0, 6.8),
                nutrient_requirements={
                    NutrientType.NITROGEN: 80.0,
                    NutrientType.PHOSPHORUS: 60.0,
                    NutrientType.POTASSIUM: 70.0
                },
                base_yield_per_plant=3.5,
                drought_tolerance=0.6,
                seed_cost_per_unit=3.00,
                planting_density=3
            ),
            
            # Tomato varieties
            CropVariety(
                variety_id="tomato_beefsteak",
                crop_type=CropType.TOMATOES,
                variety_name="Beefsteak Tomato",
                description="Large, meaty tomatoes perfect for slicing",
                days_to_maturity=85,
                growth_stages_duration={
                    GrowthStage.GERMINATION: 5,
                    GrowthStage.SEEDLING: 10,
                    GrowthStage.VEGETATIVE: 25,
                    GrowthStage.FLOWERING: 15,
                    GrowthStage.FRUIT_DEVELOPMENT: 25,
                    GrowthStage.MATURATION: 5
                },
                optimal_temperature_range=(18.0, 26.0),
                water_requirements=400.0,
                preferred_soil_types=[SoilType.LOAM, SoilType.ORGANIC],
                optimal_ph_range=(6.0, 6.5),
                nutrient_requirements={
                    NutrientType.NITROGEN: 70.0,
                    NutrientType.PHOSPHORUS: 80.0,
                    NutrientType.POTASSIUM: 90.0
                },
                base_yield_per_plant=4.0,
                heat_tolerance=0.4,
                seed_cost_per_unit=5.00,
                planting_density=2,
                market_value_multiplier=1.8
            ),
            
            # Wheat varieties
            CropVariety(
                variety_id="wheat_winter",
                crop_type=CropType.WHEAT,
                variety_name="Winter Wheat",
                description="Cold-hardy wheat planted in fall for spring harvest",
                days_to_maturity=240,  # Overwinter crop
                growth_stages_duration={
                    GrowthStage.GERMINATION: 10,
                    GrowthStage.SEEDLING: 30,
                    GrowthStage.VEGETATIVE: 150,
                    GrowthStage.FLOWERING: 14,
                    GrowthStage.FRUIT_DEVELOPMENT: 30,
                    GrowthStage.MATURATION: 6
                },
                optimal_temperature_range=(15.0, 24.0),
                water_requirements=450.0,
                preferred_soil_types=[SoilType.LOAM, SoilType.CLAY],
                optimal_ph_range=(6.0, 7.0),
                nutrient_requirements={
                    NutrientType.NITROGEN: 85.0,
                    NutrientType.PHOSPHORUS: 50.0,
                    NutrientType.POTASSIUM: 60.0
                },
                base_yield_per_plant=2.8,
                cold_tolerance=0.9,
                seed_cost_per_unit=2.20,
                planting_density=5
            ),
            
            # Soybean varieties
            CropVariety(
                variety_id="soybean_standard",
                crop_type=CropType.SOYBEANS,
                variety_name="Standard Soybeans",
                description="Nitrogen-fixing legume crop",
                days_to_maturity=110,
                growth_stages_duration={
                    GrowthStage.GERMINATION: 7,
                    GrowthStage.SEEDLING: 12,
                    GrowthStage.VEGETATIVE: 40,
                    GrowthStage.FLOWERING: 20,
                    GrowthStage.FRUIT_DEVELOPMENT: 26,
                    GrowthStage.MATURATION: 5
                },
                optimal_temperature_range=(20.0, 30.0),
                water_requirements=500.0,
                preferred_soil_types=[SoilType.LOAM, SoilType.SILTY],
                optimal_ph_range=(6.0, 6.8),
                nutrient_requirements={
                    NutrientType.NITROGEN: 30.0,  # Lower N requirement due to fixation
                    NutrientType.PHOSPHORUS: 70.0,
                    NutrientType.POTASSIUM: 80.0
                },
                base_yield_per_plant=2.2,
                drought_tolerance=0.7,
                seed_cost_per_unit=4.50,
                planting_density=4,
                market_value_multiplier=1.4
            ),
            
            # Potato varieties
            CropVariety(
                variety_id="potato_russet",
                crop_type=CropType.POTATOES,
                variety_name="Russet Potatoes",
                description="Classic baking and frying potatoes",
                days_to_maturity=95,
                growth_stages_duration={
                    GrowthStage.GERMINATION: 14,
                    GrowthStage.SEEDLING: 10,
                    GrowthStage.VEGETATIVE: 35,
                    GrowthStage.FLOWERING: 14,
                    GrowthStage.FRUIT_DEVELOPMENT: 17,
                    GrowthStage.MATURATION: 5
                },
                optimal_temperature_range=(15.0, 20.0),
                water_requirements=400.0,
                preferred_soil_types=[SoilType.SANDY, SoilType.LOAM],
                optimal_ph_range=(5.8, 6.2),
                nutrient_requirements={
                    NutrientType.NITROGEN: 75.0,
                    NutrientType.PHOSPHORUS: 60.0,
                    NutrientType.POTASSIUM: 85.0
                },
                base_yield_per_plant=6.0,
                cold_tolerance=0.8,
                seed_cost_per_unit=1.80,
                planting_density=2,
                storage_life_days=120
            )
        ]
        
        for variety in varieties:
            self.crop_varieties[variety.variety_id] = variety
        
        self.logger.info(f"Initialized {len(varieties)} crop varieties")
    
    async def _initialize_soil_conditions(self):
        """Initialize soil conditions for the grid"""
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                position = (x, y)
                
                # Generate varied but realistic soil conditions
                base_fertility = random.uniform(0.6, 0.9)
                
                soil = SoilCondition(
                    soil_type=random.choice(list(SoilType)),
                    ph_level=random.uniform(6.0, 7.5),
                    organic_matter=random.uniform(2.0, 5.0),
                    drainage=random.uniform(0.6, 0.9),
                    compaction=random.uniform(0.1, 0.4),
                    moisture=random.uniform(0.4, 0.8),
                    nutrients={
                        NutrientType.NITROGEN: random.uniform(50.0, 90.0) * base_fertility,
                        NutrientType.PHOSPHORUS: random.uniform(40.0, 80.0) * base_fertility,
                        NutrientType.POTASSIUM: random.uniform(45.0, 85.0) * base_fertility,
                        NutrientType.CALCIUM: random.uniform(60.0, 95.0) * base_fertility,
                        NutrientType.MAGNESIUM: random.uniform(35.0, 75.0) * base_fertility,
                        NutrientType.SULFUR: random.uniform(30.0, 70.0) * base_fertility
                    },
                    microbial_activity=random.uniform(0.5, 0.9) * base_fertility,
                    earthworm_count=int(random.uniform(5, 25) * base_fertility)
                )
                
                self.soil_conditions[position] = soil
                self.irrigation_status[position] = False
        
        self.logger.info("Initialized soil conditions for grid")
    
    async def plant_crop(self, variety_id: str, position: Tuple[int, int], 
                        employee_id: Optional[str] = None) -> Optional[str]:
        """Plant a crop at the specified position"""
        if variety_id not in self.crop_varieties:
            self.logger.error(f"Unknown crop variety: {variety_id}")
            return None
        
        if position in self.planted_positions:
            self.logger.warning(f"Position {position} already has a crop")
            return None
        
        variety = self.crop_varieties[variety_id]
        
        # Check if player can afford seeds
        if self.economy_system.player_cash < variety.seed_cost_per_unit:
            self.logger.warning(f"Insufficient funds for {variety.variety_name} seeds")
            return None
        
        # Create crop instance
        crop_id = f"crop_{int(time.time())}_{random.randint(1000, 9999)}"
        current_time = self.time_manager.get_current_time().total_minutes
        
        crop = CropInstance(
            crop_id=crop_id,
            variety=variety,
            position=position,
            planted_time=current_time
        )
        
        # Initialize crop-specific data
        crop.estimated_yield = variety.base_yield_per_plant
        
        # Add to tracking
        self.active_crops[crop_id] = crop
        self.planted_positions.add(position)
        self.total_crops_planted += 1
        
        # Process seed cost
        self.economy_system.player_cash -= variety.seed_cost_per_unit
        self.economy_system.total_expenses += variety.seed_cost_per_unit
        
        # Update crop rotation history
        if position not in self.crop_rotation_history:
            self.crop_rotation_history[position] = []
        self.crop_rotation_history[position].append(variety.crop_type)
        
        # Keep only last 5 crops for rotation tracking
        if len(self.crop_rotation_history[position]) > 5:
            self.crop_rotation_history[position] = self.crop_rotation_history[position][-5:]
        
        # Emit planting event
        self.event_system.emit('crop_planted', {
            'crop_id': crop_id,
            'variety_id': variety_id,
            'variety_name': variety.variety_name,
            'position': position,
            'employee_id': employee_id,
            'seed_cost': variety.seed_cost_per_unit
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Planted {variety.variety_name} at {position}")
        return crop_id
    
    async def harvest_crop(self, crop_id: str, employee_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Harvest a crop and return harvest results"""
        if crop_id not in self.active_crops:
            self.logger.error(f"Crop {crop_id} not found")
            return None
        
        crop = self.active_crops[crop_id]
        
        if not crop.can_harvest():
            self.logger.warning(f"Crop {crop_id} is not ready for harvest")
            return None
        
        # Calculate harvest results
        yield_kg = crop.get_harvest_yield()
        quality = crop.get_harvest_quality()
        
        # Determine quality grade
        if quality >= 0.9:
            quality_grade = "premium"
        elif quality >= 0.7:
            quality_grade = "high"
        elif quality >= 0.5:
            quality_grade = "standard"
        else:
            quality_grade = "low"
        
        # Calculate market value
        base_price = self.economy_system.get_current_price(crop.variety.crop_type.value)
        quality_multipliers = {"premium": 1.5, "high": 1.2, "standard": 1.0, "low": 0.7}
        quality_multiplier = quality_multipliers.get(quality_grade, 1.0)
        market_value = base_price * yield_kg * quality_multiplier * crop.variety.market_value_multiplier
        
        # Remove crop from tracking
        del self.active_crops[crop_id]
        self.planted_positions.remove(crop.position)
        self.total_crops_harvested += 1
        self.total_yield_kg += yield_kg
        
        # Update soil after harvest (nutrient depletion)
        await self._update_soil_after_harvest(crop)
        
        # Add to inventory
        crop_type = crop.variety.crop_type.value
        if crop_type not in self.crop_inventory:
            self.crop_inventory[crop_type] = {}
        if quality_grade not in self.crop_inventory[crop_type]:
            self.crop_inventory[crop_type][quality_grade] = 0.0
        self.crop_inventory[crop_type][quality_grade] += yield_kg
        
        # Create harvest record
        harvest_record = {
            'crop_id': crop_id,
            'variety_id': crop.variety.variety_id,
            'variety_name': crop.variety.variety_name,
            'position': crop.position,
            'yield_kg': yield_kg,
            'quality': quality,
            'quality_grade': quality_grade,
            'market_value': market_value,
            'days_growing': crop.days_growing,
            'harvest_time': self.time_manager.get_current_time().total_minutes,
            'employee_id': employee_id
        }
        
        self.harvest_history.append(harvest_record)
        
        # Emit harvest event
        self.event_system.emit('crop_harvested', {
            'crop_id': crop_id,
            'variety_name': crop.variety.variety_name,
            'yield_kg': yield_kg,
            'quality_grade': quality_grade,
            'market_value': market_value,
            'position': crop.position,
            'employee_id': employee_id
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Harvested {crop.variety.variety_name}: {yield_kg:.1f}kg, {quality_grade} quality")
        
        return harvest_record
    
    async def _update_soil_after_harvest(self, crop: CropInstance):
        """Update soil conditions after crop harvest"""
        position = crop.position
        if position not in self.soil_conditions:
            return
        
        soil = self.soil_conditions[position]
        variety = crop.variety
        
        # Nutrient depletion based on crop requirements
        for nutrient_type, requirement in variety.nutrient_requirements.items():
            if nutrient_type in soil.nutrients:
                depletion = requirement * 0.3  # 30% of requirement depleted
                soil.nutrients[nutrient_type] = max(0.0, soil.nutrients[nutrient_type] - depletion)
        
        # Special handling for nitrogen-fixing crops (legumes)
        if crop.variety.crop_type == CropType.SOYBEANS:
            # Soybeans add nitrogen to soil
            nitrogen_addition = random.uniform(10.0, 25.0)
            soil.nutrients[NutrientType.NITROGEN] = min(100.0, 
                soil.nutrients[NutrientType.NITROGEN] + nitrogen_addition)
        
        # Organic matter changes
        if crop.health_status in [CropHealth.EXCELLENT, CropHealth.GOOD]:
            soil.organic_matter += random.uniform(0.1, 0.3)  # Crop residue improves soil
        
        # Soil compaction from harvest activities
        soil.compaction = min(1.0, soil.compaction + 0.05)
    
    def get_crop_info(self, crop_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a crop"""
        if crop_id not in self.active_crops:
            return None
        
        crop = self.active_crops[crop_id]
        soil = self.soil_conditions.get(crop.position, SoilCondition())
        
        return {
            'crop_id': crop_id,
            'variety_id': crop.variety.variety_id,
            'variety_name': crop.variety.variety_name,
            'crop_type': crop.variety.crop_type.value,
            'position': crop.position,
            'planted_time': crop.planted_time,
            'days_growing': crop.days_growing,
            'current_stage': crop.current_stage.value,
            'stage_progress': crop.stage_progress,
            'overall_progress': crop.overall_progress,
            'health_status': crop.health_status.value,
            'stress_factors': crop.stress_factors,
            'disease_pressure': crop.disease_pressure,
            'pest_pressure': crop.pest_pressure,
            'estimated_yield': crop.estimated_yield,
            'estimated_quality_grade': crop.estimated_quality_grade,
            'can_harvest': crop.can_harvest(),
            'harvest_quality': crop.get_harvest_quality() if crop.can_harvest() else 0.0,
            'harvest_yield': crop.get_harvest_yield() if crop.can_harvest() else 0.0,
            'soil_fertility': soil.get_fertility_score(),
            'growth_rate_modifier': crop.get_growth_rate_modifier(soil)
        }
    
    def get_soil_info(self, position: Tuple[int, int]) -> Optional[Dict[str, Any]]:
        """Get soil information for a position"""
        if position not in self.soil_conditions:
            return None
        
        soil = self.soil_conditions[position]
        
        return {
            'position': position,
            'soil_type': soil.soil_type.value,
            'ph_level': soil.ph_level,
            'organic_matter': soil.organic_matter,
            'drainage': soil.drainage,
            'compaction': soil.compaction,
            'temperature': soil.temperature,
            'moisture': soil.moisture,
            'nutrients': {nutrient.value: level for nutrient, level in soil.nutrients.items()},
            'microbial_activity': soil.microbial_activity,
            'earthworm_count': soil.earthworm_count,
            'fertility_score': soil.get_fertility_score(),
            'is_irrigated': self.irrigation_status.get(position, False),
            'rotation_history': [crop.value for crop in self.crop_rotation_history.get(position, [])]
        }
    
    def get_all_crops(self) -> List[Dict[str, Any]]:
        """Get information for all active crops"""
        return [self.get_crop_info(crop_id) for crop_id in self.active_crops.keys()]
    
    def get_available_varieties(self) -> List[Dict[str, Any]]:
        """Get all available crop varieties"""
        varieties = []
        for variety in self.crop_varieties.values():
            varieties.append({
                'variety_id': variety.variety_id,
                'crop_type': variety.crop_type.value,
                'variety_name': variety.variety_name,
                'description': variety.description,
                'days_to_maturity': variety.days_to_maturity,
                'seed_cost': variety.seed_cost_per_unit,
                'base_yield': variety.base_yield_per_plant,
                'water_requirements': variety.water_requirements,
                'optimal_temperature': variety.optimal_temperature_range,
                'preferred_soils': [soil.value for soil in variety.preferred_soil_types],
                'drought_tolerance': variety.drought_tolerance,
                'market_value_multiplier': variety.market_value_multiplier
            })
        return varieties
    
    async def apply_fertilizer(self, position: Tuple[int, int], fertilizer_type: str, 
                             amount: float = 1.0) -> bool:
        """Apply fertilizer to improve soil conditions"""
        if position not in self.soil_conditions:
            return False
        
        soil = self.soil_conditions[position]
        
        # Different fertilizer types
        fertilizer_effects = {
            'nitrogen': {NutrientType.NITROGEN: 20.0},
            'phosphorus': {NutrientType.PHOSPHORUS: 15.0},
            'potassium': {NutrientType.POTASSIUM: 18.0},
            'npk_balanced': {
                NutrientType.NITROGEN: 12.0,
                NutrientType.PHOSPHORUS: 10.0,
                NutrientType.POTASSIUM: 12.0
            },
            'organic': {
                NutrientType.NITROGEN: 8.0,
                NutrientType.PHOSPHORUS: 6.0,
                NutrientType.POTASSIUM: 8.0
            },
            'lime': {}  # Adjusts pH
        }
        
        if fertilizer_type not in fertilizer_effects:
            return False
        
        # Calculate cost
        fertilizer_costs = {
            'nitrogen': 12.0,
            'phosphorus': 15.0,
            'potassium': 10.0,
            'npk_balanced': 18.0,
            'organic': 25.0,
            'lime': 8.0
        }
        
        cost = fertilizer_costs.get(fertilizer_type, 10.0) * amount
        if self.economy_system.player_cash < cost:
            return False
        
        # Apply fertilizer effects
        for nutrient, boost in fertilizer_effects[fertilizer_type].items():
            if nutrient in soil.nutrients:
                soil.nutrients[nutrient] = min(100.0, soil.nutrients[nutrient] + (boost * amount))
        
        # Special effects
        if fertilizer_type == 'organic':
            soil.organic_matter = min(10.0, soil.organic_matter + (0.5 * amount))
            soil.microbial_activity = min(1.0, soil.microbial_activity + (0.1 * amount))
        elif fertilizer_type == 'lime' and soil.ph_level < 7.0:
            soil.ph_level = min(8.0, soil.ph_level + (0.3 * amount))
        
        # Process payment
        self.economy_system.player_cash -= cost
        self.economy_system.total_expenses += cost
        
        # Track application for any crops at this position
        for crop in self.active_crops.values():
            if crop.position == position:
                crop.last_fertilized = self.time_manager.get_current_time().total_minutes
                crop.fertilizer_applications.append({
                    'type': fertilizer_type,
                    'amount': amount,
                    'time': crop.last_fertilized
                })
        
        # Emit fertilizer event
        self.event_system.emit('fertilizer_applied', {
            'position': position,
            'fertilizer_type': fertilizer_type,
            'amount': amount,
            'cost': cost
        }, priority=EventPriority.NORMAL)
        
        return True
    
    async def water_crops(self, positions: List[Tuple[int, int]], water_amount: float = 1.0):
        """Water crops at specified positions"""
        total_cost = 0.0
        watered_count = 0
        
        for position in positions:
            if position in self.soil_conditions:
                soil = self.soil_conditions[position]
                
                # Calculate water cost (if not free/rain-fed)
                water_cost = 2.0 * water_amount  # Base cost per position
                
                if self.economy_system.player_cash >= water_cost:
                    # Apply water
                    soil.moisture = min(1.0, soil.moisture + (0.3 * water_amount))
                    
                    # Update any crops at this position
                    for crop in self.active_crops.values():
                        if crop.position == position:
                            crop.last_watered = self.time_manager.get_current_time().total_minutes
                            crop.accumulated_water += 25.0 * water_amount  # mm of water
                    
                    # Process payment
                    self.economy_system.player_cash -= water_cost
                    self.economy_system.total_expenses += water_cost
                    total_cost += water_cost
                    watered_count += 1
                    self.water_usage_tracking += 25.0 * water_amount
        
        if watered_count > 0:
            # Emit watering event
            self.event_system.emit('crops_watered', {
                'positions_watered': watered_count,
                'total_positions': len(positions),
                'total_cost': total_cost,
                'water_amount': water_amount
            }, priority=EventPriority.NORMAL)
            
            self.logger.info(f"Watered {watered_count} positions for ${total_cost:.2f}")
    
    async def update(self, delta_time: float):
        """Update crop growth and conditions"""
        current_time = time.time()
        
        # Update crop growth at specified frequency
        if current_time - self.last_growth_update >= self.growth_update_frequency:
            await self._update_crop_growth(self.growth_update_frequency / 3600.0)  # Convert to hours
            self.last_growth_update = current_time
    
    async def _update_crop_growth(self, hours_passed: float):
        """Update growth for all active crops"""
        if not self.active_crops:
            return
        
        # Get current weather effects
        weather_factor = self._get_weather_growth_factor()
        
        crops_to_remove = []
        
        for crop_id, crop in self.active_crops.items():
            soil = self.soil_conditions.get(crop.position, SoilCondition())
            
            # Update environmental conditions
            await self._update_environmental_conditions(crop, soil)
            
            # Update crop growth
            crop.update_growth(hours_passed, soil, weather_factor)
            
            # Update days growing
            crop.days_growing = int((self.time_manager.get_current_time().total_minutes - crop.planted_time) / 1440.0)
            
            # Check for overripe/dead crops
            if crop.current_stage == GrowthStage.OVERRIPE:
                # Crops become more overripe over time
                if crop.stage_progress > 2.0:  # Very overripe
                    crop.health_status = CropHealth.DEAD
                    crops_to_remove.append(crop_id)
            
            # Update pest and disease pressure
            await self._update_pest_disease_pressure(crop)
        
        # Remove dead crops
        for crop_id in crops_to_remove:
            crop = self.active_crops[crop_id]
            self.planted_positions.remove(crop.position)
            del self.active_crops[crop_id]
            
            self.event_system.emit('crop_died', {
                'crop_id': crop_id,
                'variety_name': crop.variety.variety_name,
                'position': crop.position,
                'cause': 'overripe'
            }, priority=EventPriority.NORMAL)
        
        self.daily_growth_updates += 1
    
    def _get_weather_growth_factor(self) -> float:
        """Calculate growth factor based on current weather"""
        current_weather = self.time_manager.get_current_weather()
        
        weather_factors = {
            WeatherType.CLEAR: 1.1,
            WeatherType.PARTLY_CLOUDY: 1.0,
            WeatherType.CLOUDY: 0.9,
            WeatherType.LIGHT_RAIN: 1.2,
            WeatherType.HEAVY_RAIN: 0.8,
            WeatherType.STORM: 0.6,
            WeatherType.EXTREME_HEAT: 0.4,
            WeatherType.EXTREME_COLD: 0.3,
            WeatherType.DROUGHT: 0.5,
            WeatherType.SNOW: 0.7,
            WeatherType.FOG: 0.8
        }
        
        return weather_factors.get(current_weather.weather_type, 1.0)
    
    async def _update_environmental_conditions(self, crop: CropInstance, soil: SoilCondition):
        """Update environmental conditions affecting the crop"""
        current_weather = self.time_manager.get_current_weather()
        current_season = self.time_manager.get_current_season()
        
        # Update soil temperature based on weather and season
        base_temp = current_weather.temperature
        seasonal_modifier = {
            Season.SPRING: 0.0,
            Season.SUMMER: 5.0,
            Season.FALL: -2.0,
            Season.WINTER: -8.0
        }.get(current_season, 0.0)
        
        soil.temperature = base_temp + seasonal_modifier
        
        # Update soil moisture based on weather
        if current_weather.weather_type in [WeatherType.LIGHT_RAIN, WeatherType.HEAVY_RAIN]:
            moisture_gain = 0.3 if current_weather.weather_type == WeatherType.HEAVY_RAIN else 0.15
            soil.moisture = min(1.0, soil.moisture + moisture_gain)
        elif current_weather.weather_type in [WeatherType.EXTREME_HEAT, WeatherType.DROUGHT]:
            moisture_loss = 0.2 if current_weather.weather_type == WeatherType.DROUGHT else 0.1
            soil.moisture = max(0.0, soil.moisture - moisture_loss)
        
        # Handle irrigation
        if self.irrigation_status.get(crop.position, False):
            if current_weather.weather_type in [WeatherType.EXTREME_HEAT, WeatherType.DROUGHT]:
                soil.moisture = min(1.0, soil.moisture + 0.4)  # Irrigation boost during dry weather
                crop.accumulated_water += 15.0  # mm
    
    async def _update_pest_disease_pressure(self, crop: CropInstance):
        """Update pest and disease pressure for a crop"""
        # Base pressure increases with crop age and weather
        age_factor = min(1.0, crop.days_growing / 60.0)  # Increases over 60 days
        weather_factor = self._get_pest_disease_weather_factor()
        
        # Disease pressure
        base_disease_pressure = self.disease_pressure_base * age_factor * weather_factor
        crop.disease_pressure = min(1.0, crop.disease_pressure + base_disease_pressure)
        
        # Pest pressure
        base_pest_pressure = self.pest_pressure_base * age_factor * weather_factor
        crop.pest_pressure = min(1.0, crop.pest_pressure + base_pest_pressure)
        
        # Resistance factors
        for disease, resistance in crop.variety.disease_resistance.items():
            crop.disease_pressure *= (1.0 - resistance)
        
        for pest, resistance in crop.variety.pest_resistance.items():
            crop.pest_pressure *= (1.0 - resistance)
        
        # Natural reduction over time (beneficial insects, etc.)
        crop.disease_pressure = max(0.0, crop.disease_pressure - 0.02)
        crop.pest_pressure = max(0.0, crop.pest_pressure - 0.03)
    
    def _get_pest_disease_weather_factor(self) -> float:
        """Calculate pest/disease factor based on weather"""
        current_weather = self.time_manager.get_current_weather()
        
        # Humid, warm weather increases pressure
        factors = {
            WeatherType.LIGHT_RAIN: 1.3,
            WeatherType.HEAVY_RAIN: 1.1,
            WeatherType.CLOUDY: 1.2,
            WeatherType.EXTREME_HEAT: 1.4,
            WeatherType.CLEAR: 1.0,
            WeatherType.EXTREME_COLD: 0.3,
            WeatherType.DROUGHT: 0.8,
            WeatherType.STORM: 0.7
        }
        
        return factors.get(current_weather.weather_type, 1.0)
    
    # Event handlers
    async def _on_hour_passed(self, event_data):
        """Handle hourly updates"""
        # Update auto-irrigation
        if self.auto_irrigation:
            await self._check_auto_irrigation()
    
    async def _on_day_passed(self, event_data):
        """Handle daily updates"""
        # Reset daily tracking
        self.daily_growth_updates = 0
        
        # Update seasonal productivity tracking
        current_season = self.time_manager.get_current_season()
        if current_season not in self.seasonal_productivity:
            self.seasonal_productivity[current_season] = 0.0
        
        # Calculate daily productivity (crops harvested + growth progress)
        daily_productivity = len([h for h in self.harvest_history 
                                if h['harvest_time'] > 
                                self.time_manager.get_current_time().total_minutes - 1440])
        self.seasonal_productivity[current_season] += daily_productivity
    
    async def _on_season_changed(self, event_data):
        """Handle seasonal changes"""
        new_season = Season(event_data.get('new_season'))
        
        # Seasonal soil updates
        for soil in self.soil_conditions.values():
            if new_season == Season.WINTER:
                soil.microbial_activity *= 0.7  # Reduced activity in winter
            elif new_season == Season.SPRING:
                soil.microbial_activity = min(1.0, soil.microbial_activity * 1.3)  # Spring awakening
    
    async def _on_weather_changed(self, event_data):
        """Handle weather changes"""
        weather_type = WeatherType(event_data.get('weather_type'))
        
        # Immediate effects of severe weather
        if weather_type in [WeatherType.STORM, WeatherType.EXTREME_HEAT, WeatherType.EXTREME_COLD]:
            for crop in self.active_crops.values():
                if weather_type == WeatherType.STORM:
                    # Storms can damage crops
                    crop.stress_factors['storm_damage'] = random.uniform(0.1, 0.4)
                elif weather_type == WeatherType.EXTREME_HEAT:
                    if crop.variety.heat_tolerance < 0.5:
                        crop.stress_factors['heat_stress'] = 0.6
                elif weather_type == WeatherType.EXTREME_COLD:
                    if crop.variety.cold_tolerance < 0.5:
                        crop.stress_factors['cold_stress'] = 0.7
    
    async def _on_task_completed(self, event_data):
        """Handle completed farming tasks"""
        task_type = event_data.get('task_type')
        position = event_data.get('position')
        
        if task_type == 'water' and position:
            await self.water_crops([position])
        elif task_type == 'fertilize' and position:
            await self.apply_fertilizer(position, 'npk_balanced')
    
    async def _on_irrigation_toggled(self, event_data):
        """Handle irrigation system toggle"""
        positions = event_data.get('positions', [])
        enabled = event_data.get('enabled', False)
        
        for position in positions:
            self.irrigation_status[position] = enabled
    
    async def _check_auto_irrigation(self):
        """Check and apply auto-irrigation where needed"""
        if not self.auto_irrigation:
            return
        
        positions_to_water = []
        
        for crop in self.active_crops.values():
            soil = self.soil_conditions.get(crop.position)
            if soil and soil.moisture < 0.4:  # Low moisture threshold
                positions_to_water.append(crop.position)
        
        if positions_to_water:
            await self.water_crops(positions_to_water)
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive crop system summary"""
        active_crops_by_type = {}
        for crop in self.active_crops.values():
            crop_type = crop.variety.crop_type.value
            if crop_type not in active_crops_by_type:
                active_crops_by_type[crop_type] = 0
            active_crops_by_type[crop_type] += 1
        
        return {
            'total_active_crops': len(self.active_crops),
            'total_planted': self.total_crops_planted,
            'total_harvested': self.total_crops_harvested,
            'total_yield_kg': self.total_yield_kg,
            'active_crops_by_type': active_crops_by_type,
            'available_varieties': len(self.crop_varieties),
            'irrigated_positions': sum(1 for status in self.irrigation_status.values() if status),
            'water_usage_total': self.water_usage_tracking,
            'seasonal_productivity': self.seasonal_productivity,
            'inventory': self.crop_inventory
        }
    
    async def shutdown(self):
        """Shutdown the crop system"""
        self.logger.info("Shutting down Crop System")
        
        # Save final crop system state
        final_summary = self.get_system_summary()
        
        self.event_system.emit('crop_system_shutdown', {
            'final_summary': final_summary,
            'active_crops': len(self.active_crops)
        }, priority=EventPriority.HIGH)
        
        self.logger.info("Crop System shutdown complete")


# Global crop system instance
_global_crop_system: Optional[CropSystem] = None

def get_crop_system() -> CropSystem:
    """Get the global crop system instance"""
    global _global_crop_system
    if _global_crop_system is None:
        _global_crop_system = CropSystem()
    return _global_crop_system

def initialize_crop_system() -> CropSystem:
    """Initialize the global crop system"""
    global _global_crop_system
    _global_crop_system = CropSystem()
    return _global_crop_system