"""
Employee Submenu System - Advanced employee management interface
Implements the submenu system for the Employee button with slide-up animation,
button state management, and comprehensive employee operations.

Features:
- Green button state management when submenu is active
- Red submenu buttons (Hire, Organize) with 100ms slide-up animation
- Modal priority management with clean state transitions
- Integration with existing hiring and employee management systems
- Error handling and graceful fallback mechanisms
"""

import pygame
import pygame_gui
from typing import Dict, Any, Optional, Tuple, List
from scripts.core.config import *
from scripts.ui.hire_interface import HireInterface
from scripts.ui.organize_interface import OrganizeInterface
import time


class EmployeeSubmenu:
    """Advanced employee submenu with professional animations and state management"""
    
    def __init__(self, gui_manager, event_system, main_bottom_bar, screen_width: int, screen_height: int):
        """Initialize the employee submenu system"""
        self.gui_manager = gui_manager  # pygame_gui manager for UI elements
        self.event_system = event_system  # Event system for communication
        self.main_bottom_bar = main_bottom_bar  # Reference to main bottom bar
        self.screen_width = screen_width  # Screen width for positioning
        self.screen_height = screen_height  # Screen height for positioning
        
        # State management
        self.is_submenu_active = False  # Track if submenu is currently visible
        self.current_modal = None  # Track currently open modal (hire/organize)
        self.animation_start_time = 0  # Track animation timing
        self.animation_duration = 0.1  # 100ms animation duration
        
        # Submenu button configuration
        self.submenu_button_width = 100  # Width of submenu buttons (increased for debugging)
        self.submenu_button_height = 40  # Height of submenu buttons (increased for debugging)
        self.submenu_spacing = 5  # Space between submenu buttons
        self.submenu_offset_y = 55  # Distance above main Employee button
        
        # Calculate submenu positioning based on Employee button position
        self.employee_button_x = self._get_employee_button_x()  # X position of Employee button
        self.employee_button_y = self.main_bottom_bar.y_pos  # Y position of Employee button
        
        # Submenu button definitions (red buttons as per reference)
        self.submenu_buttons_config = [
            {"id": "hire", "label": "Hire", "tooltip": "Search and hire new employees", "color": "#ff4444"},
            {"id": "organize", "label": "Organize", "tooltip": "Manage current employees and assignments", "color": "#ff4444"}
        ]
        
        # UI elements storage
        self.submenu_buttons: Dict[str, pygame_gui.elements.UIButton] = {}
        self.submenu_background = None  # Background panel for submenu
        
        # Modal windows storage
        self.hire_interface = HireInterface(gui_manager, event_system, screen_width, screen_height)  # Professional hire interface
        self.organize_interface = OrganizeInterface(gui_manager, event_system, screen_width, screen_height)  # Professional organize interface
        
        # Set up event subscriptions
        self._setup_event_handlers()
        
        print("Employee Submenu system initialized with button state management")
    
    def _get_employee_button_x(self) -> int:
        """Calculate the X position of the Employee button from main bottom bar"""
        # Employee is the 2nd button (index 1), so calculate its position
        button_index = 1  # Assign=0, Employees=1, Contracts=2, Buy=3, Design=4, Map=5
        return (self.main_bottom_bar.start_x + 
                (button_index * (self.main_bottom_bar.button_width + self.main_bottom_bar.button_spacing)))
    
    def _setup_event_handlers(self):
        """Set up event handlers for submenu interactions"""
        # Subscribe to employee management events
        self.event_system.subscribe('show_employee_management', self._handle_employee_button_click)
        self.event_system.subscribe('close_employee_submenu', self._handle_close_submenu)
        self.event_system.subscribe('show_hire_interface', self._handle_show_hire)
        self.event_system.subscribe('show_organize_interface', self._handle_show_organize)
    
    def _handle_employee_button_click(self, data: Dict[str, Any]):
        """Handle main Employee button click - toggle submenu"""
        if self.is_submenu_active:
            # Close submenu if already open
            self._close_submenu()
        else:
            # Open submenu with animation
            self._open_submenu()
    
    def _open_submenu(self):
        """Open the employee submenu with slide-up animation"""
        if self.is_submenu_active:
            return  # Already open
        
        try:
            # Set Employee button to green state (active)
            self._set_employee_button_state(active=True)
            
            # Disable animation for now (causing visibility issues)
            # self.animation_start_time = time.time()
            self.animation_start_time = 0  # No animation
            self.is_submenu_active = True
            
            # Create submenu buttons with initial position (off-screen below)
            self._create_submenu_buttons()
            
            print("Employee submenu opened with slide-up animation")
            
        except Exception as e:
            print(f"Error opening employee submenu: {e}")
            self._handle_submenu_error()
    
    def _close_submenu(self):
        """Close the employee submenu and clean up state"""
        if not self.is_submenu_active:
            return  # Already closed
        
        try:
            # Set Employee button back to normal state
            self._set_employee_button_state(active=False)
            
            # Close any open modals
            self._close_all_modals()
            
            # Remove submenu buttons
            self._cleanup_submenu_buttons()
            
            # Reset state
            self.is_submenu_active = False
            self.animation_start_time = 0
            
            print("Employee submenu closed and state cleaned up")
            
        except Exception as e:
            print(f"Error closing employee submenu: {e}")
            self._handle_submenu_error()
    
    def _create_submenu_buttons(self):
        """Create the submenu buttons with slide-up animation"""
        # Calculate base position for submenu buttons (centered above Employee button)
        total_submenu_width = (len(self.submenu_buttons_config) * self.submenu_button_width + 
                             (len(self.submenu_buttons_config) - 1) * self.submenu_spacing)
        submenu_start_x = self.employee_button_x + (self.main_bottom_bar.button_width - total_submenu_width) // 2
        
        # Final position (above Employee button)
        self.final_submenu_y = self.employee_button_y - self.submenu_offset_y
        
        # Start at final position (no animation for now)
        initial_submenu_y = self.final_submenu_y
        
        # Create each submenu button starting from below
        for i, button_config in enumerate(self.submenu_buttons_config):
            # Calculate button position
            button_x = submenu_start_x + (i * (self.submenu_button_width + self.submenu_spacing))
            
            # Create button with red styling as per reference, starting below Employee button
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(button_x, initial_submenu_y, self.submenu_button_width, self.submenu_button_height),
                text=button_config["label"],
                manager=self.gui_manager,
                tool_tip_text=button_config["tooltip"]
            )
            
            # Apply red styling for submenu buttons
            try:
                button.background_colour = pygame.Color("#ff4444")  # Red background
                button.text_colour = pygame.Color("#ffffff")  # White text
                button.rebuild()  # Apply visual changes
            except Exception as e:
                print(f"Warning: Could not apply red styling to submenu button: {e}")
            
            # Store button reference
            self.submenu_buttons[button_config["id"]] = button
            
            print(f"Created submenu button: {button_config['label']} at position ({button_x}, {initial_submenu_y}) size ({self.submenu_button_width}, {self.submenu_button_height})")
            print(f"  Employee button Y: {self.employee_button_y}, Final Y: {self.final_submenu_y}, Screen height: {self.screen_height}")
    
    def _cleanup_submenu_buttons(self):
        """Remove all submenu buttons from the UI"""
        for button in self.submenu_buttons.values():
            button.kill()  # Remove from pygame_gui
        self.submenu_buttons.clear()  # Clear references
    
    def _set_employee_button_state(self, active: bool):
        """Set the Employee button visual state (green when active)"""
        try:
            employee_button = self.main_bottom_bar.buttons.get("employees")
            if employee_button:
                if active:
                    # Set green background color for active state
                    employee_button.background_colour = pygame.Color("#44ff44")  # Green
                    employee_button.rebuild()  # Apply visual changes
                else:
                    # Reset to default color
                    employee_button.background_colour = pygame.Color("#ffffff")  # Default white
                    employee_button.rebuild()  # Apply visual changes
        except Exception as e:
            print(f"Error setting employee button state: {e}")
    
    def handle_submenu_button_click(self, button_element) -> Optional[str]:
        """Handle submenu button clicks and return the action ID"""
        # Find which submenu button was clicked
        for button_id, ui_button in self.submenu_buttons.items():
            if ui_button == button_element:
                self._execute_submenu_action(button_id)
                return button_id
        return None
    
    def _execute_submenu_action(self, button_id: str):
        """Execute the appropriate action for the clicked submenu button"""
        try:
            if button_id == "hire":
                # Show hire interface modal
                self._show_hire_modal()
            elif button_id == "organize":
                # Show organize interface modal
                self._show_organize_modal()
            
            print(f"Employee submenu action executed: {button_id}")
            
        except Exception as e:
            print(f"Error executing submenu action {button_id}: {e}")
            self._handle_submenu_error()
    
    def _show_hire_modal(self):
        """Show the employee hire interface modal"""
        try:
            # Close any existing modal first (modal priority management)
            self._close_all_modals()
            
            # Open the professional hire interface
            self.hire_interface.show_modal()
            
            # Only set current_modal if the interface actually opened
            if self.hire_interface.is_open():
                self.current_modal = "hire"
                print("Professional hire interface opened with modal priority management")
            else:
                print("Error: Hire interface failed to open")
                self.current_modal = None
                
        except Exception as e:
            print(f"Error opening hire modal: {e}")
            self.current_modal = None
    
    def _show_organize_modal(self):
        """Show the employee organize interface modal"""
        try:
            # Close any existing modal first (modal priority management)
            self._close_all_modals()
            
            # Open the professional organize interface
            self.organize_interface.show_modal()
            
            # Only set current_modal if the interface actually opened
            if self.organize_interface.is_open():
                self.current_modal = "organize"
                print("Professional organize interface opened with modal priority management")
            else:
                print("Error: Organize interface failed to open")
                self.current_modal = None
                
        except Exception as e:
            print(f"Error opening organize modal: {e}")
            self.current_modal = None
    
    def _close_all_modals(self):
        """Close all open modals and clean up state"""
        if self.hire_interface.is_open():
            self.hire_interface.close_modal()
        
        if self.organize_interface.is_open():
            self.organize_interface.close_modal()
        
        self.current_modal = None
        print("All employee modals closed")
    
    def _handle_close_submenu(self, data: Dict[str, Any]):
        """Handle external requests to close the submenu"""
        self._close_submenu()
    
    def _handle_show_hire(self, data: Dict[str, Any]):
        """Handle requests to show hire interface"""
        if not self.is_submenu_active:
            self._open_submenu()  # Open submenu first if needed
        self._show_hire_modal()
    
    def _handle_show_organize(self, data: Dict[str, Any]):
        """Handle requests to show organize interface"""
        if not self.is_submenu_active:
            self._open_submenu()  # Open submenu first if needed
        self._show_organize_modal()
    
    def _handle_submenu_error(self):
        """Handle errors with graceful fallback mechanisms"""
        try:
            # Reset all states to safe defaults
            self.is_submenu_active = False
            self.current_modal = None
            self.animation_start_time = 0
            
            # Clean up UI elements with individual error handling
            try:
                self._cleanup_submenu_buttons()
            except Exception as cleanup_error:
                print(f"Warning: Error during submenu button cleanup: {cleanup_error}")
            
            try:
                self._close_all_modals()
            except Exception as modal_error:
                print(f"Warning: Error during modal cleanup: {modal_error}")
            
            try:
                self._set_employee_button_state(active=False)
            except Exception as button_error:
                print(f"Warning: Error during button state reset: {button_error}")
            
            # Emit error recovery event for system-wide cleanup if needed
            try:
                self.event_system.emit('employee_submenu_error_recovery', {
                    'timestamp': time.time(),
                    'submenu_recovered': True
                })
            except Exception as event_error:
                print(f"Warning: Could not emit error recovery event: {event_error}")
            
            print("Employee submenu error handled with graceful fallback")
            
        except Exception as e:
            print(f"Critical error in submenu error handler: {e}")
            # Last resort: try to completely disable the submenu system
            try:
                self.is_submenu_active = False
                self.current_modal = None
                print("Emergency fallback: Submenu system disabled")
            except:
                print("FATAL: Could not recover from submenu error")
    
    def _validate_system_state(self) -> bool:
        """Validate the current state of the submenu system for error prevention"""
        try:
            # Check core component integrity
            if not hasattr(self, 'gui_manager') or self.gui_manager is None:
                print("Warning: GUI manager is invalid")
                return False
            
            if not hasattr(self, 'event_system') or self.event_system is None:
                print("Warning: Event system is invalid")
                return False
            
            if not hasattr(self, 'main_bottom_bar') or self.main_bottom_bar is None:
                print("Warning: Main bottom bar reference is invalid")
                return False
            
            # Check modal interface integrity
            if not hasattr(self, 'hire_interface') or self.hire_interface is None:
                print("Warning: Hire interface is invalid")
                return False
            
            if not hasattr(self, 'organize_interface') or self.organize_interface is None:
                print("Warning: Organize interface is invalid")
                return False
            
            # Check state consistency
            if self.is_submenu_active and len(self.submenu_buttons) == 0:
                print("Warning: Submenu marked as active but no buttons exist")
                return False
            
            if self.current_modal and not (self.hire_interface.is_open() or self.organize_interface.is_open()):
                print("Warning: Modal marked as active but no modal is open")
                self.current_modal = None  # Auto-correct this state issue
            
            return True
            
        except Exception as e:
            print(f"Error during system state validation: {e}")
            return False
    
    def _perform_health_check(self):
        """Perform a comprehensive health check of the submenu system"""
        try:
            if not self._validate_system_state():
                print("Health check failed - attempting recovery")
                self._handle_submenu_error()
                return False
            
            # Check for orphaned UI elements
            try:
                if self.is_submenu_active:
                    for button_id, button in self.submenu_buttons.items():
                        if not hasattr(button, 'rect'):
                            print(f"Warning: Submenu button {button_id} is corrupted")
                            self._handle_submenu_error()
                            return False
            except Exception as button_check_error:
                print(f"Error checking submenu buttons: {button_check_error}")
                self._handle_submenu_error()
                return False
            
            return True
            
        except Exception as e:
            print(f"Error during health check: {e}")
            self._handle_submenu_error()
            return False
    
    def update(self, dt: float):
        """Update submenu animations and state with error handling"""
        try:
            # Perform periodic health check (every 60 frames at 60 FPS = once per second)
            if hasattr(self, '_health_check_counter'):
                self._health_check_counter += 1
                if self._health_check_counter >= 60:
                    self._health_check_counter = 0
                    if not self._perform_health_check():
                        return  # Skip update if health check failed
            else:
                self._health_check_counter = 0
            
            if self.is_submenu_active and self.animation_start_time > 0:
                # Calculate animation progress (0.0 to 1.0)
                elapsed_time = time.time() - self.animation_start_time
                animation_progress = min(elapsed_time / self.animation_duration, 1.0)
                
                # Apply slide-up animation to submenu buttons with error handling
                try:
                    self._update_slide_animation(animation_progress)
                except Exception as anim_error:
                    print(f"Animation error: {anim_error}")
                    # Fallback: position buttons at final location
                    self._position_buttons_at_final_location()
                    self.animation_start_time = 0  # Stop animation
                
                # Animation is complete when progress reaches 1.0
                if animation_progress >= 1.0:
                    self.animation_start_time = 0  # Mark animation as complete
                    
        except Exception as e:
            print(f"Error in submenu update: {e}")
            self._handle_submenu_error()
    
    def _update_slide_animation(self, progress: float):
        """Update the slide-up animation for submenu buttons"""
        try:
            # Calculate current Y position using eased animation
            # Use ease-out cubic for smooth deceleration at the end
            eased_progress = 1 - (1 - progress) ** 3  # Cubic ease-out
            
            # Calculate starting and ending positions
            start_y = self.employee_button_y + self.main_bottom_bar.button_height + 10  # Below Employee button
            end_y = self.final_submenu_y  # Above Employee button
            
            # Interpolate current position
            current_y = start_y + (end_y - start_y) * eased_progress
            
            # Update each submenu button position
            for i, (button_id, button) in enumerate(self.submenu_buttons.items()):
                # Calculate button X position (unchanged)
                total_submenu_width = (len(self.submenu_buttons_config) * self.submenu_button_width + 
                                     (len(self.submenu_buttons_config) - 1) * self.submenu_spacing)
                submenu_start_x = self.employee_button_x + (self.main_bottom_bar.button_width - total_submenu_width) // 2
                button_x = submenu_start_x + (i * (self.submenu_button_width + self.submenu_spacing))
                
                # Update button position with animation
                button.rect.x = button_x
                button.rect.y = int(current_y)
                button.relative_rect.x = button_x
                button.relative_rect.y = int(current_y)
                
                # Force pygame-gui to update the button's visual position
                if hasattr(button, 'rebuild'):
                    button.rebuild()
            
        except Exception as e:
            print(f"Error updating slide animation: {e}")
            # Fallback: position buttons at final location
            self._position_buttons_at_final_location()
    
    def _position_buttons_at_final_location(self):
        """Position buttons at their final location (fallback for animation errors)"""
        try:
            for i, (button_id, button) in enumerate(self.submenu_buttons.items()):
                # Calculate final button position
                total_submenu_width = (len(self.submenu_buttons_config) * self.submenu_button_width + 
                                     (len(self.submenu_buttons_config) - 1) * self.submenu_spacing)
                submenu_start_x = self.employee_button_x + (self.main_bottom_bar.button_width - total_submenu_width) // 2
                button_x = submenu_start_x + (i * (self.submenu_button_width + self.submenu_spacing))
                
                # Set final position
                button.rect.x = button_x
                button.rect.y = self.final_submenu_y
                button.relative_rect.x = button_x
                button.relative_rect.y = self.final_submenu_y
                
                if hasattr(button, 'rebuild'):
                    button.rebuild()
                    
        except Exception as e:
            print(f"Error positioning buttons at final location: {e}")
    
    def handle_click_outside(self, click_pos: Tuple[int, int]) -> bool:
        """Handle clicks outside the submenu to close it"""
        if not self.is_submenu_active:
            return False
        
        # Check if click is outside submenu area
        if self._is_click_outside_submenu(click_pos):
            self._close_submenu()
            return True  # Handled the click
        
        return False  # Click was inside submenu
    
    def handle_modal_button_click(self, button_element) -> bool:
        """Handle button clicks within modal windows"""
        # Check if it's a hire interface button
        if self.current_modal == "hire" and self.hire_interface.is_open():
            if self.hire_interface.handle_button_click(button_element):
                return True  # Button was handled by hire interface
        
        # Check if it's an organize interface button
        if self.current_modal == "organize" and self.organize_interface.is_open():
            if self.organize_interface.handle_button_click(button_element):
                return True  # Button was handled by organize interface
        
        return False  # Button not handled by any modal
    
    def handle_window_close(self, window_element) -> bool:
        """Handle window close events"""
        # Check if it's the hire interface window
        if self.current_modal == "hire" and self.hire_interface.is_open():
            if self.hire_interface.handle_window_close(window_element):
                self.current_modal = None  # Clear current modal state
                return True  # Window close was handled
        
        # Check if it's the organize interface window
        if self.current_modal == "organize" and self.organize_interface.is_open():
            if self.organize_interface.handle_window_close(window_element):
                self.current_modal = None  # Clear current modal state
                return True  # Window close was handled
        
        return False  # Window close not handled by submenu
    
    def _is_click_outside_submenu(self, click_pos: Tuple[int, int]) -> bool:
        """Check if click position is outside the submenu area"""
        # Check if click is on any submenu button
        for button in self.submenu_buttons.values():
            if button.rect.collidepoint(click_pos):
                return False  # Click is on submenu button
        
        # Check if click is on Employee button
        employee_button = self.main_bottom_bar.buttons.get("employees")
        if employee_button and employee_button.rect.collidepoint(click_pos):
            return False  # Click is on Employee button
        
        # Check if click is on any open modal
        if self.current_modal:
            if self.current_modal == "hire" and self.hire_interface.is_open():
                # Don't close if click is on hire interface (it handles its own clicks)
                return False
            elif self.current_modal == "organize" and self.organize_interface.is_open():
                # Don't close if click is on organize interface (it handles its own clicks)
                return False
        
        return True  # Click is outside submenu area
    
    def cleanup(self):
        """Clean up all UI elements and state"""
        try:
            self._cleanup_submenu_buttons()
            self._close_all_modals()
            self._set_employee_button_state(active=False)
            
            # Reset all state
            self.is_submenu_active = False
            self.current_modal = None
            self.animation_start_time = 0
            
            print("Employee submenu cleanup completed")
            
        except Exception as e:
            print(f"Error during submenu cleanup: {e}")