"""
Temporal System - Time-Based Entity Processing for AgriFun Agricultural Simulation

This system coordinates time-based updates for all entities with temporal components.
It integrates with the Time Management System to provide realistic timing for crops,
employees, buildings, and other game entities.

Key Features:
- Batch processing of temporal components for performance
- Integration with Time Management System events
- Realistic agricultural timing simulation
- Dynamic update frequency based on entity activity
- Event-driven temporal notifications

System Architecture:
- Processes all entities with temporal components each game tick
- Coordinates with Time Management System for accurate time progression
- Handles seasonal transitions and weather effects
- Manages growth cycles and aging processes
- Optimizes performance through intelligent batching

Usage Example:
    # Initialize temporal system
    temporal_system = TemporalSystem()
    await temporal_system.initialize()
    
    # Process temporal updates
    temporal_system.update(delta_time_seconds)
    
    # Handle time events
    temporal_system.on_season_changed(new_season)
"""

import time
import math
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Import Phase 1 architecture
from scripts.core.entity_component_system import get_entity_manager, System
from scripts.core.advanced_event_system import get_event_system, EventPriority
from scripts.core.time_management import get_time_manager, Season, WeatherType
from scripts.components.temporal_component import (
    TemporalComponent, ScheduleComponent, GrowthComponent, 
    WeatherEffectComponent, SeasonalComponent, TimerComponent,
    GrowthStage, ScheduleState
)


@dataclass
class TemporalUpdateBatch:
    """Batch of entities for temporal processing"""
    entity_ids: List[str]
    component_type: str
    update_frequency: float  # Updates per game minute
    last_batch_update: float = 0.0
    processing_time_ms: float = 0.0


class TemporalSystem(System):
    """System for processing time-based entity updates"""
    
    def __init__(self):
        super().__init__()
        self.system_name = "temporal_system"
        
        # Core system references
        self.entity_manager = get_entity_manager()
        self.event_system = get_event_system()
        self.time_manager = get_time_manager()
        
        # Processing batches for performance optimization
        self.update_batches: Dict[str, TemporalUpdateBatch] = {}
        
        # Performance tracking
        self.total_entities_processed = 0
        self.total_processing_time_ms = 0.0
        self.updates_per_second = 0
        self.last_performance_report = 0.0
        
        # Event tracking
        self.events_handled = 0
        self.last_season = None
        self.last_weather = None
        
        # Cache for frequently accessed data
        self.active_entities_cache: Set[str] = set()
        self.cache_dirty = True
        self.last_cache_update = 0.0
        
        # Update frequency configuration
        self.base_update_frequencies = {
            'temporal': 1.0,        # Every game minute
            'schedule': 1.0,        # Every game minute  
            'growth': 0.1,          # Every 10 game minutes
            'weather_effect': 0.5,  # Every 2 game minutes
            'seasonal': 0.02,       # Every 50 game minutes
            'timer': 2.0            # Every 30 game seconds
        }
    
    async def initialize(self):
        """Initialize the temporal system"""
        # Subscribe to time management events
        self.event_system.subscribe('time_minute_passed', self._on_minute_passed)
        self.event_system.subscribe('time_hour_passed', self._on_hour_passed)
        self.event_system.subscribe('time_day_passed', self._on_day_passed)
        self.event_system.subscribe('time_season_changed', self._on_season_changed)
        self.event_system.subscribe('weather_changed', self._on_weather_changed)
        
        # Subscribe to entity events
        self.event_system.subscribe('entity_created', self._on_entity_created)
        self.event_system.subscribe('entity_destroyed', self._on_entity_destroyed)
        self.event_system.subscribe('component_added', self._on_component_added)
        self.event_system.subscribe('component_removed', self._on_component_removed)
        
        # Initialize update batches
        await self._initialize_update_batches()
        
        # Cache active entities
        self._update_entity_cache()
        
        self.logger.info("Temporal System initialized successfully")
    
    async def _initialize_update_batches(self):
        """Initialize processing batches for all temporal component types"""
        component_types = [
            'temporal', 'schedule', 'growth', 
            'weather_effect', 'seasonal', 'timer'
        ]
        
        for component_type in component_types:
            # Query entities with this component type
            entities = self.entity_manager.query([component_type])
            
            # Create update batch
            self.update_batches[component_type] = TemporalUpdateBatch(
                entity_ids=entities,
                component_type=component_type,
                update_frequency=self.base_update_frequencies[component_type]
            )
            
            self.logger.debug(f"Initialized {component_type} batch with {len(entities)} entities")
    
    def update(self, delta_time: float):
        """Main update method called each frame"""
        current_time = time.time()
        game_time = self.time_manager.get_current_time()
        
        # Update entity cache if needed
        if self.cache_dirty or (current_time - self.last_cache_update) > 5.0:
            self._update_entity_cache()
        
        # Process each component type batch
        total_entities_this_frame = 0
        frame_start_time = time.time()
        
        for component_type, batch in self.update_batches.items():
            if self._should_update_batch(batch, game_time):
                entities_processed = self._process_temporal_batch(batch, game_time, delta_time)
                total_entities_this_frame += entities_processed
                batch.last_batch_update = game_time.total_minutes
        
        # Update performance tracking
        frame_time_ms = (time.time() - frame_start_time) * 1000
        self.total_entities_processed += total_entities_this_frame
        self.total_processing_time_ms += frame_time_ms
        
        # Performance reporting
        if current_time - self.last_performance_report > 10.0:
            self._report_performance()
            self.last_performance_report = current_time
    
    def _should_update_batch(self, batch: TemporalUpdateBatch, game_time) -> bool:
        """Check if batch should be updated based on frequency"""
        if not batch.entity_ids:
            return False
        
        time_since_update = game_time.total_minutes - batch.last_batch_update
        update_interval = 1.0 / batch.update_frequency  # Minutes between updates
        
        return time_since_update >= update_interval
    
    def _process_temporal_batch(self, batch: TemporalUpdateBatch, game_time, delta_time: float) -> int:
        """Process a batch of entities for temporal updates"""
        batch_start_time = time.time()
        entities_processed = 0
        
        for entity_id in batch.entity_ids[:]:  # Copy list to avoid modification issues
            if not self.entity_manager.entity_exists(entity_id):
                batch.entity_ids.remove(entity_id)
                continue
            
            component = self.entity_manager.get_component(entity_id, batch.component_type)
            if not component:
                batch.entity_ids.remove(entity_id)
                continue
            
            # Process component based on type
            try:
                if batch.component_type == 'temporal':
                    self._process_temporal_component(entity_id, component, game_time)
                elif batch.component_type == 'schedule':
                    self._process_schedule_component(entity_id, component, game_time)
                elif batch.component_type == 'growth':
                    self._process_growth_component(entity_id, component, game_time, delta_time)
                elif batch.component_type == 'weather_effect':
                    self._process_weather_effect_component(entity_id, component, game_time)
                elif batch.component_type == 'seasonal':
                    self._process_seasonal_component(entity_id, component, game_time)
                elif batch.component_type == 'timer':
                    self._process_timer_component(entity_id, component, game_time)
                
                entities_processed += 1
                
            except Exception as e:
                self.logger.error(f"Failed to process {batch.component_type} for entity {entity_id}: {e}")
        
        # Update batch performance tracking
        batch.processing_time_ms = (time.time() - batch_start_time) * 1000
        
        return entities_processed
    
    def _process_temporal_component(self, entity_id: str, component: TemporalComponent, game_time):
        """Process base temporal component"""
        if component.should_update(game_time.total_minutes):
            component.update_age(game_time.total_minutes)
            
            # Emit age milestone events
            if component.age_in_days > 0 and component.age_in_days % 30 < 1:  # Monthly milestones
                self.event_system.emit('entity_age_milestone', {
                    'entity_id': entity_id,
                    'age_days': component.age_in_days,
                    'age_string': component.get_age_string()
                }, priority=EventPriority.LOW)
    
    def _process_schedule_component(self, entity_id: str, component: ScheduleComponent, game_time):
        """Process schedule component for work routines"""
        current_hour = game_time.hour
        current_minutes = game_time.hour * 60 + game_time.minute
        current_season = self.time_manager.get_current_season()
        
        # Check if work time
        is_work_time = component.is_work_time(current_hour, current_season)
        is_break_time = component.is_break_time(current_minutes)
        
        # Determine current state
        new_state = component.current_state
        
        if is_break_time:
            new_state = ScheduleState.BREAK
        elif is_work_time and not is_break_time:
            new_state = ScheduleState.WORKING
        else:
            new_state = ScheduleState.OFF_DUTY
        
        # Handle state changes
        if new_state != component.current_state:
            old_state = component.current_state
            component.current_state = new_state
            component.state_start_time = game_time.total_minutes
            
            # Emit schedule state change event
            self.event_system.emit('entity_schedule_changed', {
                'entity_id': entity_id,
                'old_state': old_state.value,
                'new_state': new_state.value,
                'is_working': new_state == ScheduleState.WORKING
            }, priority=EventPriority.NORMAL)
        
        # Update energy based on current activity
        minutes_in_state = game_time.total_minutes - component.state_start_time
        is_working = component.current_state == ScheduleState.WORKING
        component.update_energy(minutes_in_state, is_working)
        
        # Apply weather efficiency modifier
        current_weather = self.time_manager.get_current_weather()
        weather_modifier = self._get_weather_work_modifier(current_weather.weather_type)
        component.weather_efficiency_modifier = weather_modifier
    
    def _process_growth_component(self, entity_id: str, component: GrowthComponent, game_time, delta_time: float):
        """Process growth component for living entities"""
        # Get environmental conditions
        current_weather = self.time_manager.get_current_weather()
        
        # Simplified environmental values - in real game these would come from grid/location
        temperature = current_weather.temperature
        water_level = 0.7  # Would be from irrigation/rain system
        light_level = 0.8 if 6 <= game_time.hour <= 18 else 0.1  # Day/night cycle
        
        # Apply seasonal light adjustments
        current_season = self.time_manager.get_current_season()
        if current_season == Season.WINTER:
            light_level *= 0.6  # Shorter days
        elif current_season == Season.SUMMER:
            light_level *= 1.2  # Longer days
        
        # Update growth
        minutes_elapsed = delta_time * self.time_manager.time_scale  # Convert to game minutes
        component.update_growth(minutes_elapsed, temperature, water_level, light_level)
        
        # Check for growth stage changes
        if component.growth_milestones:
            latest_milestone = component.growth_milestones[-1]
            self.event_system.emit('entity_growth_milestone', {
                'entity_id': entity_id,
                'milestone': latest_milestone,
                'growth_stage': component.growth_stage.value,
                'growth_progress': component.total_growth_progress,
                'is_harvestable': component.is_harvestable()
            }, priority=EventPriority.NORMAL)
            
            # Clear processed milestones
            component.growth_milestones.clear()
    
    def _process_weather_effect_component(self, entity_id: str, component: WeatherEffectComponent, game_time):
        """Process weather effects on entities"""
        current_weather = self.time_manager.get_current_weather()
        
        # Calculate hours elapsed since last update
        hours_elapsed = (game_time.total_minutes - component.last_update) / 60.0 if hasattr(component, 'last_update') else 1.0
        
        # Update weather effects
        component.update_weather_effects(
            weather_type=current_weather.weather_type,
            temperature=current_weather.temperature,
            precipitation=current_weather.precipitation,
            wind_speed=current_weather.wind_speed,
            hours_elapsed=hours_elapsed
        )
        
        # Track last update
        component.last_update = game_time.total_minutes
        
        # Emit weather stress events for significant changes
        health_modifier = component.get_overall_health_modifier()
        if health_modifier < 0.5:  # Significant weather stress
            self.event_system.emit('entity_weather_stress', {
                'entity_id': entity_id,
                'health_modifier': health_modifier,
                'weather_status': component.get_weather_status(),
                'stress_days': component.days_of_stress
            }, priority=EventPriority.NORMAL)
    
    def _process_seasonal_component(self, entity_id: str, component: SeasonalComponent, game_time):
        """Process seasonal adaptations"""
        current_season = self.time_manager.get_current_season()
        season_progress = self.time_manager.get_season_progress()
        
        # Update seasonal effects
        component.update_seasonal_effects(current_season, season_progress)
        
        # Emit adaptation events
        if component.adaptation_progress < 1.0:
            self.event_system.emit('entity_seasonal_adaptation', {
                'entity_id': entity_id,
                'season': current_season.value,
                'adaptation_progress': component.adaptation_progress,
                'seasonal_modifier': component.current_season_modifier
            }, priority=EventPriority.LOW)
    
    def _process_timer_component(self, entity_id: str, component: TimerComponent, game_time):
        """Process countdown timers"""
        # Calculate minutes elapsed since last update
        minutes_elapsed = (game_time.total_minutes - component.last_update) if hasattr(component, 'last_update') else 1
        
        # Update all timers
        expired_timers = component.update_timers(minutes_elapsed)
        
        # Handle expired timers
        for timer_name in expired_timers:
            self.event_system.emit('entity_timer_expired', {
                'entity_id': entity_id,
                'timer_name': timer_name,
                'timer_data': component.timers.get(timer_name, {}).get('data', {})
            }, priority=EventPriority.NORMAL)
        
        # Track last update
        component.last_update = game_time.total_minutes
    
    def _get_weather_work_modifier(self, weather_type: WeatherType) -> float:
        """Get work efficiency modifier based on weather"""
        weather_modifiers = {
            WeatherType.CLEAR: 1.0,
            WeatherType.PARTLY_CLOUDY: 0.95,
            WeatherType.CLOUDY: 0.9,
            WeatherType.LIGHT_RAIN: 0.8,
            WeatherType.HEAVY_RAIN: 0.6,
            WeatherType.STORM: 0.3,
            WeatherType.SNOW: 0.7,
            WeatherType.FOG: 0.8,
            WeatherType.DROUGHT: 0.85,
            WeatherType.EXTREME_HEAT: 0.6,
            WeatherType.EXTREME_COLD: 0.5
        }
        return weather_modifiers.get(weather_type, 1.0)
    
    def _update_entity_cache(self):
        """Update cache of active entities with temporal components"""
        self.active_entities_cache.clear()
        
        # Query all entities with any temporal component
        temporal_types = ['temporal', 'schedule', 'growth', 'weather_effect', 'seasonal', 'timer']
        for component_type in temporal_types:
            entities = self.entity_manager.query([component_type])
            self.active_entities_cache.update(entities)
        
        self.cache_dirty = False
        self.last_cache_update = time.time()
        
        self.logger.debug(f"Updated entity cache: {len(self.active_entities_cache)} active temporal entities")
    
    def _report_performance(self):
        """Report temporal system performance metrics"""
        if self.total_entities_processed > 0:
            avg_processing_time = self.total_processing_time_ms / self.total_entities_processed
            
            performance_data = {
                'total_entities_processed': self.total_entities_processed,
                'average_processing_time_ms': avg_processing_time,
                'active_entities': len(self.active_entities_cache),
                'update_batches': len(self.update_batches),
                'events_handled': self.events_handled
            }
            
            self.event_system.emit('temporal_system_performance', performance_data, priority=EventPriority.LOW)
            
            self.logger.debug(f"Temporal System Performance: {avg_processing_time:.2f}ms/entity, {self.total_entities_processed} total processed")
    
    # Event handlers
    def _on_minute_passed(self, event_data):
        """Handle minute passed event"""
        self.events_handled += 1
        # Minute-based events could trigger specific temporal updates here
    
    def _on_hour_passed(self, event_data):
        """Handle hour passed event"""
        self.events_handled += 1
        # Force schedule component updates
        if 'schedule' in self.update_batches:
            self.update_batches['schedule'].last_batch_update = 0  # Force update
    
    def _on_day_passed(self, event_data):
        """Handle day passed event"""
        self.events_handled += 1
        # Reset daily tracking for schedule components
        for entity_id in self.update_batches.get('schedule', TemporalUpdateBatch([], '', 0)).entity_ids:
            schedule_comp = self.entity_manager.get_component(entity_id, 'schedule')
            if schedule_comp:
                schedule_comp.reset_daily_tracking()
    
    def _on_season_changed(self, event_data):
        """Handle season change event"""
        self.events_handled += 1
        new_season = event_data.get('new_season')
        game_time = event_data.get('game_time', 0)
        
        # Notify all seasonal components
        for entity_id in self.update_batches.get('seasonal', TemporalUpdateBatch([], '', 0)).entity_ids:
            seasonal_comp = self.entity_manager.get_component(entity_id, 'seasonal')
            if seasonal_comp:
                seasonal_comp.on_season_change(Season(new_season), game_time)
        
        self.last_season = new_season
        self.logger.info(f"Processed season change to {new_season} for {len(self.active_entities_cache)} entities")
    
    def _on_weather_changed(self, event_data):
        """Handle weather change event"""
        self.events_handled += 1
        self.last_weather = event_data.get('weather_type')
        # Weather effects are processed continuously, no immediate action needed
    
    def _on_entity_created(self, event_data):
        """Handle entity creation"""
        self.cache_dirty = True
    
    def _on_entity_destroyed(self, event_data):
        """Handle entity destruction"""
        entity_id = event_data.get('entity_id')
        if entity_id:
            # Remove from all batches
            for batch in self.update_batches.values():
                if entity_id in batch.entity_ids:
                    batch.entity_ids.remove(entity_id)
            
            # Remove from cache
            self.active_entities_cache.discard(entity_id)
    
    def _on_component_added(self, event_data):
        """Handle component addition"""
        entity_id = event_data.get('entity_id')
        component_type = event_data.get('component_type')
        
        if component_type in self.update_batches and entity_id not in self.update_batches[component_type].entity_ids:
            self.update_batches[component_type].entity_ids.append(entity_id)
            self.active_entities_cache.add(entity_id)
    
    def _on_component_removed(self, event_data):
        """Handle component removal"""
        entity_id = event_data.get('entity_id')
        component_type = event_data.get('component_type')
        
        if component_type in self.update_batches and entity_id in self.update_batches[component_type].entity_ids:
            self.update_batches[component_type].entity_ids.remove(entity_id)
            
            # Check if entity still has other temporal components
            has_temporal_components = any(
                self.entity_manager.get_component(entity_id, comp_type) 
                for comp_type in ['temporal', 'schedule', 'growth', 'weather_effect', 'seasonal', 'timer']
            )
            
            if not has_temporal_components:
                self.active_entities_cache.discard(entity_id)
    
    async def shutdown(self):
        """Shutdown the temporal system"""
        self.logger.info("Shutting down Temporal System")
        
        # Final performance report
        self._report_performance()
        
        # Clear all data structures
        self.update_batches.clear()
        self.active_entities_cache.clear()
        
        self.logger.info("Temporal System shutdown complete")


# Global temporal system instance
_global_temporal_system: Optional[TemporalSystem] = None

def get_temporal_system() -> TemporalSystem:
    """Get the global temporal system instance"""
    global _global_temporal_system
    if _global_temporal_system is None:
        _global_temporal_system = TemporalSystem()
    return _global_temporal_system

def initialize_temporal_system() -> TemporalSystem:
    """Initialize the global temporal system"""
    global _global_temporal_system
    _global_temporal_system = TemporalSystem()
    return _global_temporal_system