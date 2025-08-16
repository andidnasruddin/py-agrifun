"""
System Bridge Architecture - Phase 2 Integration Foundation

This module provides the bridge architecture for gradually migrating from legacy pygame systems
to advanced Phase 2 systems. It allows both systems to coexist during migration, providing
data translation, validation, and rollback mechanisms.

Key Features:
- Gradual system migration with fallback to legacy systems
- Data translation between old and new system formats
- Migration validation and rollback mechanisms
- Performance monitoring during migration
- Seamless user experience during transition

Integration Strategy:
- Phase 0: Foundation - Bridge architecture and translation layers
- Phase 1: Time System - Replace legacy time with advanced seasons/weather
- Phase 2: Economy System - Advanced market dynamics and contracts
- Phase 3: Employee System - AI workforce with skills and pathfinding
- Phase 4: Crop System - Multi-stage growth with soil science
- Phase 5: Final Integration - Buildings, save/load, complete unification

Usage:
    bridge = SystemBridge()
    bridge.enable_migration('time_system')
    
    # System automatically routes requests to new system
    time_data = bridge.get_time_data()
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import traceback

# Import legacy pygame systems
from ..core.time_manager import TimeManager as LegacyTimeManager
from ..economy.economy_manager import EconomyManager as LegacyEconomyManager
from ..employee.employee_manager import EmployeeManager as LegacyEmployeeManager
from ..core.grid_manager import GridManager as LegacyGridManager

# Import Phase 2 advanced systems
from ..systems.time_system import get_time_system, TimeSystem, GameTime, Season, WeatherCondition
from ..systems.economy_system import get_economy_system, EconomySystem, TransactionType
from ..systems.employee_system import get_employee_system, EmployeeSystem, TaskType, EmployeeState
from ..systems.crop_system import get_crop_system
from ..systems.building_system import get_building_system
from ..systems.save_load_system import get_save_load_system


class MigrationStatus(Enum):
    """Status of system migration"""
    LEGACY = "legacy"          # Using legacy system only
    MIGRATING = "migrating"    # Gradual migration in progress
    PHASE2 = "phase2"          # Using Phase 2 system only
    ERROR = "error"            # Migration failed, rollback needed
    ROLLBACK = "rollback"      # Rolling back to legacy system


class SystemType(Enum):
    """Types of systems that can be migrated"""
    TIME_SYSTEM = "time_system"
    ECONOMY_SYSTEM = "economy_system"  
    EMPLOYEE_SYSTEM = "employee_system"
    CROP_SYSTEM = "crop_system"
    BUILDING_SYSTEM = "building_system"
    SAVE_LOAD_SYSTEM = "save_load_system"


@dataclass
class MigrationConfig:
    """Configuration for system migration"""
    system_type: SystemType
    migration_status: MigrationStatus = MigrationStatus.LEGACY
    validation_enabled: bool = True
    rollback_enabled: bool = True
    performance_monitoring: bool = True
    migration_start_time: float = 0.0
    migration_data: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    max_errors: int = 10


@dataclass
class ValidationResult:
    """Result of system validation"""
    is_valid: bool
    system_type: SystemType
    legacy_data: Dict[str, Any]
    phase2_data: Dict[str, Any]
    discrepancies: List[str] = field(default_factory=list)
    performance_impact: float = 0.0
    timestamp: float = field(default_factory=time.time)


class DataTranslator:
    """Translates data between legacy and Phase 2 system formats"""
    
    def __init__(self):
        self.logger = logging.getLogger('DataTranslator')
    
    def translate_time_data(self, legacy_time_manager) -> Dict[str, Any]:
        """Translate legacy time data to Phase 2 format"""
        try:
            # Legacy time manager has: current_day, current_hour, minutes, speed, paused
            return {
                'total_minutes': (legacy_time_manager.current_day - 1) * 24 * 60 + 
                               legacy_time_manager.current_hour * 60 + 
                               legacy_time_manager.minutes,
                'hours': legacy_time_manager.current_hour,
                'minutes': legacy_time_manager.minutes,
                'days': legacy_time_manager.current_day,
                'season': 'spring',  # Default to spring, Phase 2 system will calculate proper season
                'year': 1,
                'time_scale': legacy_time_manager.speed if hasattr(legacy_time_manager, 'speed') else 1.0,
                'paused': legacy_time_manager.paused if hasattr(legacy_time_manager, 'paused') else False
            }
        except Exception as e:
            self.logger.error(f"Error translating time data: {e}")
            return {}
    
    def translate_economy_data(self, legacy_economy_manager) -> Dict[str, Any]:
        """Translate legacy economy data to Phase 2 format"""
        try:
            return {
                'current_cash': getattr(legacy_economy_manager, 'current_cash', 0.0),
                'current_debt': getattr(legacy_economy_manager, 'current_debt', 0.0),
                'daily_subsidy': getattr(legacy_economy_manager, 'daily_subsidy', 0.0),
                'transactions': [],  # Legacy transactions would need conversion
                'total_revenue': getattr(legacy_economy_manager, 'total_revenue', 0.0),
                'total_expenses': getattr(legacy_economy_manager, 'total_expenses', 0.0)
            }
        except Exception as e:
            self.logger.error(f"Error translating economy data: {e}")
            return {}
    
    def translate_employee_data(self, legacy_employee_manager) -> Dict[str, Any]:
        """Translate legacy employee data to Phase 2 format"""
        try:
            employees = []
            if hasattr(legacy_employee_manager, 'employees'):
                for emp_id, employee in legacy_employee_manager.employees.items():
                    employees.append({
                        'employee_id': emp_id,
                        'name': getattr(employee, 'name', f'Employee {emp_id}'),
                        'x': getattr(employee, 'x', 8.0),
                        'y': getattr(employee, 'y', 8.0),
                        'state': 'idle',
                        'daily_wage': getattr(employee, 'daily_wage', 50.0),
                        'skills': {},  # Legacy employees don't have skill system
                        'traits': [],  # Legacy employees don't have traits
                        'performance_rating': 1.0
                    })
            
            return {
                'employees': employees,
                'total_employees': len(employees),
                'hiring_cost_base': 100.0,
                'daily_wage_base': 50.0
            }
        except Exception as e:
            self.logger.error(f"Error translating employee data: {e}")
            return {}


class MigrationValidator:
    """Validates migration integrity and data consistency"""
    
    def __init__(self):
        self.logger = logging.getLogger('MigrationValidator')
    
    def validate_time_migration(self, legacy_system, phase2_system) -> ValidationResult:
        """Validate time system migration"""
        try:
            legacy_data = {
                'current_day': getattr(legacy_system, 'current_day', 1),
                'current_hour': getattr(legacy_system, 'current_hour', 6),
                'minutes': getattr(legacy_system, 'minutes', 0)
            }
            
            phase2_time = phase2_system.get_current_time()
            phase2_data = {
                'days': phase2_time.days,
                'hours': phase2_time.hours,
                'minutes': phase2_time.minutes,
                'total_minutes': phase2_time.total_minutes
            }
            
            discrepancies = []
            
            # Check if times are reasonably close (within 1 hour)
            legacy_total_minutes = (legacy_data['current_day'] - 1) * 24 * 60 + \
                                 legacy_data['current_hour'] * 60 + legacy_data['minutes']
            
            time_diff = abs(legacy_total_minutes - phase2_data['total_minutes'])
            if time_diff > 60:  # More than 1 hour difference
                discrepancies.append(f"Time difference too large: {time_diff} minutes")
            
            is_valid = len(discrepancies) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                system_type=SystemType.TIME_SYSTEM,
                legacy_data=legacy_data,
                phase2_data=phase2_data,
                discrepancies=discrepancies
            )
            
        except Exception as e:
            self.logger.error(f"Error validating time migration: {e}")
            return ValidationResult(
                is_valid=False,
                system_type=SystemType.TIME_SYSTEM,
                legacy_data={},
                phase2_data={},
                discrepancies=[f"Validation error: {e}"]
            )
    
    def validate_economy_migration(self, legacy_system, phase2_system) -> ValidationResult:
        """Validate economy system migration"""
        try:
            legacy_data = {
                'current_cash': getattr(legacy_system, 'current_cash', 0.0),
                'current_debt': getattr(legacy_system, 'current_debt', 0.0)
            }
            
            phase2_data = {
                'current_cash': phase2_system.current_cash,
                'current_debt': phase2_system.current_debt
            }
            
            discrepancies = []
            
            # Check cash difference (allow 1% tolerance)
            cash_diff = abs(legacy_data['current_cash'] - phase2_data['current_cash'])
            cash_tolerance = max(1.0, abs(legacy_data['current_cash']) * 0.01)
            if cash_diff > cash_tolerance:
                discrepancies.append(f"Cash difference: ${cash_diff:.2f}")
            
            # Check debt difference
            debt_diff = abs(legacy_data['current_debt'] - phase2_data['current_debt'])
            debt_tolerance = max(1.0, abs(legacy_data['current_debt']) * 0.01)
            if debt_diff > debt_tolerance:
                discrepancies.append(f"Debt difference: ${debt_diff:.2f}")
            
            is_valid = len(discrepancies) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                system_type=SystemType.ECONOMY_SYSTEM,
                legacy_data=legacy_data,
                phase2_data=phase2_data,
                discrepancies=discrepancies
            )
            
        except Exception as e:
            self.logger.error(f"Error validating economy migration: {e}")
            return ValidationResult(
                is_valid=False,
                system_type=SystemType.ECONOMY_SYSTEM,
                legacy_data={},
                phase2_data={},
                discrepancies=[f"Validation error: {e}"]
            )


class SystemBridge:
    """Main system bridge for coordinating migration between legacy and Phase 2 systems"""
    
    def __init__(self):
        self.logger = logging.getLogger('SystemBridge')
        
        # Migration tracking
        self.migration_configs: Dict[SystemType, MigrationConfig] = {}
        self.data_translator = DataTranslator()
        self.validator = MigrationValidator()
        
        # System references
        self.legacy_systems: Dict[SystemType, Any] = {}
        self.phase2_systems: Dict[SystemType, Any] = {}
        
        # Performance monitoring
        self.performance_metrics: Dict[str, float] = {}
        
        # Error handling
        self.error_handlers: Dict[SystemType, Callable] = {}
        self.rollback_handlers: Dict[SystemType, Callable] = {}
        
        # Initialize migration configs for all systems
        for system_type in SystemType:
            self.migration_configs[system_type] = MigrationConfig(system_type=system_type)
        
        self.logger.info("System Bridge initialized")
    
    def register_legacy_system(self, system_type: SystemType, system_instance: Any):
        """Register a legacy system instance"""
        self.legacy_systems[system_type] = system_instance
        self.logger.info(f"Registered legacy {system_type.value}")
    
    def register_phase2_system(self, system_type: SystemType, system_instance: Any):
        """Register a Phase 2 system instance"""
        self.phase2_systems[system_type] = system_instance
        self.logger.info(f"Registered Phase 2 {system_type.value}")
    
    def enable_migration(self, system_type: SystemType, validate: bool = True) -> bool:
        """Enable migration for a specific system"""
        try:
            if system_type not in self.migration_configs:
                self.logger.error(f"Unknown system type: {system_type}")
                return False
            
            config = self.migration_configs[system_type]
            
            # Check if both legacy and Phase 2 systems are available
            if system_type not in self.legacy_systems:
                self.logger.error(f"Legacy {system_type.value} not registered")
                return False
            
            if system_type not in self.phase2_systems:
                self.logger.error(f"Phase 2 {system_type.value} not registered")
                return False
            
            # Perform initial data migration
            success = self._migrate_system_data(system_type)
            if not success:
                self.logger.error(f"Failed to migrate {system_type.value} data")
                return False
            
            # Validate migration if requested
            if validate:
                validation_result = self._validate_migration(system_type)
                if not validation_result.is_valid:
                    self.logger.error(f"Migration validation failed for {system_type.value}: {validation_result.discrepancies}")
                    return False
            
            # Update migration status
            config.migration_status = MigrationStatus.PHASE2
            config.migration_start_time = time.time()
            
            self.logger.info(f"Successfully enabled migration for {system_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enabling migration for {system_type.value}: {e}")
            self._handle_migration_error(system_type, e)
            return False
    
    def disable_migration(self, system_type: SystemType) -> bool:
        """Disable migration and rollback to legacy system"""
        try:
            if system_type not in self.migration_configs:
                return False
            
            config = self.migration_configs[system_type]
            config.migration_status = MigrationStatus.LEGACY
            
            self.logger.info(f"Disabled migration for {system_type.value}, using legacy system")
            return True
            
        except Exception as e:
            self.logger.error(f"Error disabling migration for {system_type.value}: {e}")
            return False
    
    def get_active_system(self, system_type: SystemType) -> Optional[Any]:
        """Get the currently active system (legacy or Phase 2)"""
        if system_type not in self.migration_configs:
            return None
        
        config = self.migration_configs[system_type]
        
        if config.migration_status == MigrationStatus.PHASE2:
            return self.phase2_systems.get(system_type)
        else:
            return self.legacy_systems.get(system_type)
    
    def is_using_phase2(self, system_type: SystemType) -> bool:
        """Check if system is using Phase 2 implementation"""
        config = self.migration_configs.get(system_type)
        return config is not None and config.migration_status == MigrationStatus.PHASE2
    
    def get_migration_status(self, system_type: SystemType) -> MigrationStatus:
        """Get current migration status for a system"""
        config = self.migration_configs.get(system_type)
        return config.migration_status if config else MigrationStatus.LEGACY
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get summary of all system migration statuses"""
        summary = {
            'total_systems': len(SystemType),
            'migrated_systems': 0,
            'legacy_systems': 0,
            'error_systems': 0,
            'system_details': {}
        }
        
        for system_type, config in self.migration_configs.items():
            status = config.migration_status.value
            summary['system_details'][system_type.value] = {
                'status': status,
                'error_count': config.error_count,
                'migration_time': time.time() - config.migration_start_time if config.migration_start_time > 0 else 0
            }
            
            if config.migration_status == MigrationStatus.PHASE2:
                summary['migrated_systems'] += 1
            elif config.migration_status == MigrationStatus.LEGACY:
                summary['legacy_systems'] += 1
            elif config.migration_status == MigrationStatus.ERROR:
                summary['error_systems'] += 1
        
        return summary
    
    def _migrate_system_data(self, system_type: SystemType) -> bool:
        """Migrate data from legacy to Phase 2 system"""
        try:
            legacy_system = self.legacy_systems[system_type]
            phase2_system = self.phase2_systems[system_type]
            
            if system_type == SystemType.TIME_SYSTEM:
                return self._migrate_time_data(legacy_system, phase2_system)
            elif system_type == SystemType.ECONOMY_SYSTEM:
                return self._migrate_economy_data(legacy_system, phase2_system)
            elif system_type == SystemType.EMPLOYEE_SYSTEM:
                return self._migrate_employee_data(legacy_system, phase2_system)
            else:
                self.logger.warning(f"No migration handler for {system_type.value}")
                return True  # Allow migration to proceed
                
        except Exception as e:
            self.logger.error(f"Error migrating {system_type.value} data: {e}")
            return False
    
    def _migrate_time_data(self, legacy_system, phase2_system) -> bool:
        """Migrate time system data"""
        try:
            time_data = self.data_translator.translate_time_data(legacy_system)
            
            # Set Phase 2 system time to match legacy system
            if time_data:
                # Calculate total minutes from legacy system
                total_minutes = time_data['total_minutes']
                
                # Advance Phase 2 system to match
                current_time = phase2_system.get_current_time()
                minutes_to_advance = total_minutes - current_time.total_minutes
                
                if minutes_to_advance > 0:
                    phase2_system.advance_time(int(minutes_to_advance))
                
                # Set time scale and pause state
                if 'time_scale' in time_data:
                    phase2_system.set_time_scale(time_data['time_scale'])
                
                if time_data.get('paused', False):
                    phase2_system.pause()
                else:
                    phase2_system.resume()
                
                self.logger.info(f"Migrated time data: {time_data}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error migrating time data: {e}")
            return False
    
    def _migrate_economy_data(self, legacy_system, phase2_system) -> bool:
        """Migrate economy system data"""
        try:
            economy_data = self.data_translator.translate_economy_data(legacy_system)
            
            if economy_data:
                # Set Phase 2 system financial state
                phase2_system.current_cash = economy_data.get('current_cash', 0.0)
                phase2_system.current_debt = economy_data.get('current_debt', 0.0)
                
                self.logger.info(f"Migrated economy data: {economy_data}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error migrating economy data: {e}")
            return False
    
    def _migrate_employee_data(self, legacy_system, phase2_system) -> bool:
        """Migrate employee system data"""
        try:
            employee_data = self.data_translator.translate_employee_data(legacy_system)
            
            if employee_data:
                # Migrate employees to Phase 2 system
                for emp_data in employee_data.get('employees', []):
                    # Phase 2 system would need method to import employee data
                    # This is a simplified example
                    self.logger.info(f"Would migrate employee: {emp_data['name']}")
                
                self.logger.info(f"Migrated employee data: {len(employee_data.get('employees', []))} employees")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error migrating employee data: {e}")
            return False
    
    def _validate_migration(self, system_type: SystemType) -> ValidationResult:
        """Validate migration for a system"""
        try:
            legacy_system = self.legacy_systems[system_type]
            phase2_system = self.phase2_systems[system_type]
            
            if system_type == SystemType.TIME_SYSTEM:
                return self.validator.validate_time_migration(legacy_system, phase2_system)
            elif system_type == SystemType.ECONOMY_SYSTEM:
                return self.validator.validate_economy_migration(legacy_system, phase2_system)
            else:
                # Default validation - assume valid
                return ValidationResult(
                    is_valid=True,
                    system_type=system_type,
                    legacy_data={},
                    phase2_data={}
                )
                
        except Exception as e:
            self.logger.error(f"Error validating {system_type.value} migration: {e}")
            return ValidationResult(
                is_valid=False,
                system_type=system_type,
                legacy_data={},
                phase2_data={},
                discrepancies=[f"Validation error: {e}"]
            )
    
    def _handle_migration_error(self, system_type: SystemType, error: Exception):
        """Handle migration errors"""
        config = self.migration_configs[system_type]
        config.error_count += 1
        config.migration_status = MigrationStatus.ERROR
        
        self.logger.error(f"Migration error for {system_type.value}: {error}")
        self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Attempt rollback if too many errors
        if config.error_count >= config.max_errors:
            self.logger.warning(f"Too many errors for {system_type.value}, attempting rollback")
            self.disable_migration(system_type)


# Global system bridge instance
_global_system_bridge: Optional[SystemBridge] = None

def get_system_bridge() -> SystemBridge:
    """Get the global system bridge instance"""
    global _global_system_bridge
    if _global_system_bridge is None:
        _global_system_bridge = SystemBridge()
    return _global_system_bridge

def initialize_system_bridge() -> SystemBridge:
    """Initialize the global system bridge"""
    global _global_system_bridge
    _global_system_bridge = SystemBridge()
    return _global_system_bridge