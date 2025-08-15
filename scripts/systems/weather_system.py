"""
Weather System - Realistic Weather Patterns and Climate Impact for AgriFun Agricultural Simulation

This system provides comprehensive weather simulation with realistic patterns, seasonal variations,
and direct impacts on agricultural operations. Integrates with crop growth, soil health, and
time management systems to create an authentic farming experience.

Key Features:
- Realistic weather pattern simulation with regional climate models
- Seasonal weather variations with authentic agricultural timing
- Weather event system (storms, droughts, heat waves, frost)
- Multi-day weather forecasting for planning decisions
- Direct weather impacts on crop growth and soil conditions
- Climate change simulation and adaptation strategies

Weather Components:
- Temperature: Daily highs/lows with realistic seasonal curves
- Precipitation: Rain patterns, intensity, and accumulation
- Humidity: Relative humidity affecting disease pressure
- Wind: Speed and direction affecting crop stress and spraying
- Solar Radiation: Light intensity affecting photosynthesis
- Atmospheric Pressure: Weather system prediction

Agricultural Integration:
- Crop Growth: Temperature and moisture effects on growth rates
- Soil Health: Precipitation impacts on soil moisture and compaction
- Equipment Operations: Weather limitations on field work
- Disease Pressure: Humidity and temperature disease modeling
- Irrigation Management: Precipitation-based irrigation decisions

Educational Value:
- Real meteorology and climate science principles
- Weather pattern recognition and forecasting skills
- Agricultural decision-making under weather uncertainty
- Climate adaptation and risk management strategies
- Understanding of weather-agriculture relationships

Usage Example:
    # Initialize weather system
    weather_system = WeatherSystem()
    await weather_system.initialize()
    
    # Get current weather
    current_weather = weather_system.get_current_weather()
    
    # Get forecast
    forecast = weather_system.get_weather_forecast(days=7)
    
    # Check agricultural suitability
    field_work_suitable = weather_system.is_suitable_for_field_work()
    spray_conditions = weather_system.get_spray_conditions()
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import logging
from datetime import datetime, timedelta
import json
import math
import random
import statistics

# Import Phase 1 systems
from scripts.core.advanced_event_system import EventSystem, get_event_system
from scripts.core.time_management import TimeManager, get_time_manager, Season
from scripts.core.advanced_config_system import ConfigurationManager, get_config_manager
from scripts.core.content_registry import ContentRegistry, get_content_registry
from scripts.core.entity_component_system import System

# Configure logging for weather system
logger = logging.getLogger(__name__)

class WeatherType(Enum):
    """Primary weather conditions"""
    CLEAR = "clear"                 # Clear skies, minimal clouds
    PARTLY_CLOUDY = "partly_cloudy" # Partial cloud cover
    CLOUDY = "cloudy"              # Overcast conditions
    LIGHT_RAIN = "light_rain"      # Light precipitation
    RAIN = "rain"                  # Moderate precipitation
    HEAVY_RAIN = "heavy_rain"      # Heavy precipitation
    THUNDERSTORM = "thunderstorm"  # Storms with lightning
    DRIZZLE = "drizzle"           # Very light precipitation
    SNOW = "snow"                  # Snow precipitation (winter)
    SLEET = "sleet"               # Mixed precipitation
    FOG = "fog"                   # Low visibility conditions
    HAIL = "hail"                 # Hailstorm events

class WeatherSeverity(Enum):
    """Weather event severity levels"""
    NORMAL = "normal"              # Typical weather conditions
    ADVISORY = "advisory"          # Watch conditions
    WARNING = "warning"            # Significant weather
    SEVERE = "severe"             # Dangerous conditions
    EXTREME = "extreme"           # Life-threatening weather

class ClimateZone(Enum):
    """Agricultural climate classifications"""
    TEMPERATE = "temperate"        # Moderate climate, four seasons
    CONTINENTAL = "continental"    # Large temperature variations
    SUBTROPICAL = "subtropical"    # Warm, humid conditions
    ARID = "arid"                 # Dry, desert-like conditions
    MEDITERRANEAN = "mediterranean" # Dry summers, wet winters
    TROPICAL = "tropical"         # Hot, humid year-round

@dataclass
class WeatherCondition:
    """Current weather state"""
    weather_type: WeatherType      # Primary weather condition
    temperature: float             # Current temperature (Celsius)
    temperature_high: float        # Daily high temperature
    temperature_low: float         # Daily low temperature
    humidity: float               # Relative humidity (0.0-1.0)
    precipitation_rate: float      # mm/hour precipitation
    precipitation_total: float     # Total daily precipitation
    wind_speed: float             # Wind speed (m/s)
    wind_direction: float         # Wind direction (degrees)
    atmospheric_pressure: float    # Pressure (hPa)
    solar_radiation: float        # Solar radiation (MJ/m²/day)
    cloud_cover: float           # Cloud coverage (0.0-1.0)
    visibility: float            # Visibility (km)
    uv_index: float             # UV index (0-11+)
    
    # Agricultural factors
    growing_degree_days: float    # Accumulated heat units
    chill_hours: float           # Hours below 7°C (for fruit trees)
    heat_stress_index: float     # Heat stress on crops
    drought_index: float         # Drought severity measure
    
    def get_comfort_description(self) -> str:
        """Get human-readable comfort description"""
        if self.temperature < 0:
            return "Freezing"
        elif self.temperature < 10:
            return "Cold"
        elif self.temperature < 20:
            return "Cool"
        elif self.temperature < 25:
            return "Comfortable"
        elif self.temperature < 30:
            return "Warm"
        elif self.temperature < 35:
            return "Hot"
        else:
            return "Extremely Hot"
    
    def is_suitable_for_field_work(self) -> bool:
        """Check if conditions are suitable for field operations"""
        # Too wet, windy, or extreme temperatures
        if self.precipitation_rate > 1.0:  # More than 1mm/hour
            return False
        if self.wind_speed > 15.0:  # More than 15 m/s
            return False
        if self.temperature < -5 or self.temperature > 40:  # Extreme temperatures
            return False
        return True
    
    def get_disease_pressure_risk(self) -> float:
        """Calculate disease pressure risk (0.0-1.0)"""
        # High humidity and moderate temperatures increase disease risk
        humidity_factor = self.humidity  # Higher humidity = higher risk
        
        # Temperature factor - disease risk peaks around 20-25°C
        if 15 <= self.temperature <= 30:
            temp_factor = 1.0 - abs(self.temperature - 22.5) / 15.0
        else:
            temp_factor = 0.2
        
        # Moisture factor - wet conditions increase risk
        moisture_factor = min(1.0, self.precipitation_total / 10.0)  # Max at 10mm
        
        return (humidity_factor * 0.4 + temp_factor * 0.4 + moisture_factor * 0.2)

@dataclass
class WeatherEvent:
    """Significant weather event"""
    event_id: str                 # Unique event identifier
    event_type: str               # Type of weather event
    severity: WeatherSeverity     # Event severity level
    start_time: datetime          # Event start time
    end_time: datetime           # Expected end time
    description: str             # Human-readable description
    
    # Impact factors
    temperature_modifier: float   # Temperature change during event
    precipitation_modifier: float # Precipitation change during event
    wind_modifier: float         # Wind speed change during event
    
    # Agricultural impacts
    crop_damage_potential: float  # Potential crop damage (0.0-1.0)
    soil_impact: float           # Impact on soil conditions
    equipment_restrictions: List[str]  # Equipment that can't operate
    
    # Advisory information
    advisory_message: str        # Advisory text for farmers
    recommended_actions: List[str] # Recommended protective actions

@dataclass
class ClimateModel:
    """Climate model for region"""
    zone: ClimateZone            # Climate zone classification
    
    # Temperature parameters
    avg_temp_by_season: Dict[Season, float]  # Average temps by season
    temp_variation: float        # Daily temperature variation
    extreme_temp_frequency: float # Frequency of extreme temperatures
    
    # Precipitation parameters
    annual_precipitation: float   # Total annual precipitation (mm)
    wet_season: Season          # Primary wet season
    dry_season: Season          # Primary dry season
    precipitation_variability: float  # Year-to-year variation
    
    # Weather pattern parameters
    storm_frequency: float       # Frequency of storm systems
    drought_frequency: float     # Frequency of drought conditions
    frost_frequency: float       # Frequency of frost events
    
    # Seasonal transitions
    season_transition_days: int  # Days for seasonal transitions
    weather_persistence: float  # Tendency for weather to persist

@dataclass
class WeatherForecast:
    """Multi-day weather forecast"""
    forecast_date: datetime      # Date forecast was generated
    forecast_days: int          # Number of days in forecast
    accuracy: float             # Forecast accuracy (decreases over time)
    
    # Daily forecasts
    daily_conditions: List[WeatherCondition]  # Daily weather conditions
    daily_confidence: List[float]  # Confidence level for each day
    
    # Extended forecast
    weekly_trends: Dict[str, str]  # Weekly weather trends
    monthly_outlook: Dict[str, str]  # Monthly climate outlook
    
    # Agricultural forecast
    planting_recommendations: List[str]  # Planting timing advice
    harvest_windows: List[Tuple[datetime, datetime]]  # Optimal harvest windows
    irrigation_schedule: List[Tuple[datetime, float]]  # Suggested irrigation
    
    def get_forecast_for_date(self, date: datetime) -> Optional[WeatherCondition]:
        """Get forecast for specific date"""
        days_ahead = (date.date() - self.forecast_date.date()).days
        if 0 <= days_ahead < len(self.daily_conditions):
            return self.daily_conditions[days_ahead]
        return None
    
    def get_precipitation_total(self, start_date: datetime, days: int) -> float:
        """Get total precipitation forecast for period"""
        total = 0.0
        for i in range(days):
            forecast_date = start_date + timedelta(days=i)
            condition = self.get_forecast_for_date(forecast_date)
            if condition:
                total += condition.precipitation_total
        return total

class WeatherSystem(System):
    """
    Weather System - Comprehensive weather simulation and forecasting
    
    This system provides realistic weather patterns with agricultural impacts,
    seasonal variations, and educational weather science content.
    """
    
    def __init__(self):
        """Initialize the Weather System"""
        super().__init__()
        self.system_name = "weather_system"
        
        # Core system references
        self.event_system: Optional[EventSystem] = None
        self.time_manager: Optional[TimeManager] = None
        self.config_manager: Optional[ConfigurationManager] = None
        self.content_registry: Optional[ContentRegistry] = None
        
        # Weather state management
        self.current_weather: Optional[WeatherCondition] = None
        self.weather_history: List[WeatherCondition] = []
        self.active_events: List[WeatherEvent] = []
        self.current_forecast: Optional[WeatherForecast] = None
        
        # Climate configuration
        self.climate_model: Optional[ClimateModel] = None
        self.climate_zone: ClimateZone = ClimateZone.TEMPERATE
        
        # Weather generation parameters
        self.update_frequency = 1.0  # Update every game hour
        self.last_update_time = 0.0
        self.weather_seed = random.randint(1, 1000000)  # For reproducible weather
        
        # Forecast parameters
        self.forecast_accuracy_decay = 0.05  # Accuracy loss per day
        self.forecast_update_hours = 6  # Update forecast every 6 hours
        self.max_forecast_days = 14  # Maximum forecast length
        
        # Weather event tracking
        self.event_probability_factors: Dict[str, float] = {}
        self.seasonal_modifiers: Dict[Season, Dict[str, float]] = {}
        
        # Performance optimization
        self.weather_cache: Dict[str, Any] = {}
        self.cache_timeout = 3600  # Cache timeout in seconds
        
        logger.info("Weather System initialized")
    
    def initialize(self) -> bool:
        """Initialize the weather system with required dependencies"""
        try:
            # Get system references
            self.event_system = get_event_system()
            self.time_manager = get_time_manager()
            self.config_manager = get_config_manager()
            self.content_registry = get_content_registry()
            
            # Load climate model
            self._load_climate_model()
            
            # Initialize current weather
            self._initialize_current_weather()
            
            # Generate initial forecast
            self._generate_forecast()
            
            # Subscribe to relevant events
            self._subscribe_to_events()
            
            # Load configuration
            self._load_configuration()
            
            logger.info("Weather System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Weather System: {e}")
            return False
    
    def _load_climate_model(self):
        """Load climate model from content registry"""
        try:
            # Try to load climate model from content
            climate_data = self.content_registry.get_content("climate", {})
            
            if climate_data and "temperate" in climate_data:
                model_data = climate_data["temperate"]
                
                self.climate_model = ClimateModel(
                    zone=ClimateZone.TEMPERATE,
                    avg_temp_by_season={
                        Season.SPRING: model_data.get("spring_temp", 15.0),
                        Season.SUMMER: model_data.get("summer_temp", 25.0),
                        Season.FALL: model_data.get("fall_temp", 10.0),
                        Season.WINTER: model_data.get("winter_temp", 0.0)
                    },
                    temp_variation=model_data.get("temp_variation", 10.0),
                    extreme_temp_frequency=model_data.get("extreme_temp_freq", 0.1),
                    annual_precipitation=model_data.get("annual_precip", 800.0),
                    wet_season=Season.SPRING,
                    dry_season=Season.SUMMER,
                    precipitation_variability=model_data.get("precip_variability", 0.3),
                    storm_frequency=model_data.get("storm_frequency", 0.2),
                    drought_frequency=model_data.get("drought_frequency", 0.1),
                    frost_frequency=model_data.get("frost_frequency", 0.3),
                    season_transition_days=model_data.get("transition_days", 30),
                    weather_persistence=model_data.get("persistence", 0.7)
                )
            else:
                # Create default temperate climate model
                self._create_default_climate_model()
            
            logger.info(f"Loaded climate model: {self.climate_model.zone.value}")
            
        except Exception as e:
            logger.error(f"Failed to load climate model: {e}")
            self._create_default_climate_model()
    
    def _create_default_climate_model(self):
        """Create default temperate climate model"""
        self.climate_model = ClimateModel(
            zone=ClimateZone.TEMPERATE,
            avg_temp_by_season={
                Season.SPRING: 15.0,  # 15°C average in spring
                Season.SUMMER: 25.0,  # 25°C average in summer
                Season.FALL: 10.0,    # 10°C average in fall
                Season.WINTER: 0.0    # 0°C average in winter
            },
            temp_variation=12.0,      # 12°C daily variation
            extreme_temp_frequency=0.05,  # 5% chance of extreme temperatures
            annual_precipitation=800.0,   # 800mm annual precipitation
            wet_season=Season.SPRING,     # Spring is wettest
            dry_season=Season.SUMMER,     # Summer is driest
            precipitation_variability=0.4, # 40% year-to-year variation
            storm_frequency=0.15,         # 15% chance of storms
            drought_frequency=0.08,       # 8% chance of drought
            frost_frequency=0.25,         # 25% chance of frost in winter/spring
            season_transition_days=21,    # 3 weeks for seasonal transitions
            weather_persistence=0.75      # 75% chance weather pattern continues
        )
        logger.info("Created default temperate climate model")
    
    def _initialize_current_weather(self):
        """Initialize current weather based on season and climate"""
        if not self.climate_model or not self.time_manager:
            return
        
        current_time = self.time_manager.get_current_time()
        current_season = self.time_manager.get_current_season()
        
        # Get base temperature for season
        base_temp = self.climate_model.avg_temp_by_season.get(current_season, 15.0)
        
        # Add random variation
        temp_variation = random.gauss(0, self.climate_model.temp_variation / 3)
        current_temp = base_temp + temp_variation
        
        # Calculate daily high/low
        daily_range = self.climate_model.temp_variation
        temp_high = current_temp + daily_range / 2
        temp_low = current_temp - daily_range / 2
        
        # Generate other weather parameters
        self.current_weather = WeatherCondition(
            weather_type=WeatherType.PARTLY_CLOUDY,
            temperature=current_temp,
            temperature_high=temp_high,
            temperature_low=temp_low,
            humidity=random.uniform(0.4, 0.8),
            precipitation_rate=0.0,
            precipitation_total=0.0,
            wind_speed=random.uniform(2.0, 8.0),
            wind_direction=random.uniform(0, 360),
            atmospheric_pressure=1013.25 + random.gauss(0, 10),
            solar_radiation=self._calculate_solar_radiation(current_season),
            cloud_cover=random.uniform(0.2, 0.6),
            visibility=random.uniform(15.0, 30.0),
            uv_index=self._calculate_uv_index(current_season),
            growing_degree_days=max(0, current_temp - 10),  # Base temperature 10°C
            chill_hours=1.0 if current_temp < 7 else 0.0,
            heat_stress_index=max(0, current_temp - 30) / 10.0,
            drought_index=0.0  # Will be calculated based on precipitation history
        )
        
        logger.info(f"Initialized current weather: {current_temp:.1f}°C, {self.current_weather.weather_type.value}")
    
    def _calculate_solar_radiation(self, season: Season) -> float:
        """Calculate solar radiation based on season"""
        base_radiation = {
            Season.SUMMER: 25.0,   # High summer radiation
            Season.SPRING: 20.0,   # Moderate spring radiation
            Season.FALL: 15.0,     # Lower fall radiation
            Season.WINTER: 8.0     # Low winter radiation
        }
        
        base = base_radiation.get(season, 15.0)
        # Add cloud cover effect
        if self.current_weather:
            cloud_factor = 1.0 - (self.current_weather.cloud_cover * 0.6)
            return base * cloud_factor
        
        return base
    
    def _calculate_uv_index(self, season: Season) -> float:
        """Calculate UV index based on season and conditions"""
        base_uv = {
            Season.SUMMER: 8.0,    # High summer UV
            Season.SPRING: 6.0,    # Moderate spring UV
            Season.FALL: 4.0,      # Lower fall UV
            Season.WINTER: 2.0     # Low winter UV
        }
        
        base = base_uv.get(season, 5.0)
        
        # Adjust for cloud cover
        if self.current_weather:
            cloud_factor = 1.0 - (self.current_weather.cloud_cover * 0.4)
            return max(0, base * cloud_factor)
        
        return base
    
    def _subscribe_to_events(self):
        """Subscribe to relevant system events"""
        if self.event_system:
            # Time-based events
            self.event_system.subscribe("time_advanced", self._on_time_advanced)
            self.event_system.subscribe("day_changed", self._on_day_changed)
            self.event_system.subscribe("season_changed", self._on_season_changed)
            
            # Request events
            self.event_system.subscribe("weather_forecast_requested", self._on_forecast_requested)
            self.event_system.subscribe("weather_event_check", self._on_weather_event_check)
    
    def _load_configuration(self):
        """Load system configuration parameters"""
        if self.config_manager:
            config = self.config_manager.get_config("weather_system", {})
            
            self.update_frequency = config.get("update_frequency", 1.0)
            self.forecast_update_hours = config.get("forecast_update_hours", 6)
            self.max_forecast_days = config.get("max_forecast_days", 14)
            self.weather_seed = config.get("weather_seed", self.weather_seed)
    
    def update(self, delta_time: float):
        """Update weather conditions and forecasts"""
        try:
            # Check if it's time for update
            current_time = self.time_manager.get_game_time_hours() if self.time_manager else 0.0
            if current_time - self.last_update_time < self.update_frequency:
                return
            
            self.last_update_time = current_time
            
            # Update current weather
            self._update_current_weather()
            
            # Check for weather events
            self._check_weather_events()
            
            # Update active weather events
            self._update_weather_events()
            
            # Update forecast if needed
            if current_time % self.forecast_update_hours < self.update_frequency:
                self._generate_forecast()
            
            # Clean old weather history
            self._cleanup_weather_history()
            
        except Exception as e:
            logger.error(f"Error updating weather: {e}")
    
    def _update_current_weather(self):
        """Update current weather conditions"""
        if not self.current_weather or not self.time_manager:
            return
        
        current_time = self.time_manager.get_current_time()
        current_season = self.time_manager.get_current_season()
        
        # Store previous weather
        previous_weather = self.current_weather
        
        # Weather persistence - tendency for current conditions to continue
        persistence_factor = self.climate_model.weather_persistence
        change_factor = 1.0 - persistence_factor
        
        # Calculate new temperature
        seasonal_temp = self.climate_model.avg_temp_by_season.get(current_season, 15.0)
        
        # Temperature evolution with persistence
        temp_target = seasonal_temp + random.gauss(0, self.climate_model.temp_variation / 4)
        new_temp = (previous_weather.temperature * persistence_factor + 
                   temp_target * change_factor)
        
        # Update daily high/low based on time of day
        hour = current_time.hour
        daily_range = self.climate_model.temp_variation
        
        # Temperature curve throughout the day (peak at 2 PM, minimum at 6 AM)
        temp_curve = math.sin((hour - 6) * math.pi / 12)
        daily_temp = new_temp + temp_curve * (daily_range / 2)
        
        # Update weather type based on conditions
        new_weather_type = self._determine_weather_type(previous_weather)
        
        # Calculate precipitation
        precipitation_rate, precipitation_total = self._calculate_precipitation(
            new_weather_type, current_season
        )
        
        # Update humidity based on weather type and season
        humidity = self._calculate_humidity(new_weather_type, current_season)
        
        # Update wind conditions
        wind_speed, wind_direction = self._calculate_wind(
            previous_weather, new_weather_type
        )
        
        # Create updated weather condition
        self.current_weather = WeatherCondition(
            weather_type=new_weather_type,
            temperature=daily_temp,
            temperature_high=new_temp + daily_range / 2,
            temperature_low=new_temp - daily_range / 2,
            humidity=humidity,
            precipitation_rate=precipitation_rate,
            precipitation_total=precipitation_total,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            atmospheric_pressure=self._calculate_pressure(previous_weather),
            solar_radiation=self._calculate_solar_radiation(current_season),
            cloud_cover=self._calculate_cloud_cover(new_weather_type),
            visibility=self._calculate_visibility(new_weather_type),
            uv_index=self._calculate_uv_index(current_season),
            growing_degree_days=max(0, daily_temp - 10),
            chill_hours=1.0 if daily_temp < 7 else 0.0,
            heat_stress_index=max(0, daily_temp - 30) / 10.0,
            drought_index=self._calculate_drought_index()
        )
        
        # Add to weather history
        self.weather_history.append(self.current_weather)
        
        # Publish weather update event
        if self.event_system:
            self.event_system.publish("weather_updated", {
                "weather": self.current_weather,
                "previous_weather": previous_weather,
                "season": current_season.value
            })
    
    def _determine_weather_type(self, previous_weather: WeatherCondition) -> WeatherType:
        """Determine new weather type based on current conditions"""
        current_season = self.time_manager.get_current_season() if self.time_manager else Season.SPRING
        
        # Weather transition probabilities
        transition_probs = {
            WeatherType.CLEAR: {
                WeatherType.CLEAR: 0.7,
                WeatherType.PARTLY_CLOUDY: 0.2,
                WeatherType.CLOUDY: 0.1
            },
            WeatherType.PARTLY_CLOUDY: {
                WeatherType.CLEAR: 0.3,
                WeatherType.PARTLY_CLOUDY: 0.4,
                WeatherType.CLOUDY: 0.2,
                WeatherType.LIGHT_RAIN: 0.1
            },
            WeatherType.CLOUDY: {
                WeatherType.PARTLY_CLOUDY: 0.3,
                WeatherType.CLOUDY: 0.4,
                WeatherType.LIGHT_RAIN: 0.2,
                WeatherType.RAIN: 0.1
            },
            WeatherType.LIGHT_RAIN: {
                WeatherType.CLOUDY: 0.3,
                WeatherType.LIGHT_RAIN: 0.4,
                WeatherType.RAIN: 0.2,
                WeatherType.DRIZZLE: 0.1
            },
            WeatherType.RAIN: {
                WeatherType.LIGHT_RAIN: 0.3,
                WeatherType.RAIN: 0.3,
                WeatherType.HEAVY_RAIN: 0.2,
                WeatherType.CLOUDY: 0.2
            }
        }
        
        # Get transition probabilities for current weather
        current_type = previous_weather.weather_type
        probs = transition_probs.get(current_type, {WeatherType.PARTLY_CLOUDY: 1.0})
        
        # Seasonal modifications
        if current_season == Season.SUMMER:
            # More clear weather in summer
            if WeatherType.CLEAR in probs:
                probs[WeatherType.CLEAR] *= 1.3
        elif current_season == Season.WINTER:
            # More cloudy/rainy weather in winter
            if WeatherType.CLOUDY in probs:
                probs[WeatherType.CLOUDY] *= 1.2
        
        # Choose new weather type based on probabilities
        weather_types = list(probs.keys())
        weights = list(probs.values())
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
            return random.choices(weather_types, weights=weights)[0]
        
        return WeatherType.PARTLY_CLOUDY
    
    def _calculate_precipitation(self, weather_type: WeatherType, 
                               season: Season) -> Tuple[float, float]:
        """Calculate precipitation rate and total"""
        base_rates = {
            WeatherType.CLEAR: 0.0,
            WeatherType.PARTLY_CLOUDY: 0.0,
            WeatherType.CLOUDY: 0.0,
            WeatherType.DRIZZLE: 0.2,
            WeatherType.LIGHT_RAIN: 1.0,
            WeatherType.RAIN: 3.0,
            WeatherType.HEAVY_RAIN: 8.0,
            WeatherType.THUNDERSTORM: 12.0
        }
        
        base_rate = base_rates.get(weather_type, 0.0)
        
        # Seasonal modifications
        seasonal_factors = {
            Season.SPRING: 1.2,  # More rain in spring
            Season.SUMMER: 0.8,  # Less rain in summer
            Season.FALL: 1.1,    # Moderate rain in fall
            Season.WINTER: 0.9   # Moderate rain in winter
        }
        
        seasonal_factor = seasonal_factors.get(season, 1.0)
        precipitation_rate = base_rate * seasonal_factor
        
        # Daily total (assuming hourly rate)
        precipitation_total = precipitation_rate * random.uniform(0.5, 4.0)
        
        return precipitation_rate, precipitation_total
    
    def _calculate_humidity(self, weather_type: WeatherType, season: Season) -> float:
        """Calculate relative humidity"""
        base_humidity = {
            WeatherType.CLEAR: 0.45,
            WeatherType.PARTLY_CLOUDY: 0.55,
            WeatherType.CLOUDY: 0.65,
            WeatherType.DRIZZLE: 0.85,
            WeatherType.LIGHT_RAIN: 0.85,
            WeatherType.RAIN: 0.90,
            WeatherType.HEAVY_RAIN: 0.95,
            WeatherType.THUNDERSTORM: 0.95
        }
        
        base = base_humidity.get(weather_type, 0.6)
        
        # Seasonal adjustments
        seasonal_adjustments = {
            Season.SPRING: 0.05,   # Slightly higher humidity
            Season.SUMMER: -0.1,   # Lower humidity
            Season.FALL: 0.0,      # Neutral
            Season.WINTER: 0.05    # Slightly higher humidity
        }
        
        adjustment = seasonal_adjustments.get(season, 0.0)
        humidity = base + adjustment + random.gauss(0, 0.05)
        
        return max(0.2, min(1.0, humidity))
    
    def _calculate_wind(self, previous_weather: WeatherCondition, 
                       weather_type: WeatherType) -> Tuple[float, float]:
        """Calculate wind speed and direction"""
        # Base wind speeds by weather type
        base_winds = {
            WeatherType.CLEAR: 3.0,
            WeatherType.PARTLY_CLOUDY: 4.0,
            WeatherType.CLOUDY: 5.0,
            WeatherType.LIGHT_RAIN: 6.0,
            WeatherType.RAIN: 8.0,
            WeatherType.HEAVY_RAIN: 12.0,
            WeatherType.THUNDERSTORM: 15.0
        }
        
        base_wind = base_winds.get(weather_type, 5.0)
        
        # Add persistence and variation
        persistence = 0.6
        new_wind = (previous_weather.wind_speed * persistence + 
                   base_wind * (1 - persistence))
        new_wind += random.gauss(0, 2.0)  # Add variation
        wind_speed = max(0.5, min(25.0, new_wind))
        
        # Wind direction - tends to persist but can shift
        direction_change = random.gauss(0, 20)  # Up to 20 degree changes
        wind_direction = (previous_weather.wind_direction + direction_change) % 360
        
        return wind_speed, wind_direction
    
    def _calculate_pressure(self, previous_weather: WeatherCondition) -> float:
        """Calculate atmospheric pressure"""
        # Pressure tends to change slowly
        persistence = 0.9
        pressure_change = random.gauss(0, 2.0)  # Small pressure changes
        
        new_pressure = previous_weather.atmospheric_pressure * persistence + pressure_change
        return max(990.0, min(1030.0, new_pressure))  # Reasonable pressure range
    
    def _calculate_cloud_cover(self, weather_type: WeatherType) -> float:
        """Calculate cloud coverage"""
        cloud_covers = {
            WeatherType.CLEAR: 0.1,
            WeatherType.PARTLY_CLOUDY: 0.4,
            WeatherType.CLOUDY: 0.8,
            WeatherType.DRIZZLE: 0.9,
            WeatherType.LIGHT_RAIN: 0.85,
            WeatherType.RAIN: 0.9,
            WeatherType.HEAVY_RAIN: 0.95,
            WeatherType.THUNDERSTORM: 0.95
        }
        
        base_cover = cloud_covers.get(weather_type, 0.5)
        variation = random.gauss(0, 0.1)
        
        return max(0.0, min(1.0, base_cover + variation))
    
    def _calculate_visibility(self, weather_type: WeatherType) -> float:
        """Calculate visibility in kilometers"""
        visibilities = {
            WeatherType.CLEAR: 25.0,
            WeatherType.PARTLY_CLOUDY: 20.0,
            WeatherType.CLOUDY: 15.0,
            WeatherType.DRIZZLE: 8.0,
            WeatherType.LIGHT_RAIN: 10.0,
            WeatherType.RAIN: 6.0,
            WeatherType.HEAVY_RAIN: 3.0,
            WeatherType.THUNDERSTORM: 2.0,
            WeatherType.FOG: 0.2
        }
        
        base_visibility = visibilities.get(weather_type, 15.0)
        variation = random.gauss(0, base_visibility * 0.1)
        
        return max(0.1, base_visibility + variation)
    
    def _calculate_drought_index(self) -> float:
        """Calculate drought index based on recent precipitation"""
        if len(self.weather_history) < 30:  # Need at least 30 days of history
            return 0.0
        
        # Calculate total precipitation over last 30 days
        recent_weather = self.weather_history[-30:]
        total_precip = sum(w.precipitation_total for w in recent_weather)
        
        # Expected precipitation for 30 days (monthly average)
        expected_precip = self.climate_model.annual_precipitation / 12.0
        
        # Drought index: 0 = no drought, 1 = severe drought
        if expected_precip > 0:
            drought_ratio = total_precip / expected_precip
            drought_index = max(0.0, 1.0 - drought_ratio)
        else:
            drought_index = 0.0
        
        return min(1.0, drought_index)
    
    def _check_weather_events(self):
        """Check for significant weather events"""
        if not self.current_weather:
            return
        
        current_time = self.time_manager.get_current_time() if self.time_manager else datetime.now()
        
        # Check for extreme temperature events
        if self.current_weather.temperature > 35:
            self._create_weather_event(
                "heat_wave", WeatherSeverity.WARNING, current_time,
                "Heat Wave Warning", "Extreme high temperatures affecting crops"
            )
        elif self.current_weather.temperature < -10:
            self._create_weather_event(
                "cold_snap", WeatherSeverity.WARNING, current_time,
                "Cold Snap Warning", "Extreme low temperatures may damage crops"
            )
        
        # Check for severe precipitation
        if self.current_weather.precipitation_rate > 10:
            self._create_weather_event(
                "heavy_rain", WeatherSeverity.ADVISORY, current_time,
                "Heavy Rain Advisory", "Heavy precipitation may affect field work"
            )
        
        # Check for drought conditions
        if self.current_weather.drought_index > 0.6:
            self._create_weather_event(
                "drought", WeatherSeverity.WARNING, current_time,
                "Drought Warning", "Extended dry period affecting crop growth"
            )
    
    def _create_weather_event(self, event_type: str, severity: WeatherSeverity,
                            start_time: datetime, title: str, description: str):
        """Create a weather event"""
        # Check if similar event already exists
        for event in self.active_events:
            if event.event_type == event_type and event.severity == severity:
                return  # Don't create duplicate events
        
        event_id = f"{event_type}_{start_time.strftime('%Y%m%d_%H%M')}"
        
        # Estimate event duration
        duration_hours = {
            "heat_wave": 24,
            "cold_snap": 12,
            "heavy_rain": 6,
            "drought": 168  # 7 days
        }
        
        duration = duration_hours.get(event_type, 12)
        end_time = start_time + timedelta(hours=duration)
        
        weather_event = WeatherEvent(
            event_id=event_id,
            event_type=event_type,
            severity=severity,
            start_time=start_time,
            end_time=end_time,
            description=description,
            temperature_modifier=0.0,
            precipitation_modifier=0.0,
            wind_modifier=0.0,
            crop_damage_potential=self._calculate_crop_damage_potential(event_type),
            soil_impact=0.1,
            equipment_restrictions=self._get_equipment_restrictions(event_type),
            advisory_message=title,
            recommended_actions=self._get_recommended_actions(event_type)
        )
        
        self.active_events.append(weather_event)
        
        # Publish weather event
        if self.event_system:
            self.event_system.publish("weather_event_started", {
                "event": weather_event,
                "severity": severity.value,
                "type": event_type
            })
        
        logger.info(f"Created weather event: {title}")
    
    def _calculate_crop_damage_potential(self, event_type: str) -> float:
        """Calculate potential crop damage from weather event"""
        damage_potentials = {
            "heat_wave": 0.3,
            "cold_snap": 0.4,
            "heavy_rain": 0.2,
            "drought": 0.5,
            "hail": 0.8,
            "thunderstorm": 0.3
        }
        
        return damage_potentials.get(event_type, 0.1)
    
    def _get_equipment_restrictions(self, event_type: str) -> List[str]:
        """Get equipment restrictions during weather event"""
        restrictions = {
            "heat_wave": ["outdoor_work_midday"],
            "cold_snap": ["water_systems"],
            "heavy_rain": ["field_equipment", "harvesting"],
            "drought": ["irrigation_intensive"],
            "thunderstorm": ["all_outdoor_equipment"]
        }
        
        return restrictions.get(event_type, [])
    
    def _get_recommended_actions(self, event_type: str) -> List[str]:
        """Get recommended actions for weather event"""
        actions = {
            "heat_wave": [
                "Increase irrigation frequency",
                "Provide shade for livestock",
                "Schedule work during cooler hours"
            ],
            "cold_snap": [
                "Protect sensitive crops with covers",
                "Ensure heating systems are working",
                "Check water systems for freezing"
            ],
            "heavy_rain": [
                "Ensure proper field drainage",
                "Delay field operations",
                "Check for soil erosion"
            ],
            "drought": [
                "Implement water conservation measures",
                "Consider drought-resistant crop varieties",
                "Monitor soil moisture levels closely"
            ]
        }
        
        return actions.get(event_type, ["Monitor conditions closely"])
    
    def _update_weather_events(self):
        """Update and cleanup weather events"""
        current_time = self.time_manager.get_current_time() if self.time_manager else datetime.now()
        
        # Remove expired events
        active_events = []
        for event in self.active_events:
            if current_time < event.end_time:
                active_events.append(event)
            else:
                # Publish event ended
                if self.event_system:
                    self.event_system.publish("weather_event_ended", {
                        "event": event,
                        "duration": (current_time - event.start_time).total_seconds() / 3600
                    })
                logger.info(f"Weather event ended: {event.event_type}")
        
        self.active_events = active_events
    
    def _generate_forecast(self):
        """Generate weather forecast"""
        if not self.current_weather or not self.time_manager:
            return
        
        current_time = self.time_manager.get_current_time()
        forecast_conditions = []
        forecast_confidence = []
        
        # Generate daily forecasts
        base_accuracy = 0.9  # Start with 90% accuracy
        
        for day in range(self.max_forecast_days):
            forecast_date = current_time + timedelta(days=day)
            
            # Accuracy decreases over time
            accuracy = max(0.3, base_accuracy - (day * self.forecast_accuracy_decay))
            forecast_confidence.append(accuracy)
            
            # Generate forecast condition for this day
            if day == 0:
                # Today's forecast is based on current conditions
                forecast_condition = self.current_weather
            else:
                # Future forecasts based on climate model and trends
                forecast_condition = self._generate_forecast_condition(forecast_date, accuracy)
            
            forecast_conditions.append(forecast_condition)
        
        # Create forecast object
        self.current_forecast = WeatherForecast(
            forecast_date=current_time,
            forecast_days=self.max_forecast_days,
            accuracy=base_accuracy,
            daily_conditions=forecast_conditions,
            daily_confidence=forecast_confidence,
            weekly_trends=self._generate_weekly_trends(),
            monthly_outlook=self._generate_monthly_outlook(),
            planting_recommendations=self._generate_planting_recommendations(),
            harvest_windows=self._generate_harvest_windows(),
            irrigation_schedule=self._generate_irrigation_schedule()
        )
        
        # Publish forecast update
        if self.event_system:
            self.event_system.publish("weather_forecast_updated", {
                "forecast": self.current_forecast,
                "forecast_days": self.max_forecast_days
            })
        
        logger.info(f"Generated {self.max_forecast_days}-day weather forecast")
    
    def _generate_forecast_condition(self, forecast_date: datetime, 
                                   accuracy: float) -> WeatherCondition:
        """Generate weather condition for forecast date"""
        # Get seasonal average for forecast date
        season = self._get_season_for_date(forecast_date)
        base_temp = self.climate_model.avg_temp_by_season.get(season, 15.0)
        
        # Add uncertainty based on accuracy
        uncertainty = (1.0 - accuracy) * 10.0  # Up to 10°C uncertainty
        temp_variation = random.gauss(0, uncertainty)
        forecast_temp = base_temp + temp_variation
        
        # Generate other forecast parameters with uncertainty
        forecast_condition = WeatherCondition(
            weather_type=self._forecast_weather_type(season, accuracy),
            temperature=forecast_temp,
            temperature_high=forecast_temp + random.uniform(5, 12),
            temperature_low=forecast_temp - random.uniform(5, 12),
            humidity=random.uniform(0.4, 0.8),
            precipitation_rate=random.uniform(0, 2) if random.random() < 0.3 else 0.0,
            precipitation_total=random.uniform(0, 15) if random.random() < 0.3 else 0.0,
            wind_speed=random.uniform(2, 10),
            wind_direction=random.uniform(0, 360),
            atmospheric_pressure=1013.25 + random.gauss(0, 5),
            solar_radiation=self._calculate_solar_radiation(season),
            cloud_cover=random.uniform(0.2, 0.8),
            visibility=random.uniform(10, 25),
            uv_index=self._calculate_uv_index(season),
            growing_degree_days=max(0, forecast_temp - 10),
            chill_hours=1.0 if forecast_temp < 7 else 0.0,
            heat_stress_index=max(0, forecast_temp - 30) / 10.0,
            drought_index=0.0  # Simplified for forecast
        )
        
        return forecast_condition
    
    def _get_season_for_date(self, date: datetime) -> Season:
        """Get season for a specific date"""
        # Simplified season calculation based on month
        month = date.month
        if 3 <= month <= 5:
            return Season.SPRING
        elif 6 <= month <= 8:
            return Season.SUMMER
        elif 9 <= month <= 11:
            return Season.FALL
        else:
            return Season.WINTER
    
    def _forecast_weather_type(self, season: Season, accuracy: float) -> WeatherType:
        """Forecast weather type with uncertainty"""
        # Seasonal probabilities for weather types
        seasonal_probs = {
            Season.SPRING: {
                WeatherType.PARTLY_CLOUDY: 0.3,
                WeatherType.CLOUDY: 0.25,
                WeatherType.LIGHT_RAIN: 0.2,
                WeatherType.CLEAR: 0.15,
                WeatherType.RAIN: 0.1
            },
            Season.SUMMER: {
                WeatherType.CLEAR: 0.4,
                WeatherType.PARTLY_CLOUDY: 0.3,
                WeatherType.CLOUDY: 0.2,
                WeatherType.THUNDERSTORM: 0.1
            },
            Season.FALL: {
                WeatherType.CLOUDY: 0.3,
                WeatherType.PARTLY_CLOUDY: 0.25,
                WeatherType.RAIN: 0.2,
                WeatherType.CLEAR: 0.15,
                WeatherType.LIGHT_RAIN: 0.1
            },
            Season.WINTER: {
                WeatherType.CLOUDY: 0.35,
                WeatherType.PARTLY_CLOUDY: 0.25,
                WeatherType.LIGHT_RAIN: 0.2,
                WeatherType.CLEAR: 0.1,
                WeatherType.RAIN: 0.1
            }
        }
        
        probs = seasonal_probs.get(season, {WeatherType.PARTLY_CLOUDY: 1.0})
        
        # Add uncertainty - lower accuracy means more random selection
        if accuracy < 0.7:
            # Add more randomness to probabilities
            for weather_type in probs:
                probs[weather_type] += random.uniform(-0.1, 0.1)
            
            # Normalize probabilities
            total = sum(probs.values())
            if total > 0:
                for weather_type in probs:
                    probs[weather_type] /= total
        
        # Select weather type
        weather_types = list(probs.keys())
        weights = list(probs.values())
        
        return random.choices(weather_types, weights=weights)[0]
    
    def _generate_weekly_trends(self) -> Dict[str, str]:
        """Generate weekly weather trends"""
        trends = {
            "temperature": "stable",
            "precipitation": "below_average",
            "general": "partly_cloudy"
        }
        
        if self.current_weather:
            # Analyze current temperature trend
            if self.current_weather.temperature > 25:
                trends["temperature"] = "above_average"
            elif self.current_weather.temperature < 10:
                trends["temperature"] = "below_average"
            
            # Analyze precipitation trend
            if self.current_weather.drought_index > 0.3:
                trends["precipitation"] = "below_average"
            elif self.current_weather.precipitation_rate > 2:
                trends["precipitation"] = "above_average"
        
        return trends
    
    def _generate_monthly_outlook(self) -> Dict[str, str]:
        """Generate monthly climate outlook"""
        current_season = self.time_manager.get_current_season() if self.time_manager else Season.SPRING
        
        outlook = {
            "temperature": "near_normal",
            "precipitation": "near_normal",
            "confidence": "moderate"
        }
        
        # Seasonal outlook adjustments
        if current_season == Season.SUMMER:
            outlook["temperature"] = "above_normal"
            outlook["precipitation"] = "below_normal"
        elif current_season == Season.WINTER:
            outlook["temperature"] = "below_normal"
            outlook["precipitation"] = "above_normal"
        
        return outlook
    
    def _generate_planting_recommendations(self) -> List[str]:
        """Generate planting recommendations based on forecast"""
        recommendations = []
        
        if not self.current_forecast:
            return ["Monitor weather conditions before planting"]
        
        # Analyze next 7 days
        next_week = self.current_forecast.daily_conditions[:7]
        
        # Check for suitable planting conditions
        avg_temp = statistics.mean(day.temperature for day in next_week)
        total_precip = sum(day.precipitation_total for day in next_week)
        
        if 15 <= avg_temp <= 25 and total_precip < 30:
            recommendations.append("Good conditions for spring planting")
        elif avg_temp > 30:
            recommendations.append("Wait for cooler temperatures before planting")
        elif total_precip > 50:
            recommendations.append("Delay planting until soil dries out")
        
        return recommendations or ["Monitor conditions for planting opportunities"]
    
    def _generate_harvest_windows(self) -> List[Tuple[datetime, datetime]]:
        """Generate optimal harvest windows"""
        if not self.current_forecast or not self.time_manager:
            return []
        
        current_time = self.time_manager.get_current_time()
        harvest_windows = []
        
        # Look for periods with low precipitation and moderate temperatures
        for i, condition in enumerate(self.current_forecast.daily_conditions):
            if (condition.precipitation_rate < 1.0 and 
                10 <= condition.temperature <= 30 and
                condition.wind_speed < 12):
                
                start_date = current_time + timedelta(days=i)
                end_date = start_date + timedelta(days=1)
                harvest_windows.append((start_date, end_date))
        
        return harvest_windows[:5]  # Return up to 5 optimal windows
    
    def _generate_irrigation_schedule(self) -> List[Tuple[datetime, float]]:
        """Generate irrigation schedule recommendations"""
        if not self.current_forecast or not self.time_manager:
            return []
        
        current_time = self.time_manager.get_current_time()
        irrigation_schedule = []
        
        # Recommend irrigation based on precipitation deficit
        for i, condition in enumerate(self.current_forecast.daily_conditions[:7]):
            irrigation_date = current_time + timedelta(days=i)
            
            # Calculate irrigation need
            if condition.precipitation_total < 5 and condition.temperature > 20:
                irrigation_amount = 15.0 - condition.precipitation_total  # mm
                irrigation_schedule.append((irrigation_date, irrigation_amount))
        
        return irrigation_schedule
    
    def _cleanup_weather_history(self):
        """Clean up old weather history to prevent memory bloat"""
        max_history_days = 365  # Keep one year of history
        
        if len(self.weather_history) > max_history_days:
            # Keep only the most recent records
            self.weather_history = self.weather_history[-max_history_days:]
            logger.info(f"Cleaned weather history, kept {max_history_days} days")
    
    # Event handlers
    def _on_time_advanced(self, event_data: Dict[str, Any]):
        """Handle time advancement"""
        delta_hours = event_data.get("delta_hours", 1.0)
        self.update(delta_hours)
    
    def _on_day_changed(self, event_data: Dict[str, Any]):
        """Handle day change events"""
        new_date = event_data.get("new_date")
        logger.info(f"New day: {new_date}, updating daily weather patterns")
    
    def _on_season_changed(self, event_data: Dict[str, Any]):
        """Handle seasonal changes"""
        new_season = event_data.get("new_season")
        old_season = event_data.get("old_season")
        
        logger.info(f"Season changed from {old_season} to {new_season}")
        
        # Update seasonal weather patterns
        if self.current_weather:
            # Adjust temperature toward seasonal average
            seasonal_temp = self.climate_model.avg_temp_by_season.get(
                Season(new_season), 15.0
            )
            
            # Gradual temperature adjustment over transition period
            temp_adjustment = (seasonal_temp - self.current_weather.temperature) * 0.1
            self.current_weather.temperature += temp_adjustment
            
        # Regenerate forecast for new season
        self._generate_forecast()
    
    def _on_forecast_requested(self, event_data: Dict[str, Any]):
        """Handle forecast requests"""
        days_requested = event_data.get("days", 7)
        location = event_data.get("location", "default")
        
        if self.current_forecast:
            # Return forecast for requested period
            forecast_data = {
                "location": location,
                "days": min(days_requested, len(self.current_forecast.daily_conditions)),
                "conditions": self.current_forecast.daily_conditions[:days_requested],
                "accuracy": self.current_forecast.accuracy
            }
            
            if self.event_system:
                self.event_system.publish("weather_forecast_response", forecast_data)
    
    def _on_weather_event_check(self, event_data: Dict[str, Any]):
        """Handle weather event checks"""
        location = event_data.get("location")
        
        # Return active weather events
        if self.event_system:
            self.event_system.publish("weather_events_response", {
                "location": location,
                "active_events": [
                    {
                        "type": event.event_type,
                        "severity": event.severity.value,
                        "description": event.description,
                        "end_time": event.end_time.isoformat()
                    }
                    for event in self.active_events
                ]
            })
    
    # Public interface methods
    def get_current_weather(self) -> Optional[WeatherCondition]:
        """Get current weather conditions"""
        return self.current_weather
    
    def get_weather_forecast(self, days: int = 7) -> Optional[WeatherForecast]:
        """Get weather forecast for specified number of days"""
        if not self.current_forecast:
            return None
        
        if days <= len(self.current_forecast.daily_conditions):
            # Return truncated forecast
            forecast_copy = WeatherForecast(
                forecast_date=self.current_forecast.forecast_date,
                forecast_days=days,
                accuracy=self.current_forecast.accuracy,
                daily_conditions=self.current_forecast.daily_conditions[:days],
                daily_confidence=self.current_forecast.daily_confidence[:days],
                weekly_trends=self.current_forecast.weekly_trends,
                monthly_outlook=self.current_forecast.monthly_outlook,
                planting_recommendations=self.current_forecast.planting_recommendations,
                harvest_windows=self.current_forecast.harvest_windows,
                irrigation_schedule=self.current_forecast.irrigation_schedule
            )
            return forecast_copy
        
        return self.current_forecast
    
    def get_weather_history(self, days: int = 30) -> List[WeatherCondition]:
        """Get weather history for specified number of days"""
        if days <= len(self.weather_history):
            return self.weather_history[-days:]
        return self.weather_history
    
    def get_active_weather_events(self) -> List[WeatherEvent]:
        """Get currently active weather events"""
        return self.active_events.copy()
    
    def is_suitable_for_field_work(self) -> bool:
        """Check if current conditions are suitable for field work"""
        if not self.current_weather:
            return False
        
        return self.current_weather.is_suitable_for_field_work()
    
    def get_spray_conditions(self) -> Dict[str, Any]:
        """Get conditions for pesticide/herbicide spraying"""
        if not self.current_weather:
            return {"suitable": False, "reason": "No weather data"}
        
        # Ideal spraying conditions
        temp_ok = 10 <= self.current_weather.temperature <= 25
        wind_ok = self.current_weather.wind_speed <= 10  # Low wind for drift control
        rain_ok = self.current_weather.precipitation_rate == 0
        humidity_ok = self.current_weather.humidity >= 0.4  # Prevent evaporation
        
        suitable = temp_ok and wind_ok and rain_ok and humidity_ok
        
        reasons = []
        if not temp_ok:
            reasons.append("Temperature outside ideal range (10-25°C)")
        if not wind_ok:
            reasons.append("Wind too strong (>10 m/s)")
        if not rain_ok:
            reasons.append("Precipitation present")
        if not humidity_ok:
            reasons.append("Humidity too low (<40%)")
        
        return {
            "suitable": suitable,
            "temperature": self.current_weather.temperature,
            "wind_speed": self.current_weather.wind_speed,
            "humidity": self.current_weather.humidity,
            "precipitation": self.current_weather.precipitation_rate,
            "reasons": reasons if not suitable else []
        }
    
    def get_irrigation_recommendation(self) -> Dict[str, Any]:
        """Get irrigation recommendations based on weather"""
        if not self.current_weather:
            return {"recommended": False, "reason": "No weather data"}
        
        # Check recent precipitation
        recent_precip = 0.0
        if len(self.weather_history) >= 3:
            recent_precip = sum(w.precipitation_total for w in self.weather_history[-3:])
        
        # Irrigation recommendation logic
        drought_stress = self.current_weather.drought_index > 0.3
        high_temp = self.current_weather.temperature > 25
        low_recent_rain = recent_precip < 15  # Less than 15mm in last 3 days
        
        recommended = drought_stress or (high_temp and low_recent_rain)
        
        # Calculate recommended amount
        if recommended:
            base_amount = 15.0  # Base irrigation amount
            temp_factor = max(1.0, self.current_weather.temperature / 25.0)
            drought_factor = 1.0 + self.current_weather.drought_index
            amount = base_amount * temp_factor * drought_factor
        else:
            amount = 0.0
        
        return {
            "recommended": recommended,
            "amount_mm": amount,
            "drought_index": self.current_weather.drought_index,
            "recent_precipitation": recent_precip,
            "temperature": self.current_weather.temperature,
            "reason": "High temperature and low precipitation" if recommended else "Adequate moisture"
        }
    
    def get_disease_pressure_forecast(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get disease pressure forecast"""
        if not self.current_forecast:
            return []
        
        disease_forecast = []
        
        for i in range(min(days, len(self.current_forecast.daily_conditions))):
            condition = self.current_forecast.daily_conditions[i]
            risk = condition.get_disease_pressure_risk()
            
            risk_level = "low"
            if risk > 0.7:
                risk_level = "high"
            elif risk > 0.4:
                risk_level = "moderate"
            
            forecast_date = self.current_forecast.forecast_date + timedelta(days=i)
            
            disease_forecast.append({
                "date": forecast_date.isoformat(),
                "risk_level": risk_level,
                "risk_score": risk,
                "temperature": condition.temperature,
                "humidity": condition.humidity,
                "precipitation": condition.precipitation_total
            })
        
        return disease_forecast
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive weather system status"""
        return {
            "system_name": self.system_name,
            "current_weather": {
                "type": self.current_weather.weather_type.value if self.current_weather else None,
                "temperature": self.current_weather.temperature if self.current_weather else None,
                "suitable_for_field_work": self.is_suitable_for_field_work()
            },
            "climate_model": {
                "zone": self.climate_model.zone.value if self.climate_model else None,
                "annual_precipitation": self.climate_model.annual_precipitation if self.climate_model else None
            },
            "forecast": {
                "available": self.current_forecast is not None,
                "days": self.current_forecast.forecast_days if self.current_forecast else 0,
                "accuracy": self.current_forecast.accuracy if self.current_forecast else 0.0
            },
            "active_events": len(self.active_events),
            "weather_history_days": len(self.weather_history),
            "update_frequency": self.update_frequency,
            "last_update": self.last_update_time
        }

# Global convenience functions for system access
_weather_system_instance = None

def get_weather_system() -> WeatherSystem:
    """Get the global Weather System instance"""
    global _weather_system_instance
    if _weather_system_instance is None:
        _weather_system_instance = WeatherSystem()
    return _weather_system_instance

def initialize_weather_system() -> bool:
    """Initialize the global Weather System"""
    system = get_weather_system()
    return system.initialize()

def get_current_weather() -> Optional[WeatherCondition]:
    """Convenience function to get current weather"""
    system = get_weather_system()
    return system.get_current_weather()

def get_weather_forecast(days: int = 7) -> Optional[WeatherForecast]:
    """Convenience function to get weather forecast"""
    system = get_weather_system()
    return system.get_weather_forecast(days)

def is_good_weather_for_farming() -> bool:
    """Convenience function to check farming conditions"""
    system = get_weather_system()
    return system.is_suitable_for_field_work()

def get_irrigation_advice() -> Dict[str, Any]:
    """Convenience function to get irrigation recommendations"""
    system = get_weather_system()
    return system.get_irrigation_recommendation()