"""
Integrated Game Manager - Phase 2 Migration-Enabled Game Coordinator

This is an enhanced version of the main GameManager that supports gradual migration
between legacy pygame systems and advanced Phase 2 systems. It provides seamless
integration capabilities while maintaining full backward compatibility.

Key Features:
- Gradual system migration with zero downtime
- Automatic system routing (legacy vs Phase 2)
- Migration health monitoring and reporting
- Emergency rollback capabilities
- Progressive feature enablement
- Comprehensive migration logging

Migration Strategy:
- Phase 0: Foundation infrastructure (completed)
- Phase 1: Time system migration (current)
- Phase 2: Economy system migration
- Phase 3: Employee system migration  
- Phase 4: Crop system migration
- Phase 5: Final integration (buildings, save/load)

Usage:
    # Create integrated game manager
    game = IntegratedGameManager()
    
    # Enable migration infrastructure
    game.initialize_migration()
    
    # Migrate specific systems
    game.migrate_time_system()
    
    # Run game normally
    game.run()
"""

import pygame
import sys
import logging
from typing import Dict, Any, Optional
import traceback

# Import legacy systems
from ..core.config import *
from ..core.event_system import EventSystem
from ..core.grid_manager import GridManager
from ..core.time_manager import TimeManager as LegacyTimeManager
from ..core.inventory_manager import InventoryManager
from ..employee.employee_manager import EmployeeManager as LegacyEmployeeManager
from ..employee.simple_hiring_system import SimpleHiringSystem
from ..economy.economy_manager import EconomyManager as LegacyEconomyManager
from ..buildings.building_manager import BuildingManager
from ..ui.ui_manager import UIManager
from ..core.save_manager import SaveManager
from ..contracts.contract_manager import ContractManager
from ..core.weather_manager import WeatherManager as LegacyWeatherManager
from ..tasks.task_integration import TaskSystemIntegration

# Import Phase 2 integration framework
from .integration_controller import get_integration_controller, MigrationPhase
from .system_bridge import SystemType


class IntegratedGameManager:
    """Enhanced game manager with Phase 2 migration capabilities"""
    
    def __init__(self):
        """Initialize the integrated game manager"""
        self.logger = logging.getLogger('IntegratedGameManager')
        
        # Initialize Pygame display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Farm Simulation Game - Phase 2 Integration")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Migration system
        self.integration_controller = get_integration_controller()
        self.migration_enabled = False
        
        # Initialize event system (must be first)
        self.event_system = EventSystem()
        
        # Initialize core legacy systems
        self._initialize_legacy_systems()
        
        # Register legacy systems with migration framework
        self._register_legacy_systems()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Migration status
        self.migrated_systems = set()
        self.migration_health_last_check = 0.0
        self.migration_health_interval = 5.0  # Check every 5 seconds
        
        self.logger.info("Integrated Game Manager initialized successfully!")
    
    def _initialize_legacy_systems(self):
        """Initialize all legacy pygame systems"""
        try:
            # Core systems
            self.grid_manager = GridManager(self.event_system)
            self.legacy_time_manager = LegacyTimeManager(self.event_system)
            
            # Connect time manager to grid manager for time-based crop growth
            self.grid_manager.time_manager = self.legacy_time_manager
            
            # Economy and inventory
            self.inventory_manager = InventoryManager(self.event_system)
            self.legacy_economy_manager = LegacyEconomyManager(self.event_system)
            
            # Buildings
            self.building_manager = BuildingManager(
                self.event_system, 
                self.legacy_economy_manager, 
                self.inventory_manager, 
                self.grid_manager
            )
            
            # Connect grid manager to building manager for spatial benefits
            self.grid_manager.building_manager = self.building_manager
            
            # Employee systems
            self.legacy_employee_manager = LegacyEmployeeManager(
                self.event_system, 
                self.grid_manager, 
                time_manager=self.legacy_time_manager
            )
            
            # Hiring system
            self.hiring_system = SimpleHiringSystem(
                self.event_system, 
                self.legacy_economy_manager, 
                self.legacy_employee_manager
            )
            
            # Task integration
            self.task_integration = TaskSystemIntegration(
                self.event_system, 
                self.grid_manager, 
                self.legacy_employee_manager
            )
            
            # Connect employee manager to inventory manager
            self.legacy_employee_manager.set_inventory_manager(self.inventory_manager)
            
            # UI system
            self.ui_manager = UIManager(self.event_system, self.screen)
            
            # Connect task integration to UI manager
            if hasattr(self, 'task_integration'):
                self.ui_manager.set_task_integration(self.task_integration)
            
            # Contract system
            self.contract_manager = ContractManager(
                self.event_system, 
                self.legacy_economy_manager, 
                self.legacy_time_manager, 
                self.inventory_manager
            )
            
            # Specialization system
            from ..core.specialization_manager import SpecializationManager
            self.specialization_manager = SpecializationManager(self.event_system)
            
            # Weather system
            self.legacy_weather_manager = LegacyWeatherManager(
                self.event_system, 
                self.legacy_time_manager
            )
            
            # Connect grid manager to game manager for specialization access
            self.grid_manager.game_manager = self
            
            # Save/load system
            self.save_manager = SaveManager(self.event_system, self)
            
            self.logger.info("Legacy systems initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize legacy systems: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _register_legacy_systems(self):
        """Register legacy systems with the migration framework"""
        try:
            # Register systems for migration
            self.integration_controller.register_legacy_system(
                SystemType.TIME_SYSTEM, self.legacy_time_manager
            )
            self.integration_controller.register_legacy_system(
                SystemType.ECONOMY_SYSTEM, self.legacy_economy_manager
            )
            self.integration_controller.register_legacy_system(
                SystemType.EMPLOYEE_SYSTEM, self.legacy_employee_manager
            )
            
            self.logger.info("Legacy systems registered with migration framework")
            
        except Exception as e:
            self.logger.error(f"Failed to register legacy systems: {e}")
            raise
    
    def _setup_event_handlers(self):
        """Setup event handlers for game events and migration events"""
        try:
            # Game event handlers
            self.event_system.subscribe('game_quit', self._handle_quit)
            self.event_system.subscribe('process_specialization_choice', self._handle_specialization_choice)
            self.event_system.subscribe('hire_applicant_confirmed', self._handle_hire_confirmed)
            
            # Building placement events
            self.building_placement_mode = False
            self.pending_building_type = None
            
            self.event_system.subscribe('enter_building_placement_mode', self._handle_enter_placement_mode)
            self.event_system.subscribe('exit_building_placement_mode', self._handle_exit_placement_mode)
            self.event_system.subscribe('building_placement_confirmed', self._handle_building_placement_confirmed)
            
            # Migration event handlers
            self.integration_controller.add_migration_callback(
                'migration_completed', self._on_migration_completed
            )
            self.integration_controller.add_migration_callback(
                'migration_failed', self._on_migration_failed
            )
            self.integration_controller.add_migration_callback(
                'emergency_rollback', self._on_emergency_rollback
            )
            
            self.logger.info("Event handlers setup complete")
            
        except Exception as e:
            self.logger.error(f"Failed to setup event handlers: {e}")
            raise
    
    def initialize_migration(self) -> bool:
        """Initialize the migration infrastructure"""
        try:
            self.logger.info("Initializing Phase 2 migration infrastructure...")
            
            # Initialize migration infrastructure
            success = self.integration_controller.initialize_migration_infrastructure()
            
            if success:
                self.migration_enabled = True
                self.logger.info("Migration infrastructure initialized successfully")
                
                # Optionally auto-migrate time system
                if self._should_auto_migrate_time():
                    self.logger.info("Auto-migrating time system...")
                    self.migrate_time_system()
                
                return True
            else:
                self.logger.error("Failed to initialize migration infrastructure")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception during migration initialization: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def migrate_time_system(self) -> bool:
        """Migrate from legacy time system to Phase 2 time system"""
        try:
            if not self.migration_enabled:
                self.logger.warning("Migration not enabled, cannot migrate time system")
                return False
            
            self.logger.info("Starting time system migration...")
            
            # Migrate time system
            success = self.integration_controller.migrate_system(SystemType.TIME_SYSTEM)
            
            if success:
                self.migrated_systems.add(SystemType.TIME_SYSTEM)
                self.logger.info("Time system migration completed successfully")
                
                # Update UI to show migration status
                self._update_ui_migration_status()
                
                return True
            else:
                self.logger.error("Time system migration failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception during time system migration: {e}")
            return False
    
    def migrate_economy_system(self) -> bool:
        """Migrate from legacy economy system to Phase 2 economy system"""
        try:
            if not self.migration_enabled:
                self.logger.warning("Migration not enabled, cannot migrate economy system")
                return False
            
            self.logger.info("Starting economy system migration...")
            
            # Check if time system is migrated first (dependency)
            if SystemType.TIME_SYSTEM not in self.migrated_systems:
                self.logger.warning("Time system must be migrated before economy system")
                return False
            
            # Migrate economy system
            success = self.integration_controller.migrate_system(SystemType.ECONOMY_SYSTEM)
            
            if success:
                self.migrated_systems.add(SystemType.ECONOMY_SYSTEM)
                self.logger.info("Economy system migration completed successfully")
                
                # Update UI to show migration status
                self._update_ui_migration_status()
                
                return True
            else:
                self.logger.error("Economy system migration failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception during economy system migration: {e}")
            return False
    
    def rollback_system(self, system_type: SystemType) -> bool:
        """Rollback a system to legacy implementation"""
        try:
            self.logger.info(f"Rolling back {system_type.value} to legacy")
            
            success = self.integration_controller.rollback_system(system_type)
            
            if success:
                self.migrated_systems.discard(system_type)
                self.logger.info(f"Successfully rolled back {system_type.value}")
                
                # Update UI to show migration status
                self._update_ui_migration_status()
                
                return True
            else:
                self.logger.error(f"Failed to rollback {system_type.value}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception during {system_type.value} rollback: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get comprehensive migration status"""
        try:
            # Get migration report from controller
            report = self.integration_controller.get_migration_report()
            
            # Add local status information
            report['local_status'] = {
                'migration_enabled': self.migration_enabled,
                'migrated_systems': [s.value for s in self.migrated_systems],
                'legacy_systems_active': len(SystemType) - len(self.migrated_systems),
                'phase2_systems_active': len(self.migrated_systems)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error getting migration status: {e}")
            return {'error': str(e)}
    
    def run(self):
        """Main game loop with migration support"""
        self.logger.info("Starting integrated game loop...")
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            # Handle events
            self._handle_events()
            
            # Update all systems
            self._update(dt)
            
            # Check migration health periodically
            self._check_migration_health()
            
            # Render everything
            self._render()
        
        self.logger.info("Integrated game loop ended.")
    
    def _handle_events(self):
        """Process pygame events and forward to event system"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.event_system.emit('game_quit', {})
            
            # Forward event to UI system for processing
            self.ui_manager.handle_event(event)
            
            # Handle mouse events for employee/grid interaction
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.legacy_employee_manager.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                # Always handle motion for building placement preview
                self.legacy_employee_manager.handle_mouse_motion(event.pos)
                
                # Handle drag selection only when mouse is pressed and not in building placement mode
                if any(pygame.mouse.get_pressed()) and not self.building_placement_mode:
                    self.legacy_employee_manager.handle_mouse_drag(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.legacy_employee_manager.handle_mouse_up(event.pos, event.button)
            elif event.type == pygame.MOUSEWHEEL:
                # Forward mouse wheel events to grid manager for zoom functionality
                self.grid_manager.handle_mouse_wheel(pygame.mouse.get_pos(), event.y)
            elif event.type == pygame.KEYDOWN:
                # Check for building placement cancellation
                if event.key == pygame.K_ESCAPE and self.building_placement_mode:
                    self.event_system.emit('exit_building_placement_mode', {})
                # Migration hotkeys
                elif event.key == pygame.K_F5:  # F5 to migrate time system
                    self.migrate_time_system()
                elif event.key == pygame.K_F6:  # F6 to migrate economy system
                    self.migrate_economy_system()
                elif event.key == pygame.K_F7:  # F7 to get migration status
                    status = self.get_migration_status()
                    self.logger.info(f"Migration Status: {status['local_status']}")
                else:
                    self.legacy_employee_manager.handle_keyboard_input(event.key)
    
    def _update(self, dt):
        """Update all game systems (using active system versions)"""
        try:
            # Update systems in dependency order
            # Use Phase 2 time system if migrated, otherwise legacy
            if SystemType.TIME_SYSTEM in self.migrated_systems:
                # Phase 2 time system update is handled internally
                pass
            else:
                self.legacy_time_manager.update(dt)
            
            # Weather (currently always legacy)
            self.legacy_weather_manager.update()
            
            # Grid and world state
            self.grid_manager.update(dt)
            self.inventory_manager.update(dt)
            self.building_manager.update(dt)
            self.contract_manager.update(dt)
            
            # Employee systems (currently always legacy)
            self.hiring_system.update(dt)
            self.legacy_employee_manager.update(dt)
            
            # Economy (use Phase 2 if migrated, otherwise legacy)
            if SystemType.ECONOMY_SYSTEM in self.migrated_systems:
                # Phase 2 economy system update is handled internally
                pass
            else:
                self.legacy_economy_manager.update(dt)
            
            # UI and save systems
            self.ui_manager.update(dt)
            self.save_manager.update(dt)
            
            # Process any pending events
            self.event_system.process_events()
            
        except Exception as e:
            self.logger.error(f"Error during system update: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _render(self):
        """Render the game world and UI"""
        try:
            # Clear screen
            self.screen.fill(COLORS['background'])
            
            # Render systems in order
            self.grid_manager.render(self.screen)
            self.legacy_employee_manager.render(self.screen)
            self.ui_manager.render(self.screen)
            
            # Render migration status if enabled
            self._render_migration_overlay()
            
            # Update display
            pygame.display.flip()
            
        except Exception as e:
            self.logger.error(f"Error during rendering: {e}")
    
    def _render_migration_overlay(self):
        """Render migration status overlay"""
        if not self.migration_enabled:
            return
        
        try:
            # Simple text overlay showing migration status
            font = pygame.font.Font(None, 24)
            
            # Show migrated systems
            if self.migrated_systems:
                migrated_text = f"Phase 2: {', '.join(s.value for s in self.migrated_systems)}"
                text_surface = font.render(migrated_text, True, (0, 255, 0))
                self.screen.blit(text_surface, (10, 10))
            
            # Show migration controls
            controls_text = "F5: Migrate Time | F6: Migrate Economy | F7: Migration Status"
            controls_surface = font.render(controls_text, True, (255, 255, 255))
            self.screen.blit(controls_surface, (10, WINDOW_HEIGHT - 30))
            
        except Exception as e:
            self.logger.warning(f"Error rendering migration overlay: {e}")
    
    def _check_migration_health(self):
        """Periodically check migration health"""
        if not self.migration_enabled:
            return
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        if current_time - self.migration_health_last_check > self.migration_health_interval:
            try:
                health = self.integration_controller.get_migration_health()
                
                # Log critical issues
                if health.critical_issues:
                    for issue in health.critical_issues:
                        self.logger.warning(f"Migration health issue: {issue}")
                
                # Trigger emergency actions if needed
                if health.status.value == 'critical':
                    self.logger.error("Critical migration health detected!")
                    # Could trigger emergency rollback here
                
                self.migration_health_last_check = current_time
                
            except Exception as e:
                self.logger.warning(f"Error checking migration health: {e}")
    
    def _should_auto_migrate_time(self) -> bool:
        """Check if time system should be auto-migrated"""
        # For demo purposes, auto-migrate time system
        # In production, this could be based on user preference or configuration
        return True
    
    def _update_ui_migration_status(self):
        """Update UI to reflect current migration status"""
        try:
            # Could send event to UI manager to update migration status display
            self.event_system.emit('migration_status_updated', {
                'migrated_systems': [s.value for s in self.migrated_systems],
                'migration_enabled': self.migration_enabled
            })
        except Exception as e:
            self.logger.warning(f"Error updating UI migration status: {e}")
    
    # Migration event handlers
    def _on_migration_completed(self, data: Dict[str, Any]):
        """Handle successful migration completion"""
        system_type = data.get('system_type', '')
        self.logger.info(f"Migration completed event: {system_type}")
    
    def _on_migration_failed(self, data: Dict[str, Any]):
        """Handle migration failure"""
        system_type = data.get('system_type', '')
        self.logger.error(f"Migration failed event: {system_type}")
    
    def _on_emergency_rollback(self, data: Dict[str, Any]):
        """Handle emergency rollback"""
        system_type = data.get('system_type', '')
        self.logger.warning(f"Emergency rollback event: {system_type}")
    
    # Legacy event handlers (preserved from original game manager)
    def _handle_quit(self, event_data):
        """Handle quit event"""
        # Cleanup task integration system
        if hasattr(self, 'task_integration'):
            self.task_integration.cleanup()
        
        self.running = False
        self.logger.info("Quit event received.")
    
    def _handle_hire_confirmed(self, event_data):
        """Handle confirmed hiring request"""
        self.logger.info("Hire request processed")
    
    def _handle_enter_placement_mode(self, event_data):
        """Handle entering building placement mode"""
        building_type = event_data.get('building_type')
        if building_type:
            self.building_placement_mode = True
            self.pending_building_type = building_type
            
            # Notify grid manager to show placement preview
            self.event_system.emit('building_placement_preview_start', {
                'building_type': building_type
            })
            
            self.logger.info(f"Entered building placement mode for {building_type}")
    
    def _handle_exit_placement_mode(self, event_data):
        """Handle exiting building placement mode"""
        if self.building_placement_mode:
            self.building_placement_mode = False
            building_type = self.pending_building_type
            self.pending_building_type = None
            
            # Notify grid manager to hide placement preview
            self.event_system.emit('building_placement_preview_stop', {})
            
            self.logger.info(f"Exited building placement mode for {building_type}")
    
    def _handle_building_placement_confirmed(self, event_data):
        """Handle confirmed building placement at specific location"""
        if not self.building_placement_mode or not self.pending_building_type:
            return
            
        x = event_data.get('x')
        y = event_data.get('y')
        building_type = self.pending_building_type
        
        if x is not None and y is not None:
            # Try to purchase building at specified location
            success = self.building_manager.purchase_building_at(building_type, x, y)
            
            if success:
                # Exit placement mode on successful placement
                self.event_system.emit('exit_building_placement_mode', {})
                self.logger.info(f"Successfully placed {building_type} at ({x}, {y})")
            else:
                self.logger.info(f"Failed to place {building_type} at ({x}, {y})")
    
    def _handle_specialization_choice(self, event_data: Dict[str, Any]):
        """Handle specialization selection with economy integration"""
        specialization_id = event_data.get('specialization_id', '')
        manager = event_data.get('manager')
        
        if not manager:
            self.logger.error("Error: No specialization manager provided")
            return
        
        # Get current cash from appropriate economy manager
        if SystemType.ECONOMY_SYSTEM in self.migrated_systems:
            # Use Phase 2 economy system
            phase2_economy = self.integration_controller.system_bridge.get_active_system(SystemType.ECONOMY_SYSTEM)
            current_cash = phase2_economy.current_cash if phase2_economy else 0.0
        else:
            # Use legacy economy manager
            current_cash = self.legacy_economy_manager.get_current_balance()
        
        # Attempt to choose specialization
        result = manager.choose_specialization(specialization_id, current_cash)
        
        if result['success']:
            # Deduct cost from appropriate economy system
            cost = result['cost']
            if cost > 0:
                if SystemType.ECONOMY_SYSTEM in self.migrated_systems:
                    # Use Phase 2 economy system
                    phase2_economy = self.integration_controller.system_bridge.get_active_system(SystemType.ECONOMY_SYSTEM)
                    if phase2_economy:
                        # Would need to add transaction to Phase 2 system
                        pass
                else:
                    # Use legacy economy manager
                    self.legacy_economy_manager.spend_money(cost, f"Farm specialization: {result['specialization']['name']}", "specialization")
            
            # Notify UI of successful specialization
            self.event_system.emit('specialization_chosen_successfully', {
                'specialization': result['specialization'],
                'cost': cost
            })
            
            self.logger.info(f"Successfully specialized as {result['specialization']['name']} for ${cost}")
        else:
            # Notify UI of failure
            reason = result.get('reason', 'Unknown error')
            self.event_system.emit('specialization_choice_failed', {
                'reason': reason,
                'cost': result.get('cost', 0)
            })
            
            self.logger.info(f"Failed to specialize: {reason}")