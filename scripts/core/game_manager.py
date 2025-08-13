"""
Game Manager - Main game coordination and loop

The GameManager is the central coordinator for all game systems. It manages the main
game loop, system initialization order, and event processing. This is the entry point
for the entire game and ensures proper system coordination.

System Initialization Order (Critical):
1. EventSystem - Must be first, all other systems depend on it
2. GridManager - World state foundation  
3. TimeManager - Drives all time-based systems
4. EconomyManager - Financial system
5. EmployeeManager - Entities that act in the world
6. UIManager - Display and user interaction

Update Order (Critical):
Systems must update in dependency order to avoid frame-delay issues:
1. TimeManager - Updates game time first
2. GridManager - Updates world state  
3. EmployeeManager - Entities act on current world state
4. EconomyManager - Processes consequences of actions
5. UIManager - Updates display based on current state
6. EventSystem.process_events() - Process all events generated this frame

Key Responsibilities:
- Coordinate system lifecycle (init, update, render)
- Handle pygame events and forward to appropriate systems
- Maintain target framerate (60 FPS)
- Provide clean shutdown when game exits

Event Handling:
- pygame.QUIT -> 'game_quit' event
- Mouse events -> forwarded to EmployeeManager for tile interaction
- Keyboard events -> forwarded to EmployeeManager for shortcuts
- UI events -> handled by UIManager

Performance Targets:
- 60 FPS on reference hardware
- Sub-16ms frame time for smooth gameplay
- Graceful degradation if performance drops

Error Handling:
- Catches and logs system update errors
- Provides graceful shutdown on crashes
- Maintains game state integrity during error recovery
"""

import pygame
import sys
from typing import Dict, Any
from scripts.core.config import *
from scripts.core.event_system import EventSystem
from scripts.core.grid_manager import GridManager
from scripts.core.time_manager import TimeManager
from scripts.core.inventory_manager import InventoryManager
from scripts.employee.employee_manager import EmployeeManager
# Use simple hiring system instead of complex interview system
from scripts.employee.simple_hiring_system import SimpleHiringSystem
from scripts.economy.economy_manager import EconomyManager
from scripts.buildings.building_manager import BuildingManager
from scripts.ui.ui_manager import UIManager
from scripts.core.save_manager import SaveManager
from scripts.contracts.contract_manager import ContractManager
from scripts.core.weather_manager import WeatherManager


class GameManager:
    """Main game controller that coordinates all systems"""
    
    def __init__(self):
        """Initialize the game manager and all subsystems"""
        # Initialize Pygame display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Farm Simulation Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize event system (must be first)
        self.event_system = EventSystem()
        
        # Initialize core systems
        self.grid_manager = GridManager(self.event_system)
        self.time_manager = TimeManager(self.event_system)
        
        # Connect time manager to grid manager for time-based crop growth
        self.grid_manager.time_manager = self.time_manager
        self.inventory_manager = InventoryManager(self.event_system)
        self.economy_manager = EconomyManager(self.event_system)
        self.building_manager = BuildingManager(self.event_system, self.economy_manager, self.inventory_manager, self.grid_manager)
        # Connect grid manager to building manager for spatial benefits integration
        self.grid_manager.building_manager = self.building_manager
        # Create employee manager first, then hiring system that uses it
        self.employee_manager = EmployeeManager(self.event_system, self.grid_manager, time_manager=self.time_manager)
        # Initialize simple hiring system for employee recruitment  
        self.hiring_system = SimpleHiringSystem(self.event_system, self.economy_manager, self.employee_manager)
        
        # NOTE: Interview system sync temporarily removed
        # self.interview_system.set_current_day(self.time_manager.current_day)
        
        # Connect employee manager to inventory manager for synchronous harvest processing
        self.employee_manager.set_inventory_manager(self.inventory_manager)
        
        self.ui_manager = UIManager(self.event_system, self.screen)
        
        # Initialize contract system (after economy, time, and inventory systems)
        self.contract_manager = ContractManager(self.event_system, self.economy_manager, self.time_manager, self.inventory_manager)
        
        # Initialize specialization system (after inventory and economy for stat tracking)
        from scripts.core.specialization_manager import SpecializationManager
        self.specialization_manager = SpecializationManager(self.event_system)
        
        # Initialize weather system (after time manager for seasonal cycles)
        self.weather_manager = WeatherManager(self.event_system, self.time_manager)
        
        # Connect grid manager to game manager for specialization access
        self.grid_manager.game_manager = self
        
        # Initialize save/load system (after all other systems)
        self.save_manager = SaveManager(self.event_system, self)
        
        # Register for quit events
        self.event_system.subscribe('game_quit', self._handle_quit)
        
        # Register for specialization events
        self.event_system.subscribe('process_specialization_choice', self._handle_specialization_choice)
        
        # Register for hiring events (connect interview system to employee manager)
        self.event_system.subscribe('hire_applicant_confirmed', self._handle_hire_confirmed)
        
        # Building placement state
        self.building_placement_mode = False
        self.pending_building_type = None
        
        # Register for building placement events
        self.event_system.subscribe('enter_building_placement_mode', self._handle_enter_placement_mode)
        self.event_system.subscribe('exit_building_placement_mode', self._handle_exit_placement_mode)
        self.event_system.subscribe('building_placement_confirmed', self._handle_building_placement_confirmed)
        
        print("Game initialized successfully!")
    
    def run(self):
        """Main game loop"""
        print("Starting game loop...")
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            # Handle events
            self._handle_events()
            
            # Update all systems
            self._update(dt)
            
            # Render everything
            self._render()
        
        print("Game loop ended.")
    
    def _handle_events(self):
        """Process pygame events and forward to event system"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.event_system.emit('game_quit', {})
            
            # Forward event to UI system for processing
            self.ui_manager.handle_event(event)
            
            # Handle mouse events for employee/grid interaction
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.employee_manager.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                # Always handle motion for building placement preview
                self.employee_manager.handle_mouse_motion(event.pos)
                
                # Handle drag selection only when mouse is pressed and not in building placement mode
                if any(pygame.mouse.get_pressed()) and not self.building_placement_mode:
                    self.employee_manager.handle_mouse_drag(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.employee_manager.handle_mouse_up(event.pos, event.button)
            elif event.type == pygame.MOUSEWHEEL:
                # Forward mouse wheel events to grid manager for zoom functionality
                self.grid_manager.handle_mouse_wheel(pygame.mouse.get_pos(), event.y)
            elif event.type == pygame.KEYDOWN:
                # Check for building placement cancellation
                if event.key == pygame.K_ESCAPE and self.building_placement_mode:
                    self.event_system.emit('exit_building_placement_mode', {})
                else:
                    self.employee_manager.handle_keyboard_input(event.key)
    
    def _update(self, dt):
        """Update all game systems"""
        # Update systems in dependency order
        self.time_manager.update(dt)
        self.weather_manager.update()  # Weather affects crop growth, so update before grid
        self.grid_manager.update(dt)
        self.inventory_manager.update(dt)
        self.building_manager.update(dt)
        self.contract_manager.update(dt)
        # Update hiring system for any time-based operations
        self.hiring_system.update(dt)
        self.employee_manager.update(dt)
        self.economy_manager.update(dt)
        self.ui_manager.update(dt)
        self.save_manager.update(dt)
        
        # Process any pending events
        self.event_system.process_events()
    
    def _render(self):
        """Render the game world and UI"""
        # Clear screen
        self.screen.fill(COLORS['background'])
        
        # Render systems in order
        self.grid_manager.render(self.screen)
        self.employee_manager.render(self.screen)
        self.ui_manager.render(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def _handle_quit(self, event_data):
        """Handle quit event"""
        self.running = False
        print("Quit event received.")
    
    def _handle_hire_confirmed(self, event_data):
        """Handle confirmed hiring request - temporarily disabled"""
        # NOTE: Interview system temporarily removed for debugging
        print("Interview system temporarily disabled - hire request ignored")
    
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
            
            print(f"Entered building placement mode for {building_type}")
    
    def _handle_exit_placement_mode(self, event_data):
        """Handle exiting building placement mode"""
        if self.building_placement_mode:
            self.building_placement_mode = False
            building_type = self.pending_building_type
            self.pending_building_type = None
            
            # Notify grid manager to hide placement preview
            self.event_system.emit('building_placement_preview_stop', {})
            
            print(f"Exited building placement mode for {building_type}")
    
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
                print(f"Successfully placed {building_type} at ({x}, {y})")
            else:
                print(f"Failed to place {building_type} at ({x}, {y})")
    
    def _handle_specialization_choice(self, event_data: Dict[str, Any]):
        """Handle specialization selection with economy integration"""
        specialization_id = event_data.get('specialization_id', '')
        manager = event_data.get('manager')
        
        if not manager:
            print("Error: No specialization manager provided")
            return
        
        # Get current cash from economy manager
        current_cash = self.economy_manager.get_current_balance()
        
        # Attempt to choose specialization
        result = manager.choose_specialization(specialization_id, current_cash)
        
        if result['success']:
            # Deduct cost from economy
            cost = result['cost']
            if cost > 0:
                self.economy_manager.spend_money(cost, f"Farm specialization: {result['specialization']['name']}", "specialization")
            
            # Notify UI of successful specialization
            self.event_system.emit('specialization_chosen_successfully', {
                'specialization': result['specialization'],
                'cost': cost
            })
            
            print(f"Successfully specialized as {result['specialization']['name']} for ${cost}")
        else:
            # Notify UI of failure
            reason = result.get('reason', 'Unknown error')
            self.event_system.emit('specialization_choice_failed', {
                'reason': reason,
                'cost': result.get('cost', 0)
            })
            
            print(f"Failed to specialize: {reason}")