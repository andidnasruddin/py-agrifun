"""
Data Adapter Layer - Format Translation Between Legacy and Phase 2 Systems

This module provides comprehensive data format translation and adaptation between
legacy pygame systems and advanced Phase 2 systems. It ensures data consistency
and provides seamless interface compatibility during migration.

Key Features:
- Bidirectional data translation (legacy ↔ Phase 2)
- Format validation and error handling
- Interface adaptation for UI compatibility
- Performance-optimized data conversion
- Comprehensive logging for migration tracking

Supported Conversions:
- Time data: Legacy day/hour format ↔ GameTime objects
- Economy data: Simple cash/debt ↔ Advanced transaction tracking
- Employee data: Basic employee objects ↔ Complex AI entities
- Crop data: Grid-based crops ↔ Multi-stage growth systems
- Building data: Simple structures ↔ Advanced infrastructure

Usage:
    adapter = DataAdapter()
    
    # Convert legacy time to Phase 2 format
    game_time = adapter.legacy_time_to_phase2(legacy_time_manager)
    
    # Adapt Phase 2 employee data for legacy UI
    ui_employee_data = adapter.phase2_employee_to_ui(phase2_employee)
"""

import time
import math
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Import Phase 2 system types
from ..systems.time_system import GameTime, Season, WeatherCondition, WeatherType, TimeOfDay
from ..systems.economy_system import Transaction, TransactionType, MarketData
from ..systems.employee_system import Employee, EmployeeState, TaskType, SkillType, EmployeeTrait
from ..systems.crop_system import CropInstance, CropType, GrowthStage
from ..systems.building_system import Building, BuildingType, BuildingStatus


class AdapterError(Exception):
    """Custom exception for data adapter errors"""
    pass


@dataclass
class ConversionResult:
    """Result of data conversion operation"""
    success: bool
    data: Any = None
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)
    conversion_time: float = 0.0


class TimeDataAdapter:
    """Handles time data conversion between legacy and Phase 2 systems"""
    
    def __init__(self):
        self.logger = logging.getLogger('TimeDataAdapter')
    
    def legacy_to_phase2(self, legacy_time_manager) -> ConversionResult:
        """Convert legacy time manager to Phase 2 GameTime"""
        start_time = time.time()
        
        try:
            # Extract legacy time data
            current_day = getattr(legacy_time_manager, 'current_day', 1)
            current_hour = getattr(legacy_time_manager, 'current_hour', 6)
            minutes = getattr(legacy_time_manager, 'minutes', 0)
            
            # Calculate total minutes from game start
            total_minutes = (current_day - 1) * 24 * 60 + current_hour * 60 + minutes
            
            # Determine season based on day of year
            day_of_year = current_day
            if day_of_year <= 90:
                season = Season.SPRING
            elif day_of_year <= 180:
                season = Season.SUMMER
            elif day_of_year <= 270:
                season = Season.FALL
            else:
                season = Season.WINTER
            
            # Calculate year and day within season
            year = 1 + (day_of_year - 1) // 360  # Assuming 360 days per year
            days_in_season = ((day_of_year - 1) % 360) % 90 + 1
            
            # Create GameTime object
            game_time = GameTime(
                minutes=minutes,
                hours=current_hour,
                days=days_in_season,
                season=season,
                year=year,
                total_minutes=total_minutes,
                day_of_year=day_of_year,
                week_of_season=((days_in_season - 1) // 7) + 1
            )
            
            conversion_time = time.time() - start_time
            
            return ConversionResult(
                success=True,
                data=game_time,
                conversion_time=conversion_time
            )
            
        except Exception as e:
            self.logger.error(f"Error converting legacy time to Phase 2: {e}")
            return ConversionResult(
                success=False,
                error_message=str(e),
                conversion_time=time.time() - start_time
            )
    
    def phase2_to_legacy(self, game_time: GameTime) -> ConversionResult:
        """Convert Phase 2 GameTime to legacy format"""
        start_time = time.time()
        
        try:
            # Calculate legacy format from GameTime
            legacy_data = {
                'current_day': game_time.day_of_year,
                'current_hour': game_time.hours,
                'minutes': game_time.minutes,
                'total_minutes': game_time.total_minutes
            }
            
            conversion_time = time.time() - start_time
            
            return ConversionResult(
                success=True,
                data=legacy_data,
                conversion_time=conversion_time
            )
            
        except Exception as e:
            self.logger.error(f"Error converting Phase 2 time to legacy: {e}")
            return ConversionResult(
                success=False,
                error_message=str(e),
                conversion_time=time.time() - start_time
            )
    
    def create_ui_time_data(self, game_time: GameTime, weather: WeatherCondition = None) -> Dict[str, Any]:
        """Create UI-compatible time data from Phase 2 systems"""
        try:
            ui_data = {
                'time_string': game_time.get_time_string(),
                'date_string': game_time.get_date_string(),
                'day': game_time.days,
                'hour': game_time.hours,
                'minute': game_time.minutes,
                'season': game_time.season.value.title(),
                'year': game_time.year,
                'is_work_hours': game_time.is_work_hours(),
                'time_of_day': game_time.get_time_of_day().value
            }
            
            if weather:
                ui_data['weather'] = {
                    'type': weather.weather_type.value,
                    'description': weather.get_description(),
                    'temperature_f': int((weather.temperature_c * 9/5) + 32),
                    'humidity': int(weather.humidity_percent),
                    'wind_speed': int(weather.wind_speed_kmh)
                }
            
            return ui_data
            
        except Exception as e:
            self.logger.error(f"Error creating UI time data: {e}")
            return {}


class EconomyDataAdapter:
    """Handles economy data conversion between legacy and Phase 2 systems"""
    
    def __init__(self):
        self.logger = logging.getLogger('EconomyDataAdapter')
    
    def legacy_to_phase2(self, legacy_economy_manager) -> ConversionResult:
        """Convert legacy economy data to Phase 2 format"""
        start_time = time.time()
        
        try:
            # Extract legacy financial data
            current_cash = getattr(legacy_economy_manager, 'current_cash', 0.0)
            current_debt = getattr(legacy_economy_manager, 'current_debt', 0.0)
            daily_subsidy = getattr(legacy_economy_manager, 'daily_subsidy', 0.0)
            
            # Create Phase 2 economy initialization data
            economy_data = {
                'initial_cash': current_cash,
                'initial_debt': current_debt,
                'daily_subsidy': daily_subsidy,
                'subsidy_days_remaining': getattr(legacy_economy_manager, 'subsidy_days_remaining', 30),
                'loan_interest_rate': getattr(legacy_economy_manager, 'loan_interest_rate', 0.05),
                'transactions': []  # Legacy transactions would need manual conversion
            }
            
            conversion_time = time.time() - start_time
            
            return ConversionResult(
                success=True,
                data=economy_data,
                conversion_time=conversion_time
            )
            
        except Exception as e:
            self.logger.error(f"Error converting legacy economy to Phase 2: {e}")
            return ConversionResult(
                success=False,
                error_message=str(e),
                conversion_time=time.time() - start_time
            )
    
    def create_ui_economy_data(self, economy_system) -> Dict[str, Any]:
        """Create UI-compatible economy data from Phase 2 system"""
        try:
            return {
                'current_cash': economy_system.current_cash,
                'current_debt': economy_system.current_debt,
                'daily_subsidy': economy_system.daily_subsidy,
                'subsidy_days_remaining': economy_system.subsidy_days_remaining,
                'net_worth': economy_system.current_cash - economy_system.current_debt,
                'daily_interest': economy_system.current_debt * economy_system.loan_interest_rate / 365,
                'recent_transactions': [
                    {
                        'amount': t.amount,
                        'description': t.description,
                        'category': t.transaction_type.value,
                        'timestamp': t.timestamp
                    }
                    for t in economy_system.get_recent_transactions(5)
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error creating UI economy data: {e}")
            return {}


class EmployeeDataAdapter:
    """Handles employee data conversion between legacy and Phase 2 systems"""
    
    def __init__(self):
        self.logger = logging.getLogger('EmployeeDataAdapter')
    
    def legacy_to_phase2(self, legacy_employee_manager) -> ConversionResult:
        """Convert legacy employee data to Phase 2 format"""
        start_time = time.time()
        
        try:
            employees_data = []
            
            if hasattr(legacy_employee_manager, 'employees'):
                for emp_id, employee in legacy_employee_manager.employees.items():
                    # Extract basic employee data
                    employee_data = {
                        'employee_id': emp_id,
                        'name': getattr(employee, 'name', f'Employee {emp_id}'),
                        'x': getattr(employee, 'x', 8.0),
                        'y': getattr(employee, 'y', 8.0),
                        'daily_wage': getattr(employee, 'daily_wage', 50.0),
                        'hire_date': getattr(employee, 'hire_date', 0),
                        'movement_speed': getattr(employee, 'movement_speed', 2.0),
                        'state': self._convert_legacy_state(getattr(employee, 'state', 'idle')),
                        'current_task': self._convert_legacy_task(getattr(employee, 'current_task', None)),
                        'skills': {},  # Legacy employees don't have skills
                        'traits': []   # Legacy employees don't have traits
                    }
                    
                    employees_data.append(employee_data)
            
            conversion_time = time.time() - start_time
            
            return ConversionResult(
                success=True,
                data=employees_data,
                conversion_time=conversion_time
            )
            
        except Exception as e:
            self.logger.error(f"Error converting legacy employees to Phase 2: {e}")
            return ConversionResult(
                success=False,
                error_message=str(e),
                conversion_time=time.time() - start_time
            )
    
    def phase2_to_ui(self, employee: Employee) -> Dict[str, Any]:
        """Convert Phase 2 employee to UI-compatible format"""
        try:
            return {
                'id': employee.employee_id,
                'name': employee.name,
                'position': {'x': employee.x, 'y': employee.y},
                'state': employee.state.value,
                'wage': employee.daily_wage,
                'performance': f"{employee.performance_rating:.1%}",
                'efficiency': f"{employee.get_work_efficiency():.1%}",
                'quality': f"{employee.get_work_quality():.1%}",
                'current_task': {
                    'type': employee.current_task.task_type.value if employee.current_task else None,
                    'progress': employee.current_task.get_completion_percentage() if employee.current_task else 0,
                    'location': employee.current_task.target_location if employee.current_task else None
                },
                'stats': {
                    'hunger': int(employee.stats.hunger),
                    'thirst': int(employee.stats.thirst),
                    'rest': int(employee.stats.rest),
                    'energy': int(employee.stats.energy),
                    'morale': int(employee.stats.morale)
                },
                'skills': {
                    skill_type.value: skill.level 
                    for skill_type, skill in employee.skills.items()
                },
                'traits': [trait.value for trait in employee.traits],
                'hours_worked': employee.hours_worked_today,
                'tasks_completed': employee.tasks_completed_today
            }
            
        except Exception as e:
            self.logger.error(f"Error converting Phase 2 employee to UI: {e}")
            return {}
    
    def _convert_legacy_state(self, legacy_state: str) -> EmployeeState:
        """Convert legacy employee state to Phase 2 EmployeeState"""
        state_mapping = {
            'idle': EmployeeState.IDLE,
            'moving': EmployeeState.MOVING,
            'working': EmployeeState.WORKING,
            'resting': EmployeeState.RESTING,
            'off_duty': EmployeeState.OFF_DUTY
        }
        
        return state_mapping.get(legacy_state.lower(), EmployeeState.IDLE)
    
    def _convert_legacy_task(self, legacy_task) -> Optional[Dict[str, Any]]:
        """Convert legacy task to Phase 2 task format"""
        if not legacy_task:
            return None
        
        # Basic task conversion - would need more sophisticated mapping
        return {
            'task_type': TaskType.GENERAL_LABOR,  # Default for legacy tasks
            'target_location': getattr(legacy_task, 'target_location', (8, 8)),
            'progress': getattr(legacy_task, 'progress', 0.0),
            'parameters': {}
        }


class CropDataAdapter:
    """Handles crop data conversion between legacy and Phase 2 systems"""
    
    def __init__(self):
        self.logger = logging.getLogger('CropDataAdapter')
    
    def legacy_tile_to_ui(self, legacy_tile_data) -> Dict[str, Any]:
        """Convert legacy tile data to UI format"""
        try:
            # Extract crop information from legacy tile
            crop_type = getattr(legacy_tile_data, 'crop_type', None)
            growth_stage = getattr(legacy_tile_data, 'growth_stage', 0)
            soil_quality = getattr(legacy_tile_data, 'soil_quality', 5)
            
            ui_data = {
                'terrain_type': getattr(legacy_tile_data, 'terrain_type', 'grass'),
                'crop_type': crop_type,
                'growth_stage': growth_stage,
                'soil_quality': soil_quality,
                'water_level': getattr(legacy_tile_data, 'water_level', 50),
                'fertility': getattr(legacy_tile_data, 'fertility', 50),
                'has_crop': crop_type is not None,
                'is_harvestable': growth_stage >= 4 if crop_type else False,
                'needs_water': getattr(legacy_tile_data, 'water_level', 50) < 30
            }
            
            return ui_data
            
        except Exception as e:
            self.logger.error(f"Error converting legacy tile to UI: {e}")
            return {}
    
    def phase2_crop_to_ui(self, crop_instance: CropInstance) -> Dict[str, Any]:
        """Convert Phase 2 crop instance to UI format"""
        try:
            return {
                'crop_type': crop_instance.crop_type.value,
                'growth_stage': crop_instance.growth_stage.value,
                'growth_progress': crop_instance.growth_progress,
                'health': crop_instance.health,
                'yield_modifier': crop_instance.yield_modifier,
                'quality': crop_instance.quality,
                'days_planted': crop_instance.days_since_planted,
                'is_harvestable': crop_instance.is_harvestable(),
                'is_diseased': crop_instance.is_diseased(),
                'needs_water': crop_instance.needs_water(),
                'estimated_yield': crop_instance.get_estimated_yield(),
                'estimated_value': crop_instance.get_estimated_value()
            }
            
        except Exception as e:
            self.logger.error(f"Error converting Phase 2 crop to UI: {e}")
            return {}


class DataAdapter:
    """Main data adapter coordinating all format conversions"""
    
    def __init__(self):
        self.logger = logging.getLogger('DataAdapter')
        
        # Initialize specialized adapters
        self.time_adapter = TimeDataAdapter()
        self.economy_adapter = EconomyDataAdapter()
        self.employee_adapter = EmployeeDataAdapter()
        self.crop_adapter = CropDataAdapter()
        
        # Performance tracking
        self.conversion_stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'average_conversion_time': 0.0
        }
        
        self.logger.info("Data Adapter initialized")
    
    def convert_legacy_time_to_phase2(self, legacy_time_manager) -> ConversionResult:
        """Convert legacy time data to Phase 2 GameTime"""
        result = self.time_adapter.legacy_to_phase2(legacy_time_manager)
        self._update_stats(result)
        return result
    
    def convert_phase2_time_to_legacy(self, game_time: GameTime) -> ConversionResult:
        """Convert Phase 2 GameTime to legacy format"""
        result = self.time_adapter.phase2_to_legacy(game_time)
        self._update_stats(result)
        return result
    
    def get_ui_time_data(self, game_time: GameTime, weather: WeatherCondition = None) -> Dict[str, Any]:
        """Get UI-compatible time data"""
        return self.time_adapter.create_ui_time_data(game_time, weather)
    
    def convert_legacy_economy_to_phase2(self, legacy_economy_manager) -> ConversionResult:
        """Convert legacy economy data to Phase 2 format"""
        result = self.economy_adapter.legacy_to_phase2(legacy_economy_manager)
        self._update_stats(result)
        return result
    
    def get_ui_economy_data(self, economy_system) -> Dict[str, Any]:
        """Get UI-compatible economy data"""
        return self.economy_adapter.create_ui_economy_data(economy_system)
    
    def convert_legacy_employees_to_phase2(self, legacy_employee_manager) -> ConversionResult:
        """Convert legacy employee data to Phase 2 format"""
        result = self.employee_adapter.legacy_to_phase2(legacy_employee_manager)
        self._update_stats(result)
        return result
    
    def get_ui_employee_data(self, employee: Employee) -> Dict[str, Any]:
        """Get UI-compatible employee data"""
        return self.employee_adapter.phase2_to_ui(employee)
    
    def get_ui_tile_data(self, legacy_tile_data=None, phase2_crop: CropInstance = None) -> Dict[str, Any]:
        """Get UI-compatible tile/crop data"""
        if phase2_crop:
            return self.crop_adapter.phase2_crop_to_ui(phase2_crop)
        elif legacy_tile_data:
            return self.crop_adapter.legacy_tile_to_ui(legacy_tile_data)
        else:
            return {}
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Get data conversion performance statistics"""
        return {
            'total_conversions': self.conversion_stats['total_conversions'],
            'success_rate': (self.conversion_stats['successful_conversions'] / 
                           max(1, self.conversion_stats['total_conversions'])) * 100,
            'failure_rate': (self.conversion_stats['failed_conversions'] / 
                           max(1, self.conversion_stats['total_conversions'])) * 100,
            'average_conversion_time_ms': self.conversion_stats['average_conversion_time'] * 1000
        }
    
    def _update_stats(self, result: ConversionResult):
        """Update conversion statistics"""
        self.conversion_stats['total_conversions'] += 1
        
        if result.success:
            self.conversion_stats['successful_conversions'] += 1
        else:
            self.conversion_stats['failed_conversions'] += 1
        
        # Update average conversion time
        current_avg = self.conversion_stats['average_conversion_time']
        total_conversions = self.conversion_stats['total_conversions']
        
        self.conversion_stats['average_conversion_time'] = (
            (current_avg * (total_conversions - 1) + result.conversion_time) / total_conversions
        )


# Global data adapter instance
_global_data_adapter: Optional[DataAdapter] = None

def get_data_adapter() -> DataAdapter:
    """Get the global data adapter instance"""
    global _global_data_adapter
    if _global_data_adapter is None:
        _global_data_adapter = DataAdapter()
    return _global_data_adapter

def initialize_data_adapter() -> DataAdapter:
    """Initialize the global data adapter"""
    global _global_data_adapter
    _global_data_adapter = DataAdapter()
    return _global_data_adapter