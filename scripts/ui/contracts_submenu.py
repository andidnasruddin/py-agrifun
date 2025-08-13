"""
Contracts Submenu System - Direct modal launcher for contract management
Unlike the Employee submenu, this directly opens the contracts modal when clicked.

Features:
- Green button state management when contracts modal is active
- Direct modal opening (no sub-buttons needed)
- Integration with contracts interface modal
- Modal priority management with clean state transitions
- Error handling and graceful fallback systems
"""

import pygame
import pygame_gui
from typing import Dict, Any, Optional, Tuple
from scripts.core.config import *
from scripts.ui.contracts_interface import ContractsInterface


class ContractsSubmenu:
    """Simplified contracts submenu that directly opens the contracts modal"""
    
    def __init__(self, gui_manager, event_system, main_bottom_bar, screen_width: int, screen_height: int):
        """Initialize the contracts submenu system"""
        self.gui_manager = gui_manager  # pygame_gui manager for UI elements
        self.event_system = event_system  # Event system for communication
        self.main_bottom_bar = main_bottom_bar  # Reference to main bottom bar
        self.screen_width = screen_width  # Screen width for positioning
        self.screen_height = screen_height  # Screen height for positioning
        
        # State management
        self.is_modal_active = False  # Track if contracts modal is currently open
        
        # Modal interface
        self.contracts_interface = ContractsInterface(gui_manager, event_system, screen_width, screen_height)
        
        # Set up event subscriptions
        self._setup_event_handlers()
        
        print("Contracts Submenu system initialized")
    
    def _setup_event_handlers(self):
        """Set up event handlers for contracts submenu interactions"""
        # Subscribe to contracts management events
        self.event_system.subscribe('show_contracts_interface', self._handle_contracts_button_click)
        self.event_system.subscribe('close_contracts_submenu', self._handle_close_submenu)
    
    def _handle_contracts_button_click(self, data: Dict[str, Any]):
        """Handle main Contracts button click - toggle modal"""
        if self.is_modal_active:
            # Close modal if already open
            self._close_modal()
        else:
            # Open modal
            self._open_modal()
    
    def _open_modal(self):
        """Open the contracts interface modal"""
        if self.is_modal_active:
            return  # Already open
        
        try:
            # Set Contracts button to green state (active)
            self._set_contracts_button_state(active=True)
            
            # Open the professional contracts interface
            self.contracts_interface.show_modal()
            
            # Only set modal state if the interface actually opened
            if self.contracts_interface.is_open():
                self.is_modal_active = True
                print("Professional contracts interface opened")
            else:
                print("Error: Contracts interface failed to open")
                self.is_modal_active = False
                self._set_contracts_button_state(active=False)
                
        except Exception as e:
            print(f"Error opening contracts modal: {e}")
            self.is_modal_active = False
            self._set_contracts_button_state(active=False)
    
    def _close_modal(self):
        """Close the contracts interface modal"""
        try:
            # Set Contracts button back to normal state
            self._set_contracts_button_state(active=False)
            
            # Close the modal
            if self.contracts_interface.is_open():
                self.contracts_interface.close_modal()
            
            # Reset state
            self.is_modal_active = False
            
            print("Contracts interface closed and state cleaned up")
            
        except Exception as e:
            print(f"Error closing contracts modal: {e}")
            self._handle_error()
    
    def _set_contracts_button_state(self, active: bool):
        """Set the Contracts button visual state (green when active)"""
        try:
            contracts_button = self.main_bottom_bar.buttons.get("contracts")
            if contracts_button:
                if active:
                    # Set green background color for active state
                    contracts_button.background_colour = pygame.Color("#44ff44")  # Green
                    contracts_button.rebuild()  # Apply visual changes
                else:
                    # Reset to default color
                    contracts_button.background_colour = pygame.Color("#ffffff")  # Default white
                    contracts_button.rebuild()  # Apply visual changes
        except Exception as e:
            print(f"Error setting contracts button state: {e}")
    
    def handle_modal_button_click(self, button_element) -> bool:
        """Handle button clicks within the contracts modal"""
        # Check if it's a contracts interface button
        if self.is_modal_active and self.contracts_interface.is_open():
            if self.contracts_interface.handle_button_click(button_element):
                return True  # Button was handled by contracts interface
        
        return False  # Button not handled by modal
    
    def handle_window_close(self, window_element) -> bool:
        """Handle window close events"""
        # Check if it's the contracts interface window
        if self.is_modal_active and self.contracts_interface.is_open():
            if self.contracts_interface.handle_window_close(window_element):
                self.is_modal_active = False  # Clear modal state
                self._set_contracts_button_state(active=False)  # Reset button state
                return True  # Window close was handled
        
        return False  # Window close not handled by submenu
    
    def handle_click_outside(self, click_pos: Tuple[int, int]) -> bool:
        """Handle clicks outside the modal to close it"""
        if not self.is_modal_active:
            return False
        
        # Check if click is outside modal area
        if self._is_click_outside_modal(click_pos):
            self._close_modal()
            return True  # Handled the click
        
        return False  # Click was inside modal
    
    def _is_click_outside_modal(self, click_pos: Tuple[int, int]) -> bool:
        """Check if click position is outside the modal area"""
        # Check if click is on Contracts button
        contracts_button = self.main_bottom_bar.buttons.get("contracts")
        if contracts_button and contracts_button.rect.collidepoint(click_pos):
            return False  # Click is on Contracts button
        
        # Check if click is on the contracts modal
        if self.is_modal_active and self.contracts_interface.is_open():
            # Don't close if click is on contracts interface (it handles its own clicks)
            return False
        
        return True  # Click is outside modal area
    
    def _handle_close_submenu(self, data: Dict[str, Any]):
        """Handle external requests to close the submenu"""
        self._close_modal()
    
    def _handle_error(self):
        """Handle errors with graceful fallback mechanisms"""
        try:
            # Reset all states to safe defaults
            self.is_modal_active = False
            
            # Clean up modal
            if self.contracts_interface.is_open():
                self.contracts_interface.close_modal()
            
            # Reset button state
            self._set_contracts_button_state(active=False)
            
            print("Contracts submenu error handled with graceful fallback")
            
        except Exception as e:
            print(f"Critical error in contracts submenu error handler: {e}")
    
    def update(self, dt: float):
        """Update contracts submenu (minimal updates needed)"""
        # Contracts submenu doesn't need regular updates like Employee submenu
        # The modal interface handles its own state
        pass
    
    def cleanup(self):
        """Clean up all UI elements and state"""
        try:
            if self.contracts_interface.is_open():
                self.contracts_interface.close_modal()
            
            self._set_contracts_button_state(active=False)
            
            # Reset all state
            self.is_modal_active = False
            
            print("Contracts submenu cleanup completed")
            
        except Exception as e:
            print(f"Error during contracts submenu cleanup: {e}")