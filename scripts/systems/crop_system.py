"""
Crop Growth & Agricultural Systems - Comprehensive Farming Simulation for AgriFun

This system provides realistic agricultural mechanics with multi-stage crop growth,
soil health management, irrigation, fertilization, and integrated farming operations.
Integrates with Time Management for seasonal cycles, Economy for market dynamics,
and Employee Management for farming task coordination.

Key Features:
- Multi-stage crop growth with realistic timing
- Comprehensive soil health system (N-P-K levels, pH, organic matter)
- Irrigation and water management
- Fertilization and soil amendment systems
- Crop rotation and soil conservation
- Pest and disease management framework
- Yield prediction and quality calculation
- Harvest timing optimization
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
from ..systems.time_system import get_time_system, Season, WeatherType
from ..systems.economy_system import get_economy_system, TransactionType


class CropType(Enum):
    """Types of crops that can be grown"""
    CORN = "corn"
    WHEAT = "wheat"
    TOMATOES = "tomatoes"
    LETTUCE = "lettuce"
    SOYBEANS = "soybeans"
    POTATOES = "potatoes"
    CARROTS = "carrots"
    ONIONS = "onions"


class CropStage(Enum):
    """Growth stages of crops"""
    EMPTY = "empty"              # No crop planted
    PLANTED = "planted"          # Seed in ground
    GERMINATED = "germinated"    # Seedling emerged
    VEGETATIVE = "vegetative"    # Growing phase
    FLOWERING = "flowering"      # Reproductive phase
    FRUIT_DEVELOPMENT = "fruit_development"  # Fruit/grain formation
    MATURE = "mature"            # Ready for harvest
    OVERRIPE = "overripe"        # Past optimal harvest time


class SoilType(Enum):
    """Types of soil composition"""
    CLAY = "clay"
    LOAM = "loam"
    SAND = "sand"
    SILT = "silt"


class FertilizerType(Enum):
    """Types of fertilizers and amendments"""
    NITROGEN = "nitrogen"        # Promotes leafy growth
    PHOSPHORUS = "phosphorus"    # Root and flower development
    POTASSIUM = "potassium"      # Overall plant health
    COMPOST = "compost"          # Organic matter and slow release nutrients
    LIME = "lime"               # pH adjustment (raise)
    SULFUR = "sulfur"           # pH adjustment (lower)


@dataclass
class SoilNutrients:
    """Soil nutrient levels and characteristics"""
    nitrogen: float = 50.0       # N level (0-100)
    phosphorus: float = 50.0     # P level (0-100)
    potassium: float = 50.0      # K level (0-100)
    ph_level: float = 7.0        # Soil pH (4.0-9.0)
    organic_matter: float = 3.0  # Organic matter percentage (0-10)
    water_content: float = 50.0  # Soil moisture (0-100)
    compaction: float = 0.0      # Soil compaction (0-100, lower is better)
    
    def get_fertility_rating(self) -> float:
        """Calculate overall soil fertility (0.0-1.0)"""
        # Optimal NPK levels
        n_score = 1.0 - abs(self.nitrogen - 70.0) / 100.0
        p_score = 1.0 - abs(self.phosphorus - 60.0) / 100.0
        k_score = 1.0 - abs(self.potassium - 65.0) / 100.0
        
        # pH score (optimal around 6.5-7.0)
        ph_score = 1.0 - abs(self.ph_level - 6.75) / 3.0
        
        # Organic matter score (optimal around 4-6%)
        om_score = min(1.0, self.organic_matter / 6.0)
        
        # Water content score (optimal around 60-80%)
        water_score = 1.0 - abs(self.water_content - 70.0) / 100.0
        
        # Compaction penalty
        compaction_penalty = self.compaction / 100.0
        
        # Weighted average
        fertility = (n_score * 0.2 + p_score * 0.15 + k_score * 0.15 + 
                    ph_score * 0.2 + om_score * 0.15 + water_score * 0.1) - compaction_penalty
        
        return max(0.0, min(1.0, fertility))


@dataclass
class CropProperties:
    """Properties and requirements for different crop types"""
    crop_type: CropType
    
    # Growth timing (in days)
    days_to_germination: int = 7
    days_to_vegetative: int = 25
    days_to_flowering: int = 50
    days_to_fruit_development: int = 70
    days_to_maturity: int = 90
    
    # Environmental requirements
    optimal_temp_min: float = 15.0    # Celsius
    optimal_temp_max: float = 25.0    # Celsius
    water_requirement: float = 2.0    # Water units per day
    light_requirement: float = 8.0    # Hours of light per day
    
    # Soil preferences
    preferred_ph_min: float = 6.0
    preferred_ph_max: float = 7.5
    nitrogen_demand: float = 1.5      # Daily N consumption
    phosphorus_demand: float = 0.8    # Daily P consumption
    potassium_demand: float = 1.2     # Daily K consumption
    
    # Yield characteristics
    base_yield_per_plant: float = 5.0
    quality_factors: Dict[str, float] = field(default_factory=dict)
    
    # Market characteristics
    base_market_value: float = 3.0    # Base price per unit
    storage_life_days: int = 30       # Days before spoilage
    
    def get_growth_stage_duration(self, stage: CropStage) -> int:
        """Get duration in days for a specific growth stage"""
        durations = {
            CropStage.PLANTED: self.days_to_germination,
            CropStage.GERMINATED: self.days_to_vegetative - self.days_to_germination,
            CropStage.VEGETATIVE: self.days_to_flowering - self.days_to_vegetative,
            CropStage.FLOWERING: self.days_to_fruit_development - self.days_to_flowering,
            CropStage.FRUIT_DEVELOPMENT: self.days_to_maturity - self.days_to_fruit_development,
            CropStage.MATURE: 14,  # Grace period before overripe
            CropStage.OVERRIPE: float('inf')
        }
        return durations.get(stage, 0)


@dataclass
class PlantedCrop:
    """A crop planted on a specific tile"""
    crop_id: str
    crop_type: CropType
    plant_date: int              # Game time when planted
    current_stage: CropStage = CropStage.PLANTED
    stage_progress: float = 0.0  # Progress through current stage (0.0-1.0)
    
    # Health and growth
    health: float = 100.0        # Plant health (0-100)
    growth_rate: float = 1.0     # Growth rate modifier
    stress_level: float = 0.0    # Environmental stress (0-100)
    
    # Care tracking
    last_watered: int = 0        # Last watering time
    last_fertilized: int = 0     # Last fertilization time
    fertilizer_applied: Dict[FertilizerType, float] = field(default_factory=dict)
    
    # Yield prediction
    expected_yield: float = 0.0  # Predicted harvest amount
    quality_rating: float = 1.0  # Quality multiplier (0.0-2.0)
    
    def get_days_planted(self, current_game_time: int) -> int:
        """Get number of days since planting"""
        return (current_game_time - self.plant_date) // (24 * 60)  # Convert minutes to days
    
    def is_ready_for_harvest(self) -> bool:
        """Check if crop is ready for harvest"""
        return self.current_stage in [CropStage.MATURE, CropStage.OVERRIPE]
    
    def get_harvest_value(self) -> float:
        """Calculate harvest value based on yield and quality"""
        return self.expected_yield * self.quality_rating


@dataclass
class FarmTile:
    """Represents a single farm tile with soil and crop information"""
    x: int
    y: int
    
    # Soil characteristics
    soil_type: SoilType = SoilType.LOAM
    soil_nutrients: SoilNutrients = field(default_factory=SoilNutrients)
    
    # Crop information
    planted_crop: Optional[PlantedCrop] = None
    crop_history: List[CropType] = field(default_factory=list)
    
    # Infrastructure
    has_irrigation: bool = False
    irrigation_efficiency: float = 0.8  # Water delivery efficiency
    
    # Tile state
    is_tilled: bool = False
    last_tilled: int = 0
    needs_cultivation: bool = False
    
    def is_empty(self) -> bool:
        """Check if tile has no crop"""
        return self.planted_crop is None
    
    def can_plant(self) -> bool:
        """Check if tile is ready for planting"""
        return self.is_tilled and self.is_empty()
    
    def get_soil_fertility(self) -> float:
        """Get soil fertility rating"""
        return self.soil_nutrients.get_fertility_rating()


class CropGrowthSimulator:
    """Simulates crop growth based on environmental conditions"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger('CropGrowthSimulator')
        
        # Load crop properties
        self.crop_properties = self._initialize_crop_properties()
    
    def _initialize_crop_properties(self) -> Dict[CropType, CropProperties]:
        """Initialize crop property definitions"""
        properties = {}
        
        # Corn - Staple grain crop
        properties[CropType.CORN] = CropProperties(
            crop_type=CropType.CORN,
            days_to_germination=7,
            days_to_vegetative=30,
            days_to_flowering=60,
            days_to_fruit_development=90,
            days_to_maturity=120,
            optimal_temp_min=20.0,
            optimal_temp_max=30.0,
            water_requirement=3.0,
            nitrogen_demand=2.0,
            phosphorus_demand=1.0,
            potassium_demand=1.5,
            base_yield_per_plant=8.0,
            base_market_value=5.0
        )
        
        # Wheat - Cool season grain
        properties[CropType.WHEAT] = CropProperties(
            crop_type=CropType.WHEAT,
            days_to_germination=10,
            days_to_vegetative=45,
            days_to_flowering=75,
            days_to_fruit_development=95,
            days_to_maturity=110,
            optimal_temp_min=15.0,
            optimal_temp_max=25.0,
            water_requirement=2.5,
            nitrogen_demand=1.8,
            phosphorus_demand=0.8,
            potassium_demand=1.0,
            base_yield_per_plant=6.0,
            base_market_value=6.0
        )
        
        # Tomatoes - High-value vegetable
        properties[CropType.TOMATOES] = CropProperties(
            crop_type=CropType.TOMATOES,
            days_to_germination=5,
            days_to_vegetative=25,
            days_to_flowering=45,
            days_to_fruit_development=65,
            days_to_maturity=85,
            optimal_temp_min=18.0,
            optimal_temp_max=28.0,
            water_requirement=4.0,
            nitrogen_demand=2.5,
            phosphorus_demand=1.5,
            potassium_demand=2.0,
            base_yield_per_plant=12.0,
            base_market_value=8.0,
            storage_life_days=14
        )
        
        # Lettuce - Quick-growing leafy green
        properties[CropType.LETTUCE] = CropProperties(
            crop_type=CropType.LETTUCE,
            days_to_germination=3,
            days_to_vegetative=15,
            days_to_flowering=30,
            days_to_fruit_development=40,
            days_to_maturity=50,
            optimal_temp_min=10.0,
            optimal_temp_max=20.0,
            water_requirement=5.0,
            nitrogen_demand=3.0,
            phosphorus_demand=1.0,
            potassium_demand=1.5,
            base_yield_per_plant=3.0,
            base_market_value=12.0,
            storage_life_days=7
        )
        
        # Soybeans - Nitrogen-fixing legume
        properties[CropType.SOYBEANS] = CropProperties(
            crop_type=CropType.SOYBEANS,
            days_to_germination=8,
            days_to_vegetative=35,
            days_to_flowering=65,
            days_to_fruit_development=85,
            days_to_maturity=110,
            optimal_temp_min=18.0,
            optimal_temp_max=28.0,
            water_requirement=2.8,
            nitrogen_demand=0.5,  # Low N demand due to nitrogen fixation
            phosphorus_demand=1.2,
            potassium_demand=1.8,
            base_yield_per_plant=7.0,
            base_market_value=7.0
        )
        
        return properties
    
    def simulate_growth(self, crop: PlantedCrop, tile: FarmTile, 
                       weather_conditions: Dict[str, Any], delta_time_hours: float) -> Dict[str, Any]:
        """Simulate crop growth for a time period"""
        if not crop or crop.current_stage == CropStage.EMPTY:
            return {'growth_occurred': False}
        
        crop_props = self.crop_properties[crop.crop_type]
        
        # Calculate environmental factors
        temperature_factor = self._calculate_temperature_factor(crop_props, weather_conditions)
        water_factor = self._calculate_water_factor(crop_props, tile, weather_conditions)
        light_factor = self._calculate_light_factor(crop_props, weather_conditions)
        soil_factor = self._calculate_soil_factor(crop_props, tile)
        
        # Overall growth rate
        growth_multiplier = (temperature_factor * water_factor * light_factor * soil_factor)
        
        # Calculate stress
        stress_factors = []
        if temperature_factor < 0.7:
            stress_factors.append("temperature")
        if water_factor < 0.6:
            stress_factors.append("water")
        if soil_factor < 0.5:
            stress_factors.append("soil")
        
        crop.stress_level = max(0, min(100, len(stress_factors) * 25))
        
        # Apply growth
        base_growth_rate = 1.0 / crop_props.get_growth_stage_duration(crop.current_stage)
        actual_growth_rate = base_growth_rate * growth_multiplier * (delta_time_hours / 24.0)
        
        crop.stage_progress += actual_growth_rate
        
        # Check for stage advancement
        stage_changed = False
        if crop.stage_progress >= 1.0:
            crop.stage_progress = 0.0
            new_stage = self._advance_crop_stage(crop.current_stage)
            if new_stage != crop.current_stage:
                crop.current_stage = new_stage
                stage_changed = True
        
        # Update yield prediction
        self._update_yield_prediction(crop, crop_props, tile, growth_multiplier)
        
        # Consume soil nutrients
        self._consume_soil_nutrients(crop_props, tile, delta_time_hours)
        
        return {
            'growth_occurred': True,
            'stage_changed': stage_changed,
            'new_stage': crop.current_stage.value if stage_changed else None,
            'growth_rate': growth_multiplier,
            'stress_level': crop.stress_level,
            'stress_factors': stress_factors
        }
    
    def _calculate_temperature_factor(self, crop_props: CropProperties, weather: Dict[str, Any]) -> float:
        """Calculate temperature growth factor"""
        temp = weather.get('temperature', 20.0)
        optimal_min = crop_props.optimal_temp_min
        optimal_max = crop_props.optimal_temp_max
        
        if optimal_min <= temp <= optimal_max:
            return 1.0
        elif temp < optimal_min:
            # Cold stress
            return max(0.1, 1.0 - (optimal_min - temp) / 10.0)
        else:
            # Heat stress
            return max(0.1, 1.0 - (temp - optimal_max) / 15.0)
    
    def _calculate_water_factor(self, crop_props: CropProperties, tile: FarmTile, weather: Dict[str, Any]) -> float:
        """Calculate water availability factor"""
        soil_moisture = tile.soil_nutrients.water_content
        water_need = crop_props.water_requirement * 10  # Convert to percentage scale
        
        # Add irrigation bonus
        if tile.has_irrigation:
            effective_moisture = soil_moisture * tile.irrigation_efficiency
        else:
            effective_moisture = soil_moisture
        
        # Add rainfall
        if 'precipitation' in weather:
            effective_moisture += weather['precipitation'] * 5  # Rainfall bonus
        
        effective_moisture = min(100, effective_moisture)
        
        if effective_moisture >= water_need:
            return 1.0
        else:
            return max(0.2, effective_moisture / water_need)
    
    def _calculate_light_factor(self, crop_props: CropProperties, weather: Dict[str, Any]) -> float:
        """Calculate light availability factor"""
        # Simplified light calculation based on weather
        weather_type = weather.get('weather_type', 'clear')
        
        light_factors = {
            'clear': 1.0,
            'partly_cloudy': 0.8,
            'cloudy': 0.6,
            'light_rain': 0.5,
            'heavy_rain': 0.3,
            'storm': 0.2
        }
        
        return light_factors.get(weather_type, 0.7)
    
    def _calculate_soil_factor(self, crop_props: CropProperties, tile: FarmTile) -> float:
        """Calculate soil suitability factor"""
        fertility = tile.get_soil_fertility()
        
        # pH factor
        soil_ph = tile.soil_nutrients.ph_level
        optimal_ph = (crop_props.preferred_ph_min + crop_props.preferred_ph_max) / 2
        ph_factor = 1.0 - abs(soil_ph - optimal_ph) / 2.0
        ph_factor = max(0.3, ph_factor)
        
        # Nutrient availability
        nutrients = tile.soil_nutrients
        n_factor = min(1.0, nutrients.nitrogen / 70.0)
        p_factor = min(1.0, nutrients.phosphorus / 60.0)
        k_factor = min(1.0, nutrients.potassium / 65.0)
        
        nutrient_factor = (n_factor + p_factor + k_factor) / 3.0
        
        return fertility * ph_factor * nutrient_factor
    
    def _advance_crop_stage(self, current_stage: CropStage) -> CropStage:
        """Advance crop to next growth stage"""
        stage_progression = {
            CropStage.PLANTED: CropStage.GERMINATED,
            CropStage.GERMINATED: CropStage.VEGETATIVE,
            CropStage.VEGETATIVE: CropStage.FLOWERING,
            CropStage.FLOWERING: CropStage.FRUIT_DEVELOPMENT,
            CropStage.FRUIT_DEVELOPMENT: CropStage.MATURE,
            CropStage.MATURE: CropStage.OVERRIPE,
            CropStage.OVERRIPE: CropStage.OVERRIPE  # Stay overripe
        }
        
        return stage_progression.get(current_stage, current_stage)
    
    def _update_yield_prediction(self, crop: PlantedCrop, crop_props: CropProperties, 
                                tile: FarmTile, growth_rate: float):
        """Update crop yield prediction"""
        base_yield = crop_props.base_yield_per_plant
        
        # Growth rate factor (better conditions = higher yield)
        yield_modifier = 0.5 + (growth_rate * 0.5)  # 0.5 to 1.0 range
        
        # Soil fertility factor
        soil_fertility = tile.get_soil_fertility()
        
        # Health factor
        health_factor = crop.health / 100.0
        
        # Stage factor (yield develops over time)
        stage_factors = {
            CropStage.PLANTED: 0.1,
            CropStage.GERMINATED: 0.2,
            CropStage.VEGETATIVE: 0.4,
            CropStage.FLOWERING: 0.6,
            CropStage.FRUIT_DEVELOPMENT: 0.9,
            CropStage.MATURE: 1.0,
            CropStage.OVERRIPE: 0.8  # Reduced yield if overripe
        }
        
        stage_factor = stage_factors.get(crop.current_stage, 0.1)
        
        # Calculate expected yield
        crop.expected_yield = (base_yield * yield_modifier * soil_fertility * 
                              health_factor * stage_factor)
        
        # Update quality rating
        crop.quality_rating = min(2.0, growth_rate * soil_fertility * health_factor)
    
    def _consume_soil_nutrients(self, crop_props: CropProperties, tile: FarmTile, delta_hours: float):
        """Consume soil nutrients based on crop demands"""
        if not tile.planted_crop:
            return
        
        # Daily consumption rates
        daily_factor = delta_hours / 24.0
        
        # Consumption based on crop stage
        stage_multipliers = {
            CropStage.PLANTED: 0.1,
            CropStage.GERMINATED: 0.3,
            CropStage.VEGETATIVE: 1.0,
            CropStage.FLOWERING: 0.8,
            CropStage.FRUIT_DEVELOPMENT: 1.2,
            CropStage.MATURE: 0.2,
            CropStage.OVERRIPE: 0.1
        }
        
        stage_multiplier = stage_multipliers.get(tile.planted_crop.current_stage, 0.5)
        
        # Consume nutrients
        nutrients = tile.soil_nutrients
        
        # Nitrogen consumption (unless soybeans which fix nitrogen)
        if crop_props.crop_type != CropType.SOYBEANS:
            n_consumption = crop_props.nitrogen_demand * daily_factor * stage_multiplier
            nutrients.nitrogen = max(0, nutrients.nitrogen - n_consumption)
        else:
            # Soybeans add nitrogen to soil
            n_addition = 0.5 * daily_factor * stage_multiplier
            nutrients.nitrogen = min(100, nutrients.nitrogen + n_addition)
        
        # Phosphorus consumption
        p_consumption = crop_props.phosphorus_demand * daily_factor * stage_multiplier
        nutrients.phosphorus = max(0, nutrients.phosphorus - p_consumption)
        
        # Potassium consumption
        k_consumption = crop_props.potassium_demand * daily_factor * stage_multiplier
        nutrients.potassium = max(0, nutrients.potassium - k_consumption)
        
        # Water consumption
        water_consumption = crop_props.water_requirement * daily_factor * stage_multiplier
        nutrients.water_content = max(0, nutrients.water_content - water_consumption)


class CropSystem:
    """Main crop and agricultural management system"""
    
    def __init__(self):
        # Core systems
        self.event_system = get_global_event_system()
        self.entity_manager = get_entity_manager()
        self.config_manager = get_configuration_manager()
        self.state_manager = get_state_manager()
        self.time_system = get_time_system()
        self.economy_system = get_economy_system()
        self.grid_system = get_grid_system()
        
        # Crop management
        self.farm_tiles: Dict[Tuple[int, int], FarmTile] = {}
        self.crop_counter = 0
        
        # Growth simulation
        self.growth_simulator = CropGrowthSimulator(self.config_manager)
        
        # Fertilizer inventory
        self.fertilizer_inventory: Dict[FertilizerType, float] = {
            fertilizer: 0.0 for fertilizer in FertilizerType
        }
        
        # Crop statistics
        self.total_crops_planted = 0
        self.total_crops_harvested = 0
        self.total_yield_harvested = 0.0
        
        self.logger = logging.getLogger('CropSystem')
        
        # Load configuration
        self._load_configuration()
        
        # Subscribe to events
        self._subscribe_to_events()
        
        # Initialize system
        self._initialize_system()
    
    def _load_configuration(self):
        """Load crop system configuration"""
        default_config = {
            'crops.growth_rate_modifier': 1.0,
            'crops.soil_degradation_rate': 1.0,
            'crops.fertilizer_effectiveness': 1.0,
            'crops.irrigation_cost_per_tile': 150.0,
            'crops.irrigation_daily_cost': 5.0
        }
        
        for key, value in default_config.items():
            if self.config_manager.get(key) is None:
                self.config_manager.set(key, value)
    
    def _subscribe_to_events(self):
        """Subscribe to relevant system events"""
        self.event_system.subscribe('hour_changed', self._on_hour_changed)
        self.event_system.subscribe('day_changed', self._on_day_changed)
        self.event_system.subscribe('season_changed', self._on_season_changed)
        self.event_system.subscribe('weather_changed', self._on_weather_changed)
    
    def _initialize_system(self):
        """Initialize crop system"""
        # Initialize farm grid (16x16)
        for x in range(16):
            for y in range(16):
                self.farm_tiles[(x, y)] = FarmTile(x=x, y=y)
        
        # Add starting fertilizer
        self.fertilizer_inventory[FertilizerType.COMPOST] = 100.0
        self.fertilizer_inventory[FertilizerType.NITROGEN] = 50.0
        
        self.logger.info("Crop system initialized with 256 farm tiles")
    
    def till_tile(self, x: int, y: int) -> Dict[str, Any]:
        """Till a farm tile to prepare for planting"""
        if (x, y) not in self.farm_tiles:
            return {'success': False, 'message': 'Invalid tile coordinates'}
        
        tile = self.farm_tiles[(x, y)]
        
        if tile.planted_crop is not None:
            return {'success': False, 'message': 'Tile has crops planted'}
        
        tile.is_tilled = True
        tile.last_tilled = self.time_system.get_current_time().total_minutes
        tile.needs_cultivation = False
        
        # Tilling improves soil structure slightly
        tile.soil_nutrients.compaction = max(0, tile.soil_nutrients.compaction - 10)
        
        self.logger.info(f"Tilled tile at ({x}, {y})")
        
        return {'success': True, 'message': f'Tile ({x}, {y}) tilled successfully'}
    
    def plant_crop(self, x: int, y: int, crop_type: CropType) -> Dict[str, Any]:
        """Plant a crop on a farm tile"""
        if (x, y) not in self.farm_tiles:
            return {'success': False, 'message': 'Invalid tile coordinates'}
        
        tile = self.farm_tiles[(x, y)]
        
        if not tile.can_plant():
            return {'success': False, 'message': 'Tile not ready for planting'}
        
        # Check if crop is suitable for current season
        current_season = self.time_system.get_current_season()
        if not self._is_suitable_planting_season(crop_type, current_season):
            return {'success': False, 'message': f'{crop_type.value} not suitable for {current_season.value}'}
        
        # Create planted crop
        self.crop_counter += 1
        crop_id = f"crop_{self.crop_counter:06d}"
        
        planted_crop = PlantedCrop(
            crop_id=crop_id,
            crop_type=crop_type,
            plant_date=self.time_system.get_current_time().total_minutes
        )
        
        tile.planted_crop = planted_crop
        tile.crop_history.append(crop_type)
        
        # Keep only last 5 crops in history
        if len(tile.crop_history) > 5:
            tile.crop_history.pop(0)
        
        self.total_crops_planted += 1
        
        # Emit planting event
        self.event_system.publish('crop_planted', {
            'crop_id': crop_id,
            'crop_type': crop_type.value,
            'location': (x, y),
            'plant_date': planted_crop.plant_date
        }, EventPriority.NORMAL, 'crop_system')
        
        self.logger.info(f"Planted {crop_type.value} at ({x}, {y})")
        
        return {
            'success': True,
            'crop_id': crop_id,
            'message': f'{crop_type.value} planted successfully'
        }
    
    def harvest_crop(self, x: int, y: int) -> Dict[str, Any]:
        """Harvest a mature crop"""
        if (x, y) not in self.farm_tiles:
            return {'success': False, 'message': 'Invalid tile coordinates'}
        
        tile = self.farm_tiles[(x, y)]
        
        if not tile.planted_crop:
            return {'success': False, 'message': 'No crop to harvest'}
        
        crop = tile.planted_crop
        
        if not crop.is_ready_for_harvest():
            return {'success': False, 'message': f'Crop not ready - currently {crop.current_stage.value}'}
        
        # Calculate harvest
        harvest_amount = crop.expected_yield
        quality = crop.quality_rating
        
        # Quality penalty for overripe crops
        if crop.current_stage == CropStage.OVERRIPE:
            quality *= 0.7
            harvest_amount *= 0.8
        
        # Calculate market value
        crop_props = self.growth_simulator.crop_properties[crop.crop_type]
        base_value = crop_props.base_market_value
        total_value = harvest_amount * base_value * quality
        
        # Add to economy
        transaction_id = self.economy_system.add_transaction(
            TransactionType.CROP_SALE,
            total_value,
            f"Harvested {crop.crop_type.value}",
            metadata={
                'crop_type': crop.crop_type.value,
                'harvest_amount': harvest_amount,
                'quality': quality,
                'location': (x, y)
            }
        )
        
        # Clear tile
        tile.planted_crop = None
        tile.needs_cultivation = True
        
        # Update statistics
        self.total_crops_harvested += 1
        self.total_yield_harvested += harvest_amount
        
        # Emit harvest event
        self.event_system.publish('crop_harvested', {
            'crop_type': crop.crop_type.value,
            'harvest_amount': harvest_amount,
            'quality': quality,
            'total_value': total_value,
            'location': (x, y),
            'transaction_id': transaction_id
        }, EventPriority.NORMAL, 'crop_system')
        
        self.logger.info(f"Harvested {harvest_amount:.1f} units of {crop.crop_type.value} for ${total_value:.2f}")
        
        return {
            'success': True,
            'harvest_amount': harvest_amount,
            'quality': quality,
            'total_value': total_value,
            'transaction_id': transaction_id
        }
    
    def apply_fertilizer(self, x: int, y: int, fertilizer_type: FertilizerType, amount: float) -> Dict[str, Any]:
        """Apply fertilizer to a farm tile"""
        if (x, y) not in self.farm_tiles:
            return {'success': False, 'message': 'Invalid tile coordinates'}
        
        if self.fertilizer_inventory[fertilizer_type] < amount:
            return {'success': False, 'message': 'Insufficient fertilizer'}
        
        tile = self.farm_tiles[(x, y)]
        
        # Apply fertilizer effects
        effectiveness = self.config_manager.get('crops.fertilizer_effectiveness', 1.0)
        effective_amount = amount * effectiveness
        
        if fertilizer_type == FertilizerType.NITROGEN:
            tile.soil_nutrients.nitrogen = min(100, tile.soil_nutrients.nitrogen + effective_amount)
        elif fertilizer_type == FertilizerType.PHOSPHORUS:
            tile.soil_nutrients.phosphorus = min(100, tile.soil_nutrients.phosphorus + effective_amount)
        elif fertilizer_type == FertilizerType.POTASSIUM:
            tile.soil_nutrients.potassium = min(100, tile.soil_nutrients.potassium + effective_amount)
        elif fertilizer_type == FertilizerType.COMPOST:
            # Compost adds all nutrients plus organic matter
            tile.soil_nutrients.nitrogen = min(100, tile.soil_nutrients.nitrogen + effective_amount * 0.4)
            tile.soil_nutrients.phosphorus = min(100, tile.soil_nutrients.phosphorus + effective_amount * 0.3)
            tile.soil_nutrients.potassium = min(100, tile.soil_nutrients.potassium + effective_amount * 0.3)
            tile.soil_nutrients.organic_matter = min(10, tile.soil_nutrients.organic_matter + effective_amount * 0.1)
        elif fertilizer_type == FertilizerType.LIME:
            # Lime raises pH
            tile.soil_nutrients.ph_level = min(9.0, tile.soil_nutrients.ph_level + effective_amount * 0.01)
        elif fertilizer_type == FertilizerType.SULFUR:
            # Sulfur lowers pH
            tile.soil_nutrients.ph_level = max(4.0, tile.soil_nutrients.ph_level - effective_amount * 0.01)
        
        # Deduct from inventory
        self.fertilizer_inventory[fertilizer_type] -= amount
        
        # Update crop if present
        if tile.planted_crop:
            tile.planted_crop.last_fertilized = self.time_system.get_current_time().total_minutes
            if fertilizer_type not in tile.planted_crop.fertilizer_applied:
                tile.planted_crop.fertilizer_applied[fertilizer_type] = 0
            tile.planted_crop.fertilizer_applied[fertilizer_type] += amount
        
        self.logger.info(f"Applied {amount} units of {fertilizer_type.value} to tile ({x}, {y})")
        
        return {
            'success': True,
            'fertilizer_type': fertilizer_type.value,
            'amount_applied': amount,
            'new_fertility': tile.get_soil_fertility()
        }
    
    def install_irrigation(self, x: int, y: int) -> Dict[str, Any]:
        """Install irrigation on a farm tile"""
        if (x, y) not in self.farm_tiles:
            return {'success': False, 'message': 'Invalid tile coordinates'}
        
        tile = self.farm_tiles[(x, y)]
        
        if tile.has_irrigation:
            return {'success': False, 'message': 'Tile already has irrigation'}
        
        # Check cost
        installation_cost = self.config_manager.get('crops.irrigation_cost_per_tile', 150.0)
        
        if self.economy_system.current_cash < installation_cost:
            return {'success': False, 'message': 'Insufficient funds'}
        
        # Install irrigation
        tile.has_irrigation = True
        tile.irrigation_efficiency = 0.8  # 80% efficiency
        
        # Pay for installation
        transaction_id = self.economy_system.add_transaction(
            TransactionType.EQUIPMENT_PURCHASE,
            -installation_cost,
            f"Irrigation installation at ({x}, {y})",
            metadata={'location': (x, y), 'equipment_type': 'irrigation'}
        )
        
        self.logger.info(f"Installed irrigation at ({x}, {y}) for ${installation_cost:.2f}")
        
        return {
            'success': True,
            'installation_cost': installation_cost,
            'transaction_id': transaction_id
        }
    
    def get_tile_info(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a farm tile"""
        if (x, y) not in self.farm_tiles:
            return None
        
        tile = self.farm_tiles[(x, y)]
        
        tile_info = {
            'coordinates': (x, y),
            'is_tilled': tile.is_tilled,
            'has_irrigation': tile.has_irrigation,
            'soil_type': tile.soil_type.value,
            'soil_fertility': tile.get_soil_fertility(),
            'soil_nutrients': {
                'nitrogen': tile.soil_nutrients.nitrogen,
                'phosphorus': tile.soil_nutrients.phosphorus,
                'potassium': tile.soil_nutrients.potassium,
                'ph_level': tile.soil_nutrients.ph_level,
                'organic_matter': tile.soil_nutrients.organic_matter,
                'water_content': tile.soil_nutrients.water_content,
                'compaction': tile.soil_nutrients.compaction
            },
            'crop_history': [crop.value for crop in tile.crop_history[-3:]]  # Last 3 crops
        }
        
        # Add crop information if present
        if tile.planted_crop:
            crop = tile.planted_crop
            tile_info['planted_crop'] = {
                'crop_id': crop.crop_id,
                'crop_type': crop.crop_type.value,
                'current_stage': crop.current_stage.value,
                'stage_progress': crop.stage_progress,
                'days_planted': crop.get_days_planted(self.time_system.get_current_time().total_minutes),
                'health': crop.health,
                'stress_level': crop.stress_level,
                'expected_yield': crop.expected_yield,
                'quality_rating': crop.quality_rating,
                'ready_for_harvest': crop.is_ready_for_harvest()
            }
        else:
            tile_info['planted_crop'] = None
        
        return tile_info
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get crop system summary"""
        # Count crops by stage
        stage_counts = {stage.value: 0 for stage in CropStage}
        total_tiles = len(self.farm_tiles)
        planted_tiles = 0
        tilled_tiles = 0
        irrigated_tiles = 0
        
        for tile in self.farm_tiles.values():
            if tile.is_tilled:
                tilled_tiles += 1
            if tile.has_irrigation:
                irrigated_tiles += 1
            
            if tile.planted_crop:
                planted_tiles += 1
                stage_counts[tile.planted_crop.current_stage.value] += 1
        
        # Calculate average soil fertility
        total_fertility = sum(tile.get_soil_fertility() for tile in self.farm_tiles.values())
        avg_fertility = total_fertility / total_tiles if total_tiles > 0 else 0
        
        return {
            'total_tiles': total_tiles,
            'tilled_tiles': tilled_tiles,
            'planted_tiles': planted_tiles,
            'irrigated_tiles': irrigated_tiles,
            'average_soil_fertility': avg_fertility,
            'crops_by_stage': stage_counts,
            'fertilizer_inventory': dict(self.fertilizer_inventory),
            'total_crops_planted': self.total_crops_planted,
            'total_crops_harvested': self.total_crops_harvested,
            'total_yield_harvested': self.total_yield_harvested
        }
    
    def _is_suitable_planting_season(self, crop_type: CropType, season: Season) -> bool:
        """Check if crop is suitable for current season"""
        # Define planting seasons for each crop
        planting_seasons = {
            CropType.CORN: [Season.SPRING, Season.SUMMER],
            CropType.WHEAT: [Season.FALL, Season.WINTER, Season.SPRING],
            CropType.TOMATOES: [Season.SPRING, Season.SUMMER],
            CropType.LETTUCE: [Season.SPRING, Season.FALL, Season.WINTER],
            CropType.SOYBEANS: [Season.SPRING, Season.SUMMER],
            CropType.POTATOES: [Season.SPRING, Season.FALL],
            CropType.CARROTS: [Season.SPRING, Season.FALL, Season.WINTER],
            CropType.ONIONS: [Season.SPRING, Season.FALL]
        }
        
        return season in planting_seasons.get(crop_type, [])
    
    def _on_hour_changed(self, event_data: Dict[str, Any]):
        """Handle hourly crop updates"""
        # Get current weather conditions
        weather = self.time_system.get_current_weather()
        weather_conditions = {
            'temperature': weather.temperature_c,
            'precipitation': getattr(weather, 'precipitation', 0),
            'weather_type': weather.weather_type.value
        }
        
        # Update all planted crops
        for tile in self.farm_tiles.values():
            if tile.planted_crop:
                growth_result = self.growth_simulator.simulate_growth(
                    tile.planted_crop, 
                    tile, 
                    weather_conditions, 
                    1.0  # 1 hour
                )
                
                # Emit growth events if significant changes
                if growth_result.get('stage_changed'):
                    self.event_system.publish('crop_stage_changed', {
                        'crop_id': tile.planted_crop.crop_id,
                        'new_stage': growth_result['new_stage'],
                        'location': (tile.x, tile.y)
                    }, EventPriority.LOW, 'crop_system')
    
    def _on_day_changed(self, event_data: Dict[str, Any]):
        """Handle daily crop management"""
        # Natural soil moisture recovery from groundwater
        for tile in self.farm_tiles.values():
            tile.soil_nutrients.water_content = min(100, tile.soil_nutrients.water_content + 2.0)
            
            # Slow nutrient regeneration in fallow fields
            if not tile.planted_crop:
                tile.soil_nutrients.nitrogen = min(100, tile.soil_nutrients.nitrogen + 0.5)
                tile.soil_nutrients.organic_matter = min(10, tile.soil_nutrients.organic_matter + 0.01)
    
    def _on_season_changed(self, event_data: Dict[str, Any]):
        """Handle seasonal changes"""
        new_season = Season(event_data['new_season'])
        self.logger.info(f"Season changed to {new_season.value} - adjusting crop systems")
        
        # Generate seasonal planting recommendations
        recommendations = self._generate_planting_recommendations(new_season)
        
        self.event_system.publish('seasonal_planting_recommendations', {
            'season': new_season.value,
            'recommendations': recommendations
        }, EventPriority.NORMAL, 'crop_system')
    
    def _on_weather_changed(self, event_data: Dict[str, Any]):
        """Handle weather changes"""
        weather_type = event_data.get('weather_type')
        
        # Apply weather effects to all tiles
        if weather_type in ['light_rain', 'heavy_rain']:
            # Rain adds soil moisture
            moisture_bonus = 15 if weather_type == 'heavy_rain' else 8
            
            for tile in self.farm_tiles.values():
                tile.soil_nutrients.water_content = min(100, 
                    tile.soil_nutrients.water_content + moisture_bonus)
    
    def _generate_planting_recommendations(self, season: Season) -> List[Dict[str, Any]]:
        """Generate crop planting recommendations for season"""
        recommendations = []
        
        for crop_type in CropType:
            if self._is_suitable_planting_season(crop_type, season):
                crop_props = self.growth_simulator.crop_properties[crop_type]
                
                recommendations.append({
                    'crop_type': crop_type.value,
                    'suitability': 'excellent' if season in [Season.SPRING, Season.SUMMER] else 'good',
                    'maturity_days': crop_props.days_to_maturity,
                    'expected_value': crop_props.base_market_value,
                    'water_requirement': crop_props.water_requirement
                })
        
        return recommendations


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

# Convenience functions
def plant_crop(x: int, y: int, crop_type: CropType) -> Dict[str, Any]:
    """Plant a crop at coordinates"""
    return get_crop_system().plant_crop(x, y, crop_type)

def harvest_crop(x: int, y: int) -> Dict[str, Any]:
    """Harvest crop at coordinates"""
    return get_crop_system().harvest_crop(x, y)

def get_tile_info(x: int, y: int) -> Optional[Dict[str, Any]]:
    """Get tile information"""
    return get_crop_system().get_tile_info(x, y)

def get_crop_summary() -> Dict[str, Any]:
    """Get crop system summary"""
    return get_crop_system().get_system_summary()