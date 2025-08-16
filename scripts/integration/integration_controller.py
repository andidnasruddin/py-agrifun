"""
Integration Controller - Master Migration Coordinator

This is the main controller that orchestrates the gradual migration from legacy
pygame systems to Phase 2 systems. It coordinates all migration components
including the system bridge, data adapters, validation framework, and rollback
mechanisms to ensure safe and smooth migration.

Key Features:
- Master migration orchestration and coordination
- Automated migration workflows with safety checks
- Integration health monitoring and reporting
- Progressive migration with milestone validation
- Emergency response and recovery coordination
- Comprehensive migration reporting and analytics

Migration Phases:
- Phase 0: Foundation Architecture (System Bridge, Validation, Rollback)
- Phase 1: Time System Migration (Advanced seasons, weather, scheduling)
- Phase 2: Economy System Migration (Market dynamics, contracts, analytics)
- Phase 3: Employee System Migration (AI workforce, skills, pathfinding)
- Phase 4: Crop System Migration (Multi-stage growth, soil science)
- Phase 5: Final Integration (Buildings, save/load, complete unification)

Safety Protocols:
- Automatic pre-migration snapshots
- Continuous validation during migration
- Emergency rollback triggers
- Progressive validation checkpoints
- Comprehensive audit trail

Usage:
    controller = IntegrationController()
    
    # Initialize migration infrastructure
    controller.initialize_migration_infrastructure()
    
    # Migrate specific system
    success = controller.migrate_system('time_system')
    
    # Monitor migration health
    health = controller.get_migration_health()
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import traceback

from .system_bridge import get_system_bridge, SystemBridge, SystemType, MigrationStatus
from .data_adapter import get_data_adapter, DataAdapter
from .migration_validator import get_migration_validator, MigrationValidator, ValidationLevel
from .rollback_manager import get_rollback_manager, RollbackManager, RollbackTrigger

# Import Phase 2 systems
from ..systems.time_system import get_time_system, initialize_time_system
from ..systems.economy_system import get_economy_system, initialize_economy_system
from ..systems.employee_system import get_employee_system, initialize_employee_system
from ..systems.crop_system import get_crop_system, initialize_crop_system
from ..systems.building_system import get_building_system, initialize_building_system
from ..systems.save_load_system import get_save_load_system, initialize_save_load_system


class MigrationPhase(Enum):
    """Migration phases"""
    PHASE_0_FOUNDATION = "phase_0_foundation"
    PHASE_1_TIME = "phase_1_time"
    PHASE_2_ECONOMY = "phase_2_economy"
    PHASE_3_EMPLOYEES = "phase_3_employees"
    PHASE_4_CROPS = "phase_4_crops"
    PHASE_5_FINAL = "phase_5_final"


class MigrationHealthStatus(Enum):
    """Overall migration health status"""
    EXCELLENT = "excellent"     # All systems migrated successfully
    GOOD = "good"              # Most systems migrated, minor issues
    FAIR = "fair"              # Some systems migrated, moderate issues
    POOR = "poor"              # Few systems migrated, major issues
    CRITICAL = "critical"      # Migration failures, emergency rollback needed


@dataclass
class MigrationProgress:
    """Progress tracking for migration"""
    current_phase: MigrationPhase
    systems_migrated: List[SystemType] = field(default_factory=list)
    systems_remaining: List[SystemType] = field(default_factory=list)
    
    # Progress metrics
    overall_progress_percent: float = 0.0
    current_phase_progress_percent: float = 0.0
    estimated_completion_time: float = 0.0
    
    # Quality metrics
    validation_score: float = 0.0
    error_count: int = 0
    warning_count: int = 0
    
    # Timeline
    migration_start_time: float = 0.0
    current_phase_start_time: float = 0.0
    last_update_time: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'current_phase': self.current_phase.value,
            'systems_migrated': [s.value for s in self.systems_migrated],
            'systems_remaining': [s.value for s in self.systems_remaining],
            'overall_progress_percent': self.overall_progress_percent,
            'current_phase_progress_percent': self.current_phase_progress_percent,
            'estimated_completion_time': self.estimated_completion_time,
            'validation_score': self.validation_score,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'migration_start_time': self.migration_start_time,
            'current_phase_start_time': self.current_phase_start_time,
            'last_update_time': self.last_update_time
        }


@dataclass
class MigrationHealth:
    """Overall migration health assessment"""
    status: MigrationHealthStatus
    score: float = 0.0  # 0-100 health score
    
    # Component health
    bridge_health: float = 0.0
    validation_health: float = 0.0
    rollback_health: float = 0.0
    data_integrity_health: float = 0.0
    
    # Issues
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Performance
    migration_performance: Dict[str, float] = field(default_factory=dict)
    
    # Timestamp
    assessment_time: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'status': self.status.value,
            'score': self.score,
            'bridge_health': self.bridge_health,
            'validation_health': self.validation_health,
            'rollback_health': self.rollback_health,
            'data_integrity_health': self.data_integrity_health,
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'recommendations': self.recommendations,
            'migration_performance': self.migration_performance,
            'assessment_time': self.assessment_time
        }


class IntegrationController:
    """Master migration coordinator"""
    
    def __init__(self):
        self.logger = logging.getLogger('IntegrationController')
        
        # Initialize migration components
        self.system_bridge = get_system_bridge()
        self.data_adapter = get_data_adapter()
        self.migration_validator = get_migration_validator()
        self.rollback_manager = get_rollback_manager()
        
        # Migration state
        self.migration_progress = MigrationProgress(
            current_phase=MigrationPhase.PHASE_0_FOUNDATION
        )
        
        # System tracking
        self.legacy_systems: Dict[SystemType, Any] = {}
        self.phase2_systems: Dict[SystemType, Any] = {}
        
        # Migration configuration
        self.auto_snapshot_enabled = True
        self.validation_required = True
        self.rollback_on_failure = True
        self.emergency_rollback_enabled = True
        
        # Progress tracking
        self.migration_milestones: Dict[MigrationPhase, List[SystemType]] = {
            MigrationPhase.PHASE_0_FOUNDATION: [],
            MigrationPhase.PHASE_1_TIME: [SystemType.TIME_SYSTEM],
            MigrationPhase.PHASE_2_ECONOMY: [SystemType.ECONOMY_SYSTEM],
            MigrationPhase.PHASE_3_EMPLOYEES: [SystemType.EMPLOYEE_SYSTEM],
            MigrationPhase.PHASE_4_CROPS: [SystemType.CROP_SYSTEM],
            MigrationPhase.PHASE_5_FINAL: [SystemType.BUILDING_SYSTEM, SystemType.SAVE_LOAD_SYSTEM]
        }
        
        # Event handlers
        self.migration_callbacks: Dict[str, List[Callable]] = {
            'migration_started': [],
            'migration_completed': [],
            'migration_failed': [],
            'phase_started': [],
            'phase_completed': [],
            'emergency_rollback': []
        }
        
        self.logger.info("Integration Controller initialized")
    
    def initialize_migration_infrastructure(self) -> bool:
        """Initialize all migration infrastructure components"""
        try:
            self.logger.info("Initializing migration infrastructure...")
            
            # Initialize Phase 2 systems (but don't activate them yet)
            self.phase2_systems[SystemType.TIME_SYSTEM] = initialize_time_system()
            self.phase2_systems[SystemType.ECONOMY_SYSTEM] = initialize_economy_system()
            self.phase2_systems[SystemType.EMPLOYEE_SYSTEM] = initialize_employee_system()
            self.phase2_systems[SystemType.CROP_SYSTEM] = initialize_crop_system()
            self.phase2_systems[SystemType.BUILDING_SYSTEM] = initialize_building_system()
            self.phase2_systems[SystemType.SAVE_LOAD_SYSTEM] = initialize_save_load_system()
            
            # Register systems with bridge
            for system_type, system_instance in self.phase2_systems.items():
                self.system_bridge.register_phase2_system(system_type, system_instance)
            
            # Register systems with rollback manager
            for system_type, system_instance in self.phase2_systems.items():
                self.rollback_manager.register_system(system_type, system_instance)
            
            # Setup emergency rollback triggers
            for system_type in SystemType:
                self.rollback_manager.setup_auto_rollback_triggers(system_type)
            
            # Update progress
            self.migration_progress.migration_start_time = time.time()
            self.migration_progress.current_phase_start_time = time.time()
            
            self.logger.info("Migration infrastructure initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize migration infrastructure: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def register_legacy_system(self, system_type: SystemType, system_instance: Any):
        """Register a legacy system for migration"""
        self.legacy_systems[system_type] = system_instance
        self.system_bridge.register_legacy_system(system_type, system_instance)
        self.rollback_manager.register_system(system_type, system_instance)
        
        self.logger.info(f"Registered legacy {system_type.value} for migration")
    
    def migrate_system(self, system_type: SystemType, 
                      force: bool = False, 
                      create_snapshot: bool = True) -> bool:
        """Migrate a specific system from legacy to Phase 2"""
        try:
            self.logger.info(f"Starting migration of {system_type.value}")
            
            # Check if system is already migrated
            if self.system_bridge.is_using_phase2(system_type) and not force:
                self.logger.info(f"{system_type.value} already migrated")
                return True
            
            # Check prerequisites
            if not self._check_migration_prerequisites(system_type):
                self.logger.error(f"Migration prerequisites not met for {system_type.value}")
                return False
            
            # Create pre-migration snapshot
            snapshot_id = None
            if create_snapshot and self.auto_snapshot_enabled:
                try:
                    snapshot_id = self.rollback_manager.create_migration_snapshot(
                        system_type, f"Pre-migration snapshot for {system_type.value}"
                    )
                    self.logger.info(f"Created pre-migration snapshot: {snapshot_id}")
                except Exception as e:
                    self.logger.warning(f"Failed to create snapshot: {e}")
                    if not force:
                        return False
            
            # Emit migration started event
            self._emit_event('migration_started', {
                'system_type': system_type.value,
                'snapshot_id': snapshot_id
            })
            
            # Perform migration
            migration_success = self.system_bridge.enable_migration(
                system_type, validate=self.validation_required
            )
            
            if migration_success:
                # Update progress
                if system_type not in self.migration_progress.systems_migrated:
                    self.migration_progress.systems_migrated.append(system_type)
                
                if system_type in self.migration_progress.systems_remaining:
                    self.migration_progress.systems_remaining.remove(system_type)
                
                self._update_migration_progress()
                
                # Emit success event
                self._emit_event('migration_completed', {
                    'system_type': system_type.value,
                    'success': True
                })
                
                self.logger.info(f"Successfully migrated {system_type.value}")
                return True
            
            else:
                # Migration failed
                if self.rollback_on_failure and snapshot_id:
                    self.logger.warning(f"Migration failed, attempting rollback for {system_type.value}")
                    rollback_success = self.rollback_manager.rollback_to_snapshot(
                        snapshot_id, trigger=RollbackTrigger.VALIDATION_FAILURE
                    )
                    
                    if rollback_success:
                        self.logger.info(f"Rollback successful for {system_type.value}")
                    else:
                        self.logger.error(f"Rollback failed for {system_type.value}")
                
                # Emit failure event
                self._emit_event('migration_failed', {
                    'system_type': system_type.value,
                    'success': False
                })
                
                self.logger.error(f"Failed to migrate {system_type.value}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception during {system_type.value} migration: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Attempt emergency rollback
            if self.emergency_rollback_enabled:
                self.rollback_manager.emergency_rollback(system_type)
            
            return False
    
    def migrate_phase(self, phase: MigrationPhase, force: bool = False) -> bool:
        """Migrate all systems in a specific phase"""
        try:
            self.logger.info(f"Starting migration of {phase.value}")
            
            # Emit phase started event
            self._emit_event('phase_started', {
                'phase': phase.value
            })
            
            # Update current phase
            self.migration_progress.current_phase = phase
            self.migration_progress.current_phase_start_time = time.time()
            
            # Get systems for this phase
            systems_to_migrate = self.migration_milestones.get(phase, [])
            
            if not systems_to_migrate:
                self.logger.info(f"No systems to migrate in {phase.value}")
                return True
            
            # Migrate each system in the phase
            phase_success = True
            for system_type in systems_to_migrate:
                system_success = self.migrate_system(system_type, force=force)
                if not system_success:
                    phase_success = False
                    if not force:
                        break  # Stop on first failure unless forced
            
            if phase_success:
                # Emit phase completed event
                self._emit_event('phase_completed', {
                    'phase': phase.value,
                    'success': True
                })
                
                self.logger.info(f"Successfully completed migration of {phase.value}")
            else:
                self.logger.error(f"Failed to complete migration of {phase.value}")
            
            return phase_success
            
        except Exception as e:
            self.logger.error(f"Exception during {phase.value} migration: {e}")
            return False
    
    def migrate_all_systems(self, force: bool = False) -> bool:
        """Migrate all systems through all phases"""
        try:
            self.logger.info("Starting complete system migration")
            
            # Migrate through all phases
            phases = [
                MigrationPhase.PHASE_1_TIME,
                MigrationPhase.PHASE_2_ECONOMY,
                MigrationPhase.PHASE_3_EMPLOYEES,
                MigrationPhase.PHASE_4_CROPS,
                MigrationPhase.PHASE_5_FINAL
            ]
            
            overall_success = True
            for phase in phases:
                phase_success = self.migrate_phase(phase, force=force)
                if not phase_success:
                    overall_success = False
                    if not force:
                        break
            
            if overall_success:
                self.logger.info("Complete system migration successful")
            else:
                self.logger.error("Complete system migration failed")
            
            return overall_success
            
        except Exception as e:
            self.logger.error(f"Exception during complete migration: {e}")
            return False
    
    def rollback_system(self, system_type: SystemType) -> bool:
        """Rollback a system to legacy implementation"""
        try:
            self.logger.info(f"Rolling back {system_type.value} to legacy")
            
            # Disable migration (rollback to legacy)
            success = self.system_bridge.disable_migration(system_type)
            
            if success:
                # Update progress
                if system_type in self.migration_progress.systems_migrated:
                    self.migration_progress.systems_migrated.remove(system_type)
                
                if system_type not in self.migration_progress.systems_remaining:
                    self.migration_progress.systems_remaining.append(system_type)
                
                self._update_migration_progress()
                
                self.logger.info(f"Successfully rolled back {system_type.value}")
            else:
                self.logger.error(f"Failed to rollback {system_type.value}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Exception during {system_type.value} rollback: {e}")
            return False
    
    def get_migration_health(self) -> MigrationHealth:
        """Assess overall migration health"""
        try:
            # Assess component health
            bridge_health = self._assess_bridge_health()
            validation_health = self._assess_validation_health()
            rollback_health = self._assess_rollback_health()
            data_integrity_health = self._assess_data_integrity_health()
            
            # Calculate overall score
            overall_score = (bridge_health + validation_health + rollback_health + data_integrity_health) / 4.0
            
            # Determine status
            if overall_score >= 90:
                status = MigrationHealthStatus.EXCELLENT
            elif overall_score >= 75:
                status = MigrationHealthStatus.GOOD
            elif overall_score >= 60:
                status = MigrationHealthStatus.FAIR
            elif overall_score >= 40:
                status = MigrationHealthStatus.POOR
            else:
                status = MigrationHealthStatus.CRITICAL
            
            # Collect issues and recommendations
            critical_issues = []
            warnings = []
            recommendations = []
            
            if bridge_health < 70:
                critical_issues.append("System bridge health is poor")
                recommendations.append("Check system bridge connectivity and data flow")
            
            if validation_health < 70:
                warnings.append("Validation health is below optimal")
                recommendations.append("Review validation results and address failures")
            
            if rollback_health < 70:
                critical_issues.append("Rollback mechanism health is poor")
                recommendations.append("Verify rollback capabilities and snapshot integrity")
            
            if data_integrity_health < 70:
                critical_issues.append("Data integrity issues detected")
                recommendations.append("Perform data validation and consistency checks")
            
            # Get performance data
            migration_performance = self._get_migration_performance_metrics()
            
            return MigrationHealth(
                status=status,
                score=overall_score,
                bridge_health=bridge_health,
                validation_health=validation_health,
                rollback_health=rollback_health,
                data_integrity_health=data_integrity_health,
                critical_issues=critical_issues,
                warnings=warnings,
                recommendations=recommendations,
                migration_performance=migration_performance
            )
            
        except Exception as e:
            self.logger.error(f"Error assessing migration health: {e}")
            return MigrationHealth(
                status=MigrationHealthStatus.CRITICAL,
                score=0.0,
                critical_issues=[f"Health assessment failed: {e}"]
            )
    
    def get_migration_report(self) -> Dict[str, Any]:
        """Get comprehensive migration report"""
        try:
            # Get current progress
            progress = self.migration_progress.to_dict()
            
            # Get health assessment
            health = self.get_migration_health().to_dict()
            
            # Get system bridge summary
            bridge_summary = self.system_bridge.get_system_summary()
            
            # Get validation report
            validation_report = self.migration_validator.get_validation_report()
            
            # Get rollback history
            rollback_history = self.rollback_manager.get_rollback_history()
            
            # Get snapshot summary
            snapshot_summary = self.rollback_manager.get_snapshot_summary()
            
            # Get data adapter stats
            adapter_stats = self.data_adapter.get_conversion_stats()
            
            return {
                'timestamp': time.time(),
                'migration_progress': progress,
                'migration_health': health,
                'system_bridge_summary': bridge_summary,
                'validation_report': validation_report,
                'rollback_history': rollback_history[-10:],  # Last 10 operations
                'snapshot_summary': snapshot_summary,
                'data_adapter_stats': adapter_stats,
                'phase_milestones': {
                    phase.value: [s.value for s in systems]
                    for phase, systems in self.migration_milestones.items()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating migration report: {e}")
            return {
                'error': f"Failed to generate report: {e}",
                'timestamp': time.time()
            }
    
    def add_migration_callback(self, event_type: str, callback: Callable):
        """Add callback for migration events"""
        if event_type in self.migration_callbacks:
            self.migration_callbacks[event_type].append(callback)
            self.logger.info(f"Added callback for {event_type}")
    
    def _check_migration_prerequisites(self, system_type: SystemType) -> bool:
        """Check if prerequisites are met for system migration"""
        # Check if legacy system is registered
        if system_type not in self.legacy_systems:
            self.logger.error(f"Legacy {system_type.value} not registered")
            return False
        
        # Check if Phase 2 system is available
        if system_type not in self.phase2_systems:
            self.logger.error(f"Phase 2 {system_type.value} not available")
            return False
        
        # Check dependencies (e.g., time system should be migrated before others)
        dependencies = {
            SystemType.ECONOMY_SYSTEM: [SystemType.TIME_SYSTEM],
            SystemType.EMPLOYEE_SYSTEM: [SystemType.TIME_SYSTEM],
            SystemType.CROP_SYSTEM: [SystemType.TIME_SYSTEM],
            SystemType.BUILDING_SYSTEM: [SystemType.ECONOMY_SYSTEM],
            SystemType.SAVE_LOAD_SYSTEM: []  # Can be migrated anytime
        }
        
        required_systems = dependencies.get(system_type, [])
        for required_system in required_systems:
            if not self.system_bridge.is_using_phase2(required_system):
                self.logger.error(f"{system_type.value} requires {required_system.value} to be migrated first")
                return False
        
        return True
    
    def _update_migration_progress(self):
        """Update migration progress metrics"""
        total_systems = len(SystemType)
        migrated_count = len(self.migration_progress.systems_migrated)
        
        self.migration_progress.overall_progress_percent = (migrated_count / total_systems) * 100
        self.migration_progress.last_update_time = time.time()
        
        # Update current phase progress
        current_phase_systems = self.migration_milestones.get(self.migration_progress.current_phase, [])
        if current_phase_systems:
            migrated_in_phase = len([s for s in current_phase_systems if s in self.migration_progress.systems_migrated])
            self.migration_progress.current_phase_progress_percent = (migrated_in_phase / len(current_phase_systems)) * 100
    
    def _assess_bridge_health(self) -> float:
        """Assess system bridge health"""
        try:
            summary = self.system_bridge.get_system_summary()
            
            migrated_count = summary.get('migrated_systems', 0)
            error_count = summary.get('error_systems', 0)
            total_count = summary.get('total_systems', 1)
            
            # Calculate health score
            if total_count == 0:
                return 100.0
            
            success_rate = (migrated_count / total_count) * 100
            error_penalty = (error_count / total_count) * 50
            
            return max(0.0, success_rate - error_penalty)
            
        except Exception as e:
            self.logger.warning(f"Error assessing bridge health: {e}")
            return 0.0
    
    def _assess_validation_health(self) -> float:
        """Assess validation system health"""
        try:
            report = self.migration_validator.get_validation_report()
            
            if 'latest_validation' in report:
                latest = report['latest_validation']
                return latest.get('score', 0.0)
            
            return 100.0  # No validations yet, assume healthy
            
        except Exception as e:
            self.logger.warning(f"Error assessing validation health: {e}")
            return 0.0
    
    def _assess_rollback_health(self) -> float:
        """Assess rollback system health"""
        try:
            snapshot_summary = self.rollback_manager.get_snapshot_summary()
            rollback_history = self.rollback_manager.get_rollback_history()
            
            # Check if snapshots exist
            if snapshot_summary.get('total_snapshots', 0) == 0:
                return 50.0  # No snapshots, moderate health
            
            # Check rollback success rate
            if rollback_history:
                successful_rollbacks = len([op for op in rollback_history if op.get('success', False)])
                total_rollbacks = len(rollback_history)
                success_rate = (successful_rollbacks / total_rollbacks) * 100
                return success_rate
            
            return 100.0  # No rollbacks attempted, assume healthy
            
        except Exception as e:
            self.logger.warning(f"Error assessing rollback health: {e}")
            return 0.0
    
    def _assess_data_integrity_health(self) -> float:
        """Assess data integrity health"""
        try:
            stats = self.data_adapter.get_conversion_stats()
            
            success_rate = stats.get('success_rate', 100.0)
            return success_rate
            
        except Exception as e:
            self.logger.warning(f"Error assessing data integrity health: {e}")
            return 0.0
    
    def _get_migration_performance_metrics(self) -> Dict[str, float]:
        """Get migration performance metrics"""
        try:
            adapter_stats = self.data_adapter.get_conversion_stats()
            
            return {
                'average_conversion_time_ms': adapter_stats.get('average_conversion_time_ms', 0.0),
                'total_conversions': adapter_stats.get('total_conversions', 0),
                'conversion_success_rate': adapter_stats.get('success_rate', 100.0)
            }
            
        except Exception as e:
            self.logger.warning(f"Error getting performance metrics: {e}")
            return {}
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit migration event to registered callbacks"""
        try:
            callbacks = self.migration_callbacks.get(event_type, [])
            for callback in callbacks:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.warning(f"Error in callback for {event_type}: {e}")
        except Exception as e:
            self.logger.error(f"Error emitting event {event_type}: {e}")


# Global integration controller instance
_global_integration_controller: Optional[IntegrationController] = None

def get_integration_controller() -> IntegrationController:
    """Get the global integration controller instance"""
    global _global_integration_controller
    if _global_integration_controller is None:
        _global_integration_controller = IntegrationController()
    return _global_integration_controller

def initialize_integration_controller() -> IntegrationController:
    """Initialize the global integration controller"""
    global _global_integration_controller
    _global_integration_controller = IntegrationController()
    return _global_integration_controller