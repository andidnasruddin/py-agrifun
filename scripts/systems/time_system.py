"""
Time Management System - Comprehensive Temporal Engine for AgriFun Agricultural Simulation

This system provides the temporal foundation for realistic agricultural simulation including:
- Dynamic seasons with agricultural effects
- Weather patterns affecting crop growth and operations
- Day/night cycles with work schedule coordination
- Time acceleration for strategic planning
- Agricultural calendar integration

Key Features:
- Realistic seasonal progression (Spring→Summer→Fall→Winter)
- Dynamic weather simulation with agricultural impacts
- Employee work schedule coordination
- Market timing and seasonal price fluctuations
- Crop growth timing and optimal planting/harvest windows
- Time-based event scheduling and management

Integration Points:
- Event System: time_tick, season_changed, weather_updated, day_started
- ECS Components: TemporalComponent, WeatherComponent, ScheduleComponent
- Configuration: Time rates, weather patterns, seasonal data
- State Management: Temporal checkpoints and time travel debugging

Example Usage:
    time_system = TimeSystem()
    time_system.start()
    
    # Set time acceleration
    time_system.set_time_scale(4.0)  # 4x speed
    
    # Get current season
    current_season = time_system.get_current_season()
    
    # Check weather conditions
    weather = time_system.get_current_weather()
    
    # Schedule agricultural events
    time_system.schedule_event("harvest_reminder", 7 * 24 * 60)  # 7 days
"""

import time
import asyncio
import threading
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import math
import random
import logging

# Import foundation systems
from ..core.event_system import get_global_event_system, EventPriority
from ..core.entity_component_system import get_entity_manager
from ..core.configuration_system import get_configuration_manager
from ..core.state_management import get_state_manager


class Season(Enum):
    """Agricultural seasons"""
    SPRING = "spring"
    SUMMER = "summer"  
    FALL = "fall"
    WINTER = "winter"


class WeatherType(Enum):
    """Weather condition types"""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    OVERCAST = "overcast"
    LIGHT_RAIN = "light_rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    FOG = "fog"
    DROUGHT = "drought"
    HEAT_WAVE = "heat_wave"
    FROST = "frost"
    SNOW = "snow"
    BLIZZARD = "blizzard"


class TimeOfDay(Enum):
    """Time periods for work scheduling"""
    EARLY_MORNING = "early_morning"  # 4-6 AM
    MORNING = "morning"              # 6-9 AM
    MID_MORNING = "mid_morning"      # 9-12 PM
    AFTERNOON = "afternoon"          # 12-3 PM
    LATE_AFTERNOON = "late_afternoon" # 3-6 PM
    EVENING = "evening"              # 6-9 PM
    NIGHT = "night"                  # 9 PM - 4 AM


@dataclass
class GameTime:
    """Comprehensive game time representation"""
    # Basic time units
    minutes: int = 0        # Game minutes (0-59)
    hours: int = 6          # Game hours (0-23), start at 6 AM
    days: int = 1           # Day of season (1-90)
    season: Season = Season.SPRING
    year: int = 1           # Game year
    
    # Derived time information
    total_minutes: int = 0  # Total minutes since game start
    day_of_year: int = 1    # Day within the year (1-360)
    week_of_season: int = 1 # Week within season (1-12)
    
    def get_time_string(self) -> str:
        """Get formatted time string"""
        am_pm = "AM" if self.hours < 12 else "PM"
        display_hour = self.hours if self.hours <= 12 else self.hours - 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:{self.minutes:02d} {am_pm}"
    
    def get_date_string(self) -> str:
        """Get formatted date string"""
        return f"{self.season.value.title()} {self.days}, Year {self.year}"
    
    def get_time_of_day(self) -> TimeOfDay:
        """Get current time period"""
        if 4 <= self.hours < 6:
            return TimeOfDay.EARLY_MORNING
        elif 6 <= self.hours < 9:
            return TimeOfDay.MORNING
        elif 9 <= self.hours < 12:
            return TimeOfDay.MID_MORNING
        elif 12 <= self.hours < 15:
            return TimeOfDay.AFTERNOON
        elif 15 <= self.hours < 18:
            return TimeOfDay.LATE_AFTERNOON
        elif 18 <= self.hours < 21:
            return TimeOfDay.EVENING
        else:
            return TimeOfDay.NIGHT
    
    def is_work_hours(self) -> bool:
        """Check if current time is during standard work hours"""
        return 6 <= self.hours < 18  # 6 AM to 6 PM
    
    def copy(self) -> 'GameTime':
        """Create a copy of game time"""
        return GameTime(
            minutes=self.minutes,
            hours=self.hours,
            days=self.days,
            season=self.season,
            year=self.year,
            total_minutes=self.total_minutes,
            day_of_year=self.day_of_year,
            week_of_season=self.week_of_season
        )


@dataclass
class WeatherCondition:
    """Current weather state"""
    weather_type: WeatherType = WeatherType.CLEAR
    temperature_c: float = 20.0      # Temperature in Celsius
    humidity_percent: float = 50.0    # Relative humidity
    wind_speed_kmh: float = 10.0     # Wind speed in km/h
    precipitation_mm: float = 0.0     # Precipitation in mm
    
    # Agricultural effects
    crop_growth_modifier: float = 1.0  # Multiplier for crop growth
    soil_moisture_change: float = 0.0  # Daily soil moisture change
    work_efficiency_modifier: float = 1.0  # Employee efficiency modifier
    
    # Weather quality indicators
    visibility_km: float = 10.0       # Visibility in kilometers
    uv_index: int = 5                 # UV index (0-11)
    
    def get_description(self) -> str:
        """Get human-readable weather description"""
        descriptions = {
            WeatherType.CLEAR: "Clear skies",
            WeatherType.PARTLY_CLOUDY: "Partly cloudy",
            WeatherType.OVERCAST: "Overcast",
            WeatherType.LIGHT_RAIN: "Light rain",
            WeatherType.HEAVY_RAIN: "Heavy rain",
            WeatherType.THUNDERSTORM: "Thunderstorm",
            WeatherType.FOG: "Foggy",
            WeatherType.DROUGHT: "Drought conditions",
            WeatherType.HEAT_WAVE: "Heat wave",
            WeatherType.FROST: "Frost warning",
            WeatherType.SNOW: "Snow",
            WeatherType.BLIZZARD: "Blizzard"
        }
        temp_f = (self.temperature_c * 9/5) + 32
        return f"{descriptions[self.weather_type]}, {temp_f:.0f}°F"


@dataclass
class ScheduledEvent:
    """Scheduled time-based event"""
    event_id: str
    event_type: str
    trigger_time: int           # Total minutes when event should trigger
    event_data: Dict[str, Any] = field(default_factory=dict)
    recurring: bool = False     # Whether event repeats
    recurrence_interval: int = 0  # Minutes between recurrences
    priority: EventPriority = EventPriority.NORMAL
    
    def should_trigger(self, current_total_minutes: int) -> bool:
        """Check if event should trigger at current time"""
        return current_total_minutes >= self.trigger_time


class WeatherSystem:
    """Dynamic weather simulation system"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger('WeatherSystem')
        
        # Weather state
        self.current_weather = WeatherCondition()
        self.forecast = []  # 7-day forecast
        
        # Weather patterns
        self.seasonal_temperature_base = {
            Season.SPRING: 15.0,  # Celsius
            Season.SUMMER: 25.0,
            Season.FALL: 12.0,
            Season.WINTER: 2.0
        }
        
        # Weather transition probabilities by season
        self.weather_transitions = {
            Season.SPRING: {
                WeatherType.CLEAR: 0.4,
                WeatherType.PARTLY_CLOUDY: 0.3,
                WeatherType.LIGHT_RAIN: 0.2,
                WeatherType.OVERCAST: 0.1
            },
            Season.SUMMER: {
                WeatherType.CLEAR: 0.6,
                WeatherType.PARTLY_CLOUDY: 0.2,
                WeatherType.HEAT_WAVE: 0.1,
                WeatherType.THUNDERSTORM: 0.1
            },
            Season.FALL: {
                WeatherType.PARTLY_CLOUDY: 0.3,
                WeatherType.OVERCAST: 0.3,
                WeatherType.LIGHT_RAIN: 0.2,
                WeatherType.HEAVY_RAIN: 0.1,
                WeatherType.FOG: 0.1
            },
            Season.WINTER: {
                WeatherType.OVERCAST: 0.4,
                WeatherType.SNOW: 0.3,
                WeatherType.FROST: 0.2,
                WeatherType.BLIZZARD: 0.1
            }
        }
    
    def update_weather(self, game_time: GameTime):
        """Update weather conditions based on season and time"""
        season = game_time.season
        base_temp = self.seasonal_temperature_base[season]
        
        # Daily temperature variation (cooler at night, warmer during day)
        time_factor = math.sin((game_time.hours / 24.0) * 2 * math.pi - math.pi/2)
        daily_variation = 8.0 * time_factor  # ±8°C variation
        
        # Random weather variation
        weather_variation = random.uniform(-3.0, 3.0)
        
        # Calculate current temperature
        self.current_weather.temperature_c = base_temp + daily_variation + weather_variation
        
        # Update weather type if it's a new day
        if game_time.hours == 6 and game_time.minutes == 0:  # 6 AM weather update
            self._generate_daily_weather(season)
        
        # Calculate agricultural effects
        self._calculate_weather_effects()
    
    def _generate_daily_weather(self, season: Season):
        """Generate new weather for the day"""
        probabilities = self.weather_transitions[season]
        
        # Weighted random selection
        weather_types = list(probabilities.keys())
        weights = list(probabilities.values())
        
        # Select weather type
        self.current_weather.weather_type = random.choices(weather_types, weights=weights)[0]
        
        # Set weather-specific parameters
        self._set_weather_parameters()
        
        self.logger.info(f"Weather updated: {self.current_weather.get_description()}")
    
    def _set_weather_parameters(self):
        """Set weather parameters based on weather type"""
        weather = self.current_weather
        
        if weather.weather_type == WeatherType.CLEAR:
            weather.humidity_percent = random.uniform(30, 50)
            weather.wind_speed_kmh = random.uniform(5, 15)
            weather.precipitation_mm = 0.0
            weather.visibility_km = 15.0
            
        elif weather.weather_type == WeatherType.LIGHT_RAIN:
            weather.humidity_percent = random.uniform(80, 95)
            weather.wind_speed_kmh = random.uniform(10, 20)
            weather.precipitation_mm = random.uniform(1, 5)
            weather.visibility_km = 8.0
            
        elif weather.weather_type == WeatherType.HEAVY_RAIN:
            weather.humidity_percent = random.uniform(90, 100)
            weather.wind_speed_kmh = random.uniform(20, 40)
            weather.precipitation_mm = random.uniform(10, 25)
            weather.visibility_km = 3.0
            
        elif weather.weather_type == WeatherType.THUNDERSTORM:
            weather.humidity_percent = random.uniform(85, 100)
            weather.wind_speed_kmh = random.uniform(30, 60)
            weather.precipitation_mm = random.uniform(15, 40)
            weather.visibility_km = 2.0
            
        elif weather.weather_type == WeatherType.DROUGHT:
            weather.humidity_percent = random.uniform(10, 30)
            weather.wind_speed_kmh = random.uniform(15, 25)
            weather.precipitation_mm = 0.0
            weather.visibility_km = 12.0
            
        elif weather.weather_type == WeatherType.HEAT_WAVE:
            weather.temperature_c += random.uniform(5, 12)
            weather.humidity_percent = random.uniform(20, 40)
            weather.wind_speed_kmh = random.uniform(5, 15)
            weather.precipitation_mm = 0.0
            
        elif weather.weather_type == WeatherType.FROST:
            weather.temperature_c = random.uniform(-5, 2)
            weather.humidity_percent = random.uniform(70, 90)
            weather.wind_speed_kmh = random.uniform(5, 15)
            weather.precipitation_mm = 0.0
            
        elif weather.weather_type == WeatherType.SNOW:
            weather.temperature_c = random.uniform(-8, 0)
            weather.humidity_percent = random.uniform(80, 95)
            weather.wind_speed_kmh = random.uniform(10, 25)
            weather.precipitation_mm = random.uniform(5, 15)  # Snow equivalent
            weather.visibility_km = 5.0
            
        elif weather.weather_type == WeatherType.BLIZZARD:
            weather.temperature_c = random.uniform(-15, -5)
            weather.humidity_percent = random.uniform(85, 100)
            weather.wind_speed_kmh = random.uniform(40, 80)
            weather.precipitation_mm = random.uniform(20, 50)
            weather.visibility_km = 0.5
    
    def _calculate_weather_effects(self):
        """Calculate agricultural and operational effects of weather"""
        weather = self.current_weather
        
        # Crop growth modifiers
        if weather.weather_type == WeatherType.CLEAR:
            weather.crop_growth_modifier = 1.1
        elif weather.weather_type == WeatherType.LIGHT_RAIN:
            weather.crop_growth_modifier = 1.2
        elif weather.weather_type == WeatherType.HEAVY_RAIN:
            weather.crop_growth_modifier = 0.9
        elif weather.weather_type == WeatherType.DROUGHT:
            weather.crop_growth_modifier = 0.6
        elif weather.weather_type == WeatherType.HEAT_WAVE:
            weather.crop_growth_modifier = 0.7
        elif weather.weather_type == WeatherType.FROST:
            weather.crop_growth_modifier = 0.3
        elif weather.weather_type == WeatherType.SNOW:
            weather.crop_growth_modifier = 0.2
        else:
            weather.crop_growth_modifier = 1.0
        
        # Work efficiency modifiers
        if weather.weather_type in [WeatherType.CLEAR, WeatherType.PARTLY_CLOUDY]:
            weather.work_efficiency_modifier = 1.0
        elif weather.weather_type in [WeatherType.LIGHT_RAIN, WeatherType.OVERCAST]:
            weather.work_efficiency_modifier = 0.9
        elif weather.weather_type in [WeatherType.HEAVY_RAIN, WeatherType.THUNDERSTORM]:
            weather.work_efficiency_modifier = 0.6
        elif weather.weather_type == WeatherType.HEAT_WAVE:
            weather.work_efficiency_modifier = 0.7
        elif weather.weather_type in [WeatherType.FROST, WeatherType.SNOW]:
            weather.work_efficiency_modifier = 0.8
        elif weather.weather_type == WeatherType.BLIZZARD:
            weather.work_efficiency_modifier = 0.3
        else:
            weather.work_efficiency_modifier = 0.85
        
        # Soil moisture changes
        if weather.weather_type in [WeatherType.LIGHT_RAIN]:
            weather.soil_moisture_change = 0.1
        elif weather.weather_type == WeatherType.HEAVY_RAIN:
            weather.soil_moisture_change = 0.2
        elif weather.weather_type == WeatherType.THUNDERSTORM:
            weather.soil_moisture_change = 0.3
        elif weather.weather_type == WeatherType.DROUGHT:
            weather.soil_moisture_change = -0.2
        elif weather.weather_type == WeatherType.HEAT_WAVE:
            weather.soil_moisture_change = -0.15
        else:
            weather.soil_moisture_change = -0.05  # Natural evaporation
    
    def get_forecast(self, days: int = 7) -> List[WeatherCondition]:
        """Get weather forecast for upcoming days"""
        # Generate basic forecast (simplified)
        forecast = []
        current_season = Season.SPRING  # Would get from time system
        
        for i in range(days):
            future_weather = WeatherCondition()
            probabilities = self.weather_transitions[current_season]
            weather_types = list(probabilities.keys())
            weights = list(probabilities.values())
            future_weather.weather_type = random.choices(weather_types, weights=weights)[0]
            forecast.append(future_weather)
        
        return forecast


class TimeSystem:
    """Main time management system"""
    
    def __init__(self):
        # Core systems
        self.event_system = get_global_event_system()
        self.entity_manager = get_entity_manager()
        self.config_manager = get_configuration_manager()
        self.state_manager = get_state_manager()
        
        # Time state
        self.game_time = GameTime()
        self.time_scale = 1.0  # 1.0 = real time, 2.0 = 2x speed
        self.paused = False
        self.running = False
        
        # Weather system
        self.weather_system = WeatherSystem(self.config_manager)
        
        # Event scheduling
        self.scheduled_events: Dict[str, ScheduledEvent] = {}
        self.event_counter = 0
        
        # Performance tracking
        self.last_update_time = 0.0
        self.update_frequency_ms = 100  # Update every 100ms
        self.time_thread: Optional[threading.Thread] = None
        
        # Agricultural calendar
        self.planting_windows = {
            Season.SPRING: ["corn", "wheat", "tomatoes", "carrots"],
            Season.SUMMER: ["tomatoes", "lettuce", "beans"],
            Season.FALL: ["wheat", "carrots", "winter_crops"],
            Season.WINTER: ["greenhouse_crops"]
        }
        
        self.logger = logging.getLogger('TimeSystem')
        
        # Load configuration
        self._load_configuration()
    
    def _load_configuration(self):
        """Load time system configuration"""
        # Default time configuration
        default_config = {
            'time.minutes_per_real_second': 2,
            'time.days_per_season': 90,
            'time.auto_pause_at_night': False,
            'weather.enable_dynamic_weather': True,
            'weather.extreme_weather_frequency': 0.1
        }
        
        for key, value in default_config.items():
            if self.config_manager.get(key) is None:
                self.config_manager.set(key, value)
    
    def start(self):
        """Start the time system"""
        if self.running:
            return
        
        self.running = True
        self.last_update_time = time.time()
        
        # Start time update thread
        self.time_thread = threading.Thread(target=self._time_loop, daemon=True)
        self.time_thread.start()
        
        self.logger.info("Time system started")
        
        # Emit start event
        self.event_system.publish('time_system_started', {
            'game_time': self._serialize_game_time()
        }, EventPriority.HIGH, 'time_system')
    
    def stop(self):
        """Stop the time system"""
        self.running = False
        
        if self.time_thread and self.time_thread.is_alive():
            self.time_thread.join(timeout=1.0)
        
        self.logger.info("Time system stopped")
        
        # Emit stop event
        self.event_system.publish('time_system_stopped', {
            'final_game_time': self._serialize_game_time()
        }, EventPriority.HIGH, 'time_system')
    
    def pause(self):
        """Pause time progression"""
        self.paused = True
        self.logger.info("Time paused")
        
        self.event_system.publish('time_paused', {
            'game_time': self._serialize_game_time()
        }, EventPriority.HIGH, 'time_system')
    
    def resume(self):
        """Resume time progression"""
        self.paused = False
        self.last_update_time = time.time()
        self.logger.info("Time resumed")
        
        self.event_system.publish('time_resumed', {
            'game_time': self._serialize_game_time()
        }, EventPriority.HIGH, 'time_system')
    
    def set_time_scale(self, scale: float):
        """Set time acceleration scale"""
        old_scale = self.time_scale
        self.time_scale = max(0.1, min(10.0, scale))  # Clamp between 0.1x and 10x
        
        self.logger.info(f"Time scale changed from {old_scale}x to {self.time_scale}x")
        
        self.event_system.publish('time_scale_changed', {
            'old_scale': old_scale,
            'new_scale': self.time_scale,
            'game_time': self._serialize_game_time()
        }, EventPriority.NORMAL, 'time_system')
    
    def advance_time(self, minutes: int):
        """Manually advance time by specified minutes"""
        old_time = self.game_time.copy()
        
        self.game_time.total_minutes += minutes
        self._update_derived_time()
        
        # Update weather
        self.weather_system.update_weather(self.game_time)
        
        # Process scheduled events
        self._process_scheduled_events()
        
        # Emit time advancement events
        self._emit_time_events(old_time)
        
        self.logger.info(f"Time advanced by {minutes} minutes to {self.game_time.get_date_string()}")
    
    def schedule_event(self, event_type: str, delay_minutes: int, 
                      event_data: Dict[str, Any] = None, 
                      recurring: bool = False, 
                      recurrence_interval: int = 0,
                      priority: EventPriority = EventPriority.NORMAL) -> str:
        """Schedule a time-based event"""
        self.event_counter += 1
        event_id = f"scheduled_event_{self.event_counter}"
        
        trigger_time = self.game_time.total_minutes + delay_minutes
        
        scheduled_event = ScheduledEvent(
            event_id=event_id,
            event_type=event_type,
            trigger_time=trigger_time,
            event_data=event_data or {},
            recurring=recurring,
            recurrence_interval=recurrence_interval,
            priority=priority
        )
        
        self.scheduled_events[event_id] = scheduled_event
        
        self.logger.info(f"Scheduled event '{event_type}' for {delay_minutes} minutes from now")
        return event_id
    
    def cancel_scheduled_event(self, event_id: str) -> bool:
        """Cancel a scheduled event"""
        if event_id in self.scheduled_events:
            del self.scheduled_events[event_id]
            self.logger.info(f"Cancelled scheduled event {event_id}")
            return True
        return False
    
    def get_current_time(self) -> GameTime:
        """Get current game time"""
        return self.game_time.copy()
    
    def get_current_season(self) -> Season:
        """Get current season"""
        return self.game_time.season
    
    def get_current_weather(self) -> WeatherCondition:
        """Get current weather conditions"""
        return self.weather_system.current_weather
    
    def get_weather_forecast(self, days: int = 7) -> List[WeatherCondition]:
        """Get weather forecast"""
        return self.weather_system.get_forecast(days)
    
    def get_planting_recommendations(self) -> List[str]:
        """Get crops recommended for current season"""
        return self.planting_windows.get(self.game_time.season, [])
    
    def is_optimal_planting_time(self, crop_type: str) -> bool:
        """Check if current season is optimal for planting crop"""
        return crop_type in self.planting_windows.get(self.game_time.season, [])
    
    def get_time_until_season(self, target_season: Season) -> int:
        """Get minutes until target season"""
        seasons = [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER]
        current_index = seasons.index(self.game_time.season)
        target_index = seasons.index(target_season)
        
        if target_index <= current_index:
            target_index += 4  # Next year
        
        seasons_to_wait = target_index - current_index
        days_per_season = self.config_manager.get('time.days_per_season', 90)
        
        # Calculate remaining days in current season
        remaining_days_current = days_per_season - self.game_time.days
        
        # Calculate total days
        total_days = remaining_days_current + (seasons_to_wait - 1) * days_per_season
        
        return total_days * 24 * 60  # Convert to minutes
    
    def _time_loop(self):
        """Main time update loop"""
        while self.running:
            try:
                current_real_time = time.time()
                
                if not self.paused:
                    # Calculate time delta
                    real_delta = current_real_time - self.last_update_time
                    
                    # Convert to game minutes
                    minutes_per_real_second = self.config_manager.get('time.minutes_per_real_second', 2)
                    game_minutes_delta = real_delta * minutes_per_real_second * self.time_scale
                    
                    if game_minutes_delta >= 1.0:  # Advance at least 1 game minute
                        old_time = self.game_time.copy()
                        
                        # Advance game time
                        self.game_time.total_minutes += int(game_minutes_delta)
                        self._update_derived_time()
                        
                        # Update weather
                        self.weather_system.update_weather(self.game_time)
                        
                        # Process scheduled events
                        self._process_scheduled_events()
                        
                        # Emit time events
                        self._emit_time_events(old_time)
                        
                        self.last_update_time = current_real_time
                
                # Sleep for update frequency
                time.sleep(self.update_frequency_ms / 1000.0)
                
            except Exception as e:
                self.logger.error(f"Time loop error: {e}")
                time.sleep(1.0)
    
    def _update_derived_time(self):
        """Update derived time values from total minutes"""
        total_minutes = self.game_time.total_minutes
        
        # Calculate minutes and hours
        self.game_time.minutes = total_minutes % 60
        total_hours = total_minutes // 60
        self.game_time.hours = total_hours % 24
        
        # Calculate days
        total_days = total_hours // 24
        days_per_season = self.config_manager.get('time.days_per_season', 90)
        
        # Calculate season and year
        season_index = (total_days // days_per_season) % 4
        seasons = [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER]
        self.game_time.season = seasons[season_index]
        
        # Calculate day within season
        self.game_time.days = (total_days % days_per_season) + 1
        
        # Calculate year
        self.game_time.year = (total_days // (days_per_season * 4)) + 1
        
        # Calculate day of year
        self.game_time.day_of_year = (total_days % (days_per_season * 4)) + 1
        
        # Calculate week of season
        self.game_time.week_of_season = ((self.game_time.days - 1) // 7) + 1
    
    def _process_scheduled_events(self):
        """Process and trigger scheduled events"""
        current_time = self.game_time.total_minutes
        triggered_events = []
        
        for event_id, event in self.scheduled_events.items():
            if event.should_trigger(current_time):
                # Trigger event
                self.event_system.publish(event.event_type, event.event_data, event.priority, 'time_system')
                
                if event.recurring:
                    # Reschedule recurring event
                    event.trigger_time = current_time + event.recurrence_interval
                else:
                    # Mark for removal
                    triggered_events.append(event_id)
        
        # Remove non-recurring triggered events
        for event_id in triggered_events:
            del self.scheduled_events[event_id]
    
    def _emit_time_events(self, old_time: GameTime):
        """Emit time-based events"""
        # Emit general time tick
        self.event_system.publish('time_tick', {
            'old_time': self._serialize_game_time(old_time),
            'new_time': self._serialize_game_time(),
            'weather': self._serialize_weather()
        }, EventPriority.HIGH, 'time_system')
        
        # Check for major time changes
        if old_time.hours != self.game_time.hours:
            self.event_system.publish('hour_changed', {
                'old_hour': old_time.hours,
                'new_hour': self.game_time.hours,
                'time_of_day': self.game_time.get_time_of_day().value
            }, EventPriority.NORMAL, 'time_system')
        
        if old_time.days != self.game_time.days:
            self.event_system.publish('day_changed', {
                'old_day': old_time.days,
                'new_day': self.game_time.days,
                'season': self.game_time.season.value
            }, EventPriority.HIGH, 'time_system')
        
        if old_time.season != self.game_time.season:
            self.event_system.publish('season_changed', {
                'old_season': old_time.season.value,
                'new_season': self.game_time.season.value,
                'year': self.game_time.year,
                'planting_recommendations': self.get_planting_recommendations()
            }, EventPriority.CRITICAL, 'time_system')
        
        if old_time.year != self.game_time.year:
            self.event_system.publish('year_changed', {
                'old_year': old_time.year,
                'new_year': self.game_time.year
            }, EventPriority.CRITICAL, 'time_system')
    
    def _serialize_game_time(self, game_time: GameTime = None) -> Dict[str, Any]:
        """Serialize game time to dictionary"""
        if game_time is None:
            game_time = self.game_time
            
        return {
            'minutes': game_time.minutes,
            'hours': game_time.hours,
            'days': game_time.days,
            'season': game_time.season.value,
            'year': game_time.year,
            'total_minutes': game_time.total_minutes,
            'time_string': game_time.get_time_string(),
            'date_string': game_time.get_date_string(),
            'time_of_day': game_time.get_time_of_day().value,
            'is_work_hours': game_time.is_work_hours()
        }
    
    def _serialize_weather(self) -> Dict[str, Any]:
        """Serialize weather condition to dictionary"""
        weather = self.weather_system.current_weather
        return {
            'weather_type': weather.weather_type.value,
            'description': weather.get_description(),
            'temperature_c': weather.temperature_c,
            'temperature_f': (weather.temperature_c * 9/5) + 32,
            'humidity_percent': weather.humidity_percent,
            'wind_speed_kmh': weather.wind_speed_kmh,
            'precipitation_mm': weather.precipitation_mm,
            'crop_growth_modifier': weather.crop_growth_modifier,
            'work_efficiency_modifier': weather.work_efficiency_modifier,
            'soil_moisture_change': weather.soil_moisture_change
        }


# Global time system instance
_global_time_system: Optional[TimeSystem] = None

def get_time_system() -> TimeSystem:
    """Get the global time system instance"""
    global _global_time_system
    if _global_time_system is None:
        _global_time_system = TimeSystem()
    return _global_time_system

def initialize_time_system() -> TimeSystem:
    """Initialize the global time system"""
    global _global_time_system
    _global_time_system = TimeSystem()
    return _global_time_system

# Convenience functions for easy access
def get_current_time() -> GameTime:
    """Get current game time"""
    return get_time_system().get_current_time()

def get_current_season() -> Season:
    """Get current season"""
    return get_time_system().get_current_season()

def get_current_weather() -> WeatherCondition:
    """Get current weather"""
    return get_time_system().get_current_weather()

def schedule_event(event_type: str, delay_minutes: int, event_data: Dict[str, Any] = None) -> str:
    """Schedule a time-based event"""
    return get_time_system().schedule_event(event_type, delay_minutes, event_data)

def set_time_scale(scale: float):
    """Set time acceleration"""
    get_time_system().set_time_scale(scale)

def pause_time():
    """Pause time progression"""
    get_time_system().pause()

def resume_time():
    """Resume time progression"""
    get_time_system().resume()