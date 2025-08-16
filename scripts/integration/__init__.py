"""
Phase 2 Integration Package - Gradual Migration Framework

This package provides comprehensive tools for gradually migrating from legacy pygame
systems to advanced Phase 2 systems while maintaining game stability and user experience.

Components:
- SystemBridge: Routes requests between legacy and Phase 2 systems
- DataAdapter: Translates data formats between system architectures  
- MigrationValidator: Validates migration integrity and performance
- RollbackManager: Provides safe rollback and recovery mechanisms
- IntegrationController: Master coordinator for the entire migration process

Usage:
    from scripts.integration import get_integration_controller
    
    controller = get_integration_controller()
    controller.initialize_migration_infrastructure()
    
    # Migrate time system
    success = controller.migrate_system('time_system')
"""

from .system_bridge import get_system_bridge, initialize_system_bridge, SystemType, MigrationStatus
from .data_adapter import get_data_adapter, initialize_data_adapter  
from .migration_validator import get_migration_validator, initialize_migration_validator
from .rollback_manager import get_rollback_manager, initialize_rollback_manager
from .integration_controller import get_integration_controller, initialize_integration_controller, MigrationPhase

__all__ = [
    'get_system_bridge',
    'initialize_system_bridge',
    'get_data_adapter', 
    'initialize_data_adapter',
    'get_migration_validator',
    'initialize_migration_validator',
    'get_rollback_manager',
    'initialize_rollback_manager',
    'get_integration_controller',
    'initialize_integration_controller',
    'SystemType',
    'MigrationStatus',
    'MigrationPhase'
]