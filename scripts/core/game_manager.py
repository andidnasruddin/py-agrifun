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
        self.building_manager = BuildingManager(self.event_system, self.economy_manager, self.inventory_manager)
        # Create employee manager first, then hiring system that uses it
        self.employee_manager = EmployeeManager(self.event_system, self.grid_manager, time_manager=self.time_manager)
        # Initialize simple hiring system for employee recruitment  
        self.hiring_system = SimpleHiringSystem(self.event_system, self.economy_manager, self.employee_manager)
        
        # NOTE: Interview system sync temporarily removed
        # self.interview_system.set_current_day(self.time_manager.current_day)
        
        # Connect employee manager to inventory manager for synchronous harvest processing
        self.employee_manager.set_inventory_manager(self.inventory_manager)
        
        self.ui_manager = UIManager(self.event_system, self.screen)
        
        # Initialize save/load system (after all other systems)
        self.save_manager = SaveManager(self.event_system, self)
        
        # Register for quit events
        self.event_system.subscribe('game_quit', self._handle_quit)
        
        # Register for hiring events (connect interview system to employee manager)
        self.event_system.subscribe('hire_applicant_confirmed', self._handle_hire_confirmed)
        
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
                if any(pygame.mouse.get_pressed()):
                    self.employee_manager.handle_mouse_drag(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.employee_manager.handle_mouse_up(event.pos, event.button)
            elif event.type == pygame.KEYDOWN:
                self.employee_manager.handle_keyboard_input(event.key)
    
    def _update(self, dt):
        """Update all game systems"""
        # Update systems in dependency order
        self.time_manager.update(dt)
        self.grid_manager.update(dt)
        self.inventory_manager.update(dt)
        self.building_manager.update(dt)
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