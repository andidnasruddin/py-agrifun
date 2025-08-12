"""
Weather Manager - Handles seasonal cycles and weather events for the farming simulation

This system manages realistic weather patterns that affect crop growth, planting decisions,
and farming strategy. It includes seasonal transitions, weather events, and mitigation systems
to add strategic depth and educational value about agricultural planning.

Key Features:
- Four-season cycle with different characteristics and crop suitability
- Dynamic weather events (rain, drought, frost, heat waves) affecting yields
- Seasonal planting windows for realistic crop selection
- Irrigation and weather mitigation systems for player strategy
- Educational agricultural principles integrated into gameplay

Design Goals:
- Realistic seasonal farming simulation with educational value
- Strategic depth through weather planning and mitigation
- Integration with existing crop growth and economic systems
- Progressive complexity that teaches agricultural principles

Usage:
    weather_manager = WeatherManager(event_system, time_manager)
    weather_manager.update()  # Called each game frame
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
from scripts.core.config import *


class Season(Enum):
    """Four agricultural seasons with different characteristics"""
    SPRING = "spring"  # Mild temperatures, good for planting most crops
    SUMMER = "summer"  # Hot temperatures, peak growing season
    FALL = "fall"      # Cooling temperatures, harvest season
    WINTER = "winter"  # Cold temperatures, limited growing options


class WeatherEvent(Enum):
    """Weather events that affect crop growth and yields"""
    CLEAR = "clear"        # Normal weather, no special effects
    RAIN = "rain"          # Beneficial for growth, +water to soil
    DROUGHT = "drought"    # Harmful, -water, slower growth
    FROST = "frost"        # Very harmful to sensitive crops
    HEAT_WAVE = "heat_wave"  # Stresses crops, increases water needs
    STORM = "storm"        # Mixed effects, can damage mature crops


@dataclass
class WeatherData:
    """Current weather state information"""
    season: Season              # Current season
    days_in_season: int        # Days elapsed in current season
    current_event: WeatherEvent # Active weather event
    event_duration: int        # Days remaining for current event
    temperature: float         # Average temperature (affects growth)
    rainfall: float           # Rainfall amount (affects soil water)
    season_progress: float    # Progress through current season (0.0-1.0)


class WeatherManager:
    """Manages seasonal cycles and weather events for farming simulation"""
    
    def __init__(self, event_system, time_manager):
        """Initialize weather manager with event system and time manager connections"""
        self.event_system = event_system  # Connect to game's event system
        self.time_manager = time_manager  # Connect to time management system
        
        # Current weather state
        self.current_season = Season.SPRING  # Start in spring for new farms
        self.days_in_season = 1             # Day count within current season
        self.current_weather_event = WeatherEvent.CLEAR  # Current weather condition
        self.weather_event_duration = 0     # Days remaining for current event
        
        # Season configuration - days per season and characteristics
        self.season_length = SEASON_LENGTH_DAYS  # From config (default: 30 days)
        self.weather_event_chance = WEATHER_EVENT_PROBABILITY  # Daily event chance
        
        # Temperature and precipitation tracking for crop effects
        self.base_temperature = 20.0  # Base temperature in Celsius
        self.daily_rainfall = 0.0     # Today's rainfall amount
        self.soil_moisture_modifier = 1.0  # Weather effect on soil water
        
        # Seasonal crop planting windows for educational realism
        self.crop_planting_seasons = {
            'corn': [Season.SPRING, Season.SUMMER],      # Warm weather crop
            'tomatoes': [Season.SPRING, Season.SUMMER],   # Heat-loving crop  
            'wheat': [Season.FALL, Season.WINTER, Season.SPRING]  # Cool weather crop
        }
        
        # Weather effects on crop growth rates and yields
        self.weather_growth_modifiers = {
            WeatherEvent.CLEAR: {'growth_rate': 1.0, 'yield_modifier': 1.0},
            WeatherEvent.RAIN: {'growth_rate': 1.2, 'yield_modifier': 1.1},
            WeatherEvent.DROUGHT: {'growth_rate': 0.7, 'yield_modifier': 0.8},
            WeatherEvent.FROST: {'growth_rate': 0.3, 'yield_modifier': 0.6},
            WeatherEvent.HEAT_WAVE: {'growth_rate': 0.8, 'yield_modifier': 0.9},
            WeatherEvent.STORM: {'growth_rate': 0.9, 'yield_modifier': 0.85}
        }
        
        # Irrigation system state (for weather mitigation)
        self.irrigation_systems = {}  # Dictionary of tile positions with irrigation
        self.irrigation_active = False  # Whether irrigation is currently running
        self.irrigation_water_cost = IRRIGATION_WATER_COST_PER_TILE  # Cost per tile per day
        
        # Subscribe to game events for weather integration
        self._setup_event_subscriptions()
        
        print(f"Weather Manager initialized - Starting in {self.current_season.value} season")
        
        # Emit initial weather state for UI
        self._emit_initial_weather_state()
    
    def _setup_event_subscriptions(self):
        """Subscribe to relevant game events for weather system integration"""
        # Time events for season transitions and weather updates
        self.event_system.subscribe('day_passed', self._handle_day_change)
        self.event_system.subscribe('hour_passed', self._handle_hour_change)
        
        # Crop events for weather effects on growth
        self.event_system.subscribe('crop_growth_update', self._handle_crop_growth_update)
        self.event_system.subscribe('plant_crop_requested', self._handle_crop_planting)
        
        # UI events for weather information display
        self.event_system.subscribe('get_weather_info_for_ui', self._handle_weather_info_request)
        self.event_system.subscribe('toggle_irrigation_requested', self._handle_irrigation_toggle)
        
        # Building events for irrigation system installation
        self.event_system.subscribe('irrigation_system_purchased', self._handle_irrigation_purchase)
    
    def update(self):
        """Update weather system each frame - called by game manager"""
        # Weather system updates are handled by day/hour events
        # No frame-by-frame updates needed currently
        pass
    
    def _handle_day_change(self, event_data):
        """Handle daily weather updates when day changes"""
        # Advance day count in current season
        self.days_in_season += 1
        
        # Check if season should transition (every SEASON_LENGTH_DAYS days)
        if self.days_in_season > self.season_length:
            self._transition_to_next_season()
        
        # Roll for new weather events
        self._check_for_weather_events()
        
        # Update weather event duration
        if self.weather_event_duration > 0:
            self.weather_event_duration -= 1
            if self.weather_event_duration <= 0:
                self._end_current_weather_event()
        
        # Emit weather update event for other systems
        self.event_system.emit('weather_updated', {
            'season': self.current_season.value,
            'weather_event': self.current_weather_event.value,
            'temperature': self._get_current_temperature(),
            'rainfall': self.daily_rainfall,
            'growth_modifier': self._get_growth_modifier(),
            'yield_modifier': self._get_yield_modifier()
        })
        
        # Handle irrigation costs during drought
        self._process_daily_irrigation_costs()
        
        # Emit enhanced day_passed event with weather data for crop growth
        self.event_system.emit('day_passed_with_weather', {
            'days': 1,
            'weather_growth_modifier': self._get_growth_modifier(),
            'weather_event': self.current_weather_event.value,
            'season': self.current_season.value,
            'temperature': self._get_current_temperature()
        })
    
    def _transition_to_next_season(self):
        """Transition to the next season in the annual cycle"""
        # Define season progression cycle
        season_order = [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER]
        current_index = season_order.index(self.current_season)
        next_index = (current_index + 1) % 4  # Cycle back to spring after winter
        
        # Update season state
        previous_season = self.current_season
        self.current_season = season_order[next_index]
        self.days_in_season = 1
        
        # Clear any inappropriate weather events for new season
        self._adjust_weather_for_season()
        
        # Emit season change event for UI and other systems
        self.event_system.emit('season_changed', {
            'previous_season': previous_season.value,
            'new_season': self.current_season.value,
            'seasonal_effects': self._get_seasonal_effects()
        })
        
        print(f"Season changed from {previous_season.value} to {self.current_season.value}")
    
    def _check_for_weather_events(self):
        """Check for random weather events each day"""
        # Only roll for new events if no event is currently active
        if self.current_weather_event == WeatherEvent.CLEAR:
            if random.random() < self.weather_event_chance:
                # Select weather event based on seasonal probability
                new_event = self._select_seasonal_weather_event()
                duration = self._get_weather_event_duration(new_event)
                
                self._start_weather_event(new_event, duration)
    
    def _select_seasonal_weather_event(self) -> WeatherEvent:
        """Select appropriate weather event based on current season"""
        # Define seasonal weather probabilities for realism
        seasonal_weather_chances = {
            Season.SPRING: {
                WeatherEvent.RAIN: 0.4,      # Spring rains common
                WeatherEvent.STORM: 0.2,     # Spring storms  
                WeatherEvent.FROST: 0.2,     # Late frost risk
                WeatherEvent.HEAT_WAVE: 0.1, # Rare early heat
                WeatherEvent.DROUGHT: 0.1    # Uncommon in spring
            },
            Season.SUMMER: {
                WeatherEvent.HEAT_WAVE: 0.3, # Summer heat waves
                WeatherEvent.DROUGHT: 0.3,   # Summer droughts
                WeatherEvent.STORM: 0.2,     # Summer thunderstorms
                WeatherEvent.RAIN: 0.2,      # Less frequent summer rain
                WeatherEvent.FROST: 0.0      # No frost in summer
            },
            Season.FALL: {
                WeatherEvent.RAIN: 0.3,      # Fall precipitation
                WeatherEvent.FROST: 0.3,     # Early frost risk
                WeatherEvent.STORM: 0.2,     # Fall weather systems
                WeatherEvent.DROUGHT: 0.1,   # Less common
                WeatherEvent.HEAT_WAVE: 0.1  # Indian summer heat
            },
            Season.WINTER: {
                WeatherEvent.FROST: 0.5,     # Frequent winter frost
                WeatherEvent.STORM: 0.2,     # Winter storms
                WeatherEvent.RAIN: 0.2,      # Winter precipitation
                WeatherEvent.DROUGHT: 0.1,   # Winter dry spells
                WeatherEvent.HEAT_WAVE: 0.0  # No heat waves in winter
            }
        }
        
        # Select event based on weighted random choice
        season_chances = seasonal_weather_chances[self.current_season]
        events = list(season_chances.keys())
        weights = list(season_chances.values())
        
        return random.choices(events, weights=weights)[0]
    
    def _get_weather_event_duration(self, event: WeatherEvent) -> int:
        """Get duration for weather event in days"""
        # Define typical durations for different weather events
        duration_ranges = {
            WeatherEvent.RAIN: (1, 3),      # 1-3 days of rain
            WeatherEvent.DROUGHT: (5, 10),  # 5-10 day drought periods
            WeatherEvent.FROST: (1, 2),     # 1-2 day frost events
            WeatherEvent.HEAT_WAVE: (3, 7), # 3-7 day heat waves
            WeatherEvent.STORM: (1, 2)      # 1-2 day storm systems
        }
        
        min_days, max_days = duration_ranges[event]
        return random.randint(min_days, max_days)
    
    def _start_weather_event(self, event: WeatherEvent, duration: int):
        """Start a new weather event with specified duration"""
        self.current_weather_event = event
        self.weather_event_duration = duration
        
        # Emit weather event started for UI notifications
        self.event_system.emit('weather_event_started', {
            'event_type': event.value,
            'duration': duration,
            'effects': self.weather_growth_modifiers[event]
        })
        
        print(f"Weather event started: {event.value} for {duration} days")
    
    def _end_current_weather_event(self):
        """End the current weather event and return to clear weather"""
        previous_event = self.current_weather_event
        self.current_weather_event = WeatherEvent.CLEAR
        self.weather_event_duration = 0
        
        # Emit weather event ended
        self.event_system.emit('weather_event_ended', {
            'previous_event': previous_event.value
        })
        
        print(f"Weather event ended: {previous_event.value}")
    
    def _handle_hour_change(self, event_data):
        """Handle hourly updates (currently unused, but subscribed for future features)"""
        # Could be used for hourly weather updates or irrigation management
        pass
    
    def _get_current_temperature(self) -> float:
        """Calculate current temperature based on season and weather"""
        # Base seasonal temperatures for realism
        seasonal_temps = {
            Season.SPRING: 15.0,  # Mild spring temperature
            Season.SUMMER: 25.0,  # Warm summer temperature  
            Season.FALL: 10.0,    # Cool fall temperature
            Season.WINTER: 5.0    # Cold winter temperature
        }
        
        base_temp = seasonal_temps[self.current_season]
        
        # Weather event temperature modifiers
        weather_temp_modifiers = {
            WeatherEvent.CLEAR: 0.0,
            WeatherEvent.RAIN: -3.0,     # Rain cools temperature
            WeatherEvent.DROUGHT: +2.0,  # Drought increases heat
            WeatherEvent.FROST: -10.0,   # Frost significantly colder
            WeatherEvent.HEAT_WAVE: +8.0, # Heat wave much hotter
            WeatherEvent.STORM: -2.0     # Storms slightly cooler
        }
        
        modifier = weather_temp_modifiers[self.current_weather_event]
        return base_temp + modifier
    
    def _get_growth_modifier(self) -> float:
        """Get current growth rate modifier based on weather"""
        base_modifier = self.weather_growth_modifiers[self.current_weather_event]['growth_rate']
        
        # Apply irrigation bonuses during drought
        if (self.current_weather_event == WeatherEvent.DROUGHT and 
            self.irrigation_active and len(self.irrigation_systems) > 0):
            # Irrigation partially mitigates drought effects
            base_modifier = min(1.0, base_modifier + 0.3)  # Boost growth but cap at normal
        
        return base_modifier
    
    def _get_yield_modifier(self) -> float:
        """Get current yield modifier based on weather"""
        return self.weather_growth_modifiers[self.current_weather_event]['yield_modifier']
    
    def _handle_weather_info_request(self, event_data):
        """Provide weather information for UI display"""
        weather_data = WeatherData(
            season=self.current_season,
            days_in_season=self.days_in_season,
            current_event=self.current_weather_event,
            event_duration=self.weather_event_duration,
            temperature=self._get_current_temperature(),
            rainfall=self.daily_rainfall,
            season_progress=self.days_in_season / self.season_length
        )
        
        # Emit weather info for UI
        self.event_system.emit('weather_info_updated', {
            'weather_data': weather_data,
            'seasonal_crop_info': self._get_seasonal_crop_recommendations()
        })
    
    def _get_seasonal_crop_recommendations(self) -> Dict:
        """Get crop recommendations for current season"""
        recommendations = {}
        
        for crop_type, suitable_seasons in self.crop_planting_seasons.items():
            if self.current_season in suitable_seasons:
                recommendations[crop_type] = 'optimal'
            else:
                recommendations[crop_type] = 'penalty'  # Growth penalty applies
        
        return recommendations
    
    def _handle_crop_growth_update(self, event_data):
        """Handle crop growth updates (for future weather interaction)"""
        # Could be used to apply weather effects during growth updates
        pass
    
    def _handle_crop_planting(self, event_data):
        """Check if crop can be planted in current season"""
        crop_type = event_data.get('crop_type', 'corn')
        
        # Check if crop is suitable for current season
        if crop_type in self.crop_planting_seasons:
            suitable_seasons = self.crop_planting_seasons[crop_type]
            if self.current_season not in suitable_seasons:
                # Emit warning about off-season planting
                self.event_system.emit('seasonal_planting_warning', {
                    'crop_type': crop_type,
                    'current_season': self.current_season.value,
                    'suitable_seasons': [s.value for s in suitable_seasons],
                    'growth_penalty': OFF_SEASON_PLANTING_PENALTY
                })
    
    def _handle_irrigation_toggle(self, event_data):
        """Handle irrigation system toggle requests"""
        requested_state = event_data.get('active', not self.irrigation_active)
        
        if len(self.irrigation_systems) == 0:
            print("No irrigation systems installed - cannot toggle irrigation")
            return
        
        self.irrigation_active = requested_state
        
        # Update all irrigation systems to match global state
        for tile_key, system in self.irrigation_systems.items():
            system['active'] = self.irrigation_active
        
        status = "activated" if self.irrigation_active else "deactivated"
        print(f"Irrigation systems {status} - {len(self.irrigation_systems)} tiles affected")
        
        # Emit status update for UI
        self.event_system.emit('irrigation_status_changed', {
            'active': self.irrigation_active,
            'total_tiles': len(self.irrigation_systems),
            'daily_cost_during_drought': len(self.irrigation_systems) * self.irrigation_water_cost
        })
    
    def _handle_irrigation_purchase(self, event_data):
        """Handle irrigation system purchases"""
        x = event_data.get('x')
        y = event_data.get('y')
        building_id = event_data.get('building_id')
        
        if x is not None and y is not None:
            # Add this tile to irrigation systems
            tile_key = f"{x},{y}"
            self.irrigation_systems[tile_key] = {
                'x': x,
                'y': y,
                'building_id': building_id,
                'active': True  # Start active by default
            }
            
            print(f"Weather Manager: Irrigation system registered at ({x}, {y})")
            
            # Emit update for UI
            self.event_system.emit('irrigation_coverage_updated', {
                'total_irrigated_tiles': len(self.irrigation_systems),
                'new_tile': {'x': x, 'y': y}
            })
    
    def get_weather_summary(self) -> Dict:
        """Get complete weather summary for display"""
        return {
            'season': self.current_season.value,
            'days_in_season': self.days_in_season,
            'season_progress': self.days_in_season / self.season_length,
            'weather_event': self.current_weather_event.value,
            'event_duration': self.weather_event_duration,
            'temperature': self._get_current_temperature(),
            'growth_modifier': self._get_growth_modifier(),
            'yield_modifier': self._get_yield_modifier(),
            'irrigation_active': self.irrigation_active,
            'seasonal_crops': self._get_seasonal_crop_recommendations()
        }
    
    def _process_daily_irrigation_costs(self):
        """Process daily irrigation costs during drought events"""
        # Only charge for irrigation during drought events
        if (self.current_weather_event != WeatherEvent.DROUGHT or 
            not self.irrigation_active or 
            len(self.irrigation_systems) == 0):
            return
        
        # Calculate total daily cost
        active_systems = sum(1 for system in self.irrigation_systems.values() 
                           if system.get('active', True))
        total_cost = active_systems * self.irrigation_water_cost
        
        if total_cost > 0:
            # Emit irrigation billing event for economy manager
            self.event_system.emit('irrigation_daily_bill', {
                'cost': total_cost,
                'irrigated_tiles': active_systems,
                'cost_per_tile': self.irrigation_water_cost,
                'weather_event': self.current_weather_event.value
            })
            
            print(f"Daily irrigation cost: ${total_cost} for {active_systems} irrigated tiles during drought")
    
    def _emit_initial_weather_state(self):
        """Emit initial weather state when game starts"""
        self.event_system.emit('weather_updated', {
            'season': self.current_season.value,
            'weather_event': self.current_weather_event.value,
            'temperature': self._get_current_temperature(),
            'rainfall': self.daily_rainfall,
            'growth_modifier': self._get_growth_modifier(),
            'yield_modifier': self._get_yield_modifier()
        })