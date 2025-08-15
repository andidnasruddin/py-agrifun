"""
Temporal Components - Time-Based ECS Components for AgriFun Agricultural Simulation

This module defines Entity-Component-System components that handle time-based behaviors,
scheduling, and temporal effects for entities in the agricultural simulation. These
components integrate with the Time Management System to provide realistic timing
and scheduling for crops, employees, buildings, and other game entities.

Key Components:
- TemporalComponent: Base time tracking for all entities
- ScheduleComponent: Work schedules and time-based routines
- GrowthComponent: Time-based growth and development
- WeatherEffectComponent: How weather affects entities over time
- SeasonalComponent: Seasonal behavior modifications
- AgingComponent: Entity aging and lifespan management
- TimerComponent: Countdown timers for temporary effects

Integration Features:
- Seamless integration with Time Management System
- Event-driven temporal updates
- Performance-optimized time calculations
- Configurable timing parameters
- Save/load compatible time state

Usage Example:
    # Add temporal tracking to an entity
    entity_manager.add_component(entity_id, 'temporal', {
        'created_at': current_game_time.total_minutes,
        'last_update': current_game_time.total_minutes
    })
    
    # Add growth component to a crop
    entity_manager.add_component(crop_id, 'growth', {
        'growth_stage': 'seed',
        'growth_rate': 1.0,
        'days_to_mature': 75
    })
    
    # Add schedule to an employee
    entity_manager.add_component(employee_id, 'schedule', {
        'work_start_hour': 6,
        'work_end_hour': 14,
        'break_times': [720, 840]  # Minutes from midnight
    })

Performance Features:
- Efficient time-based component updates
- Batch processing for similar components
- Lazy evaluation for inactive entities
- Memory-efficient temporal state storage
"""

import time
import math
from typing import Dict, List, Set, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

# Import Phase 1 architecture
from scripts.core.entity_component_system import Component
from scripts.core.time_management import Season, WeatherType


class GrowthStage(Enum):
    """Growth stages for living entities"""
    SEED = "seed"
    SPROUT = "sprout"
    SEEDLING = "seedling"
    JUVENILE = "juvenile"
    YOUNG = "young"
    MATURE = "mature"
    ADULT = "adult"
    ELDER = "elder"
    DECLINING = "declining"


class ScheduleState(Enum):
    """Current schedule state for entities"""
    IDLE = "idle"
    WORKING = "working"
    BREAK = "break"
    LUNCH = "lunch"
    OFF_DUTY = "off_duty"
    SICK = "sick"
    VACATION = "vacation"


@dataclass
class TemporalComponent(Component):
    """Base temporal component for time tracking"""
    component_type: str = "temporal"
    
    # Core timing
    created_at: int = 0              # Game minutes when entity was created
    last_update: int = 0             # Last time component was updated
    update_interval: int = 60        # How often to update (game minutes)
    
    # Age tracking
    age_in_minutes: int = 0          # Total age since creation
    age_in_days: float = 0.0         # Age in game days for display
    
    # Activity state
    is_active: bool = True           # Whether entity processes time
    is_paused: bool = False          # Temporary pause state
    
    # Performance optimization
    needs_frequent_updates: bool = False  # High-frequency update flag
    last_significant_change: int = 0      # Last major state change
    
    def update_age(self, current_time: int):
        """Update age calculations"""
        if self.is_active and not self.is_paused:
            self.age_in_minutes = current_time - self.created_at
            self.age_in_days = self.age_in_minutes / 1440.0  # 1440 minutes per day
            self.last_update = current_time
    
    def get_age_string(self) -> str:
        """Get formatted age string"""
        if self.age_in_days < 1:
            hours = self.age_in_minutes // 60
            return f"{hours}h"
        elif self.age_in_days < 30:
            return f"{self.age_in_days:.1f} days"
        elif self.age_in_days < 360:
            months = self.age_in_days / 30
            return f"{months:.1f} months"
        else:
            years = self.age_in_days / 360
            return f"{years:.1f} years"
    
    def should_update(self, current_time: int) -> bool:
        """Check if component needs updating"""
        if not self.is_active or self.is_paused:
            return False
        
        time_since_update = current_time - self.last_update
        
        if self.needs_frequent_updates:
            return time_since_update >= 1  # Update every minute
        else:
            return time_since_update >= self.update_interval


@dataclass
class ScheduleComponent(Component):
    """Work schedule and routine management"""
    component_type: str = "schedule"
    
    # Work schedule
    work_start_hour: int = 6         # Work start time (0-23)
    work_end_hour: int = 14          # Work end time (0-23)
    work_days_per_week: int = 6      # Days worked per week
    
    # Break schedule
    break_times: List[int] = field(default_factory=list)  # Break times in minutes from midnight
    break_durations: List[int] = field(default_factory=list)  # Break durations in minutes
    lunch_time: int = 720            # Lunch time (12:00 PM = 720 minutes)
    lunch_duration: int = 60         # Lunch break duration
    
    # Current state
    current_state: ScheduleState = ScheduleState.IDLE
    state_start_time: int = 0        # When current state started
    next_state_change: int = 0       # When next state change occurs
    
    # Efficiency modifiers
    energy_level: float = 1.0        # Current energy (0.0 - 1.0)
    fatigue_rate: float = 0.02       # How quickly energy depletes
    rest_rate: float = 0.1           # How quickly energy recovers
    
    # Seasonal adjustments
    seasonal_hour_modifier: Dict[Season, int] = field(default_factory=dict)
    weather_efficiency_modifier: float = 1.0
    
    # Performance tracking
    hours_worked_today: float = 0.0
    hours_worked_this_week: float = 0.0
    efficiency_rating: float = 1.0
    
    def __post_init__(self):
        """Initialize default break schedule"""
        if not self.break_times:
            # Default breaks: 9:30 AM and 3:30 PM
            self.break_times = [570, 930]  # 9:30 AM, 3:30 PM in minutes
            self.break_durations = [15, 15]  # 15-minute breaks
        
        # Initialize seasonal adjustments
        if not self.seasonal_hour_modifier:
            self.seasonal_hour_modifier = {
                Season.SPRING: 0,    # Normal hours
                Season.SUMMER: 1,    # Start 1 hour earlier (5 AM)
                Season.FALL: 0,      # Normal hours
                Season.WINTER: -1    # Start 1 hour later (7 AM)
            }
    
    def get_adjusted_work_hours(self, season: Season) -> tuple[int, int]:
        """Get work hours adjusted for season"""
        modifier = self.seasonal_hour_modifier.get(season, 0)
        start_hour = max(0, min(23, self.work_start_hour + modifier))
        end_hour = max(0, min(23, self.work_end_hour + modifier))
        return start_hour, end_hour
    
    def is_work_time(self, current_hour: int, current_season: Season) -> bool:
        """Check if current time is work time"""
        start_hour, end_hour = self.get_adjusted_work_hours(current_season)
        
        if start_hour <= end_hour:
            return start_hour <= current_hour < end_hour
        else:  # Crosses midnight
            return current_hour >= start_hour or current_hour < end_hour
    
    def is_break_time(self, current_minutes: int) -> bool:
        """Check if current time is break time"""
        for i, break_time in enumerate(self.break_times):
            break_end = break_time + self.break_durations[i]
            if break_time <= current_minutes < break_end:
                return True
        
        # Check lunch time
        lunch_end = self.lunch_time + self.lunch_duration
        if self.lunch_time <= current_minutes < lunch_end:
            return True
        
        return False
    
    def update_energy(self, minutes_elapsed: int, is_working: bool):
        """Update energy level based on activity"""
        hours_elapsed = minutes_elapsed / 60.0
        
        if is_working:
            # Lose energy while working
            energy_loss = self.fatigue_rate * hours_elapsed * self.weather_efficiency_modifier
            self.energy_level = max(0.0, self.energy_level - energy_loss)
            self.hours_worked_today += hours_elapsed
        else:
            # Recover energy while resting
            energy_gain = self.rest_rate * hours_elapsed
            self.energy_level = min(1.0, self.energy_level + energy_gain)
    
    def get_current_efficiency(self) -> float:
        """Get current work efficiency based on energy and conditions"""
        base_efficiency = self.energy_level
        
        # Apply weather modifier
        weather_adjusted = base_efficiency * self.weather_efficiency_modifier
        
        # Apply fatigue penalty for overwork
        if self.hours_worked_today > 8:
            overtime_penalty = 1.0 - ((self.hours_worked_today - 8) * 0.1)
            weather_adjusted *= max(0.3, overtime_penalty)
        
        return max(0.1, min(1.0, weather_adjusted))
    
    def reset_daily_tracking(self):
        """Reset daily work tracking"""
        self.hours_worked_this_week += self.hours_worked_today
        self.hours_worked_today = 0.0
        
        # Weekly reset
        if self.hours_worked_this_week >= self.work_days_per_week * 8:
            self.hours_worked_this_week = 0.0


@dataclass
class GrowthComponent(Component):
    """Time-based growth and development"""
    component_type: str = "growth"
    
    # Growth configuration
    growth_stage: GrowthStage = GrowthStage.SEED
    growth_rate: float = 1.0         # Base growth rate multiplier
    days_to_mature: int = 75         # Days from seed to mature
    
    # Growth progress
    growth_progress: float = 0.0     # Progress within current stage (0.0-1.0)
    total_growth_progress: float = 0.0  # Overall progress to maturity (0.0-1.0)
    
    # Growth stages configuration
    stage_durations: Dict[GrowthStage, float] = field(default_factory=dict)
    stage_requirements: Dict[GrowthStage, Dict[str, Any]] = field(default_factory=dict)
    
    # Environmental effects
    temperature_sensitivity: float = 1.0    # How much temperature affects growth
    water_sensitivity: float = 1.0          # How much water affects growth
    light_sensitivity: float = 1.0          # How much light affects growth
    
    # Current modifiers
    current_growth_modifier: float = 1.0    # Combined environmental modifier
    optimal_temperature_range: tuple[float, float] = (65.0, 85.0)
    
    # Growth events
    last_stage_change: int = 0              # When last stage change occurred
    growth_milestones: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize growth stage configuration"""
        if not self.stage_durations:
            # Default stage durations as percentage of total growth time
            total_days = self.days_to_mature
            self.stage_durations = {
                GrowthStage.SEED: total_days * 0.05,      # 5% - Germination
                GrowthStage.SPROUT: total_days * 0.10,    # 10% - First leaves
                GrowthStage.SEEDLING: total_days * 0.15,  # 15% - Establishment
                GrowthStage.JUVENILE: total_days * 0.25,  # 25% - Rapid growth
                GrowthStage.YOUNG: total_days * 0.20,     # 20% - Development
                GrowthStage.MATURE: total_days * 0.25,    # 25% - Full size
            }
        
        if not self.stage_requirements:
            # Default requirements for each stage
            self.stage_requirements = {
                GrowthStage.SEED: {
                    'min_temperature': 45.0,
                    'min_water': 0.3,
                    'min_light': 0.2
                },
                GrowthStage.SPROUT: {
                    'min_temperature': 50.0,
                    'min_water': 0.4,
                    'min_light': 0.4
                },
                GrowthStage.SEEDLING: {
                    'min_temperature': 55.0,
                    'min_water': 0.5,
                    'min_light': 0.6
                },
                GrowthStage.JUVENILE: {
                    'min_temperature': 60.0,
                    'min_water': 0.6,
                    'min_light': 0.8
                },
                GrowthStage.YOUNG: {
                    'min_temperature': 65.0,
                    'min_water': 0.7,
                    'min_light': 0.9
                },
                GrowthStage.MATURE: {
                    'min_temperature': 60.0,
                    'min_water': 0.6,
                    'min_light': 0.8
                }
            }
    
    def update_growth(self, minutes_elapsed: int, temperature: float, 
                     water_level: float, light_level: float):
        """Update growth progress based on environmental conditions"""
        # Calculate environmental modifiers
        temp_modifier = self._calculate_temperature_modifier(temperature)
        water_modifier = self._calculate_water_modifier(water_level)
        light_modifier = self._calculate_light_modifier(light_level)
        
        # Combined growth modifier
        self.current_growth_modifier = temp_modifier * water_modifier * light_modifier * self.growth_rate
        
        # Check if current stage requirements are met
        current_requirements = self.stage_requirements.get(self.growth_stage, {})
        requirements_met = (
            temperature >= current_requirements.get('min_temperature', 0) and
            water_level >= current_requirements.get('min_water', 0) and
            light_level >= current_requirements.get('min_light', 0)
        )
        
        if requirements_met and self.current_growth_modifier > 0:
            # Apply growth
            days_elapsed = minutes_elapsed / 1440.0
            growth_increment = (days_elapsed / self.days_to_mature) * self.current_growth_modifier
            
            self.total_growth_progress = min(1.0, self.total_growth_progress + growth_increment)
            
            # Check for stage advancement
            self._check_stage_advancement()
    
    def _calculate_temperature_modifier(self, temperature: float) -> float:
        """Calculate temperature effect on growth"""
        min_temp, max_temp = self.optimal_temperature_range
        
        if min_temp <= temperature <= max_temp:
            return 1.0  # Optimal temperature
        elif temperature < min_temp:
            # Cold penalty
            temp_diff = min_temp - temperature
            return max(0.0, 1.0 - (temp_diff * 0.02 * self.temperature_sensitivity))
        else:
            # Heat penalty
            temp_diff = temperature - max_temp
            return max(0.0, 1.0 - (temp_diff * 0.03 * self.temperature_sensitivity))
    
    def _calculate_water_modifier(self, water_level: float) -> float:
        """Calculate water effect on growth"""
        if water_level >= 0.7:
            return 1.0  # Optimal water
        elif water_level >= 0.3:
            return 0.5 + (water_level - 0.3) * 1.25  # Reduced growth
        else:
            return max(0.0, water_level * 1.67 * (1.0 - self.water_sensitivity))
    
    def _calculate_light_modifier(self, light_level: float) -> float:
        """Calculate light effect on growth"""
        if light_level >= 0.8:
            return 1.0  # Optimal light
        elif light_level >= 0.4:
            return 0.6 + (light_level - 0.4) * 1.0  # Reduced growth
        else:
            return max(0.0, light_level * 1.5 * (1.0 - self.light_sensitivity))
    
    def _check_stage_advancement(self):
        """Check if entity should advance to next growth stage"""
        stage_order = [
            GrowthStage.SEED, GrowthStage.SPROUT, GrowthStage.SEEDLING,
            GrowthStage.JUVENILE, GrowthStage.YOUNG, GrowthStage.MATURE
        ]
        
        current_index = stage_order.index(self.growth_stage)
        
        # Calculate cumulative progress needed for current stage
        cumulative_duration = 0
        for i in range(current_index + 1):
            cumulative_duration += self.stage_durations.get(stage_order[i], 0)
        
        required_progress = cumulative_duration / self.days_to_mature
        
        if self.total_growth_progress >= required_progress and current_index < len(stage_order) - 1:
            # Advance to next stage
            self.growth_stage = stage_order[current_index + 1]
            self.growth_milestones.append(f"Advanced to {self.growth_stage.value}")
    
    def get_stage_description(self) -> str:
        """Get description of current growth stage"""
        descriptions = {
            GrowthStage.SEED: "Planted seed ready for germination",
            GrowthStage.SPROUT: "First shoots emerging from soil",
            GrowthStage.SEEDLING: "Young plant establishing root system",
            GrowthStage.JUVENILE: "Rapid growth phase with leaf development",
            GrowthStage.YOUNG: "Plant approaching full size",
            GrowthStage.MATURE: "Fully grown and ready for harvest"
        }
        return descriptions.get(self.growth_stage, "Unknown growth stage")
    
    def is_harvestable(self) -> bool:
        """Check if entity is ready for harvest"""
        return self.growth_stage == GrowthStage.MATURE
    
    def get_harvest_window_remaining(self) -> float:
        """Get remaining time in optimal harvest window (days)"""
        if not self.is_harvestable():
            return 0.0
        
        # Harvest window is typically 20% of growth time after maturity
        harvest_window_days = self.days_to_mature * 0.2
        progress_beyond_mature = self.total_growth_progress - 1.0
        
        if progress_beyond_mature < 0:
            return harvest_window_days
        
        days_past_mature = progress_beyond_mature * self.days_to_mature
        return max(0.0, harvest_window_days - days_past_mature)


@dataclass
class WeatherEffectComponent(Component):
    """Weather impact on entities over time"""
    component_type: str = "weather_effect"
    
    # Weather sensitivity
    temperature_resistance: float = 1.0     # Resistance to temperature extremes
    precipitation_tolerance: float = 1.0    # Tolerance for rain/drought
    wind_resistance: float = 1.0            # Resistance to wind damage
    
    # Current weather effects
    current_temperature_stress: float = 0.0  # Current temperature stress (0-1)
    current_water_stress: float = 0.0       # Current water stress (0-1)
    current_wind_damage: float = 0.0        # Current wind damage (0-1)
    
    # Cumulative effects
    total_weather_damage: float = 0.0       # Total accumulated damage
    days_of_stress: int = 0                 # Days under weather stress
    
    # Weather adaptations
    cold_hardiness: float = 32.0            # Temperature below which damage occurs
    heat_tolerance: float = 95.0            # Temperature above which damage occurs
    drought_tolerance_days: int = 7         # Days without water before stress
    flood_tolerance_hours: int = 24         # Hours of excess water tolerance
    
    # Recovery rates
    stress_recovery_rate: float = 0.1       # How quickly stress recovers
    damage_healing_rate: float = 0.05       # How quickly damage heals
    
    def update_weather_effects(self, weather_type: WeatherType, temperature: float,
                              precipitation: float, wind_speed: float, hours_elapsed: float):
        """Update weather effects on entity"""
        # Calculate temperature stress
        temp_stress = 0.0
        if temperature < self.cold_hardiness:
            temp_stress = (self.cold_hardiness - temperature) / 30.0 * (1.0 - self.temperature_resistance)
        elif temperature > self.heat_tolerance:
            temp_stress = (temperature - self.heat_tolerance) / 20.0 * (1.0 - self.temperature_resistance)
        
        self.current_temperature_stress = min(1.0, temp_stress)
        
        # Calculate water stress
        water_stress = 0.0
        if precipitation == 0.0 and weather_type == WeatherType.DROUGHT:
            water_stress = 0.3 * (1.0 - self.precipitation_tolerance)
        elif precipitation > 2.0:  # Heavy rain/flooding
            water_stress = (precipitation - 2.0) / 3.0 * (1.0 - self.precipitation_tolerance)
        
        self.current_water_stress = min(1.0, water_stress)
        
        # Calculate wind damage
        wind_damage = 0.0
        if wind_speed > 20.0:  # High winds
            wind_damage = (wind_speed - 20.0) / 30.0 * (1.0 - self.wind_resistance)
        
        self.current_wind_damage = min(1.0, wind_damage)
        
        # Update cumulative effects
        total_current_stress = max(self.current_temperature_stress, 
                                  self.current_water_stress, 
                                  self.current_wind_damage)
        
        if total_current_stress > 0.3:  # Significant stress threshold
            self.days_of_stress += hours_elapsed / 24.0
            self.total_weather_damage += total_current_stress * hours_elapsed / 24.0
        else:
            # Recovery when not under stress
            recovery = self.stress_recovery_rate * hours_elapsed / 24.0
            self.total_weather_damage = max(0.0, self.total_weather_damage - recovery)
    
    def get_overall_health_modifier(self) -> float:
        """Get overall health modifier from weather effects"""
        damage_penalty = min(0.8, self.total_weather_damage)  # Max 80% penalty
        stress_penalty = max(self.current_temperature_stress,
                           self.current_water_stress,
                           self.current_wind_damage) * 0.5  # Max 50% penalty
        
        return max(0.1, 1.0 - damage_penalty - stress_penalty)
    
    def get_weather_status(self) -> str:
        """Get current weather status description"""
        if self.total_weather_damage > 0.6:
            return "Severely damaged by weather"
        elif self.total_weather_damage > 0.3:
            return "Moderately stressed by weather"
        elif max(self.current_temperature_stress, self.current_water_stress, self.current_wind_damage) > 0.3:
            return "Currently under weather stress"
        else:
            return "Healthy and weather-resistant"


@dataclass
class SeasonalComponent(Component):
    """Seasonal behavior and adaptations"""
    component_type: str = "seasonal"
    
    # Seasonal preferences
    preferred_seasons: List[Season] = field(default_factory=list)
    seasonal_activity_modifiers: Dict[Season, float] = field(default_factory=dict)
    
    # Current seasonal state
    current_season_modifier: float = 1.0
    seasonal_behavior_active: bool = True
    
    # Seasonal transitions
    last_season_change: int = 0
    seasonal_adaptation_time: int = 1440  # Time to adapt to new season (minutes)
    adaptation_progress: float = 1.0      # Current adaptation progress (0-1)
    
    # Seasonal effects
    winter_dormancy: bool = False         # Whether entity goes dormant in winter
    spring_growth_boost: float = 1.2     # Growth boost in spring
    summer_heat_stress: float = 0.8      # Activity reduction in hot summer
    fall_preparation: bool = False        # Whether entity prepares for winter
    
    def __post_init__(self):
        """Initialize seasonal modifiers"""
        if not self.seasonal_activity_modifiers:
            self.seasonal_activity_modifiers = {
                Season.SPRING: 1.2,  # 20% boost in spring
                Season.SUMMER: 1.0,  # Normal activity
                Season.FALL: 1.0,    # Normal activity
                Season.WINTER: 0.3   # Reduced activity in winter
            }
    
    def update_seasonal_effects(self, current_season: Season, season_progress: float):
        """Update seasonal effects and adaptations"""
        # Get modifier for current season
        base_modifier = self.seasonal_activity_modifiers.get(current_season, 1.0)
        
        # Apply seasonal behavior
        if self.winter_dormancy and current_season == Season.WINTER:
            self.current_season_modifier = 0.1  # Very low activity
        elif current_season == Season.SPRING and self.spring_growth_boost > 1.0:
            # Spring growth boost decreases as season progresses
            boost_strength = 1.0 + (self.spring_growth_boost - 1.0) * (1.0 - season_progress)
            self.current_season_modifier = base_modifier * boost_strength
        elif current_season == Season.SUMMER and self.summer_heat_stress < 1.0:
            # Heat stress increases as summer progresses
            stress_strength = 1.0 - (1.0 - self.summer_heat_stress) * season_progress
            self.current_season_modifier = base_modifier * stress_strength
        else:
            self.current_season_modifier = base_modifier
        
        # Update adaptation progress
        if self.adaptation_progress < 1.0:
            # Still adapting to seasonal change
            adaptation_rate = 1.0 / (self.seasonal_adaptation_time / 1440.0)  # Per day
            self.adaptation_progress = min(1.0, self.adaptation_progress + adaptation_rate)
            
            # Reduce modifier during adaptation
            adaptation_penalty = (1.0 - self.adaptation_progress) * 0.5
            self.current_season_modifier *= (1.0 - adaptation_penalty)
    
    def on_season_change(self, new_season: Season, game_time: int):
        """Handle season change event"""
        self.last_season_change = game_time
        self.adaptation_progress = 0.0  # Start adapting to new season
        
        # Trigger seasonal behaviors
        if new_season == Season.WINTER and self.winter_dormancy:
            self.seasonal_behavior_active = False
        elif new_season == Season.SPRING:
            self.seasonal_behavior_active = True
    
    def is_preferred_season(self, season: Season) -> bool:
        """Check if current season is preferred"""
        return season in self.preferred_seasons
    
    def get_seasonal_status(self, current_season: Season) -> str:
        """Get current seasonal status description"""
        if self.adaptation_progress < 1.0:
            return f"Adapting to {current_season.value} ({self.adaptation_progress*100:.0f}%)"
        elif self.winter_dormancy and current_season == Season.WINTER:
            return "Dormant for winter"
        elif self.is_preferred_season(current_season):
            return f"Thriving in preferred {current_season.value} season"
        else:
            return f"Active in {current_season.value}"


@dataclass
class TimerComponent(Component):
    """Countdown timers for temporary effects"""
    component_type: str = "timer"
    
    # Active timers
    timers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Timer configuration
    auto_remove_expired: bool = True
    max_timers: int = 10
    
    def add_timer(self, timer_name: str, duration_minutes: int, 
                  callback: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        """Add a new countdown timer"""
        if len(self.timers) >= self.max_timers:
            # Remove oldest timer if at limit
            oldest_timer = min(self.timers.items(), key=lambda x: x[1]['created_at'])
            del self.timers[oldest_timer[0]]
        
        self.timers[timer_name] = {
            'duration': duration_minutes,
            'remaining': duration_minutes,
            'created_at': 0,  # Will be set by time system
            'callback': callback,
            'data': data or {},
            'is_active': True
        }
    
    def update_timers(self, minutes_elapsed: int) -> List[str]:
        """Update all timers and return list of expired timer names"""
        expired_timers = []
        
        for timer_name, timer_data in list(self.timers.items()):
            if not timer_data['is_active']:
                continue
            
            timer_data['remaining'] -= minutes_elapsed
            
            if timer_data['remaining'] <= 0:
                expired_timers.append(timer_name)
                
                if self.auto_remove_expired:
                    del self.timers[timer_name]
                else:
                    timer_data['is_active'] = False
        
        return expired_timers
    
    def get_timer_progress(self, timer_name: str) -> float:
        """Get timer progress (0.0 = just started, 1.0 = expired)"""
        if timer_name not in self.timers:
            return 1.0
        
        timer_data = self.timers[timer_name]
        if timer_data['duration'] <= 0:
            return 1.0
        
        elapsed = timer_data['duration'] - timer_data['remaining']
        return min(1.0, elapsed / timer_data['duration'])
    
    def has_active_timer(self, timer_name: str) -> bool:
        """Check if timer is active"""
        return (timer_name in self.timers and 
                self.timers[timer_name]['is_active'] and 
                self.timers[timer_name]['remaining'] > 0)
    
    def get_remaining_time(self, timer_name: str) -> int:
        """Get remaining time for timer in minutes"""
        if timer_name in self.timers:
            return max(0, self.timers[timer_name]['remaining'])
        return 0
    
    def cancel_timer(self, timer_name: str) -> bool:
        """Cancel a timer"""
        if timer_name in self.timers:
            del self.timers[timer_name]
            return True
        return False
    
    def get_active_timers(self) -> List[str]:
        """Get list of active timer names"""
        return [name for name, data in self.timers.items() 
                if data['is_active'] and data['remaining'] > 0]