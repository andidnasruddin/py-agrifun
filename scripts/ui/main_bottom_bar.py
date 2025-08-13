"""
Main Bottom Button Bar - Core game navigation and management interface
Provides the main action buttons as shown in the reference UI design.

Button Functions:
- Assign: Task assignment interface
- Employees: Employee management and hiring
- Contracts: Contract system and market agreements
- Buy: Purchase buildings, upgrades, and resources
- Design: Farm layout and planning tools
- Map: Farm overview and navigation
"""

import pygame
import pygame_gui
from typing import Dict, Any, Optional, Tuple
from scripts.core.config import *


class MainBottomBar:
    """Main bottom navigation bar with core game functions"""
    
    def __init__(self, gui_manager, event_system, screen_width: int, screen_height: int):
        """Initialize the main bottom button bar"""
        self.gui_manager = gui_manager  # pygame_gui manager for UI elements
        self.event_system = event_system  # Event system for communication
        self.screen_width = screen_width  # Screen width for positioning
        self.screen_height = screen_height  # Screen height for positioning
        
        # Button configuration
        self.button_width = 100  # Width of each button
        self.button_height = 45  # Height of each button
        self.button_spacing = 10  # Space between buttons
        self.bottom_margin = 10  # Margin from bottom of screen
        
        # Calculate positioning
        self.total_buttons = 6  # Number of main buttons
        self.total_width = (self.total_buttons * self.button_width) + ((self.total_buttons - 1) * self.button_spacing)
        self.start_x = (screen_width - self.total_width) // 2  # Center the button bar
        self.y_pos = screen_height - self.button_height - self.bottom_margin  # Position at bottom
        
        # Button definitions matching reference image
        self.button_definitions = [
            {"id": "assign", "label": "Assign", "tooltip": "Assign tasks to employees and manage work orders"},
            {"id": "employees", "label": "Employees", "tooltip": "Hire, manage, and view employee status and roster"},
            {"id": "contracts", "label": "Contracts", "tooltip": "View and manage farming contracts and agreements"},
            {"id": "buy", "label": "Buy", "tooltip": "Purchase buildings, equipment, and farm upgrades"},
            {"id": "design", "label": "Design", "tooltip": "Plan farm layout and design improvements"},
            {"id": "map", "label": "Map", "tooltip": "View farm overview and navigate to different areas"}
        ]
        
        # UI elements storage
        self.buttons: Dict[str, pygame_gui.elements.UIButton] = {}
        
        # Create the button bar
        self._create_bottom_bar()
        
        # Set up event subscriptions
        self._setup_event_handlers()
        
        print("Main Bottom Bar initialized with core navigation buttons")
    
    def _create_bottom_bar(self):
        """Create the main bottom navigation buttons"""
        for i, button_def in enumerate(self.button_definitions):
            # Calculate button position
            button_x = self.start_x + (i * (self.button_width + self.button_spacing))
            
            # Create button with professional styling
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(button_x, self.y_pos, self.button_width, self.button_height),
                text=button_def["label"],
                manager=self.gui_manager,
                tool_tip_text=button_def["tooltip"]
            )
            
            # Store button reference
            self.buttons[button_def["id"]] = button
            
            print(f"Created bottom bar button: {button_def['label']} at ({button_x}, {self.y_pos})")
    
    def _setup_event_handlers(self):
        """Set up event handlers for button interactions"""
        # Subscribe to UI events to handle button clicks
        # Note: pygame_gui button events will be handled in the main UI manager
        pass
    
    def handle_button_click(self, button_element) -> Optional[str]:
        """Handle button clicks and return the action ID"""
        # Find which button was clicked
        for button_id, ui_button in self.buttons.items():
            if ui_button == button_element:
                self._execute_button_action(button_id)
                return button_id
        return None
    
    def _execute_button_action(self, button_id: str):
        """Execute the appropriate action for the clicked button"""
        if button_id == "assign":
            # Show task assignment interface (smart action system handles this)
            self.event_system.emit('show_task_assignment_interface', {})
        elif button_id == "employees":
            # Show employee management interface
            self.event_system.emit('show_employee_management', {})
        elif button_id == "contracts":
            # Show contracts interface  
            self.event_system.emit('show_contracts_interface', {})
        elif button_id == "buy":
            # Show building/purchase interface
            self.event_system.emit('show_purchase_interface', {})
        elif button_id == "design":
            # Show farm design interface
            self.event_system.emit('show_design_interface', {})
        elif button_id == "map":
            # Show map/overview interface
            self.event_system.emit('show_map_interface', {})
        
        print(f"Bottom bar action executed: {button_id}")
    
    def get_button_by_position(self, pos: Tuple[int, int]) -> Optional[str]:
        """Get button ID at given screen position"""
        for button_id, button in self.buttons.items():
            if button.rect.collidepoint(pos):
                return button_id
        return None
    
    def enable_button(self, button_id: str):
        """Enable a specific button"""
        if button_id in self.buttons:
            self.buttons[button_id].enable()
    
    def disable_button(self, button_id: str):
        """Disable a specific button"""
        if button_id in self.buttons:
            self.buttons[button_id].disable()
    
    def update_button_text(self, button_id: str, new_text: str):
        """Update button text dynamically"""
        if button_id in self.buttons:
            self.buttons[button_id].set_text(new_text)
    
    def cleanup(self):
        """Clean up UI elements"""
        for button in self.buttons.values():
            button.kill()
        self.buttons.clear()