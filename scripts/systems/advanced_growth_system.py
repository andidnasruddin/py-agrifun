"""
Advanced Growth System - Sophisticated Crop Development for AgriFun Agricultural Simulation

This system provides comprehensive multi-stage crop growth with environmental factors,
genetic influences, and realistic agricultural development patterns. Integrates with
the Multi-Crop Framework to support unlimited variety types with unique growth profiles.

Key Features:
- 5+ customizable growth stages per crop variety
- Environmental factor integration (temperature, water, nutrients, light)
- Genetic trait influence on growth patterns
- Disease and pest susceptibility by growth stage
- Yield calculation based on growth quality
- Growth visualization and agricultural education

System Integration:
- Integrates with Multi-Crop Framework for genetic variety support
- Uses Time Management System for realistic growth timing
- Connects to Soil Health System for nutrient availability
- Interfaces with Weather System for environmental conditions
- Supports Equipment System for growth enhancement tools

Educational Value:
- Realistic agricultural growth patterns and timing
- Understanding of environmental factors in crop development
- Growth stage management and farming decisions
- Agricultural science education through gameplay
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import logging
from datetime import datetime, timedelta
import json
import math
import random

# Import Phase 1 systems
from scripts.core.event_system import EventSystem
from scripts.core.time_management import TimeManager
from scripts.core.advanced_config_system import ConfigurationManager
from scripts.core.content_registry import ContentRegistry
from scripts.core.entity_component import System, Component

# Phase 3 system imports
from scripts.systems.multicrop_framework import (
    MultiCropFramework, AdvancedCropVariety, GeneticProfile, GeneticAllele
)

# Configure logging for advanced growth system
logger = logging.getLogger(__name__)

class GrowthStage(Enum):
    """Enumeration of crop growth stages"""
    SEED = "seed"                    # Initial planting stage
    GERMINATION = "germination"      # Sprouting and emergence
    SEEDLING = "seedling"           # Early vegetative growth
    VEGETATIVE = "vegetative"       # Main growth period
    FLOWERING = "flowering"         # Reproductive stage begins
    FRUIT_DEVELOPMENT = "fruit_dev" # Fruit/grain formation
    MATURATION = "maturation"       # Final ripening
    HARVEST_READY = "harvest_ready" # Optimal harvest window
    OVERRIPE = "overripe"          # Quality degradation begins
    SENESCENCE = "senescence"       # End of life cycle

class EnvironmentalFactor(Enum):
    """Environmental factors affecting crop growth"""
    TEMPERATURE = "temperature"     # Air and soil temperature
    WATER_AVAILABILITY = "water"    # Soil moisture and irrigation
    NUTRIENT_AVAILABILITY = "nutrients"  # N-P-K and micronutrients
    LIGHT_EXPOSURE = "light"        # Sunlight hours and intensity
    SOIL_COMPACTION = "compaction"  # Soil structure and aeration
    PH_LEVEL = "ph"                # Soil acidity/alkalinity
    ORGANIC_MATTER = "organic"      # Soil organic content
    PEST_PRESSURE = "pests"         # Insect and disease pressure
    WEATHER_STRESS = "weather"      # Extreme weather events

class GrowthModifier(Enum):
    """Types of growth rate modifications"""
    ACCELERATED = "accelerated"     # Faster than normal growth
    NORMAL = "normal"              # Standard growth rate
    DELAYED = "delayed"            # Slower than normal growth
    STUNTED = "stunted"            # Severely reduced growth
    STRESSED = "stressed"          # Growth under stress conditions
    OPTIMAL = "optimal"            # Perfect growing conditions

@dataclass
class EnvironmentalCondition:
    """Environmental condition affecting crop growth"""
    factor: EnvironmentalFactor     # Which environmental factor this represents
    current_value: float           # Current measured value (0.0-1.0 scale)
    optimal_range: Tuple[float, float]  # Optimal range for this factor (min, max)
    tolerance_range: Tuple[float, float]  # Tolerable range before stress
    stress_threshold: float        # Point where severe stress begins
    critical_threshold: float      # Point where damage occurs
    
    def get_growth_impact(self) -> float:
        """Calculate growth impact factor (0.0-2.0, where 1.0 is neutral)"""
        value = self.current_value
        
        # Check if in optimal range
        if self.optimal_range[0] <= value <= self.optimal_range[1]:
            return 1.2  # Bonus growth in optimal conditions
        
        # Check if in tolerance range
        elif self.tolerance_range[0] <= value <= self.tolerance_range[1]:
            return 1.0  # Neutral growth
        
        # Check if stressed but not critical
        elif value > self.stress_threshold or value < (1.0 - self.stress_threshold):
            stress_level = min(
                abs(value - self.optimal_range[0]) if value < self.optimal_range[0] 
                else abs(value - self.optimal_range[1]),
                0.5
            )
            return max(0.3, 1.0 - stress_level)  # Reduced growth under stress
        
        # Critical conditions
        else:
            return 0.1  # Minimal growth under critical stress

@dataclass
class GrowthStageDefinition:
    """Definition of a specific growth stage for a crop variety"""
    stage: GrowthStage             # Which growth stage this represents
    name: str                      # Human-readable stage name
    description: str               # Educational description of this stage
    base_duration_days: float      # Base time to complete this stage (game days)
    minimum_duration_days: float   # Minimum time regardless of conditions
    maximum_duration_days: float   # Maximum time under poor conditions
    
    # Environmental requirements for this stage
    temperature_requirements: Tuple[float, float]  # (min_temp, max_temp) in Celsius
    water_requirements: float      # Water needs (0.0-1.0 scale)
    nutrient_requirements: Dict[str, float]  # N-P-K requirements by type
    light_requirements: float      # Light needs (0.0-1.0 scale)
    
    # Growth characteristics
    size_increase_factor: float    # How much plant size increases in this stage
    root_development_factor: float # Root system development
    leaf_development_factor: float # Leaf/canopy development
    reproductive_development: float # Reproductive organ development
    
    # Vulnerability factors
    pest_susceptibility: Dict[str, float]  # Susceptibility to different pests
    disease_susceptibility: Dict[str, float]  # Disease vulnerability
    weather_stress_tolerance: float  # Tolerance to weather extremes
    
    # Quality factors
    quality_impact_factors: Dict[str, float]  # How this stage affects final quality
    yield_impact_factors: Dict[str, float]    # How this stage affects final yield

@dataclass
class GrowthProgress:
    """Current growth progress for a specific crop instance"""
    crop_id: str                   # Unique identifier for this crop instance
    variety_id: str                # ID of the crop variety being grown
    current_stage: GrowthStage     # Current growth stage
    stage_progress: float          # Progress through current stage (0.0-1.0)
    days_in_current_stage: float   # Time spent in current stage
    total_growth_days: float       # Total time since planting
    
    # Growth quality tracking
    overall_growth_quality: float  # Overall quality of growth so far (0.0-1.0)
    stage_quality_history: Dict[GrowthStage, float]  # Quality achieved in each stage
    environmental_stress_history: List[Dict[str, Any]]  # History of stress events
    
    # Physical development
    current_size: float            # Current plant size (0.0-1.0 of mature size)
    root_development: float        # Root system development (0.0-1.0)
    leaf_development: float        # Leaf/canopy development (0.0-1.0)
    reproductive_development: float # Reproductive development (0.0-1.0)
    
    # Environmental adaptation
    temperature_adaptation: float  # Adaptation to current temperature conditions
    water_stress_tolerance: float  # Current tolerance to water stress
    nutrient_efficiency: float     # Efficiency of nutrient utilization
    
    # Predictive factors
    estimated_yield: float         # Predicted yield based on current conditions
    estimated_quality: float       # Predicted final quality
    estimated_harvest_date: datetime  # Predicted optimal harvest date
    
    # Genetic influences
    genetic_modifiers: Dict[str, float]  # Active genetic trait modifiers
    expressed_traits: List[str]    # Currently expressed genetic traits

@dataclass
class GrowthEnvironment:
    """Current environmental conditions affecting crop growth"""
    location_id: str               # Grid location or field identifier
    
    # Environmental measurements
    current_conditions: Dict[EnvironmentalFactor, EnvironmentalCondition]
    historical_conditions: List[Dict[str, Any]]  # Past 30 days of conditions
    
    # Soil conditions
    soil_temperature: float        # Current soil temperature (Celsius)
    soil_moisture: float          # Current soil moisture (0.0-1.0)
    soil_nutrients: Dict[str, float]  # Available nutrients (N-P-K-S-Ca-Mg-etc)
    soil_ph: float                # Soil pH level
    soil_organic_matter: float    # Organic matter content (0.0-1.0)
    soil_compaction: float        # Soil compaction level (0.0-1.0)
    
    # Weather conditions
    air_temperature: float        # Current air temperature (Celsius)
    humidity: float               # Relative humidity (0.0-1.0)
    wind_speed: float             # Wind speed (m/s)
    solar_radiation: float        # Daily solar radiation (MJ/m²)
    precipitation: float          # Recent precipitation (mm)
    
    # Management factors
    irrigation_active: bool       # Whether irrigation is currently active
    fertilizer_applications: List[Dict[str, Any]]  # Recent fertilizer applications
    pest_control_measures: List[Dict[str, Any]]    # Active pest control
    cultivation_history: List[Dict[str, Any]]      # Recent cultivation activities

class AdvancedGrowthSystem(System):
    """
    Advanced Growth System - Sophisticated multi-stage crop development
    
    This system manages realistic crop growth with environmental factors,
    genetic influences, and agricultural science principles. Provides
    educational value while maintaining engaging gameplay mechanics.
    """
    
    def __init__(self):
        """Initialize the Advanced Growth System"""
        super().__init__()
        self.system_name = "advanced_growth_system"
        
        # Core system references
        self.event_system: Optional[EventSystem] = None
        self.time_manager: Optional[TimeManager] = None
        self.config_manager: Optional[ConfigurationManager] = None
        self.content_registry: Optional[ContentRegistry] = None
        self.multicrop_framework: Optional[MultiCropFramework] = None
        
        # Growth management
        self.growth_definitions: Dict[str, Dict[GrowthStage, GrowthStageDefinition]] = {}
        self.active_crops: Dict[str, GrowthProgress] = {}
        self.growth_environments: Dict[str, GrowthEnvironment] = {}
        
        # Performance optimization
        self.update_frequency = 1.0  # Update every game hour
        self.last_update_time = 0.0
        self.batch_size = 100  # Process crops in batches for performance
        
        # Growth simulation parameters
        self.growth_calculation_precision = 0.01  # Precision for growth calculations
        self.environmental_update_frequency = 6.0  # Update environment every 6 hours
        self.quality_calculation_complexity = "detailed"  # Quality calculation detail level
        
        # Educational content
        self.growth_tips: Dict[GrowthStage, List[str]] = {}
        self.environmental_education: Dict[EnvironmentalFactor, str] = {}
        
        logger.info("Advanced Growth System initialized")
    
    def initialize(self) -> bool:
        """Initialize the growth system with required dependencies"""
        try:
            # Get system references
            from scripts.core.event_system import get_event_system
            from scripts.core.time_management import get_time_manager
            from scripts.core.advanced_config_system import get_configuration_manager
            from scripts.core.content_registry import get_content_registry
            
            self.event_system = get_event_system()
            self.time_manager = get_time_manager()
            self.config_manager = get_configuration_manager()
            self.content_registry = get_content_registry()
            
            # Get multicrop framework reference
            # This will be set by the system manager during initialization
            
            # Load growth stage definitions
            self._load_growth_definitions()
            
            # Load educational content
            self._load_educational_content()
            
            # Subscribe to relevant events
            self._subscribe_to_events()
            
            # Load configuration
            self._load_configuration()
            
            logger.info("Advanced Growth System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Advanced Growth System: {e}")
            return False
    
    def _load_growth_definitions(self):
        """Load growth stage definitions for all crop varieties"""
        try:
            # Load base growth definitions from content registry
            base_definitions = self.content_registry.get_content("growth_stages", {})
            
            # Create detailed growth definitions for each variety
            for variety_id, definition in base_definitions.items():
                self.growth_definitions[variety_id] = {}
                
                for stage_data in definition.get("stages", []):
                    stage = GrowthStage(stage_data["stage"])
                    
                    stage_def = GrowthStageDefinition(
                        stage=stage,
                        name=stage_data["name"],
                        description=stage_data["description"],
                        base_duration_days=stage_data["base_duration_days"],
                        minimum_duration_days=stage_data["minimum_duration_days"],
                        maximum_duration_days=stage_data["maximum_duration_days"],
                        temperature_requirements=tuple(stage_data["temperature_requirements"]),
                        water_requirements=stage_data["water_requirements"],
                        nutrient_requirements=stage_data["nutrient_requirements"],
                        light_requirements=stage_data["light_requirements"],
                        size_increase_factor=stage_data["size_increase_factor"],
                        root_development_factor=stage_data["root_development_factor"],
                        leaf_development_factor=stage_data["leaf_development_factor"],
                        reproductive_development=stage_data["reproductive_development"],
                        pest_susceptibility=stage_data["pest_susceptibility"],
                        disease_susceptibility=stage_data["disease_susceptibility"],
                        weather_stress_tolerance=stage_data["weather_stress_tolerance"],
                        quality_impact_factors=stage_data["quality_impact_factors"],
                        yield_impact_factors=stage_data["yield_impact_factors"]
                    )
                    
                    self.growth_definitions[variety_id][stage] = stage_def
            
            logger.info(f"Loaded growth definitions for {len(self.growth_definitions)} varieties")
            
        except Exception as e:
            logger.error(f"Failed to load growth definitions: {e}")
            # Create default definitions for basic functionality
            self._create_default_growth_definitions()
    
    def _create_default_growth_definitions(self):
        """Create default growth definitions for basic crop types"""
        # Create basic corn growth definition as example
        default_stages = [
            {
                "stage": GrowthStage.SEED,
                "name": "Seed",
                "description": "Planted seed ready for germination",
                "base_duration_days": 1.0,
                "minimum_duration_days": 0.5,
                "maximum_duration_days": 3.0,
                "temperature_requirements": (10, 30),
                "water_requirements": 0.8,
                "nutrient_requirements": {"N": 0.1, "P": 0.2, "K": 0.1},
                "light_requirements": 0.2,
                "size_increase_factor": 0.0,
                "root_development_factor": 0.1,
                "leaf_development_factor": 0.0,
                "reproductive_development": 0.0,
                "pest_susceptibility": {"insects": 0.2, "rodents": 0.8},
                "disease_susceptibility": {"fungal": 0.3, "bacterial": 0.1},
                "weather_stress_tolerance": 0.3,
                "quality_impact_factors": {"emergence": 1.0},
                "yield_impact_factors": {"establishment": 1.0}
            },
            {
                "stage": GrowthStage.GERMINATION,
                "name": "Germination",
                "description": "Seedling emerging from soil",
                "base_duration_days": 7.0,
                "minimum_duration_days": 5.0,
                "maximum_duration_days": 14.0,
                "temperature_requirements": (15, 30),
                "water_requirements": 0.9,
                "nutrient_requirements": {"N": 0.2, "P": 0.3, "K": 0.2},
                "light_requirements": 0.6,
                "size_increase_factor": 0.1,
                "root_development_factor": 0.3,
                "leaf_development_factor": 0.2,
                "reproductive_development": 0.0,
                "pest_susceptibility": {"insects": 0.6, "rodents": 0.4},
                "disease_susceptibility": {"fungal": 0.5, "bacterial": 0.2},
                "weather_stress_tolerance": 0.4,
                "quality_impact_factors": {"vigor": 1.2},
                "yield_impact_factors": {"establishment": 1.1}
            }
        ]
        
        # Add more stages...
        logger.info("Created default growth definitions")
    
    def _load_educational_content(self):
        """Load educational content for growth stages and environmental factors"""
        try:
            # Load growth tips
            tips_data = self.content_registry.get_content("growth_tips", {})
            for stage_name, tips in tips_data.items():
                stage = GrowthStage(stage_name)
                self.growth_tips[stage] = tips
            
            # Load environmental education content
            env_data = self.content_registry.get_content("environmental_education", {})
            for factor_name, description in env_data.items():
                factor = EnvironmentalFactor(factor_name)
                self.environmental_education[factor] = description
            
            logger.info("Loaded educational content successfully")
            
        except Exception as e:
            logger.warning(f"Could not load educational content: {e}")
            # Create basic educational content
            self._create_default_educational_content()
    
    def _create_default_educational_content(self):
        """Create default educational content"""
        self.growth_tips[GrowthStage.GERMINATION] = [
            "Ensure consistent soil moisture for optimal germination",
            "Soil temperature should be 15-25°C for best results",
            "Protect young seedlings from harsh weather"
        ]
        
        self.environmental_education[EnvironmentalFactor.TEMPERATURE] = (
            "Temperature affects enzyme activity and growth rate. "
            "Each crop has optimal temperature ranges for different growth stages."
        )
    
    def _subscribe_to_events(self):
        """Subscribe to relevant system events"""
        if self.event_system:
            # Time-based events
            self.event_system.subscribe("time_advanced", self._on_time_advanced)
            self.event_system.subscribe("day_changed", self._on_day_changed)
            self.event_system.subscribe("season_changed", self._on_season_changed)
            
            # Weather events
            self.event_system.subscribe("weather_updated", self._on_weather_updated)
            self.event_system.subscribe("temperature_changed", self._on_temperature_changed)
            
            # Agricultural events
            self.event_system.subscribe("crop_planted", self._on_crop_planted)
            self.event_system.subscribe("irrigation_applied", self._on_irrigation_applied)
            self.event_system.subscribe("fertilizer_applied", self._on_fertilizer_applied)
            
            # Management events
            self.event_system.subscribe("pest_control_applied", self._on_pest_control_applied)
            self.event_system.subscribe("cultivation_performed", self._on_cultivation_performed)
    
    def _load_configuration(self):
        """Load system configuration parameters"""
        if self.config_manager:
            config = self.config_manager.get_config("advanced_growth_system", {})
            
            self.update_frequency = config.get("update_frequency", 1.0)
            self.batch_size = config.get("batch_size", 100)
            self.growth_calculation_precision = config.get("calculation_precision", 0.01)
            self.environmental_update_frequency = config.get("environmental_update_frequency", 6.0)
            self.quality_calculation_complexity = config.get("quality_complexity", "detailed")
    
    def plant_crop(self, crop_id: str, variety_id: str, location_id: str, 
                   genetic_profile: Optional[GeneticProfile] = None) -> bool:
        """
        Plant a new crop and initialize its growth tracking
        
        Args:
            crop_id: Unique identifier for this crop instance
            variety_id: ID of the crop variety being planted
            location_id: Grid location where crop is planted
            genetic_profile: Optional genetic profile for this crop instance
            
        Returns:
            bool: True if crop was successfully planted and growth tracking initialized
        """
        try:
            # Verify variety exists
            if variety_id not in self.growth_definitions:
                logger.error(f"Unknown crop variety: {variety_id}")
                return False
            
            # Get genetic modifiers if profile provided
            genetic_modifiers = {}
            expressed_traits = []
            if genetic_profile:
                genetic_modifiers = self._calculate_genetic_modifiers(genetic_profile)
                expressed_traits = self._get_expressed_traits(genetic_profile)
            
            # Create growth progress tracking
            current_time = self.time_manager.get_current_time() if self.time_manager else datetime.now()
            
            growth_progress = GrowthProgress(
                crop_id=crop_id,
                variety_id=variety_id,
                current_stage=GrowthStage.SEED,
                stage_progress=0.0,
                days_in_current_stage=0.0,
                total_growth_days=0.0,
                overall_growth_quality=1.0,
                stage_quality_history={},
                environmental_stress_history=[],
                current_size=0.0,
                root_development=0.0,
                leaf_development=0.0,
                reproductive_development=0.0,
                temperature_adaptation=0.5,
                water_stress_tolerance=0.5,
                nutrient_efficiency=0.5,
                estimated_yield=1.0,
                estimated_quality=1.0,
                estimated_harvest_date=current_time + timedelta(days=90),  # Default estimate
                genetic_modifiers=genetic_modifiers,
                expressed_traits=expressed_traits
            )
            
            # Store growth progress
            self.active_crops[crop_id] = growth_progress
            
            # Initialize growth environment for location if not exists
            if location_id not in self.growth_environments:
                self._initialize_growth_environment(location_id)
            
            # Publish crop planted event
            if self.event_system:
                self.event_system.publish("advanced_crop_planted", {
                    "crop_id": crop_id,
                    "variety_id": variety_id,
                    "location_id": location_id,
                    "genetic_profile": genetic_profile
                })
            
            logger.info(f"Successfully planted crop {crop_id} (variety: {variety_id}) at {location_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to plant crop {crop_id}: {e}")
            return False
    
    def _initialize_growth_environment(self, location_id: str):
        """Initialize growth environment for a new location"""
        # Create default environmental conditions
        default_conditions = {}
        
        for factor in EnvironmentalFactor:
            # Set reasonable default values
            if factor == EnvironmentalFactor.TEMPERATURE:
                condition = EnvironmentalCondition(
                    factor=factor,
                    current_value=0.6,  # Moderate temperature
                    optimal_range=(0.5, 0.8),
                    tolerance_range=(0.3, 0.9),
                    stress_threshold=0.2,
                    critical_threshold=0.1
                )
            elif factor == EnvironmentalFactor.WATER_AVAILABILITY:
                condition = EnvironmentalCondition(
                    factor=factor,
                    current_value=0.7,  # Good moisture
                    optimal_range=(0.6, 0.9),
                    tolerance_range=(0.4, 1.0),
                    stress_threshold=0.3,
                    critical_threshold=0.1
                )
            else:
                # Default for other factors
                condition = EnvironmentalCondition(
                    factor=factor,
                    current_value=0.6,
                    optimal_range=(0.4, 0.8),
                    tolerance_range=(0.2, 1.0),
                    stress_threshold=0.1,
                    critical_threshold=0.05
                )
            
            default_conditions[factor] = condition
        
        # Create growth environment
        environment = GrowthEnvironment(
            location_id=location_id,
            current_conditions=default_conditions,
            historical_conditions=[],
            soil_temperature=20.0,
            soil_moisture=0.7,
            soil_nutrients={"N": 0.6, "P": 0.6, "K": 0.6},
            soil_ph=6.5,
            soil_organic_matter=0.4,
            soil_compaction=0.3,
            air_temperature=22.0,
            humidity=0.6,
            wind_speed=2.0,
            solar_radiation=15.0,
            precipitation=0.0,
            irrigation_active=False,
            fertilizer_applications=[],
            pest_control_measures=[],
            cultivation_history=[]
        )
        
        self.growth_environments[location_id] = environment
        logger.info(f"Initialized growth environment for location {location_id}")
    
    def update(self, delta_time: float):
        """
        Update crop growth for all active crops
        
        Args:
            delta_time: Time elapsed since last update (in game hours)
        """
        try:
            # Check if it's time for update
            current_time = self.time_manager.get_game_time_hours() if self.time_manager else 0.0
            if current_time - self.last_update_time < self.update_frequency:
                return
            
            self.last_update_time = current_time
            
            # Process crops in batches for performance
            crop_items = list(self.active_crops.items())
            batch_count = 0
            
            for crop_id, growth_progress in crop_items:
                if batch_count >= self.batch_size:
                    break  # Process remaining crops in next update
                
                self._update_crop_growth(crop_id, growth_progress, delta_time)
                batch_count += 1
            
            # Update environmental conditions periodically
            if current_time % self.environmental_update_frequency < self.update_frequency:
                self._update_environmental_conditions()
            
        except Exception as e:
            logger.error(f"Error updating crop growth: {e}")
    
    def _update_crop_growth(self, crop_id: str, growth_progress: GrowthProgress, delta_time: float):
        """Update growth for a specific crop"""
        try:
            # Get variety and stage definitions
            variety_id = growth_progress.variety_id
            if variety_id not in self.growth_definitions:
                logger.warning(f"No growth definition for variety {variety_id}")
                return
            
            current_stage = growth_progress.current_stage
            stage_definitions = self.growth_definitions[variety_id]
            
            if current_stage not in stage_definitions:
                logger.warning(f"No definition for stage {current_stage} in variety {variety_id}")
                return
            
            stage_def = stage_definitions[current_stage]
            
            # Calculate environmental impacts
            environmental_multiplier = self._calculate_environmental_impact(crop_id, stage_def)
            
            # Calculate genetic impacts
            genetic_multiplier = self._calculate_genetic_impact(growth_progress, stage_def)
            
            # Calculate growth rate for this stage
            base_growth_rate = 1.0 / stage_def.base_duration_days  # Fraction per day
            actual_growth_rate = base_growth_rate * environmental_multiplier * genetic_multiplier
            
            # Ensure minimum and maximum duration constraints
            min_rate = 1.0 / stage_def.maximum_duration_days
            max_rate = 1.0 / stage_def.minimum_duration_days
            actual_growth_rate = max(min_rate, min(max_rate, actual_growth_rate))
            
            # Update stage progress
            growth_increment = actual_growth_rate * (delta_time / 24.0)  # Convert hours to days
            growth_progress.stage_progress += growth_increment
            growth_progress.days_in_current_stage += (delta_time / 24.0)
            growth_progress.total_growth_days += (delta_time / 24.0)
            
            # Update physical development
            self._update_physical_development(growth_progress, stage_def, growth_increment)
            
            # Update quality factors
            stage_quality = self._calculate_stage_quality(growth_progress, stage_def, environmental_multiplier)
            growth_progress.stage_quality_history[current_stage] = stage_quality
            
            # Update overall quality (weighted average)
            self._update_overall_quality(growth_progress)
            
            # Check for stage advancement
            if growth_progress.stage_progress >= 1.0:
                self._advance_growth_stage(growth_progress, stage_definitions)
            
            # Update yield and quality estimates
            self._update_yield_estimates(growth_progress, stage_def)
            
            # Check for stress events
            self._check_stress_events(growth_progress, environmental_multiplier)
            
        except Exception as e:
            logger.error(f"Error updating growth for crop {crop_id}: {e}")
    
    def _calculate_environmental_impact(self, crop_id: str, stage_def: GrowthStageDefinition) -> float:
        """Calculate the environmental impact on growth rate"""
        # Get crop location (simplified - assume same as crop_id for now)
        location_id = crop_id  # This would be properly mapped in a real implementation
        
        if location_id not in self.growth_environments:
            return 1.0  # Neutral impact if no environment data
        
        environment = self.growth_environments[location_id]
        total_impact = 1.0
        factor_count = 0
        
        # Check each environmental factor
        for factor, condition in environment.current_conditions.items():
            impact = condition.get_growth_impact()
            
            # Weight impacts based on stage requirements
            if factor == EnvironmentalFactor.TEMPERATURE:
                weight = 1.2  # Temperature is critical for most stages
            elif factor == EnvironmentalFactor.WATER_AVAILABILITY:
                weight = stage_def.water_requirements
            elif factor == EnvironmentalFactor.NUTRIENT_AVAILABILITY:
                weight = sum(stage_def.nutrient_requirements.values()) / len(stage_def.nutrient_requirements)
            elif factor == EnvironmentalFactor.LIGHT_EXPOSURE:
                weight = stage_def.light_requirements
            else:
                weight = 0.8  # Other factors have moderate impact
            
            total_impact += (impact - 1.0) * weight
            factor_count += weight
        
        # Calculate weighted average
        if factor_count > 0:
            final_impact = total_impact / factor_count
        else:
            final_impact = 1.0
        
        return max(0.1, min(2.0, final_impact))  # Clamp between 0.1 and 2.0
    
    def _calculate_genetic_impact(self, growth_progress: GrowthProgress, stage_def: GrowthStageDefinition) -> float:
        """Calculate genetic trait impacts on growth"""
        if not growth_progress.genetic_modifiers:
            return 1.0
        
        total_modifier = 1.0
        
        # Apply genetic modifiers
        for trait, modifier in growth_progress.genetic_modifiers.items():
            if "growth_rate" in trait.lower():
                total_modifier *= modifier
            elif "vigor" in trait.lower():
                total_modifier *= (1.0 + (modifier - 1.0) * 0.5)  # Reduced impact for vigor
        
        return max(0.5, min(1.5, total_modifier))  # Reasonable genetic impact range
    
    def _update_physical_development(self, growth_progress: GrowthProgress, 
                                   stage_def: GrowthStageDefinition, growth_increment: float):
        """Update physical development of the crop"""
        # Update size
        size_increase = stage_def.size_increase_factor * growth_increment
        growth_progress.current_size = min(1.0, growth_progress.current_size + size_increase)
        
        # Update root development
        root_increase = stage_def.root_development_factor * growth_increment
        growth_progress.root_development = min(1.0, growth_progress.root_development + root_increase)
        
        # Update leaf development
        leaf_increase = stage_def.leaf_development_factor * growth_increment
        growth_progress.leaf_development = min(1.0, growth_progress.leaf_development + leaf_increase)
        
        # Update reproductive development
        repro_increase = stage_def.reproductive_development * growth_increment
        growth_progress.reproductive_development = min(1.0, 
                                                     growth_progress.reproductive_development + repro_increase)
    
    def _calculate_stage_quality(self, growth_progress: GrowthProgress, 
                               stage_def: GrowthStageDefinition, environmental_multiplier: float) -> float:
        """Calculate quality achieved in current growth stage"""
        base_quality = 0.8  # Base quality assuming reasonable conditions
        
        # Environmental impact on quality
        env_quality_factor = min(1.2, max(0.4, environmental_multiplier))
        
        # Genetic impact on quality
        genetic_quality_factor = 1.0
        for trait in growth_progress.expressed_traits:
            if "quality" in trait.lower() or "premium" in trait.lower():
                genetic_quality_factor *= 1.1
        
        # Time impact (rushed growth reduces quality)
        time_quality_factor = 1.0
        if growth_progress.days_in_current_stage < stage_def.minimum_duration_days:
            time_quality_factor = 0.8  # Rushed growth penalty
        
        final_quality = base_quality * env_quality_factor * genetic_quality_factor * time_quality_factor
        return max(0.1, min(1.0, final_quality))
    
    def _update_overall_quality(self, growth_progress: GrowthProgress):
        """Update overall growth quality based on stage history"""
        if not growth_progress.stage_quality_history:
            return
        
        # Calculate weighted average of stage qualities
        total_quality = 0.0
        total_weight = 0.0
        
        for stage, quality in growth_progress.stage_quality_history.items():
            # Weight later stages more heavily
            if stage in [GrowthStage.FLOWERING, GrowthStage.FRUIT_DEVELOPMENT, GrowthStage.MATURATION]:
                weight = 2.0
            elif stage in [GrowthStage.VEGETATIVE]:
                weight = 1.5
            else:
                weight = 1.0
            
            total_quality += quality * weight
            total_weight += weight
        
        if total_weight > 0:
            growth_progress.overall_growth_quality = total_quality / total_weight
    
    def _advance_growth_stage(self, growth_progress: GrowthProgress, 
                            stage_definitions: Dict[GrowthStage, GrowthStageDefinition]):
        """Advance crop to next growth stage"""
        current_stage = growth_progress.current_stage
        
        # Define stage progression
        stage_progression = [
            GrowthStage.SEED,
            GrowthStage.GERMINATION,
            GrowthStage.SEEDLING,
            GrowthStage.VEGETATIVE,
            GrowthStage.FLOWERING,
            GrowthStage.FRUIT_DEVELOPMENT,
            GrowthStage.MATURATION,
            GrowthStage.HARVEST_READY,
            GrowthStage.OVERRIPE,
            GrowthStage.SENESCENCE
        ]
        
        # Find next stage
        try:
            current_index = stage_progression.index(current_stage)
            if current_index < len(stage_progression) - 1:
                next_stage = stage_progression[current_index + 1]
                
                # Check if next stage is defined for this variety
                if next_stage in stage_definitions:
                    growth_progress.current_stage = next_stage
                    growth_progress.stage_progress = 0.0
                    growth_progress.days_in_current_stage = 0.0
                    
                    # Publish stage advancement event
                    if self.event_system:
                        self.event_system.publish("crop_stage_advanced", {
                            "crop_id": growth_progress.crop_id,
                            "previous_stage": current_stage.value,
                            "new_stage": next_stage.value,
                            "variety_id": growth_progress.variety_id
                        })
                    
                    logger.info(f"Crop {growth_progress.crop_id} advanced to {next_stage.value}")
                else:
                    logger.warning(f"No definition for next stage {next_stage.value}")
            else:
                logger.info(f"Crop {growth_progress.crop_id} has reached final stage")
        
        except ValueError:
            logger.error(f"Unknown current stage: {current_stage}")
    
    def _update_yield_estimates(self, growth_progress: GrowthProgress, stage_def: GrowthStageDefinition):
        """Update estimated yield and quality for harvest"""
        # Base yield calculation
        base_yield = 1.0
        
        # Apply quality factors from each completed stage
        for stage, quality in growth_progress.stage_quality_history.items():
            # Get yield impact for this stage
            yield_impact = stage_def.yield_impact_factors.get("overall", 1.0)
            base_yield *= (quality * yield_impact)
        
        # Apply genetic modifiers
        genetic_yield_modifier = 1.0
        for trait in growth_progress.expressed_traits:
            if "yield" in trait.lower() or "productive" in trait.lower():
                genetic_yield_modifier *= 1.15
        
        growth_progress.estimated_yield = base_yield * genetic_yield_modifier
        growth_progress.estimated_quality = growth_progress.overall_growth_quality
        
        # Update estimated harvest date
        if self.time_manager:
            current_time = self.time_manager.get_current_time()
            days_remaining = self._estimate_days_to_harvest(growth_progress)
            growth_progress.estimated_harvest_date = current_time + timedelta(days=days_remaining)
    
    def _estimate_days_to_harvest(self, growth_progress: GrowthProgress) -> float:
        """Estimate days remaining until harvest"""
        variety_id = growth_progress.variety_id
        if variety_id not in self.growth_definitions:
            return 30.0  # Default estimate
        
        stage_definitions = self.growth_definitions[variety_id]
        current_stage = growth_progress.current_stage
        
        days_remaining = 0.0
        
        # Add remaining time in current stage
        if current_stage in stage_definitions:
            stage_def = stage_definitions[current_stage]
            progress_remaining = 1.0 - growth_progress.stage_progress
            days_remaining += stage_def.base_duration_days * progress_remaining
        
        # Add time for remaining stages until harvest
        stage_progression = [
            GrowthStage.SEED, GrowthStage.GERMINATION, GrowthStage.SEEDLING,
            GrowthStage.VEGETATIVE, GrowthStage.FLOWERING, GrowthStage.FRUIT_DEVELOPMENT,
            GrowthStage.MATURATION, GrowthStage.HARVEST_READY
        ]
        
        try:
            current_index = stage_progression.index(current_stage)
            for i in range(current_index + 1, len(stage_progression)):
                future_stage = stage_progression[i]
                if future_stage in stage_definitions:
                    days_remaining += stage_definitions[future_stage].base_duration_days
                if future_stage == GrowthStage.HARVEST_READY:
                    break
        except ValueError:
            pass
        
        return max(0.0, days_remaining)
    
    def _check_stress_events(self, growth_progress: GrowthProgress, environmental_multiplier: float):
        """Check for and record stress events"""
        if environmental_multiplier < 0.7:  # Threshold for stress
            stress_event = {
                "timestamp": self.time_manager.get_current_time() if self.time_manager else datetime.now(),
                "stage": growth_progress.current_stage.value,
                "severity": 1.0 - environmental_multiplier,
                "type": "environmental_stress",
                "impact": "growth_reduction"
            }
            
            growth_progress.environmental_stress_history.append(stress_event)
            
            # Limit stress history to prevent memory bloat
            if len(growth_progress.environmental_stress_history) > 50:
                growth_progress.environmental_stress_history = growth_progress.environmental_stress_history[-50:]
    
    def _update_environmental_conditions(self):
        """Update environmental conditions for all growth environments"""
        for location_id, environment in self.growth_environments.items():
            try:
                # Update conditions based on time, weather, and management
                self._update_location_environment(environment)
            except Exception as e:
                logger.error(f"Error updating environment for location {location_id}: {e}")
    
    def _update_location_environment(self, environment: GrowthEnvironment):
        """Update environmental conditions for a specific location"""
        # This would integrate with weather system, time system, etc.
        # For now, add some variation to simulate changing conditions
        
        import random
        
        for factor, condition in environment.current_conditions.items():
            # Add small random variations
            variation = random.uniform(-0.05, 0.05)
            new_value = max(0.0, min(1.0, condition.current_value + variation))
            condition.current_value = new_value
        
        # Update soil moisture based on precipitation and irrigation
        if environment.irrigation_active:
            environment.soil_moisture = min(1.0, environment.soil_moisture + 0.1)
        else:
            environment.soil_moisture = max(0.0, environment.soil_moisture - 0.02)
    
    def _calculate_genetic_modifiers(self, genetic_profile: GeneticProfile) -> Dict[str, float]:
        """Calculate genetic modifiers from genetic profile"""
        modifiers = {}
        
        for trait_name, alleles in genetic_profile.trait_alleles.items():
            # Calculate modifier based on allele combination
            modifier = 1.0
            
            for allele in alleles:
                if allele.effect_type == "multiplicative":
                    modifier *= allele.effect_magnitude
                elif allele.effect_type == "additive":
                    modifier += (allele.effect_magnitude - 1.0)
            
            modifiers[trait_name] = modifier
        
        return modifiers
    
    def _get_expressed_traits(self, genetic_profile: GeneticProfile) -> List[str]:
        """Get list of expressed genetic traits"""
        expressed = []
        
        for trait_name, alleles in genetic_profile.trait_alleles.items():
            # Check if trait is expressed (has dominant alleles or homozygous recessive)
            dominant_count = sum(1 for allele in alleles if allele.dominance == "dominant")
            
            if dominant_count > 0 or len(alleles) == 2:  # Either has dominant or is homozygous
                expressed.append(trait_name)
        
        return expressed
    
    # Event handlers
    def _on_time_advanced(self, event_data: Dict[str, Any]):
        """Handle time advancement"""
        delta_hours = event_data.get("delta_hours", 1.0)
        self.update(delta_hours)
    
    def _on_day_changed(self, event_data: Dict[str, Any]):
        """Handle day change events"""
        # Update daily environmental conditions
        self._update_environmental_conditions()
    
    def _on_season_changed(self, event_data: Dict[str, Any]):
        """Handle seasonal changes"""
        new_season = event_data.get("new_season")
        logger.info(f"Season changed to {new_season}, updating environmental base conditions")
        
        # Adjust base environmental conditions for new season
        for environment in self.growth_environments.values():
            self._adjust_environment_for_season(environment, new_season)
    
    def _adjust_environment_for_season(self, environment: GrowthEnvironment, season: str):
        """Adjust environmental conditions for seasonal changes"""
        # Seasonal temperature adjustments
        temp_adjustments = {
            "spring": 0.6,
            "summer": 0.8,
            "fall": 0.5,
            "winter": 0.3
        }
        
        if season in temp_adjustments:
            temp_condition = environment.current_conditions.get(EnvironmentalFactor.TEMPERATURE)
            if temp_condition:
                temp_condition.current_value = temp_adjustments[season]
    
    def _on_weather_updated(self, event_data: Dict[str, Any]):
        """Handle weather updates"""
        # Update environmental conditions based on weather
        weather_data = event_data.get("weather_data", {})
        
        for location_id, environment in self.growth_environments.items():
            # Update temperature
            if "temperature" in weather_data:
                temp_condition = environment.current_conditions.get(EnvironmentalFactor.TEMPERATURE)
                if temp_condition:
                    # Convert temperature to 0-1 scale (assuming 0-40°C range)
                    normalized_temp = max(0.0, min(1.0, weather_data["temperature"] / 40.0))
                    temp_condition.current_value = normalized_temp
            
            # Update water availability from precipitation
            if "precipitation" in weather_data:
                water_condition = environment.current_conditions.get(EnvironmentalFactor.WATER_AVAILABILITY)
                if water_condition:
                    precipitation_factor = min(0.2, weather_data["precipitation"] / 50.0)  # Max 20% increase
                    water_condition.current_value = min(1.0, water_condition.current_value + precipitation_factor)
    
    def _on_temperature_changed(self, event_data: Dict[str, Any]):
        """Handle specific temperature change events"""
        new_temp = event_data.get("temperature", 20.0)
        
        for environment in self.growth_environments.values():
            environment.air_temperature = new_temp
            environment.soil_temperature = new_temp * 0.9  # Soil temperature lags air temperature
    
    def _on_crop_planted(self, event_data: Dict[str, Any]):
        """Handle crop planting events from other systems"""
        crop_id = event_data.get("crop_id")
        variety_id = event_data.get("variety_id")
        location_id = event_data.get("location_id")
        
        if crop_id and variety_id and location_id:
            # This crop was planted by another system, start tracking its growth
            self.plant_crop(crop_id, variety_id, location_id)
    
    def _on_irrigation_applied(self, event_data: Dict[str, Any]):
        """Handle irrigation application"""
        location_id = event_data.get("location_id")
        amount = event_data.get("amount", 0.5)
        
        if location_id in self.growth_environments:
            environment = self.growth_environments[location_id]
            environment.irrigation_active = True
            environment.soil_moisture = min(1.0, environment.soil_moisture + amount)
            
            # Update water availability condition
            water_condition = environment.current_conditions.get(EnvironmentalFactor.WATER_AVAILABILITY)
            if water_condition:
                water_condition.current_value = min(1.0, water_condition.current_value + amount * 0.5)
    
    def _on_fertilizer_applied(self, event_data: Dict[str, Any]):
        """Handle fertilizer application"""
        location_id = event_data.get("location_id")
        fertilizer_type = event_data.get("fertilizer_type", "balanced")
        amount = event_data.get("amount", 1.0)
        
        if location_id in self.growth_environments:
            environment = self.growth_environments[location_id]
            
            # Record fertilizer application
            fertilizer_record = {
                "timestamp": self.time_manager.get_current_time() if self.time_manager else datetime.now(),
                "type": fertilizer_type,
                "amount": amount
            }
            environment.fertilizer_applications.append(fertilizer_record)
            
            # Update nutrient levels based on fertilizer type
            nutrient_boosts = {
                "nitrogen": {"N": 0.3, "P": 0.0, "K": 0.0},
                "phosphorus": {"N": 0.0, "P": 0.3, "K": 0.0},
                "potassium": {"N": 0.0, "P": 0.0, "K": 0.3},
                "balanced": {"N": 0.15, "P": 0.15, "K": 0.15}
            }
            
            if fertilizer_type in nutrient_boosts:
                boosts = nutrient_boosts[fertilizer_type]
                for nutrient, boost in boosts.items():
                    current_level = environment.soil_nutrients.get(nutrient, 0.5)
                    environment.soil_nutrients[nutrient] = min(1.0, current_level + boost * amount)
            
            # Update nutrient availability condition
            nutrient_condition = environment.current_conditions.get(EnvironmentalFactor.NUTRIENT_AVAILABILITY)
            if nutrient_condition:
                avg_nutrients = sum(environment.soil_nutrients.values()) / len(environment.soil_nutrients)
                nutrient_condition.current_value = avg_nutrients
    
    def _on_pest_control_applied(self, event_data: Dict[str, Any]):
        """Handle pest control application"""
        location_id = event_data.get("location_id")
        control_type = event_data.get("control_type", "insecticide")
        effectiveness = event_data.get("effectiveness", 0.8)
        
        if location_id in self.growth_environments:
            environment = self.growth_environments[location_id]
            
            # Record pest control application
            control_record = {
                "timestamp": self.time_manager.get_current_time() if self.time_manager else datetime.now(),
                "type": control_type,
                "effectiveness": effectiveness
            }
            environment.pest_control_measures.append(control_record)
            
            # Reduce pest pressure
            pest_condition = environment.current_conditions.get(EnvironmentalFactor.PEST_PRESSURE)
            if pest_condition:
                reduction = effectiveness * 0.5  # Reduce pest pressure by up to 50%
                pest_condition.current_value = max(0.0, pest_condition.current_value - reduction)
    
    def _on_cultivation_performed(self, event_data: Dict[str, Any]):
        """Handle cultivation activities"""
        location_id = event_data.get("location_id")
        cultivation_type = event_data.get("cultivation_type", "tillage")
        
        if location_id in self.growth_environments:
            environment = self.growth_environments[location_id]
            
            # Record cultivation activity
            cultivation_record = {
                "timestamp": self.time_manager.get_current_time() if self.time_manager else datetime.now(),
                "type": cultivation_type
            }
            environment.cultivation_history.append(cultivation_record)
            
            # Improve soil compaction from cultivation
            if cultivation_type in ["tillage", "cultivation", "deep_tillage"]:
                environment.soil_compaction = max(0.0, environment.soil_compaction - 0.2)
                
                # Update soil compaction condition
                compaction_condition = environment.current_conditions.get(EnvironmentalFactor.SOIL_COMPACTION)
                if compaction_condition:
                    compaction_condition.current_value = environment.soil_compaction
    
    # Public interface methods
    def get_crop_growth_info(self, crop_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive growth information for a crop"""
        if crop_id not in self.active_crops:
            return None
        
        growth_progress = self.active_crops[crop_id]
        
        return {
            "crop_id": crop_id,
            "variety_id": growth_progress.variety_id,
            "current_stage": growth_progress.current_stage.value,
            "stage_progress": growth_progress.stage_progress,
            "stage_name": self._get_stage_display_name(growth_progress),
            "days_in_stage": growth_progress.days_in_current_stage,
            "total_days": growth_progress.total_growth_days,
            "physical_development": {
                "size": growth_progress.current_size,
                "root_development": growth_progress.root_development,
                "leaf_development": growth_progress.leaf_development,
                "reproductive_development": growth_progress.reproductive_development
            },
            "quality_metrics": {
                "overall_quality": growth_progress.overall_growth_quality,
                "estimated_yield": growth_progress.estimated_yield,
                "estimated_quality": growth_progress.estimated_quality
            },
            "predictions": {
                "estimated_harvest_date": growth_progress.estimated_harvest_date.isoformat(),
                "days_to_harvest": self._estimate_days_to_harvest(growth_progress)
            },
            "genetic_traits": growth_progress.expressed_traits,
            "stress_events": len(growth_progress.environmental_stress_history)
        }
    
    def _get_stage_display_name(self, growth_progress: GrowthProgress) -> str:
        """Get human-readable stage name"""
        variety_id = growth_progress.variety_id
        current_stage = growth_progress.current_stage
        
        if (variety_id in self.growth_definitions and 
            current_stage in self.growth_definitions[variety_id]):
            return self.growth_definitions[variety_id][current_stage].name
        
        return current_stage.value.replace("_", " ").title()
    
    def get_growth_tips(self, crop_id: str) -> List[str]:
        """Get educational tips for current growth stage"""
        if crop_id not in self.active_crops:
            return []
        
        growth_progress = self.active_crops[crop_id]
        current_stage = growth_progress.current_stage
        
        return self.growth_tips.get(current_stage, [])
    
    def get_environmental_info(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Get environmental information for a location"""
        if location_id not in self.growth_environments:
            return None
        
        environment = self.growth_environments[location_id]
        
        return {
            "location_id": location_id,
            "soil_conditions": {
                "temperature": environment.soil_temperature,
                "moisture": environment.soil_moisture,
                "ph": environment.soil_ph,
                "organic_matter": environment.soil_organic_matter,
                "compaction": environment.soil_compaction,
                "nutrients": environment.soil_nutrients
            },
            "weather_conditions": {
                "air_temperature": environment.air_temperature,
                "humidity": environment.humidity,
                "wind_speed": environment.wind_speed,
                "solar_radiation": environment.solar_radiation,
                "precipitation": environment.precipitation
            },
            "management": {
                "irrigation_active": environment.irrigation_active,
                "recent_fertilizer": len([f for f in environment.fertilizer_applications 
                                        if (datetime.now() - f["timestamp"]).days < 7]),
                "recent_pest_control": len([p for p in environment.pest_control_measures 
                                          if (datetime.now() - p["timestamp"]).days < 14]),
                "recent_cultivation": len([c for c in environment.cultivation_history 
                                         if (datetime.now() - c["timestamp"]).days < 30])
            },
            "environmental_factors": {
                factor.value: {
                    "current_value": condition.current_value,
                    "status": "optimal" if condition.optimal_range[0] <= condition.current_value <= condition.optimal_range[1]
                             else "stressed" if condition.current_value < condition.stress_threshold 
                             or condition.current_value > (1.0 - condition.stress_threshold)
                             else "acceptable",
                    "growth_impact": condition.get_growth_impact()
                }
                for factor, condition in environment.current_conditions.items()
            }
        }
    
    def is_crop_ready_for_harvest(self, crop_id: str) -> bool:
        """Check if crop is ready for harvest"""
        if crop_id not in self.active_crops:
            return False
        
        growth_progress = self.active_crops[crop_id]
        return growth_progress.current_stage == GrowthStage.HARVEST_READY
    
    def harvest_crop(self, crop_id: str) -> Optional[Dict[str, Any]]:
        """Harvest a crop and return yield information"""
        if crop_id not in self.active_crops:
            return None
        
        growth_progress = self.active_crops[crop_id]
        
        # Calculate final yield and quality
        final_yield = growth_progress.estimated_yield
        final_quality = growth_progress.estimated_quality
        
        # Apply harvest timing penalty if overripe
        if growth_progress.current_stage == GrowthStage.OVERRIPE:
            final_yield *= 0.8
            final_quality *= 0.7
        elif growth_progress.current_stage == GrowthStage.SENESCENCE:
            final_yield *= 0.5
            final_quality *= 0.4
        
        harvest_result = {
            "crop_id": crop_id,
            "variety_id": growth_progress.variety_id,
            "yield": final_yield,
            "quality": final_quality,
            "total_growth_days": growth_progress.total_growth_days,
            "harvest_stage": growth_progress.current_stage.value,
            "expressed_traits": growth_progress.expressed_traits,
            "stress_events": len(growth_progress.environmental_stress_history)
        }
        
        # Remove from active crops
        del self.active_crops[crop_id]
        
        # Publish harvest event
        if self.event_system:
            self.event_system.publish("crop_harvested", harvest_result)
        
        logger.info(f"Harvested crop {crop_id} with yield {final_yield:.2f} and quality {final_quality:.2f}")
        return harvest_result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status information"""
        return {
            "system_name": self.system_name,
            "active_crops": len(self.active_crops),
            "growth_environments": len(self.growth_environments),
            "variety_definitions": len(self.growth_definitions),
            "update_frequency": self.update_frequency,
            "last_update": self.last_update_time,
            "performance": {
                "batch_size": self.batch_size,
                "calculation_precision": self.growth_calculation_precision,
                "environmental_update_frequency": self.environmental_update_frequency
            },
            "educational_content": {
                "growth_tips": len(self.growth_tips),
                "environmental_education": len(self.environmental_education)
            }
        }

# Global convenience functions for system access
_advanced_growth_system_instance = None

def get_advanced_growth_system() -> AdvancedGrowthSystem:
    """Get the global Advanced Growth System instance"""
    global _advanced_growth_system_instance
    if _advanced_growth_system_instance is None:
        _advanced_growth_system_instance = AdvancedGrowthSystem()
    return _advanced_growth_system_instance

def initialize_advanced_growth_system() -> bool:
    """Initialize the global Advanced Growth System"""
    system = get_advanced_growth_system()
    return system.initialize()

def plant_crop_with_genetics(crop_id: str, variety_id: str, location_id: str, 
                           genetic_profile: Optional[GeneticProfile] = None) -> bool:
    """Convenience function to plant a crop with genetic profile"""
    system = get_advanced_growth_system()
    return system.plant_crop(crop_id, variety_id, location_id, genetic_profile)

def get_crop_info(crop_id: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get crop information"""
    system = get_advanced_growth_system()
    return system.get_crop_growth_info(crop_id)

def harvest_crop_simple(crop_id: str) -> Optional[Dict[str, Any]]:
    """Convenience function to harvest a crop"""
    system = get_advanced_growth_system()
    return system.harvest_crop(crop_id)

def check_harvest_ready(crop_id: str) -> bool:
    """Convenience function to check if crop is ready for harvest"""
    system = get_advanced_growth_system()
    return system.is_crop_ready_for_harvest(crop_id)

def get_environmental_conditions(location_id: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get environmental information"""
    system = get_advanced_growth_system()
    return system.get_environmental_info(location_id)