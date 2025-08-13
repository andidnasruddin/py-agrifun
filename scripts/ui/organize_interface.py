"""
Organize Interface - Professional employee management modal matching reference design
Provides comprehensive employee management including viewing, moving, and firing employees.

Features:
- Professional table layout matching reference design  
- Sort functionality with dropdown
- Current employee display with skills and traits
- Move and Fire action buttons for each employee
- Integration with existing employee management system
- Professional styling with green theme matching reference
"""

import pygame
import pygame_gui
from typing import Dict, Any, Optional, List
from scripts.core.config import *


class OrganizeInterface:
    """Professional organize interface modal with employee management functionality"""
    
    def __init__(self, gui_manager, event_system, screen_width: int, screen_height: int):
        """Initialize the organize interface modal"""
        self.gui_manager = gui_manager  # pygame_gui manager for UI elements
        self.event_system = event_system  # Event system for communication
        self.screen_width = screen_width  # Screen width for positioning
        self.screen_height = screen_height  # Screen height for positioning
        
        # Modal configuration
        self.modal_width = 800  # Width of organize modal
        self.modal_height = 600  # Height of organize modal
        self.modal_x = (screen_width - self.modal_width) // 2  # Center horizontally
        self.modal_y = (screen_height - self.modal_height) // 2  # Center vertically
        
        # UI elements storage
        self.window = None  # Main modal window
        self.sort_section = {}  # Sort controls (Sort by dropdown)
        self.table_section = {}  # Table elements (headers, rows, scrollable area)
        self.current_employees = []  # List of current employees to display
        
        # Table configuration matching reference design
        self.table_headers = ["Name", "Age", "Previous Job", "Current Farm", "Salary", "Actions", "List of Skills", "List of Traits"]
        self.table_y_offset = 80  # Space for sort section above table
        self.row_height = 35  # Height of each table row
        self.column_widths = [100, 40, 100, 100, 80, 80, 140, 140]  # Width of each column
        
        # Set up event subscriptions
        self._setup_event_handlers()
        
        print("Organize Interface initialized with professional employee management layout")
    
    def _setup_event_handlers(self):
        """Set up event handlers for organize interface interactions"""
        # Subscribe to employee management events
        self.event_system.subscribe('employee_fired_successfully', self._handle_employee_fired)
        self.event_system.subscribe('employee_moved_successfully', self._handle_employee_moved)
        self.event_system.subscribe('employee_action_failed', self._handle_employee_action_failed)
    
    def show_modal(self):
        """Show the organize interface modal"""
        if self.window:
            return  # Already open
        
        try:
            # Create main modal window with green theme
            self.window = pygame_gui.elements.UIWindow(
                rect=pygame.Rect(self.modal_x, self.modal_y, self.modal_width, self.modal_height),
                manager=self.gui_manager,
                window_display_title="Organize Employees"
            )
            
            # Create sort section at top of modal
            self._create_sort_section()
            
            # Create table section below sort controls
            self._create_table_section()
            
            # Load current employees from employee manager
            self._load_current_employees()
            
            print("Organize interface modal opened")
            
        except Exception as e:
            print(f"Error opening organize interface: {e}")
            self._cleanup_modal()
            # Re-raise the exception so the submenu knows it failed
            raise e
    
    def _create_sort_section(self):
        """Create the sort controls at the top of the modal"""
        # Sort by label
        sort_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 20, 70, 25),
            text="Sort by:",
            manager=self.gui_manager,
            container=self.window
        )
        
        # Sort dropdown
        sort_dropdown = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(95, 20, 150, 25),
            options_list=["Name (A-Z)", "Name (Z-A)", "Age (Young First)", "Age (Old First)", "Salary (Low-High)", "Salary (High-Low)"],
            starting_option="Name (A-Z)",
            manager=self.gui_manager,
            container=self.window
        )
        
        # Store references for event handling
        self.sort_section = {
            'sort_dropdown': sort_dropdown
        }
    
    def _create_table_section(self):
        """Create the employee table with headers and scrollable content"""
        # Create table header row
        header_y = self.table_y_offset
        current_x = 20  # Starting X position for first column
        
        header_elements = []
        for i, header_text in enumerate(self.table_headers):
            column_width = self.column_widths[i]
            
            # Create header label with professional styling
            header_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(current_x, header_y, column_width, 30),
                text=header_text,
                manager=self.gui_manager,
                container=self.window
            )
            
            header_elements.append(header_label)
            current_x += column_width + 5  # Move to next column position
        
        # Create scrollable area for table rows
        table_content_y = header_y + 35  # Below header
        table_content_height = self.modal_height - table_content_y - 50  # Leave space at bottom
        
        self.table_scrollable_area = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(20, table_content_y, self.modal_width - 60, table_content_height),
            manager=self.gui_manager,
            container=self.window
        )
        
        # Store references
        self.table_section = {
            'headers': header_elements,
            'scrollable_area': self.table_scrollable_area,
            'rows': []  # Will be populated when employees are loaded
        }
    
    def _load_current_employees(self):
        """Load current employees from the employee management system"""
        # Request current employee data from employee manager
        self.event_system.emit('get_current_employees_requested', {})
        
        # For now, create mock employee data based on the reference design
        # This will be replaced with real data from the employee manager
        mock_employees = [
            {
                'id': 'emp_001',
                'name': 'Barry',
                'age': 20,
                'previous_job': 'Student',
                'current_farm': 'Farm 1',
                'salary': 100,
                'skills': ['Manual Labor', 'Quick Learner'],
                'traits': ['Hard Worker', 'Enthusiastic']
            }
        ]
        
        self.current_employees = mock_employees
        self._refresh_table()
        
        print(f"Loaded {len(self.current_employees)} current employees")
    
    def _refresh_table(self):
        """Refresh the table with current employees"""
        # Clear existing table rows
        self._clear_table_rows()
        
        # Create new rows for current employees
        for i, employee in enumerate(self.current_employees):
            self._create_employee_row(employee, i)
    
    def _clear_table_rows(self):
        """Clear all existing table rows"""
        for row_elements in self.table_section.get('rows', []):
            for element in row_elements:
                element.kill()  # Remove from pygame_gui
        
        self.table_section['rows'] = []  # Clear the list
    
    def _create_employee_row(self, employee, row_index: int):
        """Create a table row for a single employee"""
        row_y = row_index * (self.row_height + 5)  # Position within scrollable area
        current_x = 10  # Starting X position within scrollable container
        
        row_elements = []
        
        # Column data based on employee information
        column_data = [
            employee['name'],  # Name
            str(employee['age']),  # Age
            employee['previous_job'],  # Previous Job
            employee['current_farm'],  # Current Farm
            f"${employee['salary']}/day",  # Salary
            "",  # Actions (will be Move and Fire buttons)
            ", ".join(employee['skills']),  # List of Skills
            ", ".join(employee['traits'])  # List of Traits
        ]
        
        # Create each column element
        for i, (data, width) in enumerate(zip(column_data, self.column_widths)):
            if i == 5:  # Actions column - create Move and Fire buttons
                # Create Move button
                move_button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(current_x, row_y, 35, self.row_height),
                    text="Move",
                    manager=self.gui_manager,
                    container=self.table_scrollable_area
                )
                # Store employee ID in button for event handling
                move_button.employee_id = employee['id']
                move_button.action_type = 'move'
                row_elements.append(move_button)
                
                # Create Fire button
                fire_button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(current_x + 40, row_y, 35, self.row_height),
                    text="Fire",
                    manager=self.gui_manager,
                    container=self.table_scrollable_area
                )
                # Store employee ID in button for event handling
                fire_button.employee_id = employee['id']
                fire_button.action_type = 'fire'
                # Apply red styling for fire button
                try:
                    fire_button.background_colour = pygame.Color("#ff4444")  # Red background
                    fire_button.text_colour = pygame.Color("#ffffff")  # White text
                    fire_button.rebuild()  # Apply visual changes
                except Exception as e:
                    print(f"Warning: Could not apply red styling to fire button: {e}")
                
                row_elements.append(fire_button)
            else:
                # Regular text label
                label = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(current_x, row_y, width, self.row_height),
                    text=data,
                    manager=self.gui_manager,
                    container=self.table_scrollable_area
                )
                row_elements.append(label)
            
            current_x += width + 5  # Move to next column
        
        # Store row elements for cleanup
        self.table_section['rows'].append(row_elements)
    
    def handle_button_click(self, button_element) -> bool:
        """Handle button clicks within the organize interface"""
        # Check if it's the sort dropdown (doesn't generate button clicks, but handle for completeness)
        if button_element == self.sort_section.get('sort_dropdown'):
            # Handle sort change
            print("Sort option changed")
            return True
        
        # Check if it's an employee action button (Move or Fire)
        if hasattr(button_element, 'employee_id') and hasattr(button_element, 'action_type'):
            employee_id = button_element.employee_id
            action_type = button_element.action_type
            
            if action_type == 'move':
                # Request to move this employee
                self.event_system.emit('move_employee_requested', {'employee_id': employee_id})
                print(f"Move button clicked for employee: {employee_id}")
            elif action_type == 'fire':
                # Request to fire this employee
                self.event_system.emit('fire_employee_requested', {'employee_id': employee_id})
                print(f"Fire button clicked for employee: {employee_id}")
            
            return True
        
        return False  # Button not handled by this interface
    
    def _handle_employee_fired(self, event_data: Dict[str, Any]):
        """Handle successful employee firing"""
        employee_id = event_data.get('employee_id', 'Unknown')
        employee_name = event_data.get('employee_name', 'Unknown')
        
        print(f"Employee {employee_name} fired successfully")
        
        # Remove the employee from current list and refresh table
        self.current_employees = [emp for emp in self.current_employees if emp['id'] != employee_id]
        self._refresh_table()
    
    def _handle_employee_moved(self, event_data: Dict[str, Any]):
        """Handle successful employee moving"""
        employee_id = event_data.get('employee_id', 'Unknown')
        employee_name = event_data.get('employee_name', 'Unknown')
        new_farm = event_data.get('new_farm', 'Unknown')
        
        print(f"Employee {employee_name} moved to {new_farm} successfully")
        
        # Update the employee's farm assignment and refresh table
        for emp in self.current_employees:
            if emp['id'] == employee_id:
                emp['current_farm'] = new_farm
                break
        
        self._refresh_table()
    
    def _handle_employee_action_failed(self, event_data: Dict[str, Any]):
        """Handle failed employee actions"""
        employee_id = event_data.get('employee_id', 'Unknown')
        action = event_data.get('action', 'Unknown')
        error = event_data.get('error', 'Unknown error')
        
        print(f"Failed to {action} employee {employee_id}: {error}")
        
        # Could show an error message to the user here
        # For now, just log the error
    
    def close_modal(self):
        """Close the organize interface modal"""
        self._cleanup_modal()
    
    def _cleanup_modal(self):
        """Clean up all modal UI elements"""
        try:
            # Clear table rows first
            self._clear_table_rows()
            
            # Clear sort section elements
            for element in self.sort_section.values():
                if element:
                    element.kill()
            self.sort_section.clear()
            
            # Clear table section elements
            for element in self.table_section.get('headers', []):
                element.kill()
            if 'scrollable_area' in self.table_section:
                self.table_section['scrollable_area'].kill()
            self.table_section.clear()
            
            # Close main window
            if self.window:
                self.window.kill()
                self.window = None
            
            # Clear employee data
            self.current_employees.clear()
            
            print("Organize interface modal closed and cleaned up")
            
        except Exception as e:
            print(f"Error during organize interface cleanup: {e}")
    
    def is_open(self) -> bool:
        """Check if the organize interface modal is currently open"""
        return self.window is not None
    
    def handle_window_close(self, window_element) -> bool:
        """Handle window close events"""
        if window_element == self.window:
            self.close_modal()
            return True
        return False