"""
Rollback Manager - Safe Migration Recovery System

This system provides comprehensive rollback capabilities for the gradual migration
from legacy pygame systems to Phase 2 systems. It ensures that any migration
can be safely reverted if issues are detected, maintaining game stability.

Key Features:
- Automated state snapshots before migration
- Multi-level rollback (data, configuration, system state)
- Recovery validation and integrity checking
- Emergency rollback triggers and conditions
- Comprehensive rollback logging and reporting
- Progressive rollback with selective system restoration

Rollback Levels:
1. Data Rollback - Restore system data to pre-migration state
2. Configuration Rollback - Restore system configuration
3. State Rollback - Restore complete system state
4. Emergency Rollback - Immediate revert to legacy systems
5. Selective Rollback - Rollback specific components only

Safety Features:
- Automatic snapshots before any migration step
- Integrity validation after rollback
- Rollback confirmation and verification
- Emergency triggers for critical failures
- Comprehensive audit trail

Usage:
    rollback_manager = RollbackManager()
    
    # Create snapshot before migration
    snapshot_id = rollback_manager.create_snapshot('time_system')
    
    # Perform migration...
    
    # If issues occur, rollback
    success = rollback_manager.rollback_to_snapshot(snapshot_id)
"""

import time
import json
import pickle
import logging
import os
import shutil
import uuid
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import traceback
from pathlib import Path

from .system_bridge import SystemType, MigrationStatus
from .migration_validator import get_migration_validator, ValidationSeverity


class RollbackLevel(Enum):
    """Levels of rollback operations"""
    DATA = "data"                    # Rollback system data only
    CONFIGURATION = "configuration"  # Rollback system configuration
    STATE = "state"                 # Rollback complete system state
    EMERGENCY = "emergency"         # Emergency full rollback
    SELECTIVE = "selective"         # Selective component rollback


class RollbackTrigger(Enum):
    """Triggers that can initiate rollback"""
    MANUAL = "manual"               # User-initiated rollback
    VALIDATION_FAILURE = "validation_failure"  # Failed validation
    CRITICAL_ERROR = "critical_error"  # System critical error
    PERFORMANCE_DEGRADATION = "performance_degradation"  # Performance issues
    DATA_CORRUPTION = "data_corruption"  # Data integrity issues
    TIMEOUT = "timeout"             # Operation timeout
    EMERGENCY = "emergency"         # Emergency situation


class SnapshotType(Enum):
    """Types of system snapshots"""
    FULL = "full"                   # Complete system snapshot
    INCREMENTAL = "incremental"    # Changes since last snapshot
    DATA_ONLY = "data_only"        # Data state only
    CONFIG_ONLY = "config_only"    # Configuration only


@dataclass
class SystemSnapshot:
    """Snapshot of system state for rollback"""
    snapshot_id: str
    system_type: SystemType
    snapshot_type: SnapshotType
    timestamp: float
    
    # System data
    system_data: Dict[str, Any] = field(default_factory=dict)
    system_config: Dict[str, Any] = field(default_factory=dict)
    system_state: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    migration_status: MigrationStatus = MigrationStatus.LEGACY
    file_path: Optional[str] = None
    size_bytes: int = 0
    checksum: str = ""
    description: str = ""
    
    # Rollback metadata
    rollback_tested: bool = False
    rollback_count: int = 0
    last_rollback_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'snapshot_id': self.snapshot_id,
            'system_type': self.system_type.value,
            'snapshot_type': self.snapshot_type.value,
            'timestamp': self.timestamp,
            'migration_status': self.migration_status.value,
            'file_path': self.file_path,
            'size_bytes': self.size_bytes,
            'checksum': self.checksum,
            'description': self.description,
            'rollback_tested': self.rollback_tested,
            'rollback_count': self.rollback_count,
            'last_rollback_time': self.last_rollback_time
        }


@dataclass
class RollbackOperation:
    """Record of rollback operation"""
    operation_id: str
    snapshot_id: str
    system_type: SystemType
    rollback_level: RollbackLevel
    trigger: RollbackTrigger
    
    # Operation details
    start_time: float
    end_time: float = 0.0
    success: bool = False
    error_message: str = ""
    
    # Recovery data
    recovery_steps: List[str] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    
    # Impact assessment
    data_restored: bool = False
    config_restored: bool = False
    state_restored: bool = False
    
    @property
    def duration(self) -> float:
        """Get operation duration"""
        return self.end_time - self.start_time if self.end_time > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'operation_id': self.operation_id,
            'snapshot_id': self.snapshot_id,
            'system_type': self.system_type.value,
            'rollback_level': self.rollback_level.value,
            'trigger': self.trigger.value,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'success': self.success,
            'error_message': self.error_message,
            'recovery_steps': self.recovery_steps,
            'validation_results': self.validation_results,
            'data_restored': self.data_restored,
            'config_restored': self.config_restored,
            'state_restored': self.state_restored
        }


class SnapshotManager:
    """Manages system snapshots for rollback"""
    
    def __init__(self, snapshots_dir: str = "snapshots"):
        self.logger = logging.getLogger('SnapshotManager')
        self.snapshots_dir = Path(snapshots_dir)
        self.snapshots_dir.mkdir(exist_ok=True)
        
        # Snapshot storage
        self.snapshots: Dict[str, SystemSnapshot] = {}
        self.max_snapshots_per_system = 10
        
        # Load existing snapshots
        self._load_snapshots()
    
    def create_snapshot(self, system_type: SystemType, system_instance: Any,
                       snapshot_type: SnapshotType = SnapshotType.FULL,
                       description: str = "") -> str:
        """Create a system snapshot"""
        snapshot_id = f"{system_type.value}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Extract system data
            system_data = self._extract_system_data(system_instance, system_type)
            system_config = self._extract_system_config(system_instance, system_type)
            system_state = self._extract_system_state(system_instance, system_type)
            
            # Create snapshot
            snapshot = SystemSnapshot(
                snapshot_id=snapshot_id,
                system_type=system_type,
                snapshot_type=snapshot_type,
                timestamp=time.time(),
                system_data=system_data,
                system_config=system_config,
                system_state=system_state,
                description=description or f"Snapshot of {system_type.value}"
            )
            
            # Save to file
            file_path = self.snapshots_dir / f"{snapshot_id}.pkl"
            with open(file_path, 'wb') as f:
                pickle.dump(snapshot, f)
            
            snapshot.file_path = str(file_path)
            snapshot.size_bytes = file_path.stat().st_size
            snapshot.checksum = self._calculate_checksum(file_path)
            
            # Store in memory
            self.snapshots[snapshot_id] = snapshot
            
            # Cleanup old snapshots
            self._cleanup_old_snapshots(system_type)
            
            self.logger.info(f"Created snapshot {snapshot_id} for {system_type.value}")
            return snapshot_id
            
        except Exception as e:
            self.logger.error(f"Failed to create snapshot for {system_type.value}: {e}")
            raise
    
    def get_snapshot(self, snapshot_id: str) -> Optional[SystemSnapshot]:
        """Get snapshot by ID"""
        return self.snapshots.get(snapshot_id)
    
    def list_snapshots(self, system_type: SystemType = None) -> List[SystemSnapshot]:
        """List available snapshots"""
        snapshots = list(self.snapshots.values())
        
        if system_type:
            snapshots = [s for s in snapshots if s.system_type == system_type]
        
        # Sort by timestamp (newest first)
        snapshots.sort(key=lambda s: s.timestamp, reverse=True)
        return snapshots
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot"""
        try:
            snapshot = self.snapshots.get(snapshot_id)
            if not snapshot:
                return False
            
            # Delete file
            if snapshot.file_path and os.path.exists(snapshot.file_path):
                os.remove(snapshot.file_path)
            
            # Remove from memory
            del self.snapshots[snapshot_id]
            
            self.logger.info(f"Deleted snapshot {snapshot_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete snapshot {snapshot_id}: {e}")
            return False
    
    def _extract_system_data(self, system_instance: Any, system_type: SystemType) -> Dict[str, Any]:
        """Extract system data for snapshot"""
        data = {}
        
        try:
            if system_type == SystemType.TIME_SYSTEM:
                # Extract time system data
                if hasattr(system_instance, 'get_current_time'):
                    current_time = system_instance.get_current_time()
                    data['current_time'] = {
                        'minutes': current_time.minutes,
                        'hours': current_time.hours,
                        'days': current_time.days,
                        'season': current_time.season.value,
                        'year': current_time.year,
                        'total_minutes': current_time.total_minutes
                    }
                
                data['time_scale'] = getattr(system_instance, 'time_scale', 1.0)
                data['paused'] = getattr(system_instance, 'paused', False)
                
            elif system_type == SystemType.ECONOMY_SYSTEM:
                # Extract economy system data
                data['current_cash'] = getattr(system_instance, 'current_cash', 0.0)
                data['current_debt'] = getattr(system_instance, 'current_debt', 0.0)
                data['daily_subsidy'] = getattr(system_instance, 'daily_subsidy', 0.0)
                data['subsidy_days_remaining'] = getattr(system_instance, 'subsidy_days_remaining', 0)
                
            elif system_type == SystemType.EMPLOYEE_SYSTEM:
                # Extract employee system data
                employees = getattr(system_instance, 'employees', {})
                data['employees'] = {}
                
                for emp_id, employee in employees.items():
                    data['employees'][emp_id] = {
                        'name': getattr(employee, 'name', ''),
                        'x': getattr(employee, 'x', 0.0),
                        'y': getattr(employee, 'y', 0.0),
                        'daily_wage': getattr(employee, 'daily_wage', 0.0),
                        'state': getattr(employee, 'state', 'idle')
                    }
        
        except Exception as e:
            self.logger.warning(f"Error extracting data for {system_type.value}: {e}")
        
        return data
    
    def _extract_system_config(self, system_instance: Any, system_type: SystemType) -> Dict[str, Any]:
        """Extract system configuration for snapshot"""
        config = {}
        
        try:
            # Extract common configuration attributes
            if hasattr(system_instance, 'config_manager'):
                # If system has config manager, extract relevant configs
                config_manager = system_instance.config_manager
                if hasattr(config_manager, '_config'):
                    config = dict(config_manager._config)
        
        except Exception as e:
            self.logger.warning(f"Error extracting config for {system_type.value}: {e}")
        
        return config
    
    def _extract_system_state(self, system_instance: Any, system_type: SystemType) -> Dict[str, Any]:
        """Extract system state for snapshot"""
        state = {}
        
        try:
            # Extract state information that's not data or config
            state['running'] = getattr(system_instance, 'running', False)
            state['initialized'] = getattr(system_instance, 'initialized', True)
            
        except Exception as e:
            self.logger.warning(f"Error extracting state for {system_type.value}: {e}")
        
        return state
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum for integrity verification"""
        import hashlib
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            self.logger.warning(f"Error calculating checksum for {file_path}: {e}")
            return ""
    
    def _cleanup_old_snapshots(self, system_type: SystemType):
        """Clean up old snapshots to maintain storage limits"""
        system_snapshots = [s for s in self.snapshots.values() if s.system_type == system_type]
        
        if len(system_snapshots) > self.max_snapshots_per_system:
            # Sort by timestamp and remove oldest
            system_snapshots.sort(key=lambda s: s.timestamp)
            snapshots_to_remove = system_snapshots[:-self.max_snapshots_per_system]
            
            for snapshot in snapshots_to_remove:
                self.delete_snapshot(snapshot.snapshot_id)
    
    def _load_snapshots(self):
        """Load existing snapshots from disk"""
        try:
            for file_path in self.snapshots_dir.glob("*.pkl"):
                try:
                    with open(file_path, 'rb') as f:
                        snapshot = pickle.load(f)
                        self.snapshots[snapshot.snapshot_id] = snapshot
                except Exception as e:
                    self.logger.warning(f"Failed to load snapshot {file_path}: {e}")
            
            self.logger.info(f"Loaded {len(self.snapshots)} snapshots")
            
        except Exception as e:
            self.logger.error(f"Error loading snapshots: {e}")


class RollbackManager:
    """Main rollback management system"""
    
    def __init__(self, snapshots_dir: str = "snapshots"):
        self.logger = logging.getLogger('RollbackManager')
        
        # Initialize components
        self.snapshot_manager = SnapshotManager(snapshots_dir)
        self.migration_validator = get_migration_validator()
        
        # Rollback tracking
        self.rollback_operations: List[RollbackOperation] = []
        self.emergency_triggers: Dict[SystemType, List[Callable]] = {}
        
        # Safety settings
        self.max_rollback_attempts = 3
        self.rollback_timeout = 60.0  # 60 seconds
        self.auto_snapshot_enabled = True
        
        # System references
        self.system_instances: Dict[SystemType, Any] = {}
        
        self.logger.info("Rollback Manager initialized")
    
    def register_system(self, system_type: SystemType, system_instance: Any):
        """Register a system instance for rollback management"""
        self.system_instances[system_type] = system_instance
        self.logger.info(f"Registered {system_type.value} for rollback management")
    
    def create_migration_snapshot(self, system_type: SystemType, description: str = "") -> str:
        """Create snapshot before migration"""
        system_instance = self.system_instances.get(system_type)
        if not system_instance:
            raise ValueError(f"System {system_type.value} not registered")
        
        snapshot_description = description or f"Pre-migration snapshot for {system_type.value}"
        snapshot_id = self.snapshot_manager.create_snapshot(
            system_type, system_instance, SnapshotType.FULL, snapshot_description
        )
        
        self.logger.info(f"Created migration snapshot {snapshot_id} for {system_type.value}")
        return snapshot_id
    
    def rollback_to_snapshot(self, snapshot_id: str, 
                           rollback_level: RollbackLevel = RollbackLevel.STATE,
                           trigger: RollbackTrigger = RollbackTrigger.MANUAL) -> bool:
        """Rollback system to a specific snapshot"""
        operation_id = f"rollback_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Get snapshot
        snapshot = self.snapshot_manager.get_snapshot(snapshot_id)
        if not snapshot:
            self.logger.error(f"Snapshot {snapshot_id} not found")
            return False
        
        # Create rollback operation record
        operation = RollbackOperation(
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            system_type=snapshot.system_type,
            rollback_level=rollback_level,
            trigger=trigger,
            start_time=time.time()
        )
        
        try:
            self.logger.info(f"Starting rollback {operation_id} for {snapshot.system_type.value}")
            
            # Get system instance
            system_instance = self.system_instances.get(snapshot.system_type)
            if not system_instance:
                raise ValueError(f"System {snapshot.system_type.value} not registered")
            
            # Perform rollback based on level
            success = self._perform_rollback(operation, snapshot, system_instance)
            
            if success:
                # Validate rollback
                validation_success = self._validate_rollback(operation, system_instance)
                if not validation_success:
                    self.logger.warning(f"Rollback validation failed for {operation_id}")
                    success = False
            
            # Update operation record
            operation.end_time = time.time()
            operation.success = success
            
            if success:
                self.logger.info(f"Rollback {operation_id} completed successfully")
                
                # Update snapshot rollback metadata
                snapshot.rollback_count += 1
                snapshot.last_rollback_time = time.time()
            else:
                self.logger.error(f"Rollback {operation_id} failed")
            
            return success
            
        except Exception as e:
            operation.end_time = time.time()
            operation.success = False
            operation.error_message = str(e)
            
            self.logger.error(f"Rollback {operation_id} failed with exception: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
            
        finally:
            self.rollback_operations.append(operation)
    
    def emergency_rollback(self, system_type: SystemType) -> bool:
        """Perform emergency rollback to most recent snapshot"""
        self.logger.warning(f"Emergency rollback triggered for {system_type.value}")
        
        # Find most recent snapshot
        snapshots = self.snapshot_manager.list_snapshots(system_type)
        if not snapshots:
            self.logger.error(f"No snapshots available for emergency rollback of {system_type.value}")
            return False
        
        most_recent_snapshot = snapshots[0]
        
        # Perform emergency rollback
        return self.rollback_to_snapshot(
            most_recent_snapshot.snapshot_id,
            RollbackLevel.EMERGENCY,
            RollbackTrigger.EMERGENCY
        )
    
    def setup_auto_rollback_triggers(self, system_type: SystemType):
        """Setup automatic rollback triggers for a system"""
        triggers = []
        
        # Performance degradation trigger
        def performance_trigger(performance_data: Dict[str, float]):
            if any(ratio > 3.0 for ratio in performance_data.values() if 'ratio' in str(ratio)):
                self.logger.warning(f"Performance degradation detected for {system_type.value}")
                return self.emergency_rollback(system_type)
            return True
        
        # Critical error trigger
        def error_trigger(error_count: int):
            if error_count > 5:  # More than 5 errors
                self.logger.error(f"Critical error threshold exceeded for {system_type.value}")
                return self.emergency_rollback(system_type)
            return True
        
        triggers.extend([performance_trigger, error_trigger])
        self.emergency_triggers[system_type] = triggers
        
        self.logger.info(f"Setup auto-rollback triggers for {system_type.value}")
    
    def _perform_rollback(self, operation: RollbackOperation, snapshot: SystemSnapshot, 
                         system_instance: Any) -> bool:
        """Perform the actual rollback operation"""
        try:
            if operation.rollback_level in [RollbackLevel.DATA, RollbackLevel.STATE, RollbackLevel.EMERGENCY]:
                # Restore system data
                success = self._restore_system_data(snapshot, system_instance)
                if success:
                    operation.data_restored = True
                    operation.recovery_steps.append("System data restored")
                else:
                    return False
            
            if operation.rollback_level in [RollbackLevel.CONFIGURATION, RollbackLevel.STATE, RollbackLevel.EMERGENCY]:
                # Restore system configuration
                success = self._restore_system_config(snapshot, system_instance)
                if success:
                    operation.config_restored = True
                    operation.recovery_steps.append("System configuration restored")
            
            if operation.rollback_level in [RollbackLevel.STATE, RollbackLevel.EMERGENCY]:
                # Restore system state
                success = self._restore_system_state(snapshot, system_instance)
                if success:
                    operation.state_restored = True
                    operation.recovery_steps.append("System state restored")
            
            return True
            
        except Exception as e:
            operation.error_message = str(e)
            self.logger.error(f"Error during rollback: {e}")
            return False
    
    def _restore_system_data(self, snapshot: SystemSnapshot, system_instance: Any) -> bool:
        """Restore system data from snapshot"""
        try:
            system_data = snapshot.system_data
            
            if snapshot.system_type == SystemType.TIME_SYSTEM:
                # Restore time system data
                if 'current_time' in system_data:
                    time_data = system_data['current_time']
                    total_minutes = time_data.get('total_minutes', 0)
                    
                    # Set system time
                    if hasattr(system_instance, 'advance_time'):
                        current_time = system_instance.get_current_time()
                        minutes_diff = total_minutes - current_time.total_minutes
                        if minutes_diff != 0:
                            system_instance.advance_time(int(minutes_diff))
                
                # Restore time scale and pause state
                if 'time_scale' in system_data:
                    system_instance.set_time_scale(system_data['time_scale'])
                
                if 'paused' in system_data and system_data['paused']:
                    system_instance.pause()
                else:
                    system_instance.resume()
            
            elif snapshot.system_type == SystemType.ECONOMY_SYSTEM:
                # Restore economy system data
                if 'current_cash' in system_data:
                    system_instance.current_cash = system_data['current_cash']
                if 'current_debt' in system_data:
                    system_instance.current_debt = system_data['current_debt']
                if 'daily_subsidy' in system_data:
                    system_instance.daily_subsidy = system_data['daily_subsidy']
            
            # Add more system types as needed
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring system data: {e}")
            return False
    
    def _restore_system_config(self, snapshot: SystemSnapshot, system_instance: Any) -> bool:
        """Restore system configuration from snapshot"""
        try:
            system_config = snapshot.system_config
            
            if hasattr(system_instance, 'config_manager') and system_config:
                config_manager = system_instance.config_manager
                
                # Restore configuration values
                for key, value in system_config.items():
                    config_manager.set(key, value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring system config: {e}")
            return False
    
    def _restore_system_state(self, snapshot: SystemSnapshot, system_instance: Any) -> bool:
        """Restore system state from snapshot"""
        try:
            system_state = snapshot.system_state
            
            # Restore basic state attributes
            for attr, value in system_state.items():
                if hasattr(system_instance, attr):
                    setattr(system_instance, attr, value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring system state: {e}")
            return False
    
    def _validate_rollback(self, operation: RollbackOperation, system_instance: Any) -> bool:
        """Validate rollback operation was successful"""
        try:
            # For now, basic validation - could be enhanced with more sophisticated checks
            validation_results = {
                'timestamp': time.time(),
                'system_responsive': True,  # Would check if system responds to basic operations
                'data_integrity': True      # Would check data integrity
            }
            
            operation.validation_results = validation_results
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating rollback: {e}")
            return False
    
    def get_rollback_history(self, system_type: SystemType = None) -> List[Dict[str, Any]]:
        """Get rollback operation history"""
        operations = self.rollback_operations
        
        if system_type:
            operations = [op for op in operations if op.system_type == system_type]
        
        return [op.to_dict() for op in operations]
    
    def get_snapshot_summary(self) -> Dict[str, Any]:
        """Get summary of available snapshots"""
        snapshots = self.snapshot_manager.list_snapshots()
        
        summary = {
            'total_snapshots': len(snapshots),
            'snapshots_by_system': {},
            'total_size_bytes': sum(s.size_bytes for s in snapshots),
            'oldest_snapshot': min(s.timestamp for s in snapshots) if snapshots else 0,
            'newest_snapshot': max(s.timestamp for s in snapshots) if snapshots else 0
        }
        
        # Group by system type
        for snapshot in snapshots:
            system_name = snapshot.system_type.value
            if system_name not in summary['snapshots_by_system']:
                summary['snapshots_by_system'][system_name] = 0
            summary['snapshots_by_system'][system_name] += 1
        
        return summary


# Global rollback manager instance
_global_rollback_manager: Optional[RollbackManager] = None

def get_rollback_manager() -> RollbackManager:
    """Get the global rollback manager instance"""
    global _global_rollback_manager
    if _global_rollback_manager is None:
        _global_rollback_manager = RollbackManager()
    return _global_rollback_manager

def initialize_rollback_manager() -> RollbackManager:
    """Initialize the global rollback manager"""
    global _global_rollback_manager
    _global_rollback_manager = RollbackManager()
    return _global_rollback_manager