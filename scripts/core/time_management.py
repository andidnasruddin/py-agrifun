"""
Advanced Time Management System - Temporal Coordination for AgriFun Agricultural Simulation

This module implements a comprehensive time management system that serves as the temporal
heartbeat of the agricultural simulation. It coordinates seasons, weather, employee schedules,
crop growth cycles, and market dynamics through precise time progression and event coordination.

Key Features:
- Realistic agricultural timing with seasonal cycles
- Dynamic weather integration affecting all farm operations
- Employee schedule coordination with work hours and breaks
- Market timing with seasonal price fluctuations
- Multi-speed time control for strategic gameplay
- Educational accuracy in agricultural timing and weather patterns

Core Systems:
- TimeManager: Central coordination and event integration
- GameClock: Precise time progression with acceleration controls
- WeatherSystem: Dynamic weather simulation with agricultural effects
- SeasonManager: Seasonal transitions and agricultural calendar
- ScheduleManager: Entity scheduling for time-based events

Time Architecture:
- Base Unit: Game minutes (1 real second = 1 game minute at 1x speed)
- Time Hierarchy: Minutes → Hours → Days → Seasons → Years
- Agricultural Focus: 90-day seasons, realistic crop timing
- Weather Integration: Dynamic weather affecting all operations
- Employee Coordination: 8-hour workdays with seasonal adjustments

Usage Example:
    # Initialize time management system
    time_manager = TimeManager()
    await time_manager.initialize()
    
    # Control time progression
    time_manager.set_time_scale(2.0)  # 2x speed
    time_manager.pause_time()
    time_manager.resume_time()
    
    # Get current time information
    game_time = time_manager.get_current_time()
    season = time_manager.get_current_season()
    weather = time_manager.get_current_weather()
    
    # Schedule time-based events
    time_manager.schedule_event('crop_harvest', days=7)
    time_manager.schedule_recurring_event('market_day', days=7)

Performance Features:
- Event batching for efficient processing
- Lazy evaluation for systems not requiring constant updates
- Weather pattern caching and pre-calculation
- Optimized scheduling for thousands of entities
- Frame-rate independent time progression
"""

import time
import math
import asyncio
import threading
from typing import Dict, List, Set, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import json
import random

# Import Phase 1 architecture systems
from .advanced_event_system import get_event_system, EventPriority
from .entity_component_system import get_entity_manager, Component
from .advanced_config_system import get_config_manager
from .state_management import get_state_manager


class Season(Enum):
    """Agricultural seasons with timing and characteristics"""
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"


class WeatherType(Enum):
    """Weather conditions affecting agricultural operations"""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    LIGHT_RAIN = "light_rain"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    STORM = "storm"
    DROUGHT = "drought"
    HEAT_WAVE = "heat_wave"
    COLD_SNAP = "cold_snap"


class TimeScale(Enum):
    """Time progression speeds for gameplay control"""
    PAUSED = 0.0
    NORMAL = 1.0
    FAST = 2.0
    FASTER = 4.0
    FASTEST = 8.0


@dataclass
class GameTime:
    """Comprehensive game time representation"""
    # Base time units
    total_minutes: int = 0  # Total game minutes since start
    
    # Derived time components
    minutes: int = 0        # Current minute (0-59)
    hours: int = 6          # Current hour (0-23, start at 6 AM)
    day: int = 1            # Day of season (1-90)
    season: Season = Season.SPRING
    year: int = 1           # Game year
    
    # Time progression state
    is_paused: bool = False
    time_scale: float = 1.0
    
    # Work schedule information
    is_work_hours: bool = True      # 6 AM - 2 PM default
    work_start_hour: int = 6
    work_end_hour: int = 14
    
    def update_from_total_minutes(self):
        """Update all time components from total minutes"""
        # Calculate base time components
        total_hours = self.total_minutes // 60
        self.minutes = self.total_minutes % 60
        
        # Calculate hours within day
        self.hours = total_hours % 24
        
        # Calculate days and seasons
        total_days = total_hours // 24
        self.day = (total_days % 90) + 1  # 90-day seasons
        
        # Calculate season and year
        season_index = (total_days // 90) % 4
        seasons = [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER]
        self.season = seasons[season_index]
        
        self.year = (total_days // 360) + 1  # 360-day years (4 seasons × 90 days)
        
        # Update work hours status
        self.is_work_hours = self.work_start_hour <= self.hours < self.work_end_hour
    
    def get_season_day(self) -> int:
        """Get current day within the season (1-90)"""
        return self.day
    
    def get_season_progress(self) -> float:
        """Get season progress as percentage (0.0-1.0)"""
        return (self.day - 1) / 90.0
    
    def get_year_day(self) -> int:
        """Get current day of the year (1-360)"""
        season_days = {
            Season.SPRING: 0,
            Season.SUMMER: 90,
            Season.FALL: 180,
            Season.WINTER: 270
        }
        return season_days[self.season] + self.day
    
    def get_time_string(self) -> str:
        """Get formatted time string for display"""
        am_pm = "AM" if self.hours < 12 else "PM"
        display_hour = self.hours if self.hours <= 12 else self.hours - 12
        if display_hour == 0:
            display_hour = 12
        
        return f"{display_hour}:{self.minutes:02d} {am_pm}"
    
    def get_date_string(self) -> str:
        """Get formatted date string for display"""
        return f"{self.season.value.title()} {self.day}, Year {self.year}"


@dataclass
class WeatherCondition:
    """Current weather state with agricultural effects"""
    weather_type: WeatherType = WeatherType.CLEAR
    temperature: float = 68.0           # Fahrenheit
    precipitation: float = 0.0          # Inches in last 24 hours
    humidity: float = 50.0              # Percentage
    wind_speed: float = 5.0             # MPH
    
    # Agricultural effect modifiers
    crop_growth_modifier: float = 1.0   # Multiplier for crop growth
    work_efficiency_modifier: float = 1.0  # Employee work efficiency
    soil_workability: bool = True       # Can work soil/plant crops
    
    # Weather forecast confidence
    forecast_confidence: float = 1.0    # 1.0 = current, decreases for future days
    
    def get_temperature_category(self) -> str:
        """Get temperature category for agricultural planning"""
        if self.temperature < 32:
            return "freezing"
        elif self.temperature < 50:
            return "cold"
        elif self.temperature < 70:
            return "cool"
        elif self.temperature < 85:
            return "warm"
        elif self.temperature < 95:
            return "hot"
        else:
            return "extreme_heat"
    
    def get_agricultural_impact(self) -> Dict[str, float]:
        """Get weather impact on agricultural operations"""
        return {
            'crop_growth': self.crop_growth_modifier,
            'work_efficiency': self.work_efficiency_modifier,
            'soil_workable': 1.0 if self.soil_workability else 0.0,
            'irrigation_need': max(0.0, 1.0 - (self.precipitation / 2.0)),
            'disease_risk': self.humidity / 100.0 * (1.0 + self.precipitation)
        }


@dataclass
class ScheduledEvent:
    """Scheduled event for time-based game mechanics"""
    event_id: str
    event_type: str
    trigger_time: int       # Game minutes when event should trigger
    callback: Optional[Callable] = None
    data: Dict[str, Any] = field(default_factory=dict)
    recurring: bool = False
    interval_minutes: int = 0
    priority: int = 100     # Lower = higher priority
    
    # Event state
    is_active: bool = True
    execution_count: int = 0
    last_executed: int = 0


class TimeManager:
    """Central time management system coordinating all temporal aspects"""
    
    def __init__(self):
        # Core systems integration
        self.event_system = get_event_system()
        self.entity_manager = get_entity_manager()
        self.config_manager = get_config_manager()
        self.state_manager = get_state_manager()
        
        # Time state
        self.game_time = GameTime()
        self.real_time_start = time.time()
        self.last_update_time = time.time()
        
        # Time control
        self.time_scale = TimeScale.NORMAL
        self.is_initialized = False
        
        # Scheduled events
        self.scheduled_events: Dict[str, ScheduledEvent] = {}
        self.event_queue: List[ScheduledEvent] = []
        self.next_event_id = 1
        
        # Performance optimization
        self.update_intervals = {
            'minute': 1,    # Every game minute
            'hour': 60,     # Every game hour
            'day': 1440,    # Every game day (24 * 60)
            'season': 129600  # Every game season (90 * 24 * 60)
        }
        self.last_interval_updates = {
            'minute': 0,
            'hour': 0,
            'day': 0,
            'season': 0
        }
        
        # Weather system integration
        self.current_weather = WeatherCondition()
        self.weather_forecast: List[WeatherCondition] = []
        
        # Agricultural calendar data
        self.seasonal_data = {}
        self.crop_calendars = {}
        
        # Threading for background processing
        self.background_thread: Optional[threading.Thread] = None
        self.background_running = False
        
        # Performance tracking
        self.update_performance = {
            'total_updates': 0,
            'total_time_ms': 0.0,
            'average_time_ms': 0.0,
            'events_processed': 0
        }
        
        self.logger = logging.getLogger('TimeManager')
    
    async def initialize(self) -> bool:
        """Initialize the time management system"""
        try:
            self.logger.info("Initializing Time Management System")
            
            # Load configuration settings
            await self._load_time_configuration()
            
            # Initialize seasonal and agricultural data
            await self._load_seasonal_data()
            
            # Initialize weather system
            await self._initialize_weather_system()
            
            # Set up default scheduled events
            await self._setup_default_events()
            
            # Start background processing
            self._start_background_processing()
            
            # Register for game events
            self._register_event_handlers()
            
            # Initialize time from save file or defaults
            await self._initialize_time_state()
            
            self.is_initialized = True
            
            # Emit initialization event
            self.event_system.emit('time_system_initialized', {
                'current_time': self.game_time.__dict__,
                'weather': self.current_weather.__dict__
            }, priority=EventPriority.HIGH)
            
            self.logger.info("Time Management System initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Time Management System: {e}")
            return False
    
    async def _load_time_configuration(self):
        """Load time-related configuration settings"""
        # Time progression settings
        self.game_time.work_start_hour = self.config_manager.get('time.work_start_hour', 6)
        self.game_time.work_end_hour = self.config_manager.get('time.work_end_hour', 14)
        
        # Season settings
        season_length = self.config_manager.get('time.season_length_days', 90)
        
        # Weather settings
        weather_change_probability = self.config_manager.get('weather.change_probability', 0.1)
        temperature_variation = self.config_manager.get('weather.temperature_variation', 10.0)
        
        self.logger.info(f"Time configuration loaded - Work hours: {self.game_time.work_start_hour}:00-{self.game_time.work_end_hour}:00")
    
    async def _load_seasonal_data(self):
        """Load seasonal and agricultural calendar data"""
        # Default seasonal data
        self.seasonal_data = {
            Season.SPRING: {
                'avg_temperature': 60.0,
                'temp_range': 20.0,
                'precipitation_probability': 0.4,
                'crop_growth_modifier': 1.2,
                'planting_bonus': 1.0,
                'description': 'Ideal planting season with moderate temperatures'
            },
            Season.SUMMER: {
                'avg_temperature': 80.0,
                'temp_range': 15.0,
                'precipitation_probability': 0.2,
                'crop_growth_modifier': 1.5,
                'planting_bonus': 0.8,
                'description': 'Hot growing season with rapid crop development'
            },
            Season.FALL: {
                'avg_temperature': 65.0,
                'temp_range': 25.0,
                'precipitation_probability': 0.3,
                'crop_growth_modifier': 1.0,
                'planting_bonus': 0.9,
                'description': 'Harvest season with cooling temperatures'
            },
            Season.WINTER: {
                'avg_temperature': 40.0,
                'temp_range': 20.0,
                'precipitation_probability': 0.5,
                'crop_growth_modifier': 0.3,
                'planting_bonus': 0.2,
                'description': 'Cold season with limited growing opportunities'
            }
        }
        
        # Agricultural calendar data
        self.crop_calendars = {
            'corn': {
                'planting_seasons': [Season.SPRING, Season.SUMMER],
                'growing_days': 75,
                'optimal_temperature': (65, 85),
                'water_needs': 'moderate'
            },
            'tomato': {
                'planting_seasons': [Season.SPRING, Season.SUMMER],
                'growing_days': 60,
                'optimal_temperature': (70, 85),
                'water_needs': 'high'
            },
            'wheat': {
                'planting_seasons': [Season.FALL, Season.SPRING],
                'growing_days': 120,
                'optimal_temperature': (50, 75),
                'water_needs': 'moderate'
            }
        }
    
    async def _initialize_weather_system(self):
        """Initialize dynamic weather system"""
        # Set initial weather based on season
        seasonal_weather = self.seasonal_data.get(self.game_time.season, {})
        
        self.current_weather = WeatherCondition(
            weather_type=WeatherType.CLEAR,
            temperature=seasonal_weather.get('avg_temperature', 68.0),
            precipitation=0.0,
            humidity=50.0,
            wind_speed=5.0
        )
        
        # Generate initial weather forecast
        await self._generate_weather_forecast()
        
        self.logger.info(f"Weather initialized: {self.current_weather.weather_type.value} at {self.current_weather.temperature}°F")
    
    async def _generate_weather_forecast(self, days: int = 7):
        """Generate weather forecast for planning"""
        self.weather_forecast = []
        
        current_weather = self.current_weather
        seasonal_data = self.seasonal_data.get(self.game_time.season, {})
        
        for day in range(days):
            # Create forecast with decreasing confidence
            confidence = max(0.3, 1.0 - (day * 0.15))
            
            # Generate weather for this day
            forecast_weather = WeatherCondition(
                weather_type=self._predict_weather_type(current_weather.weather_type, seasonal_data),
                temperature=self._predict_temperature(current_weather.temperature, seasonal_data),
                precipitation=self._predict_precipitation(seasonal_data),
                humidity=random.uniform(30, 80),
                wind_speed=random.uniform(2, 15),
                forecast_confidence=confidence
            )
            
            # Update agricultural modifiers
            self._calculate_weather_effects(forecast_weather)
            
            self.weather_forecast.append(forecast_weather)
            current_weather = forecast_weather
    
    def _predict_weather_type(self, current_type: WeatherType, seasonal_data: Dict) -> WeatherType:
        """Predict next weather type based on current conditions and season"""
        precipitation_prob = seasonal_data.get('precipitation_probability', 0.3)
        
        # Weather transition probabilities
        if current_type == WeatherType.CLEAR:
            if random.random() < precipitation_prob:
                return random.choice([WeatherType.PARTLY_CLOUDY, WeatherType.CLOUDY])
            return WeatherType.CLEAR
        elif current_type == WeatherType.PARTLY_CLOUDY:
            return random.choice([WeatherType.CLEAR, WeatherType.CLOUDY, WeatherType.LIGHT_RAIN])
        elif current_type == WeatherType.CLOUDY:
            return random.choice([WeatherType.PARTLY_CLOUDY, WeatherType.RAIN, WeatherType.LIGHT_RAIN])
        elif current_type in [WeatherType.LIGHT_RAIN, WeatherType.RAIN]:
            if random.random() < 0.3:
                return random.choice([WeatherType.CLOUDY, WeatherType.PARTLY_CLOUDY])
            return current_type
        else:
            return WeatherType.CLEAR
    
    def _predict_temperature(self, current_temp: float, seasonal_data: Dict) -> float:
        """Predict temperature with seasonal variation"""
        avg_temp = seasonal_data.get('avg_temperature', 68.0)
        temp_range = seasonal_data.get('temp_range', 15.0)
        
        # Gradual temperature change with some randomness
        target_temp = avg_temp + random.uniform(-temp_range/2, temp_range/2)
        temp_change = (target_temp - current_temp) * 0.3 + random.uniform(-5, 5)
        
        return max(10.0, min(120.0, current_temp + temp_change))
    
    def _predict_precipitation(self, seasonal_data: Dict) -> float:
        """Predict precipitation amount"""
        precip_prob = seasonal_data.get('precipitation_probability', 0.3)
        
        if random.random() < precip_prob:
            return random.uniform(0.1, 2.0)  # 0.1 to 2 inches
        return 0.0
    
    def _calculate_weather_effects(self, weather: WeatherCondition):
        """Calculate agricultural effects of weather conditions"""
        # Temperature effects
        if weather.temperature < 32:  # Freezing
            weather.crop_growth_modifier = 0.1
            weather.work_efficiency_modifier = 0.7
            weather.soil_workability = False
        elif weather.temperature < 50:  # Cold
            weather.crop_growth_modifier = 0.5
            weather.work_efficiency_modifier = 0.9
        elif weather.temperature > 95:  # Too hot
            weather.crop_growth_modifier = 0.8
            weather.work_efficiency_modifier = 0.8
        else:  # Optimal range
            weather.crop_growth_modifier = 1.0
            weather.work_efficiency_modifier = 1.0
        
        # Precipitation effects
        if weather.precipitation > 1.0:  # Heavy rain
            weather.soil_workability = False
            weather.work_efficiency_modifier *= 0.6
        elif weather.precipitation > 0.5:  # Moderate rain
            weather.work_efficiency_modifier *= 0.8
            weather.crop_growth_modifier *= 1.1  # Good for crops
        elif weather.precipitation == 0.0 and weather.weather_type == WeatherType.DROUGHT:
            weather.crop_growth_modifier *= 0.7  # Drought stress
        
        # Weather type specific effects
        if weather.weather_type == WeatherType.STORM:
            weather.work_efficiency_modifier *= 0.3
            weather.soil_workability = False
    
    async def _setup_default_events(self):
        """Set up default recurring events"""
        # Daily work start event
        self.schedule_recurring_event(
            'work_day_start',
            trigger_hour=self.game_time.work_start_hour,
            callback=self._on_work_day_start,
            interval_days=1
        )
        
        # Daily work end event
        self.schedule_recurring_event(
            'work_day_end',
            trigger_hour=self.game_time.work_end_hour,
            callback=self._on_work_day_end,
            interval_days=1
        )
        
        # Weather update events
        self.schedule_recurring_event(
            'weather_update',
            callback=self._update_weather,
            interval_hours=6  # Update weather 4 times per day
        )
        
        # Market day events (weekly)
        self.schedule_recurring_event(
            'market_day',
            trigger_hour=8,  # 8 AM market opening
            callback=self._on_market_day,
            interval_days=7
        )
    
    def _start_background_processing(self):
        """Start background thread for time processing"""
        self.background_running = True
        self.background_thread = threading.Thread(
            target=self._background_update_loop,
            daemon=True
        )
        self.background_thread.start()
        self.logger.info("Background time processing started")
    
    def _background_update_loop(self):
        """Background loop for time updates"""
        while self.background_running:
            try:
                if not self.game_time.is_paused and self.is_initialized:
                    self._process_time_advancement()
                
                # Sleep for frame-rate independent processing
                time.sleep(0.016)  # ~60 FPS
                
            except Exception as e:
                self.logger.error(f"Background time processing error: {e}")
    
    def _process_time_advancement(self):
        """Process time advancement and trigger events"""
        current_real_time = time.time()
        delta_real_time = current_real_time - self.last_update_time
        
        # Calculate game time advancement
        game_minutes_elapsed = delta_real_time * self.time_scale.value
        
        if game_minutes_elapsed >= 1.0:  # Advance at least 1 game minute
            # Update game time
            minutes_to_advance = int(game_minutes_elapsed)
            self.game_time.total_minutes += minutes_to_advance
            self.game_time.update_from_total_minutes()
            
            # Process scheduled events
            self._process_scheduled_events()
            
            # Check for interval-based updates
            self._check_interval_updates()
            
            # Emit time advancement event
            self.event_system.emit('time_advanced', {
                'game_time': self.game_time.__dict__,
                'minutes_advanced': minutes_to_advance,
                'current_weather': self.current_weather.__dict__
            }, priority=EventPriority.NORMAL)
            
            self.last_update_time = current_real_time
            
            # Update performance tracking
            self.update_performance['total_updates'] += 1
    
    def _process_scheduled_events(self):
        """Process and execute scheduled events"""
        current_time = self.game_time.total_minutes
        
        # Sort events by trigger time and priority
        ready_events = [
            event for event in self.scheduled_events.values()
            if event.is_active and event.trigger_time <= current_time
        ]
        
        ready_events.sort(key=lambda e: (e.trigger_time, e.priority))
        
        for event in ready_events:
            try:
                # Execute event callback
                if event.callback:
                    event.callback(event.data)
                
                # Emit event
                self.event_system.emit(f'scheduled_{event.event_type}', {
                    'event_id': event.event_id,
                    'event_type': event.event_type,
                    'data': event.data,
                    'execution_count': event.execution_count + 1
                }, priority=EventPriority.NORMAL)
                
                # Update event state
                event.execution_count += 1
                event.last_executed = current_time
                
                # Handle recurring events
                if event.recurring and event.interval_minutes > 0:
                    event.trigger_time = current_time + event.interval_minutes
                else:
                    # Remove one-time events
                    event.is_active = False
                    del self.scheduled_events[event.event_id]
                
                self.update_performance['events_processed'] += 1
                
            except Exception as e:
                self.logger.error(f"Error executing scheduled event {event.event_id}: {e}")
    
    def _check_interval_updates(self):
        """Check and trigger interval-based updates"""
        current_time = self.game_time.total_minutes
        
        for interval_name, interval_minutes in self.update_intervals.items():
            last_update = self.last_interval_updates[interval_name]
            
            if current_time - last_update >= interval_minutes:
                self._trigger_interval_update(interval_name)
                self.last_interval_updates[interval_name] = current_time
    
    def _trigger_interval_update(self, interval_name: str):
        """Trigger interval-based system updates"""
        if interval_name == 'minute':
            self.event_system.emit('minute_passed', {
                'game_time': self.game_time.__dict__
            }, priority=EventPriority.LOW)
            
        elif interval_name == 'hour':
            self.event_system.emit('hour_passed', {
                'game_time': self.game_time.__dict__,
                'is_work_hours': self.game_time.is_work_hours
            }, priority=EventPriority.NORMAL)
            
        elif interval_name == 'day':
            self.event_system.emit('day_passed', {
                'game_time': self.game_time.__dict__,
                'season': self.game_time.season.value,
                'weather': self.current_weather.__dict__
            }, priority=EventPriority.HIGH)
            
        elif interval_name == 'season':
            self.event_system.emit('season_changed', {
                'new_season': self.game_time.season.value,
                'year': self.game_time.year,
                'seasonal_data': self.seasonal_data.get(self.game_time.season, {})
            }, priority=EventPriority.CRITICAL)
    
    def _register_event_handlers(self):
        """Register event handlers for time system"""
        self.event_system.subscribe('game_paused', self._on_game_paused)
        self.event_system.subscribe('game_resumed', self._on_game_resumed)
        self.event_system.subscribe('time_scale_changed', self._on_time_scale_changed)
    
    async def _initialize_time_state(self):
        """Initialize time state from save or defaults"""
        # For now, use defaults - will integrate with save system later
        self.game_time = GameTime()
        self.game_time.update_from_total_minutes()
        
        self.logger.info(f"Time state initialized: {self.game_time.get_date_string()} at {self.game_time.get_time_string()}")
    
    # Event handlers
    def _on_work_day_start(self, data: Dict[str, Any]):
        """Handle work day start event"""
        self.logger.info("Work day started")
        self.event_system.emit('work_day_started', {
            'game_time': self.game_time.__dict__,
            'weather': self.current_weather.__dict__
        }, priority=EventPriority.HIGH)
    
    def _on_work_day_end(self, data: Dict[str, Any]):
        """Handle work day end event"""
        self.logger.info("Work day ended")
        self.event_system.emit('work_day_ended', {
            'game_time': self.game_time.__dict__
        }, priority=EventPriority.HIGH)
    
    def _update_weather(self, data: Dict[str, Any]):
        """Update weather conditions"""
        if self.weather_forecast:
            # Move to next forecasted weather
            self.current_weather = self.weather_forecast.pop(0)
            
            # Generate new forecast day
            asyncio.create_task(self._generate_weather_forecast(1))
        
        self.event_system.emit('weather_updated', {
            'weather': self.current_weather.__dict__,
            'agricultural_impact': self.current_weather.get_agricultural_impact(),
            'forecast': [w.__dict__ for w in self.weather_forecast[:3]]  # 3-day forecast
        }, priority=EventPriority.HIGH)
    
    def _on_market_day(self, data: Dict[str, Any]):
        """Handle market day event"""
        self.logger.info("Market day - prices updated")
        self.event_system.emit('market_day', {
            'game_time': self.game_time.__dict__,
            'season': self.game_time.season.value
        }, priority=EventPriority.HIGH)
    
    def _on_game_paused(self, event_data: Dict[str, Any]):
        """Handle game pause event"""
        self.pause_time()
    
    def _on_game_resumed(self, event_data: Dict[str, Any]):
        """Handle game resume event"""
        self.resume_time()
    
    def _on_time_scale_changed(self, event_data: Dict[str, Any]):
        """Handle time scale change event"""
        new_scale = event_data.get('time_scale', 1.0)
        self.set_time_scale(new_scale)
    
    # Public API methods
    def set_time_scale(self, scale: float):
        """Set time progression scale"""
        try:
            self.time_scale = TimeScale(scale)
            self.game_time.time_scale = scale
            
            self.event_system.emit('time_scale_set', {
                'time_scale': scale,
                'scale_name': self.time_scale.name
            }, priority=EventPriority.NORMAL)
            
        except ValueError:
            self.logger.warning(f"Invalid time scale: {scale}")
    
    def pause_time(self):
        """Pause time progression"""
        self.game_time.is_paused = True
        self.time_scale = TimeScale.PAUSED
        
        self.event_system.emit('time_paused', {
            'game_time': self.game_time.__dict__
        }, priority=EventPriority.HIGH)
    
    def resume_time(self):
        """Resume time progression"""
        self.game_time.is_paused = False
        self.time_scale = TimeScale.NORMAL
        self.last_update_time = time.time()  # Reset to prevent time jump
        
        self.event_system.emit('time_resumed', {
            'game_time': self.game_time.__dict__
        }, priority=EventPriority.HIGH)
    
    def get_current_time(self) -> GameTime:
        """Get current game time"""
        return self.game_time
    
    def get_current_season(self) -> Season:
        """Get current season"""
        return self.game_time.season
    
    def get_current_weather(self) -> WeatherCondition:
        """Get current weather conditions"""
        return self.current_weather
    
    def get_weather_forecast(self, days: int = 7) -> List[WeatherCondition]:
        """Get weather forecast"""
        return self.weather_forecast[:days]
    
    def schedule_event(self, event_type: str, callback: Optional[Callable] = None, 
                      data: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """Schedule a one-time event"""
        # Calculate trigger time
        trigger_time = self.game_time.total_minutes
        
        if 'minutes' in kwargs:
            trigger_time += kwargs['minutes']
        if 'hours' in kwargs:
            trigger_time += kwargs['hours'] * 60
        if 'days' in kwargs:
            trigger_time += kwargs['days'] * 1440
        
        # Create event
        event_id = f"{event_type}_{self.next_event_id}"
        self.next_event_id += 1
        
        event = ScheduledEvent(
            event_id=event_id,
            event_type=event_type,
            trigger_time=trigger_time,
            callback=callback,
            data=data or {},
            recurring=False,
            priority=kwargs.get('priority', 100)
        )
        
        self.scheduled_events[event_id] = event
        return event_id
    
    def schedule_recurring_event(self, event_type: str, callback: Optional[Callable] = None,
                               data: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """Schedule a recurring event"""
        # Calculate trigger time and interval
        trigger_time = self.game_time.total_minutes
        interval_minutes = 0
        
        if 'trigger_hour' in kwargs:
            # Schedule for specific hour of day
            target_hour = kwargs['trigger_hour']
            current_hour = self.game_time.hours
            
            if target_hour > current_hour:
                hours_until = target_hour - current_hour
            else:
                hours_until = (24 - current_hour) + target_hour
            
            trigger_time += hours_until * 60
        
        if 'interval_minutes' in kwargs:
            interval_minutes = kwargs['interval_minutes']
        if 'interval_hours' in kwargs:
            interval_minutes = kwargs['interval_hours'] * 60
        if 'interval_days' in kwargs:
            interval_minutes = kwargs['interval_days'] * 1440
        
        # Create recurring event
        event_id = f"{event_type}_recurring_{self.next_event_id}"
        self.next_event_id += 1
        
        event = ScheduledEvent(
            event_id=event_id,
            event_type=event_type,
            trigger_time=trigger_time,
            callback=callback,
            data=data or {},
            recurring=True,
            interval_minutes=interval_minutes,
            priority=kwargs.get('priority', 100)
        )
        
        self.scheduled_events[event_id] = event
        return event_id
    
    def cancel_event(self, event_id: str) -> bool:
        """Cancel a scheduled event"""
        if event_id in self.scheduled_events:
            self.scheduled_events[event_id].is_active = False
            del self.scheduled_events[event_id]
            return True
        return False
    
    def get_seasonal_data(self, season: Optional[Season] = None) -> Dict[str, Any]:
        """Get seasonal data for agricultural planning"""
        target_season = season or self.game_time.season
        return self.seasonal_data.get(target_season, {})
    
    def get_crop_calendar(self, crop_type: str) -> Dict[str, Any]:
        """Get agricultural calendar for specific crop"""
        return self.crop_calendars.get(crop_type, {})
    
    def is_optimal_planting_season(self, crop_type: str) -> bool:
        """Check if current season is optimal for planting specific crop"""
        crop_data = self.get_crop_calendar(crop_type)
        planting_seasons = crop_data.get('planting_seasons', [])
        return self.game_time.season in planting_seasons
    
    def get_time_until_season(self, target_season: Season) -> int:
        """Get days until target season"""
        seasons = [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER]
        current_index = seasons.index(self.game_time.season)
        target_index = seasons.index(target_season)
        
        if target_index > current_index:
            seasons_until = target_index - current_index
        else:
            seasons_until = (4 - current_index) + target_index
        
        days_remaining_in_season = 90 - self.game_time.day
        total_days = days_remaining_in_season + ((seasons_until - 1) * 90)
        
        return total_days
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get time system performance statistics"""
        return {
            'current_time': self.game_time.__dict__,
            'time_scale': self.time_scale.value,
            'scheduled_events': len(self.scheduled_events),
            'performance': self.update_performance,
            'weather': self.current_weather.__dict__,
            'seasonal_data': self.seasonal_data.get(self.game_time.season, {})
        }
    
    def shutdown(self):
        """Shutdown time management system"""
        self.logger.info("Shutting down Time Management System")
        
        # Stop background processing
        self.background_running = False
        
        if self.background_thread:
            self.background_thread.join(timeout=1.0)
        
        # Clear scheduled events
        self.scheduled_events.clear()
        
        # Emit shutdown event
        self.event_system.emit('time_system_shutdown', {
            'final_time': self.game_time.__dict__,
            'total_updates': self.update_performance['total_updates']
        }, priority=EventPriority.HIGH)


# Global time manager instance
_global_time_manager: Optional[TimeManager] = None

def get_time_manager() -> TimeManager:
    """Get the global time manager instance"""
    global _global_time_manager
    if _global_time_manager is None:
        _global_time_manager = TimeManager()
    return _global_time_manager

def initialize_time_manager() -> TimeManager:
    """Initialize the global time manager"""
    global _global_time_manager
    _global_time_manager = TimeManager()
    return _global_time_manager

# Convenience functions for common time operations
def get_current_game_time() -> GameTime:
    """Get current game time"""
    return get_time_manager().get_current_time()

def get_current_season() -> Season:
    """Get current season"""
    return get_time_manager().get_current_season()

def get_current_weather() -> WeatherCondition:
    """Get current weather"""
    return get_time_manager().get_current_weather()

def schedule_event(event_type: str, **kwargs) -> str:
    """Schedule a time-based event"""
    return get_time_manager().schedule_event(event_type, **kwargs)

def is_work_hours() -> bool:
    """Check if it's currently work hours"""
    return get_time_manager().get_current_time().is_work_hours